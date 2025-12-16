"""WorkflowModule for Artificer CLI integration."""

import os
import shlex
from typing import TYPE_CHECKING

import click
from artificer.cli.module import ArtificerModule

from .operations import list_workflows, pause_workflow, resume_workflow
from .workflow import Workflow

if TYPE_CHECKING:
    from artificer.cli.config import ArtificerConfig


class WorkflowModule(ArtificerModule):
    """Module providing CLI commands for workflow management."""

    @classmethod
    def register(cls, cli: click.Group, config: "ArtificerConfig") -> None:
        """Register workflow commands with the CLI."""
        # Import workflow entrypoint and get workflow config
        workflows_config = cls._import_workflow_entrypoint(config)

        @cli.group()
        def workflows():
            """Manage workflows."""
            pass

        @workflows.command("list")
        @click.option(
            "--status",
            type=click.Choice(
                ["in_progress", "completed", "failed", "paused"], case_sensitive=False
            ),
            help="Filter by workflow status",
        )
        def list_cmd(status: str | None):
            """List all workflows."""
            # Convert to uppercase for internal status enum
            status_filter = status.upper() if status else None
            results = list_workflows(status=status_filter)

            if not results:
                click.echo("No workflows found.")
                return

            # Print header
            click.echo(f"{'WORKFLOW ID':<40} {'STATUS':<12} {'START TIME':<20}")
            click.echo("-" * 72)

            for wf in results:
                click.echo(
                    f"{wf['workflow_id']:<40} {wf['status']:<12} {wf['start_time']:<20}"
                )

        @workflows.command("start")
        @click.argument("workflow_name")
        def start_cmd(workflow_name: str):
            """Start a new workflow execution with an agent TUI."""
            # Get agent command from pyproject.toml config
            agent_command = workflows_config.get("agent_command")
            if not agent_command:
                click.echo("Error: No agent command configured.", err=True)
                click.echo("Add to pyproject.toml:", err=True)
                click.echo('  [tool.artificer.workflows]', err=True)
                click.echo('  agent_command = "claude"', err=True)
                raise SystemExit(1)

            # Validate workflow exists
            workflow_class = Workflow._workflow_registry.get(workflow_name)
            if workflow_class is None:
                available = list(Workflow._workflow_registry.keys())
                click.echo(f"Unknown workflow: {workflow_name}", err=True)
                if available:
                    click.echo(f"Available workflows: {', '.join(available)}", err=True)
                else:
                    click.echo("No workflows registered.", err=True)
                raise SystemExit(1)

            # Construct the initial prompt
            prompt = f"Starting a `{workflow_name}` workflow. Start the first step."

            # Launch agent with the prompt (as positional argument for interactive mode)
            cmd_parts = shlex.split(agent_command)
            cmd_parts.append(prompt)

            # Replace current process with agent
            os.execvp(cmd_parts[0], cmd_parts)

        @workflows.command("resume")
        @click.argument("workflow_id")
        def resume_cmd(workflow_id: str):
            """Resume a paused workflow with an agent TUI."""
            agent_command = workflows_config.get("agent_command")
            if not agent_command:
                click.echo("Error: No agent command configured.", err=True)
                click.echo("Add to pyproject.toml:", err=True)
                click.echo('  [tool.artificer.workflows]', err=True)
                click.echo('  agent_command = "claude"', err=True)
                raise SystemExit(1)

            result = resume_workflow(workflow_id)

            if "error" in result:
                click.echo(f"Error: {result['error']}", err=True)
                raise SystemExit(1)

            # Construct prompt to resume the workflow
            prompt = f"Resuming workflow `{workflow_id}`. Continue with the current step."

            # Launch agent with the prompt
            cmd_parts = shlex.split(agent_command)
            cmd_parts.append(prompt)
            os.execvp(cmd_parts[0], cmd_parts)

        @workflows.command("pause")
        @click.argument("workflow_id")
        def pause_cmd(workflow_id: str):
            """Pause a running workflow."""
            result = pause_workflow(workflow_id)

            if "error" in result:
                click.echo(f"Error: {result['error']}", err=True)
                raise SystemExit(1)

            click.echo(result.get("message", f"Paused workflow: {workflow_id}"))

    @classmethod
    def _import_workflow_entrypoint(cls, config: "ArtificerConfig") -> dict:
        """Import the workflow entrypoint module to register workflows.

        Returns:
            Workflow configuration dict from [tool.artificer.workflows]
        """
        import importlib
        import sys
        from pathlib import Path

        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib

        # Read pyproject.toml for workflow-specific config
        pyproject_path = Path.cwd() / "pyproject.toml"
        if not pyproject_path.exists():
            return {}

        with open(pyproject_path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception:
                return {}

        # Get workflow-specific entrypoint from [tool.artificer.workflows]
        artificer_config = data.get("tool", {}).get("artificer", {})
        workflows_config = artificer_config.get("workflows", {})
        entrypoint = workflows_config.get("entrypoint")

        if entrypoint:
            try:
                # Check if it's a file path (contains / or starts with .)
                if "/" in entrypoint or entrypoint.startswith("."):
                    # Treat as file path relative to pyproject.toml
                    module_path = Path.cwd() / entrypoint
                    if not module_path.suffix:
                        module_path = module_path.with_suffix(".py")
                    if module_path.exists():
                        # Import from file path using importlib.util
                        import importlib.util

                        spec = importlib.util.spec_from_file_location(
                            "workflow_entrypoint", module_path
                        )
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules["workflow_entrypoint"] = module
                            spec.loader.exec_module(module)
                    else:
                        click.echo(
                            f"Warning: Workflow entrypoint not found: {module_path}"
                        )
                else:
                    # Treat as module path
                    importlib.import_module(entrypoint)
            except Exception as e:
                click.echo(
                    f"Warning: Could not import workflow entrypoint '{entrypoint}': {e}"
                )

        return workflows_config
