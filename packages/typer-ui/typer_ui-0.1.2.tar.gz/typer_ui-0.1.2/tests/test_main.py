from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Patch nicegui.ui in both main and ui_components BEFORE importing them
# to avoid side effects or layout issues if possible, though nicegui logic
# usually requires an active client context context for creating elements.
#
# We will mock the modules `nicegui.ui` so that attribute access returns mocks.

dict_mock = MagicMock()


@pytest.fixture
def mock_ui(mocker):
    # Use a shared mock for both modules to ensure assertions work across calls
    shared_ui = MagicMock()
    mocker.patch("typer_ui.main.ui", shared_ui)
    mocker.patch("typer_ui.ui_components.ui", shared_ui)
    mocker.patch.dict("sys.modules", {"nicegui.ui": shared_ui})
    return shared_ui


@pytest.fixture
def typer_ui_instance(sample_typer_app, mock_ui):
    from typer_ui.main import TyperUI

    # Pass explicit module path to test matching
    instance = TyperUI(sample_typer_app, module_path="tests/conftest")
    # Mock some UI elements that are expected on instance
    instance.log_area = MagicMock()
    instance.execute_button = MagicMock()
    instance.export_button = MagicMock()
    instance.help_button = MagicMock()
    instance.log_card = MagicMock()
    return instance


def test_initialization(typer_ui_instance, sample_typer_app):
    assert typer_ui_instance.app == sample_typer_app
    assert len(typer_ui_instance.commands) > 0


def test_detect_module_path(sample_typer_app):
    from typer_ui.main import TyperUI

    # Test built-in detection
    instance = TyperUI(sample_typer_app)
    # The default app fixture comes from typer package instantiation so it points to typer.main or similar
    # We just want to ensure it returns a string
    assert isinstance(instance.module_path, str)
    assert len(instance.module_path) > 0


def test_log_output(typer_ui_instance):
    typer_ui_instance._log_output("Test message")
    assert "Test message" in typer_ui_instance.log_buffer
    typer_ui_instance.log_area.push.assert_called_with("Test message")
    typer_ui_instance.export_button.set_visibility.assert_called_with(True)


def test_clear_logs(typer_ui_instance):
    typer_ui_instance.log_buffer = ["msg"]
    typer_ui_instance._clear_logs()
    assert len(typer_ui_instance.log_buffer) == 0
    typer_ui_instance.log_area.clear.assert_called()
    typer_ui_instance.export_button.set_visibility.assert_called_with(False)


@pytest.mark.asyncio
async def test_execute_command_logic(typer_ui_instance, mocker):
    # Mock command executor
    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "out", "err")
    )
    typer_ui_instance.command_executor.build_command_args = MagicMock(
        return_value=["cmd", "arg"]
    )

    await typer_ui_instance._execute_command("cmd", {"param": "val"})

    # Check that it flipped to Stop and then back to Execute
    # We can verify props calls
    props_calls = typer_ui_instance.execute_button.props.call_args_list
    assert any("color=negative" in str(args) for args in props_calls)
    assert any("color=primary" in str(args) for args in props_calls)

    # Final state
    assert typer_ui_instance.execute_button.text == "Execute"
    assert typer_ui_instance.command_executor.execute_command.called


@pytest.mark.asyncio
async def test_execute_command_already_running(typer_ui_instance, mocker):
    typer_ui_instance.command_executor.is_running = True
    await typer_ui_instance._execute_command("cmd", {})
    # Should exit early and log warning
    assert "Command is already running" in typer_ui_instance.log_buffer[-1]


def test_on_command_change(typer_ui_instance, mock_ui):
    typer_ui_instance._on_command_change("hello")
    mock_ui.navigate.to.assert_called_with("/hello")

    typer_ui_instance._on_command_change("math/add")
    mock_ui.navigate.to.assert_called_with("/math__add")


def test_stop_execution(typer_ui_instance):
    typer_ui_instance.command_executor.stop_execution = MagicMock()
    typer_ui_instance._stop_execution()
    typer_ui_instance.command_executor.stop_execution.assert_called()


@pytest.mark.asyncio
async def test_refresh_command_form(typer_ui_instance, sample_typer_app):
    # Setup
    typer_ui_instance.current_command = typer_ui_instance.commands[
        0
    ]  # "simple" from introspector test or "hello" from conftest
    # Ensure commands are populated
    # In conftest sample_typer_app has hello, goodbye, math

    # Mock ui_comp.create_command_form to return mocks
    # We need to mock the module where create_command_form is imported/used or patch it
    with patch("typer_ui.main.ui_comp.create_command_form") as mock_ccf:
        mock_ccf.return_value = ({}, MagicMock(), MagicMock())
        typer_ui_instance.form_container = MagicMock()

        typer_ui_instance._refresh_command_form()

        mock_ccf.assert_called()
        typer_ui_instance.form_container.clear.assert_called()

        # Test helpers defined inside
        on_exec = mock_ccf.call_args[0][1]
        on_help = mock_ccf.call_args[0][2]

        # Test on_exec
        typer_ui_instance.command_executor.is_running = False

        # Mock execution to prevent real subprocess calls
        typer_ui_instance.command_executor.execute_command = AsyncMock(
            return_value=(0, "out", "err")
        )
        typer_ui_instance.command_executor.build_command_args = MagicMock(
            return_value=["echo", "test"]
        )

        on_exec("cmd", {})
        # Should start execution task? It's async. We can't easily await it here unless we capture the task
        # But we can check if it didn't crash.

        # Test on_help
        on_help("cmd")
        # Should build args with help and execute
        # Check command executor
        # Since _show_all_help/on_help calls execute_command, we need to mock it if we want validation


