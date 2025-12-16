const std = @import("std");
const c = @import("root.zig").c;
const Allocator = std.mem.Allocator;

export fn asphodel_get_device_info_summary(device_info: *const c.AsphodelDeviceInfo_t, summary_out: *[*:0]const u8) c_int {
    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
    defer arena.deinit();

    const summary = createSummaryFromDeviceInfo(arena.allocator(), device_info) catch {
        return c.ASPHODEL_NO_MEM;
    };

    const duplicate = std.heap.c_allocator.dupeZ(u8, summary) catch {
        return c.ASPHODEL_NO_MEM;
    };

    summary_out.* = duplicate.ptr;

    return c.ASPHODEL_SUCCESS;
}

pub fn createSummaryFromDeviceInfo(allocator: Allocator, device_info: *const c.AsphodelDeviceInfo_t) ![:0]u8 {
    // First allocation of 4000 bytes gives us a good balance. The smallest summaries will be around this mark.
    var out = try std.io.Writer.Allocating.initCapacity(allocator, 4000);
    const writer = &out.writer;

    if (device_info.serial_number) |serial_number| {
        try writer.print("Serial Number: {s}\n", .{serial_number});
    }

    if (device_info.user_tag_1) |user_tag_1| {
        try writer.print("User Tag 1: {s}\n", .{user_tag_1});
    }

    if (device_info.user_tag_2) |user_tag_2| {
        try writer.print("User Tag 2: {s}\n", .{user_tag_2});
    }

    if (device_info.location_string) |location_string| {
        try writer.print("Location String: {s}\n", .{location_string});
    }

    if (device_info.max_incoming_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try writer.print("Max Incoming Param Len: {d}\n", .{device_info.max_incoming_param_length});
    }

    if (device_info.max_outgoing_param_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try writer.print("Max Outgoing Param Len: {d}\n", .{device_info.max_outgoing_param_length});
    }

    if (device_info.stream_packet_length != 0) {
        // 0 isn't a valid option, so don't clutter output if it's missing
        try writer.print("Stream Packet Length: {d}\n", .{device_info.stream_packet_length});
    }

    if (device_info.supports_radio != 0) {
        if (device_info.remote_max_incoming_param_length != 0) {
            // 0 isn't a valid option, so don't clutter output if it's missing
            try writer.print("Remote Max Incoming Param Len: {d}\n", .{device_info.remote_max_incoming_param_length});
        }

        if (device_info.remote_max_outgoing_param_length != 0) {
            // 0 isn't a valid option, so don't clutter output if it's missing
            try writer.print("Remote Max Outgoing Param Len: {d}\n", .{device_info.remote_max_outgoing_param_length});
        }

        if (device_info.remote_stream_packet_length != 0) {
            // 0 isn't a valid option, so don't clutter output if it's missing
            try writer.print("Remote Stream Packet Length: {d}\n", .{device_info.remote_stream_packet_length});
        }
    }

    if (device_info.protocol_version) |protocol_version| {
        try writer.print("Protocol Version: {s}\n", .{protocol_version});
    }

    if (device_info.board_info_name) |board_info_name| {
        try writer.print("Board Info: {s} rev {d}\n", .{ board_info_name, device_info.board_info_rev });
    }

    if (device_info.build_info) |build_info| {
        try writer.print("Build Info: {s}\n", .{build_info});
    }

    if (device_info.build_date) |build_date| {
        try writer.print("Build Date: {s}\n", .{build_date});
    }

    if (device_info.commit_id) |commit_id| {
        try writer.print("Commit ID: {s}\n", .{commit_id});
    }

    if (device_info.repo_branch) |repo_branch| {
        try writer.print("Repo Branch: {s}\n", .{repo_branch});
    }

    if (device_info.repo_name) |repo_name| {
        try writer.print("Repo Name: {s}\n", .{repo_name});
    }

    if (device_info.chip_family) |chip_family| {
        try writer.print("Chip Family: {s}\n", .{chip_family});
    }

    if (device_info.chip_model) |chip_model| {
        try writer.print("Chip Model: {s}\n", .{chip_model});
    }

    if (device_info.chip_id) |chip_id| {
        try writer.print("Chip ID: {s}\n", .{chip_id});
    }

    try writer.print("Tag Locations: ({d}, {d}), ({d}, {d}), ({d}, {d})\n", .{ device_info.tag_locations[0], device_info.tag_locations[1], device_info.tag_locations[2], device_info.tag_locations[3], device_info.tag_locations[4], device_info.tag_locations[5] });

    if (device_info.nvm_modified) |nvm_modified| {
        if (nvm_modified.* != 0) {
            try writer.writeAll("NVM Modified: Yes\n");
        } else {
            try writer.writeAll("NVM Modified: No\n");
        }
    } else {
        try writer.writeAll("NVM Modified: <UNKNOWN>\n");
    }

    if (device_info.nvm_hash) |nvm_hash| {
        try writer.print("NVM Hash: {s}\n", .{nvm_hash});
    } else {
        try writer.writeAll("NVM Hash: <N/A>\n");
    }

    if (device_info.setting_hash) |setting_hash| {
        try writer.print("Setting Hash: {s}\n", .{setting_hash});
    } else {
        try writer.writeAll("Setting Hash: <N/A>\n");
    }

    if (device_info.bootloader_info) |bootloader_info| {
        try writer.print("Bootloader Info: {s}\n", .{bootloader_info});
    }

    try writer.writeAll("\n");

    try writer.print("Library Protocol Version: {s}\n", .{c.asphodel_get_library_protocol_version_string()});
    try writer.print("Library Build Info: {s}\n", .{c.asphodel_get_library_build_info()});
    try writer.print("Library Build Date: {s}\n", .{c.asphodel_get_library_build_date()});

    try writer.writeAll("\n");

    var device_decoder: ?*c.AsphodelDeviceDecoder_t = null;
    defer if (device_decoder) |d| d.free_decoder.?(d);

    if (device_info.stream_count_known != 0) {
        try writer.print("Stream Filler Bits: {d}\n", .{device_info.stream_filler_bits});
        try writer.print("Stream ID Bits: {d}\n", .{device_info.stream_id_bits});

        if (device_info.stream_count > 1 and device_info.stream_count <= 255) {
            const active_streams: []u8 = try std.heap.c_allocator.alloc(u8, device_info.stream_count);
            defer std.heap.c_allocator.free(active_streams);

            for (0..device_info.stream_count) |i| {
                active_streams[i] = @intCast(i);
            }

            // ignore the return value, as we will just carry on with a null decoder
            _ = c.asphodel_create_device_info_decoder(device_info, active_streams.ptr, @intCast(active_streams.len), &device_decoder);

            if (device_decoder) |d| {
                try writer.print("Stream Used Bits: {d}\n", .{d.used_bits});
            }
        }

        try writer.writeAll("\n");
        try writer.writeAll("Streams\n");

        var total_packet_rate: f64 = 0.0;

        if (device_info.streams) |streams| {
            for (streams[0..device_info.stream_count], 0..) |*stream, i| {
                const rate_info: ?*const c.AsphodelStreamRateInfo_t = if (device_info.stream_rates) |stream_rates| &stream_rates[i] else null;

                var stream_decoder: ?*c.AsphodelStreamDecoder_t = null;
                if (device_decoder) |d| {
                    if (d.streams > i) {
                        stream_decoder = d.decoders[i];
                    }
                }

                try writeStreamSummary(writer, stream, i, rate_info, stream_decoder);

                total_packet_rate += stream.rate;
            }
        }

        try writer.writeAll("\n");
        try writer.print("Total Rate: {d:.1} packets/s\n", .{total_packet_rate});

        const stream_bandwidth = total_packet_rate * @as(f64, @floatFromInt(device_info.stream_packet_length * 8));
        try writer.writeAll("Stream Bandwidth: ");
        try writeBitrate(writer, stream_bandwidth);
        try writer.writeAll("\n"); // for the end of the stream bandwidth line

        try writer.writeAll("\n");
    }

    if (device_info.channel_count_known != 0) {
        try writer.writeAll("Channels\n");

        var streams: ?[]const c.AsphodelStreamInfo_t = null;
        if (device_info.stream_count_known != 0) {
            if (device_info.streams) |s| {
                streams = s[0..device_info.stream_count];
            }
        }

        if (device_info.channels) |channels| {
            for (channels[0..device_info.channel_count], 0..) |*channel, i| {
                var calibration: ?*const c.AsphodelChannelCalibration_t = null;
                if (device_info.channel_calibrations) |calibrations| {
                    calibration = calibrations[i];
                }

                try writeChannelSummary(writer, channel, i, calibration, streams, device_decoder);
            }
        }

        try writer.writeAll("\n");
    }

    if (device_info.supply_count_known != 0) {
        try writer.writeAll("Supplies\n");

        if (device_info.supplies) |supplies| {
            for (supplies[0..device_info.supply_count], 0..) |*supply, i| {
                var result: ?*const c.AsphodelSupplyResult_t = null;
                if (device_info.supply_results) |supply_results| {
                    result = &supply_results[i];
                }
                try writeSupplySummary(writer, supply, i, result);
            }
        }

        try writer.writeAll("\n");
    }

    if (device_info.ctrl_var_count_known != 0) {
        try writer.writeAll("Control Variables\n");

        if (device_info.ctrl_vars) |ctrl_vars| {
            for (ctrl_vars[0..device_info.ctrl_var_count], 0..) |*ctrl_var, i| {
                try writeCtrlVarSummary(writer, ctrl_var, i);
            }
        }

        try writer.writeAll("\n");
    }

    var wrote_rf_power_or_radio_ctrl_vars: bool = false;

    if (device_info.rf_power_ctrl_var_count_known != 0) {
        if (device_info.rf_power_ctrl_var_count > 0) {
            wrote_rf_power_or_radio_ctrl_vars = true;
            try writer.writeAll("RF Power Control Variables: [");
            for (device_info.rf_power_ctrl_vars[0..device_info.rf_power_ctrl_var_count], 0..) |ctrl_var_index, i| {
                if (i == 0) {
                    try writer.print("{d}", .{ctrl_var_index});
                } else {
                    try writer.print(", {d}", .{ctrl_var_index});
                }
            }
            try writer.writeAll("]\n");
        }
    }

    if (device_info.radio_ctrl_var_count_known != 0) {
        if (device_info.radio_ctrl_var_count > 0) {
            wrote_rf_power_or_radio_ctrl_vars = true;
            try writer.writeAll("Radio Control Variables: [");
            for (device_info.radio_ctrl_vars[0..device_info.radio_ctrl_var_count], 0..) |ctrl_var_index, i| {
                if (i == 0) {
                    try writer.print("{d}", .{ctrl_var_index});
                } else {
                    try writer.print(", {d}", .{ctrl_var_index});
                }
            }
            try writer.writeAll("]\n");
        }
    }

    if (wrote_rf_power_or_radio_ctrl_vars) {
        try writer.writeAll("\n");
    }

    if (device_info.setting_count_known != 0) {
        try writer.writeAll("Settings\n");

        if (device_info.settings) |settings| {
            var nvm: ?[]const u8 = undefined;
            if (device_info.nvm_size != 0 and device_info.nvm != null) {
                nvm = device_info.nvm[0..device_info.nvm_size];
            } else {
                nvm = null;
            }

            for (settings[0..device_info.setting_count], 0..) |*setting, i| {
                try writeSettingSummary(writer, setting, i, nvm, device_info);
            }
        }

        try writer.writeAll("\n");
    }

    if (device_info.custom_enum_count != 0) {
        if (device_info.custom_enum_lengths) |custom_enum_lengths| {
            if (device_info.custom_enum_values) |custom_enum_values| {
                try writer.writeAll("Setting Custom Enums\n");

                for (custom_enum_lengths[0..device_info.custom_enum_count], 0..) |length, i| {
                    if (custom_enum_values[i]) |values| {
                        try writer.print("  Custom Enum {d}\n", .{i});
                        for (values[0..length], 0..) |value, j| {
                            if (value) |v| {
                                try writer.print("    {d}: {s}\n", .{ j, v });
                            } else {
                                try writer.print("    {d}: <UNKNOWN>\n", .{j});
                            }
                        }
                    }
                }

                try writer.writeAll("\n");
            }
        }
    }

    if (device_info.setting_category_count_known != 0) {
        if (device_info.setting_category_settings_lengths) |settings_lengths| {
            if (device_info.setting_category_settings) |settings| {
                if (device_info.setting_category_names) |names| {
                    try writer.writeAll("Setting Categories\n");

                    for (0..device_info.setting_category_count) |i| {
                        const category_length = settings_lengths[i];
                        const category_name = names[i];
                        if (category_name) |name| {
                            try writer.print("  {s}: ", .{name});
                        } else {
                            try writer.writeAll("  <UNKNOWN>: ");
                        }

                        const category_settings = settings[i];
                        if (category_settings) |s| {
                            try writer.writeAll("[");
                            for (0..category_length) |j| {
                                if (j == 0) {
                                    try writer.print("{d}", .{s[j]});
                                } else {
                                    try writer.print(", {d}", .{s[j]});
                                }
                            }
                            try writer.writeAll("]\n");
                        } else {
                            try writer.writeAll("<UNKNOWN>\n");
                        }
                    }

                    try writer.writeAll("\n");
                }
            }
        }
    }

    var wrote_led_or_rgb: bool = false;
    if (device_info.rgb_count_known != 0) {
        wrote_led_or_rgb = true;
        try writer.print("RGB Count: {d}\n", .{device_info.rgb_count});
    }

    if (device_info.led_count_known != 0) {
        wrote_led_or_rgb = true;
        try writer.print("LED Count: {d}\n", .{device_info.led_count});
    }

    if (wrote_led_or_rgb) {
        try writer.writeAll("\n");
    }

    if (device_info.nvm_size != 0) {
        try writer.writeAll("NVM\n");

        if (device_info.nvm) |nvm| {
            try writeNvm(writer, nvm[0..device_info.nvm_size]);
        }

        try writer.writeAll("\n");
    }

    return out.toOwnedSliceSentinel(0);
}

