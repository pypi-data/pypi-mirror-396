import math
import struct
from typing import Any, Optional, Sequence, cast

import asphodel


def find_usb_devices() -> dict[str, asphodel.Device]:
    devices_by_serial: dict[str, asphodel.Device] = {}
    for device in asphodel.Device.find_usb_devices():
        try:
            device.open()
            serial_number = device.get_serial_number()
            devices_by_serial[serial_number] = device
        except asphodel.AsphodelError:
            continue
        finally:
            device.close()
    return devices_by_serial


def find_tcp_devices() -> dict[str, asphodel.Device]:
    devices_by_serial: dict[str, asphodel.Device] = {}
    for device in asphodel.Device.find_tcp_devices():
        adv = device.tcp_get_advertisement()
        serial_number = adv.serial_number
        devices_by_serial[serial_number] = device
    return devices_by_serial


def find_all_devices() -> dict[str, asphodel.Device]:
    devices: dict[str, asphodel.Device] = {}

    if asphodel.usb_devices_supported:
        devices.update(find_usb_devices())

    if asphodel.tcp_devices_supported:
        devices.update(find_tcp_devices())

    if not (asphodel.usb_devices_supported or
            asphodel.tcp_devices_supported):
        # no TCP or USB supported by DLL
        raise Exception("Asphodel library does not support USB or TCP devices")

    return devices


def get_choice(options: Sequence[tuple[Optional[str], str]],
               prompt: Optional[str] = None) -> str:
    if prompt is None:
        prompt = "Selection: "

    choices = set(k for k, _m in options if k is not None)

    d = {c.lower(): c for c in choices}

    while True:
        choice = input(prompt)
        if choice:
            choice = choice.lower()
            if choice in d:
                return d[choice]


def print_options(title: str,
                  options: Sequence[tuple[Optional[str], str]]) -> None:
    max_length = max(len(k) for k, _m in options if k is not None)

    print("")
    print("--- {} ---".format(title))
    for key, message in options:
        if key is not None:
            print("{}  {}".format(key.ljust(max_length), message))
        else:
            print("")
            print("{}  {}:".format(" " * max_length, message))
    print("")


def do_string_setting(setting_name: str, initial_str: str,
                      default_str: str) -> bytes:
    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial_str))
    print("Default setting: {}".format(default_str))
    value = input("New Value: ")
    return value.encode('UTF-8')


def do_integer_setting(setting_name: str, initial: int, default: Optional[int],
                       minimum: int, maximum: int) -> int:
    if minimum > maximum:
        # they're backwards
        maximum, minimum = minimum, maximum

    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial))
    if default is not None:
        print("Default setting: {}".format(default))
    else:
        print("Default setting: invalid")
    prompt = "New Value (range {} to {}): ".format(minimum, maximum)

    while True:
        value_str = input(prompt)
        if value_str:
            try:
                value = int(value_str)
                if minimum <= value <= maximum:
                    return value
            except ValueError:
                continue


def do_float_setting(setting_name: str, initial: float,
                     default: Optional[float], minimum: float,
                     maximum: float) -> float:
    if minimum > maximum:
        # they're backwards
        maximum, minimum = minimum, maximum

    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial))
    if default is not None:
        print("Default setting: {}".format(default))
    else:
        print("Default setting: invalid")
    prompt = "New Value (range {} to {}): ".format(minimum, maximum)

    while True:
        value_str = input(prompt)
        if value_str:
            try:
                value = float(value_str)
                if math.isnan(value):
                    # can't compare to min and max
                    return value
                if minimum <= value <= maximum:
                    return value
            except ValueError:
                continue


def do_choice_setting(setting_name: str, initial: Optional[Any],
                      default: Optional[Any],
                      options: Sequence[tuple[Optional[str], str]]) -> int:
    print_options(setting_name, options)

    for key, name in options:
        if key == str(initial):
            print("Initial setting: {} ({})".format(name, key))
            break
    else:
        print("Initial setting: unknown ({})".format(initial))

    if default is not None:
        for key, name in options:
            if key == str(default):
                print("Default setting: {} ({})".format(name, key))
                break
        else:
            print("Default setting: unknown ({})".format(default))
    else:
        print("Default setting: invalid")

    choice = get_choice(options, "New Value: ")
    return int(choice)


def parse_byte_setting(nvm: bytearray, setting: asphodel.SettingInfo,
                       default_bytes: bytes) -> tuple[int, Optional[int]]:
    s = setting.u.byte_setting
    byte_offset = s.nvm_word * 4 + s.nvm_word_byte
    initial: int = struct.unpack_from(">B", nvm, byte_offset)[0]
    if len(default_bytes) == 1:
        default = default_bytes[0]
    else:
        default = None
    return initial, default


