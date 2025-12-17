"""NiceGUI components for Typer UI"""

from nicegui import ui

from typer_ui.introspector import CommandNode, ParameterInfo


def create_parameter_input(param_info: ParameterInfo, value_container: dict):
    """Create a NiceGUI input component based on parameter info

    Args:
        param_info (dict): Parameter information dictionary
        value_container (dict): Dictionary to store the input value

    Returns:
        ui.element: Created NiceGUI input component
    """
    param_name = param_info.name
    param_type = param_info.param_type
    default = param_info.default
    required = param_info.required
    help_text = param_info.help
    python_type = param_info.python_type

    # Typer may mark required options/arguments with Ellipsis (`...`).
    # Normalize Ellipsis to None so UI code treats it as "no default".
    if default is ...:
        default = None

    # initialize stored value; for arguments without default keep empty string so UI can fill
    if param_name not in value_container:
        value_container[param_name] = default if default is not None else ""

    label_text = f"{param_name}"
    if required:
        label_text += " *"
    if help_text:
        label_text += f" - ({help_text})"
    # indicate whether this parameter is an argument or an option
    try:
        label_text += f" [{param_type.value}]"
    except Exception:
        pass

    # Choose widget based on discovered python_type
    if python_type is bool or (
        isinstance(python_type, type) and issubclass(python_type, bool)
    ):
        # NiceGUI checkbox expects the label as the first positional arg
        return ui.checkbox(
            label_text,
            value=bool(default),
            on_change=lambda e: value_container.update({param_name: e.value}),
        )

    if python_type is int or (
        isinstance(python_type, type) and issubclass(python_type, int)
    ):
        return ui.number(
            label=label_text,
            value=int(default) if default is not None else 0,
            on_change=lambda e: value_container.update(
                {param_name: int(e.value) if e.value is not None else 0}
            ),
        ).classes("w-full")

    if python_type is float or (
        isinstance(python_type, type) and issubclass(python_type, float)
    ):
        return ui.number(
            label=label_text,
            value=float(default) if default is not None else 0.0,
            on_change=lambda e: value_container.update({param_name: e.value}),
            step=0.1,
        ).classes("w-full")

    # default to text input
    return ui.input(
        label=label_text,
        value=str(default) if default is not None else "",
        on_change=lambda e: value_container.update({param_name: e.value}),
    ).classes("w-full")


def create_command_form(
    command_info: CommandNode, on_execute_callback, on_help_callback
):
    """Create a NiceGUI form for a command based on its parameters

    Args:
        command_info (dict): Command information dictionary
        on_execute_callback (Callable): Callback function to call on form submission
        on_help_callback (Callable): Callback function to call on help request

    Returns:
        tuple[dict, ui.button, ui.button]: Container with values, execute button, and help button
    """
    value_container = {}
    # Highlighted card style: Thick left border, shadow, and distinct header
    # Highlighted card style: Thick left border, shadow, and distinct header
    with ui.card().classes(
        "w-full shadow-md border border-gray-200 border-l-8 p-0 gap-0"
    ).style("border-left-color: var(--q-primary)"):
        # Header section with subtle background
        with ui.row().classes(
            "w-full items-start gap-4 bg-gray-50 p-4 border-b border-gray-200 no-wrap"
        ):
            ui.avatar("code", color="primary", text_color="white").classes("flex-shrink-0")
            with ui.column().classes("gap-1 flex-1 min-w-0"):
                ui.label(f"{command_info.name}").classes("text-xl font-bold text-gray-800 leading-tight")
                if command_info.help:
                    ui.label(command_info.help).classes("text-sm text-gray-600 whitespace-normal")

        # Form inputs container
        with ui.column().classes("w-full gap-4 p-4"):
            for param_info in command_info.parameters:
                create_parameter_input(param_info, value_container)

            with ui.row().classes("w-full justify-end gap-2"):
                help_btn = ui.button(
                    "Help",
                    on_click=lambda: on_help_callback(command_info.name),
                    color="secondary",
                )
                execute_btn = ui.button(
                    "Execute",
                    on_click=lambda: on_execute_callback(command_info.name, value_container),
                )

    return value_container, execute_btn, help_btn


