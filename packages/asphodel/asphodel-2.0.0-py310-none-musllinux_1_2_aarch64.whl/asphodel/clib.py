from collections.abc import Callable
from ctypes import (CFUNCTYPE, POINTER, Structure, Union, c_char, c_char_p,
                    c_double, c_float, c_int, c_int8, c_int16, c_int32,
                    c_size_t, c_uint, c_uint8, c_uint16, c_uint32, c_uint64,
                    c_void_p, cdll)
from ctypes.util import find_library
import os
import sys
from typing import TYPE_CHECKING, Any, cast
import weakref

from .enums import SettingType

if TYPE_CHECKING:
    from .device import Device


class AsphodelError(IOError):
    pass


class StreamInfo(Structure):
    _fields_ = [("_channel_index_list", POINTER(c_uint8)),
                ("_channel_count", c_uint8),
                ("filler_bits", c_uint8),
                ("counter_bits", c_uint8),
                ("rate", c_float),
                ("rate_error", c_float),
                ("warm_up_delay", c_float)]
    _free_func: Callable[["StreamInfo"], None]

    def __del__(self) -> None:
        try:
            self._free_func(self)
        except AttributeError:
            pass

    def __reduce__(self) -> tuple[Any, ...]:
        return (StreamInfo.from_json, (self.to_json(),))

    @property
    def channel_index_list(self) -> list[int]:
        count = self._channel_count
        if count > 0:
            return self._channel_index_list[0:count]
        else:
            return []

    @classmethod
    def from_json(cls, json: str) -> "StreamInfo":
        json_bytes = json.encode("utf-8")
        stream_ptr = POINTER(StreamInfo)()
        lib.asphodel_get_stream_info_from_json(
            json_bytes, stream_ptr)
        stream = stream_ptr.contents
        stream._free_func = lib.asphodel_free_json_stream
        return stream

    def to_json(self) -> str:
        out = c_char_p()
        lib.asphodel_get_json_from_stream_info(self, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No JSON string returned")
        lib.asphodel_free_string(out)
        return out_bytes.decode("utf-8")

    def __repr__(self) -> str:
        items: list[tuple[str, Any]] = [
            ("channel_index_list", self.channel_index_list),
            ("filler_bits", self.filler_bits),
            ("counter_bits", self.counter_bits),
            ("rate", self.rate),
            ("rate_error", self.rate_error),
            ("warm_up_delay", self.warm_up_delay)
        ]
        contents = ", ".join(("{}={}".format(*i) for i in items))
        return "<AsphodelStreamInfo {" + contents + "}>"


class ChannelInfo(Structure):
    _fields_ = [("_name", c_char_p),
                ("_name_length", c_uint8),
                ("channel_type", c_uint8),
                ("unit_type", c_uint8),
                ("filler_bits", c_uint16),
                ("data_bits", c_uint16),
                ("samples", c_uint8),
                ("bits_per_sample", c_int16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("resolution", c_float),
                ("_coefficients", POINTER(c_float)),
                ("_coefficients_length", c_uint8),
                ("_chunks", POINTER(POINTER(c_uint8))),
                ("_chunk_lengths", POINTER(c_uint8)),
                ("_chunk_count", c_uint8)]
    _free_func: Callable[["ChannelInfo"], None]

    def __del__(self) -> None:
        try:
            self._free_func(self)
        except AttributeError:
            pass

    def __reduce__(self) -> tuple[Any, ...]:
        return (ChannelInfo.from_json, (self.to_json(),))

    @property
    def name(self) -> bytes:
        raw_name = self._name
        if raw_name is None:
            # This is to prevent name being None instead of empty bytes
            return b''
        return raw_name

    @property
    def coefficients(self) -> list[float]:
        count = self._coefficients_length
        if count > 0:
            return self._coefficients[0:count]
        else:
            return []

    @property
    def chunks(self) -> list[bytes]:
        chunk_list: list[bytes] = []
        for i in range(self._chunk_count):
            chunk_length: int = self._chunk_lengths[i]
            if chunk_length >= 0:
                chunk_list.append(bytes(self._chunks[i][0:chunk_length]))
            else:
                chunk_list.append(b"")
        return chunk_list

    @classmethod
    def from_json(cls, json: str) -> "ChannelInfo":
        json_bytes = json.encode("utf-8")
        channel_ptr = POINTER(ChannelInfo)()
        lib.asphodel_get_channel_info_from_json(
            json_bytes, channel_ptr)
        channel = channel_ptr.contents
        channel._free_func = lib.asphodel_free_json_channel
        return channel

    def to_json(self) -> str:
        out = c_char_p()
        lib.asphodel_get_json_from_channel_info(self, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No JSON string returned")
        lib.asphodel_free_string(out)
        return out_bytes.decode("utf-8")

    def __repr__(self) -> str:
        if self.channel_type < len(channel_type_names):
            s = channel_type_names[cast(int, self.channel_type)]
            channel_type_str = "{} ({})".format(self.channel_type, s)
        else:
            channel_type_str = "{}".format(self.channel_type)

        if self.unit_type < len(unit_type_names):
            s = unit_type_names[cast(int, self.unit_type)]
            unit_type_str = "{} ({})".format(self.unit_type, s)
        else:
            unit_type_str = "{}".format(self.unit_type)
        items: list[tuple[str, Any]] = [
            ("name", self.name),
            ("channel_type", channel_type_str),
            ("unit_type", unit_type_str),
            ("filler_bits", self.filler_bits),
            ("data_bits", self.data_bits),
            ("samples", self.samples),
            ("bits_per_sample", self.bits_per_sample),
            ("minimum", self.minimum),
            ("maximum", self.maximum),
            ("resolution", self.resolution),
            ("coefficients", self.coefficients),
            ("chunks", self.chunks),
        ]
        contents = ", ".join(("{}={}".format(*i) for i in items))
        return "<AsphodelChannelInfo {" + contents + "}>"


class ByteSetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("nvm_word_byte", c_uint8)]


class ByteArraySetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("maximum_length", c_uint8),
                ("length_nvm_word", c_uint16),
                ("length_nvm_word_byte", c_uint8)]


class StringSetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("maximum_length", c_uint8)]


class Int32Setting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_int32),
                ("maximum", c_int32)]


class Int32ScaledSetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_int32),
                ("maximum", c_int32),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float)]


class FloatSetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float)]


class FloatArraySetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("minimum", c_float),
                ("maximum", c_float),
                ("unit_type", c_uint8),
                ("scale", c_float),
                ("offset", c_float),
                ("maximum_length", c_uint8),
                ("length_nvm_word", c_uint16),
                ("length_nvm_word_byte", c_uint8)]


class CustomEnumSetting(Structure):
    _fields_ = [("nvm_word", c_uint16),
                ("nvm_word_byte", c_uint8),
                ("custom_enum_index", c_uint8)]


class SettingUnion(Union):
    _fields_ = [("byte_setting", ByteSetting),
                ("byte_array_setting", ByteArraySetting),
                ("string_setting", StringSetting),
                ("int32_setting", Int32Setting),
                ("int32_scaled_setting", Int32ScaledSetting),
                ("float_setting", FloatSetting),
                ("float_array_setting", FloatArraySetting),
                ("custom_enum_setting", CustomEnumSetting)]


class SettingInfo(Structure):
    _fields_ = [("_name", c_char_p),
                ("_name_length", c_uint8),
                ("_default_bytes", POINTER(c_uint8)),
                ("_default_bytes_length", c_uint8),
                ("setting_type", c_uint8),
                ("u", SettingUnion)]
    _free_func: Callable[["SettingInfo"], None]

    def __del__(self) -> None:
        try:
            self._free_func(self)
        except AttributeError:
            pass

    def __reduce__(self) -> tuple[Any, ...]:
        return (SettingInfo.from_json, (self.to_json(),))

    @property
    def name(self) -> bytes:
        raw_name = self._name
        if raw_name is None:
            # This is to prevent name being None instead of empty bytes
            return b''
        return raw_name

    @property
    def default_bytes(self) -> list[float]:
        count = self._default_bytes_length
        if count > 0:
            return self._default_bytes[0:count]
        else:
            return []

    @classmethod
    def from_json(cls, json: str) -> "SettingInfo":
        json_bytes = json.encode("utf-8")
        setting_ptr = POINTER(SettingInfo)()
        lib.asphodel_get_setting_info_from_json(
            json_bytes, setting_ptr)
        setting = setting_ptr.contents
        setting._free_func = lib.asphodel_free_json_setting
        return setting

    def to_json(self) -> str:
        out = c_char_p()
        lib.asphodel_get_json_from_setting_info(self, out)
        out_bytes = out.value
        if not out_bytes:
            raise AsphodelError("No JSON string returned")
        lib.asphodel_free_string(out)
        return out_bytes.decode("utf-8")

    def __repr__(self) -> str:
        return self.to_json().strip('"')

    def get_nvm_used_bytes(self) -> set[int]:
        if (self.setting_type == SettingType.BYTE or
                self.setting_type == SettingType.BOOLEAN or
                self.setting_type == SettingType.UNIT_TYPE or
                self.setting_type == SettingType.CHANNEL_TYPE):
            return set((self.u.byte_setting.nvm_word * 4 +
                        self.u.byte_setting.nvm_word_byte,))
        elif self.setting_type == SettingType.BYTE_ARRAY:
            locations = set(range(
                self.u.byte_array_setting.nvm_word * 4,
                self.u.byte_array_setting.nvm_word * 4 +
                self.u.byte_array_setting.maximum_length))
            length_byte_offset = (
                self.u.byte_array_setting.length_nvm_word * 4 +
                self.u.byte_array_setting.length_nvm_word_byte)
            locations.add(length_byte_offset)
            return locations
        elif self.setting_type == SettingType.STRING:
            return set(range(
                self.u.string_setting.nvm_word * 4,
                self.u.string_setting.nvm_word * 4 +
                self.u.string_setting.maximum_length))
        elif self.setting_type == SettingType.INT32:
            return set(range(self.u.int32_setting.nvm_word * 4,
                             self.u.int32_setting.nvm_word * 4 + 4))
        elif self.setting_type == SettingType.INT32_SCALED:
            return set(range(self.u.int32_scaled_setting.nvm_word * 4,
                             self.u.int32_scaled_setting.nvm_word * 4 + 4))
        elif self.setting_type == SettingType.FLOAT:
            return set(range(self.u.float_setting.nvm_word * 4,
                             self.u.float_setting.nvm_word * 4 + 4))
        elif self.setting_type == SettingType.FLOAT_ARRAY:
            locations = set(range(
                self.u.float_array_setting.nvm_word * 4,
                self.u.float_array_setting.nvm_word * 4 +
                self.u.float_array_setting.maximum_length))
            length_byte_offset = (
                self.u.float_array_setting.length_nvm_word * 4 +
                self.u.float_array_setting.length_nvm_word_byte)
            locations.add(length_byte_offset)
            return locations
        elif self.setting_type == SettingType.CUSTOM_ENUM:
            return set((self.u.custom_enum_setting.nvm_word * 4 +
                        self.u.custom_enum_setting.nvm_word_byte,))
        else:
            raise AsphodelError("Unknown setting type")


