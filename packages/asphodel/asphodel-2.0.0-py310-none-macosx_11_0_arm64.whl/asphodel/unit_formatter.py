from collections.abc import Callable
from ctypes import Array, c_char, create_string_buffer
from typing import Any

from .clib import (AsphodelError, AsphodelUnitFormatter, ChannelInfo,
                   CtrlVarInfo, lib)


class UnitFormatter:
    def __init__(self, formatter: AsphodelUnitFormatter,
                 recreate: tuple[Any, ...]) -> None:
        self.formatter = formatter
        self._recreate = recreate

        # copy some values out
        self.unit_ascii = self.formatter.unit_ascii.decode("ascii")
        self.unit_utf8 = self.formatter.unit_utf8.decode("utf-8")
        self.unit_html = self.formatter.unit_html.decode("ascii")
        self.conversion_scale = self.formatter.conversion_scale
        self.conversion_offset = self.formatter.conversion_offset

    def __del__(self) -> None:
        self.formatter.free(self.formatter)

    def __reduce__(self) -> tuple[Any, ...]:
        return self._recreate

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            self_tuple = (self.unit_ascii, self.unit_utf8, self.unit_html,
                          self.conversion_scale, self.conversion_offset)
            other_tuple = (other.unit_ascii, other.unit_utf8, other.unit_html,
                           other.conversion_scale, other.conversion_offset)
            return self_tuple == other_tuple
        else:
            return NotImplemented

    def format_bare(self, value: float) -> str:
        buffer = create_string_buffer(256)
        self.formatter.format_bare(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")

    def format_ascii(self, value: float) -> str:
        buffer = create_string_buffer(256)
        self.formatter.format_ascii(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")

    def format_utf8(self, value: float) -> str:
        buffer = create_string_buffer(256)
        self.formatter.format_utf8(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("utf-8")

    def format_html(self, value: float) -> str:
        buffer = create_string_buffer(256)
        self.formatter.format_html(self.formatter, buffer, len(buffer), value)
        return buffer.value.decode("ascii")


def create_unit_formatter(unit_type: int, minimum: float, maximum: float,
                          resolution: float,
                          use_metric: bool = True) -> UnitFormatter:
    use_metric_int = 1 if use_metric else 0
    formatter = lib.asphodel_create_unit_formatter(
        unit_type, minimum, maximum, resolution, use_metric_int)
    if not formatter:
        raise AsphodelError(
            0, "asphodel_create_unit_formatter returned NULL")
    recreate = (create_unit_formatter,
                (unit_type, minimum, maximum, resolution, use_metric))
    return UnitFormatter(formatter.contents, recreate)


def create_custom_unit_formatter(
        scale: float, offset: float, resolution: float, unit_ascii: str,
        unit_utf8: str, unit_html: str) -> UnitFormatter:
    formatter = lib.asphodel_create_custom_unit_formatter(
        scale, offset, resolution, unit_ascii.encode("ascii"),
        unit_utf8.encode("utf-8"), unit_html.encode("ascii"))
    if not formatter:
        raise AsphodelError(
            0, "asphodel_create_custom_unit_formatter returned NULL")
    recreate = (create_custom_unit_formatter,
                (scale, offset, resolution, unit_ascii, unit_utf8, unit_html))
    return UnitFormatter(formatter.contents, recreate)


FormatFunc = Callable[[Array[c_char], int, int, float, int, float], int]


def _format_value(lib_func: FormatFunc, unit_type: int, resolution: float,
                  value: float, use_metric: bool) -> bytes:
    use_metric_int = 1 if use_metric else 0
    buffer = create_string_buffer(256)
    lib_func(buffer, len(buffer), unit_type, resolution, use_metric_int, value)
    return buffer.value


def format_value_ascii(unit_type: int, resolution: float, value: float,
                       use_metric: bool = True) -> str:
    return _format_value(lib.asphodel_format_value_ascii, unit_type,
                         resolution, value, use_metric).decode("ascii")


def format_value_utf8(unit_type: int, resolution: float, value: float,
                      use_metric: bool = True) -> str:
    return _format_value(lib.asphodel_format_value_utf8, unit_type, resolution,
                         value, use_metric).decode("utf-8")


def format_value_html(unit_type: int, resolution: float, value: float,
                      use_metric: bool = True) -> str:
    return _format_value(lib.asphodel_format_value_html, unit_type, resolution,
                         value, use_metric).decode("ascii")


def get_channel_unit_formatter(channel: ChannelInfo,
                               use_metric: bool) -> UnitFormatter:
    return create_unit_formatter(
        channel.unit_type, channel.minimum, channel.maximum,
        channel.resolution, use_metric)


def get_ctrl_var_unit_formatter(ctrl_var_info: CtrlVarInfo,
                                use_metric: bool) -> UnitFormatter:
    return create_unit_formatter(
        ctrl_var_info.unit_type,
        ctrl_var_info.minimum * ctrl_var_info.scale + ctrl_var_info.offset,
        ctrl_var_info.maximum * ctrl_var_info.scale + ctrl_var_info.offset,
        ctrl_var_info.scale,
        use_metric
    )