def header(
    commands: list[CommandNode],
    on_command_change_callback,
    current_path: str = None,
):
    with ui.header().classes("items-center justify-between"):
        # Left side: Logo/Title
        with ui.row().classes("items-center gap-2 cursor-pointer").on(
            "click", lambda: ui.navigate.to("/")
        ):
            ui.icon("terminal", color="white").classes("text-2xl")
            ui.label("Typer UI").classes("text-xl font-bold text-white")

        # Right side: Menu
        with ui.row().classes("items-center"):
            with ui.row().classes("max-sm:hidden"):
                for node in commands:
                    if node.is_group:
                        # parent item that stays open when opening the nested menu
                        # Check if any child is selected
                        is_group_active = current_path and current_path.startswith(
                            f"{node.name}/"
                        )
                        
                        # Active: Simulate hover effect (semi-transparent white)
                        # Inactive: Flat, white text
                        if is_group_active:
                            # bg-white/20 is roughly standard hover on primary
                            props_str = "flat color=white"
                            classes_str = "bg-white/20"
                        else:
                            props_str = "flat color=white"
                            classes_str = ""
                        
                        with ui.button(node.name).props(props_str).classes(classes_str):
                            with ui.menu():
                                for child in node.children:
                                    path = f"{node.name}/{child.name}".strip("/")
                                    is_active = path == current_path
                                    # bind path into default arg to avoid late binding
                                    item = ui.menu_item(
                                        child.name,
                                        on_click=lambda e,
                                        p=path: on_command_change_callback(p),
                                        auto_close=False,
                                    )
                                    if is_active:
                                        # Use standard hover gray for active state
                                        item.classes("bg-gray-200 font-bold")
                    else:
                        # top-level command - single item
                        is_active = node.name == current_path
                        if is_active:
                            props_str = "flat color=white"
                            classes_str = "bg-white/20"
                        else:
                            props_str = "flat color=white"
                            classes_str = ""
                            
                        ui.button(
                            node.name,
                            on_click=lambda e, p=node.name: on_command_change_callback(p),
                        ).props(props_str).classes(classes_str)

            with ui.row().classes("sm:hidden"):
                with ui.button(icon="menu").props("flat color=white"):
                    with ui.menu():
                        for node in commands:
                            if node.is_group:
                                with ui.menu_item(node.name, auto_close=False).props(
                                    "flat color=white"
                                ):
                                    with ui.item_section().props("side"):
                                        ui.icon("keyboard_arrow_right")
                                    with ui.menu().props(
                                        "anchor='top end' self='top start' auto-close"
                                    ):
                                        for child in node.children:
                                            path = f"{node.name}/{child.name}".strip("/")
                                            is_active = path == current_path
                                            item = ui.menu_item(
                                                child.name,
                                                on_click=lambda e,
                                                p=path: on_command_change_callback(p),
                                            ).props("flat color=white")
                                            if is_active:
                                                item.classes("bg-gray-200 text-primary")
                            else:
                                path = node.name
                                is_active = path == current_path
                                item = ui.menu_item(
                                    node.name,
                                    on_click=lambda e,
                                    p=node.name: on_command_change_callback(p),
                                ).props("flat color=white")
                                if is_active:
                                    item.classes("bg-gray-200 text-primary")


def create_log_display():
    """Create a NiceGUI component for displaying command execution logs

    Returns:
        ui.element: Created NiceGUI log display component
    """
    # Monokai/VSCode theme style: Dark background, light text, monospace
    return ui.log(max_lines=1000).classes(
        "w-full h-96 bg-[#1e1e1e] text-[#f8f8f2] font-mono p-4 rounded-md shadow-inner text-sm"
    )


def create_command_menu(commands: list[CommandNode], on_command_change_callback):
    """Create a nested menu (buttons) for top-level commands and groups.

    Renders top-level commands as buttons and groups as expandable sections. When a
    command is selected the callback is called with a path-like name
    ("group/command" or "command").
    """

    # Render a single menu trigger (hamburger) that contains top-level commands
    # and groups. Groups are menu_items with auto_close=False and a nested menu
    # using the same pattern as the NiceGUI example provided by the user.

    with ui.button(icon="menu"):
        with ui.menu():
            for node in commands:
                if node.is_group:
                    # parent item that stays open when opening the nested menu
                    with ui.menu_item(node.name, auto_close=False):
                        with ui.item_section().props("side"):
                            ui.icon("keyboard_arrow_right")
                        # nested submenu anchored to the right/top
                        with ui.menu().props(
                            'anchor="top end" self="top start" auto-close'
                        ):
                            for child in node.children:
                                path = f"{node.name}/{child.name}".strip("/")
                                # bind path into default arg to avoid late binding
                                ui.menu_item(
                                    child.name,
                                    on_click=lambda e,
                                    p=path: on_command_change_callback(p),
                                    auto_close=False,
                                )
                else:
                    # top-level command - single item
                    ui.menu_item(
                        node.name,
                        on_click=lambda e, p=node.name: on_command_change_callback(p),
                        auto_close=False,
                    )

    return None


def create_execution_controls(on_export, on_clear):
    """Create NiceGUI buttons for controlling command execution

    Args:
        on_export (Callable): Callback for export button
        on_clear (Callable): Callback for clear button

    Returns:
        ui.element: Created NiceGUI row component containing buttons
    """
    with ui.row().classes("gap-2") as container:
        export_btn = ui.button("Export", on_click=on_export, icon="download").props(
            "flat dense color=primary"
        )
        ui.button("Clear Logs", on_click=on_clear, icon="delete").props(
            "flat dense color=primary"
        )
    return container, export_btn