# void (*)(int status, uint8_t *params, size_t param_length,
#          void * closure)
AsphodelTransferCallback = CFUNCTYPE(
    None, c_int, POINTER(c_uint8), c_size_t, c_void_p)

# void (*)(int status, uint8_t *stream_data, size_t packet_size,
#          size_t packet_count, void * closure)
AsphodelStreamingCallback = CFUNCTYPE(
    None, c_int, POINTER(c_uint8), c_size_t, c_size_t, c_void_p)

# void (*)(int status, int connected, void * closure)
AsphodelConnectCallback = CFUNCTYPE(None, c_int, c_int, c_void_p)

# void (*)(int status, void * closure)
AsphodelCommandCallback = CFUNCTYPE(None, c_int, c_void_p)

# void (*)(uint64_t counter, double *data, size_t samples,
#          size_t subchannels, void * closure)
AsphodelDecodeCallback = CFUNCTYPE(
    None, c_uint64, POINTER(c_double), c_size_t, c_size_t, c_void_p)

# uint64_t (*)(uint8_t *buffer, uint64_t last)
AsphodelCounterDecoderFunc = CFUNCTYPE(
    c_uint64, POINTER(c_uint8), c_uint64)

# void (*)(uint64_t current, uint64_t last, void * closure)
AsphodelLostPacketCallback = CFUNCTYPE(None, c_uint64, c_uint64, c_void_p)

# uint8_t (*)(uint8_t *buffer)
AsphodelIDDecoderFunc = CFUNCTYPE(c_uint8, POINTER(c_uint8))

# void (*)(uint8_t id, void * closure)
AsphodelUnknownIDCallback = CFUNCTYPE(None, c_uint8, c_void_p)

# void (*)(uint32_t finished, uint32_t total, const char *section_name,
#          void * closure)
AsphodelDeviceInfoProgressCallback = CFUNCTYPE(
    None, c_uint32, c_uint32, c_char_p, c_void_p)


class AsphodelDevice(Structure):
    pass  # need a forward declaration for the recursive structure


AsphodelDevice._fields_ = [
    # int
    ("protocol_type", c_int),
    # const char *
    ("location_string", c_char_p),
    # int (*)(struct AsphodelDevice_t * device)
    ("open_device", CFUNCTYPE(c_int, POINTER(AsphodelDevice))),
    # void (*)(struct AsphodelDevice_t *device)
    ("close_device", CFUNCTYPE(None, POINTER(AsphodelDevice))),
    # void (*)(struct AsphodelDevice_t *device)
    ("free_device", CFUNCTYPE(None, POINTER(AsphodelDevice))),
    # int (*)(struct AsphodelDevice_t *device, char *buffer,
    #         size_t buffer_size)
    ("get_serial_number", CFUNCTYPE(c_int, POINTER(AsphodelDevice),
                                    POINTER(c_char), c_size_t)),
    # int (*)(struct AsphodelDevice_t *device, uint8_t command,
    #         uint8_t *params, size_t param_length,
    #         AsphodelTransferCallback_t callback, void * closure)
    ("do_transfer", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), c_uint8, POINTER(c_uint8),
        c_size_t, AsphodelTransferCallback, c_void_p)),
    # int (*)(struct AsphodelDevice_t *device, uint8_t command,
    #         uint8_t *params, size_t param_length,
    #         AsphodelTransferCallback_t callback, void * closure)
    ("do_transfer_reset", CFUNCTYPE(c_int, POINTER(AsphodelDevice),
                                    c_uint8, POINTER(c_uint8), c_size_t,
                                    AsphodelTransferCallback, c_void_p)),
    # int (*)(struct AsphodelDevice_t *device, int packet_count,
    #         int transfer_count, unsigned int timeout,
    #         AsphodelStreamingCallback_t callback, void * closure)
    ("start_streaming_packets", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), c_int, c_int, c_uint,
        AsphodelStreamingCallback, c_void_p)),
    # void (*)(struct AsphodelDevice_t *device)
    ("stop_streaming_packets", CFUNCTYPE(
        None, POINTER(AsphodelDevice))),
    # int (*)(struct AsphodelDevice_t *device, uint8_t *buffer,
    #         int *count, unsigned int timeout)
    ("get_stream_packets_blocking", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), POINTER(c_uint8),
        POINTER(c_int), c_uint)),
    # size_t (*)(struct AsphodelDevice_t * device)
    ("get_max_incoming_param_length", CFUNCTYPE(
        c_size_t, POINTER(AsphodelDevice))),
    # size_t (*)(struct AsphodelDevice_t * device)
    ("get_max_outgoing_param_length", CFUNCTYPE(
        c_size_t, POINTER(AsphodelDevice))),
    # size_t (*)(struct AsphodelDevice_t * device)
    ("get_stream_packet_length", CFUNCTYPE(
        c_size_t, POINTER(AsphodelDevice))),
    # int (*)(struct AsphodelDevice_t * device, int milliseconds,
    #         int *completed)
    ("poll_device", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), c_int, POINTER(c_int))),
    # int (*)(struct AsphodelDevice_t * device,
    #         AsphodelConnectCallback_t callback, void * closure)
    ("set_connect_callback", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), AsphodelConnectCallback,
        c_void_p)),
    # int (*)(struct AsphodelDevice_t * device, unsigned int timeout)
    ("wait_for_connect", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), c_uint)),
    # int (*)(struct AsphodelDevice_t * device,
    #         struct AsphodelDevice_t **remote_device)
    ("get_remote_device", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice),
        POINTER(POINTER(AsphodelDevice)))),
    # int (*)(struct AsphodelDevice_t * device,
    #         struct AsphodelDevice_t **reconnected_device)
    ("reconnect_device", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice),
        POINTER(POINTER(AsphodelDevice)))),
    # void (*)(struct AsphodelDevice_t * device, int status,
    #          void *closure)
    ("error_callback", CFUNCTYPE(
        None, POINTER(AsphodelDevice), c_int, c_void_p)),
    # void *
    ("error_closure", c_void_p),
    # void *
    # int (*)(struct AsphodelDevice_t * device,
    #         struct AsphodelDevice_t **reconnected_device)
    ("reconnect_device_bootloader", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice),
        POINTER(POINTER(AsphodelDevice)))),
    # int (*)(struct AsphodelDevice_t * device,
    #         struct AsphodelDevice_t **reconnected_device)
    ("reconnect_device_application", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice),
        POINTER(POINTER(AsphodelDevice)))),
    ("implementation_info", c_void_p),
    # const char *
    ("transport_type", c_char_p),
    ("get_remote_lengths", CFUNCTYPE(
        c_int, POINTER(AsphodelDevice), POINTER(c_size_t),
        POINTER(c_size_t), POINTER(c_size_t))),
    # void * reserved[8]
    ("_reserved", c_void_p * 8)]


class ChannelCalibration(Structure):
    _fields_ = [("base_setting_index", c_int),
                ("resolution_setting_index", c_int),
                ("scale", c_float),
                ("offset", c_float),
                ("minimum", c_float),
                ("maximum", c_float)]


class SupplyInfo(Structure):
    _fields_ = [("name", c_char_p),
                ("name_length", c_uint8),
                ("unit_type", c_uint8),
                ("is_battery", c_uint8),
                ("nominal", c_int32),
                ("scale", c_float),
                ("offset", c_float)]


class CtrlVarInfo(Structure):
    _fields_ = [("name", c_char_p),
                ("name_length", c_uint8),
                ("unit_type", c_uint8),
                ("minimum", c_int32),
                ("maximum", c_int32),
                ("scale", c_float),
                ("offset", c_float)]


class ExtraScanResult(Structure):
    _fields_ = [("serial_number", c_uint32),
                ("asphodel_type", c_uint8),
                ("device_mode", c_uint8),
                ("_reserved", c_uint16)]


class GPIOPortInfo(Structure):
    _fields_ = [("name", c_char_p),
                ("name_length", c_uint8),
                ("input_pins", c_uint32),
                ("output_pins", c_uint32),
                ("floating_pins", c_uint32),
                ("loaded_pins", c_uint32),
                ("overridden_pins", c_uint32)]


class StreamAndChannels(Structure):
    _fields_ = [("stream_id", c_uint8),
                ("stream_info", POINTER(StreamInfo)),
                ("channel_info", POINTER(POINTER(ChannelInfo)))]


class AsphodelChannelDecoder(Structure):
    pass  # need a forward declaration for the recursive structure


