from enum import Enum, auto, unique
from typing import Callable, Final, Iterable

import dearpygui.dearpygui as dpg

WIDTH: Final = 600
HEIGHT: Final = 600

DEFAULT_PLOT_HEIGHT: Final = 100


@unique
class Tag(str, Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()
    PLOT_SCALE_SLIDER = auto()
    MAIN_BUTTON = auto()
    PLOT_LABEL = auto()
    PLOT_DATA = auto()
    TAB_VIEWER = auto()
    TAB_SETTINGS = auto()
    SETTINGS_INTERFACE = auto()
    SETTINGS_CHANNEL = auto()
    SETTINGS_BAUDRATE = auto()
    SETTINGS_APPLY = auto()
    SETTINGS_PLOT_HEIGHT = auto()


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
    COLUMN_1_PERCENTAGE: Final = 15
    COLUMN_2_PERCENTAGE: Final = 85

    def __init__(self, **kwargs):
        super().__init__(parent=Tag.TAB_VIEWER, **kwargs)

    def _determine_width(self, uuid) -> int:
        if uuid.startswith(Tag.PLOT_LABEL):
            return self.COLUMN_1_PERCENTAGE
        elif uuid.startswith(Tag.PLOT_DATA):
            return self.COLUMN_2_PERCENTAGE
        else:
            raise Exception("TODO")

    def add_widget(self, uuid):
        if uuid.startswith(Tag.PLOT_LABEL):
            percentage = self.COLUMN_1_PERCENTAGE
        elif uuid.startswith(Tag.PLOT_DATA):
            percentage = self.COLUMN_2_PERCENTAGE

        return super().add_widget(uuid, percentage)


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

        with dpg.group(horizontal=True):
            dpg.add_text("Plot Scale %")
            dpg.add_spacer()
            dpg.add_slider_int(
                tag=Tag.PLOT_SCALE_SLIDER, width=-1, default_value=50, format=""
            )
        dpg.add_spacer(height=2)

        dpg.add_separator()
        dpg.add_spacer()
        dpg.add_button(
            tag=Tag.MAIN_BUTTON, label="Start", width=-1, height=50, user_data=False
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
        dpg.add_input_int(
            tag=Tag.SETTINGS_PLOT_HEIGHT,
            label="Plot Height",
            default_value=DEFAULT_PLOT_HEIGHT,
            step=10,
            min_value=50,
            max_value=500,
            min_clamped=True,
            max_clamped=True,
        )
        dpg.add_button(
            label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
        )
        dpg.add_button(
            label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
        )
        dpg.add_spacer(height=5)


def create() -> None:
    _header()
    _body()
    _footer()


def resize() -> None:
    dpg.set_item_height(
        Tag.BODY, (dpg.get_viewport_height() - dpg.get_item_height(Tag.FOOTER) - 50)
    )
    dpg.set_item_width(Tag.SETTINGS_APPLY, dpg.get_viewport_width() // 4)


def get_settings_user_interface() -> str:
    return dpg.get_value(Tag.SETTINGS_INTERFACE)


def get_settings_user_channel() -> str:
    return dpg.get_value(Tag.SETTINGS_CHANNEL)


def get_settings_user_baudrate() -> int:
    return dpg.get_value(Tag.SETTINGS_BAUDRATE)


def get_settings_user_plot_height() -> int:
    return dpg.get_value(Tag.SETTINGS_PLOT_HEIGHT)


def set_main_button_callback(callable: Callable) -> None:
    dpg.configure_item(Tag.MAIN_BUTTON, callback=callable)


def set_plot_scale_slider_callback(callable: Callable) -> None:
    dpg.configure_item(Tag.PLOT_SCALE_SLIDER, callback=callable)


def set_settings_apply_button_callback(callable: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_APPLY, callback=callable)


def set_settings_plot_height_callback(callable: Callable) -> None:
    dpg.configure_item(Tag.SETTINGS_PLOT_HEIGHT, callback=callable)


def set_settings_interface_options(iterable: Iterable[str]) -> None:
    dpg.configure_item(Tag.SETTINGS_INTERFACE, items=iterable)


def set_settings_baudrate_options(iterable: Iterable[str]) -> None:
    dpg.configure_item(Tag.SETTINGS_BAUDRATE, items=iterable)