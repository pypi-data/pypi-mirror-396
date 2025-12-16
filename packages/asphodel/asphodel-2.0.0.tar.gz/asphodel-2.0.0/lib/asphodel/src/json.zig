const std = @import("std");
const ReturnedDeviceInfo = @import("root.zig").device_info.ReturnedDeviceInfo;
const free_device_info = @import("root.zig").device_info.free_device_info;
const c = @import("root.zig").c;
const Allocator = std.mem.Allocator;

// NB: this entire file is meant to interoperate with the JSON format established by the python implementation.
// To maintain backwards compatibility with both readers and writers the format can't be changed.
// I would definitely change the format if I could, but thankfully users won't have to deal with it directly.

export fn asphodel_get_device_info_from_json(json: [*:0]const u8, device_info_out: **c.AsphodelDeviceInfo_t, excess_out: ?*[*:0]const u8) c_int {
    var returned_device_info = std.heap.c_allocator.create(ReturnedDeviceInfo) catch return c.ASPHODEL_NO_MEM;
    returned_device_info.arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator); // use the raw, as it's faster and safe with arenas
    var device_info = &returned_device_info.device_info;
    device_info.* = c.AsphodelDeviceInfo_t{}; // initialize to safe defaults
    device_info.free_device_info = free_device_info;

    // NOTE: can't use errdefer here, because we need to return asphodel error codes

    var excess: []const u8 = undefined;
    const excess_ptr = if (excess_out) |_| &excess else null;

    fillDeviceInfoFromJson(returned_device_info.arena.allocator(), std.mem.span(json), device_info, excess_ptr) catch |err| {
        returned_device_info.arena.deinit();
        std.heap.c_allocator.destroy(returned_device_info);
        switch (err) {
            error.OutOfMemory => return c.ASPHODEL_NO_MEM,
            else => return c.ASPHODEL_BAD_PARAMETER,
        }
    };

    if (excess_out) |e| {
        const duplicate = std.heap.c_allocator.dupeZ(u8, excess) catch {
            returned_device_info.arena.deinit();
            std.heap.c_allocator.destroy(returned_device_info);
            return c.ASPHODEL_NO_MEM;
        };
        e.* = duplicate.ptr;
    }

    device_info_out.* = device_info;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_get_json_from_device_info(device_info: *const c.AsphodelDeviceInfo_t, json_out: *[*:0]const u8) c_int {
    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
    defer arena.deinit();

    const json = createJsonFromDeviceInfo(arena.allocator(), device_info, .{ .include_version = true }) catch {
        return c.ASPHODEL_NO_MEM;
    };

    const duplicate = std.heap.c_allocator.dupeZ(u8, json) catch {
        return c.ASPHODEL_NO_MEM;
    };

    json_out.* = duplicate.ptr;

    return c.ASPHODEL_SUCCESS;
}

const ReturnedStreamInfo = struct {
    arena: std.heap.ArenaAllocator,
    info: c.AsphodelStreamInfo_t,
};

const ReturnedChannelInfo = struct {
    arena: std.heap.ArenaAllocator,
    info: c.AsphodelChannelInfo_t,
};

const ReturnedSettingInfo = struct {
    arena: std.heap.ArenaAllocator,
    info: c.AsphodelSettingInfo_t,
};

export fn asphodel_get_stream_info_from_json(json: [*:0]const u8, stream_info_out: **c.AsphodelStreamInfo_t) c_int {
    var returned = std.heap.c_allocator.create(ReturnedStreamInfo) catch return c.ASPHODEL_NO_MEM;
    returned.arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator); // use the raw, as it's faster and safe with arenas
    const allocator = returned.arena.allocator();

    var parsed = std.json.parseFromSliceLeaky(std.json.Value, allocator, std.mem.span(json), .{ .allocate = .alloc_if_needed }) catch |err| {
        returned.arena.deinit();
        std.heap.c_allocator.destroy(returned);
        switch (err) {
            error.OutOfMemory => return c.ASPHODEL_NO_MEM,
            else => return c.ASPHODEL_BAD_PARAMETER,
        }
    };

    switch (parsed) {
        .object => |*object| {
            readStream(allocator, object, &returned.info) catch |err| {
                returned.arena.deinit();
                std.heap.c_allocator.destroy(returned);
                switch (err) {
                    error.OutOfMemory => return c.ASPHODEL_NO_MEM,
                    else => return c.ASPHODEL_BAD_PARAMETER,
                }
            };
        },
        else => {
            returned.arena.deinit();
            std.heap.c_allocator.destroy(returned);
            return c.ASPHODEL_BAD_PARAMETER;
        },
    }

    stream_info_out.* = &returned.info;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_get_channel_info_from_json(json: [*:0]const u8, channel_info_out: **c.AsphodelChannelInfo_t) c_int {
    var returned = std.heap.c_allocator.create(ReturnedChannelInfo) catch return c.ASPHODEL_NO_MEM;
    returned.arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator); // use the raw, as it's faster and safe with arenas
    const allocator = returned.arena.allocator();

    var parsed = std.json.parseFromSliceLeaky(std.json.Value, allocator, std.mem.span(json), .{ .allocate = .alloc_if_needed }) catch |err| {
        returned.arena.deinit();
        std.heap.c_allocator.destroy(returned);
        switch (err) {
            error.OutOfMemory => return c.ASPHODEL_NO_MEM,
            else => return c.ASPHODEL_BAD_PARAMETER,
        }
    };

    switch (parsed) {
        .object => |*object| {
            readChannel(allocator, object, &returned.info) catch |err| {
                returned.arena.deinit();
                std.heap.c_allocator.destroy(returned);
                switch (err) {
                    error.OutOfMemory => return c.ASPHODEL_NO_MEM,
                    else => return c.ASPHODEL_BAD_PARAMETER,
                }
            };
        },
        else => {
            returned.arena.deinit();
            std.heap.c_allocator.destroy(returned);
            return c.ASPHODEL_BAD_PARAMETER;
        },
    }

    channel_info_out.* = &returned.info;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_get_setting_info_from_json(json: [*:0]const u8, setting_info_out: **c.AsphodelSettingInfo_t) c_int {
    var returned = std.heap.c_allocator.create(ReturnedSettingInfo) catch return c.ASPHODEL_NO_MEM;
    returned.arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator); // use the raw, as it's faster and safe with arenas
    const allocator = returned.arena.allocator();

    const parsed = std.json.parseFromSliceLeaky([]const u8, allocator, std.mem.span(json), .{ .allocate = .alloc_if_needed }) catch |err| {
        returned.arena.deinit();
        std.heap.c_allocator.destroy(returned);
        switch (err) {
            error.OutOfMemory => return c.ASPHODEL_NO_MEM,
            else => return c.ASPHODEL_BAD_PARAMETER,
        }
    };

    readSetting(allocator, parsed, &returned.info) catch |err| {
        returned.arena.deinit();
        std.heap.c_allocator.destroy(returned);
        switch (err) {
            error.OutOfMemory => return c.ASPHODEL_NO_MEM,
            else => return c.ASPHODEL_BAD_PARAMETER,
        }
    };

    setting_info_out.* = &returned.info;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_free_json_stream(stream_info: *c.AsphodelStreamInfo_t) void {
    const returned: *ReturnedStreamInfo = @fieldParentPtr("info", stream_info);
    returned.arena.deinit();
    std.heap.c_allocator.destroy(returned);
}

export fn asphodel_free_json_channel(channel_info: *c.AsphodelChannelInfo_t) void {
    const returned: *ReturnedChannelInfo = @fieldParentPtr("info", channel_info);
    returned.arena.deinit();
    std.heap.c_allocator.destroy(returned);
}

export fn asphodel_free_json_setting(setting_info: *c.AsphodelSettingInfo_t) void {
    const returned: *ReturnedSettingInfo = @fieldParentPtr("info", setting_info);
    returned.arena.deinit();
    std.heap.c_allocator.destroy(returned);
}

