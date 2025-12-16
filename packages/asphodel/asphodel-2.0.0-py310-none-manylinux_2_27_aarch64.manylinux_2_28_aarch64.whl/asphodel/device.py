from collections.abc import Callable, Sequence
from ctypes import (CFUNCTYPE, POINTER, addressof, c_double, c_float, c_int,
                    c_int8, c_int32, c_size_t, c_uint8, c_uint16, c_uint32,
                    c_uint64, c_void_p, cast, create_string_buffer)
from ctypes import _Pointer  # pyright: ignore
from dataclasses import dataclass
import threading
import time
from typing import Any, NamedTuple
import weakref

from .cache import Cache
from .clib import (AsphodelConnectCallback, AsphodelDevice, AsphodelDeviceInfo,
                   AsphodelDeviceInfoProgressCallback, AsphodelError,
                   AsphodelStreamingCallback, AsphodelTransferCallback,
                   ChannelCalibration, ChannelInfo, CtrlVarInfo,
                   ExtraScanResult, GPIOPortInfo, SettingInfo, StreamInfo,
                   StreamRateInfo, SupplyInfo, asphodel_error_check,
                   device_instances, lib)
from .device_info import DeviceInfo
from .enums import TcpFilterFlags


@dataclass
class TCPAdvInfo:
    tcp_version: int
    connected: bool
    max_incoming_param_length: int
    max_outgoing_param_length: int
    stream_packet_length: int
    protocol_type: int
    serial_number: str
    board_rev: int
    board_type: str
    build_info: str
    build_date: str
    user_tag1: str
    user_tag2: str
    remote_max_incoming_param_length: int
    remote_max_outgoing_param_length: int
    remote_stream_packet_length: int


@dataclass
class PartialStreamInfo:
    # Note: this is just the raw form returned from get_stream_format().
    # You should probably use get_stream() for the complete information
    filler_bits: int
    counter_bits: int
    rate: float
    rate_error: float
    warm_up_delay: float


@dataclass
class PartialChannelInfo:
    # Note: this is just the raw form returned from get_channel_info().
    # You should probably use get_channel() for the complete information
    channel_type: int
    unit_type: int
    filler_bits: int
    data_bits: int
    samples: int
    bits_per_sample: int
    minimum: float
    maximum: float
    resolution: float
    chunk_count: int


class BridgeValues(NamedTuple):
    pos_sense: float
    neg_sense: float
    nominal: float
    minimum: float
    maximum: float


class SelfTestLimits(NamedTuple):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float


class PartialSupplyInfo(NamedTuple):
    unit_type: int
    is_battery: int
    nominal: int
    scale: float
    offset: float


class PartialCtrlVarInfo(NamedTuple):
    unit_type: int
    minimum: int
    maximum: int
    scale: float
    offset: float


class PartialGPIOPortInfo(NamedTuple):
    input_pins: int
    output_pins: int
    floating_pins: int
    loaded_pins: int
    overridden_pins: int