def write_byte_setting(nvm: bytearray, setting: asphodel.SettingInfo,
                       value: int) -> None:
    s = setting.u.byte_setting
    byte_offset = s.nvm_word * 4 + s.nvm_word_byte
    struct.pack_into(">B", nvm, byte_offset, value)


def do_setting(nvm: bytearray, setting: asphodel.SettingInfo,
               custom_enums: dict[int, list[str]]) -> None:
    length = setting.default_bytes_length
    default_bytes = bytes(setting.default_bytes[0:length])
    setting_name = setting.name.decode("utf-8")

    options: list[tuple[str, str]]  # type it now, declare later

    if setting.setting_type == asphodel.SettingType.BYTE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        value_int = do_integer_setting(setting_name, initial, default, 0, 255)
        write_byte_setting(nvm, setting, value_int)
    elif setting.setting_type == asphodel.SettingType.BOOLEAN:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = [
            ("0", "False"),
            ("1", "True")
        ]
        if initial > 1:
            options.append((str(initial), "unknown"))
        value_int = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value_int)
    elif setting.setting_type == asphodel.SettingType.UNIT_TYPE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = []
        for i, name in enumerate(asphodel.unit_type_names):
            options.append((str(i), name))
        if initial >= len(options):
            options.append((str(initial), "unknown"))
        value_int = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value_int)
    elif setting.setting_type == asphodel.SettingType.CHANNEL_TYPE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = []
        for i, name in enumerate(asphodel.channel_type_names):
            options.append((str(i), name))
        if initial >= len(options):
            options.append((str(initial), "unknown"))
        value_int = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value_int)
    elif setting.setting_type == asphodel.SettingType.STRING:
        s_str = setting.u.string_setting
        fmt = ">{}s".format(s_str.maximum_length)
        raw: bytes = struct.unpack_from(fmt, nvm, s_str.nvm_word * 4)[0]
        raw = raw.split(b'\x00', 1)[0]
        raw = raw.split(b'\xff', 1)[0]
        try:
            initial_str = raw.decode("utf-8")
        except UnicodeDecodeError:
            initial_str = "<ERROR>"
        try:
            default_str = default_bytes.decode("utf-8")
        except UnicodeDecodeError:
            default_str = "unknown"
        value_bytes = do_string_setting(setting_name, initial_str, default_str)
        struct.pack_into(fmt, nvm, s_str.nvm_word * 4, value_bytes)
    elif setting.setting_type == asphodel.SettingType.INT32:
        s_int = setting.u.int32_setting
        initial = cast(
            int, struct.unpack_from(">i", nvm, s_int.nvm_word * 4)[0])
        if len(default_bytes) == 4:
            default = cast(
                int, struct.unpack_from(">i", default_bytes, 0)[0])
        else:
            default = None
        value_int = do_integer_setting(setting_name, initial, default,
                                       s_int.minimum, s_int.maximum)
        struct.pack_into(">i", nvm, s_int.nvm_word * 4, value_int)
    elif setting.setting_type == asphodel.SettingType.INT32_SCALED:
        s_scaled = setting.u.int32_scaled_setting
        scaled_min = s_scaled.minimum * s_scaled.scale + s_scaled.offset
        scaled_max = s_scaled.maximum * s_scaled.scale + s_scaled.offset
        initial = cast(
            int, struct.unpack_from(">i", nvm, s_scaled.nvm_word * 4)[0])
        initial_float = initial * s_scaled.scale + s_scaled.offset
        if len(default_bytes) == 4:
            default = cast(int, struct.unpack_from(">i", default_bytes, 0)[0])
            default_float = default * s_scaled.scale + s_scaled.offset
        else:
            default_float = None
        value_float = do_float_setting(setting_name, initial_float,
                                       default_float, scaled_min, scaled_max)
        unscaled_value = int(round((value_float - s_scaled.offset) /
                                   s_scaled.scale))
        unscaled_value = max(unscaled_value, s_scaled.minimum)
        unscaled_value = min(unscaled_value, s_scaled.maximum)
        struct.pack_into(">i", nvm, s_scaled.nvm_word * 4, unscaled_value)
    elif setting.setting_type == asphodel.SettingType.FLOAT:
        s_float = setting.u.float_setting
        scaled_min = s_float.minimum * s_float.scale + s_float.offset
        scaled_max = s_float.maximum * s_float.scale + s_float.offset
        initial_float = cast(
            float, struct.unpack_from(">f", nvm, s_float.nvm_word * 4)[0])
        initial_float = initial_float * s_float.scale + s_float.offset
        if len(default_bytes) == 4:
            default_float = cast(
                float, struct.unpack_from(">f", default_bytes, 0)[0])
            default_float = default_float * s_float.scale + s_float.offset
        else:
            default_float = None
        value_float = do_float_setting(
            setting_name, initial_float, default_float, scaled_min, scaled_max)
        unscaled_float = (value_float - s_float.offset) / s_float.scale
        struct.pack_into(">f", nvm, s_float.nvm_word * 4, unscaled_float)
    elif setting.setting_type == asphodel.SettingType.CUSTOM_ENUM:
        s_enum = setting.u.custom_enum_setting
        byte_offset = s_enum.nvm_word * 4 + s_enum.nvm_word_byte
        initial = struct.unpack_from(">B", nvm, byte_offset)[0]
        if len(default_bytes) == 1:
            default = default_bytes[0]
        else:
            default = None
        if s_enum.custom_enum_index >= len(custom_enums):
            # invalid index
            value_int = do_integer_setting(
                setting_name, initial, default, 0, 255)
        else:
            options = []
            for i, name in enumerate(custom_enums[s_enum.custom_enum_index]):
                options.append((str(i), name))
            if initial >= len(options):
                options.append((str(initial), "unknown"))
            value_int = do_choice_setting(
                setting_name, initial, default, options)
        struct.pack_into(">B", nvm, byte_offset, value_int)
    else:
        # Note SETTING_TYPE_BYTE_ARRAY and SETTING_TYPE_FLOAT_ARRAY are not
        # supported by this utility as they're not actually used in any devices
        # at the time of this writing
        print("Unsupported setting type!")


