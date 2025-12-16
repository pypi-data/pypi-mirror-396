const std = @import("std");
const c = @import("root.zig").c;

export fn asphodel_write_setting(device_info: *const c.AsphodelDeviceInfo_t, setting_name: [*:0]const u8, json: [*:0]const u8, nvm_buffer: [*]u8) c_int {
    if (device_info.nvm_size == 0) return c.ASPHODEL_BAD_PARAMETER;

    const parsed: std.json.Parsed(std.json.Value) = std.json.parseFromSlice(std.json.Value, std.heap.c_allocator, std.mem.span(json), .{}) catch {
        return c.ASPHODEL_BAD_PARAMETER;
    };
    defer parsed.deinit();

    if (device_info.setting_count_known == 0) return c.ASPHODEL_NOT_FOUND; // no settings: couldn't find the setting
    if (device_info.setting_count == 0) return c.ASPHODEL_NOT_FOUND; // no settings: couldn't find the setting
    if (device_info.settings) |settings| {
        for (settings[0..device_info.setting_count]) |*setting| {
            if (std.mem.eql(u8, std.mem.span(setting.name), std.mem.span(setting_name))) {
                return writeSetting(
                    device_info,
                    setting,
                    parsed.value,
                    nvm_buffer[0..device_info.nvm_size],
                );
            }
        }
    }

    return c.ASPHODEL_NOT_FOUND; // couldn't find the setting
}

export fn asphodel_write_settings(device_info: *const c.AsphodelDeviceInfo_t, json: [*:0]const u8, nvm_buffer: [*]u8) c_int {
    if (device_info.nvm_size == 0) return c.ASPHODEL_BAD_PARAMETER;
    const nvm_slice = nvm_buffer[0..device_info.nvm_size];

    var parsed: std.json.Parsed(std.json.Value) = std.json.parseFromSlice(std.json.Value, std.heap.c_allocator, std.mem.span(json), .{}) catch {
        return c.ASPHODEL_BAD_PARAMETER;
    };
    defer parsed.deinit();

    var map: *std.json.ObjectMap = switch (parsed.value) {
        .object => |*obj| obj,
        else => return c.ASPHODEL_BAD_PARAMETER,
    };

    if (map.count() == 0) return c.ASPHODEL_SUCCESS; // no settings in the input, bail out early

    if (device_info.setting_count_known == 0) return c.ASPHODEL_NOT_FOUND; // no settings: couldn't find a setting
    if (device_info.setting_count == 0) return c.ASPHODEL_NOT_FOUND; // no settings: couldn't find a setting

    var first_error: ?c_int = null;

    if (device_info.settings) |settings| {
        for (settings[0..device_info.setting_count]) |*setting| {
            const maybe_kv = map.fetchSwapRemove(std.mem.span(setting.name));
            if (maybe_kv) |kv| {
                const ret = writeSetting(device_info, setting, kv.value, nvm_slice);
                if (ret != c.ASPHODEL_SUCCESS) {
                    if (ret == c.ASPHODEL_NOT_FOUND or ret == c.ASPHODEL_INVALID_SETTING_VALUE) {
                        if (first_error == null) {
                            first_error = ret;
                        }
                    } else {
                        // not recoverable
                        return ret;
                    }
                }
            } else {
                // this is fine, the input json isn't setting this setting
            }
        }
    } else {
        return c.ASPHODEL_NOT_FOUND; // no settings in the device info: couldn't find a setting
    }

    // check if we had any errors in the loop
    if (first_error) |err| return err;

    // see if there were any leftover settings
    if (map.count() > 0) return c.ASPHODEL_NOT_FOUND;

    return c.ASPHODEL_SUCCESS;
}

