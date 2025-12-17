"""Azure-related helpers used by tgwrap services."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys

import click
import requests


class AzureService:
    """Wrap Azure CLI interactions needed by tgwrap."""

    def __init__(self, printer):
        self.printer = printer

    def get_access_token(self) -> tuple[str, str]:
        """Retrieve the principal and access token using the Azure CLI."""

        def _run_az(command: str, description: str):
            try:
                return subprocess.run(
                    shlex.split(command),
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except FileNotFoundError as exc:
                self.printer.error(
                    "Azure CLI (az) is required but not found on PATH."
                )
                raise click.ClickException(
                    "Azure CLI is not available; install it to enable Azure integrations."
                ) from exc
            except subprocess.CalledProcessError as exc:
                stderr_msg = exc.stderr.decode().strip() if exc.stderr else ""
                message = (
                    f"Azure CLI failed while {description} (exit code {exc.returncode})."
                )
                self.printer.error(message)
                if stderr_msg and self.printer.print_verbose:
                    self.printer.normal(stderr_msg, print_line_before=True)
                raise click.ClickException(message) from exc

        account_proc = _run_az("az account show", "retrieving Azure account info")
        self.printer.verbose("Azure account information retrieved successfully")

        try:
            account_info = json.loads(account_proc.stdout.decode())
        except json.JSONDecodeError as exc:
            raise click.ClickException(
                "Azure CLI returned malformed account information."
            ) from exc

        if account_info.get("environmentName") != "AzureCloud":
            raise click.ClickException(
                f"Environment is not an Azure cloud:\n{json.dumps(account_info, indent=2)}"
            )

        if not account_info.get("tenantId"):
            raise click.ClickException(
                f"Could not determine Azure tenant id:\n{json.dumps(account_info, indent=2)}"
            )

        principal = account_info.get("user", {}).get("name")
        if not principal:
            raise click.ClickException(
                f"Could not determine principal:\n{json.dumps(account_info, indent=2)}"
            )

        token_proc = _run_az(
            'az account get-access-token --scope "https://monitor.azure.com//.default"',
            "retrieving an access token",
        )
        self.printer.verbose("Azure access token retrieved successfully")

        try:
            token_payload = json.loads(token_proc.stdout.decode())
        except json.JSONDecodeError as exc:
            raise click.ClickException(
                "Azure CLI returned malformed access token information."
            ) from exc

        token = token_payload.get("accessToken")
        if not token:
            raise click.ClickException(
                f"Could not retrieve an access token:\n{json.dumps(token_payload, indent=2)}"
            )

        return principal, token

    def post_to_dce(self, *, data_collection_endpoint: str, payload, token: str | None = None):
        """Post the payload to an Azure Data Collection Endpoint."""

        if not token:
            _, token = self.get_access_token()

        if not isinstance(payload, list):
            dce_payload = [payload]
        else:
            dce_payload = payload

        self.printer.verbose("About to log:")
        self.printer.verbose(f"- to: {data_collection_endpoint}")
        self.printer.verbose(f"- payload:\n{json.dumps(dce_payload, indent=2)}")

        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                url=data_collection_endpoint,
                headers=headers,
                json=dce_payload,
                timeout=10,
            )
            resp.raise_for_status()
            self.printer.success(
                "Analyze results logged to DCE", print_line_before=True
            )
        except requests.exceptions.RequestException as exc:
            self.printer.warning(
                f"Error while posting the analyze results ({type(exc)}): {exc}",
                print_line_before=True,
            )
        except Exception as exc:  # pylint: disable=broad-except
            self.printer.error(f"Unexpected error: {exc}")
            if self.printer.print_verbose:
                raise
            sys.exit(1)

    def post_analyze_results(
        self, *, data_collection_endpoint: str, payload: dict
    ) -> None:
        """Enrich and forward analyze results to the Azure endpoint."""

        principal, token = self.get_access_token()

        def mask_basic_auth(url: str) -> str:
            auth_pattern = re.compile(r"(https?://)([^:@]+):([^:@]+)@(.+)")
            return auth_pattern.sub(r"\1\4", url)

        rc = subprocess.run(
            shlex.split("git config --get remote.origin.url"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc)
        if rc.returncode != 0:
            raise RuntimeError("Could not get git repo info")

        repo = rc.stdout.decode().rstrip("\n")
        if not repo:
            raise RuntimeError(f"Could not get git repo info: {repo}")
        repo = mask_basic_auth(repo)

        rc = subprocess.run(
            shlex.split("git rev-parse --show-prefix"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        self.printer.verbose(rc)
        if rc.returncode != 0:
            raise RuntimeError("Could not get current scope")

        scope = rc.stdout.decode().rstrip("\n")
        if not scope:
            raise RuntimeError(f"Could not get scope: {scope}")

        enriched_payload = {
            "scope": scope,
            "principal": principal,
            "repo": repo,
            "creations": payload.get("summary", {}).get("creations"),
            "updates": payload.get("summary", {}).get("updates"),
            "deletions": payload.get("summary", {}).get("deletions"),
            "minor": payload.get("summary", {}).get("minor"),
            "medium": payload.get("summary", {}).get("medium"),
            "major": payload.get("summary", {}).get("major"),
            "unknown": payload.get("summary", {}).get("unknown"),
            "total": payload.get("summary", {}).get("total"),
            "score": payload.get("summary", {}).get("score"),
            "details": payload.get("details"),
        }

        self.post_to_dce(
            data_collection_endpoint=data_collection_endpoint,
            payload=enriched_payload,
            token=token,
        )

        self.printer.verbose("Done")
