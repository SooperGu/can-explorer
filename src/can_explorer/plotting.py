from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Generator, Iterable, Optional

import dearpygui.dearpygui as dpg

from can_explorer.layout import DEFAULT_PLOT_HEIGHT, PlotTable, Tag


class Config:
    PLOT = dict(
        no_title=True,
        no_menus=True,
        no_child=True,
        no_mouse_pos=True,
        no_highlight=True,
        no_box_select=True,
    )

    X_AXIS = dict(axis=dpg.mvXAxis, lock_min=True, lock_max=True, no_tick_labels=True)

    Y_AXIS = dict(axis=dpg.mvYAxis, lock_min=True, lock_max=True, no_tick_labels=True)


@dataclass
class PlotItem:
    parent: str
    data: str


@dataclass
class RowItem:
    table: PlotTable
    label: Optional[str] = None
    plot: Optional[PlotItem] = None


class PlotManager:
    height = DEFAULT_PLOT_HEIGHT
    plots: Dict[int, RowItem] = {}

    def _make_label(self, can_id: int) -> int:
        return dpg.add_button(
            tag=f"{Tag.PLOT_LABEL}{dpg.generate_uuid()}",
            label=hex(can_id),
            height=self.height,
            enabled=False,
        )

    def _make_plot(self, payloads: Iterable) -> PlotItem:
        with dpg.plot(
            tag=f"{Tag.PLOT_ITEM}{dpg.generate_uuid()}",
            height=self.height,
            **Config.PLOT,
        ) as plot:
            dpg.add_plot_axis(**Config.X_AXIS)
            with dpg.plot_axis(
                **Config.Y_AXIS,
            ):
                data = dpg.add_line_series(list(range(len(payloads))), payloads)

        return PlotItem(plot, data)

    @staticmethod
    @contextmanager
    def _make_row() -> Generator:
        row = RowItem(PlotTable())
        try:
            yield row
        finally:
            row.table.add_widget(row.label)
            row.table.add_widget(row.plot.parent)
            row.table.submit()

    def update_plot(self, can_id: int, payloads: Iterable) -> None:
        dpg.set_value(
            self.plots[can_id].plot.data, [list(range(len(payloads))), payloads]
        )

    def add_plot(self, can_id: int, payload: Iterable) -> None:
        with self._make_row() as row_item:
            row_item.label = self._make_label(can_id)
            row_item.plot = self._make_plot(payload)
        self.plots[can_id] = row_item

    def remove_plot(self, can_id: int) -> None:
        row_item = self.plots.pop(can_id)
        dpg.delete_item(row_item.table.table_id)

    def set_height(self, height: int) -> None:
        self.height = height
        for row_item in self.plots.values():
            dpg.set_item_height(row_item.label, self.height)
            dpg.set_item_height(row_item.plot.parent, self.height)

    def clear_all(self) -> None:
        while self.plots:
            self.remove_plot(list(self.plots).pop())