fn writeStreamSummary(
    writer: *std.io.Writer,
    stream: *const c.AsphodelStreamInfo_t,
    stream_index: usize,
    rate_info: ?*const c.AsphodelStreamRateInfo_t,
    decoder: ?*const c.AsphodelStreamDecoder_t,
) !void {
    try writer.print("  Stream {d}\n", .{stream_index});

    try writer.writeAll("    channels: [");
    if (stream.channel_count > 0) {
        for (stream.channel_index_list[0..stream.channel_count], 0..) |channel_index, j| {
            if (j == 0) {
                try writer.print("{d}", .{channel_index});
            } else {
                try writer.print(", {d}", .{channel_index});
            }
        }
    }
    try writer.writeAll("]\n");

    try writer.print("    filler_bits={d}, counter_bits={d}\n", .{ stream.filler_bits, stream.counter_bits });
    try writer.print("    rate={d}, rate_error={d}%\n", .{ stream.rate, stream.rate_error * 100.0 });
    try writer.print("    warm_up_delay={d}\n", .{stream.warm_up_delay});

    if (rate_info) |r| {
        if (r.available != 0) {
            try writer.print("    rate_channel={d}, rate_invert={d}\n", .{ r.channel_index, r.invert });
            try writer.print("    rate_scale={d}, rate_offset={d}\n", .{ r.scale, r.offset });
        } else {
            try writer.writeAll("    rate_channel=<N/A>\n");
        }
    } else {
        try writer.writeAll("    rate_channel=<N/A>\n");
    }

    if (decoder) |d| {
        try writer.print("    used_bits={d}\n", .{d.used_bits});
    }
}