fn writeSetting(device_info: *const c.AsphodelDeviceInfo_t, setting_info: *const c.AsphodelSettingInfo_t, value: std.json.Value, nvm_buffer: []u8) c_int {
    switch (setting_info.setting_type) {
        c.SETTING_TYPE_BYTE => {
            const u = &setting_info.u.byte_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4 + @as(usize, u.nvm_word_byte);
            if (byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_value = switch (value) {
                .integer => |i| std.math.cast(u8, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            nvm_buffer[byte_offset] = byte_value;
        },
        c.SETTING_TYPE_UNIT_TYPE => {
            const u = &setting_info.u.byte_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4 + @as(usize, u.nvm_word_byte);
            if (byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_value = switch (value) {
                .integer => |i| std.math.cast(u8, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                .string => |s| parseUnitType(s) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            nvm_buffer[byte_offset] = byte_value;
        },
        c.SETTING_TYPE_CHANNEL_TYPE => {
            const u = &setting_info.u.byte_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4 + @as(usize, u.nvm_word_byte);
            if (byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_value = switch (value) {
                .integer => |i| std.math.cast(u8, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                .string => |s| parseChannelType(s) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            nvm_buffer[byte_offset] = byte_value;
        },
        c.SETTING_TYPE_BOOLEAN => {
            const u = &setting_info.u.byte_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4 + @as(usize, u.nvm_word_byte);
            if (byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_value: u8 = switch (value) {
                .bool => |b| if (b) 1 else 0,
                .integer => |i| @as(u8, std.math.cast(u1, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE),
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            nvm_buffer[byte_offset] = byte_value;
        },
        c.SETTING_TYPE_BYTE_ARRAY => {
            const u = &setting_info.u.byte_array_setting;
            const length_byte_offset = @as(usize, u.length_nvm_word) * 4 + @as(usize, u.length_nvm_word_byte);
            if (length_byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + u.maximum_length > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;

            const array = switch (value) {
                .array => |array| array,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };

            if (array.items.len > u.maximum_length) return c.ASPHODEL_INVALID_SETTING_VALUE;

            const temp_buffer = std.heap.c_allocator.alloc(u8, array.items.len) catch return c.ASPHODEL_NO_MEM;
            defer std.heap.c_allocator.free(temp_buffer);

            // write the array items
            for (array.items, 0..) |item, index| {
                const byte_value = switch (item) {
                    .integer => |i| std.math.cast(u8, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                    else => return c.ASPHODEL_INVALID_SETTING_VALUE,
                };
                temp_buffer[index] = byte_value;
            }

            // finish
            nvm_buffer[length_byte_offset] = @intCast(array.items.len);
            @memcpy(nvm_buffer[byte_offset .. byte_offset + array.items.len], temp_buffer);
        },
        c.SETTING_TYPE_STRING => {
            const u = &setting_info.u.string_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + u.maximum_length > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const string_value = switch (value) {
                .string => |s| s,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            if (string_value.len > u.maximum_length) return c.ASPHODEL_INVALID_SETTING_VALUE;
            @memcpy(nvm_buffer[byte_offset .. byte_offset + string_value.len], string_value);
            @memset(nvm_buffer[byte_offset + string_value.len .. byte_offset + u.maximum_length], 0);
        },
        c.SETTING_TYPE_INT32 => {
            const u = &setting_info.u.int32_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + 4 > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const i32_value = switch (value) {
                .integer => |i| std.math.cast(i32, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            if (i32_value < u.minimum or i32_value > u.maximum) return c.ASPHODEL_INVALID_SETTING_VALUE;
            std.mem.writeInt(i32, nvm_buffer[byte_offset..][0..4], i32_value, .big);
        },
        c.SETTING_TYPE_INT32_SCALED => {
            const u = &setting_info.u.int32_scaled_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + 4 > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            var f32_value: f32 = switch (value) {
                .float => |f| @floatCast(f),
                .integer => |i| @floatFromInt(i),
                .string => |s| std.fmt.parseFloat(f32, s) catch return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            f32_value = (f32_value - u.offset) / u.scale;
            const i32_value = std.math.lossyCast(i32, @round(f32_value));
            if (i32_value < u.minimum or i32_value > u.maximum) return c.ASPHODEL_INVALID_SETTING_VALUE;
            std.mem.writeInt(i32, nvm_buffer[byte_offset..][0..4], i32_value, .big);
        },
        c.SETTING_TYPE_FLOAT => {
            const u = &setting_info.u.float_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + 4 > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            var f32_value: f32 = switch (value) {
                .float => |f| @floatCast(f),
                .integer => |i| @floatFromInt(i),
                .string => |s| std.fmt.parseFloat(f32, s) catch return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            f32_value = (f32_value - u.offset) / u.scale;
            if (f32_value < u.minimum or f32_value > u.maximum) return c.ASPHODEL_INVALID_SETTING_VALUE;
            std.mem.writeInt(u32, nvm_buffer[byte_offset..][0..4], @as(u32, @bitCast(f32_value)), .big);
        },
        c.SETTING_TYPE_FLOAT_ARRAY => {
            const u = &setting_info.u.float_array_setting;
            const length_byte_offset = @as(usize, u.length_nvm_word) * 4 + @as(usize, u.length_nvm_word_byte);
            if (length_byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            const byte_offset = @as(usize, u.nvm_word) * 4;
            if (byte_offset + @as(usize, u.maximum_length) * 4 > nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;

            const array = switch (value) {
                .array => |array| array,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };

            if (array.items.len > u.maximum_length) return c.ASPHODEL_INVALID_SETTING_VALUE;

            const temp_buffer = std.heap.c_allocator.alloc(f32, array.items.len) catch return c.ASPHODEL_NO_MEM;
            defer std.heap.c_allocator.free(temp_buffer);

            // write the array items
            for (array.items, 0..) |item, index| {
                var f32_value: f32 = switch (item) {
                    .float => |f| @floatCast(f),
                    .integer => |i| @floatFromInt(i),
                    .string => |s| std.fmt.parseFloat(f32, s) catch return c.ASPHODEL_INVALID_SETTING_VALUE,
                    else => return c.ASPHODEL_INVALID_SETTING_VALUE,
                };
                f32_value = (f32_value - u.offset) / u.scale;
                if (f32_value < u.minimum or f32_value > u.maximum) return c.ASPHODEL_INVALID_SETTING_VALUE;
                temp_buffer[index] = f32_value;
            }

            // finish
            nvm_buffer[length_byte_offset] = @intCast(array.items.len);
            for (temp_buffer, 0..) |f32_value, index| {
                std.mem.writeInt(u32, nvm_buffer[byte_offset + index * 4 ..][0..4], @as(u32, @bitCast(f32_value)), .big);
            }
        },
        c.SETTING_TYPE_CUSTOM_ENUM => {
            const u = &setting_info.u.custom_enum_setting;
            const byte_offset = @as(usize, u.nvm_word) * 4 + @as(usize, u.nvm_word_byte);
            if (byte_offset >= nvm_buffer.len) return c.ASPHODEL_BAD_PARAMETER;
            if (device_info.custom_enum_lengths == null or device_info.custom_enum_count <= u.custom_enum_index) return c.ASPHODEL_BAD_PARAMETER;
            const byte_value = switch (value) {
                .integer => |i| parseCustomEnumIndex(device_info, u.custom_enum_index, i) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                .string => |s| parseCustomEnumString(device_info, u.custom_enum_index, s) orelse return c.ASPHODEL_INVALID_SETTING_VALUE,
                else => return c.ASPHODEL_INVALID_SETTING_VALUE,
            };
            nvm_buffer[byte_offset] = byte_value;
        },
        else => return c.ASPHODEL_INVALID_SETTING_VALUE,
    }

    return c.ASPHODEL_SUCCESS;
}

fn parseCustomEnumIndex(device_info: *const c.AsphodelDeviceInfo_t, index: u8, input: i64) ?u8 {
    std.debug.assert(device_info.custom_enum_lengths != null);
    std.debug.assert(device_info.custom_enum_count > index);
    const enum_length = device_info.custom_enum_lengths[index];

    const value = std.math.cast(u8, input) orelse return null;

    if (value >= enum_length) return null;

    return value;
}

fn parseCustomEnumString(device_info: *const c.AsphodelDeviceInfo_t, index: u8, input: []const u8) ?u8 {
    std.debug.assert(device_info.custom_enum_lengths != null);
    std.debug.assert(device_info.custom_enum_count > index);
    const enum_length = device_info.custom_enum_lengths[index];

    if (device_info.custom_enum_values) |custom_enum_values| {
        const maybe_values = custom_enum_values[index];
        if (maybe_values) |values| {
            for (values[0..enum_length], 0..) |value, i| {
                if (std.mem.eql(u8, std.mem.span(value), input)) {
                    return @intCast(i);
                }
            }
        }
    }

    return null; // not found
}

fn parseUnitType(s: []const u8) ?u8 {
    inline for (0..c.UNIT_TYPE_COUNT) |i| {
        const name = c.asphodel_unit_type_name(i);
        if (std.mem.eql(u8, s, std.mem.span(name))) {
            return i;
        }
    }

    return null;
}

test "parseUnitType" {
    try std.testing.expectEqual(c.UNIT_TYPE_VOLT, parseUnitType("UNIT_TYPE_VOLT").?);
    try std.testing.expectEqual(c.UNIT_TYPE_WATT, parseUnitType("UNIT_TYPE_WATT").?);
    try std.testing.expectEqual(null, parseUnitType("UNIT_TYPE_COUNT"));
    try std.testing.expectEqual(null, parseUnitType("INVALID"));
    try std.testing.expectEqual(null, parseUnitType(""));
    try std.testing.expectEqual(null, parseUnitType("CHANNEL_TYPE_NTC"));
}

fn parseChannelType(s: []const u8) ?u8 {
    inline for (0..c.CHANNEL_TYPE_COUNT) |i| {
        const name = c.asphodel_channel_type_name(i);
        if (std.mem.eql(u8, s, std.mem.span(name))) {
            return i;
        }
    }

    return null;
}

test "parseChannelType" {
    try std.testing.expectEqual(c.CHANNEL_TYPE_ARRAY, parseChannelType("CHANNEL_TYPE_ARRAY").?);
    try std.testing.expectEqual(c.CHANNEL_TYPE_NTC, parseChannelType("CHANNEL_TYPE_NTC").?);
    try std.testing.expectEqual(null, parseChannelType("CHANNEL_TYPE_COUNT"));
    try std.testing.expectEqual(null, parseChannelType("INVALID"));
    try std.testing.expectEqual(null, parseChannelType(""));
    try std.testing.expectEqual(null, parseChannelType("UNIT_TYPE_VOLT"));
}