AsphodelChannelDecoder._fields_ = [
    ("decode", CFUNCTYPE(
        None, POINTER(AsphodelChannelDecoder), c_uint64, POINTER(c_uint8))),
    ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelChannelDecoder))),
    ("reset", CFUNCTYPE(None, POINTER(AsphodelChannelDecoder))),
    ("set_conversion_factor", CFUNCTYPE(
        None, POINTER(AsphodelChannelDecoder), c_double, c_double)),
    ("channel_bit_offset", c_uint16),
    ("samples", c_size_t),
    ("channel_name", c_char_p),
    ("subchannels", c_size_t),
    ("subchannel_names", POINTER(c_char_p)),
    ("callback", AsphodelDecodeCallback),
    ("closure", c_void_p)]


class AsphodelStreamDecoder(Structure):
    pass  # need a forward declaration for the recursive structure


AsphodelStreamDecoder._fields_ = [
    ("decode", CFUNCTYPE(
        None, POINTER(AsphodelStreamDecoder), POINTER(c_uint8))),
    ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelStreamDecoder))),
    ("reset", CFUNCTYPE(None, POINTER(AsphodelStreamDecoder))),
    ("last_count", c_uint64),
    ("counter_byte_offset", c_size_t),
    ("counter_decoder", AsphodelCounterDecoderFunc),
    ("channels", c_size_t),
    ("decoders", POINTER(POINTER(AsphodelChannelDecoder))),
    ("lost_packet_callback", AsphodelLostPacketCallback),
    ("lost_packet_closure", c_void_p),
    ("used_bits", c_uint16)]


class AsphodelDeviceDecoder(Structure):
    pass  # need a forward declaration for the recursive structure


AsphodelDeviceDecoder._fields_ = [
    ("decode", CFUNCTYPE(
        None, POINTER(AsphodelDeviceDecoder), POINTER(c_uint8))),
    ("free_decoder", CFUNCTYPE(None, POINTER(AsphodelDeviceDecoder))),
    ("reset", CFUNCTYPE(None, POINTER(AsphodelDeviceDecoder))),
    ("id_byte_offset", c_size_t),
    ("id_decoder", AsphodelIDDecoderFunc),
    ("streams", c_size_t),
    ("stream_ids", POINTER(c_uint8)),
    ("decoders", POINTER(POINTER(AsphodelStreamDecoder))),
    ("unknown_id_callback", AsphodelUnknownIDCallback),
    ("unknown_id_closure", c_void_p),
    ("used_bits", c_uint16)]


class AsphodelTCPAdvInfo(Structure):
    _fields_ = [("tcp_version", c_uint8),
                ("connected", c_uint8),
                ("max_incoming_param_length", c_size_t),
                ("max_outgoing_param_length", c_size_t),
                ("stream_packet_length", c_size_t),
                ("protocol_type", c_int),
                ("serial_number", c_char_p),
                ("board_rev", c_uint8),
                ("board_type", c_char_p),
                ("build_info", c_char_p),
                ("build_date", c_char_p),
                ("user_tag1", c_char_p),
                ("user_tag2", c_char_p),
                ("remote_max_incoming_param_length", c_size_t),
                ("remote_max_outgoing_param_length", c_size_t),
                ("remote_stream_packet_length", c_size_t)]


class AsphodelUnitFormatter(Structure):
    pass  # need a forward declaration for the recursive structure


AsphodelUnitFormatter._fields_ = [
    ("format_bare", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                              POINTER(c_char), c_size_t, c_double)),
    ("format_ascii", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                               POINTER(c_char), c_size_t, c_double)),
    ("format_utf8", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                              POINTER(c_char), c_size_t, c_double)),
    ("format_html", CFUNCTYPE(c_int, POINTER(AsphodelUnitFormatter),
                              POINTER(c_char), c_size_t, c_double)),
    ("free", CFUNCTYPE(None, POINTER(AsphodelUnitFormatter))),
    ("unit_ascii", c_char_p),
    ("unit_utf8", c_char_p),
    ("unit_html", c_char_p),
    ("conversion_scale", c_double),
    ("conversion_offset", c_double)]


class StreamRateInfo(Structure):
    _fields_ = [("available", c_int),
                ("channel_index", c_int),
                ("invert", c_int),
                ("scale", c_float),
                ("offset", c_float)]


class SupplyResult(Structure):
    _fields_ = [("error_code", c_int),
                ("measurement", c_int32),
                ("result", c_uint8)]


class AsphodelDeviceInfo(Structure):
    pass    # need a forward declaration for the recursive structure


AsphodelDeviceInfo._fields_ = [
    # void (*)(struct AsphodelDeviceInfo_t *device_info)
    ("free_device_info", CFUNCTYPE(None, POINTER(AsphodelDeviceInfo))),
    # const char *
    ("serial_number", c_char_p),
    # const char *
    ("location_string", c_char_p),
    # size_t
    ("max_incoming_param_length", c_size_t),
    # size_t
    ("max_outgoing_param_length", c_size_t),
    # size_t
    ("stream_packet_length", c_size_t),
    # size_t
    ("remote_max_incoming_param_length", c_size_t),
    # size_t
    ("remote_max_outgoing_param_length", c_size_t),
    # size_t
    ("remote_stream_packet_length", c_size_t),
    # uint8_t
    ("supports_bootloader", c_uint8),
    # uint8_t
    ("supports_radio", c_uint8),
    # uint8_t
    ("supports_remote", c_uint8),
    # uint8_t
    ("supports_rf_power", c_uint8),
    # const char *
    ("build_date", c_char_p),
    # const char *
    ("build_info", c_char_p),
    # const char *
    ("nvm_hash", c_char_p),
    # uint8_t *
    ("nvm_modified", POINTER(c_uint8)),
    # const char *
    ("setting_hash", c_char_p),
    # const char *
    ("board_info_name", c_char_p),
    # uint8_t
    ("board_info_rev", c_uint8),
    # const char *
    ("protocol_version", c_char_p),
    # const char *
    ("chip_family", c_char_p),
    # const char *
    ("chip_id", c_char_p),
    # const char *
    ("chip_model", c_char_p),
    # const char *
    ("bootloader_info", c_char_p),
    # uint8_t
    ("rgb_count_known", c_uint8),
    # uint8_t
    ("led_count_known", c_uint8),
    # size_t
    ("rgb_count", c_size_t),
    # size_t
    ("led_count", c_size_t),
    # uint8_t (*)[3]
    ("rgb_settings", POINTER(c_uint8 * 3)),
    # uint8_t *
    ("led_settings", POINTER(c_uint8)),
    # const char *
    ("commit_id", c_char_p),
    # const char *
    ("repo_branch", c_char_p),
    # const char *
    ("repo_name", c_char_p),
    # uint8_t
    ("stream_count_known", c_uint8),
    # uint8_t
    ("stream_filler_bits", c_uint8),
    # uint8_t
    ("stream_id_bits", c_uint8),
    # size_t
    ("stream_count", c_size_t),
    # AsphodelStreamInfo_t *
    ("streams", POINTER(StreamInfo)),
    # AsphodelStreamRateInfo_t *
    ("stream_rates", POINTER(StreamRateInfo)),
    # uint8_t
    ("channel_count_known", c_uint8),
    # size_t
    ("channel_count", c_size_t),
    # AsphodelChannelInfo_t *
    ("channels", POINTER(ChannelInfo)),
    # AsphodelChannelCalibration_t **
    ("channel_calibrations", POINTER(POINTER(ChannelCalibration))),
    # uint8_t
    ("supply_count_known", c_uint8),
    # size_t
    ("supply_count", c_size_t),
    # AsphodelSupplyInfo_t *
    ("supplies", POINTER(SupplyInfo)),
    # AsphodelSupplyResult_t *
    ("supply_results", POINTER(SupplyResult)),
    # uint8_t
    ("ctrl_var_count_known", c_uint8),
    # size_t
    ("ctrl_var_count", c_size_t),
    # AsphodelCtrlVarInfo_t *
    ("ctrl_vars", POINTER(CtrlVarInfo)),
    # int32_t *
    ("ctrl_var_states", POINTER(c_int32)),
    # uint8_t
    ("setting_count_known", c_uint8),
    # size_t
    ("setting_count", c_size_t),
    # AsphodelSettingInfo_t *
    ("settings", POINTER(SettingInfo)),
    # size_t
    ("custom_enum_count", c_size_t),
    # uint8_t *
    ("custom_enum_lengths", POINTER(c_uint8)),
    # const char ***
    ("custom_enum_values", POINTER(POINTER(c_char_p))),
    # uint8_t
    ("setting_category_count_known", c_uint8),
    # size_t
    ("setting_category_count", c_size_t),
    # const char **
    ("setting_category_names", POINTER(c_char_p)),
    # uint8_t *
    ("setting_category_settings_lengths", POINTER(c_uint8)),
    # uint8_t **
    ("setting_category_settings", POINTER(POINTER(c_uint8))),
    # uint8_t *
    ("supports_device_mode", POINTER(c_uint8)),
    # uint8_t
    ("device_mode", c_uint8),
    # uint8_t
    ("rf_power_ctrl_var_count_known", c_uint8),
    # size_t
    ("rf_power_ctrl_var_count", c_size_t),
    # uint8_t *
    ("rf_power_ctrl_vars", POINTER(c_uint8)),
    # uint8_t
    ("rf_power_enabled", c_uint8),
    # uint8_t
    ("radio_ctrl_var_count_known", c_uint8),
    # size_t
    ("radio_ctrl_var_count", c_size_t),
    # uint8_t *
    ("radio_ctrl_vars", POINTER(c_uint8)),
    # uint32_t *
    ("radio_default_serial", POINTER(c_uint32)),
    # uint8_t *
    ("radio_scan_power_supported", POINTER(c_uint8)),
    # size_t
    ("nvm_size", c_size_t),
    # const uint8_t *
    ("nvm", POINTER(c_uint8)),
    # size_t[6]
    ("tag_locations", c_size_t * 6),
    # const char *
    ("user_tag_1", c_char_p),
    # const char *
    ("user_tag_2", c_char_p)]