fn writeBitrate(writer: *std.io.Writer, bitrate: f64) !void {
    const Scale = struct { factor: f64, suffix: []const u8 };
    const scales = [_]Scale{
        .{ .factor = 1, .suffix = "bit/s" },
        .{ .factor = 1e3, .suffix = "kbit/s" },
        .{ .factor = 1e6, .suffix = "Mbit/s" },
        .{ .factor = 1e9, .suffix = "Gbit/s" },
    };

    for (scales) |scale| {
        if (bitrate < scale.factor * 1000) {
            try writer.print("{d:.1} {s}", .{ bitrate / scale.factor, scale.suffix });
            return;
        }
    }

    // If the bitrate is extremely large, use the largest scale
    try writer.print("{d:.3} Gbit/s", .{bitrate / 1e9});
}

fn writeChannelSummary(
    writer: *std.io.Writer,
    channel: *const c.AsphodelChannelInfo_t,
    channel_index: usize,
    calibration: ?*const c.AsphodelChannelCalibration_t,
    streams: ?[]const c.AsphodelStreamInfo_t,
    device_decoder: ?*const c.AsphodelDeviceDecoder_t,
) !void {
    try writer.print("  Channel {d}\n", .{channel_index});
    if (channel.name) |name| {
        try writer.print("    name: {s}\n", .{name});
    } else {
        try writer.writeAll("    name: <UNKNOWN>\n");
    }

    var last_stream: ?usize = null;
    var stream_count: usize = 0;
    if (streams) |s| {
        for (s, 0..) |*stream, j| {
            if (stream.channel_count == 0) continue;
            const channels = stream.channel_index_list[0..stream.channel_count];
            const index_u8 = std.math.cast(u8, channel_index) orelse continue;
            if (std.mem.indexOfScalar(u8, channels, index_u8) != null) {
                if (last_stream) |last_stream_id| {
                    // found a second (or later) stream
                    if (stream_count == 1) {
                        try writer.print("    streams: [{d}, {d}", .{ last_stream_id, j });
                    } else {
                        try writer.print(", {d}", .{j});
                    }
                } else {
                    // found our first stream
                    last_stream = j;
                }

                stream_count += 1;
            }
        }
    }

    var decoder: ?*const c.AsphodelChannelDecoder_t = null;

    if (stream_count > 1) {
        // finish the partially written line
        try writer.writeAll("]\n");
    } else if (stream_count == 1) {
        const last_stream_id = last_stream.?;
        try writer.print("    stream: {d}\n", .{last_stream_id});

        const stream = &streams.?[last_stream_id];

        const sampling_rate = stream.rate * @as(f32, @floatFromInt(channel.samples));
        try writer.print("    rate={d}\n", .{sampling_rate});

        if (device_decoder) |d| {
            if (d.streams > last_stream_id) {
                const stream_decoder: *c.AsphodelStreamDecoder_t = d.decoders[last_stream_id];

                for (0..stream.channel_count) |i| {
                    if (stream.channel_index_list[i] == channel_index) {
                        if (stream_decoder.channels > i) {
                            decoder = stream_decoder.decoders[i];
                        }
                        break;
                    }
                }
            }
        }
    } else {
        try writer.writeAll("    stream: <N/A>\n");
    }

    try writer.print("    channel_type={d} ({s})\n", .{ channel.channel_type, c.asphodel_channel_type_name(channel.channel_type) });
    try writer.print("    unit_type={d} ({s})\n", .{ channel.unit_type, c.asphodel_unit_type_name(channel.unit_type) });
    try writer.print("    filler_bits={d}, data_bits={d}\n", .{ channel.filler_bits, channel.data_bits });
    try writer.print("    samples={d}, bits_per_sample={d}\n", .{ channel.samples, channel.bits_per_sample });
    try writer.print("    minimum={d}, maximum={d}, resolution={d}\n", .{ channel.minimum, channel.maximum, channel.resolution });
    try writer.writeAll("    coefficients: [");
    if (channel.coefficients_length > 0) {
        for (channel.coefficients[0..channel.coefficients_length], 0..) |coefficient, j| {
            if (j == 0) {
                try writer.print("{d}", .{coefficient});
            } else {
                try writer.print(", {d}", .{coefficient});
            }
        }
    }
    try writer.writeAll("]\n");
    try writer.print("    Chunk Count: {d}\n", .{channel.chunk_count});

    if (channel.chunk_count != 0) {
        if (channel.chunk_lengths) |chunk_lengths| {
            if (channel.chunks) |chunks| {
                for (chunk_lengths[0..channel.chunk_count], 0..) |chunk_length, j| {
                    const chunk_ptr: [*c]const u8 = chunks[j];
                    if (chunk_length == 0 or chunk_ptr == null) {
                        try writer.print("      Chunk {d}: []\n", .{j});
                    } else {
                        try writer.print("      Chunk {d}: [", .{j});
                        for (chunk_ptr[0..chunk_length], 0..) |v, k| {
                            if (k == 0) {
                                try writer.print("{x:0>2}", .{v});
                            } else {
                                try writer.print(",{x:0>2}", .{v});
                            }
                        }
                        try writer.writeAll("]\n");
                    }
                }
            }
        }
    }

    if (calibration) |cal| {
        // print out channel calibration
        try writer.print("    cal base_setting={d}, cal resolution_setting={d}\n", .{ cal.base_setting_index, cal.resolution_setting_index });
        try writer.print("    cal scale={d}, cal offset={d}\n", .{ cal.scale, cal.offset });
        try writer.print("    cal minimum={d}, cal maximum={d}\n", .{ cal.minimum, cal.maximum });
    }

    switch (channel.channel_type) {
        c.CHANNEL_TYPE_SLOW_STRAIN, c.CHANNEL_TYPE_FAST_STRAIN, c.CHANNEL_TYPE_COMPOSITE_STRAIN => {
            try writeStrainChannelSpecifics(writer, channel);
        },
        c.CHANNEL_TYPE_SLOW_ACCEL, c.CHANNEL_TYPE_PACKED_ACCEL, c.CHANNEL_TYPE_LINEAR_ACCEL => {
            try writeAccelChannelSpecifics(writer, channel);
        },
        else => {
            // nothing to do
        },
    }

    if (decoder) |d| {
        try writer.print("    channel_bit_offset={d}, samples={d}\n", .{ d.channel_bit_offset, d.samples });

        if (d.subchannels > 0) {
            try writer.writeAll("    subchannels:\n");
            for (d.subchannel_names[0..d.subchannels]) |name| {
                // subchannel names are guaranteed to be non-null
                try writer.print("      {s}\n", .{name});
            }
        }
    }
}

