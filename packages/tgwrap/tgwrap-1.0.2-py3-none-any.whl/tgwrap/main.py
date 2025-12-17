"""High-level wrapper orchestrating Terragrunt workflows."""

from __future__ import annotations

import glob
import json
import os
import shlex
import shutil
import subprocess
import sys

import networkx as nx
import yaml

from .command_constructor import TgCommandConstructor
from .core.constants import STAGES
from .inspector import AzureInspector
from .printer import Printer
from .services.analyzer import AnalyzerService
from .services.azure import AzureService
from .services.deployer import DeploymentService
from .services.graph_runner import GraphRunner

__all__ = ["STAGES", "TgWrap"]

class TgWrap:
    """User-facing façade that coordinates the various tgwrap services."""

    SEPARATOR = ":|:"
    VERSION_FILE = "version.hcl"
    LATEST_VERSION = "latest"
    PLANFILE_NAME = "planfile"
    TG_FILE = "terragrunt.hcl"
    TG_SOURCE_VAR = "TG_SOURCE"

    def __init__(self, verbose: bool, check_tg_source: bool = False, skip_version_check: bool = True) -> None:
        self.printer = Printer(verbose)

        self.command_constructor = TgCommandConstructor(
            printer=self.printer,
            check_tg_source=check_tg_source,
            skip_version_check=skip_version_check,
        )
        self.graph_runner = GraphRunner(
            self.printer,
            tg_file=self.TG_FILE,
            planfile_name=self.PLANFILE_NAME,
            separator=self.SEPARATOR,
        )
        self.azure_service = AzureService(self.printer)
        self.deployment_service = DeploymentService(
            printer=self.printer,
            tg_file=self.TG_FILE,
            latest_version=self.LATEST_VERSION,
            version_file=self.VERSION_FILE,
            yaml_loader=self._load_yaml_file,
        )
        self.analyzer_service = AnalyzerService(
            printer=self.printer,
            command_constructor=self.command_constructor,
            graph_runner=self.graph_runner,
            azure_service=self.azure_service,
            planfile_name=self.PLANFILE_NAME,
            separator=self.SEPARATOR,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_yaml_file(self, filepath: str):
        try:
            # Validate file path for security
            normalized_path = os.path.normpath(filepath.strip())
            if '..' in normalized_path:
                self.printer.error("Invalid file path: path traversal detected")
                sys.exit(1)

            with open(normalized_path, encoding="utf-8") as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            self.printer.error(f"Cannot parse YAML file {os.path.basename(filepath)}: Invalid syntax")
            if self.printer.print_verbose:
                self.printer.error(f"Parser error: {str(e)}")
            sys.exit(1)
        except FileNotFoundError:
            self.printer.error(f"YAML file not found: {os.path.basename(filepath)}")
            sys.exit(1)
        except PermissionError:
            self.printer.error(f"Permission denied accessing file: {os.path.basename(filepath)}")
            sys.exit(1)
        except OSError as exc:
            self.printer.error(f"Error loading YAML file: {os.path.basename(filepath)}")
            if self.printer.print_verbose:
                self.printer.error(f"Error details: {exc}")
            sys.exit(1)

    def _show_version(self, working_dir: str | None) -> None:
        """Show the version information of the tools"""

        for path in [
            "~/.tenv/Terragrunt/.lock",
            "~/.tenv/OpenTofu/.lock",
            "~/.tenv/Terraform/.lock",
        ]:
            if os.path.exists(os.path.expanduser(path)):
                self.printer.warning(
                    f"Detected '{path}' file, which may cause version check to hang. Consider removing it."
                )

        self.printer.header("Version info")
        for cmd in ["terragrunt --version", "tf --version", "tgwrap --version"]:
            cmd_args = shlex.split(cmd)
            try:
                rc = subprocess.run(
                    cmd_args,
                    check=True,
                    stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                    stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
                    cwd=working_dir if working_dir else None,
                )
                self.printer.verbose(rc)
            except FileNotFoundError:
                self.printer.warning(
                    f"Command '{cmd_args[0]}' not found on PATH, skipping version check."
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        command: str,
        debug: bool,
        no_lock: bool,
        update: bool,
        upgrade: bool,
        planfile: bool,
        auto_approve: bool,
        run_all: bool,
        clean: bool,
        working_dir: str | None,
        queue_exclude_external: bool,
        step_by_step: bool,
        continue_on_error: bool,
        start_at_step: float,
        include_dirs: list[str],
        exclude_dirs: list[str],
        analyze_after_plan: bool | None,
        analyze_config: str | None,
        ignore_attributes: list[str],
        planfile_dir: str | None,
        data_collection_endpoint: str | None,
        terragrunt_args: list[str],
    ) -> None:  # pylint: disable=too-many-arguments,too-many-locals
        """Execute a Terragrunt command across multiple modules."""

        self.printer.verbose(f"Attempting to execute 'run {command}'")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        if self.printer.print_verbose:
            self._show_version(working_dir=working_dir)

        if not run_all and not step_by_step:
            check_for_file = self.TG_FILE
            if working_dir:
                check_for_file = os.path.join(working_dir, check_for_file)

            if not os.path.isfile(check_for_file):
                self.printer.error(
                    f"{check_for_file} not found, this seems not to be a terragrunt module directory!"
                )
                sys.exit(1)

        modifying_command = command.lower() in {"apply", "destroy"}
        auto_approve = auto_approve if modifying_command else True

        cmd = self.command_constructor.construct_command(
            command=command,
            debug=debug,
            queue_exclude_external=True if step_by_step else queue_exclude_external,
            run_all=run_all,
            step_by_step=step_by_step,
            non_interactive=True if step_by_step else auto_approve,
            no_auto_approve=False if step_by_step else (not auto_approve),
            no_lock=no_lock,
            update=update,
            upgrade=upgrade,
            planfile=planfile,
            working_dir=None if step_by_step else working_dir,
            include_dirs=[] if step_by_step else include_dirs,
            exclude_dirs=[] if step_by_step else exclude_dirs,
            terragrunt_args=terragrunt_args,
        )

        if clean:
            self.clean(working_dir=working_dir)

        rc = None
        if step_by_step:
            self.printer.verbose(
                f"This command will be executed for each individual module:\n$ {cmd}"
            )

            include_dirs_glob = [
                dir.rstrip(f".{os.path.sep}*") + f"{os.path.sep}*"
                for dir in include_dirs
            ]
            exclude_dirs_glob = [
                dir.rstrip(f".{os.path.sep}*") + f"{os.path.sep}*"
                for dir in exclude_dirs
            ]

            self.graph_runner.run(
                command=cmd,
                queue_exclude_external=queue_exclude_external,
                working_dir=working_dir,
                ask_for_confirmation=not auto_approve,
                continue_on_error=continue_on_error,
                start_at_step=start_at_step,
                backwards=(command.lower() in {"destroy"}),
                include_dirs=include_dirs_glob,
                exclude_dirs=exclude_dirs_glob,
                display_groups=True,
            )
        else:
            rc = subprocess.run(shlex.split(cmd), check=False)
            self.printer.verbose(rc)

        analyze_after_plan = run_all if analyze_after_plan is None else analyze_after_plan

        if rc and rc.returncode != 0:
            self.printer.error(
                f"An error occurred (return code {rc.returncode}) while executing command: {command.lower()}"
            )
            self.printer.verbose(f"Executed command: {json.dumps(rc.args, indent=2)}")
        elif analyze_after_plan and command.lower() == "plan":
            self.printer.verbose("Analyze after plan requested")
            self.analyzer_service.run(
                queue_exclude_external=queue_exclude_external,
                working_dir=working_dir,
                start_at_step=0,
                out=None,
                analyze_config=analyze_config,
                ignore_attributes=ignore_attributes,
                include_dirs=include_dirs,
                exclude_dirs=exclude_dirs,
                planfile_dir=planfile_dir,
                data_collection_endpoint=data_collection_endpoint,
                terragrunt_args=terragrunt_args,
                load_config=self._load_yaml_file,
            )

        if rc:
            sys.exit(rc.returncode)

    def analyze(
        self,
        queue_exclude_external,
        working_dir,
        start_at_step,
        out,
        analyze_config,
        ignore_attributes,
        include_dirs,
        exclude_dirs,
        planfile_dir,
        data_collection_endpoint,
        terragrunt_args,
    ):
        """Analyze Terragrunt plan files and optionally emit telemetry."""
        self.analyzer_service.run(
            queue_exclude_external=queue_exclude_external,
            working_dir=working_dir,
            start_at_step=start_at_step,
            out=out,
            analyze_config=analyze_config,
            ignore_attributes=ignore_attributes,
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            planfile_dir=planfile_dir,
            data_collection_endpoint=data_collection_endpoint,
            terragrunt_args=terragrunt_args,
            load_config=self._load_yaml_file,
        )

    def sync(
        self,
        source_stage,
        target_stage,
        source_domain,
        target_domain,
        module,
        auto_approve,
        clean,
        include_dotenv_file,
        working_dir,
    ):
        """Synchronise configuration for a single module between stages/domains."""
        self.deployment_service.sync(
            source_stage=source_stage,
            target_stage=target_stage,
            source_domain=source_domain,
            target_domain=target_domain,
            module=module,
            auto_approve=auto_approve,
            clean=clean,
            include_dotenv_file=include_dotenv_file,
            working_dir=working_dir,
        )

    def sync_dir(
        self,
        source_directory,
        target_directory,
        auto_approve,
        clean,
        include_dotenv_file,
        working_dir,
    ):
        """Synchronise entire configuration directories."""
        self.deployment_service.sync_dir(
            source_directory=source_directory,
            target_directory=target_directory,
            auto_approve=auto_approve,
            clean=clean,
            include_dotenv_file=include_dotenv_file,
            working_dir=working_dir,
        )

    def deploy(
        self,
        manifest_file,
        version_tag,
        target_stages,
        include_global_config_files,
        auto_approve,
        working_dir,
    ):
        """Deploy Terragrunt sources referenced in the manifest."""
        self.deployment_service.deploy(
            manifest_file=manifest_file,
            version_tag=version_tag,
            target_stages=target_stages,
            include_global_config_files=include_global_config_files,
            auto_approve=auto_approve,
            working_dir=working_dir,
        )

    def check_deployments(self, repo_url, levels_deep, working_dir, out):
        """Report freshness of deployed versions relative to a repository."""
        self.deployment_service.check_deployments(
            repo_url=repo_url,
            levels_deep=levels_deep,
            working_dir=working_dir,
            out=out,
        )

    def show_graph(
        self,
        backwards,
        exclude_external_dependencies,
        analyze,
        working_dir,
        include_dirs,
        exclude_dirs,
        terragrunt_args,
    ):
        """Display the dependency graph and optional metrics."""
        self.printer.verbose("Attempting to show dependencies")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        graph = self.graph_runner.get_di_graph(
            backwards=backwards, working_dir=working_dir
        )
        try:
            graph.remove_node(r"\n")
        except nx.exception.NetworkXError:
            pass

        groups = self.graph_runner.prepare_groups(
            graph=graph,
            exclude_external_dependencies=exclude_external_dependencies,
            working_dir=working_dir,
            include_dirs=include_dirs or [],
            exclude_dirs=exclude_dirs or [],
        )

        if not groups:
            self.printer.error("No groups in scope, this smells fishy!")
        else:
            self.printer.header("The following groups are in scope:")
            for idx, group in enumerate(groups):
                self.printer.normal(f"\nGroup {idx + 1}:")
                for directory in group:
                    self.printer.normal(f"- {directory}")

        if analyze:
            def set_json_dumps_default(obj):
                if isinstance(obj, set):
                    return list(obj)
                raise TypeError

            def calculate_dependencies(graph_obj):
                dependencies = {}
                for node in graph_obj.nodes:
                    out_degree = graph_obj.out_degree(node)
                    in_degree = graph_obj.in_degree(node)
                    total_degree = out_degree + in_degree
                    dependencies[node] = {
                        "dependencies": out_degree,
                        "dependent_on_it": in_degree,
                        "total": total_degree,
                    }
                return dependencies

            def calculate_graph_metrics(graph_obj):
                metrics = {}
                metrics["degree_centrality"] = {
                    "values": dict(
                        sorted(
                            nx.degree_centrality(graph_obj).items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ),
                    "description": "Shows the degree of each node relative to the number of nodes in the graph",
                }
                metrics["betweenness_centrality"] = {
                    "values": dict(
                        sorted(
                            nx.betweenness_centrality(graph_obj).items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ),
                    "description": "Indicates nodes that frequently lie on shortest paths between other nodes",
                }
                metrics["closeness_centrality"] = {
                    "values": dict(
                        sorted(
                            nx.closeness_centrality(graph_obj).items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ),
                    "description": "Reflects how quickly a node can reach other nodes in the graph",
                }
                metrics["strongly_connected_components"] = {
                    "values": list(nx.strongly_connected_components(graph_obj)),
                    "description": "Lists sets of nodes that are mutually reachable",
                }
                metrics["weakly_connected_components"] = {
                    "values": list(nx.weakly_connected_components(graph_obj)),
                    "description": "Lists sets of nodes that are connected disregarding edge directions",
                }
                if nx.is_strongly_connected(graph_obj):
                    metrics["average_path_length"] = {
                        "values": nx.average_shortest_path_length(graph_obj),
                        "description": "Shows the average shortest path length, indicating the graph's efficiency",
                    }
                return metrics

            self.printer.header("Graph analysis", print_line_before=True)
            self.printer.bold("Dependencies counts:", print_line_before=True)
            dependencies = calculate_dependencies(graph)
            sorted_dependencies = sorted(
                dependencies.items(), key=lambda x: x[1]["total"], reverse=True
            )
            for node, counts in sorted_dependencies:
                msg = f"""
{node} ->
\ttotal:        {counts['total']}
\tdependent on: {counts['dependent_on_it']}
\tdependencies: {counts['dependencies']}
"""
                self.printer.normal(msg)

            metrics = calculate_graph_metrics(graph)
            for metric, item in metrics.items():
                self.printer.bold(f"Metric: {metric}")
                self.printer.normal(f'Description: {item["description"]}')
                self.printer.normal(
                    json.dumps(item["values"], indent=2, default=set_json_dumps_default)
                )

    def clean(self, working_dir):
        """Remove Terragrunt caches and debug artefacts."""
        if not working_dir:
            working_dir = os.getcwd()
        for root, dirs, _ in os.walk(working_dir):
            for directory in dirs:
                if directory == ".terragrunt-cache":
                    shutil.rmtree(os.path.join(root, directory))

            for pattern in glob.glob(os.path.join(root, "terragrunt-debug*.json")):
                try:
                    os.remove(pattern)
                except OSError as exc:
                    self.printer.warning(f"Could not remove {pattern}: {exc}")

        self.printer.normal("Cleaned the temporary files")

    def inspect(
        self,
        domain: str,
        substack: str,
        stage: str,
        azure_subscription_id: str,
        config_file: str,
        out: bool,
        data_collection_endpoint: str,
    ):
        """Inspect an Azure environment against the provided configuration."""
        inspector = AzureInspector(
            subscription_id=azure_subscription_id,
            domain=domain,
            substack=substack,
            stage=stage,
            config_file=config_file,
            verbose=self.printer.print_verbose,
        )

        try:
            results = inspector.inspect()

            exit_code = 0
            self.printer.header("Inspection status:", print_line_before=True)
            for key, value in results.items():
                resource_status = value.get("inspect_status_code", "NC")
                resource_message = value.get("inspect_message", "not found")
                msg = (
                    f"{value['type']}: {key}\n"
                    f"        -> Resource:  {resource_status} ({resource_message})"
                )
                if "rbac_assignment_status_code" in value:
                    rbac_status = value["rbac_assignment_status_code"]
                    rbac_message = value.get("rbac_assignment_message")
                    msg = msg + f"\n        -> RBAC: {rbac_status} ({rbac_message})"
                if (
                    value["inspect_status_code"] != "OK"
                    or value.get("rbac_assignment_status_code", "OK") == "NOK"
                ):
                    self.printer.error(msg=msg)
                    exit_code += 1
                else:
                    self.printer.success(msg=msg)

            if out or data_collection_endpoint:
                payload = []
                for key, value in results.items():
                    value_with_key = value.copy()
                    value_with_key["resource_type"] = value_with_key.pop("type")
                    value_with_key["resource"] = key
                    value_with_key["domain"] = domain
                    value_with_key["substack"] = substack
                    value_with_key["stage"] = stage
                    value_with_key["subscription_id"] = azure_subscription_id
                    payload.append(value_with_key)

                if out:
                    print(json.dumps(payload, indent=2))

                if data_collection_endpoint:
                    self.azure_service.post_to_dce(
                        data_collection_endpoint=data_collection_endpoint,
                        payload=payload,
                    )

            return exit_code
        except Exception as exc:  # pylint: disable=broad-except
            self.printer.normal(f"Exception occurred: {exc}")

            if self.printer.print_verbose:
                raise

            return -1