export fn asphodel_get_json_from_stream_info(stream_info: *const c.AsphodelStreamInfo_t, json_out: *[*:0]const u8) c_int {
    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var out: std.io.Writer.Allocating = .init(allocator);
    var write_stream: std.json.Stringify = .{ .writer = &out.writer };

    writeStream(&write_stream, stream_info) catch return c.ASPHODEL_NO_MEM;
    const json = out.toOwnedSlice() catch return c.ASPHODEL_NO_MEM;
    const duplicate = std.heap.c_allocator.dupeZ(u8, json) catch return c.ASPHODEL_NO_MEM;

    json_out.* = duplicate.ptr;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_get_json_from_channel_info(channel_info: *const c.AsphodelChannelInfo_t, json_out: *[*:0]const u8) c_int {
    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var out: std.io.Writer.Allocating = .init(allocator);
    var write_stream: std.json.Stringify = .{ .writer = &out.writer };

    writeChannel(&write_stream, channel_info) catch return c.ASPHODEL_NO_MEM;
    const json = out.toOwnedSlice() catch return c.ASPHODEL_NO_MEM;
    const duplicate = std.heap.c_allocator.dupeZ(u8, json) catch return c.ASPHODEL_NO_MEM;

    json_out.* = duplicate.ptr;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_get_json_from_setting_info(setting_info: *const c.AsphodelSettingInfo_t, json_out: *[*:0]const u8) c_int {
    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    var out: std.io.Writer.Allocating = .init(allocator);
    var write_stream: std.json.Stringify = .{ .writer = &out.writer };

    writeSetting(&write_stream, setting_info) catch return c.ASPHODEL_NO_MEM;
    const json = out.toOwnedSlice() catch return c.ASPHODEL_NO_MEM;
    const duplicate = std.heap.c_allocator.dupeZ(u8, json) catch return c.ASPHODEL_NO_MEM;

    json_out.* = duplicate.ptr;

    return c.ASPHODEL_SUCCESS;
}

export fn asphodel_free_string(str: ?[*:0]const u8) void {
    if (str) |j| {
        std.heap.c_allocator.free(std.mem.span(j));
    }
}

pub const Options = struct {
    json_options: std.json.Stringify.Options = .{},
    include_version: bool = false,
    exclude_nvm: bool = false, // used for creating strings for the cache
};

pub fn createJsonFromDeviceInfo(allocator: Allocator, device_info: *const c.AsphodelDeviceInfo_t, options: Options) ![:0]u8 {
    var out: std.io.Writer.Allocating = .init(allocator);
    var write_stream: std.json.Stringify = .{
        .writer = &out.writer,
        .options = options.json_options,
    };

    try write_stream.beginObject();

    if (device_info.serial_number) |serial_number| {
        try write_stream.objectField("serial_number");
        try write_stream.write(@as([*:0]const u8, serial_number));
    }

    if (device_info.location_string) |location_string| {
        try write_stream.objectField("location_string");
        try write_stream.write(@as([*:0]const u8, location_string));
    }

    if (device_info.max_incoming_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("max_incoming_param_length");
        try write_stream.write(device_info.max_incoming_param_length);
    }

    if (device_info.max_outgoing_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("max_outgoing_param_length");
        try write_stream.write(device_info.max_outgoing_param_length);
    }

    if (device_info.stream_packet_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("stream_packet_length");
        try write_stream.write(device_info.stream_packet_length);
    }

    if (device_info.remote_max_incoming_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("remote_max_incoming_param_length");
        try write_stream.write(device_info.remote_max_incoming_param_length);
    }

    if (device_info.remote_max_outgoing_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("remote_max_outgoing_param_length");
        try write_stream.write(device_info.remote_max_outgoing_param_length);
    }

    if (device_info.remote_stream_packet_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try write_stream.objectField("remote_stream_packet_length");
        try write_stream.write(device_info.remote_stream_packet_length);
    }

    try write_stream.objectField("supports_bootloader");
    try write_stream.write(device_info.supports_bootloader != 0);

    try write_stream.objectField("supports_radio");
    try write_stream.write(device_info.supports_radio != 0);

    try write_stream.objectField("supports_remote");
    try write_stream.write(device_info.supports_remote != 0);

    try write_stream.objectField("supports_rf_power");
    try write_stream.write(device_info.supports_rf_power != 0);

    if (device_info.build_date) |build_date| {
        try write_stream.objectField("build_date");
        try write_stream.write(@as([*:0]const u8, build_date));
    }

    if (device_info.build_info) |build_info| {
        try write_stream.objectField("build_info");
        try write_stream.write(@as([*:0]const u8, build_info));
    }

    if (device_info.nvm_hash) |nvm_hash| {
        try write_stream.objectField("nvm_hash");
        try write_stream.write(@as([*:0]const u8, nvm_hash));
    }

    if (device_info.nvm_modified) |nvm_modified| {
        try write_stream.objectField("nvm_modified");
        try write_stream.write(nvm_modified.* != 0);
    }

    if (device_info.setting_hash) |setting_hash| {
        try write_stream.objectField("setting_hash");
        try write_stream.write(@as([*:0]const u8, setting_hash));
    }

    if (device_info.board_info_name) |board_info_name| {
        try write_stream.objectField("board_info");
        try write_stream.beginArray();
        try write_stream.write(@as([*:0]const u8, board_info_name));
        try write_stream.write(device_info.board_info_rev);
        try write_stream.endArray();
    }

    if (device_info.protocol_version) |protocol_version| {
        try write_stream.objectField("protocol_version");
        try write_stream.write(@as([*:0]const u8, protocol_version));
    }

    if (device_info.chip_family) |chip_family| {
        try write_stream.objectField("chip_family");
        try write_stream.write(@as([*:0]const u8, chip_family));
    }

    if (device_info.chip_id) |chip_id| {
        try write_stream.objectField("chip_id");
        try write_stream.write(@as([*:0]const u8, chip_id));
    }

    if (device_info.chip_model) |chip_model| {
        try write_stream.objectField("chip_model");
        try write_stream.write(@as([*:0]const u8, chip_model));
    }

    if (device_info.bootloader_info) |bootloader_info| {
        try write_stream.objectField("bootloader_info");
        try write_stream.write(@as([*:0]const u8, bootloader_info));
    }

    if (device_info.rgb_count_known != 0) {
        try write_stream.objectField("rgb_settings");
        try write_stream.beginArray();
        for (0..device_info.rgb_count) |i| {
            if (device_info.rgb_settings != null) {
                try write_stream.beginArray();
                try write_stream.write(device_info.rgb_settings[i][0]);
                try write_stream.write(device_info.rgb_settings[i][1]);
                try write_stream.write(device_info.rgb_settings[i][2]);
                try write_stream.endArray();
            } else {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();
    }

    if (device_info.led_count_known != 0) {
        try write_stream.objectField("led_settings");
        try write_stream.beginArray();
        for (0..device_info.led_count) |i| {
            if (device_info.led_settings != null) {
                try write_stream.write(device_info.led_settings[i]);
            } else {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();
    }

    if (device_info.commit_id) |commit_id| {
        try write_stream.objectField("commit_id");
        try write_stream.write(@as([*:0]const u8, commit_id));
    }

    if (device_info.repo_branch) |repo_branch| {
        try write_stream.objectField("repo_branch");
        try write_stream.write(@as([*:0]const u8, repo_branch));
    }

    if (device_info.repo_name) |repo_name| {
        try write_stream.objectField("repo_name");
        try write_stream.write(@as([*:0]const u8, repo_name));
    }

    if (device_info.stream_count_known != 0) {
        try write_stream.objectField("stream_filler_bits");
        try write_stream.write(device_info.stream_filler_bits);
        try write_stream.objectField("stream_id_bits");
        try write_stream.write(device_info.stream_id_bits);

        try write_stream.objectField("streams");
        try write_stream.beginArray();
        if (@as(?[*]c.AsphodelStreamInfo_t, device_info.streams)) |streams| {
            for (0..device_info.stream_count) |i| {
                try writeStream(&write_stream, &streams[i]);
            }
        } else {
            for (0..device_info.stream_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();

        if (@as(?[*]c.AsphodelStreamRateInfo_t, device_info.stream_rates)) |stream_rates| {
            try write_stream.objectField("stream_rate_info");
            try write_stream.beginArray();
            for (0..device_info.stream_count) |i| {
                try writeStreamRate(&write_stream, &stream_rates[i]);
            }
            try write_stream.endArray();
        }
    }

    if (device_info.channel_count_known != 0) {
        try write_stream.objectField("channels");
        try write_stream.beginArray();
        if (@as(?[*]c.AsphodelChannelInfo_t, device_info.channels)) |channels| {
            for (0..device_info.channel_count) |i| {
                try writeChannel(&write_stream, &channels[i]);
            }
        } else {
            for (0..device_info.channel_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();

        if (@as(?[*]?*c.AsphodelChannelCalibration_t, device_info.channel_calibrations)) |channel_calibrations| {
            try write_stream.objectField("channel_calibration");
            try write_stream.beginArray();
            for (0..device_info.channel_count) |i| {
                if (channel_calibrations[i]) |channel_calibration| {
                    try writeChannelCalibration(&write_stream, channel_calibration);
                } else {
                    try write_stream.write(@as(?u8, null));
                }
            }
            try write_stream.endArray();
        }
    }

    if (device_info.supply_count_known != 0) {
        try write_stream.objectField("supplies");
        try write_stream.beginArray();
        if (@as(?[*]c.AsphodelSupplyInfo_t, device_info.supplies)) |supplies| {
            for (0..device_info.supply_count) |i| {
                try writeSupply(&write_stream, &supplies[i]);
            }
        } else {
            for (0..device_info.supply_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();

        if (@as(?[*]c.AsphodelSupplyResult_t, device_info.supply_results)) |supply_results| {
            try write_stream.objectField("supply_results");
            try write_stream.beginArray();
            for (0..device_info.supply_count) |i| {
                try writeSupplyResult(&write_stream, &supply_results[i]);
            }
            try write_stream.endArray();
        }
    }

    if (device_info.ctrl_var_count_known != 0) {
        try write_stream.objectField("ctrl_vars");
        try write_stream.beginArray();
        if (@as(?[*]c.AsphodelCtrlVarInfo_t, device_info.ctrl_vars)) |ctrl_vars| {
            for (0..device_info.ctrl_var_count) |i| {
                const state: ?i32 = if (device_info.ctrl_var_states) |states| states[i] else null;
                try writeCtrlVarInfo(&write_stream, &ctrl_vars[i], state);
            }
        } else {
            for (0..device_info.ctrl_var_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }

        try write_stream.endArray();
    }

    if (device_info.setting_count_known != 0) {
        try write_stream.objectField("settings");
        try write_stream.beginArray();
        if (@as(?[*]c.AsphodelSettingInfo_t, device_info.settings)) |settings| {
            for (0..device_info.setting_count) |i| {
                try writeSetting(&write_stream, &settings[i]);
            }
        } else {
            for (0..device_info.setting_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }

        try write_stream.endArray();
    }

    if (@as(?[*]u8, device_info.custom_enum_lengths)) |custom_enum_lengths| {
        try write_stream.objectField("custom_enums");
        try write_stream.beginObject();
        for (0..device_info.custom_enum_count) |i| {
            try write_stream.beginObjectFieldRaw();
            try write_stream.writer.print("\"{d}\"", .{i});
            write_stream.endObjectFieldRaw();

            const length: u8 = custom_enum_lengths[i];
            const values: ?[*]?[*:0]const u8 = if (device_info.custom_enum_values) |values| values[i] else null;
            try write_stream.beginArray();
            for (0..length) |j| {
                if (values) |v| {
                    try write_stream.write(v[j]);
                } else {
                    try write_stream.write(@as(?u8, null));
                }
            }
            try write_stream.endArray();
        }
        try write_stream.endObject();
    }

    if (device_info.setting_category_count_known != 0) {
        try write_stream.objectField("setting_categories");
        try write_stream.beginArray();
        for (0..device_info.setting_category_count) |i| {
            const name: ?[*:0]const u8 = if (device_info.setting_category_names) |names| names[i] else null;
            const settings: ?[*]u8 = if (device_info.setting_category_settings) |settings| settings[i] else null;
            const length: u8 = if (device_info.setting_category_settings_lengths) |lengths| lengths[i] else 0;

            try write_stream.beginArray();
            try write_stream.write(name);
            if (settings) |s| {
                try write_stream.beginArray();
                for (0..length) |j| {
                    try write_stream.write(s[j]);
                }
                try write_stream.endArray();
            } else {
                try write_stream.write(@as(?u8, null));
            }
            try write_stream.endArray();
        }

        try write_stream.endArray();
    }

    if (device_info.supports_device_mode) |supports_device_mode| {
        try write_stream.objectField("supports_device_mode");
        try write_stream.write(supports_device_mode.* != 0);

        try write_stream.objectField("device_mode");
        if (supports_device_mode.* != 0) {
            try write_stream.write(device_info.device_mode);
        } else {
            try write_stream.write(@as(?u8, null));
        }
    }

    if (device_info.rf_power_ctrl_var_count_known != 0) {
        try write_stream.objectField("rf_power_ctrl_vars");
        try write_stream.beginArray();
        if (@as(?[*]u8, device_info.rf_power_ctrl_vars)) |ctrl_var_indexes| {
            for (0..device_info.rf_power_ctrl_var_count) |i| {
                try write_stream.write(ctrl_var_indexes[i]);
            }
        } else {
            for (0..device_info.rf_power_ctrl_var_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();
    }

    if (device_info.supports_rf_power != 0) {
        try write_stream.objectField("rf_power_status");
        try write_stream.write(device_info.rf_power_enabled != 0);
    }

    if (device_info.radio_ctrl_var_count_known != 0) {
        try write_stream.objectField("radio_ctrl_vars");
        try write_stream.beginArray();
        if (@as(?[*]u8, device_info.radio_ctrl_vars)) |ctrl_var_indexes| {
            for (0..device_info.radio_ctrl_var_count) |i| {
                try write_stream.write(ctrl_var_indexes[i]);
            }
        } else {
            for (0..device_info.radio_ctrl_var_count) |_| {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();
    }

    if (@as(?*u32, device_info.radio_default_serial)) |serial| {
        try write_stream.objectField("radio_default_serial");
        try write_stream.write(serial.*);
    }

    if (device_info.radio_scan_power_supported) |supported| {
        try write_stream.objectField("radio_scan_power");
        try write_stream.write(supported.* != 0);
    }

    if (!options.exclude_nvm) {
        if (device_info.nvm_size != 0) {
            if (@as(?[*]const u8, device_info.nvm)) |nvm| {
                try write_stream.objectField("nvm");
                try write_stream.print("\"{x}\"", .{nvm[0..device_info.nvm_size]});
            }
        }
    }

    var tag_locations_present = false;
    for (device_info.tag_locations) |loc| {
        if (loc != 0) {
            tag_locations_present = true;
            break;
        }
    }
    if (tag_locations_present) {
        try write_stream.objectField("tag_locations");
        try write_stream.beginArray();

        try write_stream.beginArray();
        try write_stream.write(device_info.tag_locations[0]);
        try write_stream.write(device_info.tag_locations[1]);
        try write_stream.endArray();
        try write_stream.beginArray();
        try write_stream.write(device_info.tag_locations[2]);
        try write_stream.write(device_info.tag_locations[3]);
        try write_stream.endArray();
        try write_stream.beginArray();
        try write_stream.write(device_info.tag_locations[4]);
        try write_stream.write(device_info.tag_locations[5]);
        try write_stream.endArray();

        try write_stream.endArray();
    }

    if (!options.exclude_nvm) {
        if (device_info.user_tag_1) |user_tag_1| {
            try write_stream.objectField("user_tag_1");
            try write_stream.write(@as([*:0]const u8, user_tag_1));
        }

        if (device_info.user_tag_2) |user_tag_2| {
            try write_stream.objectField("user_tag_2");
            try write_stream.write(@as([*:0]const u8, user_tag_2));
        }
    }

    if (options.include_version) {
        try write_stream.objectField("library_build_date");
        try write_stream.write(@as([*:0]const u8, c.asphodel_get_library_build_date()));
        try write_stream.objectField("library_build_info");
        try write_stream.write(@as([*:0]const u8, c.asphodel_get_library_build_info()));
        try write_stream.objectField("library_protocol_version");
        try write_stream.write(@as([*:0]const u8, c.asphodel_get_library_protocol_version_string()));
    }

    try write_stream.endObject();

    return out.toOwnedSliceSentinel(0);
}

fn writeStream(write_stream: *std.json.Stringify, stream: *const c.AsphodelStreamInfo_t) !void {
    try write_stream.beginObject();

    if (stream.channel_index_list != null) {
        try write_stream.objectField("_channel_array");
        try write_stream.beginArray();
        for (0..stream.channel_count) |i| {
            try write_stream.write(stream.channel_index_list[i]);
        }
        try write_stream.endArray();
    }

    try write_stream.objectField("channel_count");
    try write_stream.write(stream.channel_count);

    try write_stream.objectField("counter_bits");
    try write_stream.write(stream.counter_bits);
    try write_stream.objectField("filler_bits");
    try write_stream.write(stream.filler_bits);
    try write_stream.objectField("rate");
    try writeFloat(write_stream, stream.rate);
    try write_stream.objectField("rate_error");
    try writeFloat(write_stream, stream.rate_error);
    try write_stream.objectField("warm_up_delay");
    try writeFloat(write_stream, stream.warm_up_delay);

    try write_stream.endObject();
}

fn writeFloat(write_stream: *std.json.Stringify, value: f32) !void {
    if (std.math.isFinite(value)) {
        try write_stream.write(value);
    } else {
        try write_stream.print("\"{}\"", .{value});
    }
}

fn writeStreamRate(write_stream: *std.json.Stringify, stream_rate_info: *const c.AsphodelStreamRateInfo_t) !void {
    try write_stream.beginArray();
    try write_stream.write(stream_rate_info.available != 0);
    try write_stream.write(stream_rate_info.channel_index);
    try write_stream.write(stream_rate_info.invert);
    try writeFloat(write_stream, stream_rate_info.scale);
    try writeFloat(write_stream, stream_rate_info.offset);
    try write_stream.endArray();
}

fn writeChannel(write_stream: *std.json.Stringify, channel_info: *const c.AsphodelChannelInfo_t) !void {
    try write_stream.beginObject();

    if (channel_info.name != null and channel_info.name_length > 0) {
        try write_stream.objectField("_name_array");
        try write_stream.print("\"{x}\"", .{channel_info.name[0..channel_info.name_length]});

        try write_stream.objectField("name_length");
        try write_stream.write(channel_info.name_length);
    }

    if (channel_info.coefficients != null) {
        try write_stream.objectField("_coefficients_array");
        try write_stream.beginArray();
        for (0..channel_info.coefficients_length) |i| {
            try writeFloat(write_stream, channel_info.coefficients[i]);
        }
        try write_stream.endArray();

        // only write coefficients_length if the array is present
        try write_stream.objectField("coefficients_length");
        try write_stream.write(channel_info.coefficients_length);
    }

    try write_stream.objectField("chunk_count"); // always valid
    try write_stream.write(channel_info.chunk_count);

    if ((channel_info.chunk_lengths != null and channel_info.chunks != null) or channel_info.chunk_count == 0) {
        try write_stream.objectField("_chunk_length_array");
        try write_stream.beginArray();
        for (0..channel_info.chunk_count) |i| {
            try write_stream.write(channel_info.chunk_lengths[i]);
        }
        try write_stream.endArray();

        try write_stream.objectField("_chunk_list");
        try write_stream.beginArray();
        for (0..channel_info.chunk_count) |i| {
            const length = channel_info.chunk_lengths[i];
            const maybe_array: ?[*]const u8 = channel_info.chunks[i];
            if (maybe_array) |array| {
                try write_stream.beginArray();
                for (0..length) |j| {
                    try write_stream.write(array[j]);
                }
                try write_stream.endArray();
            } else {
                try write_stream.write(@as(?u8, null));
            }
        }
        try write_stream.endArray();
    }

    try write_stream.objectField("channel_type");
    try write_stream.write(channel_info.channel_type);
    try write_stream.objectField("unit_type");
    try write_stream.write(channel_info.unit_type);
    try write_stream.objectField("filler_bits");
    try write_stream.write(channel_info.filler_bits);
    try write_stream.objectField("data_bits");
    try write_stream.write(channel_info.data_bits);
    try write_stream.objectField("samples");
    try write_stream.write(channel_info.samples);
    try write_stream.objectField("bits_per_sample");
    try write_stream.write(channel_info.bits_per_sample);
    try write_stream.objectField("minimum");
    try writeFloat(write_stream, channel_info.minimum);
    try write_stream.objectField("maximum");
    try writeFloat(write_stream, channel_info.maximum);
    try write_stream.objectField("resolution");
    try writeFloat(write_stream, channel_info.resolution);

    try write_stream.endObject();
}

fn writeChannelCalibration(write_stream: *std.json.Stringify, channel_calibration: *const c.AsphodelChannelCalibration_t) !void {
    try write_stream.beginArray();
    try write_stream.write(channel_calibration.base_setting_index);
    try write_stream.write(channel_calibration.resolution_setting_index);
    try writeFloat(write_stream, channel_calibration.scale);
    try writeFloat(write_stream, channel_calibration.offset);
    try writeFloat(write_stream, channel_calibration.minimum);
    try writeFloat(write_stream, channel_calibration.maximum);
    try write_stream.endArray();
}

fn writeSupply(write_stream: *std.json.Stringify, supply_info: *const c.AsphodelSupplyInfo_t) !void {
    try write_stream.beginArray();
    try write_stream.write(@as(?[*:0]const u8, supply_info.name));
    try write_stream.beginArray();
    try write_stream.write(supply_info.unit_type);
    try write_stream.write(supply_info.is_battery);
    try write_stream.write(supply_info.nominal);
    try writeFloat(write_stream, supply_info.scale);
    try writeFloat(write_stream, supply_info.offset);
    try write_stream.endArray();
    try write_stream.endArray();
}

fn writeSupplyResult(write_stream: *std.json.Stringify, supply_result: *const c.AsphodelSupplyResult_t) !void {
    if (supply_result.error_code == c.ASPHODEL_SUCCESS) {
        try write_stream.beginArray();
        try write_stream.write(supply_result.measurement);
        try write_stream.write(supply_result.result);
        try write_stream.endArray();
    } else {
        try write_stream.write(@as(?u8, null));
    }
}

fn writeCtrlVarInfo(write_stream: *std.json.Stringify, ctrl_var_info: *const c.AsphodelCtrlVarInfo_t, state: ?i32) !void {
    try write_stream.beginArray();

    try write_stream.write(@as(?[*:0]const u8, ctrl_var_info.name));

    try write_stream.beginArray();

    try write_stream.write(ctrl_var_info.unit_type);
    try write_stream.write(ctrl_var_info.minimum);
    try write_stream.write(ctrl_var_info.maximum);
    try writeFloat(write_stream, ctrl_var_info.scale);
    try writeFloat(write_stream, ctrl_var_info.offset);

    try write_stream.endArray();

    try write_stream.write(state);

    try write_stream.endArray();
}

fn writeSetting(write_stream: *std.json.Stringify, setting_info: *const c.AsphodelSettingInfo_t) !void {
    try write_stream.beginWriteRaw();
    try write_stream.writer.writeAll("\"<AsphodelSettingInfo {name=b'");
    try writeSettingName(write_stream, std.mem.span(setting_info.name));
    try write_stream.writer.print("', name_length={d}, default_bytes=", .{setting_info.name_length});
    for (setting_info.default_bytes[0..setting_info.default_bytes_length], 0..) |b, i| {
        if (i == 0) {
            try write_stream.writer.print("0x{x:0>2}", .{b});
        } else {
            try write_stream.writer.print(",0x{x:0>2}", .{b});
        }
    }
    try write_stream.writer.print(", default_bytes_length={d}, setting_type={d} ({s}), u=", .{
        setting_info.default_bytes_length,
        setting_info.setting_type,
        c.asphodel_setting_type_name(setting_info.setting_type),
    });
    try writeSettingUnion(write_stream, setting_info);
    try write_stream.writer.writeAll("}>\"");
    write_stream.endWriteRaw();
}

fn writeSettingName(write_stream: *std.json.Stringify, name: []const u8) !void {
    for (name) |char| {
        switch (char) {
            '\\' => try write_stream.writer.writeAll("\\\\"),
            '\"' => try write_stream.writer.writeAll("\\\""),
            0x00...0x1F, 0x7F...0xFF => try write_stream.writer.print("\\\\x{x:0>2}", .{char}),
            else => try write_stream.writer.writeByte(char),
        }
    }
}

fn writeSettingUnion(write_stream: *std.json.Stringify, setting_info: *const c.AsphodelSettingInfo_t) !void {
    if (setting_info.setting_type == c.SETTING_TYPE_BYTE or
        setting_info.setting_type == c.SETTING_TYPE_BOOLEAN or
        setting_info.setting_type == c.SETTING_TYPE_UNIT_TYPE or
        setting_info.setting_type == c.SETTING_TYPE_CHANNEL_TYPE)
    {
        try write_stream.writer.writeAll("<AsphodelByteSetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.byte_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_BYTE_ARRAY) {
        try write_stream.writer.writeAll("<AsphodelByteArraySetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.byte_array_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_STRING) {
        try write_stream.writer.writeAll("<AsphodelStringSetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.string_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_INT32) {
        try write_stream.writer.writeAll("<AsphodelInt32Setting {");
        try writeSettingUnionFields(write_stream, setting_info.u.int32_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_INT32_SCALED) {
        try write_stream.writer.writeAll("<AsphodelInt32ScaledSetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.int32_scaled_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_FLOAT) {
        try write_stream.writer.writeAll("<AsphodelFloatSetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.float_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_FLOAT_ARRAY) {
        try write_stream.writer.writeAll("<AsphodelFloatArraySetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.float_array_setting);
    } else if (setting_info.setting_type == c.SETTING_TYPE_CUSTOM_ENUM) {
        try write_stream.writer.writeAll("<AsphodelCustomEnumSetting {");
        try writeSettingUnionFields(write_stream, setting_info.u.custom_enum_setting);
    } else {
        try write_stream.writer.writeAll("UNKNOWN TYPE");
        return; // don't write the final part
    }

    try write_stream.writer.writeAll("}>");
}

fn writeSettingUnionFields(write_stream: *std.json.Stringify, setting_info: anytype) !void {
    const T = @TypeOf(setting_info);
    inline for (@typeInfo(T).@"struct".fields, 0..) |field, i| {
        if (i == 0) {
            try write_stream.writer.print("{s}=", .{field.name});
        } else {
            try write_stream.writer.print(", {s}=", .{field.name});
        }

        if (comptime std.mem.eql(u8, field.name, "unit_type")) {
            const unit_type: u8 = @field(setting_info, field.name);
            try write_stream.writer.print("{d} ({s})", .{ unit_type, c.asphodel_unit_type_name(unit_type) });
        } else if (@typeInfo(field.type) == .int) {
            try write_stream.writer.print("{d}", .{@field(setting_info, field.name)});
        } else if (@typeInfo(field.type) == .float) {
            try write_stream.writer.print("{d}", .{@field(setting_info, field.name)});
        } else {
            unreachable;
        }
    }
}

pub fn fillDeviceInfoFromJson(allocator: std.mem.Allocator, json: []const u8, device_info: *c.AsphodelDeviceInfo_t, excess_out: ?*[]const u8) !void {
    var parsed = try std.json.parseFromSliceLeaky(std.json.Value, allocator, json, .{ .allocate = .alloc_if_needed });

    const map: *std.json.ObjectMap = switch (parsed) {
        .object => |*obj| obj,
        else => return error.InvalidJson,
    };

    try readStringKey(allocator, map, "serial_number", &device_info.serial_number);
    try readStringKey(allocator, map, "location_string", &device_info.location_string);
    try readUsizeKey(map, "max_incoming_param_length", &device_info.max_incoming_param_length);
    try readUsizeKey(map, "max_outgoing_param_length", &device_info.max_outgoing_param_length);
    try readUsizeKey(map, "stream_packet_length", &device_info.stream_packet_length);
    try readUsizeKey(map, "remote_max_incoming_param_length", &device_info.remote_max_incoming_param_length);
    try readUsizeKey(map, "remote_max_outgoing_param_length", &device_info.remote_max_outgoing_param_length);
    try readUsizeKey(map, "remote_stream_packet_length", &device_info.remote_stream_packet_length);
    try readBoolKey(map, "supports_bootloader", &device_info.supports_bootloader);
    try readBoolKey(map, "supports_radio", &device_info.supports_radio);
    try readBoolKey(map, "supports_remote", &device_info.supports_remote);
    try readBoolKey(map, "supports_rf_power", &device_info.supports_rf_power);
    try readStringKey(allocator, map, "build_date", &device_info.build_date);
    try readStringKey(allocator, map, "build_info", &device_info.build_info);
    try readStringKey(allocator, map, "nvm_hash", &device_info.nvm_hash);

    try readNvmModified(allocator, map, device_info);

    try readStringKey(allocator, map, "setting_hash", &device_info.setting_hash);

    try readBoardInfo(allocator, map, device_info);

    try readStringKey(allocator, map, "protocol_version", &device_info.protocol_version);
    try readStringKey(allocator, map, "chip_family", &device_info.chip_family);
    try readStringKey(allocator, map, "chip_id", &device_info.chip_id);
    try readStringKey(allocator, map, "chip_model", &device_info.chip_model);
    try readStringKey(allocator, map, "bootloader_info", &device_info.bootloader_info);

    try readRgbs(allocator, map, device_info);
    try readLeds(allocator, map, device_info);

    try readStringKey(allocator, map, "commit_id", &device_info.commit_id);
    try readStringKey(allocator, map, "repo_branch", &device_info.repo_branch);
    try readStringKey(allocator, map, "repo_name", &device_info.repo_name);

    try readStreams(allocator, map, device_info);
    try readChannels(allocator, map, device_info);
    try readSupplies(allocator, map, device_info);
    try readCtrlVars(allocator, map, device_info);

    try readSettings(allocator, map, device_info);
    try readCustomEnums(allocator, map, device_info);
    try readSettingCategories(allocator, map, device_info);

    try readDeviceMode(allocator, map, device_info);
    try readRFPowerInfo(allocator, map, device_info);
    try readRadioInfo(allocator, map, device_info);

    try readNvm(allocator, map, device_info);
    try readTagLocations(map, device_info);
    try readStringKey(allocator, map, "user_tag_1", &device_info.user_tag_1);
    try readStringKey(allocator, map, "user_tag_2", &device_info.user_tag_2);

    if (excess_out) |e| {
        var out: std.io.Writer.Allocating = .init(allocator);
        const writer = &out.writer;
        try std.json.Stringify.value(parsed, .{}, writer);
        e.* = out.written();
    }
}

fn readIntegerFromValue(comptime T: type, value: std.json.Value) !T {
    switch (value) {
        .integer => |i| return std.math.cast(T, i) orelse return error.InvalidJson,
        .float => return error.InvalidJson, // I don't know how to make this perfectly safe
        else => return error.InvalidJson, // null here is disallowed
    }
}

fn readFloatFromValue(comptime T: type, value: std.json.Value) !T {
    switch (value) {
        .float => |f| {
            const result: T = @floatCast(f);
            return result;
        },
        .integer => |i| {
            const result: T = @floatFromInt(i);
            return result;
        },
        .string => |str| {
            const result: T = std.fmt.parseFloat(T, str) catch return error.InvalidJson;
            return result;
        },
        else => return error.InvalidJson, // null here is disallowed
    }
}

fn readStringKey(allocator: std.mem.Allocator, map: *std.json.ObjectMap, key: []const u8, destination: *?[*:0]const u8) !void {
    const kv = map.fetchSwapRemove(key) orelse return;

    switch (kv.value) {
        .string => |str| {
            const value = try allocator.dupeZ(u8, str);
            destination.* = value;
        },
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readBoolKey(map: *std.json.ObjectMap, key: []const u8, destination: *u8) !void {
    const kv = map.fetchSwapRemove(key) orelse return;

    switch (kv.value) {
        .bool => |b| destination.* = if (b) 1 else 0,
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readUsizeKey(map: *std.json.ObjectMap, key: []const u8, destination: *usize) !void {
    const kv = map.fetchSwapRemove(key) orelse return;

    switch (kv.value) {
        .integer => |i| destination.* = std.math.cast(usize, i) orelse return error.InvalidJson,
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readNvmModified(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("nvm_modified") orelse return;

    switch (kv.value) {
        .bool => |b| {
            const a = try allocator.alloc(u8, 1);
            a[0] = if (b) 1 else 0;
            device_info.nvm_modified = a.ptr;
        },
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readBoardInfo(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("board_info") orelse return;

    switch (kv.value) {
        .array => |array| {
            if (array.items.len != 2) return error.InvalidJson;
            switch (array.items[0]) {
                .string => |str| {
                    const board_name = try allocator.dupeZ(u8, str);
                    device_info.board_info_name = board_name;
                },
                else => return error.InvalidJson, // null here is disallowed
            }

            device_info.board_info_rev = try readIntegerFromValue(u8, array.items[1]);
        },
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readRgbs(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("rgb_settings") orelse return;

    switch (kv.value) {
        .array => |outer_array| {
            device_info.rgb_count = outer_array.items.len;
            device_info.rgb_count_known = 1;

            var allocated: ?[][3]u8 = null;
            errdefer if (allocated) |a| allocator.free(a);
            errdefer device_info.rgb_settings = null;

            for (outer_array.items, 0..) |outer_item, i| {
                switch (outer_item) {
                    .array => |inner_array| {
                        if (inner_array.items.len != 3) return error.InvalidJson;
                        if (device_info.rgb_settings == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc([3]u8, device_info.rgb_count);
                            device_info.rgb_settings = a.ptr;
                            allocated = a;
                        }

                        for (inner_array.items, 0..) |inner_item, j| {
                            device_info.rgb_settings[i][j] = try readIntegerFromValue(u8, inner_item);
                        }
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            allocator.free(a);
                            device_info.rgb_settings = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => return, // ignore a null for the outer array
        else => return error.InvalidJson,
    }
}

fn readLeds(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("led_settings") orelse return;

    switch (kv.value) {
        .array => |array| {
            device_info.led_count = array.items.len;
            device_info.led_count_known = 1;

            var allocated: ?[]u8 = null;
            errdefer if (allocated) |a| allocator.free(a);
            errdefer device_info.led_settings = null;

            for (array.items, 0..) |item, i| {
                switch (item) {
                    .integer => |value| {
                        if (device_info.led_settings == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc(u8, device_info.led_count);
                            device_info.led_settings = a.ptr;
                            allocated = a;
                        }
                        device_info.led_settings[i] = std.math.cast(u8, value) orelse return error.InvalidJson;
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            allocator.free(a);
                            device_info.led_settings = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => return, // ignore a null for the array
        else => return error.InvalidJson,
    }
}

fn readStreams(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const rate_kv = map.fetchSwapRemove("stream_rate_info"); // grab now so it doesn't show up in excess keys
    const filler_bits_kv = map.fetchSwapRemove("stream_filler_bits");
    const id_bits_kv = map.fetchSwapRemove("stream_id_bits");
    const kv = map.fetchSwapRemove("streams") orelse return;

    switch (kv.value) {
        .array => |array| {
            device_info.stream_count = array.items.len;
            device_info.stream_count_known = 1;

            device_info.stream_filler_bits = if (filler_bits_kv) |x| try readIntegerFromValue(u8, x.value) else return error.InvalidJson;
            device_info.stream_id_bits = if (id_bits_kv) |x| try readIntegerFromValue(u8, x.value) else return error.InvalidJson;

            var allocated: ?[]c.AsphodelStreamInfo_t = null;
            errdefer if (allocated) |a| allocator.free(a);
            errdefer device_info.streams = null;

            for (array.items, 0..) |item, i| {
                switch (item) {
                    .object => |*object| {
                        if (device_info.streams == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc(c.AsphodelStreamInfo_t, device_info.stream_count);
                            device_info.streams = a.ptr;
                            allocated = a;
                        }
                        try readStream(allocator, object, &@as([*]c.AsphodelStreamInfo_t, device_info.streams)[i]);
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            allocator.free(a);
                            device_info.streams = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => {
            // we need to check the filler bits and id bits to know if the stream count is known or unknown
            const filler_bits: ?u8 = if (filler_bits_kv) |x| readIntegerFromValue(u8, x.value) catch null else null;
            const id_bits: ?u8 = if (id_bits_kv) |x| readIntegerFromValue(u8, x.value) catch null else null;

            device_info.stream_count = 0; // zero either way
            if (filler_bits != null and id_bits != null) {
                device_info.stream_filler_bits = filler_bits.?;
                device_info.stream_id_bits = id_bits.?;
                device_info.stream_count_known = 1;
            } else {
                device_info.stream_count_known = 0;
            }
        },
        else => return error.InvalidJson,
    }

    if (rate_kv == null) return; // not present is fine

    switch (rate_kv.?.value) {
        .array => |outer_array| {
            if (outer_array.items.len == 0) return; // empty array is always valid
            if (device_info.stream_count_known == 0 or outer_array.items.len != device_info.stream_count) return error.InvalidJson;

            const allocated: []c.AsphodelStreamRateInfo_t = try allocator.alloc(c.AsphodelStreamRateInfo_t, device_info.stream_count);
            errdefer allocator.free(allocated);

            device_info.stream_rates = allocated.ptr;
            errdefer device_info.stream_rates = null;

            for (outer_array.items, 0..) |outer_item, i| {
                switch (outer_item) {
                    .array => |inner_array| {
                        if (inner_array.items.len != 5) return error.InvalidJson;

                        switch (inner_array.items[0]) {
                            .bool => |b| device_info.stream_rates[i].available = if (b) 1 else 0, // boolean is the normal case
                            .integer => |x| device_info.stream_rates[i].available = std.math.cast(u1, x) orelse return error.InvalidJson, // only accept 0 or 1
                            else => return error.InvalidJson,
                        }
                        device_info.stream_rates[i].channel_index = try readIntegerFromValue(c_int, inner_array.items[1]);
                        device_info.stream_rates[i].invert = try readIntegerFromValue(c_int, inner_array.items[2]);
                        device_info.stream_rates[i].scale = try readFloatFromValue(f32, inner_array.items[3]);
                        device_info.stream_rates[i].offset = try readFloatFromValue(f32, inner_array.items[4]);
                    },
                    else => return error.InvalidJson, // disallow nulls, it would complicate this code and won't be emitted by the writer code
                }
            }
        },
        .null => return, // null array is fine
        else => return error.InvalidJson,
    }
}

fn readStream(allocator: Allocator, map: *const std.json.ObjectMap, stream_info: *c.AsphodelStreamInfo_t) !void {
    stream_info.* = .{}; // not strictly needed

    const counter_bits_value = map.get("counter_bits") orelse return error.InvalidJson;
    stream_info.counter_bits = try readIntegerFromValue(u8, counter_bits_value);

    const filler_bits_value = map.get("filler_bits") orelse return error.InvalidJson;
    stream_info.filler_bits = try readIntegerFromValue(u8, filler_bits_value);

    const rate_value = map.get("rate") orelse return error.InvalidJson;
    stream_info.rate = try readFloatFromValue(f32, rate_value);

    const rate_error_value = map.get("rate_error") orelse return error.InvalidJson;
    stream_info.rate_error = try readFloatFromValue(f32, rate_error_value);

    const warm_up_delay_value = map.get("warm_up_delay") orelse return error.InvalidJson;
    stream_info.warm_up_delay = try readFloatFromValue(f32, warm_up_delay_value);

    // ignore "channel_count" key

    const maybe_channel_array_value = map.get("_channel_array");
    if (maybe_channel_array_value) |channel_array_value| {
        switch (channel_array_value) {
            .array => |array| {
                stream_info.channel_count = std.math.cast(u8, array.items.len) orelse return error.InvalidJson;

                if (array.items.len > 0) {
                    var channels = try allocator.alloc(u8, array.items.len);
                    stream_info.channel_index_list = channels.ptr;
                    errdefer allocator.free(channels);
                    errdefer stream_info.channel_index_list = null;

                    for (array.items, 0..) |item, i| {
                        channels[i] = try readIntegerFromValue(u8, item);
                    }
                }
            },
            .null => {
                stream_info.channel_count = 0;
                stream_info.channel_index_list = null;
            },
            else => return error.InvalidJson,
        }
    } else {
        stream_info.channel_count = 0;
        stream_info.channel_index_list = null;
    }
}

fn readChannels(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const cal_kv = map.fetchSwapRemove("channel_calibration"); // grab now so it doesn't show up in excess keys
    const kv = map.fetchSwapRemove("channels") orelse return;

    switch (kv.value) {
        .array => |array| {
            device_info.channel_count = array.items.len;
            device_info.channel_count_known = 1;

            var allocated: ?[]c.AsphodelChannelInfo_t = null;
            errdefer if (allocated) |a| allocator.free(a);
            errdefer device_info.channels = null;

            for (array.items, 0..) |item, i| {
                switch (item) {
                    .object => |*object| {
                        if (device_info.channels == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc(c.AsphodelChannelInfo_t, device_info.channel_count);
                            device_info.channels = a.ptr;
                            allocated = a;
                        }
                        try readChannel(allocator, object, &@as([*]c.AsphodelChannelInfo_t, device_info.channels)[i]);
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            allocator.free(a);
                            device_info.channels = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => {}, // ignore a null for the outer array
        else => return error.InvalidJson,
    }

    if (cal_kv == null) return; // not present is fine

    switch (cal_kv.?.value) {
        .array => |outer_array| {
            if (outer_array.items.len == 0) return; // empty array is always valid
            if (device_info.channel_count_known == 0 or outer_array.items.len != device_info.channel_count) return error.InvalidJson;

            const allocated: []?*c.AsphodelChannelCalibration_t = try allocator.alloc(?*c.AsphodelChannelCalibration_t, device_info.channel_count);
            for (allocated) |*cal| {
                cal.* = null;
            }
            errdefer {
                for (allocated) |maybe_cal| {
                    if (maybe_cal) |cal| {
                        allocator.destroy(cal);
                    }
                }
                allocator.free(allocated);
                device_info.channel_calibrations = null;
            }
            device_info.channel_calibrations = allocated.ptr;

            for (outer_array.items, 0..) |outer_item, i| {
                switch (outer_item) {
                    .array => |inner_array| {
                        if (inner_array.items.len != 6) return error.InvalidJson;

                        var cal = try allocator.create(c.AsphodelChannelCalibration_t);
                        device_info.channel_calibrations[i] = cal;

                        cal.base_setting_index = try readIntegerFromValue(c_int, inner_array.items[0]);
                        cal.resolution_setting_index = try readIntegerFromValue(c_int, inner_array.items[1]);
                        cal.scale = try readFloatFromValue(f32, inner_array.items[2]);
                        cal.offset = try readFloatFromValue(f32, inner_array.items[3]);
                        cal.minimum = try readFloatFromValue(f32, inner_array.items[4]);
                        cal.maximum = try readFloatFromValue(f32, inner_array.items[5]);
                    },
                    .null => {
                        device_info.channel_calibrations[i] = null;
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => return, // null array is fine
        else => return error.InvalidJson,
    }
}

fn readChannel(allocator: Allocator, map: *const std.json.ObjectMap, channel_info: *c.AsphodelChannelInfo_t) !void {
    channel_info.* = .{}; // not strictly needed

    const channel_type_value = map.get("channel_type") orelse return error.InvalidJson;
    channel_info.channel_type = try readIntegerFromValue(u8, channel_type_value);
    const unit_type_value = map.get("unit_type") orelse return error.InvalidJson;
    channel_info.unit_type = try readIntegerFromValue(u8, unit_type_value);
    const filler_bits_value = map.get("filler_bits") orelse return error.InvalidJson;
    channel_info.filler_bits = try readIntegerFromValue(u16, filler_bits_value);
    const data_bits_value = map.get("data_bits") orelse return error.InvalidJson;
    channel_info.data_bits = try readIntegerFromValue(u16, data_bits_value);
    const samples_value = map.get("samples") orelse return error.InvalidJson;
    channel_info.samples = try readIntegerFromValue(u8, samples_value);
    const bits_per_sample_value = map.get("bits_per_sample") orelse return error.InvalidJson;
    channel_info.bits_per_sample = try readIntegerFromValue(i16, bits_per_sample_value);
    const minimum_value = map.get("minimum") orelse return error.InvalidJson;
    channel_info.minimum = try readFloatFromValue(f32, minimum_value);
    const maximum_value = map.get("maximum") orelse return error.InvalidJson;
    channel_info.maximum = try readFloatFromValue(f32, maximum_value);
    const resolution_value = map.get("resolution") orelse return error.InvalidJson;
    channel_info.resolution = try readFloatFromValue(f32, resolution_value);

    const chunk_count_value = map.get("chunk_count") orelse return error.InvalidJson;
    channel_info.chunk_count = try readIntegerFromValue(u8, chunk_count_value);

    // NOTE: ignoring "name_length" key
    const maybe_name_value = map.get("_name_array");
    if (maybe_name_value) |name_value| {
        switch (name_value) {
            .string => |str| {
                if (str.len & 1 != 0) return error.InvalidJson;
                channel_info.name_length = std.math.cast(u8, str.len / 2) orelse return error.InvalidJson;
                const name = try allocator.alloc(u8, channel_info.name_length + 1);
                errdefer allocator.free(name);
                name[channel_info.name_length] = 0; // null terminate
                channel_info.name = name.ptr;
                errdefer channel_info.name = null;

                _ = std.fmt.hexToBytes(name, str) catch return error.InvalidJson;
            },
            .null => {
                channel_info.name = null;
                channel_info.name_length = 0;
            }, // ignore any null values
            else => return error.InvalidJson,
        }
    } else {
        channel_info.name = null;
        channel_info.name_length = 0;
    }

    // NOTE: ignoring "coefficients_length" key
    const maybe_coefficients_value = map.get("_coefficients_array");
    if (maybe_coefficients_value) |coefficients_value| {
        switch (coefficients_value) {
            .array => |array| {
                channel_info.coefficients_length = std.math.cast(u8, array.items.len) orelse return error.InvalidJson;
                if (array.items.len > 0) {
                    var coefficients = try allocator.alloc(f32, channel_info.coefficients_length);
                    errdefer allocator.free(coefficients);
                    channel_info.coefficients = coefficients.ptr;
                    errdefer channel_info.coefficients = null;

                    for (array.items, 0..) |item, i| {
                        coefficients[i] = try readFloatFromValue(f32, item);
                    }
                } else {
                    channel_info.coefficients = null;
                }
            },
            .null => {
                channel_info.coefficients = null;
                channel_info.coefficients_length = 0;
            },
            else => return error.InvalidJson,
        }
    } else {
        channel_info.coefficients = null;
        channel_info.coefficients_length = 0;
    }

    // NOTE: ignoring "_chunk_length_array" key
    const maybe_chunk_list = map.get("_chunk_list");
    if (maybe_chunk_list) |chunk_list| {
        switch (chunk_list) {
            .array => |outer_array| {
                if (outer_array.items.len != channel_info.chunk_count) return error.InvalidJson;

                if (outer_array.items.len > 0) {
                    var chunk_lengths = try allocator.alloc(u8, channel_info.chunk_count);
                    errdefer allocator.free(chunk_lengths);
                    channel_info.chunk_lengths = chunk_lengths.ptr;
                    errdefer channel_info.chunk_lengths = null;

                    var top_level_chunks = try allocator.alloc(?[*]const u8, channel_info.chunk_count);
                    @memset(top_level_chunks, null);
                    channel_info.chunks = top_level_chunks.ptr;
                    errdefer {
                        // NOTE: chunk_lengths have not yet been freed
                        for (top_level_chunks, 0..) |maybe_chunk, i| {
                            if (maybe_chunk) |chunk| {
                                const length = chunk_lengths[i];
                                allocator.free(chunk[0..length]);
                            }
                        }
                        allocator.free(top_level_chunks);
                        channel_info.chunks = null;
                    }

                    for (outer_array.items, 0..) |item, i| {
                        switch (item) {
                            .array => |inner_array| {
                                if (inner_array.items.len == 0) {
                                    top_level_chunks[i] = null;
                                    chunk_lengths[i] = 0;
                                } else {
                                    chunk_lengths[i] = std.math.cast(u8, inner_array.items.len) orelse return error.InvalidJson;
                                    const chunk = try allocator.alloc(u8, chunk_lengths[i]);
                                    top_level_chunks[i] = chunk.ptr;

                                    for (inner_array.items, 0..) |inner_item, j| {
                                        chunk[j] = try readIntegerFromValue(u8, inner_item);
                                    }
                                }
                            },
                            .null => {
                                top_level_chunks[i] = null;
                                chunk_lengths[i] = 0;
                            },
                            else => return error.InvalidJson,
                        }
                    }
                } else {
                    channel_info.chunk_lengths = null;
                    channel_info.chunks = null;
                }
            },
            .null => {
                channel_info.chunk_lengths = null;
                channel_info.chunks = null;
            },
            else => return error.InvalidJson,
        }
    } else {
        channel_info.chunk_lengths = null;
        channel_info.chunks = null;
    }
}

fn readSupplies(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const result_kv = map.fetchSwapRemove("supply_results"); // grab now so it doesn't show up in excess keys
    const kv = map.fetchSwapRemove("supplies") orelse return;

    switch (kv.value) {
        .array => |outer_array| {
            device_info.supply_count = outer_array.items.len;
            device_info.supply_count_known = 1;

            var allocated: ?[]c.AsphodelSupplyInfo_t = null;
            errdefer if (allocated) |a| {
                for (a) |*supply_info| {
                    if (supply_info.name) |name| {
                        allocator.free(std.mem.span(name));
                    }
                }
                allocator.free(a);
                device_info.supplies = null;
            };

            for (outer_array.items, 0..) |item, i| {
                switch (item) {
                    .array => |inner_array| {
                        if (device_info.supplies == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc(c.AsphodelSupplyInfo_t, device_info.supply_count);
                            for (a) |*supply_info| {
                                supply_info.name = null; // explicitly null this out so we can potentially free it later
                            }
                            device_info.supplies = a.ptr;
                            allocated = a;
                        }
                        try readSupply(allocator, inner_array, &@as([*]c.AsphodelSupplyInfo_t, device_info.supplies)[i]);
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            for (a) |*supply_info| {
                                if (supply_info.name) |name| {
                                    allocator.free(std.mem.span(name));
                                }
                            }
                            allocator.free(a);
                            device_info.supplies = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => {}, // ignore a null for the outer array
        else => return error.InvalidJson,
    }

    if (result_kv == null) return; // not present is fine

    switch (result_kv.?.value) {
        .array => |outer_array| {
            if (outer_array.items.len == 0) return; // empty array is always valid
            if (device_info.supply_count_known == 0 or outer_array.items.len != device_info.supply_count) return error.InvalidJson;

            const allocated: []c.AsphodelSupplyResult_t = try allocator.alloc(c.AsphodelSupplyResult_t, device_info.supply_count);
            errdefer allocator.free(allocated);

            device_info.supply_results = allocated.ptr;
            errdefer device_info.supply_results = null;

            for (outer_array.items, 0..) |outer_item, i| {
                switch (outer_item) {
                    .array => |inner_array| {
                        if (inner_array.items.len != 2) return error.InvalidJson;

                        device_info.supply_results[i].error_code = c.ASPHODEL_SUCCESS;
                        device_info.supply_results[i].measurement = try readIntegerFromValue(i32, inner_array.items[0]);
                        device_info.supply_results[i].result = try readIntegerFromValue(u8, inner_array.items[1]);
                    },
                    .null => {
                        // null possibly translated from an unknown error code result. error code picked at random.
                        device_info.supply_results[i].error_code = c.ASPHODEL_UNINITIALIZED;
                        device_info.supply_results[i].measurement = 0;
                        device_info.supply_results[i].result = 0;
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => return, // null array is fine
        else => return error.InvalidJson,
    }
}

fn readSupply(allocator: Allocator, array: std.json.Array, supply_info: *c.AsphodelSupplyInfo_t) !void {
    if (array.items.len != 2) return error.InvalidJson;

    const name = array.items[0];
    switch (name) {
        .string => |str| {
            supply_info.name = try allocator.dupeZ(u8, str);
            errdefer allocator.free(std.mem.span(supply_info.name));

            if (str.len > std.math.maxInt(u8)) return error.InvalidJson;
            supply_info.name_length = @intCast(str.len);
        },
        .null => {
            supply_info.name = null;
            supply_info.name_length = 0;
        },
        else => return error.InvalidJson,
    }

    const value_array = array.items[1];
    switch (value_array) {
        .array => |inner_array| {
            if (inner_array.items.len != 5) return error.InvalidJson;

            supply_info.unit_type = try readIntegerFromValue(u8, inner_array.items[0]);
            supply_info.is_battery = try readIntegerFromValue(u8, inner_array.items[1]);
            supply_info.nominal = try readIntegerFromValue(i32, inner_array.items[2]);
            supply_info.scale = try readFloatFromValue(f32, inner_array.items[3]);
            supply_info.offset = try readFloatFromValue(f32, inner_array.items[4]);
        },
        else => return error.InvalidJson,
    }
}

fn readCtrlVars(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("ctrl_vars") orelse return;

    switch (kv.value) {
        .array => |outer_array| {
            device_info.ctrl_var_count = outer_array.items.len;
            device_info.ctrl_var_count_known = 1;

            var allocated: ?[]c.AsphodelCtrlVarInfo_t = null;
            errdefer if (allocated) |a| {
                for (a) |*ctrl_var_info| {
                    if (ctrl_var_info.name) |name| {
                        allocator.free(std.mem.span(name));
                    }
                }
                allocator.free(a);
                device_info.ctrl_vars = null;
            };

            var state_array: ?[]i32 = null;
            errdefer if (state_array) |a| {
                allocator.free(a);
                device_info.ctrl_var_states = null;
            };

            for (outer_array.items, 0..) |item, i| {
                switch (item) {
                    .array => |inner_array| {
                        if (device_info.ctrl_vars == null) {
                            // allocate memory for the array
                            const a = try allocator.alloc(c.AsphodelCtrlVarInfo_t, device_info.ctrl_var_count);
                            for (a) |*ctrl_var_info| {
                                ctrl_var_info.name = null; // explicitly null this out so we can potentially free it later
                            }
                            device_info.ctrl_vars = a.ptr;
                            allocated = a;
                        }
                        const state = try readCtrlVar(allocator, inner_array, &@as([*]c.AsphodelCtrlVarInfo_t, device_info.ctrl_vars)[i]);

                        if (state) |s| {
                            if (state_array) |a| {
                                // have memory ready to be filled; write it in
                                a[i] = s;
                            } else {
                                // haven't allocated memory yet
                                if (i == 0) {
                                    // ok to allocate memory for the very first index
                                    const a = try allocator.alloc(i32, device_info.ctrl_var_count);
                                    device_info.ctrl_var_states = a.ptr;
                                    state_array = a;

                                    // write it in
                                    a[i] = s;
                                }
                            }
                        } else if (state_array) |a| {
                            // found a null after having allocated memory. We either need all of the states or none, so free it
                            allocator.free(a);
                            device_info.ctrl_var_states = null;
                            state_array = null;
                        }
                    },
                    .null => {
                        // any nulls means the array is incomplete and we must free any memory we've already allocated
                        // NOTE: this is unlikely but possible if the json itself is partially filled
                        if (allocated) |a| {
                            for (a) |*ctrl_var_info| {
                                if (ctrl_var_info.name) |name| {
                                    allocator.free(std.mem.span(name));
                                }
                            }
                            allocator.free(a);
                            device_info.ctrl_vars = null;
                        }
                        return; // we already got the count filled
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => {}, // ignore a null for the outer array
        else => return error.InvalidJson,
    }
}

fn readCtrlVar(allocator: Allocator, array: std.json.Array, ctrl_var_info: *c.AsphodelCtrlVarInfo_t) !?i32 {
    if (array.items.len != 3) return error.InvalidJson;

    const name = array.items[0];
    switch (name) {
        .string => |str| {
            ctrl_var_info.name = try allocator.dupeZ(u8, str);
            errdefer allocator.free(std.mem.span(ctrl_var_info.name));

            if (str.len > std.math.maxInt(u8)) return error.InvalidJson;
            ctrl_var_info.name_length = @intCast(str.len);
        },
        .null => {
            ctrl_var_info.name = null;
            ctrl_var_info.name_length = 0;
        },
        else => return error.InvalidJson,
    }

    const value_array = array.items[1];
    switch (value_array) {
        .array => |inner_array| {
            if (inner_array.items.len != 5) return error.InvalidJson;

            ctrl_var_info.unit_type = try readIntegerFromValue(u8, inner_array.items[0]);
            ctrl_var_info.minimum = try readIntegerFromValue(i32, inner_array.items[1]);
            ctrl_var_info.maximum = try readIntegerFromValue(i32, inner_array.items[2]);
            ctrl_var_info.scale = try readFloatFromValue(f32, inner_array.items[3]);
            ctrl_var_info.offset = try readFloatFromValue(f32, inner_array.items[4]);
        },
        else => return error.InvalidJson,
    }

    const state = array.items[2];
    switch (state) {
        .integer => |i| return std.math.cast(i32, i) orelse return error.InvalidJson,
        .null => return null,
        else => return error.InvalidJson,
    }
}

fn readSettings(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("settings") orelse return;

    switch (kv.value) {
        .array => |array| {
            device_info.setting_count = array.items.len;
            device_info.setting_count_known = 1;

            const allocated: []c.AsphodelSettingInfo_t = try allocator.alloc(c.AsphodelSettingInfo_t, device_info.setting_count);
            errdefer allocator.free(allocated);
            device_info.settings = allocated.ptr;
            errdefer device_info.settings = null;

            for (array.items, 0..) |item, i| {
                switch (item) {
                    .string => |str| {
                        try readSetting(allocator, str, &@as([*]c.AsphodelSettingInfo_t, device_info.settings)[i]);
                    },
                    .null => {
                        // a null element means the whole array needs to be marked incomplete
                        allocator.free(allocated);
                        device_info.settings = null;
                        break;
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => {}, // ignore a null for the outer array
        else => return error.InvalidJson,
    }
}

fn readSetting(allocator: Allocator, str: []const u8, setting_info: *c.AsphodelSettingInfo_t) !void {
    var s = try trimPrefix(str, "<AsphodelSettingInfo {");
    s = try trimSuffix(s, "}>");

    if (std.mem.endsWith(u8, s, "UNKNOWN TYPE")) return error.InvalidJson;

    s = try trimSuffix(s, "}>");

    var backit = std.mem.splitBackwardsSequence(u8, s, " {");
    const u_values = backit.first();
    s = backit.rest();

    backit = std.mem.splitBackwardsSequence(u8, s, ", u=<");
    const u_type = backit.first();
    s = backit.rest();

    backit = std.mem.splitBackwardsSequence(u8, s, ", setting_type=");
    const setting_type_str = backit.first();
    s = backit.rest();

    var it = std.mem.splitSequence(u8, setting_type_str, " (");
    setting_info.setting_type = try std.fmt.parseUnsigned(u8, it.first(), 10);

    try readSettingUnion(u_type, u_values, setting_info);

    backit = std.mem.splitBackwardsSequence(u8, s, ", default_bytes_length=");
    setting_info.default_bytes_length = try std.fmt.parseUnsigned(u8, backit.first(), 10);
    s = backit.rest();

    backit = std.mem.splitBackwardsSequence(u8, s, ", default_bytes=");
    const default_bytes_str = backit.first();
    s = backit.rest();

    const default_bytes = try readSettingDefaultBytes(allocator, default_bytes_str, setting_info.default_bytes_length);
    setting_info.default_bytes = default_bytes.ptr;

    backit = std.mem.splitBackwardsSequence(u8, s, ", name_length=");
    setting_info.name_length = try std.fmt.parseUnsigned(u8, backit.first(), 10);
    s = backit.rest();

    const name_str = try trimPrefix(s, "name=b");
    setting_info.name = try readSettingName(allocator, name_str, setting_info.name_length);
}

fn testSetting(str: []const u8, expected: c.AsphodelSettingInfo_t) !void {
    var dest = c.AsphodelSettingInfo_t{};
    try readSetting(std.testing.allocator, str, &dest);
    defer std.testing.allocator.free(std.mem.span(dest.name));
    defer std.testing.allocator.free(dest.default_bytes[0..dest.default_bytes_length]);

    try std.testing.expectEqual(expected.name_length, dest.name_length);
    try std.testing.expectEqualStrings(std.mem.span(expected.name), std.mem.span(dest.name));
    try std.testing.expectEqual(expected.default_bytes_length, dest.default_bytes_length);
    try std.testing.expectEqualSlices(u8, expected.default_bytes[0..expected.default_bytes_length], dest.default_bytes[0..dest.default_bytes_length]);
    try std.testing.expectEqual(expected.setting_type, dest.setting_type);
}

test "readSetting" {
    const test_cases = &[_]struct { str: []const u8, expected: c.AsphodelSettingInfo_t }{
        .{
            .str = "<AsphodelSettingInfo {name=b'CT Model', name_length=8, default_bytes=0x01, default_bytes_length=1, setting_type=10 (SETTING_TYPE_CUSTOM_ENUM), u=<AsphodelCustomEnumSetting {nvm_word=65, nvm_word_byte=1, custom_enum_index=0}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 8,
                .name = "CT Model",
                .default_bytes_length = 1,
                .default_bytes = &[1]u8{1},
                .setting_type = c.SETTING_TYPE_CUSTOM_ENUM,
                .u = .{ .custom_enum_setting = c.AsphodelCustomEnumSetting_t{
                    .nvm_word = 65,
                    .nvm_word_byte = 1,
                    .custom_enum_index = 0,
                } },
            },
        },
        .{
            .str = "<AsphodelSettingInfo {name=b'Custom CT Sensitivity (A/V)', name_length=27, default_bytes=0x3f,0x80,0x00,0x00, default_bytes_length=4, setting_type=8 (SETTING_TYPE_FLOAT), u=<AsphodelFloatSetting {nvm_word=66, minimum=-inf, maximum=inf, unit_type=0 (UNIT_TYPE_NONE), scale=1.0, offset=0.0}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 27,
                .name = "Custom CT Sensitivity (A/V)",
                .default_bytes_length = 4,
                .default_bytes = &[4]u8{ 0x3f, 0x80, 0x00, 0x00 },
                .setting_type = c.SETTING_TYPE_FLOAT,
                .u = .{ .float_setting = c.AsphodelFloatSetting_t{
                    .nvm_word = 66,
                    .minimum = -std.math.inf(f32),
                    .maximum = std.math.inf(f32),
                    .unit_type = c.UNIT_TYPE_NONE,
                    .scale = 1.0,
                    .offset = 0.0,
                } },
            },
        },
        .{
            .str = "<AsphodelSettingInfo {name=b'CT Turns', name_length=8, default_bytes=0x3f,0x80,0x00,0x00, default_bytes_length=4, setting_type=8 (SETTING_TYPE_FLOAT), u=<AsphodelFloatSetting {nvm_word=67, minimum=-inf, maximum=inf, unit_type=0 (UNIT_TYPE_NONE), scale=1.0, offset=0.0}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 8,
                .name = "CT Turns",
                .default_bytes_length = 4,
                .default_bytes = &[4]u8{ 0x3f, 0x80, 0x00, 0x00 },
                .setting_type = c.SETTING_TYPE_FLOAT,
                .u = .{ .float_setting = c.AsphodelFloatSetting_t{
                    .nvm_word = 67,
                    .minimum = -std.math.inf(f32),
                    .maximum = std.math.inf(f32),
                    .unit_type = c.UNIT_TYPE_NONE,
                    .scale = 1.0,
                    .offset = 0.0,
                } },
            },
        },
        .{
            .str = "<AsphodelSettingInfo {name=b'Default Filter Cutoff', name_length=21, default_bytes=0x00,0x00,0x00,0x0f, default_bytes_length=4, setting_type=7 (SETTING_TYPE_INT32_SCALED), u=<AsphodelInt32ScaledSetting {nvm_word=64, minimum=0, maximum=24, unit_type=15 (UNIT_TYPE_HZ), scale=1.0, offset=0.0}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 21,
                .name = "Default Filter Cutoff",
                .default_bytes_length = 4,
                .default_bytes = &[4]u8{ 0x00, 0x00, 0x00, 0x0f },
                .setting_type = c.SETTING_TYPE_INT32_SCALED,
                .u = .{ .int32_scaled_setting = c.AsphodelInt32ScaledSetting_t{
                    .nvm_word = 64,
                    .minimum = 0,
                    .maximum = 24,
                    .unit_type = c.UNIT_TYPE_HZ,
                    .scale = 1.0,
                    .offset = 0.0,
                } },
            },
        },
        .{
            .str = "<AsphodelSettingInfo {name=b'Fast Data', name_length=9, default_bytes=0x00, default_bytes_length=1, setting_type=1 (SETTING_TYPE_BOOLEAN), u=<AsphodelByteSetting {nvm_word=65, nvm_word_byte=0}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 9,
                .name = "Fast Data",
                .default_bytes_length = 1,
                .default_bytes = &[1]u8{0},
                .setting_type = c.SETTING_TYPE_BOOLEAN,
                .u = .{ .byte_setting = c.AsphodelByteSetting_t{
                    .nvm_word = 65,
                    .nvm_word_byte = 0,
                } },
            },
        },
        .{
            .str = "<AsphodelSettingInfo {name=b'Two Phase Only', name_length=14, default_bytes=0x00, default_bytes_length=1, setting_type=1 (SETTING_TYPE_BOOLEAN), u=<AsphodelByteSetting {nvm_word=65, nvm_word_byte=2}>}>",
            .expected = c.AsphodelSettingInfo_t{
                .name_length = 14,
                .name = "Two Phase Only",
                .default_bytes_length = 1,
                .default_bytes = &[1]u8{0},
                .setting_type = c.SETTING_TYPE_BOOLEAN,
                .u = .{ .byte_setting = c.AsphodelByteSetting_t{
                    .nvm_word = 65,
                    .nvm_word_byte = 2,
                } },
            },
        },
    };

    for (test_cases) |test_case| {
        try testSetting(test_case.str, test_case.expected);
    }
}

fn trimPrefix(s: []const u8, comptime prefix: []const u8) ![]const u8 {
    if (std.mem.startsWith(u8, s, prefix)) {
        return s[prefix.len..];
    } else {
        return error.PrefixNotFound;
    }
}

fn trimSuffix(s: []const u8, comptime suffix: []const u8) ![]const u8 {
    if (std.mem.endsWith(u8, s, suffix)) {
        return s[0 .. s.len - suffix.len];
    } else {
        return error.SuffixNotFound;
    }
}

fn readSettingUnion(type_str: []const u8, values: []const u8, setting_info: *c.AsphodelSettingInfo_t) !void {
    // NOTE: setting_info.setting_type has been set before calling this function
    if (std.mem.eql(u8, type_str, "AsphodelByteSetting") and (setting_info.setting_type == c.SETTING_TYPE_BYTE or
        setting_info.setting_type == c.SETTING_TYPE_BOOLEAN or
        setting_info.setting_type == c.SETTING_TYPE_UNIT_TYPE or
        setting_info.setting_type == c.SETTING_TYPE_CHANNEL_TYPE))
    {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "nvm_word_byte", .T = u8 },
        }, &setting_info.u.byte_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelByteArraySetting") and setting_info.setting_type == c.SETTING_TYPE_BYTE_ARRAY) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "maximum_length", .T = u8 },
            .{ .name = "length_nvm_word", .T = u16 },
            .{ .name = "length_nvm_word_byte", .T = u8 },
        }, &setting_info.u.byte_array_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelStringSetting") and setting_info.setting_type == c.SETTING_TYPE_STRING) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "maximum_length", .T = u8 },
        }, &setting_info.u.string_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelInt32Setting") and setting_info.setting_type == c.SETTING_TYPE_INT32) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "minimum", .T = i32 },
            .{ .name = "maximum", .T = i32 },
        }, &setting_info.u.int32_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelInt32ScaledSetting") and setting_info.setting_type == c.SETTING_TYPE_INT32_SCALED) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "minimum", .T = i32 },
            .{ .name = "maximum", .T = i32 },
            .{ .name = "unit_type", .T = u8 },
            .{ .name = "scale", .T = f32 },
            .{ .name = "offset", .T = f32 },
        }, &setting_info.u.int32_scaled_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelFloatSetting") and setting_info.setting_type == c.SETTING_TYPE_FLOAT) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "minimum", .T = f32 },
            .{ .name = "maximum", .T = f32 },
            .{ .name = "unit_type", .T = u8 },
            .{ .name = "scale", .T = f32 },
            .{ .name = "offset", .T = f32 },
        }, &setting_info.u.float_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelFloatArraySetting") and setting_info.setting_type == c.SETTING_TYPE_FLOAT_ARRAY) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "minimum", .T = f32 },
            .{ .name = "maximum", .T = f32 },
            .{ .name = "unit_type", .T = u8 },
            .{ .name = "scale", .T = f32 },
            .{ .name = "offset", .T = f32 },
            .{ .name = "maximum_length", .T = u8 },
            .{ .name = "length_nvm_word", .T = u16 },
            .{ .name = "length_nvm_word_byte", .T = u8 },
        }, &setting_info.u.float_array_setting);
    } else if (std.mem.eql(u8, type_str, "AsphodelCustomEnumSetting") and setting_info.setting_type == c.SETTING_TYPE_CUSTOM_ENUM) {
        try fillSettingUnion(values, &[_]SettingUnionField{
            .{ .name = "nvm_word", .T = u16 },
            .{ .name = "nvm_word_byte", .T = u8 },
            .{ .name = "custom_enum_index", .T = u8 },
        }, &setting_info.u.custom_enum_setting);
    } else {
        return error.InvalidSettingUnion;
    }
}

const SettingUnionField = struct {
    name: []const u8,
    T: type,
};

fn fillSettingUnion(values: []const u8, comptime fields: []const SettingUnionField, u: anytype) !void {
    var it = std.mem.splitSequence(u8, values, ", ");
    inline for (fields) |field| {
        const field_value_str = it.next() orelse return error.InvalidSettingUnion;
        var field_split_it = std.mem.splitScalar(u8, field_value_str, '=');
        const field_name = field_split_it.first();
        const field_value_raw = field_split_it.next() orelse return error.InvalidSettingUnion;
        var field_value_it = std.mem.splitScalar(u8, field_value_raw, ' ');
        const field_value = field_value_it.first();

        if (!std.mem.eql(u8, field_name, field.name)) return error.InvalidSettingUnion;

        switch (@typeInfo(field.T)) {
            .int => {
                @field(u, field.name) = std.fmt.parseInt(field.T, field_value, 10) catch return error.InvalidSettingUnion;
            },
            .float => {
                @field(u, field.name) = std.fmt.parseFloat(field.T, field_value) catch return error.InvalidSettingUnion;
            },
            else => @compileError("unsupported type"),
        }
    }
    if (it.next() != null) return error.InvalidSettingUnion;
}

fn readSettingDefaultBytes(allocator: Allocator, default_bytes_str: []const u8, default_bytes_length: u8) ![]const u8 {
    if (default_bytes_str.len == 0) {
        if (default_bytes_length == 0) {
            return "";
        } else {
            return error.InvalidDefaultBytes;
        }
    }

    var list = try std.array_list.Managed(u8).initCapacity(allocator, 1);
    errdefer list.deinit();

    var it = std.mem.splitScalar(u8, default_bytes_str, ',');
    while (it.next()) |item| {
        const value = std.fmt.parseUnsigned(u8, item, 0) catch return error.InvalidDefaultBytes;
        try list.append(value);
    }

    if (list.items.len != default_bytes_length) return error.InvalidDefaultBytes;
    return try list.toOwnedSlice();
}

test "readSettingDefaultBytes" {
    {
        const bytes = try readSettingDefaultBytes(std.testing.allocator, "", 0);
        defer std.testing.allocator.free(bytes);
        try std.testing.expectEqualSlices(u8, bytes, "");
    }
    {
        const bytes = try readSettingDefaultBytes(std.testing.allocator, "0x00", 1);
        defer std.testing.allocator.free(bytes);
        try std.testing.expectEqualSlices(u8, bytes, "\x00");
    }
    {
        const bytes = try readSettingDefaultBytes(std.testing.allocator, "0x00,0x01", 2);
        defer std.testing.allocator.free(bytes);
        try std.testing.expectEqualSlices(u8, bytes, "\x00\x01");
    }
    {
        try std.testing.expectError(error.InvalidDefaultBytes, readSettingDefaultBytes(std.testing.allocator, "0x00", 0));
        try std.testing.expectError(error.InvalidDefaultBytes, readSettingDefaultBytes(std.testing.allocator, "x", 1));
    }
}

fn readSettingName(allocator: Allocator, str: []const u8, name_length: u8) ![:0]const u8 {
    // this code is trying to read a string formatted by python's "{}".format(some_bytes) with the leading 'b' removed
    var list = try std.array_list.Managed(u8).initCapacity(allocator, name_length + 1);
    errdefer list.deinit();

    if (str.len < 2) return error.InvalidName;

    const quote = str[0];
    if (quote != '\'' and quote != '"') return error.InvalidName;
    if (quote != str[str.len - 1]) return error.InvalidName;

    var i: usize = 1;
    const stop = str.len - 1;

    while (i < stop) : (i += 1) {
        const ch = str[i];

        if (ch != '\\') {
            try list.append(ch);
            continue;
        }

        // must be an escape sequence

        if (i + 1 >= stop) return error.InvalidName;
        const escape = str[i + 1];
        i += 1;

        switch (escape) {
            'n' => try list.append('\n'),
            'r' => try list.append('\r'),
            't' => try list.append('\t'),
            'a' => try list.append(0x07),
            'b' => try list.append(0x08),
            'v' => try list.append(0x0B),
            'f' => try list.append(0x0C),
            '\\' => try list.append('\\'),
            '\'' => try list.append('\''),
            '"' => try list.append('"'),
            'x' => {
                if (i + 2 >= stop) return error.InvalidName;
                const hex = std.fmt.charToDigit(str[i + 1], 16) catch return error.InvalidName;
                const hex2 = std.fmt.charToDigit(str[i + 2], 16) catch return error.InvalidName;
                i += 2;
                try list.append(hex << 4 | hex2);
            },
            else => return error.InvalidName,
        }
    }

    const name: [:0]const u8 = try list.toOwnedSliceSentinel(0);
    if (name.len != name_length) return error.InvalidName;
    return name;
}

test "readSettingName" {
    {
        const name = try readSettingName(std.testing.allocator, "''", 0);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "");
    }
    {
        const name = try readSettingName(std.testing.allocator, "\"\"", 0);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "");
    }
    {
        const name = try readSettingName(std.testing.allocator, "\"'\"", 1);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "'");
    }
    {
        const name = try readSettingName(std.testing.allocator, "'\"'", 1);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "\"");
    }
    {
        const name = try readSettingName(std.testing.allocator, "'test'", 4);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "test");
    }
    {
        const name = try readSettingName(std.testing.allocator, "'\\x00\\xFF'", 2);
        defer std.testing.allocator.free(name);
        try std.testing.expectEqualSlices(u8, name, "\x00\xFF");
    }
}

fn readCustomEnums(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("custom_enums") orelse return;

    switch (kv.value) {
        .object => |object| {
            const count = object.count();
            device_info.custom_enum_count = count;

            if (count == 0) {
                // need to allocate something to make custom_enum_lengths non-null
                const a = try allocator.alloc(u8, 1);
                a[0] = 0; // not strictly necessary since custom_enum_count is 0
                device_info.custom_enum_lengths = a.ptr;
                return;
            }

            // allocate top level memory
            var lengths_alloc: []u8 = try allocator.alloc(u8, device_info.custom_enum_count);
            device_info.custom_enum_lengths = lengths_alloc.ptr;
            errdefer allocator.free(lengths_alloc);
            errdefer device_info.custom_enum_lengths = null;

            var top_level_names: []?[*]?[*:0]const u8 = try allocator.alloc(?[*]?[*:0]const u8, device_info.custom_enum_count);
            @memset(top_level_names, null);
            device_info.custom_enum_values = top_level_names.ptr;
            errdefer {
                // NOTE: lengths_alloc is still valid at this point
                for (top_level_names, 0..) |maybe_array, i| {
                    if (maybe_array) |array| {
                        const length = lengths_alloc[i];
                        const slice = array[0..length];
                        for (slice) |maybe_str| {
                            if (maybe_str) |str| {
                                allocator.free(std.mem.span(str));
                            }
                        }
                        allocator.free(slice);
                    }
                }
                allocator.free(top_level_names);
                device_info.custom_enum_values = null;
            }

            for (0..count) |i| {
                var buffer: [32]u8 = undefined;
                const key = std.fmt.bufPrint(&buffer, "{d}", .{i}) catch return error.InvalidJson;
                const value = object.get(key) orelse return error.InvalidJson;
                switch (value) {
                    .array => |array| {
                        lengths_alloc[i] = std.math.cast(u8, array.items.len) orelse return error.InvalidJson;
                        if (array.items.len == 0) continue; // don't allocate anything

                        const names_array: []?[*:0]const u8 = try allocator.alloc(?[*:0]const u8, array.items.len);
                        @memset(names_array, null);
                        top_level_names[i] = names_array.ptr;
                        // NOTE: the top level errdefer will handle any cleanup

                        for (array.items, 0..) |item, j| {
                            switch (item) {
                                .string => |str| names_array[j] = try allocator.dupeZ(u8, str),
                                .null => {}, // allowed
                                else => return error.InvalidJson,
                            }
                        }
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        .null => return,
        else => return error.InvalidJson,
    }
}

fn readSettingCategories(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("setting_categories") orelse return;

    switch (kv.value) {
        .array => |outer_array| {
            device_info.setting_category_count = outer_array.items.len;
            device_info.setting_category_count_known = 1;

            if (outer_array.items.len == 0) return; // bail out before doing allocations

            // do the top level allocations now, as it simplifies the errdefer code

            var names_alloc: []?[*:0]const u8 = try allocator.alloc(?[*:0]const u8, device_info.setting_category_count);
            @memset(names_alloc, null);
            device_info.setting_category_names = @ptrCast(names_alloc.ptr); // zig wouldn't coerece between these for some reason
            errdefer {
                for (names_alloc) |maybe_name| {
                    if (maybe_name) |name| {
                        allocator.free(std.mem.span(name));
                    }
                }
                allocator.free(names_alloc);
                device_info.setting_category_names = null;
            }

            var lengths_alloc: []u8 = try allocator.alloc(u8, device_info.setting_category_count);
            device_info.setting_category_settings_lengths = lengths_alloc.ptr;
            errdefer allocator.free(lengths_alloc);
            errdefer device_info.setting_category_settings_lengths = null;

            var settings_alloc: []?[*]u8 = try allocator.alloc(?[*]u8, device_info.setting_category_count);
            @memset(settings_alloc, null);
            device_info.setting_category_settings = settings_alloc.ptr;
            errdefer {
                // NOTE: lengths_alloc is still valid at this point
                for (settings_alloc, 0..) |maybe_settings, i| {
                    if (maybe_settings) |settings| {
                        const length = lengths_alloc[i];
                        allocator.free(settings[0..length]);
                    }
                }
                allocator.free(settings_alloc);
                device_info.setting_category_settings = null;
            }

            for (outer_array.items, 0..) |outer_item, i| {
                switch (outer_item) {
                    .array => |pair| {
                        if (pair.items.len != 2) return error.InvalidJson;

                        switch (pair.items[0]) {
                            .string => |str| names_alloc[i] = try allocator.dupeZ(u8, str),
                            .null => names_alloc[i] = null, // allowed
                            else => return error.InvalidJson,
                        }

                        switch (pair.items[1]) {
                            .array => |inner_array| {
                                const settings_length: u8 = std.math.cast(u8, inner_array.items.len) orelse return error.InvalidJson;

                                var list = try allocator.alloc(u8, settings_length);
                                settings_alloc[i] = list.ptr;
                                lengths_alloc[i] = settings_length;

                                for (inner_array.items, 0..) |item, j| {
                                    switch (item) {
                                        .integer => |integer| list[j] = std.math.cast(u8, integer) orelse return error.InvalidJson,
                                        else => return error.InvalidJson, // no nulls inside the list
                                    }
                                }
                            },
                            .null => {
                                settings_alloc[i] = null; // not strictly necessary
                                lengths_alloc[i] = 0;
                            },
                            else => return error.InvalidJson,
                        }
                    },
                    else => return error.InvalidJson, // null not allowed at this position
                }
            }
        },
        .null => {},
        else => return error.InvalidJson,
    }
}

fn readDeviceMode(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const support_kv = map.fetchSwapRemove("supports_device_mode");
    const mode_kv = map.fetchSwapRemove("device_mode");

    if (support_kv) |kv| {
        switch (kv.value) {
            .bool => |b| {
                const value = try allocator.create(u8);
                value.* = if (b) 1 else 0;
                device_info.supports_device_mode = value;
            },
            .null => {},
            else => return error.InvalidJson,
        }
    }

    if (mode_kv) |kv| {
        switch (kv.value) {
            .integer => |i| device_info.device_mode = std.math.cast(u8, i) orelse return error.InvalidJson,
            .null => {},
            else => return error.InvalidJson,
        }
    }
}

fn readRFPowerInfo(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const ctrl_vars_kv = map.fetchSwapRemove("rf_power_ctrl_vars");
    if (ctrl_vars_kv) |kv| {
        try readCtrlVarIndexes(allocator, kv.value, &device_info.rf_power_ctrl_var_count_known, &device_info.rf_power_ctrl_var_count, &device_info.rf_power_ctrl_vars);
    }

    const status_kv = map.fetchSwapRemove("rf_power_status");
    if (status_kv) |kv| {
        switch (kv.value) {
            .bool => |b| device_info.rf_power_enabled = if (b) 1 else 0,
            .null => {},
            else => return error.InvalidJson,
        }
    }
}

fn readRadioInfo(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const ctrl_vars_kv = map.fetchSwapRemove("radio_ctrl_vars");
    if (ctrl_vars_kv) |kv| {
        try readCtrlVarIndexes(allocator, kv.value, &device_info.radio_ctrl_var_count_known, &device_info.radio_ctrl_var_count, &device_info.radio_ctrl_vars);
    }

    const default_serial_kv = map.fetchSwapRemove("radio_default_serial");
    if (default_serial_kv) |kv| {
        switch (kv.value) {
            .integer => |i| {
                const value = try allocator.create(u32);
                value.* = std.math.cast(u32, i) orelse return error.InvalidJson;
                device_info.radio_default_serial = value;
            },
            .null => {},
            else => return error.InvalidJson,
        }
    }

    const support_kv = map.fetchSwapRemove("radio_scan_power");
    if (support_kv) |kv| {
        switch (kv.value) {
            .bool => |b| {
                const value = try allocator.create(u8);
                value.* = if (b) 1 else 0;
                device_info.radio_scan_power_supported = value;
            },
            .null => {},
            else => return error.InvalidJson,
        }
    }
}

fn readCtrlVarIndexes(allocator: Allocator, value: std.json.Value, known: *u8, count: *usize, indexes: *?[*]u8) !void {
    switch (value) {
        .array => |array| {
            known.* = 1;
            count.* = array.items.len;
            if (array.items.len == 0) return; // don't allocate anything

            const allocated: []u8 = try allocator.alloc(u8, array.items.len);
            errdefer allocator.free(allocated);

            indexes.* = allocated.ptr;
            errdefer indexes.* = null;

            for (array.items, 0..) |item, i| {
                allocated[i] = try readIntegerFromValue(u8, item);
            }
        },
        .null => {},
        else => return error.InvalidJson,
    }
}

fn readNvm(allocator: Allocator, map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("nvm") orelse return;

    switch (kv.value) {
        .string => |str| {
            if (str.len & 1 != 0) return error.InvalidJson;
            device_info.nvm_size = str.len / 2;
            const nvm = try allocator.alloc(u8, device_info.nvm_size);
            errdefer allocator.free(nvm);
            device_info.nvm = nvm.ptr;
            errdefer device_info.nvm = null;
            _ = std.fmt.hexToBytes(nvm, str) catch return error.InvalidJson;
        },
        .null => return, // ignore any null values
        else => return error.InvalidJson,
    }
}

fn readTagLocations(map: *std.json.ObjectMap, device_info: *c.AsphodelDeviceInfo_t) !void {
    const kv = map.fetchSwapRemove("tag_locations") orelse return;

    var i: usize = 0;
    switch (kv.value) {
        .array => |outer_array| {
            if (outer_array.items.len != 3) return error.InvalidJson;
            for (outer_array.items) |outer_item| {
                switch (outer_item) {
                    .array => |inner_array| {
                        if (inner_array.items.len != 2) return error.InvalidJson;
                        for (inner_array.items) |inner_item| {
                            device_info.tag_locations[i] = try readIntegerFromValue(usize, inner_item);
                            i += 1;
                        }
                    },
                    else => return error.InvalidJson,
                }
            }
        },
        else => return error.InvalidJson,
    }
}

test "empty device info json" {
    const device_info = c.AsphodelDeviceInfo_t{};
    const json = try createJsonFromDeviceInfo(std.testing.allocator, &device_info, .{
        .json_options = .{ .whitespace = .indent_2 },
        .include_version = false,
    });
    defer std.testing.allocator.free(json);

    const expected =
        \\{
        \\  "supports_bootloader": false,
        \\  "supports_radio": false,
        \\  "supports_remote": false,
        \\  "supports_rf_power": false
        \\}
    ;

    try std.testing.expectEqualStrings(expected, json);
}

test "basic json to device_info" {
    const input =
        \\{
        \\  "serial_number": "test_sn",
        \\  "supports_bootloader": true
        \\}
    ;

    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    const allocator = arena.allocator();
    defer arena.deinit();

    var device_info = c.AsphodelDeviceInfo_t{};
    var excess: []const u8 = undefined;
    try fillDeviceInfoFromJson(allocator, input, &device_info, &excess);

    try std.testing.expectEqualStrings(std.mem.span(device_info.serial_number), "test_sn");
    try std.testing.expect(device_info.supports_bootloader == 1);
    try std.testing.expectEqualStrings(excess, "{}");
}

test "excess elements" {
    const input = "{\"bogus\":\"test_value\"}";

    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    const allocator = arena.allocator();
    defer arena.deinit();

    var device_info = c.AsphodelDeviceInfo_t{};
    var excess: []const u8 = undefined;
    try fillDeviceInfoFromJson(allocator, input, &device_info, &excess);

    try std.testing.expectEqualStrings(excess, input);
}