fn writeStrainChannelSpecifics(writer: *std.io.Writer, channel: *const c.AsphodelChannelInfo_t) !void {
    var result: c_int = undefined;

    var bridge_count: c_int = undefined;
    result = c.asphodel_get_strain_bridge_count(channel, &bridge_count);
    if (result != c.ASPHODEL_SUCCESS or bridge_count < 0) {
        try writer.writeAll("    Bridges: <ERROR>\n");
        return;
    }

    var i: c_int = 0;
    while (i < bridge_count) : (i += 1) {
        var subchannel_index: usize = undefined;
        result = c.asphodel_get_strain_bridge_subchannel(channel, i, &subchannel_index);
        if (result != c.ASPHODEL_SUCCESS) {
            try writer.print("    Bridge {d}: <ERROR>\n", .{i});
            continue;
        }

        try writer.print("    Bridge {d} (subchannel_index={d})\n", .{ i, subchannel_index });

        var bridge_values: [5]f32 = undefined;
        result = c.asphodel_get_strain_bridge_values(channel, i, &bridge_values);
        if (result != c.ASPHODEL_SUCCESS) {
            try writer.writeAll("      <ERROR>\n");
            continue;
        }

        try writer.print("      positive sense={d}\n", .{bridge_values[0]});
        try writer.print("      negative sense={d}\n", .{bridge_values[1]});
        try writer.print("      bridge element nominal={d}\n", .{bridge_values[2]});
        try writer.print("      bridge element minimum={d}\n", .{bridge_values[3]});
        try writer.print("      bridge element maximum={d}\n", .{bridge_values[4]});
    }
}

