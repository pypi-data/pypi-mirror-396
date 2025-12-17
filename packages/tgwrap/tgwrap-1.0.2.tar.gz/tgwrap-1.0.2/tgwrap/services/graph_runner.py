"""Service responsible for executing Terragrunt dependency graphs."""

from __future__ import annotations

import fnmatch
import json
import os
import shlex
import subprocess
import sys
import tempfile
from typing import Iterable

import click
import networkx as nx


class GraphRunner:
    """Execute commands following the Terragrunt dependency graph."""

    def __init__(
        self,
        printer,
        *,
        tg_file: str = "terragrunt.hcl",
        planfile_name: str = "planfile",
        separator: str = ":|:",
    ) -> None:
        self.printer = printer
        self.tg_file = tg_file
        self.planfile_name = planfile_name
        self.separator = separator

    # Public API ---------------------------------------------------------

    def run(
        self,
        command: str,
        queue_exclude_external: bool,
        start_at_step: float,
        *,
        ask_for_confirmation: bool = False,
        collect_output_file=None,
        backwards: bool = False,
        working_dir: str | None = None,
        include_dirs: Iterable[str] | None = None,
        exclude_dirs: Iterable[str] | None = None,
        use_native_terraform: bool = False,
        add_to_workdir: str | None = None,
        continue_on_error: bool = False,
        display_groups: bool | None = None,
    ) -> None:
        """Execute a command for each node in the dependency graph."""

        if use_native_terraform:
            module_dirs = self._get_subdirectories_with_file(
                root_dir=working_dir if working_dir else ".",
                file_name=self.tg_file,
                exclude_external_dependencies=queue_exclude_external,
                include_dirs=include_dirs or [],
                exclude_dirs=exclude_dirs or [],
            )
            groups = [module_dirs]
        else:
            graph = self.get_di_graph(backwards=backwards, working_dir=working_dir)
            groups = self.prepare_groups(
                graph=graph,
                exclude_external_dependencies=queue_exclude_external,
                working_dir=working_dir,
                include_dirs=include_dirs or [],
                exclude_dirs=exclude_dirs or [],
            )

        if display_groups is None:
            display_groups = ask_for_confirmation or self.printer.print_verbose

        if not groups:
            self.printer.error("No groups to process, this smells fishy!")
        elif display_groups:
            self.printer.header(
                "The following groups will be processed (sequentially):"
            )
            for idx, group in enumerate(groups):
                self.printer.normal(f"\nGroup {idx + 1}:")
                for module in group:
                    self.printer.normal(f"- {module}")

        if ask_for_confirmation:
            response = input("\nDo you want to continue? (y/N) ")
            if response.lower() != "y":
                sys.exit(1)

        counter = 0
        nbr_of_groups = len(groups)
        for idx, group in enumerate(groups):
            group_nbr = idx + 1
            self.printer.header(f"Group {group_nbr}")
            self.printer.verbose(group)

            nbr_of_modules = len(group)
            for idx2, module in enumerate(group):
                counter += 1
                module_nbr = idx2 + 1
                progress = (
                    f"module {module_nbr} (of {nbr_of_modules}) of group {group_nbr} (of {nbr_of_groups})"
                )

                step_nbr = group_nbr + module_nbr / 100
                if step_nbr < start_at_step:
                    self.printer.normal(
                        f"Skip step {step_nbr}, start at {start_at_step}"
                    )
                    continue

                stop_processing = self._run_graph_step(
                    command=command,
                    working_dir=working_dir,
                    add_to_workdir=add_to_workdir,
                    unit=module,
                    collect_output_file=collect_output_file,
                    progress=progress,
                )

                if stop_processing and not continue_on_error:
                    self.printer.warning(
                        f"Processing needs to be stopped at step {step_nbr}."
                    )
                    self.printer.normal(
                        "After you've fixed the problem, you can continue where you left off by adding '--start-at-step {step_nbr}'."
                    )
                    sys.exit(1)

        if self.printer.print_verbose:
            total_items = sum(len(group) for group in groups)
            self.printer.verbose(f"Executed {group_nbr} groups and {total_items} steps")

    def get_di_graph(
        self, *, backwards: bool = False, working_dir: str | None = None
    ) -> nx.DiGraph:
        """Return the directed dependency graph from terragrunt."""

        try:
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix="tgwrap-", delete=True
            ) as temp_file:
                self.printer.verbose(
                    f"Opened temp file for graph collection: {temp_file.name}"
                )

                working_dir_stmt = (
                    f"--working-dir {working_dir}" if working_dir else ""
                )
                command = f"terragrunt dag graph --non-interactive {working_dir_stmt}"
                rc = subprocess.run(
                    shlex.split(command),
                    text=True,
                    stdout=temp_file,
                    check=True,
                )
                self.printer.verbose(rc)

                temp_file.flush()

                graph = nx.DiGraph(nx.nx_pydot.read_dot(temp_file.name))
                if not backwards:
                    graph = graph.reverse()
                else:
                    self.printer.verbose("Graph will be interpreted backwards!")
        except TypeError as exc:
            self.printer.error(
                "terragrunt has problems generating the graph, check the dependencies please!"
            )
            self.printer.error("once fixed, you can run 'tgwrap show-graph' to verify.")
            raise click.ClickException(exc)
        except Exception as exc:  # pylint: disable=broad-except
            self.printer.error(exc)
            raise click.ClickException(exc) from exc

        return graph

    def prepare_groups(
        self,
        *,
        graph: nx.DiGraph,
        exclude_external_dependencies: bool,
        working_dir: str | None,
        include_dirs: Iterable[str],
        exclude_dirs: Iterable[str],
    ) -> list[list[str]]:
        """Return the list of execution groups derived from the graph."""

        working_dir = os.path.abspath(working_dir) if working_dir else os.getcwd()
        self.printer.verbose(f"Check for working dir: {working_dir}")

        exclude_dirs = [dir.rstrip(os.path.sep) for dir in exclude_dirs]
        include_dirs = [dir.rstrip(os.path.sep) for dir in include_dirs]

        self.printer.verbose(f"Include dirs: {'; '.join(include_dirs)}")
        self.printer.verbose(f"Exclude dirs: {'; '.join(exclude_dirs)}")

        groups: list[list[str]] = []
        for group in nx.topological_generations(graph):
            try:
                group.remove("\\n")
            except ValueError:
                pass

            for idx, directory in enumerate(group):
                include = self._check_directory_inclusion(
                    directory=directory,
                    working_dir=working_dir,
                    exclude_external_dependencies=exclude_external_dependencies,
                    include_dirs=include_dirs,
                    exclude_dirs=exclude_dirs,
                )

                if not include:
                    group[idx] = None

            group = [item for item in group if item]
            if group:
                groups.append(group)

        return groups

    # Internal helpers ---------------------------------------------------

    def _check_directory_inclusion(
        self,
        *,
        directory: str,
        working_dir: str,
        exclude_external_dependencies: bool,
        include_dirs: Iterable[str],
        exclude_dirs: Iterable[str],
    ) -> bool:
        dir_excluded = False
        dir_included = not include_dirs
        dir_excluded_reason = ""

        directory = directory.rstrip(os.path.sep)
        include_dirs = [dir.lstrip(f".{os.path.sep}") for dir in include_dirs]
        exclude_dirs = [dir.lstrip(f".{os.path.sep}") for dir in exclude_dirs]

        if exclude_external_dependencies and self._is_external_dependency(
            directory, working_dir
        ):
            dir_excluded = True
            dir_excluded_reason = "directory out of scope"
        else:
            for pattern in exclude_dirs:
                if fnmatch.fnmatch(directory, pattern):
                    dir_excluded = True
                    dir_excluded_reason = "directory explicitly excluded"
                elif pattern.endswith("/*"):
                    base_pattern = pattern[:-2]
                    wildcard_pattern = base_pattern + "*"
                    if fnmatch.fnmatch(directory, base_pattern) or fnmatch.fnmatch(
                        directory, wildcard_pattern
                    ):
                        dir_excluded = True
                        dir_excluded_reason = "directory explicitly excluded"

            for pattern in include_dirs:
                if fnmatch.fnmatch(directory, pattern):
                    dir_included = True
                elif pattern.endswith("/*"):
                    base_pattern = pattern[:-2]
                    wildcard_pattern = base_pattern + "*"
                    if fnmatch.fnmatch(directory, base_pattern) or fnmatch.fnmatch(
                        directory, wildcard_pattern
                    ):
                        dir_included = True

        if dir_excluded:
            self.printer.verbose(
                f"- Remove directory '{directory}': {dir_excluded_reason}"
            )
        elif not dir_included:
            self.printer.verbose(
                f"- Remove directory '{directory}': specific list of include dirs given"
            )
        else:
            self.printer.verbose(f"+ Include directory: {directory}")

        return dir_included and not dir_excluded

    def _get_subdirectories_with_file(
        self,
        *,
        root_dir: str,
        file_name: str,
        exclude_external_dependencies: bool,
        include_dirs: Iterable[str],
        exclude_dirs: Iterable[str],
        exclude_hidden_dir: bool = True,
    ) -> list[str]:
        current_dir = os.getcwd()
        os.chdir(root_dir)

        try:
            exclude_dirs = [dir.rstrip(os.path.sep) for dir in exclude_dirs]
            include_dirs = [dir.rstrip(os.path.sep) for dir in include_dirs]

            subdirectories: list[str] = []
            for directory, dirnames, filenames in os.walk("."):
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not (d.startswith(".") and exclude_hidden_dir)
                ]

                if file_name in filenames:
                    self.printer.verbose(f"Directory found: {directory}")

                    include = self._check_directory_inclusion(
                        directory=directory.lstrip(f".{os.path.sep}"),
                        working_dir=".",
                        exclude_external_dependencies=exclude_external_dependencies,
                        include_dirs=include_dirs,
                        exclude_dirs=exclude_dirs,
                    )

                    if include:
                        subdirectories.append(directory.lstrip(f".{os.path.sep}"))
        finally:
            os.chdir(current_dir)

        return subdirectories

    def _run_graph_step(
        self,
        *,
        command: str,
        working_dir: str | None,
        add_to_workdir: str | None,
        unit: str,
        collect_output_file,
        progress: str,
        output_queue=None,
        semaphore=None,
    ) -> bool:
        unit_identifier = f"{unit}{self.separator}"

        stop_processing = False
        error = False
        skip = False
        output = None
        error_msg = None
        messages = ""
        execution_dir = unit

        try:
            if semaphore:
                semaphore.acquire()

            execution_dir = (
                os.path.join(os.path.abspath(working_dir), unit)
                if working_dir and not os.path.isabs(unit)
                else unit
            )

            if add_to_workdir:
                execution_dir = os.path.join(execution_dir, add_to_workdir)

            self.printer.verbose(
                f"Execute command: {command} in working dir: {execution_dir}"
            )

            self.printer.header(
                f"\n\nStart processing unit: {unit} ({progress})\n\n",
                print_line_before=True,
            )

            if collect_output_file:
                self.printer.verbose("Use an output file for output collection")
                collect_output_file.write(unit_identifier)
                collect_output_file.flush()
            elif output_queue:
                self.printer.verbose("Use an output queue for output collection")
                collect_output_file = subprocess.PIPE

            messages = ""

            if os.path.exists(execution_dir):
                with tempfile.NamedTemporaryFile(
                    mode="w+", prefix="tgwrap-", delete=False
                ) as handle:
                    error_path = handle.name
                    self.printer.verbose(
                        f"Opened temp file for error collection: {error_path}"
                    )

                with open(error_path, "w", encoding="utf-8") as err_handle:
                    rc = subprocess.run(
                        shlex.split(command),
                        text=True,
                        cwd=execution_dir,
                        stdout=collect_output_file if collect_output_file else sys.stdout,
                        stderr=err_handle,
                        check=False,
                    )

                self.printer.verbose(f"arguments: {rc.args}")
                self.printer.verbose(f"returncode: {rc.returncode}")
                if getattr(rc, "stdout", None):
                    self.printer.verbose(f"stdout: {rc.stdout[:200]}")

                with open(error_path, encoding="utf-8") as reader:
                    messages = reader.read()

                error, skip = self._analyze_results(rc=rc, messages=messages)
                output = rc.stdout if getattr(rc, "stdout", None) else "\n"

                os.remove(error_path)
            else:
                skip = True
                output = "\n"
                self.printer.verbose(f"Directory '{execution_dir}' does not exist")

            if skip:
                self.printer.verbose("Module is skipped")

            if error:
                raise RuntimeError(
                    f"An error situation detected while processing the terragrunt dependencies graph in directory {unit}"
                )

            self.printer.success(f"Directory {unit} processed successfully")

        except FileNotFoundError:
            error_msg = f"Directory {execution_dir} not found, continue"
            self.printer.warning(error_msg)
        except Exception as exc:  # pylint: disable=broad-except
            error_msg = f"Error occurred:\n{exc}"
            self.printer.error(error_msg)
            self.printer.error("Full stack:", print_line_before=True)
            self.printer.normal(messages, print_line_after=True)
            self.printer.normal(f"Directory {unit} failed!")
            stop_processing = True
        finally:
            if error_msg:
                output = json.dumps({"exception": error_msg})

            try:
                if output_queue:
                    output_queue.put(f"{unit_identifier}{output}")
                elif collect_output_file and (skip or error):
                    collect_output_file.write(output)
                    collect_output_file.flush()
            except Exception as exc:  # pylint: disable=broad-except
                self.printer.error(f"Error writing the results: {exc}")

            if semaphore:
                semaphore.release()

        return stop_processing

    def _analyze_results(self, *, rc, messages: str) -> tuple[bool, bool]:
        error = False
        skip = False

        messages_lower = messages.lower()
        if rc.returncode != 0 or "error" in messages_lower:
            error = True
        if "skipping terragrunt module" in messages_lower:
            skip = True

        return error, skip

    def _is_external_dependency(self, directory: str, working_dir: str) -> bool:
        try:
            abs_working_dir = os.path.abspath(working_dir)
            abs_directory = os.path.abspath(directory)
            return not abs_directory.startswith(abs_working_dir)
        except Exception:  # pylint: disable=broad-except
            return False