class AsphodelDeviceInfoCache(Structure):
    pass  # opaque structure type


class AsphodelVirtualDeviceCallbacks(Structure):  # TODO: rename?
    pass  # TODO: fill this in


# list of names of functions that couldn't be loaded
missing_funcs: list[str] = []

if sys.platform == "win32":
    library_dir = os.path.join(os.path.dirname(__file__), "lib")
    library_path = os.path.join(library_dir, "asphodel.dll")
    os.environ['PATH'] = (
        library_dir + os.pathsep + os.path.dirname(sys.executable) +
        os.pathsep + os.environ['PATH']
    )
elif sys.platform == "darwin":
    library_path = os.path.join(os.path.dirname(__file__),
                                "lib/libasphodel.dylib")
else:
    library_path = os.path.join(os.path.dirname(__file__),
                                "lib/libasphodel.so")

if not os.path.isfile(library_path):
    library_path = find_library('asphodel')
    if library_path is None:
        raise AsphodelError(0, "Could not find asphodel library!")

try:
    lib = cdll.LoadLibrary(library_path)
except Exception as e:
    raise AsphodelError(0, "Could not load asphodel library!") from e


def asphodel_error_check(result: int, func: Any = None,
                         arguments: tuple[Any, ...] | None = None) -> None:
    if result != 0:
        error_name = lib.asphodel_error_name(result)
        raise AsphodelError(result, error_name)


def asphodel_string_decode_check(result: bytes, func: Any,
                                 arguments: tuple[Any, ...] | None) -> str:
    return result.decode("utf-8")


ErrCheck = Callable[[Any, Any, tuple[Any, ...]], Any]


def load_library_function(
        name: str, restype: Any, argtypes: list[Any],
        errcheck: ErrCheck | None = None,
        ignore_missing: bool = True) -> None:
    try:
        func = getattr(lib, name)
    except AttributeError:
        if ignore_missing:
            missing_funcs.append(name)

            def missing_func(*args, **kwargs):  # type: ignore
                msg = "Library missing {}()".format(name)
                raise AsphodelError(0, msg)
            setattr(lib, name, missing_func)
            return
        else:
            raise
    func.restype = restype
    if errcheck is not None:
        func.errcheck = errcheck
    func.argtypes = argtypes


def load_device_function(base_name: str, argtypes: list[Any]) -> None:
    non_blocking_name = base_name
    blocking_name = base_name + "_blocking"

    blocking_argtypes: list[Any] = [POINTER(AsphodelDevice)]
    blocking_argtypes.extend(argtypes)

    non_blocking_argtypes: list[Any] = list(blocking_argtypes)
    non_blocking_argtypes.append(AsphodelCommandCallback)
    non_blocking_argtypes.append(c_void_p)

    load_library_function(
        non_blocking_name, c_int, non_blocking_argtypes, asphodel_error_check)
    load_library_function(
        blocking_name, c_int, blocking_argtypes, asphodel_error_check)


#
# --- asphodel_api.h ---
#

# const char * asphodel_error_name(int error_code)
load_library_function(
    "asphodel_error_name", c_char_p, [c_int], asphodel_string_decode_check)

# const char * asphodel_unit_type_name(uint8_t unit_type)
load_library_function(
    "asphodel_unit_type_name", c_char_p, [c_uint8],
    asphodel_string_decode_check)

# uint8_t asphodel_get_unit_type_count(void)
load_library_function("asphodel_get_unit_type_count", c_uint8, [])

# const char * asphodel_channel_type_name(uint8_t channel_type)
load_library_function(
    "asphodel_channel_type_name", c_char_p, [c_uint8],
    asphodel_string_decode_check)

# uint8_t asphodel_get_channel_type_count(void)
load_library_function(
    "asphodel_get_channel_type_count", c_uint8, [])

# const char * asphodel_setting_type_name(uint8_t setting_type)
load_library_function(
    "asphodel_setting_type_name", c_char_p, [c_uint8],
    asphodel_string_decode_check)

# uint8_t asphodel_get_setting_type_count(void)
load_library_function("asphodel_get_setting_type_count", c_uint8, [])


#
# --- asphodel_bootloader.h ---
#

# int asphodel_bootloader_start_program(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_bootloader_start_program", [])

# int asphodel_get_bootloader_page_info(AsphodelDevice_t *device,
#         uint32_t *page_info, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_bootloader_page_info",
                     [POINTER(c_uint32), POINTER(c_uint8)])

# int asphodel_get_bootloader_block_sizes(AsphodelDevice_t *device,
#         uint16_t *block_sizes, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_bootloader_block_sizes",
                     [POINTER(c_uint16), POINTER(c_uint8)])

# int asphodel_start_bootloader_page(AsphodelDevice_t *device,
#         uint32_t page_number, uint8_t *nonce, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_start_bootloader_page",
                     [c_uint32, POINTER(c_uint8), c_size_t])

# int asphodel_write_bootloader_code_block(AsphodelDevice_t *device,
#         uint8_t *data, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_write_bootloader_code_block",
                     [POINTER(c_uint8), c_size_t])

# int asphodel_write_bootloader_page(AsphodelDevice_t *device,
#         uint8_t *data, size_t data_length, uint16_t *block_sizes,
#         uint8_t block_sizes_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_write_bootloader_page",
                     [POINTER(c_uint8), c_size_t, POINTER(c_uint16), c_uint8])

# int asphodel_finish_bootloader_page(AsphodelDevice_t *device,
#         uint8_t *mac_tag, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_finish_bootloader_page",
                     [POINTER(c_uint8), c_size_t])

# int asphodel_verify_bootloader_page(AsphodelDevice_t *device,
#         uint8_t *mac_tag, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_verify_bootloader_page",
                     [POINTER(c_uint8), c_size_t])


#
# --- asphodel_channel_specific.h ---
#

# int asphodel_get_strain_bridge_count(
#         const AsphodelChannelInfo_t *channel_info, int *bridge_count)
load_library_function(
    "asphodel_get_strain_bridge_count", c_int,
    [POINTER(ChannelInfo), POINTER(c_int)],
    asphodel_error_check)

# int asphodel_get_strain_bridge_subchannel(
#         const AsphodelChannelInfo_t *channel_info, int bridge_index,
#         size_t *subchannel_index)
load_library_function(
    "asphodel_get_strain_bridge_subchannel", c_int,
    [POINTER(ChannelInfo), c_int, POINTER(c_size_t)],
    asphodel_error_check)

# int asphodel_get_strain_bridge_values(
#         const AsphodelChannelInfo_t *channel_info, int bridge_index,
#         float *values)
load_library_function(
    "asphodel_get_strain_bridge_values", c_int,
    [POINTER(ChannelInfo), c_int, c_float * 5],
    asphodel_error_check)

# int asphodel_set_strain_outputs(AsphodelDevice_t *device,
#         int channel_index, int bridge_index, int positive_side,
#         int negative_side, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_set_strain_outputs",
                     [c_int, c_int, c_int, c_int])

# int asphodel_check_strain_resistances(
#         const AsphodelChannelInfo_t *channel_info, int bridge_index,
#         double baseline, double positive_high, double negative_high,
#         double *positive_resistance, double *negative_resistance,
#         int *passed)
load_library_function(
    "asphodel_check_strain_resistances", c_int,
    [POINTER(ChannelInfo), c_int, c_double, c_double, c_double,
     POINTER(c_double), POINTER(c_double), POINTER(c_int)],
    asphodel_error_check)

# int asphodel_get_accel_self_test_limits(
#         const AsphodelChannelInfo_t *channel_info, float *limits)
load_library_function(
    "asphodel_get_accel_self_test_limits", c_int,
    [POINTER(ChannelInfo), c_float * 6],
    asphodel_error_check)

# int asphodel_enable_accel_self_test(AsphodelDevice_t *device,
#         int channel_index, int enable,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_enable_accel_self_test", [c_int, c_int])

# int asphodel_check_accel_self_test(
#         const AsphodelChannelInfo_t *channel_info, double *disabled,
#         double *enabled, int *passed)
load_library_function(
    "asphodel_check_accel_self_test", c_int,
    [POINTER(ChannelInfo), c_double * 3, c_double * 3,
     POINTER(c_int)],
    asphodel_error_check)


#
# --- asphodel_ctrl_var.h ---
#

# int asphodel_get_ctrl_var_count(AsphodelDevice_t *device,
#         int *count, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_ctrl_var_count", [POINTER(c_int)])

# int asphodel_get_ctrl_var_name(AsphodelDevice_t *device,
#         int index, char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_ctrl_var_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_ctrl_var_info(AsphodelDevice_t *device,
#         int index, AsphodelCtrlVarInfo_t *ctrl_var_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_ctrl_var_info",
                     [c_int, POINTER(CtrlVarInfo)])

# int asphodel_get_ctrl_var(AsphodelDevice_t *device, int index,
#         int32_t *value, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_ctrl_var", [c_int, POINTER(c_int32)])

# int asphodel_set_ctrl_var(AsphodelDevice_t *device, int index,
#         int32_t value, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_set_ctrl_var", [c_int, c_int32])


#
# --- asphodel_decode.h ---
#

# int asphodel_create_channel_decoder(const AsphodelChannelInfo_t *ch_info,
#         uint16_t bit_offset, AsphodelChannelDecoder_t **decoder)
load_library_function(
    "asphodel_create_channel_decoder", c_int,
    [POINTER(ChannelInfo), c_uint16,
     POINTER(POINTER(AsphodelChannelDecoder))],
    asphodel_error_check)