fn writeAccelChannelSpecifics(writer: *std.io.Writer, channel: *const c.AsphodelChannelInfo_t) !void {
    var limits: [6]f32 = undefined;
    const result: c_int = c.asphodel_get_accel_self_test_limits(channel, &limits);
    if (result != 0) {
        try writer.writeAll("    Accel self test: <ERROR>\n");
        return;
    }

    const maybe_formatter: ?*c.AsphodelUnitFormatter_t = c.asphodel_create_unit_formatter(channel.unit_type, channel.minimum, channel.maximum, channel.resolution, 1);
    if (maybe_formatter) |formatter| {
        defer formatter.free.?(formatter);

        var min_buffer: [64]u8 = undefined;
        var max_buffer: [64]u8 = undefined;

        _ = formatter.format_ascii.?(formatter, &min_buffer, min_buffer.len, limits[0] * formatter.conversion_scale + formatter.conversion_offset);
        _ = formatter.format_ascii.?(formatter, &max_buffer, max_buffer.len, limits[1] * formatter.conversion_scale + formatter.conversion_offset);
        try writer.print("    X axis self test difference: min={s}, max={s}\n", .{ std.mem.sliceTo(&min_buffer, 0), std.mem.sliceTo(&max_buffer, 0) });

        _ = formatter.format_ascii.?(formatter, &min_buffer, min_buffer.len, limits[2] * formatter.conversion_scale + formatter.conversion_offset);
        _ = formatter.format_ascii.?(formatter, &max_buffer, max_buffer.len, limits[3] * formatter.conversion_scale + formatter.conversion_offset);
        try writer.print("    Y axis self test difference: min={s}, max={s}\n", .{ std.mem.sliceTo(&min_buffer, 0), std.mem.sliceTo(&max_buffer, 0) });

        _ = formatter.format_ascii.?(formatter, &min_buffer, min_buffer.len, limits[4] * formatter.conversion_scale + formatter.conversion_offset);
        _ = formatter.format_ascii.?(formatter, &max_buffer, max_buffer.len, limits[5] * formatter.conversion_scale + formatter.conversion_offset);
        try writer.print("    Z axis self test difference: min={s}, max={s}\n", .{ std.mem.sliceTo(&min_buffer, 0), std.mem.sliceTo(&max_buffer, 0) });
    } else {
        try writer.print("    X axis self test difference: min={d}, max={d}\n", .{ limits[0], limits[1] });
        try writer.print("    Y axis self test difference: min={d}, max={d}\n", .{ limits[2], limits[3] });
        try writer.print("    Z axis self test difference: min={d}, max={d}\n", .{ limits[4], limits[5] });
    }
}

