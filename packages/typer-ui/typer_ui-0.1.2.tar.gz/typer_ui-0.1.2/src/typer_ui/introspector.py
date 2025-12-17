import inspect
from enum import Enum
from typing import Any, Callable, List, Optional, get_type_hints

import typer
from pydantic import BaseModel, ConfigDict, Field


class ParamType(Enum):
    """Enumeration for parameter types"""

    OPTION = "option"
    ARGUMENT = "argument"


class ParameterInfo(BaseModel):
    """Information about a Typer command parameter"""

    name: str
    param_type: ParamType
    python_type: Any
    default: Optional[Any] = None
    required: bool = False
    help: Optional[str] = None


class CommandNode(BaseModel):
    """Pydantic-backed tree node representing a command or a group.

    - If `is_group` is True then `children` contains subcommands/groups.
    - If `is_group` is False then `func` and `parameters` contain command details.
    """

    name: str
    help: Optional[str] = None
    is_group: bool = False
    parameters: List[ParameterInfo] = Field(default_factory=list)
    children: List["CommandNode"] = Field(default_factory=list)
    func: Optional[Callable[..., Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


CommandNode.model_rebuild()


def _extract_parameters_from_callable(func: Callable[..., Any]) -> List[ParameterInfo]:
    """Extract ParameterInfo list from a callable using inspect + typer metadata."""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    params: List[ParameterInfo] = []

    for param_name, param in sig.parameters.items():
        default = param.default
        if isinstance(default, typer.models.OptionInfo):
            param_type = ParamType.OPTION
            default_value = None if default.default is ... else default.default
            required = default.default is ...
        elif isinstance(default, typer.models.ArgumentInfo):
            param_type = ParamType.ARGUMENT
            default_value = None if default.default is ... else default.default
            required = default.default is ...
        else:
            if default is inspect.Parameter.empty:
                param_type = ParamType.ARGUMENT
                default_value = None
                required = True
            else:
                param_type = ParamType.OPTION
                default_value = default
                required = False

        python_type = type_hints.get(
            param_name, type(default_value) if default_value is not None else str
        )
        help_text = (
            getattr(param.default, "help", "") if hasattr(param.default, "help") else ""
        )

        params.append(
            ParameterInfo(
                name=param_name,
                param_type=param_type,
                python_type=python_type,
                default=default_value,
                required=required,
                help=help_text,
            )
        )

    return params


class TyperIntrospector:
    """Class to introspect a Typer app and extract command information.

    Produces a tree of `CommandNode` objects in `self.__commands` which makes it
    easier for UIs to render nested menus and traverse groups/commands.
    """

    def __init__(self, app: typer.Typer) -> None:
        self.app = app
        self.__commands: List[CommandNode] = []
        self._extract_commands()

    def _extract_commands(self) -> None:
        """Extract commands and groups from the Typer app into a tree of CommandNode."""
        # Top-level commands
        if hasattr(self.app, "registered_commands") and self.app.registered_commands:
            for cmd in self.app.registered_commands:
                cmd_name = cmd.name or cmd.callback.__name__ or "main"
                func = cmd.callback
                help_text = cmd.help or func.__doc__ or ""
                node = CommandNode(
                    name=cmd_name,
                    help=help_text,
                    is_group=False,
                    func=func,
                    parameters=_extract_parameters_from_callable(func),
                )
                self.__commands.append(node)

        # Groups (added via add_typer)
        if hasattr(self.app, "registered_groups") and self.app.registered_groups:
            for group in self.app.registered_groups:
                group_name = getattr(group, "name", None) or ""
                group_help = getattr(group, "help", "") or ""
                sub_app = getattr(group, "typer_instance", None)
                group_node = CommandNode(
                    name=group_name, help=group_help, is_group=True
                )

                if sub_app and hasattr(sub_app, "registered_commands"):
                    for sub_cmd in sub_app.registered_commands:
                        sub_cmd_name = sub_cmd.name or getattr(
                            sub_cmd, "callback", None
                        )
                        if callable(sub_cmd_name):
                            sub_cmd_name = sub_cmd_name.__name__
                        sub_cmd_name = sub_cmd_name or "main"
                        func = sub_cmd.callback
                        help_text = sub_cmd.help or func.__doc__ or group_help or ""
                        child_node = CommandNode(
                            name=sub_cmd_name,
                            help=help_text,
                            is_group=False,
                            func=func,
                            parameters=_extract_parameters_from_callable(func),
                        )
                        group_node.children.append(child_node)

                # Only add group node if it has children; otherwise treat it as a no-op
                if group_node.children:
                    self.__commands.append(group_node)

    @property
    def commands(self) -> List[CommandNode]:
        """Get the list of top-level CommandNode objects"""
        return self.__commands

    def get_command_by_name(self, name: str) -> Optional[CommandNode]:
        """Get a command node by its name.

        The function supports both plain command names and space-separated
        group + command names (for backwards compatibility with earlier code).
        """
        # direct match on top-level
        for node in self.__commands:
            if not node.is_group and node.name == name:
                return node
            if node.is_group:
                # try group match: "group command" or "group/command"
                for child in node.children:
                    full_space = f"{node.name} {child.name}".strip()
                    full_slash = f"{node.name}/{child.name}".strip()
                    if name in (child.name, full_space, full_slash):
                        return child

        return None
