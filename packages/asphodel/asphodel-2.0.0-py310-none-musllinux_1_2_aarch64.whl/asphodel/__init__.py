import string

from .cache import Cache
from .clib import (AsphodelChannelDecoder, AsphodelDevice,
                   AsphodelDeviceDecoder, AsphodelDeviceInfo, AsphodelError,
                   AsphodelStreamDecoder, AsphodelTCPAdvInfo,
                   AsphodelUnitFormatter, AsphodelVirtualDeviceCallbacks,
                   ByteArraySetting, ByteSetting, ChannelCalibration,
                   ChannelInfo, CtrlVarInfo, CustomEnumSetting,
                   ExtraScanResult, FloatArraySetting, FloatSetting,
                   GPIOPortInfo, Int32ScaledSetting, Int32Setting, SettingInfo,
                   SettingUnion, StreamAndChannels, StreamInfo, StreamRateInfo,
                   StringSetting, SupplyInfo, SupplyResult, channel_type_names,
                   lib, missing_funcs, setting_type_names,
                   tcp_devices_supported, unit_type_names,
                   usb_devices_supported)
from .decoder import (ChannelDecoder, DeviceDecoder, StreamDecoder,
                      get_streaming_counts)
from .device import (BridgeValues, Device, PartialChannelInfo,
                     PartialCtrlVarInfo, PartialGPIOPortInfo,
                     PartialStreamInfo, PartialSupplyInfo, SelfTestLimits,
                     TCPAdvInfo)
from .device_info import DeviceInfo
from .enums import (ChannelType, DeviceInfoFlags, GpioPinMode, ProtocolType,
                    SettingType, SpiCsMode, SupplyResultFlags, TcpFilterFlags,
                    UnitType)
from .unit_formatter import (UnitFormatter, create_custom_unit_formatter,
                             create_unit_formatter, format_value_ascii,
                             format_value_html, format_value_utf8,
                             get_channel_unit_formatter,
                             get_ctrl_var_unit_formatter)

try:
    from .version import version as __version__
except ImportError:
    __version__ = "UNKNOWN"


def format_nvm_data(data: bytes, size: int = 16) -> list[str]:
    def to_ascii(input: int) -> str:
        c = chr(input)
        if c in string.whitespace:
            return " "
        elif c in string.printable:
            return c
        else:
            return '.'
    output: list[str] = []
    for i in range(0, len(data), size):
        data_chunk = data[i:min(len(data), i + size)]
        hex_values = " ".join(map("{:02x}".format, data_chunk))
        filler = "   " * (size - len(data_chunk))
        ascii_values = "".join(map(to_ascii, data_chunk))
        output.append(hex_values + filler + " " + ascii_values)
    return output


# get library version strings
protocol_version: int = lib.asphodel_get_library_protocol_version()
protocol_version_string: str = \
    lib.asphodel_get_library_protocol_version_string()
build_info: str = lib.asphodel_get_library_build_info()
build_date: str = lib.asphodel_get_library_build_date()
try:
    usb_backend_version: str = lib.asphodel_usb_get_backend_version()
except Exception:
    usb_backend_version = "<UNKNOWN>"

error_name = lib.asphodel_error_name

__all__ = [
    "build_date",
    "build_info",
    "error_name",
    "format_nvm_data",
    "protocol_version",
    "protocol_version_string",
    "usb_backend_version",

    "AsphodelChannelDecoder",
    "AsphodelDevice",
    "AsphodelDeviceDecoder",
    "AsphodelDeviceInfo",
    "AsphodelError",
    "AsphodelStreamDecoder",
    "AsphodelTCPAdvInfo",
    "AsphodelUnitFormatter",
    "AsphodelVirtualDeviceCallbacks",
    "ByteArraySetting",
    "ByteSetting",
    "channel_type_names",
    "ChannelCalibration",
    "ChannelInfo",
    "CtrlVarInfo",
    "CustomEnumSetting",
    "ExtraScanResult",
    "FloatArraySetting",
    "FloatSetting",
    "GPIOPortInfo",
    "Int32ScaledSetting",
    "Int32Setting",
    "lib",
    "missing_funcs",
    "setting_type_names",
    "SettingInfo",
    "SettingUnion",
    "StreamAndChannels",
    "StreamInfo",
    "StreamRateInfo",
    "StringSetting",
    "SupplyInfo",
    "SupplyResult",
    "tcp_devices_supported",
    "unit_type_names",
    "usb_devices_supported",

    "Cache",

    "ChannelDecoder",
    "StreamDecoder",
    "DeviceDecoder",
    "get_streaming_counts",

    "BridgeValues",
    "PartialCtrlVarInfo",
    "Device",
    "PartialGPIOPortInfo",
    "PartialChannelInfo",
    "PartialStreamInfo",
    "SelfTestLimits",
    "PartialSupplyInfo",
    "TCPAdvInfo",

    "DeviceInfo",

    "DeviceInfoFlags",
    "GpioPinMode",
    "ProtocolType",
    "SpiCsMode",
    "SupplyResultFlags",
    "TcpFilterFlags",
    "UnitType",
    "ChannelType",
    "SettingType",

    "create_custom_unit_formatter",
    "create_unit_formatter",
    "format_value_ascii",
    "format_value_utf8",
    "format_value_html",
    "get_channel_unit_formatter",
    "get_ctrl_var_unit_formatter",
    "UnitFormatter",

    "__version__",
]
