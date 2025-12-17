from unittest.mock import MagicMock

import typer

from typer_ui.introspector import ParamType, TyperIntrospector


def test_single_command_introspection():
    app = typer.Typer()

    @app.command()
    def simple(name: str = "User", count: int = 1):
        """Simple command"""
        pass

    introspector = TyperIntrospector(app)
    commands = introspector.commands

    assert len(commands) == 1
    cmd = commands[0]
    assert cmd.name == "simple"
    assert cmd.help == "Simple command"
    assert not cmd.is_group
    assert len(cmd.parameters) == 2

    p1 = cmd.parameters[0]
    assert p1.name == "name"
    assert p1.default == "User"
    assert p1.python_type == str

    p2 = cmd.parameters[1]
    assert p2.name == "count"
    assert p2.default == 1
    assert p2.python_type == int


def test_nested_commands_introspection(sample_typer_app):
    introspector = TyperIntrospector(sample_typer_app)
    commands = introspector.commands

    # Expect 'hello', 'goodbye', and 'math' group
    cmd_names = [c.name for c in commands]
    assert "hello" in cmd_names
    assert "goodbye" in cmd_names
    assert "math" in cmd_names

    # Check math group
    math_node = next(c for c in commands if c.name == "math")
    assert math_node.is_group
    assert len(math_node.children) == 1
    assert math_node.children[0].name == "add"

    add_cmd = math_node.children[0]
    assert len(add_cmd.parameters) == 2
    assert add_cmd.parameters[0].name == "a"
    assert add_cmd.parameters[0].param_type == ParamType.ARGUMENT


def test_get_command_by_name(sample_typer_app):
    introspector = TyperIntrospector(sample_typer_app)

    # Top level
    cmd = introspector.get_command_by_name("hello")
    assert cmd is not None
    assert cmd.name == "hello"

    # Nested space
    cmd = introspector.get_command_by_name("math add")
    assert cmd is not None
    assert cmd.name == "add"

    # Nested slash
    cmd = introspector.get_command_by_name("math/add")
    assert cmd is not None
    assert cmd.name == "add"

    # Non-existent
    assert introspector.get_command_by_name("nonexistent") is None


def test_parameter_extraction_details():
    app = typer.Typer()

    @app.command()
    def details(
        req_arg: int,
        opt_arg: int = typer.Argument(10, help="An optional argument"),
        flag: bool = False,
        opt: str = typer.Option("default", help="An option"),
    ):
        pass

    introspector = TyperIntrospector(app)
    cmd = introspector.commands[0]

    params = {p.name: p for p in cmd.parameters}

    assert params["req_arg"].required is True
    assert params["req_arg"].param_type == ParamType.ARGUMENT

    assert params["opt_arg"].required is False
    assert params["opt_arg"].default == 10
    assert params["opt_arg"].help == "An optional argument"
    assert params["opt_arg"].param_type == ParamType.ARGUMENT

    assert params["flag"].python_type == bool
    assert params["flag"].default is False
    assert params["flag"].param_type == ParamType.OPTION

    assert params["opt"].default == "default"
    assert params["opt"].help == "An option"
    assert params["opt"].param_type == ParamType.OPTION


def test_extract_parameters_complex_cases():
    from typer_ui.introspector import _extract_parameters_from_callable

    def func(
        a: int = typer.Argument(..., help="req arg"),
        b: str = typer.Option("def", help="opt"),
        c: bool = False,
    ):
        pass

    params = _extract_parameters_from_callable(func)

    assert params[0].required is True
    assert params[1].required is False

    def func_varargs(*args, **kwargs):
        pass

    params_var = _extract_parameters_from_callable(func_varargs)
    # The loop iterates `sig.parameters.items()`. *args/**kwargs are var_positional/var_keyword.
    # Current code does NOT skip them explicitly, but defaults handling might handle them.
    # Check `_extract_parameters_from_callable`:
    # It loops all params.
    # param.default for *args is `inspect.Parameter.empty`.
    # Line 65: if default is inspect.Parameter.empty: param_type = ARGUMENT.
    # So *args becomes an ARGUMENT.
    pass


def test_introspector_branch_coverage():
    # 1. Empty app (No commands, no groups) -> Covers 110->125 (no commands), 125->exit (no groups)
    empty_app = typer.Typer()
    intro = TyperIntrospector(empty_app)
    assert len(intro.commands) == 0

    # 2. Group with no commands -> Covers 134->154 (no subapp commands), 154->loop (no children added)
    app = typer.Typer()
    group = typer.Typer(name="empty_group")
    app.add_typer(group)
    # Note: add_typer without naming might leave name empty if not set in Typer(name=...)
    # But here we set name="empty_group".
    # However, `group.registered_commands` is empty.

    intro = TyperIntrospector(app)
    # Group has no children, so it should NOT be added to __commands (Line 154 check)
    assert len(intro.commands) == 0

    # 3. Group subcommand with explicit name -> Covers 139->141 (name is string)
    app2 = typer.Typer()
    group2 = typer.Typer()

    @group2.command(name="explicit")
    def sub():
        pass

    app2.add_typer(group2, name="grp")
    intro2 = TyperIntrospector(app2)
    grp_node = intro2.commands[0]
    assert grp_node.name == "grp"
    assert grp_node.children[0].name == "explicit"


def test_group_without_registered_commands():
    # Cover 134->154: Group found but sub_app has no registered_commands
    app = typer.Typer()

    # Configure mock group
    mock_sub_app = MagicMock()
    del mock_sub_app.registered_commands  # ensure hasattr returns False

    mock_group = MagicMock()
    mock_group.name = "grp"
    mock_group.help = "help"
    mock_group.typer_instance = mock_sub_app

    app.registered_groups = [mock_group]

    intro = TyperIntrospector(app)
    # 134 `hasattr` returns False. Jumps to 154.
    assert len(intro.commands) == 0
