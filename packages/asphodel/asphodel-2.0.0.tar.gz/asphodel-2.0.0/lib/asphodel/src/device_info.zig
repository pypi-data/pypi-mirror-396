const std = @import("std");
const c = @import("root.zig").c;
const Cache = @import("root.zig").device_info_cache.Cache;
const Allocator = std.mem.Allocator;

// NOTE: most of the functions in this file depend on the fact that we're using arena allocators.
// The cleanup code is mostly non-existent within the step functions, but the arena ensures that
// the memory will be freed regardless.

pub export fn asphodel_get_device_info(device: *c.AsphodelDevice_t, cache: ?*Cache, flags: u32, device_info_out: **c.AsphodelDeviceInfo_t, callback: c.AsphodelDeviceInfoProgressCallback_t, closure: ?*anyopaque) c_int {
    var returned_device_info = std.heap.c_allocator.create(ReturnedDeviceInfo) catch return c.ASPHODEL_NO_MEM;
    returned_device_info.arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator); // use the raw, as it's faster and safe with arenas
    var device_info = &returned_device_info.device_info;
    device_info.* = c.AsphodelDeviceInfo_t{}; // initialize to safe defaults
    device_info.free_device_info = free_device_info;

    // NOTE: can't use errdefer here, because we need to return asphodel error codes

    const allocator = returned_device_info.arena.allocator();

    const cache_info_result = getCacheInfo(allocator, device, device_info);
    if (cache_info_result != c.ASPHODEL_SUCCESS) {
        returned_device_info.arena.deinit();
        std.heap.c_allocator.destroy(returned_device_info);
        return cache_info_result;
    }

    // cache lookup
    if (cache) |ca| {
        ca.fill(allocator, device_info) catch |err| {
            returned_device_info.arena.deinit();
            std.heap.c_allocator.destroy(returned_device_info);
            switch (err) {
                error.OutOfMemory => return c.ASPHODEL_NO_MEM,
                else => return c.ASPHODEL_BAD_PARAMETER,
            }
        };
    }

    var second_pass_needed = [_]bool{false} ** steps.len;
    var finished: u32 = CACHE_INFO_COST;
    var total: u32 = CACHE_INFO_COST;

    for (steps, 0..) |step, i| {
        if ((step.flags & flags) != 0) {
            continue;
        } else if (step.first_pass) |first_pass| {
            const result = first_pass(allocator, device, device_info, flags);

            if (result.second_pass_needed) {
                std.debug.assert(step.second_pass != null);
            } else {
                std.debug.assert(result.total == result.finished);
            }

            if (result.result_code == c.ASPHODEL_SUCCESS) {
                finished += result.finished;
                total += result.total;
                second_pass_needed[i] = result.second_pass_needed;
            } else {
                if (cache) |ca| {
                    // write what we've got so far to save partial progress
                    ca.save(device_info) catch {}; // ignore any errors
                }

                // free everything
                returned_device_info.arena.deinit();
                std.heap.c_allocator.destroy(returned_device_info);

                // bail out
                return result.result_code;
            }
        }
    }

    var incrementer = Incrementer{
        .finished = finished,
        .total = total,
        .callback = callback,
        .closure = closure,
    };

    for (steps, 0..) |step, i| {
        if (second_pass_needed[i]) {
            if (step.second_pass) |second_pass| {
                const result_code = second_pass(allocator, device, device_info, flags, &incrementer);

                if (result_code != c.ASPHODEL_SUCCESS) {
                    if (cache) |ca| {
                        // write what we've got so far to save partial progress
                        ca.save(device_info) catch {}; // ignore any errors
                    }

                    // free everything
                    returned_device_info.arena.deinit();
                    std.heap.c_allocator.destroy(returned_device_info);

                    // bail out
                    return result_code;
                }
            }
        }
    }

    // write the device info to the cache
    if (cache) |ca| {
        ca.save(device_info) catch {}; // ignore any errors
    }

    // NOTE: this should happen after any caching, but before returning the device info to the user
    for (steps) |step| {
        if ((step.flags & flags) != 0) {
            if (step.clear_when_disabled) |clear| {
                clear(device_info);
            }
        }
    }

    incrementer.finish();

    device_info_out.* = device_info;

    return c.ASPHODEL_SUCCESS;
}

pub const ReturnedDeviceInfo = struct {
    arena: std.heap.ArenaAllocator,
    device_info: c.AsphodelDeviceInfo_t,
};

pub fn free_device_info(device_info: ?*c.AsphodelDeviceInfo_t) callconv(.c) void {
    if (device_info) |d| {
        const returned_device_info: *ReturnedDeviceInfo = @fieldParentPtr("device_info", d);
        returned_device_info.arena.deinit();
        std.heap.c_allocator.destroy(returned_device_info);
    }
}

const CACHE_INFO_COST: u32 = 6; // getCacheInfo() always performs this many transfers to the device.

fn getCacheInfo(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t) c_int {
    var buffer: [256]u8 = undefined;
    var ret: c_int = undefined;

    ret = c.asphodel_get_build_date_blocking(device, &buffer, buffer.len);
    if (ret != c.ASPHODEL_SUCCESS) return ret;
    device_info.build_date = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;

    ret = c.asphodel_get_build_info_blocking(device, &buffer, buffer.len);
    if (ret != c.ASPHODEL_SUCCESS) return ret;
    device_info.build_info = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;

    ret = c.asphodel_get_nvm_hash_blocking(device, &buffer, buffer.len);
    if (ret == c.ASPHODEL_SUCCESS) {
        device_info.nvm_hash = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
    } else if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
        // device is too old to support this command
        device_info.nvm_hash = null;
    } else {
        return ret;
    }

    ret = c.asphodel_get_setting_hash_blocking(device, &buffer, buffer.len);
    if (ret == c.ASPHODEL_SUCCESS) {
        device_info.setting_hash = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
    } else if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
        // device is too old to support this command
        device_info.setting_hash = null;
    } else {
        return ret;
    }

    ret = c.asphodel_get_board_info_blocking(device, &device_info.board_info_rev, &buffer, buffer.len);
    if (ret != c.ASPHODEL_SUCCESS) return ret;
    device_info.board_info_name = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;

    var modified: u8 = undefined;
    ret = c.asphodel_get_nvm_modified_blocking(device, &modified);
    if (ret == c.ASPHODEL_SUCCESS) {
        const ptr = allocator.create(u8) catch return c.ASPHODEL_NO_MEM;
        ptr.* = modified;
        device_info.nvm_modified = ptr;
    } else if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
        // device is too old to support this command
        device_info.nvm_modified = null; // redundant with the initial zeroing, but intent is clear
    } else {
        return ret;
    }

    return c.ASPHODEL_SUCCESS;
}

const Incrementer = struct {
    finished: u32,
    total: u32,
    callback: c.AsphodelDeviceInfoProgressCallback_t,
    closure: ?*anyopaque,

    const Self = @This();

    pub fn increment(self: *Self, just_completed: u32, message: [*:0]const u8) void {
        if (self.callback) |callback| {
            self.finished += just_completed;

            std.debug.assert(self.total >= self.finished);

            callback(self.finished, self.total, message, self.closure);
        }
    }

    pub fn finish(self: *Self) void {
        if (self.callback) |callback| {
            std.debug.assert(self.total == self.finished);
            callback(self.finished, self.total, "Final", self.closure);
        }
    }
};

const StepResult = struct {
    result_code: c_int = c.ASPHODEL_SUCCESS, // ASPHODEL_SUCCESS if successful
    second_pass_needed: bool = false,
    finished: u32 = 0,
    total: u32 = 0,
};

