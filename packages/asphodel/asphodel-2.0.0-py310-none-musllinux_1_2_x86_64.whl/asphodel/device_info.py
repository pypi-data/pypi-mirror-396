from collections.abc import Sequence
from ctypes import POINTER, c_char_p, c_int, c_uint, c_uint8
from dataclasses import dataclass
from typing import Any, TypeVar

from .clib import (AsphodelDeviceDecoder, AsphodelDeviceInfo, AsphodelError,
                   ChannelCalibration, ChannelInfo, CtrlVarInfo, SettingInfo,
                   StreamInfo, StreamRateInfo, SupplyInfo, SupplyResult, lib)
from .decoder import DeviceDecoder

T = TypeVar("T")


def _from_bytes(b: bytes | None, default: T) -> str | T:
    if b is None:
        return default
    return b.decode("utf-8", "replace")


@dataclass
class DeviceInfo:
    # NOTE: all structures in this are held by the underlying C struct, and
    # are not copied. If this class instance is GC'd then any held references
    # will become invalid!

    _device_info: AsphodelDeviceInfo

    serial_number: str
    location_string: str
    max_incoming_param_length: int
    max_outgoing_param_length: int
    stream_packet_length: int
    remote_max_incoming_param_length: int
    remote_max_outgoing_param_length: int
    remote_stream_packet_length: int
    supports_bootloader: bool
    supports_radio: bool
    supports_remote: bool
    supports_rf_power: bool

    build_date: str
    build_info: str
    nvm_hash: str | None
    nvm_modified: bool | None
    setting_hash: str | None
    board_info: tuple[str, int]

    protocol_version: str

    chip_family: str
    chip_id: str
    chip_model: str

    bootloader_info: str

    # for these lists, if the elements are None then the state is unknown,
    # but the count is still good.
    rgb: list[tuple[int, int, int] | None]
    led: list[int | None]

    commit_id: str
    repo_branch: str
    repo_name: str

    stream_filler_bits: int
    stream_id_bits: int
    streams: list[StreamInfo]
    stream_rates: list[StreamRateInfo]

    # these lists will always have the same length
    channels: list[ChannelInfo]
    channel_calibrations: list[ChannelCalibration | None]

    # these lists will always have the same length
    supplies: list[SupplyInfo]
    supply_results: list[SupplyResult | None]

    # these lists will always have the same length
    ctrl_vars: list[CtrlVarInfo]
    ctrl_var_states: list[int | None]

    settings: list[SettingInfo]

    custom_enums: list[list[str]]

    setting_categories: list[tuple[str, list[int]]]

    device_mode: int | None

    rf_power_ctrl_vars: list[int]
    rf_power_enabled: bool

    radio_ctrl_vars: list[int]
    radio_default_serial: int | None
    radio_scan_power: bool | None

    nvm: bytes
    tag_locations: tuple[int, int, int, int, int, int]

    user_tag_1: str
    user_tag_2: str

    def __del__(self) -> None:
        self._device_info.free_device_info(self._device_info)

    @classmethod
    def from_struct(cls, device_info: AsphodelDeviceInfo) -> "DeviceInfo":
        nvm_modified: bool | None
        if device_info.nvm_modified:
            nvm_modified = bool(device_info.nvm_modified.contents.value)
        else:
            nvm_modified = None

        board_info: tuple[str, int]
        if device_info.board_info_name:
            board_info = (device_info.board_info_name.decode("utf-8"),
                          device_info.board_info_rev)
        else:
            board_info = ("UNKNOWN", 0)

        rgb: list[tuple[int, int, int] | None]
        if device_info.rgb_count_known != 0:
            if device_info.rgb_settings:
                rgb = []
                for i in range(device_info.rgb_count):
                    rgb.append(tuple(device_info.rgb_settings[i]))
            else:
                rgb = [None] * device_info.rgb_count
        else:
            rgb = []

        led: list[int | None]
        if device_info.led_count_known != 0:
            if device_info.led_settings:
                led = []
                for i in range(device_info.led_count):
                    led.append(device_info.led_settings[i])
            else:
                led = [None] * device_info.led_count
        else:
            led = []

        streams: list[StreamInfo] = []
        stream_rates: list[StreamRateInfo] = []
        if device_info.stream_count_known != 0:
            if device_info.streams:
                for i in range(device_info.stream_count):
                    streams.append(device_info.streams[i])

                for i in range(device_info.stream_count):
                    if device_info.stream_rates:
                        stream_rate = device_info.stream_rates[i]
                    else:
                        stream_rate = StreamRateInfo()
                        stream_rate.available = 0
                    stream_rates.append(stream_rate)

        channels: list[ChannelInfo]
        channel_calibrations: list[ChannelCalibration | None]
        if device_info.channel_count_known != 0:
            if device_info.channels:
                channels = []
                for i in range(device_info.channel_count):
                    channels.append(device_info.channels[i])

                if device_info.channel_calibrations:
                    channel_calibrations = []
                    for i in range(device_info.channel_count):
                        cal = device_info.channel_calibrations[i]
                        if cal:
                            channel_calibrations.append(cal.contents)
                        else:
                            channel_calibrations.append(None)
                else:
                    channel_calibrations = \
                        [None] * device_info.channel_count
            else:
                channels = []
                channel_calibrations = []
        else:
            channels = []
            channel_calibrations = []

        supplies: list[SupplyInfo]
        supply_results: list[SupplyResult | None]
        if device_info.supply_count_known != 0:
            if device_info.supplies:
                supplies = []
                for i in range(device_info.supply_count):
                    supplies.append(device_info.supplies[i])

                if device_info.supply_results:
                    supply_results = []
                    for i in range(device_info.supply_count):
                        supply_results.append(device_info.supply_results[i])
                else:
                    supply_results = \
                        [None] * device_info.supply_count
            else:
                supplies = []
                supply_results = []
        else:
            supplies = []
            supply_results = []

        ctrl_vars: list[CtrlVarInfo]
        ctrl_var_states: list[int | None]
        if device_info.ctrl_var_count_known != 0:
            if device_info.ctrl_vars:
                ctrl_vars = []
                for i in range(device_info.ctrl_var_count):
                    ctrl_vars.append(device_info.ctrl_vars[i])

                if device_info.ctrl_var_states:
                    ctrl_var_states = []
                    for i in range(device_info.ctrl_var_count):
                        state: int = device_info.ctrl_var_states[i]
                        ctrl_var_states.append(state)
                else:
                    ctrl_var_states = [None] * device_info.ctrl_var_count
            else:
                ctrl_vars = []
                ctrl_var_states = []
        else:
            ctrl_vars = []
            ctrl_var_states = []

        settings: list[SettingInfo] = []
        if device_info.setting_count_known != 0:
            if device_info.settings:
                for i in range(device_info.setting_count):
                    settings.append(device_info.settings[i])

        custom_enums: list[list[str]] = []
        if device_info.custom_enum_lengths and device_info.custom_enum_values:
            for i in range(device_info.custom_enum_count):
                length: int = device_info.custom_enum_lengths[i]
                values: list[str] = []
                for j in range(length):
                    value: bytes = device_info.custom_enum_values[i][j]
                    values.append(value.decode("utf-8"))
                custom_enums.append(values)

        setting_categories: list[tuple[str, list[int]]] = []
        if device_info.setting_category_count_known != 0:
            if (device_info.setting_category_names and
                    device_info.setting_category_settings_lengths and
                    device_info.setting_category_settings):
                for i in range(device_info.setting_category_count):
                    name: bytes = device_info.setting_category_names[i]
                    length = device_info.setting_category_settings_lengths[i]
                    s: list[int] = \
                        device_info.setting_category_settings[i][0:length]
                    setting_categories.append((name.decode("utf-8"), s))

        device_mode: int | None
        if device_info.supports_device_mode:
            if device_info.supports_device_mode.contents.value != 0:
                device_mode = device_info.device_mode
            else:
                device_mode = None
        else:
            device_mode = None

        rf_power_ctrl_vars: list[int]
        if device_info.rf_power_ctrl_var_count_known != 0:
            if device_info.rf_power_ctrl_vars:
                rf_power_ctrl_vars = device_info.rf_power_ctrl_vars[
                    0:device_info.rf_power_ctrl_var_count]
            else:
                rf_power_ctrl_vars = []
        else:
            rf_power_ctrl_vars = []

        radio_ctrl_vars: list[int] = []
        if device_info.radio_ctrl_var_count_known != 0:
            if device_info.radio_ctrl_vars:
                radio_ctrl_vars = device_info.radio_ctrl_vars[
                    0:device_info.radio_ctrl_var_count]
            else:
                radio_ctrl_vars = []
        else:
            radio_ctrl_vars = []

        radio_default_serial: int | None
        if device_info.radio_default_serial:
            radio_default_serial = \
                device_info.radio_default_serial.contents.value
        else:
            radio_default_serial = None

        radio_scan_power: bool | None
        if device_info.radio_scan_power_supported:
            radio_scan_power = bool(
                device_info.radio_scan_power_supported.contents.value)
        else:
            radio_scan_power = None

        if device_info.nvm and device_info.nvm_size > 0:
            nvm = bytes(device_info.nvm[0:device_info.nvm_size])
        else:
            nvm = b""

        return cls(
            _device_info=device_info,
            serial_number=_from_bytes(device_info.serial_number, "UNKNOWN"),
            location_string=_from_bytes(device_info.location_string,
                                        "UNKNOWN"),
            max_incoming_param_length=device_info.max_incoming_param_length,
            max_outgoing_param_length=device_info.max_outgoing_param_length,
            remote_max_incoming_param_length=(
                device_info.remote_max_incoming_param_length),
            remote_max_outgoing_param_length=(
                device_info.remote_max_outgoing_param_length),
            remote_stream_packet_length=(
                device_info.remote_stream_packet_length),
            stream_packet_length=device_info.stream_packet_length,
            supports_bootloader=bool(device_info.supports_bootloader),
            supports_radio=bool(device_info.supports_radio),
            supports_remote=bool(device_info.supports_remote),
            supports_rf_power=bool(device_info.supports_rf_power),
            build_date=_from_bytes(device_info.build_date, "UNKNOWN"),
            build_info=_from_bytes(device_info.build_info, "UNKNOWN"),
            nvm_hash=_from_bytes(device_info.nvm_hash, None),
            nvm_modified=nvm_modified,
            setting_hash=_from_bytes(device_info.setting_hash, None),
            board_info=board_info,
            protocol_version=_from_bytes(device_info.protocol_version,
                                         "UNKNOWN"),
            chip_family=_from_bytes(device_info.chip_family, "UNKNOWN"),
            chip_id=_from_bytes(device_info.chip_id, "UNKNOWN"),
            chip_model=_from_bytes(device_info.chip_model, "UNKNOWN"),
            bootloader_info=_from_bytes(device_info.bootloader_info,
                                        "UNKNOWN"),
            rgb=rgb,
            led=led,
            commit_id=_from_bytes(device_info.commit_id, "UNKNOWN"),
            repo_branch=_from_bytes(device_info.repo_branch, "UNKNOWN"),
            repo_name=_from_bytes(device_info.repo_name, "UNKNOWN"),
            stream_filler_bits=device_info.stream_filler_bits,
            stream_id_bits=device_info.stream_id_bits,
            streams=streams,
            stream_rates=stream_rates,
            channels=channels,
            channel_calibrations=channel_calibrations,
            supplies=supplies,
            supply_results=supply_results,
            ctrl_vars=ctrl_vars,
            ctrl_var_states=ctrl_var_states,
            settings=settings,
            custom_enums=custom_enums,
            setting_categories=setting_categories,
            device_mode=device_mode,
            rf_power_ctrl_vars=rf_power_ctrl_vars,
            rf_power_enabled=bool(device_info.rf_power_enabled),
            radio_ctrl_vars=radio_ctrl_vars,
            radio_default_serial=radio_default_serial,
            radio_scan_power=radio_scan_power,
            nvm=nvm,
            tag_locations=tuple(device_info.tag_locations),
            user_tag_1=_from_bytes(device_info.user_tag_1, ""),
            user_tag_2=_from_bytes(device_info.user_tag_2, ""),
        )

    def __repr__(self) -> str:
        return self.to_json()

    def __reduce__(self) -> tuple[Any, ...]:
        return (DeviceInfo.from_json, (self.to_json(),))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeviceInfo):
            return False
        return lib.asphodel_device_info_equal(
            self._device_info, other._device_info) != 0

    def is_subset(self, other: "DeviceInfo") -> bool:
        return lib.asphodel_device_info_is_subset(
            self._device_info, other._device_info) != 0

    @staticmethod
    def from_json_raw(json: str) -> AsphodelDeviceInfo:
        json_bytes = json.encode("utf-8")
        device_info_ptr = POINTER(AsphodelDeviceInfo)()
        lib.asphodel_get_device_info_from_json(
            json_bytes, device_info_ptr, None)
        return device_info_ptr.contents

    @classmethod
    def from_json(cls, json: str) -> "DeviceInfo":
        return cls.from_struct(cls.from_json_raw(json))

    @staticmethod
    def from_json_with_excess_raw(json: str) -> tuple[AsphodelDeviceInfo, str]:
        json_bytes = json.encode("utf-8")
        device_info_ptr = POINTER(AsphodelDeviceInfo)()
        out = c_char_p()
        lib.asphodel_get_device_info_from_json(
            json_bytes, device_info_ptr, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No excess string returned")
        lib.asphodel_free_string(out)
        return (device_info_ptr.contents, out_bytes.decode("utf-8"))

    @classmethod
    def from_json_with_excess(cls, json: str) -> tuple["DeviceInfo", str]:
        device_info, excess = cls.from_json_with_excess_raw(json)
        return (cls.from_struct(device_info), excess)

    @staticmethod
    def raw_to_json(device_info: AsphodelDeviceInfo) -> str:
        out = c_char_p()
        lib.asphodel_get_json_from_device_info(device_info, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No JSON string returned")
        lib.asphodel_free_string(out)
        return out_bytes.decode("utf-8")

    def to_json(self) -> str:
        return self.raw_to_json(self._device_info)

    @staticmethod
    def raw_summary(device_info: AsphodelDeviceInfo) -> str:
        out = c_char_p()
        lib.asphodel_get_device_info_summary(device_info, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No summary string returned")
        lib.asphodel_free_string(out)
        return out_bytes.decode("utf-8", "replace")

    def summary(self) -> str:
        return self.raw_summary(self._device_info)

    def get_decoder_raw(
            self, active_streams: Sequence[int]) -> AsphodelDeviceDecoder:
        decoder_ptr = POINTER(AsphodelDeviceDecoder)()
        active_streams_array = (c_uint8 * len(active_streams))(*active_streams)
        lib.asphodel_create_device_info_decoder(
            self._device_info, active_streams_array, len(active_streams),
            decoder_ptr)
        return decoder_ptr.contents

    def get_decoder(self, active_streams: Sequence[int]) -> DeviceDecoder:
        # because the python decoder wrappers are structured such that they
        # need the channels and stream structs passed in independently, we
        # can't just wrap the get_decoder_raw() function, and instead we need
        # to build up an info list manually and create the device decoder in
        # the "usual" way.
        info_list: list[tuple[int, StreamInfo, list[ChannelInfo]]] = []
        for stream_id in active_streams:
            stream: StreamInfo = self.streams[stream_id]
            channel_list: list[ChannelInfo] = []
            for ch_index in stream.channel_index_list:
                channel_list.append(self.channels[ch_index])
            info_list.append((stream_id, stream, channel_list))

        return DeviceDecoder.create(
            info_list, self.stream_filler_bits, self.stream_id_bits,
            self.stream_packet_length)

    def get_streaming_counts(self, response_time: float, buffer_time: float,
                             timeout: int) -> tuple[int, int, int]:
        """
        returns (packet_count, transfer_count, timeout)
        """
        packet_count = c_int()
        transfer_count = c_int()
        timeout_io = c_uint(timeout)
        lib.asphodel_get_device_info_streaming_counts(
            self._device_info, response_time, buffer_time, packet_count,
            transfer_count, timeout_io)
        return (packet_count.value, transfer_count.value, timeout_io.value)

    def write_setting(self, setting_name: str, json: str,
                      nvm: bytearray) -> None:
        setting_name_bytes = setting_name.encode("utf-8")
        json_bytes = json.encode("utf-8")
        buffer = (c_uint8 * len(nvm)).from_buffer(nvm)
        lib.asphodel_write_setting(
            self._device_info, setting_name_bytes, json_bytes, buffer)

    def write_settings(self, json: str, nvm: bytearray) -> None:
        json_bytes = json.encode("utf-8")
        buffer = (c_uint8 * len(nvm)).from_buffer(nvm)
        lib.asphodel_write_settings(
            self._device_info, json_bytes, buffer)