# int asphodel_create_channel_decoder_checked(
#         const AsphodelChannelInfo_t *channel_info,
#         uint16_t channel_bit_offset, size_t stream_packet_length,
#         AsphodelChannelDecoder_t **decoder)
load_library_function(
    "asphodel_create_channel_decoder_checked", c_int,
    [POINTER(ChannelInfo), c_uint16, c_size_t,
     POINTER(POINTER(AsphodelChannelDecoder))],
    asphodel_error_check)

# int asphodel_create_stream_decoder(const AsphodelStreamAndChannels_t *info,
#         uint16_t stream_bit_offset, AsphodelStreamDecoder_t **decoder)
load_library_function(
    "asphodel_create_stream_decoder", c_int,
    [POINTER(StreamAndChannels), c_uint16,
     POINTER(POINTER(AsphodelStreamDecoder))],
    asphodel_error_check)

# int asphodel_create_stream_decoder_checked(
#         const AsphodelStreamAndChannels_t *info,
#         uint16_t stream_bit_offset, size_t stream_packet_length,
#         AsphodelStreamDecoder_t **decoder)
load_library_function(
    "asphodel_create_stream_decoder_checked", c_int,
    [POINTER(StreamAndChannels), c_uint16, c_size_t,
     POINTER(POINTER(AsphodelStreamDecoder))],
    asphodel_error_check)

# int asphodel_create_device_decoder(
#         const AsphodelStreamAndChannels_t *info_array,
#         uint8_t info_array_size, uint8_t filler_bits,
#         uint8_t id_bits, AsphodelDeviceDecoder_t **decoder)
load_library_function(
    "asphodel_create_device_decoder", c_int,
    [POINTER(StreamAndChannels), c_uint8, c_uint8, c_uint8,
     POINTER(POINTER(AsphodelDeviceDecoder))],
    asphodel_error_check)

# int asphodel_create_device_decoder_checked(
#         const AsphodelStreamAndChannels_t *info_array,
#         uint8_t info_array_size, uint8_t filler_bits, uint8_t id_bits,
#         size_t stream_packet_length, AsphodelDeviceDecoder_t **decoder)
load_library_function(
    "asphodel_create_device_decoder_checked", c_int,
    [POINTER(StreamAndChannels), c_uint8, c_uint8, c_uint8, c_size_t,
     POINTER(POINTER(AsphodelDeviceDecoder))],
    asphodel_error_check)

# int asphodel_create_device_info_decoder(
#         const AsphodelDeviceInfo_t *device_info,
#         const uint8_t *active_streams, uint8_t active_streams_length,
#         AsphodelDeviceDecoder_t **decoder)
load_library_function(
    "asphodel_create_device_info_decoder", c_int,
    [POINTER(AsphodelDeviceInfo), POINTER(c_uint8), c_uint8,
     POINTER(POINTER(AsphodelDeviceDecoder))],
    asphodel_error_check)

# int asphodel_get_streaming_counts(
#         const AsphodelStreamAndChannels_t *info_array,
#         uint8_t info_array_size, double response_time,
#         double buffer_time, int *packet_count, int *transfer_count,
#         unsigned int *timeout)
load_library_function(
    "asphodel_get_streaming_counts", c_int,
    [POINTER(StreamAndChannels), c_uint8, c_double, c_double, POINTER(c_int),
     POINTER(c_int), POINTER(c_uint)],
    asphodel_error_check)

# int asphodel_get_device_info_streaming_counts(
#         const AsphodelDeviceInfo_t *device_info, double response_time,
#         double buffer_time, int *packet_count, int *transfer_count,
#         unsigned int *timeout)
load_library_function(
    "asphodel_get_device_info_streaming_counts", c_int,
    [POINTER(AsphodelDeviceInfo), c_double, c_double, POINTER(c_int),
     POINTER(c_int), POINTER(c_uint)],
    asphodel_error_check)


#
# --- asphodel_device.h ---
#

# int asphodel_get_protocol_version(AsphodelDevice_t *device,
#         uint16_t *version, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_protocol_version", [POINTER(c_uint16)])

# int asphodel_get_protocol_version_string(AsphodelDevice_t *device,
#         char *buffer, size_t buffer_size,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_protocol_version_string",
                     [POINTER(c_char), c_size_t])

# int asphodel_get_board_info(AsphodelDevice_t *device, uint8_t *rev,
#         char *buffer, size_t buffer_size,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_board_info",
                     [POINTER(c_uint8), POINTER(c_char), c_size_t])

# int asphodel_get_user_tag_locations(AsphodelDevice_t *device,
#         size_t *locations, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_user_tag_locations", [c_size_t * 6])

# int asphodel_get_build_info(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_build_info", [POINTER(c_char), c_size_t])

# int asphodel_get_build_date(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_build_date", [POINTER(c_char), c_size_t])

# int asphodel_get_commit_id(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_commit_id", [POINTER(c_char), c_size_t])

# int asphodel_get_repo_branch(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_repo_branch", [POINTER(c_char), c_size_t])

# int asphodel_get_repo_name(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_repo_name", [POINTER(c_char), c_size_t])

# int asphodel_get_chip_family(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_chip_family", [POINTER(c_char), c_size_t])

# int asphodel_get_chip_model(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_chip_model", [POINTER(c_char), c_size_t])

# int asphodel_get_chip_id(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_chip_id", [POINTER(c_char), c_size_t])

# int asphodel_get_nvm_size(AsphodelDevice_t *device, size_t *size,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_nvm_size", [POINTER(c_size_t)])

# int asphodel_erase_nvm(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_erase_nvm", [])

# int asphodel_write_nvm_raw(AsphodelDevice_t *device,
#         size_t start_address, uint8_t *data, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_write_nvm_raw",
                     [c_size_t, POINTER(c_uint8), c_size_t])

# int asphodel_write_nvm_section(AsphodelDevice_t *device,
#         size_t start_address, uint8_t *data, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_write_nvm_section",
                     [c_size_t, POINTER(c_uint8), c_size_t])

# int asphodel_read_nvm_raw(AsphodelDevice_t *device,
#         size_t start_address, uint8_t *data, size_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_read_nvm_raw",
                     [c_size_t, POINTER(c_uint8), POINTER(c_size_t)])

# int asphodel_read_nvm_section(AsphodelDevice_t *device,
#         size_t start_address, uint8_t *data, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_read_nvm_section",
                     [c_size_t, POINTER(c_uint8), c_size_t])

# int asphodel_read_user_tag_string(AsphodelDevice_t *device,
#         size_t offset, size_t length, char *buffer,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_read_user_tag_string",
                     [c_size_t, c_size_t, POINTER(c_char)])

# int asphodel_write_user_tag_string(AsphodelDevice_t *device,
#         size_t offset, size_t length, char *buffer,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_write_user_tag_string",
                     [c_size_t, c_size_t, c_char_p])

# int asphodel_get_nvm_modified(AsphodelDevice_t *device,
#         uint8_t *modified, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_nvm_modified", [POINTER(c_uint8)])

# int asphodel_get_nvm_hash(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_nvm_hash", [POINTER(c_char), c_size_t])

# int asphodel_get_setting_hash(AsphodelDevice_t *device, char *buffer,
#         size_t buffer_size, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_setting_hash", [POINTER(c_char), c_size_t])

# int asphodel_flush(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_flush", [])

# int asphodel_reset(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_reset", [])

# int asphodel_get_bootloader_info(AsphodelDevice_t *device,
#         char *buffer, size_t buffer_size,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_bootloader_info",
                     [POINTER(c_char), c_size_t])

# int asphodel_bootloader_jump(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_bootloader_jump", [])

# int asphodel_get_reset_flag(AsphodelDevice_t *device, uint8_t *flag,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_reset_flag", [POINTER(c_uint8)])

# int asphodel_clear_reset_flag(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_clear_reset_flag", [])

# int asphodel_get_rgb_count(AsphodelDevice_t *device, int *count,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_rgb_count", [POINTER(c_int)])

# int asphodel_get_rgb_values(AsphodelDevice_t *device, int index,
#         uint8_t *values, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_rgb_values", [c_int, c_uint8 * 3])

# int asphodel_set_rgb_values(AsphodelDevice_t *device, int index,
#         uint8_t *values, int instant,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_set_rgb_values", [c_int, c_uint8 * 3, c_int])

# int asphodel_set_rgb_values_hex(AsphodelDevice_t *device, int index,
#         uint32_t color, int instant,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_set_rgb_values_hex", [c_int, c_uint32, c_int])

# int asphodel_get_led_count(AsphodelDevice_t *device, int *count,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_led_count", [POINTER(c_int)])

# int asphodel_get_led_value(AsphodelDevice_t *device, int index,
#         uint8_t *value, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_led_value", [c_int, POINTER(c_uint8)])

# int asphodel_set_led_value(AsphodelDevice_t *device, int index,
#         uint8_t value, int instant,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_set_led_value", [c_int, c_uint8, c_int])

# int asphodel_set_device_mode(AsphodelDevice_t *device, uint8_t mode,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_set_device_mode", [c_uint8])

# int asphodel_get_device_mode(AsphodelDevice_t *device, uint8_t *mode,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_device_mode", [POINTER(c_uint8)])


#
# --- asphodel_device_info.h ---
#

# int asphodel_get_device_info_file_cache(const char *path,
#         AsphodelDeviceInfoCache_t **cache)
load_library_function(
    "asphodel_get_device_info_file_cache", c_int,
    [c_char_p, POINTER(POINTER(AsphodelDeviceInfoCache))],
    asphodel_error_check)

# int asphodel_get_device_info_static_cache(const char *json,
#         AsphodelDeviceInfoCache_t **cache)
load_library_function(
    "asphodel_get_device_info_static_cache", c_int,
    [c_char_p, POINTER(POINTER(AsphodelDeviceInfoCache))],
    asphodel_error_check)