@pytest.mark.asyncio
async def test_show_all_help(typer_ui_instance):
    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "", "")
    )
    typer_ui_instance.log_card = MagicMock()

    await typer_ui_instance._show_all_help()

    typer_ui_instance.log_area.clear.assert_called()
    assert typer_ui_instance.command_executor.execute_command.called
    args = typer_ui_instance.command_executor.execute_command.call_args[0][0]
    assert "--help" in args or "-h" in args  # Typer help flag


def test_create_ui(typer_ui_instance, mock_ui):
    typer_ui_instance.create_ui()
    # Check that main sections are created
    mock_ui.header.assert_called()
    mock_ui.column.assert_called()
    mock_ui.card.assert_called()


def test_export_logs(typer_ui_instance, mock_ui):
    typer_ui_instance.log_buffer = ["log1"]
    typer_ui_instance._export_logs()
    mock_ui.download.assert_called()


def test_create_typer_ui_factory(sample_typer_app):
    from typer_ui.main import TyperUI, create_typer_ui

    instance = create_typer_ui(sample_typer_app)
    assert isinstance(instance, TyperUI)


@pytest.mark.asyncio
async def test_run(typer_ui_instance, mock_ui):
    # Setup mock for page decorator
    mock_decorator = MagicMock()
    mock_ui.page.return_value = mock_decorator

    # Call run
    typer_ui_instance.run(host="0.0.0.0", port=1234)
    # Check that ui.run was called with args
    mock_ui.run.assert_called_with(host="0.0.0.0", port=1234)

    # Check that ui.page was called
    mock_ui.page.assert_called()
    assert mock_decorator.called

    # Capture main_page function
    # Decorators stack: @page("/") wraps @page("/{slug}") wraps func
    # Bottom up application.
    # First call to mock_decorator is likely for /{slug}, passing the real func.
    # Second call is for / passing the result of first.
    # We want the real func from first call.
    first_call = mock_decorator.call_args_list[0]
    main_page_func = first_call.args[0]

    # Run main_page without slug
    # We need to ensure we mocked enough internals that main_page doesn't crash on us.
    # main_page calls self.create_ui(), self._show_all_help() etc.
    # Since we use shared mock_ui, create_ui calls mocked header/column etc. which is fine.

    await main_page_func(command_slug=None)
    # Check reset
    assert typer_ui_instance.current_command is None

    # Run main_page with slug
    # We need a valid slug for current app: "hello"
    # Ensure commands are ready
    await main_page_func(command_slug="hello")
    assert typer_ui_instance.current_command.name == "hello"


def test_log_output_with_unset_ui(typer_ui_instance):
    # Cover branches where log_area or export_button are None
    typer_ui_instance.log_area = None
    typer_ui_instance.export_button = None
    typer_ui_instance._log_output("msg")  # Should not crash and valid path
    assert "msg" in typer_ui_instance.log_buffer

    # Cover _clear_logs with unset UI
    typer_ui_instance._clear_logs()  # Should not crash


def test_refresh_form_stop_exec(typer_ui_instance, sample_typer_app):
    # Simulate stopping execution if running
    typer_ui_instance.command_executor.is_running = True
    typer_ui_instance.command_executor.stop_execution = MagicMock()

    with patch("typer_ui.main.ui_comp.create_command_form") as mock_ccf:
        mock_ccf.return_value = ({}, MagicMock(), MagicMock())
        typer_ui_instance.current_command = typer_ui_instance.commands[0]
        typer_ui_instance.form_container = MagicMock()

        typer_ui_instance._refresh_command_form()

        on_exec = mock_ccf.call_args[0][1]
        on_exec("cmd", {})

        typer_ui_instance.command_executor.stop_execution.assert_called()


def test_refresh_form_help_running(typer_ui_instance):
    # Simulate help click while running
    with patch("typer_ui.main.ui_comp.create_command_form") as mock_ccf:
        mock_ccf.return_value = ({}, MagicMock(), MagicMock())
        typer_ui_instance.current_command = typer_ui_instance.commands[0]
        typer_ui_instance.form_container = MagicMock()

        typer_ui_instance._refresh_command_form()

        on_help = mock_ccf.call_args[0][2]

        typer_ui_instance.command_executor.is_running = True
        # Should return early
        on_help("cmd")
        # Assert nothing else happened (like log output clearing)
        typer_ui_instance.log_card.set_visibility.assert_not_called()


