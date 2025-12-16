from enum import IntEnum, IntFlag, unique


@unique
class UnitType(IntEnum):
    NONE = 0
    LSB = 1
    PERCENT = 2
    VOLT = 3
    AMPERE = 4
    WATT = 5
    OHM = 6
    CELSIUS = 7
    PASCAL = 8
    NEWTON = 9
    M_PER_S = 10
    M_PER_S2 = 11
    DB = 12
    DBM = 13
    STRAIN = 14
    HZ = 15
    SECOND = 16
    LSB_PER_CELSIUS = 17
    GRAM_PER_S = 18
    L_PER_S = 19
    NEWTON_METER = 20
    METER = 21
    GRAM = 22
    M3_PER_S = 23
    VOLT_PER_VOLT = 24


@unique
class ChannelType(IntEnum):
    LINEAR = 0
    NTC = 1
    ARRAY = 2
    SLOW_STRAIN = 3
    FAST_STRAIN = 4
    SLOW_ACCEL = 5
    PACKED_ACCEL = 6
    COMPOSITE_STRAIN = 7
    LINEAR_ACCEL = 8
    BIG_ENDIAN_FLOAT32 = 9
    BIG_ENDIAN_FLOAT64 = 10
    LITTLE_ENDIAN_FLOAT32 = 11
    LITTLE_ENDIAN_FLOAT64 = 12


@unique
class SettingType(IntEnum):
    BYTE = 0
    BOOLEAN = 1
    UNIT_TYPE = 2
    CHANNEL_TYPE = 3
    BYTE_ARRAY = 4
    STRING = 5
    INT32 = 6
    INT32_SCALED = 7
    FLOAT = 8
    FLOAT_ARRAY = 9
    CUSTOM_ENUM = 10


@unique
class GpioPinMode(IntEnum):
    HI_Z = 0
    PULL_DOWN = 1
    PULL_UP = 2
    LOW = 3
    HIGH = 4


@unique
class ProtocolType(IntFlag):
    BASIC = 0x00
    RF_POWER = 0x01
    RADIO = 0x02
    REMOTE = 0x04
    BOOTLOADER = 0x08


@unique
class SpiCsMode(IntEnum):
    LOW = 0
    HIGH = 1
    AUTO_TRANSFER = 2
    AUTO_BYTE = 3


@unique
class SupplyResultFlags(IntFlag):
    LOW_BATTERY = 0x01
    TOO_LOW = 0x02
    TOO_HIGH = 0x04


class TcpFilterFlags(IntFlag):
    DEFAULT = 0x0
    PREFER_IPV6 = 0x0
    PREFER_IPV4 = 0x1
    ONLY_IPV6 = 0x2
    ONLY_IPV4 = 0x3
    RETURN_ALL = 0x4


class DeviceInfoFlags(IntFlag):
    NO_PROTOCOL_VERSION = 1 << 0
    NO_CHIP_INFO = 1 << 1
    NO_BOOTLOADER_INFO = 1 << 2
    NO_RGB_OR_LED_INFO = 1 << 3
    NO_RGB_OR_LED_STATE = 1 << 4
    NO_REPO_DETAIL_INFO = 1 << 5
    NO_STREAM_INFO = 1 << 6
    NO_STREAM_RATE_INFO = 1 << 7
    NO_CHANNEL_INFO = 1 << 8
    NO_CHANNEL_CAL_INFO = 1 << 9
    NO_SUPPLY_INFO = 1 << 10
    NO_SUPPLY_RESULT = 1 << 11
    NO_CTRL_VAR_INFO = 1 << 12
    NO_CTRL_VAR_STATE = 1 << 13
    NO_SETTING_INFO = 1 << 14
    NO_SETTING_CATEGORY_INFO = 1 << 15
    NO_DEVICE_MODE = 1 << 16
    NO_DEVICE_MODE_STATE = 1 << 17
    NO_RF_POWER_INFO = 1 << 18
    NO_RF_POWER_STATE = 1 << 19
    NO_RADIO_INFO = 1 << 20
    NVM_OPTIONAL = 1 << 21
    NO_USER_TAG_INFO = 1 << 22
    NO_UNCACHED = (NO_RGB_OR_LED_STATE |
                   NO_SUPPLY_RESULT |
                   NO_CTRL_VAR_STATE |
                   NO_DEVICE_MODE_STATE |
                   NO_RF_POWER_STATE)
    ACTIVE_SCAN_DEFAULT = 0x3FFFFF