# int asphodel_get_device_info_dynamic_cache(const char *json,
#         AsphodelDeviceInfoCache_t **cache)
load_library_function(
    "asphodel_get_device_info_dynamic_cache", c_int,
    [c_char_p, POINTER(POINTER(AsphodelDeviceInfoCache))],
    asphodel_error_check)

# int asphodel_get_device_info_dynamic_cache_state(
#         AsphodelDeviceInfoCache_t *cache, const char **json_out)
load_library_function(
    "asphodel_get_device_info_dynamic_cache_state", c_int,
    [POINTER(AsphodelDeviceInfoCache), POINTER(c_char_p)],
    asphodel_error_check)

# void asphodel_free_device_info_cache(
#         AsphodelDeviceInfoCache_t *cache)
load_library_function(
    "asphodel_free_device_info_cache", None,
    [POINTER(AsphodelDeviceInfoCache)])

# int asphodel_get_device_info(AsphodelDevice_t *device,
#         AsphodelDeviceInfoCache_t *cache, uint32_t flags,
#         AsphodelDeviceInfo_t **device_info,
#         AsphodelDeviceInfoProgressCallback_t callback, void *closure)
load_library_function(
    "asphodel_get_device_info", c_int,
    [POINTER(AsphodelDevice),
     POINTER(AsphodelDeviceInfoCache),
     c_uint32,
     POINTER(POINTER(AsphodelDeviceInfo)),
     AsphodelDeviceInfoProgressCallback,
     c_void_p],
    asphodel_error_check)

# int asphodel_get_cached_board_info(AsphodelDeviceInfoCache_t *cache,
#         uint32_t serial_number, uint8_t *found, uint8_t *rev,
#         char *buffer, size_t buffer_size)
load_library_function(
    "asphodel_get_cached_board_info", c_int,
    [POINTER(AsphodelDeviceInfoCache), c_uint32, POINTER(c_uint8),
     POINTER(c_uint8), POINTER(c_char), c_size_t],
    asphodel_error_check)

# int asphodel_get_device_info_summary(
#         const AsphodelDeviceInfo_t *device_info,
#         const char **summary_out)
load_library_function(
    "asphodel_get_device_info_summary", c_int,
    [POINTER(AsphodelDeviceInfo), POINTER(c_char_p)],
    asphodel_error_check)

# uint8_t asphodel_device_info_equal(const AsphodelDeviceInfo_t *a,
#         const AsphodelDeviceInfo_t *b);
load_library_function(
    "asphodel_device_info_equal", c_uint8,
    [POINTER(AsphodelDeviceInfo), POINTER(AsphodelDeviceInfo)])

# uint8_t asphodel_device_info_is_subset(const AsphodelDeviceInfo_t *subset,
#         const AsphodelDeviceInfo_t *superset);
load_library_function(
    "asphodel_device_info_is_subset", c_uint8,
    [POINTER(AsphodelDeviceInfo), POINTER(AsphodelDeviceInfo)])


#
# --- asphodel_device_type.h ---
#

# int asphodel_supports_rf_power_commands(AsphodelDevice_t *device)
load_library_function("asphodel_supports_rf_power_commands",
                      c_int, [POINTER(AsphodelDevice)])

# int asphodel_supports_radio_commands(AsphodelDevice_t *device)
load_library_function("asphodel_supports_radio_commands",
                      c_int, [POINTER(AsphodelDevice)])

# int asphodel_supports_remote_commands(AsphodelDevice_t *device)
load_library_function("asphodel_supports_remote_commands",
                      c_int, [POINTER(AsphodelDevice)])

# int asphodel_supports_bootloader_commands(AsphodelDevice_t *device)
load_library_function("asphodel_supports_bootloader_commands",
                      c_int, [POINTER(AsphodelDevice)])


#
# --- asphodel_json.h ---
#

# int asphodel_get_device_info_from_json(const char *json,
#         AsphodelDeviceInfo_t **device_info_out,
#         const char **excess_out)
load_library_function(
    "asphodel_get_device_info_from_json", c_int,
    [c_char_p,
     POINTER(POINTER(AsphodelDeviceInfo)),
     POINTER(c_char_p)],
    asphodel_error_check)

# int asphodel_get_json_from_device_info(
#         const AsphodelDeviceInfo_t *device_info,
#         const char **json_out)
load_library_function(
    "asphodel_get_json_from_device_info", c_int,
    [POINTER(AsphodelDeviceInfo), POINTER(c_char_p)],
    asphodel_error_check)

# int asphodel_get_stream_info_from_json(const char *json,
#         AsphodelStreamInfo_t **stream_info_out)
load_library_function(
    "asphodel_get_stream_info_from_json", c_int,
    [c_char_p, POINTER(POINTER(StreamInfo))],
    asphodel_error_check)

# void asphodel_free_json_stream(AsphodelStreamInfo_t *stream_info)
load_library_function("asphodel_free_json_stream", None, [POINTER(StreamInfo)])

# int asphodel_get_json_from_stream_info(
#         const AsphodelStreamInfo_t *stream_info, const char **json_out)
load_library_function(
    "asphodel_get_json_from_stream_info", c_int,
    [POINTER(StreamInfo), POINTER(c_char_p)],
    asphodel_error_check)

# int asphodel_get_channel_info_from_json(const char *json,
#         AsphodelChannelInfo_t **channel_info_out)
load_library_function(
    "asphodel_get_channel_info_from_json", c_int,
    [c_char_p, POINTER(POINTER(ChannelInfo))],
    asphodel_error_check)

# void asphodel_free_json_channel(AsphodelChannelInfo_t *channel_info)
load_library_function("asphodel_free_json_channel", None,
                      [POINTER(ChannelInfo)])

# int asphodel_get_json_from_channel_info(
#         const AsphodelChannelInfo_t *channel_info, const char **json_out)
load_library_function(
    "asphodel_get_json_from_channel_info", c_int,
    [POINTER(ChannelInfo), POINTER(c_char_p)],
    asphodel_error_check)

# int asphodel_get_setting_info_from_json(const char *json,
#         AsphodelSettingInfo_t **setting_info_out)
load_library_function(
    "asphodel_get_setting_info_from_json", c_int,
    [c_char_p, POINTER(POINTER(SettingInfo))],
    asphodel_error_check)

# void asphodel_free_json_setting(AsphodelSettingInfo_t *setting_info)
load_library_function("asphodel_free_json_setting", None,
                      [POINTER(SettingInfo)])

# int asphodel_get_json_from_setting_info(
#         const AsphodelSettingInfo_t *setting_info, const char **json_out)
load_library_function(
    "asphodel_get_json_from_setting_info", c_int,
    [POINTER(SettingInfo), POINTER(c_char_p)],
    asphodel_error_check)

# void asphodel_free_string(const char *str)
load_library_function("asphodel_free_string", None, [c_char_p])

# int asphodel_write_setting(
#         AsphodelDeviceInfo_t *device_info, const char *setting_name,
#         const char *json, uint8_t *nvm_buffer)
load_library_function(
    "asphodel_write_setting", c_int,
    [POINTER(AsphodelDeviceInfo), c_char_p, c_char_p, POINTER(c_uint8)],
    asphodel_error_check)

# int asphodel_write_settings(
#         AsphodelDeviceInfo_t *device_info, const char *json,
#         uint8_t *nvm_buffer)
load_library_function(
    "asphodel_write_settings", c_int,
    [POINTER(AsphodelDeviceInfo), c_char_p, POINTER(c_uint8)],
    asphodel_error_check)

#
# --- asphodel_low_level.h ---
#

# int asphodel_get_gpio_port_count(AsphodelDevice_t *device,
#         int *count, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_gpio_port_count", [POINTER(c_int)])

# int asphodel_get_gpio_port_name(AsphodelDevice_t *device, int index,
#         char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_gpio_port_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_gpio_port_info(AsphodelDevice_t *device, int index,
#         AsphodelGPIOPortInfo_t *gpio_port_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_gpio_port_info",
                     [c_int, POINTER(GPIOPortInfo)])

# int asphodel_get_gpio_port_values(AsphodelDevice_t *device,
#         int index, uint32_t *pin_values,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_gpio_port_values",
                     [c_int, POINTER(c_uint32)])

# int asphodel_set_gpio_port_modes(AsphodelDevice_t *device, int index,
#         uint8_t mode, uint32_t pins,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_set_gpio_port_modes",
                     [c_int, c_uint8, c_uint32])

# int asphodel_disable_gpio_overrides(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_disable_gpio_overrides", [])

# int asphodel_get_bus_counts(AsphodelDevice_t *device, int *spi_count,
#         int *i2c_count, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_bus_counts",
                     [POINTER(c_int), POINTER(c_int)])
# int asphodel_set_spi_cs_mode(AsphodelDevice_t *device, int index,
#         uint8_t cs_mode, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_set_spi_cs_mode", [c_int, c_uint8])

# int asphodel_do_spi_transfer(AsphodelDevice_t *device, int index,
#         uint8_t *tx_data, uint8_t *rx_data, uint8_t data_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_spi_transfer",
                     [c_int, POINTER(c_uint8), POINTER(c_uint8), c_uint8])

# int asphodel_do_i2c_write(AsphodelDevice_t *device, int index,
#         uint8_t addr, uint8_t *tx_data, uint8_t write_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_i2c_write",
                     [c_int, c_uint8, POINTER(c_uint8), c_uint8])

# int asphodel_do_i2c_read(AsphodelDevice_t *device, int index,
#         uint8_t addr, uint8_t *rx_data, uint8_t read_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_i2c_read",
                     [c_int, c_uint8, POINTER(c_uint8), c_uint8])

# int asphodel_do_i2c_write_read(AsphodelDevice_t *device, int index,
#         uint8_t addr, uint8_t *tx_data, uint8_t write_length,
#         uint8_t *rx_data, uint8_t read_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_i2c_write_read",
                     [c_int, c_uint8, POINTER(c_uint8), c_uint8,
                      POINTER(c_uint8), c_uint8])

