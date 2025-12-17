"""Main entry point for the Typer UI application."""

import asyncio
from datetime import datetime
from typing import Optional

import typer
from nicegui import ui

from . import ui_components as ui_comp
from .command_executor import CommandExecutor
from .introspector import TyperIntrospector


class TyperUI:
    """Main TyperUI application class"""

    def __init__(
        self,
        app: typer.Typer,
        module_path: Optional[str] = None,
        title: str = "Typer UI",
        subtitle: str = "Command executor UI",
    ):
        self.app = app
        self.module_path = module_path or self._detect_module_path()
        self.title = title
        self.subtitle = subtitle
        self.introspector = TyperIntrospector(app)
        self.command_executor = CommandExecutor(self._log_output)
        self.commands = self.introspector.commands
        self.current_command = None
        # store the selected command path (e.g. 'user/add') so execution can
        # include group names even when CommandNode.name is just the subcommand
        self.current_command_path = None
        self._current_form_values = {}
        self.log_area = None
        self.execute_button = None
        self.log_controls = None
        self.export_button = None
        self.help_button = None
        self.form_container = None
        self.log_buffer = []

    def _detect_module_path(self) -> str:
        """Detect the module path from the app's __module__ attribute"""
        return self.app.__module__.replace(".", "/")

    def _log_output(self, message: str) -> None:
        """Log output to the UI log area"""
        self.log_buffer.append(message)
        if self.log_area:
            self.log_area.push(message)
        if self.export_button:
            self.export_button.set_visibility(True)

    async def _execute_command(self, commands_name: str, parameters: dict):
        """Execute a command with the given parameters"""
        if self.command_executor.is_running:
            self._log_output(
                "Command is already running. Please wait or stop it first."
            )
            return

        # pair parameter values with their ParameterInfo metadata when available
        param_map = {}
        if self.current_command:
            # build a mapping name -> (ParameterInfo, value)
            for p in self.current_command.parameters:
                val = parameters.get(p.name)
                param_map[p.name] = (p, val)
            # also include any extra keys from parameters not in introspector
            for k, v in parameters.items():
                if k not in param_map:
                    param_map[k] = v

        else:
            param_map = parameters

        command_args = self.command_executor.build_command_args(
            module_path=self.module_path,
            command_name=commands_name,
            parameters=param_map,
        )

        # Add separator with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_output(f"======== EXECUTION STARTED: {timestamp} ========")

        self._log_output(f"Executing command: {' '.join(command_args)}")
        self._log_output("-" * 40)

        # Update UI state to Running
        if self.execute_button:
            self.execute_button.text = "Stop Execution"
            self.execute_button.props("color=negative")
        if self.help_button:
            self.help_button.set_visibility(False)
        if self.log_controls:
            self.log_controls.set_visibility(False)
        if self.log_card:
            self.log_card.set_visibility(True)

        try:
            (
                return_code,
                _,
                _,
            ) = await self.command_executor.execute_command(command_args)
            self._log_output("--" * 20)
            self._log_output(f"Command finished with return code: {return_code}")
        finally:
            # Update UI state to Idle
            if self.execute_button:
                self.execute_button.text = "Execute"
                self.execute_button.props("color=primary")
            if self.help_button:
                self.help_button.set_visibility(True)
            if self.log_controls:
                self.log_controls.set_visibility(True)

    def _on_command_change(self, command_name: str):
        """Handle command/menu selection change.

        `command_name` may be a path like "group/command" or a simple command name.
        Update current command and refresh the form. Also try to update the
        browser URL so navigation works when users select a command.
        """
        # update current command from introspector and remember the path used
        # to select it (this path may be 'group/command' or a simple name)

        # Navigate to the new URL with the command slug
        # This will trigger a page reload/render which will handle setting the command
        slug = command_name.replace("/", "__")
        ui.navigate.to(f"/{slug}")

    def _refresh_command_form(self):
        """Refresh the command form with the current command's parameters"""
        if self.form_container:
            self.form_container.clear()

        if self.current_command:
            with self.form_container:
                # ensure execution uses the selected command path so groups are included
                def _on_interaction(cmd_name, params):
                    if self.command_executor.is_running:
                        self._stop_execution()
                    else:
                        # prefer the recorded path; fall back to the form's command name
                        exec_name = self.current_command_path or cmd_name
                        asyncio.create_task(self._execute_command(exec_name, params))

                def _on_help(cmd_name):
                    # prefer the recorded path; fall back to the form's command name
                    exec_name = self.current_command_path or cmd_name
                    # Pass empty params but with help flag handled by executor logic if we passed it
                    # But _execute_command takes params. We can manually trigger help execution
                    # similar to _show_all_help but for single command.

                    # We'll use _execute_command but pass a special flag or just handle it here.
                    # Let's handle it here to avoid messing with form values.

                    if self.command_executor.is_running:
                        return

                    self._clear_logs()
                    if self.log_card:
                        self.log_card.set_visibility(True)

                    args = self.command_executor.build_command_args(
                        self.module_path, exec_name, {"help": True}
                    )

                    # Separator
                    display_args = list(args)
                    if display_args:
                        display_args[0] = "python"
                    cmd_str = " ".join(display_args)
                    self._log_output(f"$ {cmd_str}")

                    asyncio.create_task(self.command_executor.execute_command(args))

                (
                    self._current_form_values,
                    self.execute_button,
                    self.help_button,
                ) = ui_comp.create_command_form(
                    self.current_command,
                    _on_interaction,
                    _on_help,
                )

    def _stop_execution(self):
        """Stop the currently running command"""
        self.command_executor.stop_execution()

    def _clear_logs(self):
        """Clear the log area"""
        self.log_buffer.clear()
        if self.log_area:
            self.log_area.clear()
        if self.export_button:
            self.export_button.set_visibility(False)

    def _export_logs(self):
        """Export logs to a text file"""
        content = "\n".join(self.log_buffer)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.txt"
        ui.download(content.encode("utf-8"), filename)

    async def _show_all_help(self):
        """Show help for the main app in the log area"""
        self._clear_logs()
        if self.log_card:
            self.log_card.set_visibility(True)

        self._log_output("Welcome to Typer UI!\n")

        # Run help for the main app (no subcommand)
        args = self.command_executor.build_command_args(
            self.module_path,
            "",  # Empty command name for top-level help
            {"help": True},
        )

        # Show the command being executed
        display_args = list(args)
        if display_args:
            display_args[0] = "python"
        cmd_str = " ".join(display_args)
        self._log_output(f"$ {cmd_str}")

        # Execute directly
        await self.command_executor.execute_command(args)

    def create_ui(self):
        """Create the NiceGUI UI components"""
        ui_comp.header(
            self.commands,
            self._on_command_change,
            self.current_command_path,
        )
        ui.page_title(self.title)

        # Use gap-6 for consistent spacing, remove fixed margins from children
        with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-6"):
            # Styled Header Section
            # Styled Header Section matching NiceGUI theme
            with ui.card().classes("w-full no-shadow border-[1px] border-gray-200"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.row().classes("items-center gap-4"):
                        ui.avatar("terminal", color="primary", text_color="white")
                        with ui.column().classes("gap-0"):
                            ui.label(self.title).classes("text-xl font-bold")
                            ui.label(self.subtitle).classes(
                                "text-caption text-gray-600"
                            )

                    with ui.chip(icon="folder", color="grey-2").classes("text-caption"):
                        ui.label(self.module_path).classes("font-mono")

            if self.commands:
                # Render a nested menu for the command tree. We expect
                # `self.commands` to be a list of CommandNode objects.
                self.form_container = ui.column().classes("w-full")
            else:
                ui.label("No commands found in the Typer app.").classes("text-red-500")

            # Execution Logs Section
            # Hidden by default, shown when needed
            self.log_card = ui.card().classes(
                "w-full no-shadow border-[1px] border-gray-200 p-0 gap-0"
            )
            with self.log_card:
                with ui.row().classes(
                    "w-full items-center justify-between bg-gray-50 p-4 border-b border-gray-200"
                ):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("dvr", color="primary")
                        ui.label("Execution Logs").classes("text-lg font-bold")

                    self.log_controls, self.export_button = (
                        ui_comp.create_execution_controls(
                            self._export_logs, self._clear_logs
                        )
                    )
                    # Initially hide export button if buffer is empty
                    if not self.log_buffer:
                        self.export_button.set_visibility(False)

                with ui.column().classes("w-full p-4"):
                    self.log_area = ui_comp.create_log_display()

    def run(self, host: str = "localhost", port: int = 8080, **kwargs) -> None:
        """Run the NiceGUI app"""

        @ui.page("/")
        @ui.page("/{command_slug}")
        async def main_page(command_slug: str = None):
            if command_slug:
                # Convert slug back to path
                command_path = command_slug.replace("__", "/")
                # Verify command exists
                cmd = self.introspector.get_command_by_name(command_path)
                if cmd:
                    self.current_command = cmd
                    self.current_command_path = command_path
            else:
                # Reset if no command in URL (optional, or keep last state)
                # For now, let's reset to ensure clean state on root
                self.current_command = None
                self.current_command_path = None

            self.create_ui()

            if self.current_command:
                # Command selected: Show form, hide log initially
                self._refresh_command_form()
                if self.log_card:
                    self.log_card.set_visibility(False)
            else:
                # Index page: Show help in log
                if self.log_card:
                    self.log_card.set_visibility(True)
                # Run help generation in background or await it
                # Since main_page is async, we can await it
                await self._show_all_help()

        ui.run(host=host, port=port, **kwargs)


def create_typer_ui(
    app: typer.Typer,
    module_path: Optional[str] = None,
    title: str = "Typer UI",
    subtitle: str = "Command executor UI",
):
    """Create and run the Typer UI application

    Args:
        app (typer.Typer): Typer application instance
        module_path (Optional[str], optional): Path to the module containing the Typer app. Defaults to None.
        title (str, optional): Title of the application. Defaults to "Typer UI".
        subtitle (str, optional): Subtitle of the application. Defaults to "Command executor UI".
    """
    return TyperUI(app, module_path, title=title, subtitle=subtitle)