const Step = struct {
    flags: u32, // disable this step if any flags match

    // the first pass is for calculating the total numbers of steps, optionally querying the device.
    // If the device is queried as part of the first pass, the finished count should be the number of queries.
    // The total count should also reflect the number of queries performed in the first pass.
    //
    // If the desired information is already present, the second pass can be skipped by returning needed = false.
    //
    // If there's an error with the device, the non-zero result code should be put into the StepResult and the loop
    // will be aborted.
    //
    // During error conditions, the device_info should be filled with as much information as possible for caching.
    // This allows incremental progress to be made. Consequently, this function should tolerate incomplete information.
    first_pass: ?*const fn (allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult,

    // The second pass should process the remaining device information, calling into the incrementer as needed.
    // This should always increment exactly (total - finished) steps returned in the first pass.
    // If this is null, then the first pass must return a result where finished == total.
    //
    // If there's an error with the device, the non-zero result code be returned and the loop will be aborted.
    //
    // During error conditions, the device_info should be filled with as much information as possible for caching.
    // This allows incremental progress to be made. Consequently, this function should tolerate incomplete information.
    second_pass: ?*const fn (allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int = null,

    // If this is non-null, it will be called when the flags disable this step to clear out any device information that
    // might be coming in from the cache.
    clear_when_disabled: ?*const fn (device_info: *c.AsphodelDeviceInfo_t) void = null,
};

const steps = &[_]Step{
    .{
        .flags = 0,
        .first_pass = firstPassNoCost,
    },
    .{
        .flags = 0, // the functions will parse the flags internally
        .first_pass = firstPassNvm,
        .second_pass = secondPassNvm,
    },
    .{
        .flags = c.ASPHODEL_NO_PROTOCOL_VERSION,
        .first_pass = firstPassProtocolVersion,
        .second_pass = secondPassProtocolVersion,
        .clear_when_disabled = clearProtocolVersion,
    },
    .{
        .flags = c.ASPHODEL_NO_CHIP_INFO,
        .first_pass = firstPassChipInfo,
        .second_pass = secondPassChipInfo,
        .clear_when_disabled = clearChipInfo,
    },
    .{
        .flags = c.ASPHODEL_NO_REPO_DETAIL_INFO,
        .first_pass = firstPassRepoDetails,
        .second_pass = secondPassRepoDetails,
        .clear_when_disabled = clearRepoDetails,
    },
    .{
        .flags = c.ASPHODEL_NO_STREAM_INFO,
        .first_pass = firstPassStreams,
        .second_pass = secondPassStreams,
        .clear_when_disabled = clearStreams,
    },
    .{
        .flags = c.ASPHODEL_NO_STREAM_RATE_INFO | c.ASPHODEL_NO_STREAM_INFO,
        .first_pass = firstPassStreamRates,
        .second_pass = secondPassStreamRates,
        .clear_when_disabled = clearStreamRates,
    },
    .{
        .flags = c.ASPHODEL_NO_CHANNEL_INFO,
        .first_pass = firstPassChannels,
        .second_pass = secondPassChannels,
        .clear_when_disabled = clearChannels,
    },
    .{
        .flags = c.ASPHODEL_NO_CHANNEL_CAL_INFO | c.ASPHODEL_NO_CHANNEL_INFO,
        .first_pass = firstPassChannelCalibrations,
        .second_pass = secondPassChannelCalibrations,
        .clear_when_disabled = clearChannelCalibrations,
    },
    .{
        .flags = c.ASPHODEL_NO_SUPPLY_INFO,
        .first_pass = firstPassSupplies,
        .second_pass = secondPassSupplies,
        .clear_when_disabled = clearSupplies,
    },
    .{
        .flags = c.ASPHODEL_NO_CTRL_VAR_INFO,
        .first_pass = firstPassCtrlVars,
        .second_pass = secondPassCtrlVars,
        .clear_when_disabled = clearCtrlVars,
    },
    .{
        .flags = c.ASPHODEL_NO_SETTING_INFO,
        .first_pass = firstPassSettings,
        .second_pass = secondPassSettings,
        .clear_when_disabled = clearSettings,
    },
    .{
        .flags = c.ASPHODEL_NO_SETTING_INFO,
        .first_pass = firstPassCustomEnums,
        .second_pass = secondPassCustomEnums,
        .clear_when_disabled = clearCustomEnums,
    },
    .{
        .flags = c.ASPHODEL_NO_SETTING_CATEGORY_INFO | c.ASPHODEL_NO_SETTING_INFO,
        .first_pass = firstPassSettingCategories,
        .second_pass = secondPassSettingCategories,
        .clear_when_disabled = clearSettingCategories,
    },
    .{
        .flags = c.ASPHODEL_NO_RF_POWER_INFO,
        .first_pass = firstPassRfPowerCtrlVars,
        .second_pass = secondPassRfPowerCtrlVars,
        .clear_when_disabled = clearRfPowerCtrlVars,
    },
    .{
        .flags = c.ASPHODEL_NO_RADIO_INFO,
        .first_pass = firstPassRadioCtrlVars,
        .second_pass = secondPassRadioCtrlVars,
        .clear_when_disabled = clearRadioCtrlVars,
    },
    .{
        .flags = c.ASPHODEL_NO_RADIO_INFO,
        .first_pass = firstPassRadioDefaultSerial,
        .second_pass = secondPassRadioDefaultSerial,
        .clear_when_disabled = clearRadioDefaultSerial,
    },
    .{
        .flags = c.ASPHODEL_NO_RADIO_INFO,
        .first_pass = firstPassRadioScanPower,
        .second_pass = secondPassRadioScanPower,
        .clear_when_disabled = clearRadioScanPower,
    },
    .{
        .flags = c.ASPHODEL_NO_USER_TAG_INFO,
        .first_pass = null,
        .clear_when_disabled = clearUserTags,
    },

    // the ones below here aren't cached (or partially), so we should do them last

    .{ // NOTE: this must come before the rgb led count step
        .flags = c.ASPHODEL_NO_RGB_OR_LED_STATE | c.ASPHODEL_NO_RGB_OR_LED_INFO,
        .first_pass = firstPassRgbLedState,
        .second_pass = secondPassRgbLedState,
        .clear_when_disabled = clearRgbLedState,
    },
    .{
        .flags = c.ASPHODEL_NO_RGB_OR_LED_INFO,
        .first_pass = firstPassRgbLedCount,
        .second_pass = secondPassRgbLedCount,
        .clear_when_disabled = clearRgbLedCount,
    },
    .{
        .flags = c.ASPHODEL_NO_BOOTLOADER_INFO,
        .first_pass = firstPassBootloader,
        .second_pass = secondPassBootloader,
        .clear_when_disabled = clearBootloader,
    },
    .{
        .flags = c.ASPHODEL_NO_SUPPLY_RESULT | c.ASPHODEL_NO_SUPPLY_INFO,
        .first_pass = firstPassSupplyResults,
        .second_pass = secondPassSupplyResults,
        .clear_when_disabled = clearSupplyResults,
    },
    .{
        .flags = c.ASPHODEL_NO_CTRL_VAR_STATE | c.ASPHODEL_NO_CTRL_VAR_INFO,
        .first_pass = firstPassCtrlVarStates,
        .second_pass = secondPassCtrlVarStates,
        .clear_when_disabled = clearCtrlVarStates,
    },
    .{
        .flags = c.ASPHODEL_NO_DEVICE_MODE, // NOTE: will check for c.ASPHODEL_NO_DEVICE_MODE_STATE internally
        .first_pass = firstPassDeviceMode,
        .second_pass = secondPassDeviceMode,
        .clear_when_disabled = clearDeviceMode,
    },
    .{
        .flags = c.ASPHODEL_NO_RF_POWER_STATE | c.ASPHODEL_NO_RF_POWER_INFO,
        .first_pass = firstPassRfPowerState,
        .second_pass = secondPassRfPowerState,
        .clear_when_disabled = clearRfPowerState,
    },
};

fn firstPassNoCost(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = flags;

    var buffer: [100]u8 = undefined;

    // this information can be read from a device without any transfers
    var ret = device.get_serial_number.?(device, &buffer, buffer.len);
    if (ret != 0) return .{ .result_code = ret };
    device_info.serial_number = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return .{ .result_code = c.ASPHODEL_NO_MEM };

    device_info.location_string = allocator.dupeZ(u8, std.mem.span(device.location_string)) catch return .{ .result_code = c.ASPHODEL_NO_MEM };
    device_info.max_incoming_param_length = device.get_max_incoming_param_length.?(device);
    device_info.max_outgoing_param_length = device.get_max_outgoing_param_length.?(device);
    device_info.stream_packet_length = device.get_stream_packet_length.?(device);
    device_info.supports_bootloader = if (c.asphodel_supports_bootloader_commands(device) != 0) 1 else 0;
    device_info.supports_radio = if (c.asphodel_supports_radio_commands(device) != 0) 1 else 0;
    device_info.supports_remote = if (c.asphodel_supports_remote_commands(device) != 0) 1 else 0;
    device_info.supports_rf_power = if (c.asphodel_supports_rf_power_commands(device) != 0) 1 else 0;

    if (c.asphodel_supports_radio_commands(device) != 0) {
        ret = device.get_remote_lengths.?(device, &device_info.remote_max_incoming_param_length, &device_info.remote_max_outgoing_param_length, &device_info.remote_stream_packet_length);
        if (ret != 0) return .{ .result_code = ret };
    } else {
        device_info.remote_max_incoming_param_length = 0;
        device_info.remote_max_outgoing_param_length = 0;
        device_info.remote_stream_packet_length = 0;
    }

    return .{};
}

fn firstPassProtocolVersion(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.protocol_version != null) {
        return .{};
    } else {
        return .{
            .total = 1,
            .second_pass_needed = true,
        };
    }
}

fn secondPassProtocolVersion(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    var buffer: [32]u8 = undefined;
    const ret = c.asphodel_get_protocol_version_string_blocking(device, &buffer, buffer.len);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    device_info.protocol_version = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;

    incrementer.increment(1, "Protocol Version");
    return c.ASPHODEL_SUCCESS;
}

fn clearProtocolVersion(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.protocol_version = null;
}

fn firstPassChipInfo(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    var total: u32 = 0;

    if (device_info.chip_family == null) total += 1;
    if (device_info.chip_model == null) total += 1;
    if (device_info.chip_id == null) total += 1;

    return .{
        .total = total,
        .second_pass_needed = total != 0,
    };
}

fn secondPassChipInfo(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    var buffer: [256]u8 = undefined;
    var ret: c_int = undefined;

    if (device_info.chip_family == null) {
        ret = c.asphodel_get_chip_family_blocking(device, &buffer, buffer.len);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        device_info.chip_family = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        incrementer.increment(1, "Chip Family");
    }

    if (device_info.chip_model == null) {
        ret = c.asphodel_get_chip_model_blocking(device, &buffer, buffer.len);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        device_info.chip_model = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        incrementer.increment(1, "Chip Model");
    }

    if (device_info.chip_id == null) {
        ret = c.asphodel_get_chip_id_blocking(device, &buffer, buffer.len);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        device_info.chip_id = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        incrementer.increment(1, "Chip ID");
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearChipInfo(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.chip_family = null;
    device_info.chip_model = null;
    device_info.chip_id = null;
}

fn firstPassBootloader(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = device_info;
    _ = flags;

    // bootloader info is not cached
    return .{ .second_pass_needed = true, .total = 1 };
}

fn secondPassBootloader(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    var buffer: [256]u8 = undefined;

    const ret = c.asphodel_get_bootloader_info_blocking(device, &buffer, buffer.len);
    if (ret != c.ASPHODEL_SUCCESS) return ret;
    device_info.bootloader_info = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
    incrementer.increment(1, "Bootloader Info");

    return c.ASPHODEL_SUCCESS;
}

fn clearBootloader(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.bootloader_info = null;
}

fn firstPassRgbLedState(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var ret: c_int = undefined;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.rgb_count_known == 0) {
        var rgb_count: c_int = undefined;
        ret = c.asphodel_get_rgb_count_blocking(device, &rgb_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.rgb_count_known = 1;
        device_info.rgb_count = @intCast(rgb_count);

        finished += 1;
        total += 1 + @as(u32, @intCast(rgb_count));
    }

    if (device_info.led_count_known == 0) {
        var led_count: c_int = undefined;
        ret = c.asphodel_get_led_count_blocking(device, &led_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.led_count_known = 1;
        device_info.led_count = @intCast(led_count);

        finished += 1;
        total += 1 + @as(u32, @intCast(led_count));
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassRgbLedState(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    // the states are never cached, so we need to fetch every one

    // first pass ran already
    std.debug.assert(device_info.rgb_count_known != 0);
    std.debug.assert(device_info.led_count_known != 0);

    var ret: c_int = undefined;

    if (device_info.rgb_count != 0) {
        const a = allocator.alloc([3]u8, device_info.rgb_count) catch return c.ASPHODEL_NO_MEM;

        for (0..device_info.rgb_count) |i| {
            ret = c.asphodel_get_rgb_values_blocking(device, @intCast(i), &a[i]);
            if (ret != c.ASPHODEL_SUCCESS) return ret;
        }

        device_info.rgb_settings = a.ptr;

        incrementer.increment(@intCast(device_info.rgb_count), "RGB States");
    }

    if (device_info.led_count != 0) {
        const a = allocator.alloc(u8, device_info.led_count) catch return c.ASPHODEL_NO_MEM;

        for (0..device_info.led_count) |i| {
            ret = c.asphodel_get_led_value_blocking(device, @intCast(i), &a[i]);
            if (ret != c.ASPHODEL_SUCCESS) return ret;
        }

        device_info.led_settings = a.ptr;

        incrementer.increment(@intCast(device_info.led_count), "LED States");
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearRgbLedState(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.rgb_settings = null;
    device_info.led_settings = null;
}

fn firstPassRgbLedCount(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    // firstPassRgbLedState should have already run (and filled these in) if it was going to

    var total: u32 = 0;

    if (device_info.rgb_count_known == 0) {
        total += 1;
    }

    if (device_info.led_count_known == 0) {
        total += 1;
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassRgbLedCount(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = allocator;
    _ = flags;

    var ret: c_int = undefined;

    if (device_info.rgb_count_known == 0) {
        var rgb_count: c_int = undefined;
        ret = c.asphodel_get_rgb_count_blocking(device, &rgb_count);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        device_info.rgb_count_known = 1;
        device_info.rgb_count = @intCast(rgb_count);

        incrementer.increment(1, "RGB Count");
    }

    if (device_info.led_count_known == 0) {
        var led_count: c_int = undefined;
        ret = c.asphodel_get_led_count_blocking(device, &led_count);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        device_info.led_count_known = 1;
        device_info.led_count = @intCast(led_count);

        incrementer.increment(1, "LED Count");
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearRgbLedCount(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.rgb_count_known = 0;
    device_info.rgb_count = 0;
    device_info.rgb_settings = null; // necessary for certain flag + cache combos

    device_info.led_count_known = 0;
    device_info.led_count = 0;
    device_info.led_settings = null; // necessary for certain flag + cache combos
}

fn firstPassRepoDetails(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    var total: u32 = 0;

    if (device_info.commit_id == null) total += 1;
    if (device_info.repo_branch == null) total += 1;
    if (device_info.repo_name == null) total += 1;

    return .{
        .total = total,
        .second_pass_needed = total != 0,
    };
}

fn secondPassRepoDetails(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    var buffer: [256]u8 = undefined;
    var ret: c_int = undefined;

    if (device_info.commit_id == null) {
        ret = c.asphodel_get_commit_id_blocking(device, &buffer, buffer.len);
        if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
            // not supported
            device_info.commit_id = "";
        } else if (ret != c.ASPHODEL_SUCCESS) {
            return ret;
        } else {
            device_info.commit_id = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        }
        incrementer.increment(1, "Commit ID");
    }

    if (device_info.repo_branch == null) {
        ret = c.asphodel_get_repo_branch_blocking(device, &buffer, buffer.len);
        if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
            // not supported
            device_info.repo_branch = "";
        } else if (ret != c.ASPHODEL_SUCCESS) {
            return ret;
        } else {
            device_info.repo_branch = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        }
        incrementer.increment(1, "Repo Branch");
    }

    if (device_info.repo_name == null) {
        ret = c.asphodel_get_repo_name_blocking(device, &buffer, buffer.len);
        if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
            // not supported
            device_info.repo_name = "";
        } else if (ret != c.ASPHODEL_SUCCESS) {
            return ret;
        } else {
            device_info.repo_name = allocator.dupeZ(u8, std.mem.sliceTo(&buffer, 0)) catch return c.ASPHODEL_NO_MEM;
        }
        incrementer.increment(1, "Repo Name");
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearRepoDetails(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.commit_id = null;
    device_info.repo_branch = null;
    device_info.repo_name = null;
}

fn firstPassStreams(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.stream_count_known == 0) {
        var stream_count: c_int = undefined;
        var stream_filler_bits: u8 = undefined;
        var stream_id_bits: u8 = undefined;

        const ret = c.asphodel_get_stream_count_blocking(device, &stream_count, &stream_filler_bits, &stream_id_bits);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.stream_count_known = 1;
        device_info.stream_count = @intCast(stream_count);
        device_info.stream_filler_bits = stream_filler_bits;
        device_info.stream_id_bits = stream_id_bits;

        finished += 1;
        total += 1 + 2 * @as(u32, @intCast(stream_count)); // each stream needs 2 transfers
    } else if (device_info.stream_count > 0) {
        if (device_info.streams) |streams| {
            // we have the array, but its elements may not be complete
            for (streams[0..device_info.stream_count]) |*stream| {
                if (stream.channel_count == 0) {
                    total += 1; // need to fetch the channel list for this stream
                }
            }
        } else {
            // need the whole array
            total += 2 * @as(u32, @intCast(device_info.stream_count)); // each stream needs 2 transfers
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassStreams(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.stream_count_known != 0);
    std.debug.assert(device_info.stream_count > 0);

    var ret: c_int = undefined;

    if (device_info.streams) |streams| {
        // we have the array, but at least some of its elements are not complete
        ret = fillStreamChannels(allocator, device, streams[0..device_info.stream_count], incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    } else {
        // allocate the array but don't assign it to the device info until it's been filled
        const streams = allocator.alloc(c.AsphodelStreamInfo_t, device_info.stream_count) catch return c.ASPHODEL_NO_MEM;

        for (streams, 0..) |*stream, i| {
            // initialize these values so we can safely call fillStreamChannels, because they're not set in asphodel_get_stream_format_blocking()
            stream.channel_count = 0;
            stream.channel_index_list = null;

            ret = c.asphodel_get_stream_format_blocking(device, @intCast(i), stream);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            incrementer.increment(1, "Stream Format");
        }

        // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
        device_info.streams = streams.ptr;

        // fetch all of the remaining info (not necessary for valid json output)
        ret = fillStreamChannels(allocator, device, streams, incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillStreamChannels(allocator: Allocator, device: *c.AsphodelDevice_t, streams: []c.AsphodelStreamInfo_t, incrementer: *Incrementer) c_int {
    for (streams, 0..) |*stream, i| {
        if (stream.channel_count == 0) {
            var channels: [255]u8 = undefined;
            var channel_count: u8 = channels.len;
            const ret = c.asphodel_get_stream_channels_blocking(device, @intCast(i), &channels, &channel_count);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            if (channel_count != 0) {
                const channel_slice = allocator.dupe(u8, channels[0..channel_count]) catch return c.ASPHODEL_NO_MEM;
                stream.channel_index_list = channel_slice.ptr;
                stream.channel_count = channel_count;
            }

            incrementer.increment(1, "Stream Channels");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearStreams(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.stream_count_known = 0;
    device_info.stream_filler_bits = 0;
    device_info.stream_id_bits = 0;
    device_info.stream_count = 0;
    device_info.streams = null;
}

fn firstPassStreamRates(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    std.debug.assert(device_info.stream_count_known != 0); // should have been fetched by firstPassStreams()

    var total: u32 = 0;

    if (device_info.stream_count > 0) {
        if (device_info.stream_rates == null) {
            // need the whole array
            total += @as(u32, @intCast(device_info.stream_count));
        }
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassStreamRates(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    // this function should only be called if firstPassStreamRates() returned .second_pass_needed = true
    std.debug.assert(device_info.stream_count_known != 0);
    std.debug.assert(device_info.stream_count > 0);
    std.debug.assert(device_info.stream_rates == null);

    // allocate the array but don't assign it to the device info until it's been filled
    const stream_rates = allocator.alloc(c.AsphodelStreamRateInfo_t, device_info.stream_count) catch return c.ASPHODEL_NO_MEM;
    @memset(stream_rates, .{});

    for (stream_rates, 0..) |*stream_rate, i| {
        const ret = c.asphodel_get_stream_rate_info_blocking(
            device,
            @intCast(i),
            &stream_rate.available,
            &stream_rate.channel_index,
            &stream_rate.invert,
            &stream_rate.scale,
            &stream_rate.offset,
        );
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        incrementer.increment(1, "Stream Rate");
    }

    device_info.stream_rates = stream_rates.ptr;

    return c.ASPHODEL_SUCCESS;
}

fn clearStreamRates(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.stream_rates = null;
}

fn firstPassChannels(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.channel_count_known == 0) {
        var channel_count: c_int = undefined;

        const ret = c.asphodel_get_channel_count_blocking(device, &channel_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.channel_count_known = 1;
        device_info.channel_count = @intCast(channel_count);

        finished += 1;
        total += 1 + 4 * @as(u32, @intCast(channel_count)); // each channel needs 4 transfers
    } else if (device_info.channel_count > 0) {
        if (device_info.channels) |channels| {
            // we have the array, but its elements may not be complete
            for (channels[0..device_info.channel_count]) |*channel| {
                if (channel.name_length == 0) {
                    total += 1; // need to fetch the channel name for this channel
                }

                if (channel.coefficients_length == 0) {
                    total += 1; // need to fetch the coefficients for this channel
                }

                if (channel.chunk_count > 0) {
                    if (channel.chunk_lengths) |chunk_lengths| {
                        for (chunk_lengths[0..channel.chunk_count]) |chunk_length| {
                            if (chunk_length == 0) {
                                total += 1; // need to fetch some/all chunks for this channel, but it all counts as one regardless of the reality
                                break;
                            }
                        }
                    } else {
                        // missing chunk lengths array: this must have deserialized from a different code base, but it's not an issue
                        total += 1;
                    }
                }
            }
        } else {
            // need the whole array
            total += 4 * @as(u32, @intCast(device_info.channel_count)); // each channel needs 4 transfers
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassChannels(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.channel_count_known != 0);
    std.debug.assert(device_info.channel_count > 0);

    var ret: c_int = undefined;

    if (device_info.channels) |channels| {
        // we have the array, but at least some of its elements are not complete
        ret = fillChannelNames(allocator, device, channels[0..device_info.channel_count], incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        ret = fillChannelCoefficients(allocator, device, channels[0..device_info.channel_count], incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        // only increment channels that needed chunks, because we only added missing chunks in the first pass
        ret = fillChannelChunks(allocator, device, channels[0..device_info.channel_count], incrementer, false);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    } else {
        // allocate the array but don't assign it to the device info until it's been filled
        const channels = allocator.alloc(c.AsphodelChannelInfo_t, device_info.channel_count) catch return c.ASPHODEL_NO_MEM;

        for (channels, 0..) |*channel, i| {
            // initialize these values so we can safely call fillChannel*(), because they're not set in asphodel_get_channel_info_blocking()
            channel.name_length = 0;
            channel.name = null;
            channel.coefficients_length = 0;
            channel.coefficients = null;
            channel.chunks = null;
            channel.chunk_lengths = null;

            ret = c.asphodel_get_channel_info_blocking(device, @intCast(i), channel);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            incrementer.increment(1, "Channel Info");
        }

        // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
        device_info.channels = channels.ptr;

        // fetch all of the remaining info (not necessary for valid json output)
        ret = fillChannelNames(allocator, device, channels, incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        ret = fillChannelCoefficients(allocator, device, channels, incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        // increment all channels because we assumed all channels would have chunks in the first pass
        ret = fillChannelChunks(allocator, device, channels, incrementer, true);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillChannelNames(allocator: Allocator, device: *c.AsphodelDevice_t, channels: []c.AsphodelChannelInfo_t, incrementer: *Incrementer) c_int {
    for (channels, 0..) |*channel, i| {
        if (channel.name_length == 0) {
            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            const ret = c.asphodel_get_channel_name_blocking(device, @intCast(i), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            channel.name = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
            channel.name_length = length;

            incrementer.increment(1, "Channel Name");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillChannelCoefficients(allocator: Allocator, device: *c.AsphodelDevice_t, channels: []c.AsphodelChannelInfo_t, incrementer: *Incrementer) c_int {
    for (channels, 0..) |*channel, i| {
        if (channel.coefficients_length == 0) {
            var coefficients: [255]f32 = undefined;
            var length: u8 = coefficients.len;
            const ret = c.asphodel_get_channel_coefficients_blocking(device, @intCast(i), &coefficients, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            if (length != 0) {
                const slice = allocator.dupe(f32, coefficients[0..length]) catch return c.ASPHODEL_NO_MEM;
                channel.coefficients = slice.ptr;
                channel.coefficients_length = length;
            }

            incrementer.increment(1, "Channel Coefficients");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillChannelChunks(allocator: Allocator, device: *c.AsphodelDevice_t, channels: []c.AsphodelChannelInfo_t, incrementer: *Incrementer, increment_all: bool) c_int {
    // if increment_all is true then the first pass assumed all channels have one chunk.
    // if increment_all is false then the first pass only accounted for channels missing one or more chunks (but still only counts them as 1 transfer)

    for (channels, 0..) |*channel, i| {
        var missing_chunks: bool = false;
        if (channel.chunk_count > 0) {
            if (channel.chunks == null) {
                // allocate the outer array and memset it to nulls
                const array = allocator.alloc(?[*]const u8, channel.chunk_count) catch return c.ASPHODEL_NO_MEM;
                @memset(array, null);
                channel.chunks = array.ptr;
            }

            if (channel.chunk_lengths == null) {
                // allocate the array and memset it to zeros
                const array = allocator.alloc(u8, channel.chunk_count) catch return c.ASPHODEL_NO_MEM;
                @memset(array, 0);
                channel.chunk_lengths = array.ptr;
            }

            const chunks: []?[*]const u8 = channel.chunks[0..channel.chunk_count];
            const chunk_lengths: []u8 = channel.chunk_lengths[0..channel.chunk_count];

            for (chunks, chunk_lengths, 0..) |*chunk, *chunk_length, j| {
                if (chunk.* == null or chunk_length.* == 0) {
                    missing_chunks = true;

                    var buffer: [255]u8 = undefined;
                    var length: u8 = buffer.len;
                    const ret = c.asphodel_get_channel_chunk_blocking(device, @intCast(i), @intCast(j), &buffer, &length);
                    if (ret != c.ASPHODEL_SUCCESS) return ret;

                    if (length != 0) {
                        const slice = allocator.dupe(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
                        chunk.* = slice.ptr;
                        chunk_length.* = length;
                    }
                }
            }
        }

        if (missing_chunks or increment_all) {
            incrementer.increment(1, "Channel Chunks");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearChannels(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.channel_count_known = 0;
    device_info.channel_count = 0;
    device_info.channels = null;
}

fn firstPassChannelCalibrations(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    std.debug.assert(device_info.channel_count_known != 0); // should have been fetched by firstPassChannels()

    var total: u32 = undefined;

    if (device_info.channel_calibrations == null) {
        total = @intCast(device_info.channel_count);
    } else {
        // if we have the top level array, then everything is present
        total = 0;
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassChannelCalibrations(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.channel_count_known != 0);
    std.debug.assert(device_info.channel_count > 0);
    std.debug.assert(device_info.channel_calibrations == null);

    // allocate the array but don't assign it to the device info until it's been filled
    const channel_calibrations = allocator.alloc(?*c.AsphodelChannelCalibration_t, device_info.channel_count) catch return c.ASPHODEL_NO_MEM;

    for (channel_calibrations, 0..) |*calibration_ptr, i| {
        var available: c_int = undefined;
        var calibration: c.AsphodelChannelCalibration_t = undefined;
        const ret = c.asphodel_get_channel_calibration_blocking(device, @intCast(i), &available, &calibration);
        if (ret == c.ERROR_CODE_UNIMPLEMENTED_COMMAND) {
            available = 0;
        } else if (ret != c.ASPHODEL_SUCCESS) {
            return ret;
        }

        if (available == 0) {
            calibration_ptr.* = null;
        } else {
            const ptr = allocator.create(c.AsphodelChannelCalibration_t) catch return c.ASPHODEL_NO_MEM;
            ptr.* = calibration;
            calibration_ptr.* = ptr;
        }

        incrementer.increment(1, "Channel Calibration");
    }

    // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
    device_info.channel_calibrations = channel_calibrations.ptr;

    return c.ASPHODEL_SUCCESS;
}

fn clearChannelCalibrations(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.channel_calibrations = null;
}

fn firstPassSupplies(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.supply_count_known == 0) {
        var supply_count: c_int = undefined;

        const ret = c.asphodel_get_supply_count_blocking(device, &supply_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.supply_count_known = 1;
        device_info.supply_count = @intCast(supply_count);

        finished += 1;
        total += 1 + 2 * @as(u32, @intCast(supply_count)); // each supply needs 2 transfers
    } else if (device_info.supply_count > 0) {
        if (device_info.supplies) |supplies| {
            // we have the array, but its elements may not be complete
            for (supplies[0..device_info.supply_count]) |*supply| {
                if (supply.name_length == 0) {
                    total += 1; // need to fetch the name for this supply
                }
            }
        } else {
            // need the whole array
            total += 2 * @as(u32, @intCast(device_info.supply_count)); // each supply needs 2 transfers
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassSupplies(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.supply_count_known != 0);
    std.debug.assert(device_info.supply_count > 0);

    var ret: c_int = undefined;

    if (device_info.supplies) |supplies| {
        // we have the array, but at least some of its elements are not complete
        ret = fillSupplyNames(allocator, device, supplies[0..device_info.supply_count], incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    } else {
        // allocate the array but don't assign it to the device info until it's been filled
        const supplies = allocator.alloc(c.AsphodelSupplyInfo_t, device_info.supply_count) catch return c.ASPHODEL_NO_MEM;

        for (supplies, 0..) |*supply, i| {
            // initialize these values so we can safely call fillSupplyNames(), because they're not set in asphodel_get_supply_info_blocking()
            supply.name_length = 0;
            supply.name = null;

            ret = c.asphodel_get_supply_info_blocking(device, @intCast(i), supply);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            incrementer.increment(1, "Supply Info");
        }

        // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
        device_info.supplies = supplies.ptr;

        // fetch all of the remaining info (not necessary for valid json output)
        ret = fillSupplyNames(allocator, device, supplies, incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillSupplyNames(allocator: Allocator, device: *c.AsphodelDevice_t, supplies: []c.AsphodelSupplyInfo_t, incrementer: *Incrementer) c_int {
    for (supplies, 0..) |*supply, i| {
        if (supply.name_length == 0) {
            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            const ret = c.asphodel_get_supply_name_blocking(device, @intCast(i), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            supply.name = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
            supply.name_length = length;

            incrementer.increment(1, "Supply Name");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearSupplies(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.supply_count_known = 0;
    device_info.supply_count = 0;
    device_info.supplies = null;
}

fn firstPassSupplyResults(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    std.debug.assert(device_info.supply_count_known != 0); // should have been fetched by firstPassSupplies()

    const total: u32 = @intCast(device_info.supply_count); // supply results are never cached, so we always need all of them

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassSupplyResults(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    // this function should only be called if firstPassSupplyResults() returned .second_pass_needed = true
    std.debug.assert(device_info.supply_count_known != 0);
    std.debug.assert(device_info.supply_count > 0);

    // allocate the array but don't assign it to the device info until it's been filled
    const supply_results = allocator.alloc(c.AsphodelSupplyResult_t, device_info.supply_count) catch return c.ASPHODEL_NO_MEM;

    for (supply_results, 0..) |*supply_result, i| {
        supply_result.error_code = c.asphodel_check_supply_blocking(
            device,
            @intCast(i),
            &supply_result.measurement,
            &supply_result.result,
            20,
        );

        incrementer.increment(1, "Supply Result");
    }

    device_info.supply_results = supply_results.ptr;

    return c.ASPHODEL_SUCCESS;
}

fn clearSupplyResults(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.supply_results = null;
}

fn firstPassCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.ctrl_var_count_known == 0) {
        var ctrl_var_count: c_int = undefined;

        const ret = c.asphodel_get_ctrl_var_count_blocking(device, &ctrl_var_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.ctrl_var_count_known = 1;
        device_info.ctrl_var_count = @intCast(ctrl_var_count);

        finished += 1;
        total += 1 + 2 * @as(u32, @intCast(ctrl_var_count)); // each ctrl var needs 2 transfers
    } else if (device_info.ctrl_var_count > 0) {
        if (device_info.ctrl_vars) |ctrl_vars| {
            // we have the array, but its elements may not be complete
            for (ctrl_vars[0..device_info.ctrl_var_count]) |*ctrl_var| {
                if (ctrl_var.name_length == 0) {
                    total += 1; // need to fetch the name for this ctrl var
                }
            }
        } else {
            // need the whole array
            total += 2 * @as(u32, @intCast(device_info.ctrl_var_count)); // each ctrl var needs 2 transfers
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.ctrl_var_count_known != 0);
    std.debug.assert(device_info.ctrl_var_count > 0);

    var ret: c_int = undefined;

    if (device_info.ctrl_vars) |ctrl_vars| {
        // we have the array, but at least some of its elements are not complete
        ret = fillCtrlVarNames(allocator, device, ctrl_vars[0..device_info.ctrl_var_count], incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    } else {
        // allocate the array but don't assign it to the device info until it's been filled
        const ctrl_vars = allocator.alloc(c.AsphodelCtrlVarInfo_t, device_info.ctrl_var_count) catch return c.ASPHODEL_NO_MEM;

        for (ctrl_vars, 0..) |*ctrl_var, i| {
            // initialize these values so we can safely call fillCtrlVarNames(), because they're not set in asphodel_get_ctrl_var_info_blocking()
            ctrl_var.name_length = 0;
            ctrl_var.name = null;

            ret = c.asphodel_get_ctrl_var_info_blocking(device, @intCast(i), ctrl_var);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            incrementer.increment(1, "Ctrl Var Info");
        }

        // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
        device_info.ctrl_vars = ctrl_vars.ptr;

        // fetch all of the remaining info (not necessary for valid json output)
        ret = fillCtrlVarNames(allocator, device, ctrl_vars, incrementer);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillCtrlVarNames(allocator: Allocator, device: *c.AsphodelDevice_t, ctrl_vars: []c.AsphodelCtrlVarInfo_t, incrementer: *Incrementer) c_int {
    for (ctrl_vars, 0..) |*ctrl_var, i| {
        if (ctrl_var.name_length == 0) {
            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            const ret = c.asphodel_get_ctrl_var_name_blocking(device, @intCast(i), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            ctrl_var.name = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
            ctrl_var.name_length = length;

            incrementer.increment(1, "Ctrl Var Name");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearCtrlVars(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.ctrl_var_count_known = 0;
    device_info.ctrl_var_count = 0;
    device_info.ctrl_vars = null;
}

fn firstPassCtrlVarStates(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    std.debug.assert(device_info.ctrl_var_count_known != 0); // should have been fetched by firstPassCtrlVars()

    const total: u32 = @intCast(device_info.ctrl_var_count); // ctrl var states are never cached, so we always need all of them

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassCtrlVarStates(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    // this function should only be called if firstPassCtrlVarStates() returned .second_pass_needed = true
    std.debug.assert(device_info.ctrl_var_count_known != 0);
    std.debug.assert(device_info.ctrl_var_count > 0);

    // allocate the array but don't assign it to the device info until it's been filled
    const ctrl_var_states = allocator.alloc(i32, device_info.ctrl_var_count) catch return c.ASPHODEL_NO_MEM;

    for (ctrl_var_states, 0..) |*ctrl_var_state, i| {
        const ret = c.asphodel_get_ctrl_var_blocking(device, @intCast(i), ctrl_var_state);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        incrementer.increment(1, "Ctrl Var State");
    }

    device_info.ctrl_var_states = ctrl_var_states.ptr;

    return c.ASPHODEL_SUCCESS;
}

fn clearCtrlVarStates(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.ctrl_var_states = null;
}

fn firstPassSettings(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    // NOTE: the json serializer needs the settings to be complete (name + default bytes), so we either need the whole array or nothing

    if (device_info.setting_count_known == 0) {
        var setting_count: c_int = undefined;

        const ret = c.asphodel_get_setting_count_blocking(device, &setting_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.setting_count_known = 1;
        device_info.setting_count = @intCast(setting_count);

        finished += 1;
        total += 1 + 3 * @as(u32, @intCast(setting_count)); // each setting needs 3 transfers
    } else if (device_info.setting_count > 0) {
        if (device_info.settings == null) {
            // need the whole array
            total += 3 * @as(u32, @intCast(device_info.setting_count)); // each setting needs 3 transfers
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassSettings(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.setting_count_known != 0);
    std.debug.assert(device_info.setting_count > 0);
    std.debug.assert(device_info.settings == null);

    var ret: c_int = undefined;

    // allocate the array but don't assign it to the device info until it's been completely filled
    const settings = allocator.alloc(c.AsphodelSettingInfo_t, device_info.setting_count) catch return c.ASPHODEL_NO_MEM;

    for (settings, 0..) |*setting, i| {
        ret = c.asphodel_get_setting_info_blocking(device, @intCast(i), setting);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        var buffer: [255]u8 = undefined;
        var length: u8 = buffer.len;
        ret = c.asphodel_get_setting_name_blocking(device, @intCast(i), &buffer, &length);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        setting.name = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
        setting.name_length = length;

        length = buffer.len;
        ret = c.asphodel_get_setting_default_blocking(device, @intCast(i), &buffer, &length);
        if (ret != c.ASPHODEL_SUCCESS) return ret;
        if (length != 0) {
            const slice = allocator.dupe(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
            setting.default_bytes = slice.ptr;
            setting.default_bytes_length = length;
        } else {
            setting.default_bytes = null;
            setting.default_bytes_length = 0;
        }

        incrementer.increment(3, "Setting");
    }

    // now that the array is filled (and will serialize to json correctly), we can assign it to the device info
    device_info.settings = settings.ptr;

    return c.ASPHODEL_SUCCESS;
}

fn clearSettings(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.setting_count_known = 0;
    device_info.setting_count = 0;
    device_info.settings = null;
}

fn firstPassCustomEnums(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.custom_enum_lengths == null) {
        // need everything
        var buffer: [255]u8 = undefined;
        var length: u8 = buffer.len;
        const ret = c.asphodel_get_custom_enum_counts_blocking(device, &buffer, &length);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        finished += 1;
        total += 1;

        if (length > 0) {
            const slice = allocator.dupe(u8, buffer[0..length]) catch return .{ .result_code = c.ASPHODEL_NO_MEM };
            device_info.custom_enum_lengths = slice.ptr;
            device_info.custom_enum_count = slice.len;

            for (slice) |enum_length| {
                total += enum_length;
            }
        } else {
            // we need to allocate something to make custom_enum_lengths non-null
            const slice = allocator.alloc(u8, 0) catch return .{ .result_code = c.ASPHODEL_NO_MEM };
            device_info.custom_enum_lengths = slice.ptr;
            device_info.custom_enum_count = 0;
            device_info.custom_enum_values = null;
        }
    } else if (device_info.custom_enum_count > 0) {
        if (device_info.custom_enum_values) |custom_enum_values| {
            for (custom_enum_values[0..device_info.custom_enum_count], 0..) |enum_values, i| {
                const enum_length = device_info.custom_enum_lengths[i];
                if (enum_values) |values| {
                    for (values[0..enum_length]) |value| {
                        if (value == null) {
                            total += 1; // need to fetch the value for this enum
                        }
                    }
                } else {
                    // need all values for this enum
                    total += enum_length;
                }
            }
        } else {
            // need everything
            for (device_info.custom_enum_lengths[0..device_info.custom_enum_count]) |enum_length| {
                total += enum_length;
            }
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassCustomEnums(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.custom_enum_count > 0);
    std.debug.assert(device_info.custom_enum_lengths != null);

    if (device_info.custom_enum_values == null) {
        // allocate the outer array
        const outer = allocator.alloc(?[*]?[*:0]const u8, device_info.custom_enum_count) catch return c.ASPHODEL_NO_MEM;
        @memset(outer, null);
        device_info.custom_enum_values = outer.ptr;
    }

    const enum_lengths: []const u8 = device_info.custom_enum_lengths[0..device_info.custom_enum_count];
    const enum_values: []?[*]?[*:0]const u8 = device_info.custom_enum_values[0..device_info.custom_enum_count];

    for (enum_values, enum_lengths, 0..) |*enum_array, enum_length, i| {
        if (enum_length == 0) continue;
        if (enum_array.* == null) {
            // allocate the inner array
            const inner = allocator.alloc(?[*:0]const u8, enum_length) catch return c.ASPHODEL_NO_MEM;
            @memset(inner, null);
            enum_array.* = inner.ptr;
        }

        for (enum_array.*.?[0..enum_length], 0..) |*value, j| {
            if (value.* != null) continue; // already have it

            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            const ret = c.asphodel_get_custom_enum_value_name_blocking(device, @intCast(i), @intCast(j), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            value.* = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;

            incrementer.increment(1, "Custom Enum Value");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearCustomEnums(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.custom_enum_count = 0;
    device_info.custom_enum_lengths = null;
    device_info.custom_enum_values = null;
}

fn firstPassSettingCategories(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = flags;

    var finished: u32 = 0;
    var total: u32 = 0;

    if (device_info.setting_category_count_known == 0) {
        var setting_category_count: c_int = undefined;

        const ret = c.asphodel_get_setting_category_count_blocking(device, &setting_category_count);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        device_info.setting_category_count_known = 1;
        device_info.setting_category_count = @intCast(setting_category_count);

        finished += 1;
        total += 1 + 2 * @as(u32, @intCast(setting_category_count)); // each setting category needs 2 transfers
    } else if (device_info.setting_category_count > 0) {
        if (device_info.setting_category_names) |setting_category_names| {
            for (setting_category_names[0..device_info.setting_category_count]) |setting_category_name| {
                if (setting_category_name == null) total += 1; // need to fetch the name for this setting category
            }
        } else {
            // need all of the names
            total += @as(u32, @intCast(device_info.setting_category_count));
        }

        if (device_info.setting_category_settings_lengths) |setting_category_settings_lengths| {
            for (setting_category_settings_lengths[0..device_info.setting_category_count]) |length| {
                if (length == 0) total += 1; // need to fetch the settings list for this setting category
            }
        } else {
            // need all of the setting category settings
            total += @as(u32, @intCast(device_info.setting_category_count));
        }
    }

    return .{
        .finished = finished,
        .total = total,
        .second_pass_needed = finished < total,
    };
}

fn secondPassSettingCategories(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.setting_category_count_known != 0);
    std.debug.assert(device_info.setting_category_count > 0);

    var ret: c_int = undefined;

    if (device_info.setting_category_names == null) {
        // allocate the array
        const slice = allocator.alloc(?[*]const u8, device_info.setting_category_count) catch return c.ASPHODEL_NO_MEM;
        @memset(slice, null);
        device_info.setting_category_names = slice.ptr;
    }

    if (device_info.setting_category_settings_lengths == null) {
        // allocate the array
        const slice = allocator.alloc(u8, device_info.setting_category_count) catch return c.ASPHODEL_NO_MEM;
        @memset(slice, 0);
        device_info.setting_category_settings_lengths = slice.ptr;
    }

    if (device_info.setting_category_settings == null) {
        // allocate the array
        const slice = allocator.alloc(?[*]u8, device_info.setting_category_count) catch return c.ASPHODEL_NO_MEM;
        @memset(slice, null);
        device_info.setting_category_settings = slice.ptr;
    }

    const setting_category_names: []?[*:0]const u8 = device_info.setting_category_names[0..device_info.setting_category_count];
    ret = fillSettingCategoryNames(allocator, device, setting_category_names, incrementer);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    const category_settings_lengths: []u8 = device_info.setting_category_settings_lengths[0..device_info.setting_category_count];
    const category_settings: []?[*]u8 = device_info.setting_category_settings[0..device_info.setting_category_count];

    for (category_settings_lengths, category_settings, 0..) |*length_ptr, *settings, i| {
        if (settings.* == null or length_ptr.* == 0) {
            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            ret = c.asphodel_get_setting_category_settings_blocking(device, @intCast(i), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            if (length > 0) {
                const slice = allocator.dupe(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
                settings.* = slice.ptr;
                length_ptr.* = length;
            }

            incrementer.increment(1, "Setting Category Settings");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn fillSettingCategoryNames(allocator: Allocator, device: *c.AsphodelDevice_t, settings_category_names: []?[*:0]const u8, incrementer: *Incrementer) c_int {
    for (settings_category_names, 0..) |*name, i| {
        if (name.* == null) {
            var buffer: [255]u8 = undefined;
            var length: u8 = buffer.len;
            const ret = c.asphodel_get_setting_category_name_blocking(device, @intCast(i), &buffer, &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            name.* = allocator.dupeZ(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;

            incrementer.increment(1, "Setting Category Name");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn clearSettingCategories(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.setting_category_count_known = 0;
    device_info.setting_category_count = 0;
    device_info.setting_category_names = null;
    device_info.setting_category_settings_lengths = null;
    device_info.setting_category_settings = null;
}

fn firstPassDeviceMode(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;

    var total: u32 = undefined;

    if (device_info.supports_device_mode) |supports_device_mode| {
        if (supports_device_mode.* != 0) {
            // device mode is supported
            const want_device_mode: bool = (flags & c.ASPHODEL_NO_DEVICE_MODE_STATE) == 0;
            total = if (want_device_mode) 1 else 0;
        } else {
            // device mode is not supported
            total = 0;
        }
    } else {
        // need to fetch the device mode to know if it's supported
        total = 1;
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassDeviceMode(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags; // NOTE: we write the device mode regardless of c.ASPHODEL_NO_DEVICE_MODE_STATE because we're fetching it no matter what

    const ret = c.asphodel_get_device_mode_blocking(device, &device_info.device_mode);

    const supported: u8 = switch (ret) {
        c.ASPHODEL_SUCCESS => 1,
        c.ERROR_CODE_UNIMPLEMENTED_COMMAND => 0,
        else => return ret,
    };

    const ptr = allocator.create(u8) catch return c.ASPHODEL_NO_MEM;
    ptr.* = supported;
    device_info.supports_device_mode = ptr;

    incrementer.increment(1, "Device Mode");

    return c.ASPHODEL_SUCCESS;
}

fn clearDeviceMode(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.supports_device_mode = null;
    device_info.device_mode = 0;
}

fn firstPassRfPowerCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.supports_rf_power == 0) {
        clearRfPowerCtrlVars(device_info);
        return .{};
    }

    var total: u32 = 0;

    if (device_info.rf_power_ctrl_var_count_known == 0) {
        total += 1; // ctrl var list is sent all in one transfer
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassRfPowerCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.supports_rf_power != 0);
    std.debug.assert(device_info.rf_power_ctrl_var_count_known == 0);

    var buffer: [255]u8 = undefined;
    var length: u8 = buffer.len;
    const ret = c.asphodel_get_rf_power_ctrl_vars_blocking(device, &buffer, &length);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    const slice = allocator.dupe(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
    device_info.rf_power_ctrl_vars = slice.ptr;
    device_info.rf_power_ctrl_var_count = slice.len;
    device_info.rf_power_ctrl_var_count_known = 1;

    incrementer.increment(1, "RF Power Control Variables");

    return c.ASPHODEL_SUCCESS;
}

fn clearRfPowerCtrlVars(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.rf_power_ctrl_var_count_known = 0;
    device_info.rf_power_ctrl_var_count = 0;
    device_info.rf_power_ctrl_vars = null;
}

fn firstPassRfPowerState(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.supports_rf_power == 0) {
        clearRfPowerState(device_info);
        return .{};
    }

    return .{
        .finished = 0,
        .total = 1,
        .second_pass_needed = true,
    };
}

fn secondPassRfPowerState(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = allocator;
    _ = flags;

    std.debug.assert(device_info.supports_rf_power != 0);

    var enabled: c_int = undefined;
    const ret = c.asphodel_get_rf_power_status_blocking(device, &enabled);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    device_info.rf_power_enabled = if (enabled != 0) 1 else 0;

    incrementer.increment(1, "RF Power State");

    return c.ASPHODEL_SUCCESS;
}

fn clearRfPowerState(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.rf_power_enabled = 0;
}

fn firstPassRadioCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.supports_radio == 0) {
        clearRadioCtrlVars(device_info);
        return .{};
    }

    var total: u32 = 0;

    if (device_info.radio_ctrl_var_count_known == 0) {
        total += 1; // ctrl var list is sent all in one transfer
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassRadioCtrlVars(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.supports_radio != 0);
    std.debug.assert(device_info.radio_ctrl_var_count_known == 0);

    var buffer: [255]u8 = undefined;
    var length: u8 = buffer.len;
    const ret = c.asphodel_get_radio_ctrl_vars_blocking(device, &buffer, &length);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    const slice = allocator.dupe(u8, buffer[0..length]) catch return c.ASPHODEL_NO_MEM;
    device_info.radio_ctrl_vars = slice.ptr;
    device_info.radio_ctrl_var_count = slice.len;
    device_info.radio_ctrl_var_count_known = 1;

    incrementer.increment(1, "Radio Control Variables");

    return c.ASPHODEL_SUCCESS;
}

fn clearRadioCtrlVars(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.radio_ctrl_var_count_known = 0;
    device_info.radio_ctrl_var_count = 0;
    device_info.radio_ctrl_vars = null;
}

fn firstPassRadioDefaultSerial(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.supports_radio == 0) {
        clearRadioDefaultSerial(device_info);
        return .{};
    }

    var total: u32 = 0;

    if (device_info.radio_default_serial == null) {
        total += 1;
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassRadioDefaultSerial(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.supports_radio != 0);
    std.debug.assert(device_info.radio_default_serial == null);

    var serial_number: u32 = undefined;
    const ret = c.asphodel_get_radio_default_serial_blocking(device, &serial_number);
    if (ret != c.ASPHODEL_SUCCESS) return ret;

    device_info.radio_default_serial = allocator.create(u32) catch return c.ASPHODEL_NO_MEM;
    device_info.radio_default_serial.* = serial_number;

    incrementer.increment(1, "Radio Default Serial");

    return c.ASPHODEL_SUCCESS;
}

fn clearRadioDefaultSerial(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.radio_default_serial = null;
}

fn firstPassRadioScanPower(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    _ = allocator;
    _ = device;
    _ = flags;

    if (device_info.supports_radio == 0) {
        clearRadioScanPower(device_info);
        return .{};
    }

    var total: u32 = 0;

    if (device_info.radio_scan_power_supported == null) {
        total += 1;
    }

    return .{
        .finished = 0,
        .total = total,
        .second_pass_needed = total > 0,
    };
}

fn secondPassRadioScanPower(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    _ = flags;

    std.debug.assert(device_info.supports_radio != 0);
    std.debug.assert(device_info.radio_scan_power_supported == null);

    const serials: [1]u32 = .{0};
    var powers: [1]i8 = undefined;
    const ret = c.asphodel_get_radio_scan_power_blocking(device, &serials, &powers, serials.len);

    const radio_scan_power_supported: u8 = switch (ret) {
        c.ASPHODEL_SUCCESS => 1,
        c.ERROR_CODE_UNIMPLEMENTED_COMMAND => 0,
        else => return ret,
    };

    const ptr = allocator.create(u8) catch return c.ASPHODEL_NO_MEM;
    ptr.* = radio_scan_power_supported;
    device_info.radio_scan_power_supported = ptr;

    incrementer.increment(1, "Radio Scan Power Supported");

    return c.ASPHODEL_SUCCESS;
}

fn clearRadioScanPower(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.radio_scan_power_supported = null;
}

fn firstPassNvm(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32) StepResult {
    const want_nvm = wantWholeNvm(flags, device_info.nvm_hash != null);
    const want_tags = wantUserTags(flags);

    var ret: c_int = undefined;
    var finished: u32 = 0;
    var total: u32 = 0;

    if (!want_nvm and !want_tags) {
        return .{}; // don't need to do anything
    }

    // we need the size now
    if (device_info.nvm_size == 0) {
        ret = c.asphodel_get_nvm_size_blocking(device, &device_info.nvm_size);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };

        if (device_info.nvm_size == 0) {
            // invalid response from the device
            return .{ .result_code = c.ASPHODEL_MALFORMED_REPLY };
        }

        finished += 1;
        total += 1;
    }

    // we need to fetch the tag locations now
    if (!userTagLocationsPresent(device_info)) {
        ret = c.asphodel_get_user_tag_locations_blocking(device, &device_info.tag_locations);
        if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };
        if (!userTagLocationsPresent(device_info)) {
            // invalid response from the device
            return .{ .result_code = c.ASPHODEL_MALFORMED_REPLY };
        }

        finished += 1;
        total += 1;
    }

    if (device_info.nvm != null) {
        // already have the nvm
        if (want_tags) {
            ret = fillTagsFromNvm(allocator, device_info);
            if (ret != c.ASPHODEL_SUCCESS) return .{ .result_code = ret };
        }

        // don't need a second pass
        if (total != finished) unreachable;
        return .{
            .finished = finished,
            .total = total,
        };
    }

    // calculate the number of transfers for the whole NVM
    const max_bytes_per_command = device_info.max_incoming_param_length & ~@as(usize, 0x3);
    std.debug.assert(max_bytes_per_command >= 4);
    const whole_nvm_transfer_count = std.math.divCeil(usize, device_info.nvm_size, max_bytes_per_command) catch unreachable;

    if (want_nvm or whole_nvm_transfer_count == 1) {
        // we want the whole NVM
        total += @intCast(whole_nvm_transfer_count);
    } else {
        // just want the user tags. calculate the number of transfers needed
        total += calculateUserTagTransferCount(&device_info.tag_locations, max_bytes_per_command);
    }

    return .{
        .second_pass_needed = true,
        .finished = finished,
        .total = total,
    };
}

fn secondPassNvm(allocator: Allocator, device: *c.AsphodelDevice_t, device_info: *c.AsphodelDeviceInfo_t, flags: u32, incrementer: *Incrementer) c_int {
    const want_nvm = wantWholeNvm(flags, device_info.nvm_hash != null);
    const want_tags = wantUserTags(flags);

    std.debug.assert(want_nvm or want_tags); // shouldn't be in the second pass if we don't want either
    std.debug.assert(device_info.nvm == null); // shouldn't be in the second pass if we already have the nvm
    std.debug.assert(device_info.nvm_size != 0); // should be fetched in the first pass
    std.debug.assert(userTagLocationsPresent(device_info)); // should be fetched in the first pass

    var ret: c_int = undefined;

    const max_bytes_per_command = device_info.max_incoming_param_length & ~@as(usize, 0x3);
    std.debug.assert(max_bytes_per_command >= 4);

    if (want_nvm or max_bytes_per_command >= device_info.nvm_size) {
        // we want the whole NVM. allocate the buffer to write into it
        var buffer = allocator.alloc(u8, device_info.nvm_size) catch return c.ASPHODEL_NO_MEM;

        var read_address: usize = 0;
        while (read_address < device_info.nvm_size) {
            const remaining = device_info.nvm_size - read_address;
            var length: usize = remaining;
            ret = c.asphodel_read_nvm_raw_blocking(device, read_address, &buffer[read_address], &length);
            if (ret != c.ASPHODEL_SUCCESS) return ret;

            if (length != @min(remaining, max_bytes_per_command)) {
                // didn't get a full transfer
                return c.ASPHODEL_BAD_REPLY_LENGTH;
            }

            read_address += length;

            incrementer.increment(1, "NVM");
        }

        device_info.nvm = buffer.ptr;

        if (want_tags) {
            ret = fillTagsFromNvm(allocator, device_info);
            if (ret != c.ASPHODEL_SUCCESS) return ret;
        }
    } else {
        // just want the user tags
        const max_transfers = calculateUserTagTransferCount(&device_info.tag_locations, max_bytes_per_command);

        var start1 = device_info.tag_locations[0];
        var len1 = device_info.tag_locations[1];
        var start2 = device_info.tag_locations[2];
        var len2 = device_info.tag_locations[3];

        // make sure the locations are in order
        var swapped: bool = undefined;
        if (start2 < start1) {
            swapped = true;
            std.mem.swap(usize, &start1, &start2);
            std.mem.swap(usize, &len1, &len2);
        } else {
            swapped = false;
        }

        var transfers: u32 = 0;
        var read_bytes: usize = undefined;

        const first_buffer_length = max_bytes_per_command * (std.math.divCeil(usize, len1, max_bytes_per_command) catch unreachable);
        const second_buffer_length = len2; // no benefit from excess bytes
        const buffer_size = @max(first_buffer_length, second_buffer_length);

        // grab the first transfer
        const buffer = allocator.alloc(u8, buffer_size) catch return c.ASPHODEL_NO_MEM;
        const message1: [*:0]const u8 = if (!swapped) "User Tag 1" else "User Tag 2";
        ret = readUserTag(device, buffer[0..first_buffer_length], start1, &read_bytes, &transfers, incrementer, message1);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        // generate the first tag
        var it = std.mem.splitAny(u8, buffer[0..read_bytes], "\xFF\x00");
        var tag = allocator.dupeZ(u8, it.first()) catch return c.ASPHODEL_NO_MEM;
        if (!swapped) {
            device_info.user_tag_1 = tag;
        } else {
            device_info.user_tag_2 = tag;
        }

        var second_tag_buffer: []u8 = undefined;
        if (start2 + len2 <= start1 + read_bytes) {
            // the second transfer is contained within the first
            const start = start2 - start1;
            const end = start + len2;
            second_tag_buffer = buffer[start..end];
        } else {
            const message2: [*:0]const u8 = if (!swapped) "User Tag 2" else "User Tag 1";
            if (start2 <= start1 + read_bytes) {
                // some overlap
                const start = start2 - start1;
                const overlap = read_bytes - start;
                @memmove(buffer[0..overlap], buffer[start..read_bytes]);

                ret = readUserTag(device, buffer[overlap..second_buffer_length], start2 + overlap, &read_bytes, &transfers, incrementer, message2);
                if (ret != c.ASPHODEL_SUCCESS) return ret;
                second_tag_buffer = buffer[0 .. overlap + read_bytes];
            } else {
                // no overlap
                ret = readUserTag(device, buffer[0..second_buffer_length], start2, &read_bytes, &transfers, incrementer, message2);
                if (ret != c.ASPHODEL_SUCCESS) return ret;
                second_tag_buffer = buffer[0..read_bytes];
            }
        }

        // generate the second tag
        it = std.mem.splitAny(u8, second_tag_buffer, "\xFF\x00");
        tag = allocator.dupeZ(u8, it.first()) catch return c.ASPHODEL_NO_MEM;
        if (!swapped) {
            device_info.user_tag_2 = tag;
        } else {
            device_info.user_tag_1 = tag;
        }

        // run any remaining increments
        if (transfers < max_transfers) {
            incrementer.increment(max_transfers - transfers, "User Tag Excess");
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn wantWholeNvm(flags: u32, hash_present: bool) bool {
    if ((flags & c.ASPHODEL_NVM_OPTIONAL) == 0) {
        return true; // the whole nvm has been requested
    } else if (hash_present and wantUserTags(flags)) {
        return true; // the nvm hash allows caching of the NVM, so it's worth grabbing the whole NVM while we fetch the tags
    } else {
        return false;
    }
}

fn wantUserTags(flags: u32) bool {
    return ((flags & c.ASPHODEL_NO_USER_TAG_INFO) == 0);
}

fn userTagLocationsPresent(device_info: *c.AsphodelDeviceInfo_t) bool {
    for (device_info.tag_locations, 0..) |loc, i| {
        if (i % 2 == 1) {
            // check the lengths
            if (loc == 0) {
                return false;
            }
        }
    }
    return true;
}

fn calculateUserTagTransferCount(tag_locations: *const [6]usize, max_bytes_per_command: usize) u32 {
    var start1 = tag_locations[0];
    var len1 = tag_locations[1];
    var start2 = tag_locations[2];
    var len2 = tag_locations[3];

    std.debug.assert(max_bytes_per_command >= 4);

    // make sure the locations are in order
    if (start2 < start1) {
        std.mem.swap(usize, &start1, &start2);
        std.mem.swap(usize, &len1, &len2);
    }

    const first_transfers = std.math.divCeil(usize, len1, max_bytes_per_command) catch unreachable;
    const first_end = start1 + first_transfers * max_bytes_per_command;

    var remaining_bytes: usize = undefined;
    if (start2 + len2 <= first_end) {
        // the second transfer is contained within the first
        remaining_bytes = 0;
    } else if (start2 < first_end) {
        const overlap = first_end - start2;
        remaining_bytes = len2 - overlap;
    } else {
        remaining_bytes = len2;
    }

    const second_transfers = std.math.divCeil(usize, remaining_bytes, max_bytes_per_command) catch unreachable;

    return @intCast(first_transfers + second_transfers);
}

test "calculateUserTagTransferCount" {
    const touching = &[_]usize{ 0, 8, 8, 8, 0, 0 };
    try std.testing.expectEqual(@as(u32, 4), calculateUserTagTransferCount(touching, 4));
    try std.testing.expectEqual(@as(u32, 2), calculateUserTagTransferCount(touching, 12));
    try std.testing.expectEqual(@as(u32, 1), calculateUserTagTransferCount(touching, 16));
    try std.testing.expectEqual(@as(u32, 1), calculateUserTagTransferCount(touching, 24));

    const disjoint = &[_]usize{ 0, 8, 16, 8, 0, 0 };
    try std.testing.expectEqual(@as(u32, 4), calculateUserTagTransferCount(disjoint, 4));
    try std.testing.expectEqual(@as(u32, 2), calculateUserTagTransferCount(disjoint, 12));
    try std.testing.expectEqual(@as(u32, 2), calculateUserTagTransferCount(disjoint, 16));
    try std.testing.expectEqual(@as(u32, 1), calculateUserTagTransferCount(disjoint, 24));

    const out_of_order = &[_]usize{ 8, 8, 0, 8, 0, 0 };
    try std.testing.expectEqual(@as(u32, 4), calculateUserTagTransferCount(out_of_order, 4));
    try std.testing.expectEqual(@as(u32, 2), calculateUserTagTransferCount(out_of_order, 12));
    try std.testing.expectEqual(@as(u32, 1), calculateUserTagTransferCount(out_of_order, 16));
    try std.testing.expectEqual(@as(u32, 1), calculateUserTagTransferCount(out_of_order, 24));
}

fn fillTagsFromNvm(allocator: Allocator, device_info: *c.AsphodelDeviceInfo_t) c_int {
    // NOTE: cached values are always valid, so prefer them

    std.debug.assert(device_info.nvm != null);

    if (device_info.user_tag_1 == null) {
        const start = device_info.tag_locations[0];
        const end = start + device_info.tag_locations[1];
        if (end > device_info.nvm_size) return c.ASPHODEL_MALFORMED_REPLY;

        const slice = device_info.nvm[start..end];
        var it = std.mem.splitAny(u8, slice, "\xFF\x00");

        device_info.user_tag_1 = allocator.dupeZ(u8, it.first()) catch return c.ASPHODEL_NO_MEM;
    }

    if (device_info.user_tag_2 == null) {
        const start = device_info.tag_locations[2];
        const end = start + device_info.tag_locations[3];
        if (end > device_info.nvm_size) return c.ASPHODEL_MALFORMED_REPLY;

        const slice = device_info.nvm[start..end];
        var it = std.mem.splitAny(u8, slice, "\xFF\x00");

        device_info.user_tag_2 = allocator.dupeZ(u8, it.first()) catch return c.ASPHODEL_NO_MEM;
    }

    return c.ASPHODEL_SUCCESS;
}

fn readUserTag(device: *c.AsphodelDevice_t, buffer: []u8, start: usize, read_bytes_out: *usize, transfers: *u32, incrementer: *Incrementer, message: [*:0]const u8) c_int {
    var read_bytes: usize = 0;
    while (read_bytes < buffer.len) {
        const remaining = buffer.len - read_bytes;
        var length: usize = remaining;
        const ret = c.asphodel_read_nvm_raw_blocking(device, read_bytes + start, &buffer[read_bytes], &length);
        if (ret != c.ASPHODEL_SUCCESS) return ret;

        const slice_to_check = buffer[read_bytes .. read_bytes + length];

        read_bytes += length;

        transfers.* += 1;
        incrementer.increment(1, message);

        // break early if the read bytes contain a terminator
        if (std.mem.indexOfAny(u8, slice_to_check, "\xFF\x00") != null) break;
    }

    read_bytes_out.* = read_bytes;

    return c.ASPHODEL_SUCCESS;
}

// NOTE: no clearNvm() function

fn clearUserTags(device_info: *c.AsphodelDeviceInfo_t) void {
    device_info.user_tag_1 = null;
    device_info.user_tag_2 = null;
}