# int asphodel_do_radio_fixed_test(AsphodelDevice_t *device,
#         uint16_t channel, uint16_t duration, uint8_t mode,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_radio_fixed_test",
                     [c_uint16, c_uint16, c_uint8])

# int asphodel_do_radio_sweep_test(AsphodelDevice_t *device,
#         uint16_t start_channel, uint16_t stop_channel,
#         uint16_t hop_interval, uint16_t hop_count, uint8_t mode,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_do_radio_sweep_test",
                     [c_uint16, c_uint16, c_uint16, c_uint16, c_uint8])

# int asphodel_get_info_region_count(AsphodelDevice_t *device,
#         int *count, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_info_region_count", [POINTER(c_int)])

# int asphodel_get_info_region_name(AsphodelDevice_t *device,
#         int index, char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_info_region_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_info_region(AsphodelDevice_t *device, int index,
#         uint8_t *data, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_info_region",
                     [c_int, POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_stack_info(AsphodelDevice_t *device,
#         uint32_t *stack_info, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_stack_info", [c_uint32 * 2])

# int asphodel_echo_raw(AsphodelDevice_t *device, uint8_t *data,
#         size_t data_length, uint8_t *reply, size_t *reply_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_echo_raw",
                     [POINTER(c_uint8), c_size_t, POINTER(c_uint8),
                      POINTER(c_size_t)])

# int asphodel_echo_transaction(AsphodelDevice_t *device,
#         uint8_t *data, size_t data_length, uint8_t *reply,
#         size_t *reply_length, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_echo_transaction",
                     [POINTER(c_uint8), c_size_t, POINTER(c_uint8),
                      POINTER(c_size_t)])

# int asphodel_echo_params(AsphodelDevice_t *device, uint8_t *data,
#         size_t data_length, uint8_t *reply, size_t *reply_length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_echo_params",
                     [POINTER(c_uint8), c_size_t, POINTER(c_uint8),
                      POINTER(c_size_t)])

#
# --- asphodel_radio.h ---
#

# int asphodel_stop_radio(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_stop_radio", [])

# int asphodel_start_radio_scan(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_start_radio_scan", [])

# int asphodel_get_raw_radio_scan_results(AsphodelDevice_t *device,
#         uint32_t *serials, size_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_raw_radio_scan_results",
                     [POINTER(c_uint32), POINTER(c_size_t)])

# int asphodel_get_radio_scan_results(AsphodelDevice_t *device,
#         uint32_t **serials, size_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function(
    "asphodel_get_radio_scan_results",
    [POINTER(POINTER(c_uint32)), POINTER(c_size_t)])

# void asphodel_free_radio_scan_results(uint32_t *serials)
load_library_function(
    "asphodel_free_radio_scan_results", None, [POINTER(c_uint32)])

# int asphodel_get_raw_radio_extra_scan_results(
#         AsphodelDevice_t *device, AsphodelExtraScanResult_t *results,
#         size_t *length, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_raw_radio_extra_scan_results",
                     [POINTER(ExtraScanResult), POINTER(c_size_t)])

# int asphodel_get_radio_extra_scan_results(AsphodelDevice_t *device,
#         AsphodelExtraScanResult_t **results, size_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function(
    "asphodel_get_radio_extra_scan_results",
    [POINTER(POINTER(ExtraScanResult)), POINTER(c_size_t)])

# void asphodel_free_radio_extra_scan_results(
#         AsphodelExtraScanResult_t *results)
load_library_function(
    "asphodel_free_radio_extra_scan_results", None,
    [POINTER(ExtraScanResult)])

# int asphodel_get_radio_scan_power(AsphodelDevice_t *device,
#         const uint32_t *serials, int8_t *powers, size_t length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_radio_scan_power",
                     [POINTER(c_uint32), POINTER(c_int8), c_size_t])

# int asphodel_connect_radio(AsphodelDevice_t *device,
#         uint32_t serial_number, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_connect_radio", [c_uint32])

# int asphodel_get_radio_status(AsphodelDevice_t *device,
#         int *connected, uint32_t *serial_number,
#         uint8_t *protocol_type, int *scanning,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function(
    "asphodel_get_radio_status",
    [POINTER(c_int), POINTER(c_uint32), POINTER(c_uint8), POINTER(c_int)])

