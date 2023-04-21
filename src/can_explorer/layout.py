from enum import Enum, auto, unique
from pathlib import Path
from typing import Callable, Final, Iterable, Union

import dearpygui.dearpygui as dpg

from can_explorer.can_bus import PayloadBuffer
from can_explorer.resources import Percentage

RESOURCES_DIR = Path(__file__).parent / "resources"


class Default:
    WIDTH: Final = 600
    HEIGHT: Final = 600
    FONT_HEIGHT: Final = 14
    PLOT_HEIGHT: Final = 100
    BUFFER_SIZE: Final = 100
    FONT: Final = RESOURCES_DIR / "Inter-Medium.ttf"


class Font:
    DEFAULT: str
    LABEL: str


@unique
class Tag(str, Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()
    MAIN_BUTTON = auto()
    CLEAR_BUTTON = auto()
    PLOT_LABEL = auto()
    PLOT_ITEM = auto()
    TAB_VIEWER = auto()
    TAB_SETTINGS = auto()
    SETTINGS_PLOT_BUFFER = auto()
    SETTINGS_PLOT_HEIGHT = auto()
    SETTINGS_INTERFACE = auto()
    SETTINGS_CHANNEL = auto()
    SETTINGS_BAUDRATE = auto()
    SETTINGS_APPLY = auto()


class PercentageWidthTableRow:
    # https://github.com/hoffstadt/DearPyGui/discussions/1306

    def __init__(self, **kwargs):
        self.table_id = dpg.add_table(
            header_row=False,
            policy=dpg.mvTable_SizingStretchProp,
            **kwargs,
        )
        self.stage_id = dpg.add_stage()
        dpg.push_container_stack(self.stage_id)

    def add_widget(self, uuid, percentage):
        dpg.add_table_column(
            init_width_or_weight=percentage / 100.0, parent=self.table_id
        )
        dpg.set_item_width(uuid, -1)

    def submit(self):
        dpg.pop_container_stack()
        with dpg.table_row(parent=self.table_id):
            dpg.unstage(self.stage_id)


class PlotTable(PercentageWidthTableRow):
    COLUMN_1_WIDTH: Final = 15
    COLUMN_2_WIDTH: Final = 85

    def __init__(self, **kwargs):
        super().__init__(parent=Tag.TAB_VIEWER, **kwargs)

    def add_label(self, uuid):
        return super().add_widget(uuid, self.COLUMN_1_WIDTH)

    def add_plot(self, uuid):
        return super().add_widget(uuid, self.COLUMN_2_WIDTH)


def _init_fonts():
    global Font
    with dpg.font_registry():
        Font.DEFAULT = dpg.add_font(Default.FONT, Default.FONT_HEIGHT)
        Font.LABEL = dpg.add_font(Default.FONT, Default.FONT_HEIGHT * 1.75)

    dpg.bind_font(Font.DEFAULT)


def _init_themes():
    default_background = (50, 50, 50, 255)
    with dpg.theme() as disabled_theme:
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, default_background)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, default_background)

    dpg.bind_theme(disabled_theme)


def _header() -> None:
    def tab_callback(sender, app_data, user_data) -> None:
        current_tab = dpg.get_item_label(app_data)

        if current_tab == "Viewer":
            dpg.configure_item(Tag.TAB_VIEWER, show=True)
            dpg.configure_item(Tag.TAB_SETTINGS, show=False)
        else:
            dpg.configure_item(Tag.TAB_VIEWER, show=False)
            dpg.configure_item(Tag.TAB_SETTINGS, show=True)

    with dpg.tab_bar(tag=Tag.HEADER, callback=tab_callback):
        dpg.add_tab(label="Viewer")
        dpg.add_tab(label="Settings")


def _body() -> None:
    with dpg.child_window(tag=Tag.BODY, border=False):
        with dpg.group(tag=Tag.TAB_VIEWER, show=True):
            _viewer_tab()
        with dpg.group(tag=Tag.TAB_SETTINGS, show=False):
            _settings_tab()