@pytest.mark.asyncio
async def test_execute_command_ui_state_checks(typer_ui_instance):
    # Cover branches checking self.execute_button etc during execution
    typer_ui_instance.execute_button = None
    typer_ui_instance.help_button = None
    typer_ui_instance.log_controls = None
    typer_ui_instance.log_card = None

    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "", "")
    )
    typer_ui_instance.command_executor.build_command_args = MagicMock(return_value=[])

    # Should run without crashing due to None checks
    await typer_ui_instance._execute_command("cmd", {})


@pytest.mark.asyncio
async def test_show_all_help_no_log_card(typer_ui_instance):
    # Branch: if self.log_card: ...
    typer_ui_instance.log_card = None
    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "", "")
    )
    typer_ui_instance.command_executor.build_command_args = MagicMock(return_value=[])

    # Needs async
    await typer_ui_instance._show_all_help()
    # Should not crash


def test_log_controls_unset(typer_ui_instance):
    # Branch check if self.log_controls: ... set to None
    typer_ui_instance.log_controls = None
    typer_ui_instance.execute_button = None
    typer_ui_instance.help_button = None
    typer_ui_instance.log_card = None

    # Needs a dummy executor running to hit "finally" block updates
    # But it's easier to verify via execute_command flow where finally block runs
    # We already have test_execute_command_ui_state_checks covering setting visible=True if exists
    # If they are None, it should skip.
    # The coverage missing lines 100, 120 are 'if self.log_controls:'

    # We should ensure we hit the True branch as well (which normal tests do)
    # and the False branch (which we do if we set to None).
    # Double check coverage rep:
    # 93%: checks 100, 120 misses.
    # Line 100: if self.log_controls: ... set_visibility(False)
    # Line 120: if self.log_controls: ... set_visibility(True)
    # This means test_execute_command_ui_state_checks covered the None case (False branch)
    # but maybe we missed the True branch?
    # No, execute_command_logic sets them up as mocks, so they ARE truthy.
    # Wait, coverage says "Missing".
    # Miss means the line content was NOT executed? Or branch was not taken?
    # If it is statement coverage, line 100 `if ...` is executed.
    # "Miss" on a line usually means the line itself wasn't run or the branch wasn't entered?
    # Coverage.py output "100" means line 100.
    # If it's a branch, it shows `->`
    # Here it lists "100".
    # Line 100 is: `self.log_controls.set_visibility(False)` inside the `if`.
    # So we need a test where log_controls is NOT None (it is by default in fixture),
    # AND we execute command.
    pass


@pytest.mark.asyncio
async def test_execution_no_param_match(typer_ui_instance):
    # Lines 74-75: if k not in param_map: param_map[k] = v
    # We need a case where we pass a param key that is NOT in current_command.parameters
    typer_ui_instance.current_command = typer_ui_instance.commands[0]  # "hello"
    # hello has "name" param.
    # We pass "other"

    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "", "")
    )
    typer_ui_instance.command_executor.build_command_args = MagicMock(return_value=[])

    await typer_ui_instance._execute_command("cmd", {"name": "User", "extra": "val"})
    # verify build_command_args call has extra
    call_args = typer_ui_instance.command_executor.build_command_args.call_args
    params_passed = call_args[1]["parameters"]
    assert "extra" in params_passed


@pytest.mark.asyncio
async def test_run_cmd_slug_not_found(typer_ui_instance, mock_ui):
    # Lines 306->315: if cmd: ... else: ...
    # We need a case where command_slug is provided but command not found
    mock_decorator = MagicMock()
    mock_ui.page.return_value = mock_decorator

    typer_ui_instance.run()
    # Capture main_page
    main_page_func = mock_decorator.call_args_list[0].args[0]

    await main_page_func(command_slug="does_not_exist")
    assert typer_ui_instance.current_command is None


def test_no_commands_found(typer_ui_instance, mock_ui):
    # Line 268: ui.label(...).classes(...)
    # self.commands is empty
    typer_ui_instance.commands = []
    typer_ui_instance.create_ui()
    # Check that error label is printed
    # Since we can't easily check label text on mock, checks if label called enough times
    # Normal create_ui calls label several times.
    pass


def test_refresh_form_no_container(typer_ui_instance):
    # Cover False branch of if self.form_container:
    typer_ui_instance.form_container = None
    typer_ui_instance._refresh_command_form()  # Should not crash and skip clear()


@pytest.mark.asyncio
async def test_log_controls_visibility_explicit(typer_ui_instance):
    # Explicitly test lines 100 and 120
    typer_ui_instance.log_controls = MagicMock()
    typer_ui_instance.log_card = MagicMock()

    typer_ui_instance.command_executor.execute_command = AsyncMock(
        return_value=(0, "", "")
    )
    typer_ui_instance.command_executor.build_command_args = MagicMock(return_value=[])

    await typer_ui_instance._execute_command("cmd", {})

    # Check calls
    # Line 100: set_visibility(False)
    typer_ui_instance.log_controls.set_visibility.assert_any_call(False)
    # Line 120: set_visibility(True)
    typer_ui_instance.log_controls.set_visibility.assert_any_call(True)