fn writeSupplySummary(writer: *std.io.Writer, supply: *const c.AsphodelSupplyInfo_t, supply_index: usize, result: ?*const c.AsphodelSupplyResult_t) !void {
    try writer.print("  Supply {d}\n", .{supply_index});
    if (supply.name) |name| {
        try writer.print("    name: {s}\n", .{name});
    } else {
        try writer.writeAll("    name: <UNKNOWN>\n");
    }

    try writer.print("    unit_type={d} ({s})\n", .{ supply.unit_type, c.asphodel_unit_type_name(supply.unit_type) });
    try writer.print("    is_battery={d}, nominal={d}\n", .{ supply.is_battery, supply.nominal });
    try writer.print("    scale={d}, offset={d}\n", .{ supply.scale, supply.offset });

    if (result) |r| {
        if (r.error_code == c.ASPHODEL_SUCCESS) {
            const passfail = if (r.result == 0) "pass" else "FAIL";
            try writer.print("    value={d}, result=0x{x:0>2} ({s})\n", .{ r.measurement, r.result, passfail });

            const scaled_value: f64 = @as(f64, @floatFromInt(r.measurement)) * supply.scale + supply.offset;
            const scaled_nominal: f64 = @as(f64, @floatFromInt(supply.nominal)) * supply.scale + supply.offset;
            const percent = if (scaled_nominal != 0.0) (scaled_value) / scaled_nominal * 100.0 else 0.0;

            try writer.print("    scaled_value={d} ({d:.0}%)\n", .{ scaled_value, percent });
        } else {
            try writer.print("    Error code {d} ({s})\n", .{ r.error_code, c.asphodel_error_name(r.error_code) });
        }
    } else {
        try writer.writeAll("    value=<UNKNOWN>\n");
    }
}

fn writeCtrlVarSummary(writer: *std.io.Writer, ctrl_var: *const c.AsphodelCtrlVarInfo_t, ctrl_var_index: usize) !void {
    try writer.print("  Control Variable {d}\n", .{ctrl_var_index});
    if (ctrl_var.name) |name| {
        try writer.print("    name: {s}\n", .{name});
    } else {
        try writer.writeAll("    name: <UNKNOWN>\n");
    }

    try writer.print("    unit_type={d} ({s})\n", .{ ctrl_var.unit_type, c.asphodel_unit_type_name(ctrl_var.unit_type) });
    try writer.print("    minimum={d}, maximum={d}\n", .{ ctrl_var.minimum, ctrl_var.maximum });
    try writer.print("    scale={d}, offset={d}\n", .{ ctrl_var.scale, ctrl_var.offset });
}

