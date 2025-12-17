"""Command execution module with live logging suport"""

import asyncio
import sys
from collections.abc import Callable
from typing import Optional


class CommandExecutor:
    """Execute typer commands in subprocess with live output streamiing"""

    def __init__(self, output_callback: Optional[Callable[[str], None]] = None) -> None:
        self.output_callback = output_callback or print
        self.process = None
        self.is_running = False

    async def execute_command(
        self, command_args: list[str], cwd: Optional[str] = None
    ) -> tuple[int, str, str]:
        """Execute a command and stream output in real-time

        Args:
            command_args (list[str]): Command and its arguments as a list
            cwd (Optional[str], optional): Working directory. Defaults to None.

        Returns:
            tuple[int, str, str]: Return code, standard output, standard error
        """
        self.is_running = True
        stdout_lines = []
        stderr_lines = []
        try:
            self.process = await asyncio.create_subprocess_exec(
                *command_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            await asyncio.gather(
                self._read_stream(self.process.stdout, stdout_lines, "STDOUT"),
                self._read_stream(self.process.stderr, stderr_lines, "STDERR"),
            )
            return_code = await self.process.wait()
        except (OSError, ValueError) as e:
            self.output_callback(f"Error executing command: {e}")
            return_code = 1
            stderr_lines.append(f"Error executing command: {e}")
        finally:
            self.is_running = False
            self.process = None
        return return_code, "\n".join(stdout_lines), "\n".join(stderr_lines)

    async def _read_stream(
        self, stream: asyncio.StreamReader, lines: list[str], stream_name: str
    ) -> None:
        """Read a stream line by line and store lines in a list

        Args:
            stream (asyncio.StreamReader): Stream to read from
            lines (list[str]): List to store lines
            stream_name (str): Name of the stream for logging purposes
        """
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded_line = line.decode().rstrip()
                lines.append(decoded_line)
                formatted_line = f"{decoded_line}"
                self.output_callback(formatted_line)
        except (OSError, UnicodeDecodeError) as e:
            error_msg = f"Error reading {stream_name} stream: {e}"
            self.output_callback(error_msg)
            lines.append(error_msg)

    def stop_execution(self) -> None:
        """Stop the currently running command"""
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.output_callback("Process terminated by user.")
            except (OSError, ProcessLookupError) as e:
                self.output_callback(f"Error terminating process: {e}")

    def build_command_args(
        self, module_path: str, command_name: str, parameters: dict
    ) -> list[str]:
        """Build command arguments list for subprocess execution

        Args:
            module_path (str): Path to the module containing the command
            command_name (str): Name of the command to execute
            parameters (dict): Command parameters as key-value pairs

        Returns:
            list[str]: List of command arguments
        """
        """Build argv list. `parameters` expected to be a mapping of param_name -> value
        where CommandInfo from the introspector determines whether a parameter
        is an argument (positional) or option (flag/key).

        The UI currently passes only a mapping of names to raw values; callers
        should pass parameters in the order they want positional args to appear.
        """
        args = [sys.executable, module_path]

        # support nested commands like "group subcommand" or "group/subcommand"
        # by splitting on whitespace or slashes so tokens become separate argv items
        if command_name and command_name != "main":
            import re

            parts = [p for p in re.split(r"[\s/]+", str(command_name).strip()) if p]
            args.extend(parts)

        # parameters is a dict of name->value. For positional arguments we
        # expect callers to pass them in the correct order; we'll append any
        # non-empty values as positional args first if their key starts with
        # a special marker (not enforced here). For backward compatibility we
        # treat the incoming dict as: if the key maps to a tuple of
        # (ParameterInfo, value) then use ParameterInfo.param_type to decide.

        # First, detect if values are (ParameterInfo, value)
        positional_parts = []
        option_parts = []

        for name, raw in parameters.items():
            param_info = None
            value = None
            if isinstance(raw, (list, tuple)) and len(raw) == 2:
                param_info, value = raw
            else:
                # legacy: just a value
                value = raw

            if value is None or value == "":
                continue

            # booleans and simple options
            if (
                param_info is not None
                and getattr(param_info, "param_type", None) is not None
            ):
                from typer_ui.introspector import ParamType

                if param_info.param_type == ParamType.ARGUMENT:
                    positional_parts.append(str(value))
                else:
                    # option
                    if isinstance(value, bool):
                        if value:
                            option_parts.append(f"--{name.replace('_', '-')}")
                    else:
                        option_parts.extend([f"--{name.replace('_', '-')}", str(value)])
            else:
                # no param metadata: fallback to option style
                if isinstance(value, bool):
                    if value:
                        option_parts.append(f"--{name.replace('_', '-')}")
                else:
                    option_parts.extend([f"--{name.replace('_', '-')}", str(value)])

        # append positional args first, then options
        args.extend(positional_parts)
        args.extend(option_parts)

        return args