# int asphodel_get_radio_ctrl_vars(AsphodelDevice_t *device,
#         uint8_t *ctrl_var_indexes, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_radio_ctrl_vars",
                     [POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_radio_default_serial(AsphodelDevice_t *device,
#         uint32_t *serial_number, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_radio_default_serial", [POINTER(c_uint32)])

# int asphodel_start_radio_scan_boot(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_start_radio_scan_boot", [])

# int asphodel_connect_radio_boot(AsphodelDevice_t *device,
#         uint32_t serial_number, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_connect_radio_boot", [c_uint32])

# int asphodel_stop_remote(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_stop_remote", [])

# int asphodel_restart_remote(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_restart_remote", [])

# int asphodel_get_remote_status(AsphodelDevice_t *device,
#         int *connected, uint32_t *serial_number,
#         uint8_t *protocol_type, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_remote_status",
                     [POINTER(c_int), POINTER(c_uint32), POINTER(c_uint8)])

# int asphodel_restart_remote_app(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_restart_remote_app", [])
# int asphodel_restart_remote_boot(AsphodelDevice_t *device,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_restart_remote_boot", [])


#
# --- asphodel_rf_power.h ---
#

# int asphodel_enable_rf_power(AsphodelDevice_t *device, int enable,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_enable_rf_power", [c_int])

# int asphodel_get_rf_power_status(AsphodelDevice_t *device,
#         int *enabled, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_rf_power_status", [POINTER(c_int)])

# int asphodel_get_rf_power_ctrl_vars(AsphodelDevice_t *device,
#         uint8_t *ctrl_var_indexes, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_rf_power_ctrl_vars",
                     [POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_reset_rf_power_timeout(AsphodelDevice_t *device,
#         uint32_t timeout, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_reset_rf_power_timeout", [c_uint32])


#
# --- asphodel_setting.h ---
#

# int asphodel_get_setting_count(AsphodelDevice_t *device, int *count,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_count", [POINTER(c_int)])

# int asphodel_get_setting_name(AsphodelDevice_t *device, int index,
#         char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_setting_info(AsphodelDevice_t *device, int index,
#         AsphodelSettingInfo_t *setting_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_info",
                     [c_int, POINTER(SettingInfo)])

# int asphodel_get_setting_default(AsphodelDevice_t *device, int index,
#         uint8_t *default_bytes, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_default",
                     [c_int, POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_custom_enum_counts(AsphodelDevice_t *device,
#         uint8_t *counts, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_custom_enum_counts",
                     [POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_custom_enum_value_name(AsphodelDevice_t *device,
#         int index, int value, char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_custom_enum_value_name",
                     [c_int, c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_setting_category_count(AsphodelDevice_t *device,
#         int *count, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_setting_category_count", [POINTER(c_int)])

# int asphodel_get_setting_category_name(AsphodelDevice_t *device,
#         int index, char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_category_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_setting_category_settings(AsphodelDevice_t *device,
#         int index, uint8_t *settings, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_setting_category_settings",
                     [c_int, POINTER(c_uint8), POINTER(c_uint8)])


#
# --- asphodel_stream.h ---
#

# int asphodel_get_stream_count(AsphodelDevice_t *device, int *count,
#         uint8_t *filler_bits, uint8_t *id_bits,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_stream_count",
                     [POINTER(c_int), POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_stream(AsphodelDevice_t *device, int index,
#         AsphodelStreamInfo_t **stream_info,
#         AsphodelCommandCallback_t callback, void * closure)

load_device_function("asphodel_get_stream",
                     [c_int, POINTER(POINTER(StreamInfo))])

# void asphodel_free_stream(AsphodelStreamInfo_t *stream_info)
load_library_function("asphodel_free_stream", None,
                      [POINTER(StreamInfo)])

# int asphodel_get_stream_channels(AsphodelDevice_t *device, int index,
#         uint8_t *channels, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)

load_device_function("asphodel_get_stream_channels",
                     [c_int, POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_get_stream_format(AsphodelDevice_t *device, int index,
#         AsphodelStreamInfo_t *stream_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_stream_format",
                     [c_int, POINTER(StreamInfo)])

# int asphodel_enable_stream(AsphodelDevice_t *device, int index,
#         int enable, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_enable_stream", [c_int, c_int])

# int asphodel_warm_up_stream(AsphodelDevice_t *device, int index,
#         int enable, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_warm_up_stream", [c_int, c_int])

# int asphodel_get_stream_status(AsphodelDevice_t *device, int index,
#         int *enable, int *warm_up,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_stream_status",
                     [c_int, POINTER(c_int), POINTER(c_int)])

# int asphodel_get_stream_rate_info(AsphodelDevice_t *device,
#         int index, int *available, int *channel_index, int *invert,
#         float *scale, float *offset,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_stream_rate_info",
                     [c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int),
                      POINTER(c_float), POINTER(c_float)])

# int asphodel_get_channel_count(AsphodelDevice_t *device, int *count,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel_count", [POINTER(c_int)])

# int asphodel_get_channel(AsphodelDevice_t *device, int index,
#         AsphodelChannelInfo_t **channel_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel",
                     [c_int, POINTER(POINTER(ChannelInfo))])

# void asphodel_free_channel(AsphodelChannelInfo_t *channel_info)
load_library_function("asphodel_free_channel", None,
                      [POINTER(ChannelInfo)])

# int asphodel_get_channel_name(AsphodelDevice_t *device, int index,
#         char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_channel_info(AsphodelDevice_t *device, int index,
#         AsphodelChannelInfo_t *channel_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel_info",
                     [c_int, POINTER(ChannelInfo)])

# int asphodel_get_channel_coefficients(AsphodelDevice_t *device,
#         int index, float *coefficients, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel_coefficients",
                     [c_int, POINTER(c_float), POINTER(c_uint8)])

# int asphodel_get_channel_chunk(AsphodelDevice_t *device,
#         int index, uint8_t chunk_number, uint8_t *chunk,
#         uint8_t *length, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_get_channel_chunk",
                     [c_int, c_uint8, POINTER(c_uint8), POINTER(c_uint8)])

# int asphodel_channel_specific(AsphodelDevice_t *device, int index,
#         uint8_t *data, uint8_t data_length, uint8_t *reply,
#         uint8_t *reply_length, AsphodelCommandCallback_t callback,
#         void * closure)
load_device_function("asphodel_channel_specific",
                     [c_int, POINTER(c_uint8), c_uint8, POINTER(c_uint8),
                      POINTER(c_uint8)])

# int asphodel_get_channel_calibration(AsphodelDevice_t *device,
#         int index, int *available,
#         AsphodelChannelCalibration_t *calibration,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_channel_calibration",
                     [c_int, POINTER(c_int),
                      POINTER(ChannelCalibration)])


#
# --- asphodel_supply.h ---
#

# int asphodel_get_supply_count(AsphodelDevice_t *device, int *count,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_supply_count", [POINTER(c_int)])

# int asphodel_get_supply_name(AsphodelDevice_t *device, int index,
#         char *buffer, uint8_t *length,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_supply_name",
                     [c_int, POINTER(c_char), POINTER(c_uint8)])

# int asphodel_get_supply_info(AsphodelDevice_t *device, int index,
#         AsphodelSupplyInfo_t *supply_info,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_get_supply_info",
                     [c_int, POINTER(SupplyInfo)])

# int asphodel_check_supply(AsphodelDevice_t *device, int index,
#         int32_t *measurement, uint8_t *result, int tries,
#         AsphodelCommandCallback_t callback, void * closure)
load_device_function("asphodel_check_supply",
                     [c_int, POINTER(c_int32), POINTER(c_uint8), c_uint])


#
# --- asphodel_tcp.h ---
#
try:
    # int asphodel_tcp_devices_supported(void)
    load_library_function("asphodel_tcp_devices_supported", c_int,
                          [], None, ignore_missing=False)
    tcp_devices_supported = bool(lib.asphodel_tcp_devices_supported())
except AttributeError:
    tcp_devices_supported = False

# int asphodel_tcp_init(void)
load_library_function("asphodel_tcp_init", c_int, [], asphodel_error_check)

# void asphodel_tcp_deinit(void)
load_library_function("asphodel_tcp_deinit", None, [])

# int asphodel_tcp_find_devices(AsphodelDevice_t **device_list,
#         size_t *list_size)
load_library_function(
    "asphodel_tcp_find_devices", c_int,
    [POINTER(POINTER(AsphodelDevice)), POINTER(c_size_t)],
    asphodel_error_check)

# int asphodel_tcp_find_devices_filter(AsphodelDevice_t **device_list,
#         size_t *list_size, uint32_t flags)
load_library_function(
    "asphodel_tcp_find_devices_filter", c_int,
    [POINTER(POINTER(AsphodelDevice)), POINTER(c_size_t),
     c_uint32], asphodel_error_check)

# Asphodel_TCPAdvInfo_t* asphodel_tcp_get_advertisement(
#         AsphodelDevice_t* device)
load_library_function(
    "asphodel_tcp_get_advertisement", POINTER(AsphodelTCPAdvInfo),
    [POINTER(AsphodelDevice)])

# int asphodel_tcp_create_device(const char* host, uint16_t port,
#         int timeout, const char* serial, AsphodelDevice_t **device)
load_library_function(
    "asphodel_tcp_create_device", c_int,
    [c_char_p, c_uint16, c_int, c_char_p,
     POINTER(POINTER(AsphodelDevice))],
    asphodel_error_check)

#
# --- asphodel_unit_format.h ---
#

# AsphodelUnitFormatter_t* asphodel_create_unit_formatter(
#         uint8_t unit_type, double minimum, double maximum,
#         double resolution, int use_metric)
load_library_function(
    "asphodel_create_unit_formatter",
    POINTER(AsphodelUnitFormatter),
    [c_uint8, c_double, c_double, c_double, c_int])

# AsphodelUnitFormatter_t* asphodel_create_custom_unit_formatter(
#         double scale, double offset, double resolution,
#         const char *unit_ascii, const char *unit_utf8,
#         const char *unit_html)
load_library_function(
    "asphodel_create_custom_unit_formatter",
    POINTER(AsphodelUnitFormatter),
    [c_double, c_double, c_double, c_char_p, c_char_p, c_char_p])

# int asphodel_format_value_ascii(char *buffer, size_t buffer_size,
#         uint8_t unit_type, double resolution, int use_metric,
#         double value)
load_library_function(
    "asphodel_format_value_ascii", c_int,
    [POINTER(c_char), c_size_t, c_uint8, c_double, c_int, c_double])

# int asphodel_format_value_utf8(char *buffer, size_t buffer_size,
#         uint8_t unit_type, double resolution, int use_metric,
#         double value)
load_library_function("asphodel_format_value_utf8", c_int,
                      [POINTER(c_char), c_size_t, c_uint8, c_double, c_int,
                       c_double])

# int asphodel_format_value_html(char *buffer, size_t buffer_size,
#         uint8_t unit_type, double resolution, int use_metric,
#         double value)
load_library_function("asphodel_format_value_html", c_int,
                      [POINTER(c_char), c_size_t, c_uint8, c_double, c_int,
                       c_double])


#
# --- asphodel_usb.h ---
#

try:
    # int asphodel_usb_devices_supported(void)
    load_library_function("asphodel_usb_devices_supported", c_int, [], None,
                          ignore_missing=False)
    usb_devices_supported = bool(lib.asphodel_usb_devices_supported())
except AttributeError:
    # NOTE: any DLL too old to support this check will support USB
    # and we can continue loading the rest of the functions
    usb_devices_supported = True

# int asphodel_usb_init(void)
load_library_function("asphodel_usb_init", c_int, [], asphodel_error_check)

# void asphodel_usb_deinit(void)
load_library_function("asphodel_usb_deinit", None, [])

# int asphodel_usb_find_devices(AsphodelDevice_t **device_list,
#         size_t *list_size)
load_library_function(
    "asphodel_usb_find_devices", c_int,
    [POINTER(POINTER(AsphodelDevice)), POINTER(c_size_t)],
    asphodel_error_check)

# const char * asphodel_usb_get_backend_version(void)
load_library_function(
    "asphodel_usb_get_backend_version", c_char_p, [],
    asphodel_string_decode_check)


#
# --- asphodel_version.h ---
#

# uint16_t asphodel_get_library_protocol_version(void)
load_library_function(
    "asphodel_get_library_protocol_version", c_uint16, [])

# const char * asphodel_get_library_protocol_version_string(void)
load_library_function(
    "asphodel_get_library_protocol_version_string", c_char_p, [],
    asphodel_string_decode_check)

# const char * asphodel_get_library_build_info(void)
load_library_function(
    "asphodel_get_library_build_info", c_char_p, [],
    asphodel_string_decode_check)

# const char * asphodel_get_library_build_date(void)
load_library_function(
    "asphodel_get_library_build_date", c_char_p, [],
    asphodel_string_decode_check)


#
# --- asphodel_virtual_device.h ---
#

# int asphodel_create_virtual_device(
#         const AsphodelDeviceInfo_t *device_info,
#         const AsphodelVirtualDeviceCallbacks_t *callbacks,
#         uint8_t allow_fallback_values, AsphodelDevice_t **device)
load_library_function(
    "asphodel_create_virtual_device", c_int,
    [POINTER(AsphodelDeviceInfo), POINTER(AsphodelVirtualDeviceCallbacks),
     c_uint8, POINTER(POINTER(AsphodelDevice))],
    asphodel_error_check)

# int asphodel_submit_virtual_device_packets(AsphodelDevice_t *device,
#         const uint8_t *buffer, size_t buffer_length)
load_library_function(
    "asphodel_submit_virtual_device_packets", c_int,
    [POINTER(AsphodelDevice), POINTER(c_uint8), c_size_t],
    asphodel_error_check)

# int asphodel_set_virtual_transfer_limit(AsphodelDevice_t *device,
#         uint64_t remaining_transfers)
load_library_function(
    "asphodel_set_virtual_transfer_limit", c_int,
    [POINTER(AsphodelDevice), c_uint64],
    asphodel_error_check)

# int asphodel_get_virtual_transfer_limit(AsphodelDevice_t *device,
#         uint64_t *remaining_transfers)
load_library_function(
    "asphodel_get_virtual_transfer_limit", c_int,
    [POINTER(AsphodelDevice), POINTER(c_uint64)],
    asphodel_error_check)


# initialize USB
if usb_devices_supported:
    lib.asphodel_usb_init()

# initialize TCP
if tcp_devices_supported:
    lib.asphodel_tcp_init()


device_instances: "weakref.WeakSet[Device]" = weakref.WeakSet()


def _deinit() -> None:
    for device in device_instances:
        device.__del__()
    if usb_devices_supported:
        lib.asphodel_usb_deinit()
    if tcp_devices_supported:
        lib.asphodel_tcp_deinit()


weakref.finalize(sys.modules[__name__], _deinit)


unit_type_names: list[str] = [
    lib.asphodel_unit_type_name(i)
    for i in range(lib.asphodel_get_unit_type_count())]

channel_type_names: list[str] = [
    lib.asphodel_channel_type_name(i)
    for i in range(lib.asphodel_get_channel_type_count())]

setting_type_names: list[str] = [
    lib.asphodel_setting_type_name(i)
    for i in range(lib.asphodel_get_setting_type_count())]