class Device:
    MAX_STRING_LENGTH = 128

    def __init__(self, device: AsphodelDevice) -> None:
        self.device = device
        self._callbacks: list[Any] = []
        self._remote: weakref.ReferenceType[Device] | None = None

        if self.get_transport_type() == "usb":
            self.reconnect_time = 5.0
        else:
            self.reconnect_time = 10.0

        device_instances.add(self)

    def open(self) -> None:
        ret = self.device.open_device(self.device)
        asphodel_error_check(ret)

    def close(self) -> None:
        self.device.close_device(self.device)

    def __del__(self) -> None:
        device = getattr(self, "device", None)
        if device:
            del self.device
            device.close_device(device)
            device.free_device(device)

    def get_location_string(self) -> str:
        return self.device.location_string.decode("utf-8")

    def get_transport_type(self) -> str:
        if lib.asphodel_get_library_protocol_version() >= 0x203:
            return self.device.transport_type.decode("utf-8")
        else:
            # library is too old to support transport type; must be USB
            return "usb"

    def get_serial_number(self) -> str:
        buffer = create_string_buffer(64)
        ret = self.device.get_serial_number(
            self.device, buffer, len(buffer))
        asphodel_error_check(ret)
        return buffer.value.decode("utf-8")

    def do_transfer(self, cmd: int, params: bytes | None,
                    callback: Callable[[int, bytes], None]) -> None:
        if params is None:
            params = b""

        params_buffer = (c_uint8 * len(params)).from_buffer_copy(params)

        def cb(status: int, params: "_Pointer[c_uint8]", param_length: int,
               closure: c_void_p) -> None:
            if params:
                array_type = POINTER(c_uint8 * param_length)
                param_bytes = bytes(cast(params, array_type).contents)
            else:
                param_bytes = b""
            try:
                callback(status, param_bytes)
            except Exception:
                pass  # nothing can be done about it here
            self._callbacks.remove(c_callback)

        c_callback = AsphodelTransferCallback(cb)
        self._callbacks.append(c_callback)

        ret = self.device.do_transfer(
            self.device, cmd, params_buffer, len(params), c_callback, None)
        asphodel_error_check(ret)

    def do_transfer_blocking(self, cmd: int,
                             params: bytes | None = None) -> bytes:
        """
        This function is for testing purposes only!
        """
        finished = threading.Event()
        result: tuple[int, bytes] | None = None

        def callback(status: int, param_bytes: bytes) -> None:
            nonlocal result
            result = (status, param_bytes)
            finished.set()
        self.do_transfer(cmd, params, callback)

        while not finished.is_set():
            self.poll_device(100)

        if result is None:
            raise Exception("Callback never fired")

        ret, params = result

        asphodel_error_check(ret)

        return params

    def do_transfer_reset(self, cmd: int, params: bytes | None,
                          callback: Callable[[int], None]) -> None:
        if params is None:
            params = b""

        params_buffer = (c_uint8 * len(params)).from_buffer_copy(params)

        def cb(status: int, params: "_Pointer[c_uint8]", param_length: int,
               closure: c_void_p) -> None:
            try:
                callback(status)
            except Exception:
                pass  # nothing can be done about it here
            self._callbacks.remove(c_callback)

        c_callback = AsphodelTransferCallback(cb)
        self._callbacks.append(c_callback)

        ret = self.device.do_transfer_reset(
            self.device, cmd, params_buffer, len(params), c_callback, None)
        asphodel_error_check(ret)

    def do_transfer_reset_blocking(self, cmd: int,
                                   params: bytes | None = None) -> None:
        """
        This function is for testing purposes only!
        """
        finished = threading.Event()
        ret: int | None = None

        def callback(status: int) -> None:
            nonlocal ret
            ret = status
            finished.set()
        self.do_transfer_reset(cmd, params, callback)

        while not finished.is_set():
            self.poll_device(100)

        if ret is None:
            raise Exception("Callback never fired")

        asphodel_error_check(ret)

    def start_streaming_packets(
            self, packet_count: int, transfer_count: int, timeout: int,
            callback: Callable[[int, list[bytes]], None] | None) -> None:
        if callback:
            def cb(status: int, stream_data: "_Pointer[c_uint8]",
                   packet_size: int, packet_count: int,
                   closure: c_void_p) -> None:
                if stream_data:
                    array_type = POINTER(
                        (c_uint8 * packet_size) * packet_count)
                    array = cast(stream_data, array_type).contents
                    stream_packets = [bytes(a) for a in array]
                else:
                    stream_packets = []
                try:
                    callback(status, stream_packets)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = AsphodelStreamingCallback(cb)
            self._streaming_callback = c_callback
        else:
            try:
                del self._streaming_callback
            except AttributeError:
                pass
            c_callback = AsphodelStreamingCallback(0)
        ret = self.device.start_streaming_packets(
            self.device, packet_count, transfer_count, timeout, c_callback,
            None)
        asphodel_error_check(ret)

    def stop_streaming_packets(self) -> None:
        self.device.stop_streaming_packets(self.device)
        try:
            del self._streaming_callback
        except AttributeError:
            pass

    def get_stream_packets_blocking(self, byte_count: int,
                                    timeout: int) -> bytes:
        buffer = (c_uint8 * byte_count)()
        count_int = c_int(byte_count)
        ret = self.device.get_stream_packets_blocking(
            self.device, buffer, count_int, timeout)
        asphodel_error_check(ret)
        return bytes(buffer[0:count_int.value])

    def get_max_incoming_param_length(self) -> int:
        v = self.device.get_max_incoming_param_length(self.device)
        return v

    def get_max_outgoing_param_length(self) -> int:
        v = self.device.get_max_outgoing_param_length(self.device)
        return v

    def get_stream_packet_length(self) -> int:
        v = self.device.get_stream_packet_length(self.device)
        return v

    def poll_device(self, milliseconds: int) -> None:
        ret = self.device.poll_device(self.device, milliseconds, None)
        asphodel_error_check(ret)

    def set_connect_callback(
            self, callback: Callable[[int, int], None] | None) -> None:
        if callback:
            # void (*)(int status, int connected, void * closure)
            def cb(status: int, connected: int, closure: c_void_p) -> None:
                try:
                    callback(status, connected)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = AsphodelConnectCallback(cb)
            self._connect_callback: Any = c_callback
        else:
            c_callback = AsphodelConnectCallback(0)
            self._connect_callback = None

        ret = self.device.set_connect_callback(self.device, c_callback, None)
        asphodel_error_check(ret)

    def wait_for_connect(self, timeout: int) -> None:
        ret = self.device.wait_for_connect(self.device, timeout)
        asphodel_error_check(ret)

    def _get_raw_remote_device(self) -> AsphodelDevice:
        remote_ptr = POINTER(AsphodelDevice)()
        ret = self.device.get_remote_device(self.device, remote_ptr)
        asphodel_error_check(ret)
        return remote_ptr.contents

    def get_remote_device(self) -> "Device":
        if self._remote is None:
            remote = None
        else:
            remote = self._remote()

        if remote is None:
            remote_dev = self._get_raw_remote_device()
            remote = Device(remote_dev)
            self._remote = weakref.ref(remote)

        return remote

    def reconnect(self, bootloader: bool = False, application: bool = False,
                  serial_number: str | None = None) -> None:
        if bootloader and application:
            raise ValueError("cannot set both application and bootloader")
        elif bootloader:
            reconnect_func = self.reconnect_device_bootloader
        elif application:
            reconnect_func = self.reconnect_device_application
        else:
            reconnect_func = self.reconnect_device

        if not serial_number:
            try:
                serial_number = self.get_serial_number()
            except AsphodelError:
                pass

        end_time = time.monotonic() + self.reconnect_time

        # give the device some time to process
        time.sleep(0.5)

        while True:
            try:
                # try a reconnect
                reconnect_func(reopen=True)
                break
            except AsphodelError:
                if time.monotonic() >= end_time:
                    raise

            if serial_number:
                # scan for an identical serial number
                device = self.find_device_by_serial(serial_number)
                if device:
                    # give the device some time to process
                    time.sleep(0.5)

                    # try 1/2 reconnect
                    try:
                        reconnect_func(reopen=True)
                        break
                    except AsphodelError:
                        pass

                    # give the device some time to process
                    time.sleep(0.5)

                    # try 2/2 reconnect
                    try:
                        reconnect_func(reopen=True)
                        break
                    except AsphodelError:
                        pass

                    # use the device we found
                    native_device = device.device

                    # set the inner device to None to prevent it from being
                    # freed along with the outer device
                    device.device = None  # type: ignore

                    self._reconnect_helper(native_device, reopen=True)
                    break

            # wait a bit to not hog resources
            time.sleep(0.25)

        self.wait_for_connect(int(self.reconnect_time * 1000))

    def _reconnect_helper(self, new_device: AsphodelDevice,
                          reopen: bool) -> None:
        if addressof(new_device) == addressof(self.device):
            return

        self.close()
        if self.device:
            self.device.free_device(self.device)
        self.device = new_device
        if reopen:
            self.open()

        if self._remote is not None:
            remote = self._remote()
            if remote:
                try:
                    remote_dev = self._get_raw_remote_device()
                    remote.close()
                    remote.device.free_device(remote.device)
                    remote.device = remote_dev
                    if reopen:
                        remote.open()
                except AsphodelError:
                    pass

        self._callbacks.clear()

    def reconnect_device(self, reopen: bool = False) -> None:
        reconnected_ptr = POINTER(AsphodelDevice)()
        ret = self.device.reconnect_device(self.device, reconnected_ptr)
        asphodel_error_check(ret)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def reconnect_device_bootloader(self, reopen: bool = False) -> None:
        reconnected_ptr = POINTER(AsphodelDevice)()
        ret = self.device.reconnect_device_bootloader(
            self.device, reconnected_ptr)
        asphodel_error_check(ret)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def reconnect_device_application(self, reopen: bool = False) -> None:
        reconnected_ptr = POINTER(AsphodelDevice)()
        ret = self.device.reconnect_device_application(
            self.device, reconnected_ptr)
        asphodel_error_check(ret)
        self._reconnect_helper(reconnected_ptr.contents, reopen)

    def supports_rf_power_commands(self) -> bool:
        v = lib.asphodel_supports_rf_power_commands(self.device)
        return bool(v)

    def supports_radio_commands(self) -> bool:
        v = lib.asphodel_supports_radio_commands(self.device)
        return bool(v)

    def supports_remote_commands(self) -> bool:
        v = lib.asphodel_supports_remote_commands(self.device)
        return bool(v)

    def supports_bootloader_commands(self) -> bool:
        v = lib.asphodel_supports_bootloader_commands(self.device)
        return bool(v)

    def set_error_callback(
            self, callback: Callable[["Device", int], None] | None) -> None:
        error_cb_type = CFUNCTYPE(
            None, POINTER(AsphodelDevice), c_int, c_void_p)

        if callback:
            def cb(device: "_Pointer[AsphodelDevice]", error_code: int,
                   closure: c_void_p) -> None:
                try:
                    callback(self, error_code)
                except Exception:
                    pass  # nothing can be done about it here

            c_callback = error_cb_type(cb)
            self.device.error_callback = c_callback
            self._error_callback: Any = c_callback
        else:
            self.device.error_callback = error_cb_type()
            self._error_callback = None

    def get_remote_lengths(self) -> tuple[int, int, int]:
        max_incoming_param_length = c_size_t()
        max_outgoing_param_length = c_size_t()
        stream_packet_length = c_size_t()
        ret = self.device.get_remote_lengths(
            self.device, max_incoming_param_length, max_outgoing_param_length,
            stream_packet_length)
        asphodel_error_check(ret)
        return (max_incoming_param_length.value,
                max_outgoing_param_length.value,
                stream_packet_length.value)

    def tcp_get_advertisement(self) -> TCPAdvInfo:
        adv_ptr = lib.asphodel_tcp_get_advertisement(self.device)
        adv = adv_ptr.contents

        def decode_safe(b: bytes) -> str:
            try:
                return b.decode("utf-8")
            except UnicodeDecodeError:
                return "ERROR"

        return TCPAdvInfo(
            adv.tcp_version,
            bool(adv.connected),
            adv.max_incoming_param_length,
            adv.max_outgoing_param_length,
            adv.stream_packet_length,
            adv.protocol_type,
            decode_safe(adv.serial_number),
            adv.board_rev,
            decode_safe(adv.board_type),
            decode_safe(adv.build_info),
            decode_safe(adv.build_date),
            decode_safe(adv.user_tag1),
            decode_safe(adv.user_tag2),
            adv.remote_max_incoming_param_length,
            adv.remote_max_outgoing_param_length,
            adv.remote_stream_packet_length
        )

    def submit_virtual_device_packets(self, buffer: bytes) -> None:
        data = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        lib.asphodel_submit_virtual_device_packets(
            self.device, data, len(buffer))

    def set_virtual_device_transfer_limit(
            self, remaining_transfers: int) -> None:
        lib.asphodel_set_virtual_transfer_limit(
            self.device, remaining_transfers)

    def get_virtual_device_transfer_limit(self) -> int:
        remaining_transfers = c_uint64()
        lib.asphodel_get_virtual_transfer_limit(
            self.device, remaining_transfers)
        return remaining_transfers.value

    def get_protocol_version(self) -> int:
        version = c_uint16()
        lib.asphodel_get_protocol_version_blocking(self.device, version)
        return version.value

    def get_protocol_version_string(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_protocol_version_string_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_board_info(self) -> tuple[str, int]:
        rev = c_uint8()
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_board_info_blocking(self.device, rev, buffer,
                                             self.MAX_STRING_LENGTH)
        return (buffer.value.decode("utf-8"), rev.value)

    def get_user_tag_locations(self) -> tuple[int, int, int, int, int, int]:
        array = (c_size_t * 6)()
        lib.asphodel_get_user_tag_locations_blocking(self.device, array)
        values: tuple[int, int, int, int, int, int] = tuple(array)
        return values

    def get_build_info(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_build_info_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_build_date(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_build_date_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_commit_id(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_commit_id_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_repo_branch(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_repo_branch_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_repo_name(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_repo_name_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_chip_family(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_chip_family_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_chip_model(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_chip_model_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_chip_id(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_chip_id_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_nvm_size(self) -> int:
        size = c_size_t()
        lib.asphodel_get_nvm_size_blocking(self.device, size)
        return size.value

    def erase_nvm(self) -> None:
        lib.asphodel_erase_nvm_blocking(self.device)

    def write_nvm_raw(self, address: int,
                      values: bytes | bytearray) -> None:
        data = (c_uint8 * len(values)).from_buffer_copy(values)
        lib.asphodel_write_nvm_raw_blocking(
            self.device, address, data, len(values))

    def write_nvm_section(self, address: int,
                          values: bytes | bytearray) -> None:
        data = (c_uint8 * len(values)).from_buffer_copy(values)
        lib.asphodel_write_nvm_section_blocking(
            self.device, address, data, len(values))

    def read_nvm_raw(self, address: int) -> bytes:
        max_length = self.get_max_incoming_param_length()
        data = (c_uint8 * max_length)()
        data_length = c_size_t(max_length)
        lib.asphodel_read_nvm_raw_blocking(
            self.device, address, data, data_length)
        actual_length = min(max_length, data_length.value)
        return bytes(data[0:actual_length])

    def read_nvm_section(self, address: int, length: int) -> bytes:
        data = (c_uint8 * length)()
        lib.asphodel_read_nvm_section_blocking(
            self.device, address, data, length)
        return bytes(data)

    def read_user_tag_string(self, offset: int, length: int) -> str:
        buffer = create_string_buffer(length + 1)
        lib.asphodel_read_user_tag_string_blocking(
            self.device, offset, length, buffer)
        return buffer.value.decode("utf-8")

    def write_user_tag_string(self, offset: int, length: int,
                              string: str) -> None:
        lib.asphodel_write_user_tag_string_blocking(
            self.device, offset, length, string.encode("utf-8"))

    def get_nvm_modified(self) -> bool:
        modified = c_uint8()
        lib.asphodel_get_nvm_modified_blocking(self.device, modified)
        return bool(modified.value)

    def get_nvm_hash(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_nvm_hash_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def get_setting_hash(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_setting_hash_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def flush(self) -> None:
        lib.asphodel_flush_blocking(self.device)

    def reset(self) -> None:
        lib.asphodel_reset_blocking(self.device)

    def get_bootloader_info(self) -> str:
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_bootloader_info_blocking(
            self.device, buffer, self.MAX_STRING_LENGTH)
        return buffer.value.decode("utf-8")

    def bootloader_jump(self) -> None:
        lib.asphodel_bootloader_jump_blocking(self.device)

    def get_reset_flag(self) -> int:
        flag = c_uint8()
        lib.asphodel_get_reset_flag_blocking(self.device, flag)
        return flag.value

    def clear_reset_flag(self) -> None:
        lib.asphodel_clear_reset_flag_blocking(self.device)

    def get_rgb_count(self) -> int:
        count = c_int()
        lib.asphodel_get_rgb_count_blocking(self.device, count)
        return count.value

    def get_rgb_values(self, index: int) -> tuple[int, int, int]:
        values = (c_uint8 * 3)()
        lib.asphodel_get_rgb_values_blocking(self.device, index, values)
        return tuple(values)

    def set_rgb_values(self, index: int,
                       values: tuple[int, int, int] | list[int] | bytes,
                       instant: bool = False) -> None:
        data = (c_uint8 * 3).from_buffer_copy(bytes(values))
        lib.asphodel_set_rgb_values_blocking(
            self.device, index, data, instant)

    def set_rgb_values_hex(self, index: int, hex_color: int,
                           instant: bool = False) -> None:
        lib.asphodel_set_rgb_values_hex_blocking(
            self.device, index, hex_color, instant)

    def get_led_count(self) -> int:
        count = c_int()
        lib.asphodel_get_led_count_blocking(self.device, count)
        return count.value

    def get_led_value(self, index: int) -> int:
        value = c_uint8()
        lib.asphodel_get_led_value_blocking(self.device, index, value)
        return value.value

    def set_led_value(self, index: int, value: int,
                      instant: bool = False) -> None:
        lib.asphodel_set_led_value_blocking(
            self.device, index, value, instant)

    def set_device_mode(self, mode: int) -> None:
        lib.asphodel_set_device_mode_blocking(self.device, mode)

    def get_device_mode(self) -> int:
        mode = c_uint8()
        lib.asphodel_get_device_mode_blocking(self.device, mode)
        return mode.value

    def get_stream_count(self) -> tuple[int, int, int]:
        count = c_int()
        filler_bits = c_uint8()
        id_bits = c_uint8()
        lib.asphodel_get_stream_count_blocking(
            self.device, count, filler_bits, id_bits)
        return (count.value, filler_bits.value, id_bits.value)

    def get_stream(self, index: int) -> StreamInfo:
        ptr = POINTER(StreamInfo)()
        lib.asphodel_get_stream_blocking(self.device, index, ptr)
        stream = ptr.contents
        stream._free_func = lib.asphodel_free_stream
        return stream

    def get_stream_channels(self, index: int) -> tuple[int, ...]:
        channels = (c_uint8 * 255)()
        channels_length = c_uint8(255)
        lib.asphodel_get_stream_channels_blocking(
            self.device, index, channels, channels_length)
        return tuple(channels[0:channels_length.value])

    def get_stream_format(self, index: int) -> PartialStreamInfo:
        """
        Prefer get_stream()
        """
        info = StreamInfo()
        lib.asphodel_get_stream_format_blocking(self.device, index, info)
        return PartialStreamInfo(
            filler_bits=info.filler_bits,
            counter_bits=info.counter_bits,
            rate=info.rate,
            rate_error=info.rate_error,
            warm_up_delay=info.warm_up_delay,
        )

    def enable_stream(self, index: int, enable: bool = True) -> None:
        lib.asphodel_enable_stream_blocking(self.device, index, enable)

    def warm_up_stream(self, index: int, enable: bool = True) -> None:
        lib.asphodel_warm_up_stream_blocking(self.device, index, enable)

    def get_stream_status(self, index: int) -> tuple[bool, bool]:
        enable = c_int()
        warm_up = c_int()
        lib.asphodel_get_stream_status_blocking(
            self.device, index, enable, warm_up)
        return (bool(enable.value), bool(warm_up.value))

    def get_stream_rate_info(self, index: int) -> StreamRateInfo:
        """
        Return (available, channel_index, invert, scale, offset) for a
        specific stream.
        """
        available = c_int()
        channel_index = c_int()
        invert = c_int()
        scale = c_float()
        offset = c_float()
        lib.asphodel_get_stream_rate_info_blocking(
            self.device, index, available, channel_index, invert, scale,
            offset)

        value = StreamRateInfo()
        value.available = available.value
        value.channel_index = channel_index.value
        value.invert = invert.value
        value.scale = scale.value
        value.offset = offset.value

        return value

    def get_channel_count(self) -> int:
        count = c_int()
        lib.asphodel_get_channel_count_blocking(self.device, count)
        return count.value

    def get_channel(self, index: int) -> ChannelInfo:
        ptr = POINTER(ChannelInfo)()
        lib.asphodel_get_channel_blocking(self.device, index, ptr)
        channel = ptr.contents
        channel._free_func = lib.asphodel_free_channel
        return channel

    def get_channel_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_channel_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_channel_info(self, index: int) -> PartialChannelInfo:
        """
        Prefer get_channel()
        """
        info = ChannelInfo()
        lib.asphodel_get_channel_info_blocking(self.device, index, info)
        return PartialChannelInfo(
            channel_type=info.channel_type,
            unit_type=info.unit_type,
            filler_bits=info.filler_bits,
            data_bits=info.data_bits,
            samples=info.samples,
            bits_per_sample=info.bits_per_sample,
            minimum=info.minimum,
            maximum=info.maximum,
            resolution=info.resolution,
            chunk_count=info._chunk_count,
        )

    def get_channel_coefficients(self, index: int) -> tuple[float, ...]:
        coefficients = (c_float * 255)()
        coefficients_length = c_uint8(255)
        lib.asphodel_get_channel_coefficients_blocking(
            self.device, index, coefficients, coefficients_length)
        return tuple(coefficients[0:coefficients_length.value])

    def get_channel_chunk(self, index: int, chunk_number: int) -> bytes:
        chunk = (c_uint8 * 255)()
        chunk_length = c_uint8(255)
        lib.asphodel_get_channel_chunk_blocking(
            self.device, index, chunk_number, chunk, chunk_length)
        return bytes(chunk[0:chunk_length.value])

    def channel_specific(self, index: int, values: bytes) -> bytes:
        reply = (c_uint8 * 255)()
        reply_length = c_uint8(255)
        data = (c_uint8 * len(values))()
        for i in range(len(values)):
            data[i] = values[i]
        lib.asphodel_channel_specific_blocking(
            self.device, index, data, len(values), reply, reply_length)
        return bytes(reply[0:reply_length.value])

    def get_channel_calibration(
            self, index: int) -> ChannelCalibration | None:
        """
        Return ChannelCalibration for a specific channel. If no
        calibration is available for that channel then None in returned instead
        """
        available = c_int()
        cal = ChannelCalibration()
        lib.asphodel_get_channel_calibration_blocking(
            self.device, index, available, cal)
        if not bool(available.value):
            return None
        else:
            return cal

    def get_supply_count(self) -> int:
        count = c_int()
        lib.asphodel_get_supply_count_blocking(self.device, count)
        return count.value

    def get_supply_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_supply_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_supply_info_raw(self, index: int) -> PartialSupplyInfo:
        info = SupplyInfo()
        lib.asphodel_get_supply_info_blocking(self.device, index, info)
        return PartialSupplyInfo(
            unit_type=info.unit_type,
            is_battery=info.is_battery,
            nominal=info.nominal,
            scale=info.scale,
            offset=info.offset,
        )

    def get_supply_info(self, index: int) -> SupplyInfo:
        info = SupplyInfo()
        lib.asphodel_get_supply_info_blocking(self.device, index, info)

        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_supply_name_blocking(
            self.device, index, buffer, buffer_length)
        name = buffer.raw[0:buffer_length.value]

        info._name = name  # store a reference so they're not freed
        info.name = name
        info.name_length = len(name)

        return info

    def check_supply(self, index: int, tries: int = 20) -> tuple[int, int]:
        """
        Return (measurement, result) for a specific supply. If tries is
        positive & non-zero, then no more than this number of transfers will be
        sent before raising an exception. Otherwise, an unlimited number of
        transfers may be performed.
        """
        measurement = c_int32()
        result = c_uint8()
        lib.asphodel_check_supply_blocking(
            self.device, index, measurement, result, tries)
        return (measurement.value, result.value)

    def get_ctrl_var_count(self) -> int:
        count = c_int()
        lib.asphodel_get_ctrl_var_count_blocking(self.device, count)
        return count.value

    def get_ctrl_var_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_ctrl_var_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_ctrl_var_info_raw(self, index: int) -> PartialCtrlVarInfo:
        info = CtrlVarInfo()
        lib.asphodel_get_ctrl_var_info_blocking(self.device, index, info)
        return PartialCtrlVarInfo(
            unit_type=info.unit_type,
            minimum=info.minimum,
            maximum=info.maximum,
            scale=info.scale,
            offset=info.offset,
        )

    def get_ctrl_var_info(self, index: int) -> CtrlVarInfo:
        info = CtrlVarInfo()
        lib.asphodel_get_ctrl_var_info_blocking(self.device, index, info)

        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_ctrl_var_name_blocking(
            self.device, index, buffer, buffer_length)
        name = buffer.raw[0:buffer_length.value]

        info._name = name  # store a reference so they're not freed
        info.name = name
        info.name_length = len(name)

        return info

    def get_ctrl_var(self, index: int) -> int:
        value = c_int32()
        lib.asphodel_get_ctrl_var_blocking(self.device, index, value)
        return value.value

    def set_ctrl_var(self, index: int, value: int) -> None:
        lib.asphodel_set_ctrl_var_blocking(self.device, index, value)

    def get_setting_count(self) -> int:
        count = c_int()
        lib.asphodel_get_setting_count_blocking(self.device, count)
        return count.value

    def get_setting_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_setting_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_setting_info(self, index: int) -> SettingInfo:
        info = SettingInfo()
        lib.asphodel_get_setting_info_blocking(self.device, index, info)
        return info

    def get_setting_default(self, index: int) -> bytes:
        default = (c_uint8 * 255)()
        default_length = c_uint8(255)
        lib.asphodel_get_setting_default_blocking(
            self.device, index, default, default_length)
        return bytes(default[0:default_length.value])

    def get_custom_enum_counts(self) -> tuple[int, ...]:
        counts = (c_uint8 * 255)()
        counts_length = c_uint8(255)
        lib.asphodel_get_custom_enum_counts_blocking(
            self.device, counts, counts_length)
        return tuple(counts[0:counts_length.value])

    def get_custom_enum_value_name(self, index: int, value: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_custom_enum_value_name_blocking(
            self.device, index, value, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_setting_category_count(self) -> int:
        count = c_int()
        lib.asphodel_get_setting_category_count_blocking(self.device, count)
        return count.value

    def get_setting_category_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_setting_category_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_setting_category_settings(self, index: int) -> tuple[int, ...]:
        settings = (c_uint8 * 255)()
        settings_length = c_uint8(255)
        lib.asphodel_get_setting_category_settings_blocking(
            self.device, index, settings, settings_length)
        return tuple(settings[0:settings_length.value])

    def get_gpio_port_count(self) -> int:
        count = c_int()
        lib.asphodel_get_gpio_port_count_blocking(self.device, count)
        return count.value

    def get_gpio_port_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_gpio_port_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_gpio_port_info_raw(self, index: int) -> PartialGPIOPortInfo:
        info = GPIOPortInfo()
        lib.asphodel_get_gpio_port_info_blocking(self.device, index, info)
        return PartialGPIOPortInfo(
            input_pins=info.input_pins,
            output_pins=info.output_pins,
            floating_pins=info.floating_pins,
            loaded_pins=info.loaded_pins,
            overridden_pins=info.overridden_pins,
        )

    def get_gpio_port_info(self, index: int) -> GPIOPortInfo:
        info = GPIOPortInfo()
        lib.asphodel_get_gpio_port_info_blocking(self.device, index, info)

        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_gpio_port_name_blocking(
            self.device, index, buffer, buffer_length)
        name = buffer.raw[0:buffer_length.value]

        info._name = name  # store a reference so they're not freed
        info.name = name
        info.name_length = len(name)

        return info

    def get_gpio_port_values(self, index: int) -> int:
        pin_values = c_uint32()
        lib.asphodel_get_gpio_port_values_blocking(
            self.device, index, pin_values)
        return pin_values.value

    def set_gpio_port_modes(self, index: int, mode: int, pins: int) -> None:
        lib.asphodel_set_gpio_port_modes_blocking(
            self.device, index, mode, pins)

    def disable_gpio_overrides(self) -> None:
        lib.asphodel_disable_gpio_overrides_blocking(self.device)

    def get_bus_counts(self) -> tuple[int, int]:
        spi_count = c_int()
        i2c_count = c_int()
        lib.asphodel_get_bus_counts_blocking(self.device, spi_count, i2c_count)
        return (spi_count.value, i2c_count.value)

    def set_spi_cs_mode(self, index: int, mode: int) -> None:
        lib.asphodel_set_spi_cs_mode_blocking(self.device, index, mode)

    def do_spi_transfer(self, index: int, write_bytes: bytes) -> bytes:
        data_length = len(write_bytes)
        tx_data = (c_uint8 * data_length).from_buffer_copy(write_bytes)
        rx_data = (c_uint8 * data_length)()
        lib.asphodel_do_spi_transfer_blocking(
            self.device, index, tx_data, rx_data, data_length)
        return bytes(rx_data[0:data_length])

    def do_i2c_write(self, index: int, addr: int, write_bytes: bytes) -> None:
        tx_data = (c_uint8 * len(write_bytes)).from_buffer_copy(write_bytes)
        lib.asphodel_do_i2c_write_blocking(
            self.device, index, addr, tx_data, len(write_bytes))

    def do_i2c_read(self, index: int, addr: int, read_length: int) -> bytes:
        rx_data = (c_uint8 * read_length)()
        lib.asphodel_do_i2c_read_blocking(
            self.device, index, addr, rx_data, read_length)
        return bytes(rx_data[0:read_length])

    def do_i2c_write_read(self, index: int, addr: int, write_bytes: bytes,
                          read_length: int) -> bytes:
        tx_data = (c_uint8 * len(write_bytes)).from_buffer_copy(write_bytes)
        rx_data = (c_uint8 * read_length)()
        lib.asphodel_do_i2c_write_read_blocking(
            self.device, index, addr, tx_data, len(write_bytes), rx_data,
            read_length)
        return bytes(rx_data[0:read_length])

    def do_radio_fixed_test(self, channel: int, duration: int,
                            mode: int) -> None:
        lib.asphodel_do_radio_fixed_test_blocking(
            self.device, channel, duration, mode)

    def do_radio_sweep_test(self, start: int, stop: int, hop_interval: int,
                            hop_count: int, mode: int) -> None:
        lib.asphodel_do_radio_sweep_test_blocking(
            self.device, start, stop, hop_interval, hop_count, mode)

    def get_info_region_count(self) -> int:
        count = c_int()
        lib.asphodel_get_info_region_count_blocking(self.device, count)
        return count.value

    def get_info_region_name(self, index: int) -> str:
        buffer = create_string_buffer(255)
        buffer_length = c_uint8(255)
        lib.asphodel_get_info_region_name_blocking(
            self.device, index, buffer, buffer_length)
        result = buffer.raw[0:buffer_length.value]
        return result.decode("utf-8")

    def get_info_region(self, index: int) -> tuple[int, ...]:
        data = (c_uint8 * 255)()
        data_length = c_uint8(255)
        lib.asphodel_get_info_region_blocking(
            self.device, index, data, data_length)
        return tuple(data[0:data_length.value])

    def get_stack_info(self) -> tuple[int, int]:
        array = (c_uint32 * 2)()
        lib.asphodel_get_stack_info_blocking(self.device, array)
        return tuple(array)

    def echo_raw(self, values: bytes | bytearray) -> bytes:
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(values)
        lib.asphodel_echo_raw_blocking(
            self.device, data, len(values), reply, reply_length)
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    def echo_transaction(self, values: bytes | bytearray) -> bytes:
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(values)
        lib.asphodel_echo_transaction_blocking(
            self.device, data, len(values), reply, reply_length)
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    def echo_params(self, values: bytes | bytearray) -> bytes:
        max_length = self.get_max_incoming_param_length()
        reply = (c_uint8 * max_length)()
        reply_length = c_size_t(max_length)
        data = (c_uint8 * len(values)).from_buffer_copy(values)
        lib.asphodel_echo_params_blocking(
            self.device, data, len(values), reply, reply_length)
        actual_length = min(max_length, reply_length.value)
        return bytes(reply[0:actual_length])

    def enable_rf_power(self, enable: bool = True) -> None:
        lib.asphodel_enable_rf_power_blocking(self.device, enable)

    def get_rf_power_status(self) -> bool:
        enabled = c_int()
        lib.asphodel_get_rf_power_status_blocking(self.device, enabled)
        return bool(enabled.value)

    def get_rf_power_ctrl_vars(self) -> tuple[int, ...]:
        ctrl_var_indexes = (c_uint8 * 255)()
        length = c_uint8(255)
        lib.asphodel_get_rf_power_ctrl_vars_blocking(
            self.device, ctrl_var_indexes, length)
        return tuple(ctrl_var_indexes[0:length.value])

    def reset_rf_power_timeout(self, timeout: int) -> None:
        lib.asphodel_reset_rf_power_timeout_blocking(self.device, timeout)

    def stop_radio(self) -> None:
        lib.asphodel_stop_radio_blocking(self.device)

    def start_radio_scan(self) -> None:
        lib.asphodel_start_radio_scan_blocking(self.device)

    def get_raw_radio_scan_results(self) -> tuple[int, ...]:
        serials = (c_uint32 * 255)()
        serials_length = c_size_t(255)
        lib.asphodel_get_raw_radio_scan_results_blocking(
            self.device, serials, serials_length)
        return tuple(serials[0:serials_length.value])

    def get_radio_scan_results(self) -> set[int]:
        serials_ptr = POINTER(c_uint32)()
        serials_length = c_size_t()
        lib.asphodel_get_radio_scan_results_blocking(
            self.device, serials_ptr, serials_length)
        serials = set(serials_ptr[0:serials_length.value])
        lib.asphodel_free_radio_scan_results(serials_ptr)
        return serials

    def get_raw_radio_extra_scan_results(
            self) -> list[ExtraScanResult]:
        results = (ExtraScanResult * 255)()
        results_length = c_size_t(255)
        lib.asphodel_get_raw_radio_extra_scan_results_blocking(
            self.device, results, results_length)
        result_list: list[ExtraScanResult] = []
        for result_struct in results[0:results_length.value]:
            result_list.append(ExtraScanResult.from_buffer_copy(
                result_struct))
        return result_list

    def get_radio_extra_scan_results(self) -> list[ExtraScanResult]:
        results_ptr = POINTER(ExtraScanResult)()
        results_length = c_size_t()
        lib.asphodel_get_radio_extra_scan_results_blocking(
            self.device, results_ptr, results_length)
        result_list: list[ExtraScanResult] = []
        for result_struct in results_ptr[0:results_length.value]:
            result_list.append(ExtraScanResult.from_buffer_copy(
                result_struct))
        lib.asphodel_free_radio_extra_scan_results(results_ptr)
        return result_list

    def get_radio_scan_power(self, serial_numbers: Sequence[int]) -> list[int]:
        sn_array = (c_uint32 * len(serial_numbers))(*serial_numbers)
        powers = (c_int8 * len(serial_numbers))()
        lib.asphodel_get_radio_scan_power_blocking(
            self.device, sn_array, powers, len(serial_numbers))
        return list(powers[0:len(serial_numbers)])

    def connect_radio(self, serial_number: int) -> None:
        lib.asphodel_connect_radio_blocking(self.device, serial_number)

    def get_radio_status(self) -> tuple[bool, int, int, bool]:
        connected = c_int()
        serial_number = c_uint32()
        protocol_type = c_uint8()
        scanning = c_int()
        lib.asphodel_get_radio_status_blocking(
            self.device, connected, serial_number, protocol_type, scanning)
        return (bool(connected.value), serial_number.value,
                protocol_type.value, bool(scanning.value))

    def get_radio_ctrl_vars(self) -> tuple[int, ...]:
        ctrl_var_indexes = (c_uint8 * 255)()
        length = c_uint8(255)
        lib.asphodel_get_radio_ctrl_vars_blocking(
            self.device, ctrl_var_indexes, length)
        return tuple(ctrl_var_indexes[0:length.value])

    def get_radio_default_serial(self) -> int:
        serial_number = c_uint32()
        lib.asphodel_get_radio_default_serial_blocking(
            self.device, serial_number)
        return serial_number.value

    def start_radio_scan_boot(self) -> None:
        lib.asphodel_start_radio_scan_boot_blocking(self.device)

    def connect_radio_boot(self, serial_number: int) -> None:
        lib.asphodel_connect_radio_boot_blocking(self.device, serial_number)

    def stop_remote(self) -> None:
        lib.asphodel_stop_remote_blocking(self.device)

    def restart_remote(self) -> None:
        lib.asphodel_restart_remote_blocking(self.device)

    def get_remote_status(self) -> tuple[bool, int, int]:
        connected = c_int()
        serial_number = c_uint32()
        protocol_type = c_uint8()
        lib.asphodel_get_remote_status_blocking(
            self.device, connected, serial_number, protocol_type)
        return (bool(connected.value), serial_number.value,
                protocol_type.value)

    def restart_remote_app(self) -> None:
        lib.asphodel_restart_remote_app_blocking(self.device)

    def restart_remote_boot(self) -> None:
        lib.asphodel_restart_remote_boot_blocking(self.device)

    def bootloader_start_program(self) -> None:
        lib.asphodel_bootloader_start_program_blocking(self.device)

    def get_bootloader_page_info(self) -> tuple[tuple[int, int], ...]:
        page_info = (c_uint32 * 255)()
        length = c_uint8(255)
        lib.asphodel_get_bootloader_page_info_blocking(
            self.device, page_info, length)
        values = page_info[0:length.value]
        return tuple(zip(values[0::2], values[1::2]))

    def get_bootloader_block_sizes(self) -> tuple[int, ...]:
        block_sizes = (c_uint16 * 255)()
        length = c_uint8(255)
        lib.asphodel_get_bootloader_block_sizes_blocking(
            self.device, block_sizes, length)
        return tuple(block_sizes[0:length.value])

    def start_bootloader_page(self, page_number: int,
                              nonce: bytes | bytearray) -> None:
        data = (c_uint8 * len(nonce)).from_buffer_copy(nonce)
        lib.asphodel_start_bootloader_page_blocking(
            self.device, page_number, data, len(nonce))

    def write_bootloader_code_block(self, data: bytes | bytearray) -> None:
        buffer = (c_uint8 * len(data)).from_buffer_copy(data)
        lib.asphodel_write_bootloader_code_block_blocking(
            self.device, buffer, len(data))

    def write_bootloader_page(self, data: bytes | bytearray,
                              block_sizes: Sequence[int]) -> None:
        buffer = (c_uint8 * len(data)).from_buffer_copy(data)
        block_sizes_length = len(block_sizes)
        block_sizes_array = (c_uint16 * block_sizes_length)()
        for i in range(block_sizes_length):
            block_sizes_array[i] = block_sizes[i]
        lib.asphodel_write_bootloader_page_blocking(
            self.device, buffer, len(data), block_sizes_array,
            block_sizes_length)

    def finish_bootloader_page(
            self, mac_tag: bytes | bytearray | None = None) -> None:
        if mac_tag is None:
            mac_tag = b""
        data = (c_uint8 * len(mac_tag)).from_buffer_copy(mac_tag)
        lib.asphodel_finish_bootloader_page_blocking(
            self.device, data, len(mac_tag))

    def verify_bootloader_page(
            self, mac_tag: bytes | bytearray | None = None) -> None:
        if mac_tag is None:
            mac_tag = b""
        data = (c_uint8 * len(mac_tag)).from_buffer_copy(mac_tag)
        lib.asphodel_verify_bootloader_page_blocking(
            self.device, data, len(mac_tag))

    def get_strain_bridge_count(
            self, channel_info: ChannelInfo) -> int:
        count = c_int()
        lib.asphodel_get_strain_bridge_count(channel_info, count)
        return count.value

    def get_strain_bridge_subchannel(self, channel_info: ChannelInfo,
                                     bridge_index: int) -> int:
        subchannel = c_size_t()
        lib.asphodel_get_strain_bridge_subchannel(
            channel_info, bridge_index, subchannel)
        return subchannel.value

    def get_strain_bridge_values(self, channel_info: ChannelInfo,
                                 bridge_index: int) -> BridgeValues:
        array = (c_float * 5)()
        lib.asphodel_get_strain_bridge_values(
            channel_info, bridge_index, array)
        return BridgeValues(*array)

    def set_strain_outputs(self, channel_index: int, bridge_index: int,
                           pos: int, neg: int) -> None:
        lib.asphodel_set_strain_outputs_blocking(self.device, channel_index,
                                                 bridge_index, pos, neg)

    def check_strain_resistances(
            self, channel_info: ChannelInfo, bridge_index: int,
            baseline: float, pos_high: float,
            neg_high: float) -> tuple[bool, float, float]:
        """
        Return (passed, pos_res, neg_res)
        """
        passed = c_int(0)
        pos_res = c_double()
        neg_res = c_double()
        lib.asphodel_check_strain_resistances(
            channel_info, bridge_index, baseline, pos_high, neg_high,
            pos_res, neg_res, passed)
        return (bool(passed.value), pos_res.value, neg_res.value)

    def get_accel_self_test_limits(
            self, channel_info: ChannelInfo) -> SelfTestLimits:
        array = (c_float * 6)()
        lib.asphodel_get_accel_self_test_limits(channel_info, array)
        return SelfTestLimits(*array)

    def enable_accel_self_test(self, channel_index: int,
                               enable: bool = True) -> None:
        lib.asphodel_enable_accel_self_test_blocking(
            self.device, channel_index, enable)

    def check_accel_self_test(
            self, channel_info: ChannelInfo,
            disabled: tuple[float, float, float] | list[float],
            enabled: tuple[float, float, float] | list[float]) -> bool:
        """
        Return passed
        """
        dis_array = (c_double * 3)(*disabled)
        en_array = (c_double * 3)(*enabled)
        passed = c_int(0)
        lib.asphodel_check_accel_self_test(
            channel_info, dis_array, en_array, passed)
        return bool(passed.value)

    def get_setting(self, index: int) -> SettingInfo:
        info = self.get_setting_info(index)
        name = self.get_setting_name(index)
        default = self.get_setting_default(index)
        name_bytes = name.encode("utf-8")
        info._name = name_bytes
        info._name_length = len(name_bytes)

        # the memory needs to be kept around
        info._default_bytes_storage = (c_uint8 * len(default))(*default)
        info._default_bytes = cast(
            info._default_bytes_storage, POINTER(c_uint8))
        info._default_bytes_length = len(default)
        return info

    def get_device_info_raw(
            self, cache: Cache | None = None, flags: int | None = None,
            callback: Callable[[int, int, str],
                               None] | None = None) -> AsphodelDeviceInfo:
        if flags is None:
            flags = 0
        device_info_ptr = POINTER(AsphodelDeviceInfo)()

        cache_internal = cache.cache if cache else None

        if callback:
            def cb(finished: int, total: int, section_name: bytes,
                   closure: c_void_p) -> None:
                try:
                    callback(finished, total, section_name.decode("utf-8"))
                except Exception:
                    pass  # nothing can be done about it here
            c_callback = AsphodelDeviceInfoProgressCallback(cb)
        else:
            c_callback = AsphodelDeviceInfoProgressCallback(0)

        lib.asphodel_get_device_info(
            self.device, cache_internal, flags, device_info_ptr, c_callback,
            None)
        return device_info_ptr.contents

    def get_device_info(
            self, cache: Cache | None = None, flags: int | None = None,
            callback: Callable[[int, int, str],
                               None] | None = None) -> DeviceInfo:
        device_info = self.get_device_info_raw(cache, flags, callback)
        return DeviceInfo.from_struct(device_info)

    @staticmethod
    def find_usb_devices() -> list["Device"]:
        count = c_size_t(0)

        # first get a count of how many devices are on the system:
        lib.asphodel_usb_find_devices(None, count)

        array_size = count.value

        if array_size == 0:
            return []

        array = (POINTER(AsphodelDevice) * array_size)()
        lib.asphodel_usb_find_devices(array, count)

        array_entries = min(array_size, count.value)

        device_list: list[Device] = []
        for i in range(array_entries):
            device_list.append(Device(array[i].contents))
        return device_list

    @staticmethod
    def find_tcp_devices(flags: int | None = None) -> list["Device"]:
        if flags is None:
            flags = TcpFilterFlags.DEFAULT

        # provide an array of 10 for the first attempt
        array_size = 100
        count = c_size_t(array_size)
        array = (POINTER(AsphodelDevice) * array_size)()

        # first try
        lib.asphodel_tcp_find_devices_filter(array, count, flags)

        if count.value > array_size:
            # there are too many devices for the initial array.

            # free the original list
            for i in range(array_size):
                device = array[i].contents
                device.free_device(device)

            array_size = count.value
            array = (POINTER(AsphodelDevice) * array_size)()

            # try again
            lib.asphodel_tcp_find_devices_filter(array, count, flags)

            device_count = min(count.value, array_size)
        else:
            device_count = count.value

        device_list: list[Device] = []
        for i in range(device_count):
            device_list.append(Device(array[i].contents))
        return device_list

    @staticmethod
    def create_tcp_device(host: str, port: int, timeout: int,
                          serial: str | None = None) -> "Device":
        device_ptr = POINTER(AsphodelDevice)()

        if serial:
            serial_bytes = serial.encode("utf-8")
        else:
            serial_bytes = None

        lib.asphodel_tcp_create_device(
            host.encode("utf-8"), port, timeout, serial_bytes, device_ptr)

        return Device(device_ptr.contents)

    @classmethod
    def find_devices(cls) -> list["Device"]:
        usb_devices = cls.find_usb_devices()
        tcp_devices = cls.find_tcp_devices()
        return usb_devices + tcp_devices

    @classmethod
    def find_device_by_serial(cls, serial: str) -> "Device | None":
        for device in cls.find_tcp_devices():
            adv = device.tcp_get_advertisement()
            if adv.serial_number == serial:
                return device

        for device in cls.find_usb_devices():
            try:
                device.open()
                if device.get_serial_number() == serial:
                    return device
            except AsphodelError:
                continue
            finally:
                device.close()

        return None

    @staticmethod
    def create_virtual(device_info: AsphodelDeviceInfo | DeviceInfo,
                       allow_fallback: bool = False) -> "Device":
        if isinstance(device_info, DeviceInfo):
            device_info = device_info._device_info  # pyright: ignore
        device_ptr = POINTER(AsphodelDevice)()
        lib.asphodel_create_virtual_device(
            device_info, None, allow_fallback, device_ptr)
        return Device(device_ptr.contents)