fn writeSettingSummary(writer: *std.io.Writer, setting: *const c.AsphodelSettingInfo_t, setting_index: usize, nvm: ?[]const u8, device_info: *const c.AsphodelDeviceInfo_t) !void {
    try writer.print("  Setting {d}\n", .{setting_index});
    if (setting.name) |name| {
        try writer.print("    name: {s}\n", .{name});
    } else {
        try writer.writeAll("    name: <UNKNOWN>\n");
    }

    try writer.print("    setting_type={d} ({s})\n", .{ setting.setting_type, c.asphodel_setting_type_name(setting.setting_type) });

    const default_bytes: []const u8 = if (setting.default_bytes) |bytes| bytes[0..setting.default_bytes_length] else &[0]u8{};

    switch (setting.setting_type) {
        c.SETTING_TYPE_BYTE => {
            if (default_bytes.len == 1) {
                try writer.print("    default={d}\n", .{default_bytes[0]});
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = (@as(usize, setting.u.byte_setting.nvm_word) * 4) + setting.u.byte_setting.nvm_word_byte;
                if (nvm_bytes.len > byte_offset) {
                    try writer.print("    value={d}\n", .{nvm_bytes[byte_offset]});
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_BOOLEAN => {
            if (default_bytes.len == 1) {
                const truefalse = if (default_bytes[0] != 0) "True" else "False";
                try writer.print("    default={s}\n", .{truefalse});
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = (@as(usize, setting.u.byte_setting.nvm_word) * 4) + setting.u.byte_setting.nvm_word_byte;
                if (nvm_bytes.len > byte_offset) {
                    const truefalse = if (nvm_bytes[byte_offset] != 0) "True" else "False";
                    try writer.print("    value={s}\n", .{truefalse});
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_UNIT_TYPE => {
            if (default_bytes.len == 1) {
                try writer.print("    default={d} ({s})\n", .{ default_bytes[0], c.asphodel_unit_type_name(default_bytes[0]) });
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = (@as(usize, setting.u.byte_setting.nvm_word) * 4) + setting.u.byte_setting.nvm_word_byte;
                if (nvm_bytes.len > byte_offset) {
                    try writer.print("    value={d} ({s})\n", .{ nvm_bytes[byte_offset], c.asphodel_unit_type_name(nvm_bytes[byte_offset]) });
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_CHANNEL_TYPE => {
            if (default_bytes.len == 1) {
                try writer.print("    default={d} ({s})\n", .{ default_bytes[0], c.asphodel_channel_type_name(default_bytes[0]) });
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = (@as(usize, setting.u.byte_setting.nvm_word) * 4) + setting.u.byte_setting.nvm_word_byte;
                if (nvm_bytes.len > byte_offset) {
                    try writer.print("    value={d} ({s})\n", .{ nvm_bytes[byte_offset], c.asphodel_channel_type_name(nvm_bytes[byte_offset]) });
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_BYTE_ARRAY => {
            try writer.writeAll("    default=[");
            for (default_bytes, 0..) |byte, i| {
                if (i == 0) {
                    try writer.print("{x:0>2}", .{byte});
                } else {
                    try writer.print(",{x:0>2}", .{byte});
                }
            }
            try writer.writeAll("]\n");
            if (nvm) |nvm_bytes| {
                const length_byte_offset = (@as(usize, setting.u.byte_array_setting.length_nvm_word) * 4) + setting.u.byte_array_setting.length_nvm_word_byte;
                if (nvm_bytes.len > length_byte_offset) {
                    var length = nvm_bytes[length_byte_offset];
                    if (length > setting.u.byte_array_setting.maximum_length) {
                        length = setting.u.byte_array_setting.maximum_length;
                    }

                    const byte_offset = @as(usize, setting.u.byte_array_setting.nvm_word) * 4;
                    if (nvm_bytes.len >= byte_offset + length) {
                        const raw_bytes = nvm_bytes[byte_offset .. byte_offset + length];
                        try writer.writeAll("    value=[");
                        for (raw_bytes, 0..) |byte, i| {
                            if (i == 0) {
                                try writer.print("{x:0>2}", .{byte});
                            } else {
                                try writer.print(",{x:0>2}", .{byte});
                            }
                        }
                        try writer.writeAll("]\n");
                    } else {
                        try writer.writeAll("    value=<ERROR>\n");
                    }
                }
            }
        },
        c.SETTING_TYPE_STRING => {
            if (std.mem.indexOfScalar(u8, default_bytes, 0) == null) {
                if (std.unicode.utf8ValidateSlice(default_bytes)) {
                    try writer.print("    default=\"{s}\"\n", .{default_bytes});
                } else {
                    try writer.writeAll("    default=<ERROR>\n");
                }
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            try writer.print("    maximum_length={d}\n", .{setting.u.string_setting.maximum_length});
            if (nvm) |nvm_bytes| {
                const byte_offset = @as(usize, setting.u.string_setting.nvm_word) * 4;
                if (nvm_bytes.len >= byte_offset + setting.u.string_setting.maximum_length) {
                    const raw_string = nvm_bytes[byte_offset .. byte_offset + setting.u.string_setting.maximum_length];
                    // split on null or 0xFF
                    var it = std.mem.splitAny(u8, raw_string, &[_]u8{ 0x00, 0xFF });
                    const string = it.first();
                    if (std.unicode.utf8ValidateSlice(string)) {
                        try writer.print("    value=\"{s}\"\n", .{string});
                    } else {
                        try writer.writeAll("    value=<ERROR>\n");
                    }
                }
            }
        },
        c.SETTING_TYPE_INT32 => {
            if (default_bytes.len == 4) {
                const default = std.mem.readInt(i32, @as(*const [4]u8, @ptrCast(default_bytes.ptr)), .big);
                try writer.print("    default={d}\n", .{default});
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = @as(usize, setting.u.int32_setting.nvm_word) * 4;
                if (nvm_bytes.len >= byte_offset + 4) {
                    const value = std.mem.readInt(i32, @as(*const [4]u8, @ptrCast(nvm_bytes.ptr + byte_offset)), .big);
                    try writer.print("    value={d}\n", .{value});
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_INT32_SCALED => {
            if (default_bytes.len == 4) {
                const default = std.mem.readInt(i32, @as(*const [4]u8, @ptrCast(default_bytes.ptr)), .big);
                const scaled = @as(f64, @floatFromInt(default)) * setting.u.int32_scaled_setting.scale + setting.u.int32_scaled_setting.offset;
                try writer.print("    default={d}\n", .{scaled});
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            try writer.print("    unit_type={d} ({s})\n", .{ setting.u.int32_scaled_setting.unit_type, c.asphodel_unit_type_name(setting.u.int32_scaled_setting.unit_type) });
            if (nvm) |nvm_bytes| {
                const byte_offset = @as(usize, setting.u.int32_scaled_setting.nvm_word) * 4;
                if (nvm_bytes.len >= byte_offset + 4) {
                    const value = std.mem.readInt(i32, @as(*const [4]u8, @ptrCast(nvm_bytes.ptr + byte_offset)), .big);
                    const scaled = @as(f64, @floatFromInt(value)) * setting.u.int32_scaled_setting.scale + setting.u.int32_scaled_setting.offset;
                    try writer.print("    value={d}\n", .{scaled});
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_FLOAT => {
            if (default_bytes.len == 4) {
                const default_int = std.mem.readInt(u32, @as(*const [4]u8, @ptrCast(default_bytes.ptr)), .big);
                const default: f32 = @bitCast(default_int);
                const scaled = default * setting.u.float_setting.scale + setting.u.float_setting.offset;
                try writer.print("    default={d}\n", .{scaled});
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            try writer.print("    unit_type={d} ({s})\n", .{ setting.u.float_setting.unit_type, c.asphodel_unit_type_name(setting.u.float_setting.unit_type) });
            if (nvm) |nvm_bytes| {
                const byte_offset = @as(usize, setting.u.float_setting.nvm_word) * 4;
                if (nvm_bytes.len >= byte_offset + 4) {
                    const value_int = std.mem.readInt(u32, @as(*const [4]u8, @ptrCast(nvm_bytes.ptr + byte_offset)), .big);
                    const value: f32 = @bitCast(value_int);
                    const scaled = value * setting.u.float_setting.scale + setting.u.float_setting.offset;
                    try writer.print("    value={d}\n", .{scaled});
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        c.SETTING_TYPE_FLOAT_ARRAY => {
            if (default_bytes.len % 4 == 0) {
                try writer.writeAll("    default=[");
                var i: usize = 0;
                while (i < default_bytes.len) : (i += 4) {
                    const default_int = std.mem.readInt(u32, @as(*const [4]u8, @ptrCast(default_bytes.ptr + i)), .big);
                    const default: f32 = @bitCast(default_int);
                    const scaled = default * setting.u.float_array_setting.scale + setting.u.float_array_setting.offset;
                    if (i == 0) {
                        try writer.print("{d}", .{scaled});
                    } else {
                        try writer.print(", {d}", .{scaled});
                    }
                }
                try writer.writeAll("]\n");

                try writer.print("    unit_type={d} ({s})\n", .{ setting.u.float_array_setting.unit_type, c.asphodel_unit_type_name(setting.u.float_array_setting.unit_type) });

                if (nvm) |nvm_bytes| {
                    const length_byte_offset = (@as(usize, setting.u.float_array_setting.length_nvm_word) * 4) + setting.u.float_array_setting.length_nvm_word_byte;
                    if (nvm_bytes.len > length_byte_offset) {
                        var length = nvm_bytes[length_byte_offset];
                        if (length > setting.u.float_array_setting.maximum_length) {
                            length = setting.u.float_array_setting.maximum_length;
                        }

                        const byte_offset = @as(usize, setting.u.float_array_setting.nvm_word) * 4;
                        if (nvm_bytes.len >= byte_offset + length * 4) {
                            const raw_bytes = nvm_bytes[byte_offset .. byte_offset + length * 4];

                            try writer.writeAll("    value=[");
                            i = 0;
                            while (i < raw_bytes.len) : (i += 4) {
                                const value_int = std.mem.readInt(u32, @as(*const [4]u8, @ptrCast(raw_bytes.ptr + i)), .big);
                                const value: f32 = @bitCast(value_int);
                                const scaled = value * setting.u.float_array_setting.scale + setting.u.float_array_setting.offset;
                                if (i == 0) {
                                    try writer.print("{d}", .{scaled});
                                } else {
                                    try writer.print(", {d}", .{scaled});
                                }
                            }
                            try writer.writeAll("]\n");
                        } else {
                            try writer.writeAll("    value=<ERROR>\n");
                        }
                    }
                }
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
        },
        c.SETTING_TYPE_CUSTOM_ENUM => {
            if (default_bytes.len == 1) {
                try writer.writeAll("    default=");
                try writeCustomEnum(writer, device_info, setting.u.custom_enum_setting.custom_enum_index, default_bytes[0]);
                try writer.writeAll("\n");
            } else {
                try writer.writeAll("    default=<ERROR>\n");
            }
            if (nvm) |nvm_bytes| {
                const byte_offset = (@as(usize, setting.u.custom_enum_setting.nvm_word) * 4) + setting.u.custom_enum_setting.nvm_word_byte;
                if (nvm_bytes.len > byte_offset) {
                    try writer.writeAll("    value=");
                    try writeCustomEnum(writer, device_info, setting.u.custom_enum_setting.custom_enum_index, nvm_bytes[byte_offset]);
                    try writer.writeAll("\n");
                } else {
                    try writer.writeAll("    value=<ERROR>\n");
                }
            }
        },
        else => {
            try writer.writeAll("    unknown setting type!\n");
        },
    }
}

fn writeCustomEnum(writer: *std.io.Writer, device_info: *const c.AsphodelDeviceInfo_t, enum_index: u8, enum_value: u8) !void {
    if (device_info.custom_enum_lengths) |custom_enum_lengths| {
        // if custom_enum_lengths exists then device_info.custom_enum_count is known
        if (device_info.custom_enum_count > enum_index) {
            const values_length = custom_enum_lengths[enum_index];
            if (enum_value < values_length) {
                if (device_info.custom_enum_values) |custom_enum_values| {
                    if (custom_enum_values[enum_index]) |values| {
                        if (values[enum_value]) |value| {
                            try writer.writeAll(std.mem.span(value));
                        } else {
                            // this specific value is missing, value is unknown
                            try writer.print("<UNKNOWN> ({d})", .{enum_value});
                        }
                    } else {
                        // All of this enum's values are missing, value is unknown
                        try writer.print("<UNKNOWN> ({d})", .{enum_value});
                    }
                } else {
                    // all custom enums are missing, value is unknown
                    try writer.print("<UNKNOWN> ({d})", .{enum_value});
                }
            } else {
                // invalid enum_value
                try writer.print("<ERROR> ({d})", .{enum_value});
            }
        } else {
            // invalid enum_index
            try writer.print("<ERROR> ({d})", .{enum_value});
        }
    } else {
        // all custom enums are missing, value is unknown
        try writer.print("<UNKNOWN> ({d})", .{enum_value});
    }
}

fn writeNvm(writer: *std.io.Writer, nvm: []const u8) !void {
    const stride: usize = 16;

    var line_first_index: usize = 0;
    while (line_first_index < nvm.len) : (line_first_index += stride) {
        const line_elements: usize = @min(stride, nvm.len - line_first_index);

        for (0..line_elements) |i| {
            const byte = nvm[line_first_index + i];
            if (i == 0) {
                try writer.print("{x:0>2}", .{byte});
            } else {
                try writer.print(" {x:0>2}", .{byte});
            }
        }

        // fill in the gap (if any)
        if (line_elements < stride) {
            try writer.splatBytesAll("   ", stride - line_elements);
        }

        // space before ASCII column
        try writer.writeAll(" ");

        // ASCII column
        for (0..line_elements) |i| {
            const byte = nvm[line_first_index + i];
            const output_byte = switch (byte) {
                '\t', '\n', '\r', 0x0B, 0x0C => ' ',
                0x20...0x7E => byte,
                else => '.',
            };
            try writer.writeByte(output_byte);
        }

        try writer.writeAll("\n");
    }
}
