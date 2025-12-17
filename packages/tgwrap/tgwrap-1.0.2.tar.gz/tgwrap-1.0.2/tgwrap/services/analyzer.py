"""Service responsible for plan analysis logic."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Iterable

from ..analyze import run_analyze


class AnalyzerService:  # pylint: disable=too-few-public-methods
    """Encapsulate the `tgwrap analyze` workflow."""

    def __init__(
        self,
        *,
        printer,
        command_constructor,
        graph_runner,
        azure_service,
        planfile_name: str,
        separator: str,
    ) -> None:
        self.printer = printer
        self.command_constructor = command_constructor
        self.graph_runner = graph_runner
        self.azure = azure_service
        self.planfile_name = planfile_name
        self.separator = separator

    def run(
        self,
        *,
        queue_exclude_external: bool,
        working_dir: str | None,
        start_at_step: float,
        out: bool,
        analyze_config: str | None,
        ignore_attributes: Iterable[str],
        include_dirs: Iterable[str],
        exclude_dirs: Iterable[str],
        planfile_dir: str | None,
        data_collection_endpoint: str | None,
        terragrunt_args: Iterable[str],
        load_config,
    ) -> None:
        """Execute the analyze workflow."""

        def calculate_score(major: int, medium: int, minor: int) -> float:
            return major * 10 + medium + minor / 10

        self.printer.verbose("Attempting to 'analyze'")
        if terragrunt_args:
            self.printer.verbose(
                f"- with additional parameters: {' '.join(terragrunt_args)}"
            )

        if start_at_step > 1 or not queue_exclude_external or not planfile_dir:
            if self.printer.print_verbose:
                self.printer.warning(
                    "Use terragrunt for module selection, this will be significantly slower!"
                )

            use_native_tf = False
            tg_args_list = list(terragrunt_args)

            if not any(arg in ["--json", "-json"] for arg in tg_args_list):
                tg_args_list.append("--json")

            if self.planfile_name not in tg_args_list:
                tg_args_list.append(self.planfile_name)

            cmd = self.command_constructor.construct_command(
                command="show",
                debug=False,
                queue_exclude_external=queue_exclude_external,
                terragrunt_args=tg_args_list,
            )
        else:
            if self.printer.print_verbose:
                self.printer.success(
                    "Use native tofu|terraform (by using tf alias) for module selection"
                )

            use_native_tf = True
            cmd = f"tf show --json {self.planfile_name}"

        config = None
        if analyze_config:
            self.printer.verbose(f"\nAnalyze using config {analyze_config}")
            config = load_config(analyze_config)

        ts_validation_successful = True
        details = {}
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix="tgwrap-", delete=False
            ) as handle:
                temp_file_path = handle.name
                self.printer.verbose(
                    f"Opened temp file for output collection: {handle.name}"
                )

                self.graph_runner.run(
                    command=cmd,
                    queue_exclude_external=queue_exclude_external,
                    collect_output_file=handle,
                    working_dir=working_dir,
                    start_at_step=start_at_step,
                    include_dirs=include_dirs,
                    exclude_dirs=exclude_dirs,
                    use_native_terraform=use_native_tf,
                    add_to_workdir=planfile_dir if use_native_tf else None,
                )

            with open(temp_file_path, encoding="utf-8") as reader:
                for line in reader:
                    split_line = line.split(self.separator)
                    module = split_line[0]

                    try:
                        plan_file = split_line[1]
                    except IndexError:
                        self.printer.warning(
                            f"Could not determine planfile: {line[:100]}"
                        )
                        continue

                    try:
                        if len(plan_file) > 1:
                            data = json.loads(plan_file)

                            if "exception" in data:
                                raise RuntimeError(data["exception"])

                            details[module], ts_success = run_analyze(
                                config=config,
                                data=data,
                                verbose=self.printer.print_verbose,
                                ignore_attributes=ignore_attributes,
                            )

                            if not ts_success:
                                ts_validation_successful = False
                        else:
                            self.printer.warning(
                                f"Planfile for module {module} is empty"
                            )
                    except Exception as exc:  # pylint: disable=broad-except
                        self.printer.error(
                            f"Error processing module {module}: {exc}",
                            print_line_before=True,
                        )
                        self.printer.error(plan_file)
                        raise
        finally:
            if temp_file_path:
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass

        total_drifts = {
            "creations": 0,
            "updates": 0,
            "deletions": 0,
            "minor": 0,
            "medium": 0,
            "major": 0,
            "unknown": 0,
            "total": 0,
            "ignorable_updates": 0,
            "outputs": 0,
        }

        severity_printers = {
            "creations": self.printer.success,
            "updates": self.printer.warning,
            "deletions": self.printer.error,
            "unauthorized": self.printer.error,
            "unknowns": self.printer.warning,
        }

        self.printer.header("Analysis results:", print_line_before=True)

        for key, value in details.items():
            self.printer.header(f"Module: {key}")
            if not value["all"] and not value["outputs"]:
                self.printer.success("No changes detected")

            for item in [
                "creations",
                "updates",
                "deletions",
                "unauthorized",
                "unknowns",
            ]:
                printer_method = severity_printers.get(item, self.printer.normal)
                if value[item]:
                    printer_method(f"{item.title()} ({len(value[item])}):")
                    for module_value in value[item]:
                        total_drifts[item] = total_drifts.get(item, 0) + 1
                        printer_method(f"-> {module_value}")
                else:
                    printer_method(f"{item.title()}: 0")

            if value["ignorable_updates"]:
                self.printer.success("Updates (ignored):")
                for module_value in value["ignorable_updates"]:
                    total_drifts["ignorable_updates"] += 1
                    self.printer.normal(f"-> {module_value}")
            else:
                self.printer.success(
                    f'Updates (ignored): {len(value["ignorable_updates"])} resources (add --verbose to see them)'
                )
            if value["outputs"]:
                self.printer.success("Output changes:")
                for module_value in value["outputs"]:
                    total_drifts["outputs"] = total_drifts["outputs"] + 1
                    self.printer.normal(f"-> {module_value}")

        if not analyze_config:
            self.printer.error(
                "Analyze config file is not set, this is required for checking for unauthorized deletions and drift detection scores!",
                print_line_before=True,
            )
        else:
            for value in details.values():
                for drift_type in ["minor", "medium", "major", "unknown", "total"]:
                    total_drifts[drift_type] += value["drifts"][drift_type]

                value["drifts"]["score"] = calculate_score(
                    major=value["drifts"]["major"],
                    medium=value["drifts"]["medium"],
                    minor=value["drifts"]["minor"],
                )

            total_drift_score = calculate_score(
                major=total_drifts["major"],
                medium=total_drifts["medium"],
                minor=total_drifts["minor"],
            )
            total_drifts["score"] = total_drift_score

            self.printer.header(
                f"Drift score: {total_drift_score} ({total_drifts['major']}.{total_drifts['medium']}.{total_drifts['minor']})"
            )
            if total_drifts["unknown"] > 0:
                self.printer.warning(
                    f"For {total_drifts['unknown']} resources, drift score is not configured, please update configuration!"
                )
                self.printer.warning("- Unknowns:")
                for key, value in details.items():
                    for module_value in value["unknowns"]:
                        self.printer.warning(f" -> {module_value}")

        if out or data_collection_endpoint:
            output = {
                "details": [],
                "summary": {},
            }
            for key, value in details.items():
                copy_value = value.copy()
                copy_value["module"] = key
                output["details"].append(copy_value)

            output["summary"] = total_drifts

            if out:
                print(json.dumps(output, indent=4))

            if data_collection_endpoint:
                self.azure.post_analyze_results(
                    data_collection_endpoint=data_collection_endpoint,
                    payload=output,
                )

        if not ts_validation_successful:
            self.printer.error(
                "Analysis detected unauthorised deletions, please check your configuration!!!"
            )
            sys.exit(1)