def _footer() -> None:
    with dpg.child_window(tag=Tag.FOOTER, height=110, border=False, no_scrollbar=True):
        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=2)

        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                with dpg.group(horizontal=True):
                    dpg.add_text("Message Buffer Size")
                    dpg.add_spacer()
                    dpg.add_slider_int(
                        tag=Tag.SETTINGS_PLOT_BUFFER,
                        width=-1,
                        default_value=Percentage.get(
                            Default.BUFFER_SIZE, PayloadBuffer.MAX
                        ),
                        min_value=2,
                        max_value=100,
                        clamped=True,
                        format="%d%%",
                    )

                with dpg.group(horizontal=True):
                    dpg.add_text("Plot Height")
                    dpg.add_spacer()
                    dpg.add_slider_int(
                        tag=Tag.SETTINGS_PLOT_HEIGHT,
                        width=-1,
                        default_value=Percentage.get(Default.PLOT_HEIGHT, 500),
                        min_value=10,
                        max_value=100,
                        clamped=True,
                        format="%d%%",
                    )
        dpg.add_spacer(height=2)

        dpg.add_separator()
        dpg.add_spacer()
        with dpg.group(horizontal=True):
            dpg.add_button(
                tag=Tag.MAIN_BUTTON,
                label="Start",
                width=-100,
                height=50,
                user_data=False,
            )
            dpg.add_button(
                tag=Tag.CLEAR_BUTTON,
                label="Clear",
                width=-1,
                height=50,
            )


def _viewer_tab() -> None:
    ...


def _settings_tab() -> None:
    with dpg.collapsing_header(label="CAN Bus", default_open=True):
        dpg.add_combo(tag=Tag.SETTINGS_INTERFACE, label="Interface")
        dpg.add_input_text(tag=Tag.SETTINGS_CHANNEL, label="Channel")
        dpg.add_combo(tag=Tag.SETTINGS_BAUDRATE, label="Baudrate")
        dpg.add_spacer(height=5)
        dpg.add_button(tag=Tag.SETTINGS_APPLY, label="Apply", height=30)
        dpg.add_spacer(height=5)

    with dpg.collapsing_header(label="GUI"):
        dpg.add_button(
            label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
        )
        dpg.add_button(
            label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
        )
        dpg.add_spacer(height=5)


def create() -> None:
    _init_fonts()
    _init_themes()
    _header()
    _body()
    _footer()


def resize() -> None:
    dpg.set_item_height(
        Tag.BODY, (dpg.get_viewport_height() - dpg.get_item_height(Tag.FOOTER) - 50)
    )
    dpg.set_item_width(Tag.SETTINGS_APPLY, dpg.get_viewport_width() // 4)


def popup_error(name: Union[str, Exception], info: Union[str, Exception]) -> None:
    # https://github.com/hoffstadt/DearPyGui/discussions/1308

    def on_selection(sender, unused, user_data):
        # delete window
        dpg.delete_item(user_data[0])

    # guarantee these commands happen in the same frame
    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label="ERROR", modal=True, no_close=True) as modal_id:
            dpg.add_text(name, color=(255, 0, 0))  # red
            dpg.add_separator()
            dpg.add_text(info)
            with dpg.group():
                dpg.add_button(
                    label="Close",
                    width=-1,
                    user_data=(modal_id, True),
                    callback=on_selection,
                )

    # guarantee these commands happen in another frame
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(
        modal_id,
        [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2],
    )


def get_main_button_state() -> bool:
    return dpg.get_item_user_data(Tag.MAIN_BUTTON)


def get_settings_plot_buffer() -> int:
    max_value = PayloadBuffer.MAX
    percentage = dpg.get_value(Tag.SETTINGS_PLOT_BUFFER)
    return Percentage.reverse(percentage, max_value)


def get_settings_plot_height() -> int:
    max_value = 500  # px
    percentage = dpg.get_value(Tag.SETTINGS_PLOT_HEIGHT)
    return Percentage.reverse(percentage, max_value)


def get_settings_interface() -> str:
    return dpg.get_value(Tag.SETTINGS_INTERFACE)


def get_settings_channel() -> str:
    return dpg.get_value(Tag.SETTINGS_CHANNEL)


def get_settings_baudrate() -> int:
    return dpg.get_value(Tag.SETTINGS_BAUDRATE)


def set_main_button_callback(callback: Callable) -> None:
    button_labels = ("Stop", "Start")

    def wrapped_callback(sender, app_data, user_data):
        """
        Set the button label and toggle the state.
        """
        dpg.configure_item(
            Tag.MAIN_BUTTON, label=button_labels[user_data], user_data=not user_data
        )

        return callback(sender, app_data, user_data)

    dpg.configure_item(Tag.MAIN_BUTTON, callback=wrapped_callback)


def set_clear_button_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.CLEAR_BUTTON, callback=callback)


def set_plot_buffer_slider_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_PLOT_BUFFER, callback=callback)


def set_plot_height_slider_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_PLOT_HEIGHT, callback=callback)


def set_settings_apply_button_callback(callback: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_APPLY, callback=callback)


def set_settings_interface_options(iterable: Iterable[str]) -> None:
    dpg.configure_item(Tag.SETTINGS_INTERFACE, items=iterable)


def set_settings_baudrate_options(iterable: Iterable[str]) -> None:
    dpg.configure_item(Tag.SETTINGS_BAUDRATE, items=iterable)