def reset_and_reconnect(device: asphodel.Device) -> None:
    device.reset()
    device.reconnect()


def do_device_menu(device: asphodel.Device) -> None:
    device.open()
    sn = device.get_serial_number()
    title = "{} Menu".format(sn)

    setting_count = device.get_setting_count()
    settings = [device.get_setting(i) for i in range(setting_count)]
    unassigned_setting_ids = set(range(setting_count))

    setting_category_count = device.get_setting_category_count()
    setting_categories: list[tuple[str, tuple[int, ...]]] = []
    for i in range(setting_category_count):
        name = device.get_setting_category_name(i)
        category_settings = device.get_setting_category_settings(i)
        setting_categories.append((name, category_settings))
        for setting_id in category_settings:
            unassigned_setting_ids.discard(setting_id)

    custom_enum_counts = device.get_custom_enum_counts()
    custom_enums: dict[int, list[str]] = {}
    for i, count in enumerate(custom_enum_counts):
        custom_enums[i] = [device.get_custom_enum_value_name(i, v)
                           for v in range(count)]

    nvm_size = device.get_nvm_size()
    nvm = bytearray(device.read_nvm_section(0, nvm_size))

    options: list[tuple[Optional[str], str]] = [
        ('p', "Print NVM"),
        ('w', "Write NVM and reset device"),
        ('a', "Abort without saving"),
    ]

    if (unassigned_setting_ids):
        options.append((None, "Device Settings"))
        for setting_id in sorted(unassigned_setting_ids):
            setting_name = settings[setting_id].name.decode("utf-8")
            options.append((str(setting_id), setting_name))
    for category_name, category_settings in setting_categories:
        options.append((None, category_name))
        for setting_id in category_settings:
            setting_name = settings[setting_id].name.decode("utf-8")
            options.append((str(setting_id), setting_name))

    while True:
        print_options(title, options)
        choice = get_choice(options)

        if choice == 'p':
            print("")
            for line in asphodel.format_nvm_data(nvm):
                print(line)
        elif choice == 'a':
            device.close()
            return
        elif choice == 'w':
            device.erase_nvm()
            device.write_nvm_section(0, nvm)
            reset_and_reconnect(device)
            device.close()
            return
        else:
            setting_id = int(choice)
            do_setting(nvm, settings[setting_id], custom_enums)


def do_main_menu(devices: dict[str, asphodel.Device]) -> None:
    while True:
        options: list[tuple[Optional[str], str]] = [
            ('r', "Rescan devices"),
            ('q', "Quit"),
        ]

        if not devices:
            options.append((None, "No Devices"))
        else:
            options.append((None, "Devices"))
            for sn in devices.keys():
                options.append((sn, "Edit device {}".format(sn)))

        print_options("Main Menu", options)
        choice = get_choice(options)

        if choice == 'r':
            devices = find_all_devices()
        elif choice == 'q':
            return
        else:
            do_device_menu(devices[choice])


def main() -> None:
    devices = find_all_devices()
    do_main_menu(devices)


if __name__ == "__main__":
    main()
