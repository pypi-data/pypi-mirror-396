import sys

import pytest

from typer_ui.command_executor import CommandExecutor
from typer_ui.introspector import ParameterInfo, ParamType


@pytest.mark.asyncio
async def test_execute_command_success(mocker):
    # Mock asyncio.create_subprocess_exec
    mock_process = mocker.AsyncMock()
    mock_process.stdout = mocker.AsyncMock()
    mock_process.stderr = mocker.AsyncMock()
    mock_process.wait.return_value = 0

    # Mock reading lines
    mock_process.stdout.readline = mocker.AsyncMock(
        side_effect=[b"line1\n", b"line2\n", b""]
    )
    mock_process.stderr.readline = mocker.AsyncMock(side_effect=[b""])

    mocker.patch("asyncio.create_subprocess_exec", return_value=mock_process)

    output_lines = []

    def output_cb(msg):
        output_lines.append(msg)

    executor = CommandExecutor(output_callback=output_cb)
    ret, stdout, stderr = await executor.execute_command(["echo", "hello"])

    assert ret == 0
    assert "line1" in stdout
    assert "line2" in stdout
    assert "line1" in output_lines
    assert "line2" in output_lines
    assert not executor.is_running


@pytest.mark.asyncio
async def test_execute_command_error(mocker):
    mocker.patch("asyncio.create_subprocess_exec", side_effect=OSError("Exec failed"))

    output_lines = []
    executor = CommandExecutor(output_callback=lambda m: output_lines.append(m))

    ret, stdout, stderr = await executor.execute_command(["invalid_cmd"])

    assert ret == 1
    assert "Error executing command: Exec failed" in stderr
    assert "Error executing command: Exec failed" in output_lines


def test_build_command_args():
    executor = CommandExecutor()
    module = "my_module"

    # 1. Simple command with one positional arg
    # Note: introspector isn't used here directly, caller passes raw dict.
    # But usually the caller passes (ParameterInfo, value) tuples or just values.
    # The logic in build_command_args handles both.

    # Case A: Legacy/Simple values
    params = {"name": "Alice", "count": 1, "flag": True}
    # Logic:
    # - name -> --name Alice
    # - count -> --count 1
    # - flag -> --flag
    # IF no metadata is present, it assumes everything is an option unless manual handling matches.
    # Wait, looking at the code:
    # `if param_info.param_type == ParamType.ARGUMENT: positional_parts.append...`
    # `else: option_parts...`
    # If param_info is None (legacy path), it goes to `else` (option style).

    args = executor.build_command_args(module, "greet", params)
    expected_base = [sys.executable, module, "greet"]
    assert args[:3] == expected_base
    assert "--name" in args
    assert "Alice" in args
    assert "--count" in args
    assert "1" in args
    assert "--flag" in args

    # Case B: With ParameterInfo metadata (simulating real usage)
    p_arg = ParameterInfo(name="name", param_type=ParamType.ARGUMENT, python_type=str)
    p_opt = ParameterInfo(name="count", param_type=ParamType.OPTION, python_type=int)

    rich_params = {"name": (p_arg, "Alice"), "count": (p_opt, 5)}

    args = executor.build_command_args(module, "greet", rich_params)
    # Check that positional came first
    # args: [exe, module, greet, "Alice", "--count", "5"]
    assert args[3] == "Alice"
    assert args[4] == "--count"
    assert args[5] == "5"


def test_build_command_args_nested():
    executor = CommandExecutor()
    args = executor.build_command_args("mod", "group/sub", {})
    assert args[2] == "group"
    assert args[2] == "group"
    assert args[3] == "sub"


def test_build_command_args_edge_cases():
    executor = CommandExecutor()
    module = "mod"
    # Case C: Mixed and edge cases for coverage
    # 1. No param info found for a key
    args_edge = executor.build_command_args(
        module, "cmd", {"unknown": "val", "bool_flag": True}
    )
    assert "--unknown" in args_edge
    assert "val" in args_edge
    assert "--bool-flag" in args_edge

    # 2. Boolean true/false handling without metadata
    args_bool = executor.build_command_args(
        module, "cmd", {"flag": True, "noflag": False}
    )
    assert "--flag" in args_bool
    assert "--noflag" not in args_bool

    # 3. Empty value check (Line 138)
    # If value is "", continue
    args_empty = executor.build_command_args(module, "cmd", {"empty": ""})
    # Should not include empty
    assert "--empty" not in args_empty

    # 4. Legacy bool check (Line 152: if value: ...)
    # Already covered by "flag": True above?
    # Let's verify exactly which branch:
    # if isinstance(raw, (list, tuple)) ... else: value=raw
    # if param_info...
    # else: # no param info (lines 157)
    # if isinstance(value, bool): if value: ...
    # So "flag": True covers lines 158-160.

    # What about lines 152-153?
    # That is inside `if param_info is not None ...`
    # checking `if isinstance(value, bool): if value: ...`
    # We need to construct a case with valid param_info but bool value

    # We can mock ParameterInfo easily or use a real object
    # But since build_command_args handles `(ParameterInfo, value)`
    # We can pass that.
    pass


def test_build_command_args_with_param_info_bool():
    # Covers lines 151-153
    executor = CommandExecutor()
    from typer_ui.introspector import ParameterInfo, ParamType

    info = ParameterInfo(name="mybool", param_type=ParamType.OPTION, python_type=bool)

    # Case 1: True
    args_true = executor.build_command_args("mod", "cmd", {"mybool": (info, True)})
    assert "--mybool" in args_true

    # Case 2: False
    args_false = executor.build_command_args("mod", "cmd", {"mybool": (info, False)})
    assert "--mybool" not in args_false


@pytest.mark.asyncio
async def test_execute_command_exception(mocker):
    # Cover the specific exception clause in execute_command
    mocker.patch(
        "asyncio.create_subprocess_exec", side_effect=OSError("Process failed")
    )

    output = []
    executor = CommandExecutor(output_callback=lambda m: output.append(m))

    ret, out, err = await executor.execute_command(["cmd"])
    assert ret == 1
    assert "Error executing command: Process failed" in err


def test_stop_execution_no_process():
    # Cover safe stop when no process or not running
    executor = CommandExecutor()
    executor.is_running = False
    executor.process = None
    executor.stop_execution()  # Should not raise

    executor.is_running = True
    executor.process = None
    executor.stop_execution()  # Should not raise


def test_stop_execution(mocker):
    executor = CommandExecutor()
    executor.process = mocker.Mock()
    executor.is_running = True

    executor.stop_execution()

    executor.process.terminate.assert_called_once()


def test_stop_execution_error(mocker):
    executor = CommandExecutor()
    executor.process = mocker.Mock()
    executor.is_running = True
    executor.process.terminate.side_effect = ProcessLookupError("error")

    # Should catch exception and log
    output = []
    executor.output_callback = lambda m: output.append(m)

    executor.stop_execution()
    assert "Error terminating process" in output[0]


@pytest.mark.asyncio
async def test_read_stream_error(mocker):
    executor = CommandExecutor()
    stream = mocker.AsyncMock()
    stream.readline.side_effect = OSError("Read fail")

    lines = []
    output = []
    executor.output_callback = lambda m: output.append(m)

    await executor._read_stream(stream, lines, "TEST")

    assert "Error reading TEST stream" in output[0]
    assert "Error reading TEST stream" in lines[0]
