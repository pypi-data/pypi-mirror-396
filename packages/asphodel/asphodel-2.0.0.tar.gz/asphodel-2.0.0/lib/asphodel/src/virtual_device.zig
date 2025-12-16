const std = @import("std");
const c = @import("root.zig").c;
const version = @import("root.zig").version;
const Allocator = std.mem.Allocator;

// These get filled in on device infos that are missing them. They're the values taken from a WMRP/WMRTCP.
const REMOTE_MAX_INCOMING_PARAM_LENGTH_FALLBACK: usize = 29;
const REMOTE_MAX_OUTGOING_PARAM_LENGTH_FALLBACK: usize = 28;
const REMOTE_STREAM_PACKET_LENGTH_FALLBACK: usize = 64;

const Context = struct { // allocated with c_allocator
    mutex: std.Thread.Mutex.Recursive,
    ref_count: usize, // starts at 1, incremented on getRemoteDevice(), decremented freeDevice()

    main_device: c.AsphodelDevice_t,
    main_internals: DeviceInternals,
    main_open: bool = false,
    main_streaming_state: StreamingState,

    remote_device: ?*c.AsphodelDevice_t, // allocated with main_internals's arena
    remote_internals: ?*DeviceInternals, // allocated with c_allocator
    remote_open: bool = false, // protected by mutex
    remote_streaming_state: StreamingState,

    remote_connect_callback: c.AsphodelConnectCallback_t = null,
    remote_connect_closure: ?*anyopaque = null,
};

const StreamingState = struct {
    streaming_timer: std.time.Timer,
    packet_length: usize = 0, // copied in here when starting streaming for convenience elsewhere
    streaming_callback: c.AsphodelStreamingCallback_t = null,
    streaming_closure: ?*anyopaque = null,
    streaming_packet_count: usize = 0,
    streaming_timeout_ns: u64 = 0,
};

const DeviceInternals = struct {
    arena: std.heap.ArenaAllocator,
    device_info: *const c.AsphodelDeviceInfo_t,
    callbacks: c.AsphodelVirtualDeviceCallbacks_t,
    remaining_transfers: u64,
    reply_buffer: []u8,
    scan_result_buffer: ?[]c.AsphodelExtraScanResult_t = null,
    state: State = State{},
};

const State = struct {
    const StreamState = struct {
        enabled: bool,
        warm_up: bool,
    };

    const RadioState = union(enum) {
        stopped,
        scanning,
        connecting: u32,
        connected: struct { u32, u8 }, // serial number, protocol type
    };

    reset_flag: bool = true,
    nvm_modified: bool = false, // always tracked, but only reported if device_info allows
    rgb_settings: [][3]u8 = &[0][3]u8{},
    led_settings: []u8 = &[0]u8{},
    streams: []StreamState = &[0]StreamState{},
    ctrl_vars: []i32 = &[0]i32{},
    device_mode: u8 = 0, // only reported if device_info allows
    rf_power_enabled: bool = false,
    radio_state: RadioState = .stopped,
    nvm: []u8 = &[0]u8{},
};

pub export fn asphodel_create_virtual_device(device_info: *const c.AsphodelDeviceInfo_t, callbacks: ?*const c.AsphodelVirtualDeviceCallbacks_t, allow_fallback_values: u8, device_out: *?*c.AsphodelDevice_t) c_int {
    const timer = std.time.Timer.start() catch return c.ASPHODEL_NOT_SUPPORTED;

    if (missingRequiredDeviceInfo(device_info)) {
        return c.ASPHODEL_BAD_PARAMETER;
    }

    if (allow_fallback_values == 0 and missingOptionalDeviceInfo(device_info)) {
        return c.ASPHODEL_BAD_PARAMETER;
    }

    var context = std.heap.c_allocator.create(Context) catch return c.ASPHODEL_NO_MEM;
    context.* = .{
        .mutex = std.Thread.Mutex.Recursive.init,
        .ref_count = 1,
        .main_device = undefined,
        .main_internals = .{
            .arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator), // use the raw, as it's faster and safe with arenas
            .device_info = device_info,
            .callbacks = undefined,
            .remaining_transfers = std.math.maxInt(u64),
            .reply_buffer = undefined,
            .state = undefined,
        },
        .main_streaming_state = .{
            .streaming_timer = timer,
        },
        .remote_device = undefined,
        .remote_internals = null,
        .remote_streaming_state = .{
            .streaming_timer = timer,
        },
    };

    const main_allocator: Allocator = context.main_internals.arena.allocator();

    const maybe_reply_buffer = main_allocator.alloc(u8, device_info.max_outgoing_param_length);
    if (maybe_reply_buffer) |reply_buffer| {
        context.main_internals.reply_buffer = reply_buffer;
    } else |_| {
        context.main_internals.arena.deinit();
        std.heap.c_allocator.destroy(context);
        return c.ASPHODEL_NO_MEM;
    }

    createInitialState(&context.main_internals) catch {
        context.main_internals.arena.deinit();
        std.heap.c_allocator.destroy(context);
        return c.ASPHODEL_NO_MEM;
    };

    if (callbacks) |cb| {
        // copy the callbacks in
        context.main_internals.callbacks = cb.*;
    } else {
        // set the callbacks to all nulls
        context.main_internals.callbacks = c.AsphodelVirtualDeviceCallbacks_t{};
    }

    const device = &context.main_device;

    const location_string: [:0]const u8 = blk: {
        if (device_info.location_string) |location_string| {
            break :blk std.mem.span(location_string); // device_info will live as long as the device
        } else {
            std.debug.assert(allow_fallback_values != 0); // location_string checked in missingOptionalDeviceInfo()
            break :blk "UNKNOWN";
        }
    };

    device.* = c.AsphodelDevice_t{
        .protocol_type = getProtocolType(device_info),
        .location_string = location_string,
        .open_device = openDevice,
        .close_device = closeDevice,
        .free_device = freeDevice,
        .get_serial_number = getSerialNumber,
        .do_transfer = doTransfer,
        .do_transfer_reset = doTransferReset,
        .start_streaming_packets = startStreamingPackets,
        .stop_streaming_packets = stopStreamingPackets,
        .get_stream_packets_blocking = getStreamPacketsBlocking,
        .get_max_incoming_param_length = getMaxIncomingParamLength,
        .get_max_outgoing_param_length = getMaxOutgoingParamLength,
        .get_stream_packet_length = getStreamPacketLength,
        .poll_device = pollDevice,
        .set_connect_callback = setConnectCallback,
        .wait_for_connect = waitForConnect,
        .get_remote_device = getRemoteDevice,
        .reconnect_device = reconnectMainDevice,
        .error_callback = null,
        .error_closure = null,
        .reconnect_device_bootloader = reconnectMainDevice,
        .reconnect_device_application = reconnectMainDevice,
        .implementation_info = context,
        .transport_type = "virtual",
        .get_remote_lengths = getRemoteLengths,
    };

    device_out.* = device;

    if (device_info.supports_radio != 0) {
        const remote_location = std.mem.concatWithSentinel(main_allocator, u8, &[_][]const u8{ location_string, "-remote" }, 0) catch {
            context.main_internals.arena.deinit();
            std.heap.c_allocator.destroy(context);
            return c.ASPHODEL_NO_MEM;
        };

        const remote_device = main_allocator.create(c.AsphodelDevice_t) catch {
            context.main_internals.arena.deinit();
            std.heap.c_allocator.destroy(context);
            return c.ASPHODEL_NO_MEM;
        };

        context.remote_device = remote_device;

        remote_device.* = c.AsphodelDevice_t{
            .protocol_type = c.ASPHODEL_PROTOCOL_TYPE_REMOTE,
            .location_string = remote_location,
            .open_device = openDevice,
            .close_device = closeDevice,
            .free_device = freeDevice,
            .get_serial_number = getSerialNumber,
            .do_transfer = doTransfer,
            .do_transfer_reset = doTransferReset,
            .start_streaming_packets = startStreamingPackets,
            .stop_streaming_packets = stopStreamingPackets,
            .get_stream_packets_blocking = getStreamPacketsBlocking,
            .get_max_incoming_param_length = getMaxIncomingParamLength,
            .get_max_outgoing_param_length = getMaxOutgoingParamLength,
            .get_stream_packet_length = getStreamPacketLength,
            .poll_device = pollDevice,
            .set_connect_callback = setConnectCallback,
            .wait_for_connect = waitForConnect,
            .get_remote_device = getRemoteDevice,
            .reconnect_device = reconnectRemoteDevice,
            .error_callback = null,
            .error_closure = null,
            .reconnect_device_bootloader = reconnectRemoteDeviceBoot,
            .reconnect_device_application = reconnectRemoteDeviceApp,
            .implementation_info = context,
            .transport_type = "virtual",
            .get_remote_lengths = getRemoteLengths,
        };
    } else {
        context.remote_device = null;
    }

    return c.ASPHODEL_SUCCESS;
}

pub export fn asphodel_set_virtual_remote_device(device: ?*c.AsphodelDevice_t, serial_number: u32, remote_device_info: ?*const c.AsphodelDeviceInfo_t, callbacks: ?*const c.AsphodelVirtualDeviceCallbacks_t, allow_fallback_values: u8) c_int {
    _ = serial_number;
    _ = callbacks;
    _ = allow_fallback_values;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));
    context.mutex.lock();
    defer context.mutex.unlock();

    // make sure this is being called on the main device of a radio
    if (device != &context.main_device) return c.ASPHODEL_BAD_PARAMETER;
    if (context.remote_device == null) return c.ASPHODEL_NOT_SUPPORTED;

    // free the old remote info, if present
    if (context.remote_internals) |remote_internals| {
        if (context.remote_open) {
            if (remote_internals.callbacks.close_device) |close_device| {
                close_device(remote_internals.callbacks.closure);
            }
        }

        remote_internals.arena.deinit();
        std.heap.c_allocator.destroy(remote_internals);
        context.remote_internals = null;

        stopRadio(&context.main_internals); // TODO: decide if the stop will disconnect the remote or not. Possibly add a function parameter to set the lifetime of the remote.
    }

    if (remote_device_info) |device_info| {
        _ = device_info; // TODO: implement this
    }
    // TODO: implement this

    // TODO: fail if the remote device info doesn't support remote

    // TODO: call the open callback if the remote is already open

    return c.ASPHODEL_NOT_SUPPORTED;
}

pub export fn asphodel_submit_virtual_device_packets(device: ?*c.AsphodelDevice_t, buffer: ?[*]const u8, buffer_length: usize) c_int {
    if (device == null) return c.ASPHODEL_BAD_PARAMETER;

    if (buffer == null or buffer_length == 0) {
        return c.ASPHODEL_BAD_PARAMETER;
    }

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const streaming_state: *StreamingState = blk: {
        if (device == context.remote_device) {
            if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;
            break :blk &context.remote_streaming_state;
        } else {
            if (!context.main_open) return c.ASPHODEL_DEVICE_CLOSED;
            break :blk &context.main_streaming_state;
        }
    };

    var processed_packets: usize = 0;
    if (streaming_state.streaming_callback) |callback| {
        if (streaming_state.packet_length == 0 or buffer_length % streaming_state.packet_length != 0) {
            // packet length shouldn't be zero if the callback exists, but still good practice to check
            return c.ASPHODEL_BAD_PARAMETER;
        }
        const packet_count: usize = @divExact(buffer_length, streaming_state.packet_length);

        while (processed_packets < packet_count) {
            if (streaming_state.streaming_packet_count == 0) break; // can't really happen, but makes this safe
            const remaining = packet_count - processed_packets;
            const to_process: usize = @min(remaining, streaming_state.streaming_packet_count);
            const b = buffer.?[processed_packets * streaming_state.packet_length .. (processed_packets + to_process) * streaming_state.packet_length];
            callback(c.ASPHODEL_SUCCESS, b.ptr, streaming_state.packet_length, to_process, streaming_state.streaming_closure);
            processed_packets += to_process;
        }
    }

    streaming_state.streaming_timer.reset();

    return c.ASPHODEL_SUCCESS;
}

// Sets the maximum number of transfers that can be sent to the device before it will return an error. This is used
// for testing purposes. If the limit is set to 0, then the next transfer will return ASPHODEL_TRANSPORT_ERROR.
pub export fn asphodel_set_virtual_transfer_limit(device: ?*c.AsphodelDevice_t, remaining_transfers: u64) c_int {
    if (device == null) return c.ASPHODEL_BAD_PARAMETER;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const internals: *DeviceInternals = blk: {
        if (device == context.remote_device) {
            if (context.remote_internals) |remote_internals| {
                break :blk remote_internals;
            } else {
                // can this happen?
                return c.ASPHODEL_BAD_PARAMETER;
            }
        } else {
            break :blk &context.main_internals;
        }
    };

    internals.remaining_transfers = remaining_transfers;

    return c.ASPHODEL_SUCCESS;
}

// Returns the number of transfers that can be performed before the device returns an error. By comparing before and
// after, the number of transfers can be measured (assuming the limit is set sufficiently high). When the virtual
// device is created, this limit is set to the largest possible value.
pub export fn asphodel_get_virtual_transfer_limit(device: ?*c.AsphodelDevice_t, remaining_transfers: ?*u64) c_int {
    if (device == null or remaining_transfers == null) return c.ASPHODEL_BAD_PARAMETER;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const internals: *DeviceInternals = blk: {
        if (device == context.remote_device) {
            if (context.remote_internals) |remote_internals| {
                break :blk remote_internals;
            } else {
                // can this happen?
                return c.ASPHODEL_BAD_PARAMETER;
            }
        } else {
            break :blk &context.main_internals;
        }
    };

    remaining_transfers.?.* = internals.remaining_transfers;

    return c.ASPHODEL_SUCCESS;
}

fn missingRequiredDeviceInfo(device_info: *const c.AsphodelDeviceInfo_t) bool {
    // these are things we can't create a fallback for

    if (device_info.max_incoming_param_length < 24) return true;
    if (device_info.max_outgoing_param_length < 24) return true;
    if (device_info.stream_packet_length < 1) return true;

    if (device_info.nvm_size % 4 != 0) return true; // just flat out invalid

    // make sure everything is present for streams
    if (device_info.stream_count_known != 0) {
        if (device_info.stream_count > 0) {
            if (device_info.streams) |streams| {
                for (streams[0..device_info.stream_count]) |*stream| {
                    if (stream.channel_count > 0) {
                        if (stream.channel_index_list == null) return true;
                    }
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for channels
    if (device_info.channel_count_known != 0) {
        if (device_info.channel_count > 0) {
            if (device_info.channels) |channels| {
                for (channels[0..device_info.channel_count]) |*channel| {
                    if (channel.name == null) return true;
                    if (channel.coefficients_length > 0 and channel.coefficients == null) return true;
                    if (channel.chunk_count > 0) {
                        if (channel.chunk_lengths == null) return true;
                        if (channel.chunks) |chunks| {
                            for (chunks[0..channel.chunk_count]) |chunk| {
                                if (chunk == null) return true;
                            }
                        } else {
                            return true;
                        }
                    }
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for supplies
    if (device_info.supply_count_known != 0) {
        if (device_info.supply_count > 0) {
            if (device_info.supplies) |supplies| {
                for (supplies[0..device_info.supply_count]) |*supply| {
                    if (supply.name == null) return true;
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for ctrl vars
    if (device_info.ctrl_var_count_known != 0) {
        if (device_info.ctrl_var_count > 0) {
            if (device_info.ctrl_vars) |ctrl_vars| {
                for (ctrl_vars[0..device_info.ctrl_var_count]) |*ctrl_var| {
                    if (ctrl_var.name == null) return true;
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for settings
    if (device_info.setting_count_known != 0) {
        if (device_info.setting_count > 0) {
            if (device_info.settings) |settings| {
                for (settings[0..device_info.setting_count]) |*setting| {
                    if (setting.name == null) return true;
                    if (setting.default_bytes_length > 0 and setting.default_bytes == null) return true;
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for custom enums
    if (device_info.custom_enum_lengths) |custom_enum_lengths| {
        if (device_info.custom_enum_count > 0) {
            if (device_info.custom_enum_values) |custom_enum_values| {
                for (custom_enum_lengths[0..device_info.custom_enum_count], 0..) |length, i| {
                    if (custom_enum_values[i]) |values| {
                        for (0..length) |j| {
                            if (values[j] == null) return true;
                        }
                    } else {
                        return true;
                    }
                }
            } else {
                return true;
            }
        }
    }

    // make sure everything is present for setting categories
    if (device_info.setting_category_count_known != 0) {
        if (device_info.setting_category_count > 0) {
            if (device_info.setting_category_settings_lengths == null) return true;
            if (device_info.setting_category_names) |names| {
                for (0..device_info.setting_category_count) |i| {
                    if (names[i] == null) return true;
                }
            } else {
                return true;
            }
            if (device_info.setting_category_settings) |settings| {
                for (0..device_info.setting_category_count) |i| {
                    if (settings[i] == null) return true;
                }
            } else {
                return true;
            }
        }
    }

    return false;
}

fn missingOptionalDeviceInfo(device_info: *const c.AsphodelDeviceInfo_t) bool {
    // these are things we can create a fallback for if they're missing

    if (device_info.serial_number == null) return true;
    if (device_info.location_string == null) return true;
    if (device_info.build_date == null) return true;
    if (device_info.build_info == null) return true;
    if (device_info.board_info_name == null) return true;
    if (device_info.protocol_version == null) return true;
    if (device_info.chip_family == null) return true;
    if (device_info.chip_id == null) return true;
    if (device_info.chip_model == null) return true;
    if (device_info.nvm_size == 0 or device_info.nvm == null) return true;
    if (device_info.tag_locations[1] == 0 or device_info.tag_locations[3] == 0 or device_info.tag_locations[5] == 0) return true;

    if (device_info.rgb_count_known != 0) {
        if (device_info.rgb_count > 0) {
            if (device_info.rgb_settings == null) return true;
        }
    }

    if (device_info.led_count_known != 0) {
        if (device_info.led_count > 0) {
            if (device_info.led_settings == null) return true;
        }
    }

    if (device_info.supply_count_known != 0) {
        if (device_info.supply_count > 0) {
            if (device_info.supply_results == null) return true;
        }
    }

    if (device_info.ctrl_var_count_known != 0) {
        if (device_info.ctrl_var_count > 0) {
            if (device_info.ctrl_var_states == null) return true;
        }
    }

    if (device_info.rf_power_ctrl_var_count_known != 0) {
        if (device_info.rf_power_ctrl_var_count > 0) {
            if (device_info.rf_power_ctrl_vars == null) return true;
        }
    }

    if (device_info.radio_ctrl_var_count_known != 0) {
        if (device_info.radio_ctrl_var_count > 0) {
            if (device_info.radio_ctrl_vars == null) return true;
        }
    }

    if (device_info.supports_radio != 0) {
        if (device_info.radio_default_serial == null) return true;
    }

    return false;
}

fn createInitialState(internals: *DeviceInternals) error{OutOfMemory}!void {
    // Mutex must be locked when calling this on remote devices. This is only called on init for non-remote devices.

    const device_info: *const c.AsphodelDeviceInfo_t = internals.device_info;
    const state: *State = &internals.state;
    state.* = State{};

    const allocator: Allocator = internals.arena.allocator();

    if (device_info.nvm_modified) |nvm_modified| {
        state.nvm_modified = nvm_modified.* != 0;
    }

    if (device_info.supports_device_mode) |supports_device_mode| {
        if (supports_device_mode.* != 0) {
            state.device_mode = device_info.device_mode;
        }
    }

    if (device_info.rgb_count_known != 0) {
        if (device_info.rgb_count != 0) {
            state.rgb_settings = try allocator.alloc([3]u8, device_info.rgb_count);
        }
    }

    if (device_info.led_count_known != 0) {
        if (device_info.led_count != 0) {
            state.led_settings = try allocator.alloc(u8, device_info.led_count);
        }
    }

    if (device_info.stream_count_known != 0) {
        if (device_info.stream_count != 0) {
            state.streams = try allocator.alloc(State.StreamState, device_info.stream_count);
        }
    }

    if (device_info.ctrl_var_count_known != 0) {
        if (device_info.ctrl_var_count != 0) {
            state.ctrl_vars = try allocator.alloc(i32, device_info.ctrl_var_count);

            for (state.ctrl_vars, 0..) |*value, i| {
                if (device_info.ctrl_var_states) |ctrl_var_states| {
                    value.* = ctrl_var_states[i];
                } else {
                    // fallback to zero
                    value.* = 0;
                }
            }
        }
    }

    if (device_info.nvm_size != 0) {
        state.nvm = try allocator.dupe(u8, device_info.nvm[0..device_info.nvm_size]);
    } else {
        // create a fallback NVM
        state.nvm = try allocator.alloc(u8, 32 * 3);
        @memset(state.nvm, 0xFF);
    }

    // will set rf_power_enabled, rgb_settings, led_settings, and streams
    flushState(internals, false);
}

fn flushState(internals: *DeviceInternals, run_callback: bool) void {
    // Mutex should be held when this is called

    const device_info: *const c.AsphodelDeviceInfo_t = internals.device_info;
    const state: *State = &internals.state;

    if (device_info.supports_rf_power != 0) {
        state.rf_power_enabled = device_info.rf_power_enabled != 0;
    }

    stopRadio(internals);

    for (state.rgb_settings, 0..) |*values, i| {
        if (device_info.rgb_settings) |rgb_settings| {
            @memcpy(values, &rgb_settings[i]);
        } else {
            // fallback to all zero
            @memset(values, 0);
        }
    }

    for (state.led_settings, 0..) |*value, i| {
        if (device_info.led_settings) |led_settings| {
            value.* = led_settings[i];
        } else {
            // fallback to zero
            value.* = 0;
        }
    }

    for (state.streams) |*stream| {
        stream.enabled = false;
        stream.warm_up = false;
    }

    if (run_callback) {
        if (internals.callbacks.flush_device) |flush_device| {
            flush_device(internals.callbacks.closure);
        }
    }
}

fn stopRadio(internals: *DeviceInternals) void {
    // call with the mutex held

    switch (internals.state.radio_state) {
        .stopped => {},
        .scanning => {
            internals.state.radio_state = .stopped;
            if (internals.callbacks.stop_radio_scan) |stop_radio_scan| {
                stop_radio_scan(internals.callbacks.closure);
            }
        },
        .connecting, .connected => {
            internals.state.radio_state = .stopped;
            if (internals.callbacks.disconnect_radio) |disconnect_radio| {
                disconnect_radio(internals.callbacks.closure);
            }
        },
    }
}

fn getProtocolType(device_info: *const c.AsphodelDeviceInfo_t) c_int {
    var result: c_int = 0;

    if (device_info.supports_rf_power != 0) {
        result |= c.ASPHODEL_PROTOCOL_TYPE_RF_POWER;
    }

    if (device_info.supports_radio != 0) {
        result |= c.ASPHODEL_PROTOCOL_TYPE_RADIO;
    }

    if (device_info.supports_remote != 0) {
        result |= c.ASPHODEL_PROTOCOL_TYPE_REMOTE;
    }

    if (device_info.supports_bootloader != 0) {
        result |= c.ASPHODEL_PROTOCOL_TYPE_BOOTLOADER;
    }

    return result;
}

fn openDevice(device: ?*c.AsphodelDevice_t) callconv(.c) c_int {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device == &context.main_device) {
        if (!context.main_open) {
            context.main_open = true;
            if (context.main_internals.callbacks.open_device) |open_device| {
                open_device(context.main_internals.callbacks.closure);
            }
        }
    } else {
        if (!context.remote_open) {
            context.remote_open = true;

            if (context.remote_internals) |internals| {
                if (internals.callbacks.open_device) |open_device| {
                    open_device(internals.callbacks.closure);
                }
            }
        }
    }

    return c.ASPHODEL_SUCCESS;
}

fn closeDevice(device: ?*c.AsphodelDevice_t) callconv(.c) void {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const maybe_streaming_state: ?*StreamingState = blk: {
        if (device == &context.main_device) {
            if (context.main_open) {
                context.main_open = false;
                if (context.main_internals.callbacks.close_device) |close_device| {
                    close_device(context.main_internals.callbacks.closure);
                }

                break :blk &context.main_streaming_state;
            }
        } else {
            if (context.remote_open) {
                context.remote_open = false;

                if (context.remote_internals) |internals| {
                    if (internals.callbacks.close_device) |close_device| {
                        close_device(internals.callbacks.closure);
                    }
                }

                break :blk &context.remote_streaming_state;
            }
        }
        break :blk null;
    };

    if (maybe_streaming_state) |streaming_state| {
        streaming_state.packet_length = 0;
        streaming_state.streaming_callback = null;
        streaming_state.streaming_closure = null;
        streaming_state.streaming_packet_count = 0;
        streaming_state.streaming_timeout_ns = 0;
    }
}

fn freeDevice(device: ?*c.AsphodelDevice_t) callconv(.c) void {
    if (device) |d| {
        const context: *Context = @ptrCast(@alignCast(d.implementation_info));

        {
            context.mutex.lock();
            defer context.mutex.unlock();

            context.ref_count -= 1;
            if (context.ref_count != 0) {
                return;
            }
        }

        if (context.remote_internals) |remote_internals| {
            remote_internals.arena.deinit();
            std.heap.c_allocator.destroy(remote_internals);
        }
        context.main_internals.arena.deinit();
        std.heap.c_allocator.destroy(context);
    }
}

fn getSerialNumber(device: ?*c.AsphodelDevice_t, buffer: ?[*]u8, buffer_size: usize) callconv(.c) c_int {
    if (buffer == null or buffer_size == 0) {
        return c.ASPHODEL_BAD_PARAMETER;
    }

    if (buffer_size == 1) {
        buffer.?[0] = 0; // null terminate
        return c.ASPHODEL_SUCCESS; // nothing more we can do
    }

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const dest = buffer.?[0 .. buffer_size - 1];
    var writer = std.Io.Writer.fixed(dest);

    if (device == &context.main_device) {
        if (context.main_internals.device_info.serial_number) |serial_number| {
            writer.writeAll(std.mem.span(serial_number)) catch {}; // ignore too long
        } else {
            writer.writeAll("VIRT1") catch {}; // ignore too long
        }
    } else {
        // see if the remote device is connected and has a serial number
        if (context.remote_internals) |internals| {
            if (internals.device_info.serial_number) |serial_number| {
                writer.writeAll(std.mem.span(serial_number)) catch {}; // ignore too long
            }
        } else {
            // see if the main device (radio) is connected
            switch (context.main_internals.state.radio_state) {
                .connected => |connected| {
                    const serial_number = connected[0];
                    writer.print("WM{d}", .{serial_number}) catch {}; // ignore too long
                },
                else => {
                    // return empty string
                },
            }
        }
    }

    buffer.?[writer.end] = 0; // null terminate

    return c.ASPHODEL_SUCCESS;
}

fn doTransfer(device: ?*c.AsphodelDevice_t, command: u8, params: ?[*]const u8, param_length: usize, callback: c.AsphodelTransferCallback_t, closure: ?*anyopaque) callconv(.c) c_int {
    return doTransferInternal(device, command, params, param_length, callback, closure, false);
}

fn doTransferReset(device: ?*c.AsphodelDevice_t, command: u8, params: ?[*]const u8, param_length: usize, callback: c.AsphodelTransferCallback_t, closure: ?*anyopaque) callconv(.c) c_int {
    return doTransferInternal(device, command, params, param_length, callback, closure, true);
}

fn doTransferInternal(device: ?*c.AsphodelDevice_t, command: u8, params: ?[*]const u8, param_length: usize, callback: c.AsphodelTransferCallback_t, closure: ?*anyopaque, suppress_error: bool) c_int {
    const b: []const u8 = blk: {
        if (params) |p| {
            if (param_length > 0) {
                break :blk p[0..param_length];
            } else {
                break :blk "";
            }
        } else {
            break :blk "";
        }
    };

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock(); // because the return value is a pointer into the reply buffer we need to keep the lock until it's copied for the callback

    const internals: *DeviceInternals = blk: {
        if (device == context.remote_device) {
            if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;

            var reply_buffer: [7]u8 = undefined;
            const reply = handleRemoteCommand(context, command, &reply_buffer) catch {
                // not a remote specific command
                if (context.remote_internals) |internals| {
                    // handle normally
                    break :blk internals;
                } else {
                    // no remote device available, handle the error and return early
                    if (callback) |cb| {
                        if (!suppress_error) {
                            cb(c.ERROR_CODE_BAD_STATE, null, 0, closure);
                        } else {
                            cb(c.ASPHODEL_SUCCESS, null, 0, closure);
                        }
                    }
                    return c.ASPHODEL_SUCCESS;
                }
            };

            // handle the reply and return early
            if (callback) |cb| {
                if (reply.len > 0) {
                    // no need to copy as we can hold the whole thing on the stack during the callback
                    cb(c.ASPHODEL_SUCCESS, reply.ptr, reply.len, closure);
                } else {
                    cb(c.ASPHODEL_SUCCESS, null, 0, closure);
                }
            }
            return c.ASPHODEL_SUCCESS;
        } else {
            if (!context.main_open) return c.ASPHODEL_DEVICE_CLOSED;
            break :blk &context.main_internals;
        }
    };

    if (internals.remaining_transfers == 0) {
        if (callback) |cb| {
            if (!suppress_error) {
                cb(c.ASPHODEL_TRANSPORT_ERROR, null, 0, closure);
            } else {
                cb(c.ASPHODEL_SUCCESS, null, 0, closure);
            }
        }
        return c.ASPHODEL_SUCCESS; // this is the return value for the do_transfer() call, not the callback
    } else {
        internals.remaining_transfers -= 1;
    }

    const response = handleCommand(internals, command, b);
    switch (response) {
        .reply => |reply| {
            if (callback) |cb| {
                if (reply.len > 0) {
                    // use the c allocator to copy the reply because the callback may recursively call into do_transfer()
                    const reply_copy = std.heap.c_allocator.dupe(u8, reply) catch return c.ASPHODEL_NO_MEM;
                    defer std.heap.c_allocator.free(reply_copy);
                    cb(c.ASPHODEL_SUCCESS, reply_copy.ptr, reply_copy.len, closure);
                } else {
                    cb(c.ASPHODEL_SUCCESS, null, 0, closure);
                }
            }
        },
        .status => |status| {
            if (callback) |cb| {
                if (!suppress_error) {
                    cb(status, null, 0, closure);
                } else {
                    cb(c.ASPHODEL_SUCCESS, null, 0, closure);
                }
            }
        },
    }

    return c.ASPHODEL_SUCCESS;
}

fn startStreamingPackets(device: ?*c.AsphodelDevice_t, packet_count: c_int, transfer_count: c_int, timeout: c_uint, callback: c.AsphodelStreamingCallback_t, closure: ?*anyopaque) callconv(.c) c_int {
    if (packet_count == 0 or timeout == 0) return c.ASPHODEL_BAD_PARAMETER;

    _ = transfer_count; // this is ignored; it's part of the API useful for USB devices, but irrelevant for virtual devices

    const packet_length = getStreamPacketLength(device);
    if (packet_length == 0) return c.ASPHODEL_BAD_PARAMETER; // shouldn't happen

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const streaming_state: *StreamingState = blk: {
        if (device == context.remote_device) {
            if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;
            break :blk &context.remote_streaming_state;
        } else {
            if (!context.main_open) return c.ASPHODEL_DEVICE_CLOSED;
            break :blk &context.main_streaming_state;
        }
    };

    streaming_state.packet_length = packet_length;
    streaming_state.streaming_callback = callback;
    streaming_state.streaming_closure = closure;
    streaming_state.streaming_packet_count = std.math.cast(usize, packet_count) orelse return c.ASPHODEL_BAD_PARAMETER;
    streaming_state.streaming_timeout_ns = std.time.ns_per_ms * (std.math.cast(u64, timeout) orelse return c.ASPHODEL_BAD_PARAMETER);

    streaming_state.streaming_timer.reset();

    return c.ASPHODEL_SUCCESS;
}

fn stopStreamingPackets(device: ?*c.AsphodelDevice_t) callconv(.c) void {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    const streaming_state: *StreamingState = blk: {
        if (device == context.remote_device) {
            break :blk &context.remote_streaming_state;
        } else {
            break :blk &context.main_streaming_state;
        }
    };

    streaming_state.packet_length = 0;
    streaming_state.streaming_callback = null;
    streaming_state.streaming_closure = null;
    streaming_state.streaming_packet_count = 0;
    streaming_state.streaming_timeout_ns = 0;
}

const StreamPacketsBlockingData = struct {
    buffer: [*]u8,
    remaining: usize,
    index: usize,
    status: c_int,
    finished: std.Thread.ResetEvent,
};

fn getStreamPacketsBlocking(device: ?*c.AsphodelDevice_t, buffer: ?[*]u8, count: ?*c_int, timeout: c_uint) callconv(.c) c_int {
    if (buffer == null or count == null) {
        return c.ASPHODEL_BAD_PARAMETER;
    }

    const original_count: usize = std.math.cast(usize, count.?.*) orelse return c.ASPHODEL_BAD_PARAMETER;
    const packet_length = getStreamPacketLength(device);
    const packet_count = std.math.divExact(usize, original_count, packet_length) catch return c.ASPHODEL_BAD_PARAMETER;
    const timeout_ns = std.time.ns_per_ms * (std.math.cast(u64, timeout) orelse return c.ASPHODEL_BAD_PARAMETER);

    var data = StreamPacketsBlockingData{
        .buffer = buffer.?,
        .remaining = original_count,
        .index = 0,
        .status = c.ASPHODEL_SUCCESS,
        .finished = std.Thread.ResetEvent{},
    };

    const result = startStreamingPackets(device, @intCast(packet_count), 1, timeout, streamPacketsBlockingCb, &data);
    if (result != c.ASPHODEL_SUCCESS) {
        return result;
    }

    const wait_result = data.finished.timedWait(timeout_ns);

    stopStreamingPackets(device);

    if (wait_result == error.Timeout) {
        // ignore the timeout: the logic is the same either way
    }

    var status = data.status;
    if (status == c.ASPHODEL_SUCCESS) {
        if (data.index == 0) {
            status = c.ASPHODEL_TIMEOUT;
        }
    }

    count.?.* = @intCast(data.index); // will fit inside an int, since the original count was an int

    return status;
}

fn streamPacketsBlockingCb(status: c_int, stream_data: ?[*]const u8, packet_size: usize, packet_count: usize, closure: ?*anyopaque) callconv(.c) void {
    var data: *StreamPacketsBlockingData = @ptrCast(@alignCast(closure));

    if (status != c.ASPHODEL_SUCCESS) {
        // wake up now
        data.status = status;
        data.finished.set();
    } else {
        // copy the data
        const copy_size = @min(packet_size * packet_count, data.remaining);
        if (copy_size > 0) {
            @memcpy(data.buffer[data.index .. data.index + copy_size], stream_data.?[0..copy_size]);
            data.index += copy_size;
            data.remaining -= copy_size;
        }

        if (data.remaining == 0) {
            // wake up now
            data.finished.set();
        }
    }
}

fn getMaxIncomingParamLength(device: ?*c.AsphodelDevice_t) callconv(.c) usize {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device == context.remote_device) {
        if (context.remote_internals) |remote_internals| {
            // connected remote device
            return remote_internals.device_info.max_incoming_param_length;
        } else {
            // disconnected remote device
            const val = context.main_internals.device_info.remote_max_incoming_param_length;
            if (val != 0) {
                return val;
            } else {
                return REMOTE_MAX_INCOMING_PARAM_LENGTH_FALLBACK;
            }
        }
    } else {
        // main device
        return context.main_internals.device_info.max_incoming_param_length;
    }
}

fn getMaxOutgoingParamLength(device: ?*c.AsphodelDevice_t) callconv(.c) usize {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device == context.remote_device) {
        if (context.remote_internals) |remote_internals| {
            // connected remote device
            return remote_internals.device_info.max_outgoing_param_length;
        } else {
            // disconnected remote device
            const val = context.main_internals.device_info.remote_max_outgoing_param_length;
            if (val != 0) {
                return val;
            } else {
                return REMOTE_MAX_OUTGOING_PARAM_LENGTH_FALLBACK;
            }
        }
    } else {
        // main device
        return context.main_internals.device_info.max_outgoing_param_length;
    }
}

fn getStreamPacketLength(device: ?*c.AsphodelDevice_t) callconv(.c) usize {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device == context.remote_device) {
        if (context.remote_internals) |remote_internals| {
            // connected remote device
            return remote_internals.device_info.stream_packet_length;
        } else {
            // disconnected remote device
            const val = context.main_internals.device_info.remote_stream_packet_length;
            if (val != 0) {
                return val;
            } else {
                return REMOTE_STREAM_PACKET_LENGTH_FALLBACK;
            }
        }
    } else {
        // main device
        return context.main_internals.device_info.stream_packet_length;
    }
}

fn pollDevice(device: ?*c.AsphodelDevice_t, milliseconds: c_int, completed: ?*c_int) callconv(.c) c_int {
    const max_sleep_ns: u64 = std.time.ns_per_ms * (std.math.cast(u64, milliseconds) orelse return c.ASPHODEL_BAD_PARAMETER);

    if (completed) |comp| {
        if (comp.* != 0) {
            return c.ASPHODEL_SUCCESS;
        }
    }

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    var sleep_ns: u64 = undefined;
    {
        context.mutex.lock();
        defer context.mutex.unlock();

        const main_timeout = handleStreamingTimeouts(&context.main_streaming_state) orelse max_sleep_ns;
        const remote_timeout = handleStreamingTimeouts(&context.remote_streaming_state) orelse max_sleep_ns;

        sleep_ns = @min(@min(main_timeout, remote_timeout), max_sleep_ns);
    }

    if (sleep_ns == 0) {
        return c.ASPHODEL_SUCCESS;
    }

    // do the wait
    std.Thread.sleep(sleep_ns);

    {
        context.mutex.lock();
        defer context.mutex.unlock();

        _ = handleStreamingTimeouts(&context.main_streaming_state);
        _ = handleStreamingTimeouts(&context.remote_streaming_state);
    }

    return c.ASPHODEL_SUCCESS;
}

fn handleStreamingTimeouts(streaming_state: *StreamingState) ?u64 {
    // call this with the mutex locked

    if (streaming_state.streaming_callback != null and streaming_state.streaming_timeout_ns != 0) {
        const elapsed = streaming_state.streaming_timer.read();
        if (elapsed >= streaming_state.streaming_timeout_ns) {
            // timed out: let the callback know
            streaming_state.streaming_timer.reset(); // reset so we don't timeout again next poll
            streaming_state.streaming_callback.?(c.ASPHODEL_TIMEOUT, null, streaming_state.packet_length, 0, streaming_state.streaming_closure);

            return 0; // don't wait
        } else {
            return streaming_state.streaming_timeout_ns - elapsed;
        }
    } else {
        return null; // maximum wait time
    }
}

fn setConnectCallback(device: ?*c.AsphodelDevice_t, callback: c.AsphodelConnectCallback_t, closure: ?*anyopaque) callconv(.c) c_int {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device == &context.main_device) {
        // the main device is always connected
        if (callback) |cb| {
            cb(c.ASPHODEL_SUCCESS, 1, closure);
        }
    } else {
        // NOTE: the passed callback may be null to unregister the existing callback.
        context.remote_connect_callback = callback;
        context.remote_connect_closure = closure;

        if (callback) |cb| {
            if (context.remote_internals != null) {
                // the remote device is already connected
                cb(c.ASPHODEL_SUCCESS, 1, closure);
            }
        }
    }

    return c.ASPHODEL_SUCCESS;
}

const WaitForConnectData = struct {
    status: c_int,
    finished: std.Thread.ResetEvent,
};

fn waitForConnect(device: ?*c.AsphodelDevice_t, timeout: c_uint) callconv(.c) c_int {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));
    const timeout_ns = std.time.ns_per_ms * (std.math.cast(u64, timeout) orelse return c.ASPHODEL_BAD_PARAMETER);

    if (device == &context.main_device) {
        // the main device is always connected
        return c.ASPHODEL_SUCCESS;
    } else {
        var data: WaitForConnectData = .{
            .status = c.ASPHODEL_TIMEOUT,
            .finished = std.Thread.ResetEvent{},
        };

        const ret = setConnectCallback(device, waitForConnectCb, &data);
        if (ret != c.ASPHODEL_SUCCESS) {
            return ret;
        }

        const wait_result = data.finished.timedWait(timeout_ns);
        if (wait_result == error.Timeout) {
            // ignore the timeout: the logic is the same either way
        }

        return data.status;
    }
}

fn waitForConnectCb(status: c_int, connected: c_int, closure: ?*anyopaque) callconv(.c) void {
    var data: *WaitForConnectData = @ptrCast(@alignCast(closure));

    if (status != c.ASPHODEL_SUCCESS or connected != 0) {
        // if we get an error or a connect, we're done
        data.status = status;
        data.finished.set();
    }
}

fn getRemoteDevice(device: ?*c.AsphodelDevice_t, remote_device: ?*?*c.AsphodelDevice_t) callconv(.c) c_int {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (device != &context.main_device) {
        // not the main device
        return c.ASPHODEL_NOT_SUPPORTED;
    }

    if (context.remote_device) |remote| {
        if (remote_device) |remote_out| {
            context.ref_count += 1;

            remote_out.* = remote;
            return c.ASPHODEL_SUCCESS;
        } else {
            return c.ASPHODEL_BAD_PARAMETER;
        }
    } else {
        // not a radio
        return c.ASPHODEL_NOT_SUPPORTED;
    }
}

fn getRemoteLengths(device: ?*c.AsphodelDevice_t, max_incoming_param_length_out: ?*usize, max_outgoing_param_length_out: ?*usize, stream_packet_length_out: ?*usize) callconv(.c) c_int {
    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    var max_incoming_param_length: usize = undefined;
    var max_outgoing_param_length: usize = undefined;
    var stream_packet_length: usize = undefined;

    if (device == context.remote_device) {
        if (context.remote_internals) |remote_internals| {
            // connected remote device
            max_incoming_param_length = remote_internals.device_info.max_incoming_param_length;
            max_outgoing_param_length = remote_internals.device_info.max_outgoing_param_length;
            stream_packet_length = remote_internals.device_info.stream_packet_length;
        } else {
            // disconnected remote device

            max_incoming_param_length = context.main_internals.device_info.remote_max_incoming_param_length;
            if (max_incoming_param_length == 0) {
                max_incoming_param_length = REMOTE_MAX_INCOMING_PARAM_LENGTH_FALLBACK;
            }

            max_outgoing_param_length = context.main_internals.device_info.remote_max_outgoing_param_length;
            if (max_outgoing_param_length == 0) {
                max_outgoing_param_length = REMOTE_MAX_OUTGOING_PARAM_LENGTH_FALLBACK;
            }

            stream_packet_length = context.main_internals.device_info.remote_stream_packet_length;
            if (stream_packet_length == 0) {
                stream_packet_length = REMOTE_STREAM_PACKET_LENGTH_FALLBACK;
            }
        }
    } else {
        // main device
        max_incoming_param_length = context.main_internals.device_info.max_incoming_param_length;
        max_outgoing_param_length = context.main_internals.device_info.max_outgoing_param_length;
        stream_packet_length = context.main_internals.device_info.stream_packet_length;
    }

    if (max_incoming_param_length_out) |out| {
        out.* = max_incoming_param_length;
    }

    if (max_outgoing_param_length_out) |out| {
        out.* = max_outgoing_param_length;
    }

    if (stream_packet_length_out) |out| {
        out.* = stream_packet_length;
    }

    return c.ASPHODEL_SUCCESS;
}

fn reconnectMainDevice(device: ?*c.AsphodelDevice_t, reconnected_device: ?*?*c.AsphodelDevice_t) callconv(.c) c_int {
    if (device == null or reconnected_device == null) return c.ASPHODEL_BAD_PARAMETER;

    reconnected_device.?.* = device;

    return c.ASPHODEL_SUCCESS;
}

fn reconnectRemoteDevice(device: ?*c.AsphodelDevice_t, reconnected_device: ?*?*c.AsphodelDevice_t) callconv(.c) c_int {
    if (device == null or reconnected_device == null) return c.ASPHODEL_BAD_PARAMETER;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;

    if (context.main_internals.callbacks.restart_remote) |restart_remote| {
        restart_remote(c.CMD_RESTART_REMOTE, context.main_internals.callbacks.closure);
    }

    reconnected_device.?.* = device;
    return c.ASPHODEL_SUCCESS;
}

fn reconnectRemoteDeviceBoot(device: ?*c.AsphodelDevice_t, reconnected_device: ?*?*c.AsphodelDevice_t) callconv(.c) c_int {
    if (device == null or reconnected_device == null) return c.ASPHODEL_BAD_PARAMETER;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;

    if (context.main_internals.callbacks.restart_remote) |restart_remote| {
        restart_remote(c.CMD_RESTART_REMOTE_BOOT, context.main_internals.callbacks.closure);
    }

    reconnected_device.?.* = device;

    return c.ASPHODEL_SUCCESS;
}

fn reconnectRemoteDeviceApp(device: ?*c.AsphodelDevice_t, reconnected_device: ?*?*c.AsphodelDevice_t) callconv(.c) c_int {
    if (device == null or reconnected_device == null) return c.ASPHODEL_BAD_PARAMETER;

    const context: *Context = @ptrCast(@alignCast(device.?.implementation_info));

    context.mutex.lock();
    defer context.mutex.unlock();

    if (!context.remote_open) return c.ASPHODEL_DEVICE_CLOSED;

    if (context.main_internals.callbacks.restart_remote) |restart_remote| {
        restart_remote(c.CMD_RESTART_REMOTE_APP, context.main_internals.callbacks.closure);
    }

    reconnected_device.?.* = device;

    return c.ASPHODEL_SUCCESS;
}

const AsphodelError = error{
    OutOfMemory,
    Unspecified,
    MalformedCommand,
    UnimplementedCommand,
    BadCmdLength,
    BadAddress,
    BadIndex,
    InvalidData,
    Unsupported,
    BadState,
    I2cError,
    Incomplete,
};

fn errorToValue(err: AsphodelError) c_int {
    return switch (err) {
        error.OutOfMemory => c.ASPHODEL_NO_MEM,
        error.Unspecified => c.ERROR_CODE_UNSPECIFIED,
        error.MalformedCommand => c.ERROR_CODE_MALFORMED_COMMAND,
        error.UnimplementedCommand => c.ERROR_CODE_UNIMPLEMENTED_COMMAND,
        error.BadCmdLength => c.ERROR_CODE_BAD_CMD_LENGTH,
        error.BadAddress => c.ERROR_CODE_BAD_ADDRESS,
        error.BadIndex => c.ERROR_CODE_BAD_INDEX,
        error.InvalidData => c.ERROR_CODE_INVALID_DATA,
        error.Unsupported => c.ERROR_CODE_UNSUPPORTED,
        error.BadState => c.ERROR_CODE_BAD_STATE,
        error.I2cError => c.ERROR_CODE_I2C_ERROR,
        error.Incomplete => c.ERROR_CODE_INCOMPLETE,
    };
}

const CommandResponse = union(enum) {
    reply: []const u8,
    status: c_int,
};

fn handleCommand(internals: *DeviceInternals, command: u8, params: []const u8) CommandResponse {
    // NOTE: this function is called with the mutex locked

    // need to handle the echo commands at this level, because they're used to generate errors for testing
    switch (command) {
        c.CMD_ECHO_RAW => {
            if (params.len == 0) {
                return .{ .status = c.ASPHODEL_TIMEOUT };
            } else {
                return .{ .status = c.ASPHODEL_MISMATCHED_TRANSACTION };
            }
        },
        c.CMD_ECHO_TRANSACTION => {
            if (params.len == 0) {
                return .{ .status = c.ASPHODEL_MALFORMED_REPLY };
            } else if (params[0] == c.CMD_REPLY_ERROR) {
                // echo trying to create an error response
                if (params.len < 2) {
                    return .{ .status = c.ASPHODEL_MALFORMED_ERROR };
                } else if (params[1] == 0x00) {
                    return .{ .status = c.ERROR_CODE_UNSPECIFIED };
                } else {
                    return .{ .status = params[1] };
                }
            } else if (params[0] == c.CMD_ECHO_TRANSACTION) {
                // handle as an echo
                return .{ .reply = params[1..] };
            } else {
                return .{ .status = c.ASPHODEL_MISMATCHED_COMMAND };
            }
        },
        c.CMD_ECHO_PARAMS => return .{ .reply = params },
        c.CMD_REPLY_ERROR => return .{ .reply = &[2]u8{
            c.ERROR_CODE_UNIMPLEMENTED_COMMAND,
            c.CMD_REPLY_ERROR,
        } },
        else => {
            const response = handleCommandInner(internals, command, params);
            if (response) |reply| {
                return .{ .reply = reply };
            } else |err| {
                return .{ .status = errorToValue(err) };
            }
        },
    }
}

fn handleCommandInner(internals: *DeviceInternals, command: u8, params: []const u8) AsphodelError![]const u8 {
    // NOTE: this function is called with the mutex locked

    const device_info = internals.device_info;
    var reader = std.Io.Reader.fixed(params);
    var writer = std.Io.Writer.fixed(internals.reply_buffer);

    switch (command) {
        c.CMD_GET_PROTOCOL_VERSION => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.protocol_version) |protocol_version| {
                const maybe_protocol_version = parseProtocolVersion(std.mem.span(protocol_version));
                if (maybe_protocol_version) |p| {
                    @memcpy(internals.reply_buffer[0..2], &p);
                    return internals.reply_buffer[0..2];
                }
            }

            // couldn't use the one from the device info: use the library version as a fallback
            return &[2]u8{ c.ASPHODEL_PROTOCOL_VERSION_MAJOR, (c.ASPHODEL_PROTOCOL_VERSION_MINOR << 4) | c.ASPHODEL_PROTOCOL_VERSION_SUBMINOR };
        },
        c.CMD_GET_BOARD_INFO => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            writer.writeByte(device_info.board_info_rev) catch unreachable;
            try handleString(&writer, device_info.board_info_name, "Virtual");
        },
        c.CMD_GET_USER_TAG_LOCATIONS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            for (device_info.tag_locations) |loc| {
                const word_loc: u16 = std.math.cast(u16, @divFloor(loc, 4)) orelse return error.InvalidData;
                writer.writeInt(u16, word_loc, .big) catch unreachable;
            }
        },
        c.CMD_GET_BUILD_INFO => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            try handleString(&writer, device_info.build_info, version.BUILD_INFO_STR);
        },
        c.CMD_GET_BUILD_DATE => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            try handleString(&writer, device_info.build_date, version.BUILD_DATE_STR);
        },
        c.CMD_GET_CHIP_FAMILY => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            try handleString(&writer, device_info.chip_family, "Virtual");
        },
        c.CMD_GET_CHIP_MODEL => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            try handleString(&writer, device_info.chip_model, "Virtual");
        },
        c.CMD_GET_CHIP_ID => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.chip_id) |chip_id| {
                return std.fmt.hexToBytes(internals.reply_buffer, std.mem.span(chip_id)) catch error.InvalidData;
            } else {
                return &[1]u8{1}; // fallback value
            }
        },
        c.CMD_GET_NVM_SIZE => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const nvm_size = internals.state.nvm.len / 4;
            writer.writeInt(u16, std.math.lossyCast(u16, nvm_size), .big) catch unreachable;
        },
        c.CMD_ERASE_NVM => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            internals.state.nvm_modified = true;
            @memset(internals.state.nvm, 0xFF);
        },
        c.CMD_WRITE_NVM => {
            const address = reader.takeInt(u16, .big) catch return error.BadCmdLength;
            const byte_count: usize = reader.bufferedLen();
            if (byte_count == 0 or byte_count % 4 != 0) return error.BadCmdLength;
            const byte_address = @as(usize, address) * 4;
            if (byte_address + byte_count > internals.state.nvm.len) return error.BadAddress;
            internals.state.nvm_modified = true;
            reader.readSliceAll(internals.state.nvm[byte_address .. byte_address + byte_count]) catch unreachable;
        },
        c.CMD_READ_NVM => {
            const word_address = reader.takeInt(u16, .big) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const byte_address = @as(usize, word_address) * 4;
            if (byte_address >= internals.state.nvm.len) return error.BadAddress;
            const remaining_bytes = internals.state.nvm.len - byte_address;
            const read_bytes = @min(device_info.max_outgoing_param_length & ~@as(usize, 0x03), remaining_bytes);
            writer.writeAll(internals.state.nvm[byte_address .. byte_address + read_bytes]) catch unreachable;
        },
        c.CMD_FLUSH => {
            // NOTE: this is also handled by handleRemoteCommand()
            flushState(internals, true);
        },
        c.CMD_RESET => {
            internals.state.reset_flag = true;
            flushState(internals, true);
        },
        c.CMD_GET_BOOTLOADER_INFO => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            try handleString(&writer, device_info.bootloader_info, "");
        },
        c.CMD_BOOTLOADER_JUMP => {
            internals.state.reset_flag = true;
            flushState(internals, true);
        },
        c.CMD_GET_RGB_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const count: u8 = std.math.lossyCast(u8, internals.state.rgb_settings.len);
            writer.writeByte(count) catch unreachable;
        },
        c.CMD_GET_RGB_VALUES => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.rgb_settings.len) {
                const values = internals.state.rgb_settings[index];
                writer.writeAll(&values) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_RGB => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const values: *[3]u8 = reader.takeArray(3) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.rgb_settings.len) {
                @memcpy(&internals.state.rgb_settings[index], values);
                if (internals.callbacks.set_rgb) |set_rgb| {
                    set_rgb(index, values, 0, internals.callbacks.closure);
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_RGB_INSTANT => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const values: *[3]u8 = reader.takeArray(3) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.rgb_settings.len) {
                @memcpy(&internals.state.rgb_settings[index], values);
                if (internals.callbacks.set_rgb) |set_rgb| {
                    set_rgb(index, values, 1, internals.callbacks.closure);
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_LED_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const count: u8 = std.math.lossyCast(u8, internals.state.led_settings.len);
            writer.writeByte(count) catch unreachable;
        },
        c.CMD_GET_LED_VALUE => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.led_settings.len) {
                const value: u8 = internals.state.led_settings[index];
                writer.writeByte(value) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_LED => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const value = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.led_settings.len) {
                internals.state.led_settings[index] = value;
                if (internals.callbacks.set_led) |set_led| {
                    set_led(index, value, 0, internals.callbacks.closure);
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_LED_INSTANT => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const value = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.led_settings.len) {
                internals.state.led_settings[index] = value;
                if (internals.callbacks.set_led) |set_led| {
                    set_led(index, value, 1, internals.callbacks.closure);
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_RESET_FLAG => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const reset_flag: u8 = if (internals.state.reset_flag) 1 else 0;
            writer.writeByte(reset_flag) catch unreachable;
        },
        c.CMD_CLEAR_RESET_FLAG => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            internals.state.reset_flag = false;
        },
        c.CMD_GET_NVM_MODIFIED => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.nvm_modified != null) {
                // only report it if the device supports the command
                const nvm_modified: u8 = if (internals.state.nvm_modified) 1 else 0;
                writer.writeByte(nvm_modified) catch unreachable;
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_NVM_HASH => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.nvm_hash) |value| {
                return std.fmt.hexToBytes(internals.reply_buffer, std.mem.span(value)) catch error.InvalidData;
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_SETTING_HASH => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_hash) |value| {
                return std.fmt.hexToBytes(internals.reply_buffer, std.mem.span(value)) catch error.InvalidData;
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_COMMIT_ID => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.commit_id) |value| {
                const str: [:0]const u8 = std.mem.span(value);
                if (str.len > 0) {
                    writer.writeAll(str) catch {}; // ignore too long
                } else {
                    // empty string in device info means device doesn't support this command
                    return error.UnimplementedCommand;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_REPO_BRANCH => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.repo_branch) |value| {
                const str: [:0]const u8 = std.mem.span(value);
                if (str.len > 0) {
                    writer.writeAll(str) catch {}; // ignore too long
                } else {
                    // empty string in device info means device doesn't support this command
                    return error.UnimplementedCommand;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_REPO_NAME => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.repo_name) |value| {
                const str: [:0]const u8 = std.mem.span(value);
                if (str.len > 0) {
                    writer.writeAll(str) catch {}; // ignore too long
                } else {
                    // empty string in device info means device doesn't support this command
                    return error.UnimplementedCommand;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_STREAM_COUNT_AND_ID => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.stream_count_known != 0) {
                writer.writeByte(std.math.lossyCast(u8, device_info.stream_count)) catch unreachable;
                writer.writeByte(device_info.stream_filler_bits) catch unreachable;
                writer.writeByte(device_info.stream_id_bits) catch unreachable;
            } else {
                writer.writeAll(&[_]u8{ 0, 0, 0 }) catch unreachable;
            }
        },
        c.CMD_GET_STREAM_CHANNELS => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                const stream = &device_info.streams[index];
                const channels = stream.channel_index_list[0..stream.channel_count];
                writer.writeAll(channels) catch {}; // ignore too long
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_STREAM_FORMAT => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                const stream = &device_info.streams[index];
                writer.writeByte(stream.filler_bits) catch unreachable;
                writer.writeByte(stream.counter_bits) catch unreachable;
                writer.writeInt(u32, @as(u32, @bitCast(stream.rate)), .big) catch unreachable;
                writer.writeInt(u32, @as(u32, @bitCast(stream.rate_error)), .big) catch unreachable;
                writer.writeInt(u32, @as(u32, @bitCast(stream.warm_up_delay)), .big) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_ENABLE_STREAM => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const enable = (reader.takeByte() catch return error.BadCmdLength) != 0;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                const stream_state: *State.StreamState = &internals.state.streams[index];
                if (stream_state.enabled != enable) {
                    stream_state.enabled = enable;
                    if (internals.callbacks.set_stream_state) |set_stream_state| {
                        set_stream_state(index, if (enable) 1 else 0, if (stream_state.warm_up) 1 else 0, internals.callbacks.closure);
                    }
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_WARM_UP_STREAM => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const warm_up = (reader.takeByte() catch return error.BadCmdLength) != 0;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                const stream_state: *State.StreamState = &internals.state.streams[index];
                if (stream_state.warm_up != warm_up) {
                    stream_state.warm_up = warm_up;
                    if (internals.callbacks.set_stream_state) |set_stream_state| {
                        set_stream_state(index, if (stream_state.enabled) 1 else 0, if (warm_up) 1 else 0, internals.callbacks.closure);
                    }
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_STREAM_STATUS => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                const stream_state: *const State.StreamState = &internals.state.streams[index];
                writer.writeByte(if (stream_state.enabled) 1 else 0) catch unreachable;
                writer.writeByte(if (stream_state.warm_up) 1 else 0) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_STREAM_RATE_INFO => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.streams.len) {
                if (device_info.stream_rates) |stream_rates| {
                    const stream_rate = &stream_rates[index];
                    if (stream_rate.available != 0) {
                        writer.writeByte(std.math.lossyCast(u8, stream_rate.channel_index)) catch unreachable;
                        writer.writeByte(if (stream_rate.invert != 0) 1 else 0) catch unreachable;
                        writer.writeInt(u32, @as(u32, @bitCast(stream_rate.scale)), .big) catch unreachable;
                        writer.writeInt(u32, @as(u32, @bitCast(stream_rate.offset)), .big) catch unreachable;
                    }
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CHANNEL_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                const count = std.math.lossyCast(u8, device_info.channel_count);
                writer.writeByte(count) catch unreachable;
            } else {
                return &[1]u8{0}; // zero
            }
        },
        c.CMD_GET_CHANNEL_NAME => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                if (index < device_info.channel_count) {
                    const channel = &device_info.channels[index];
                    writer.writeAll(std.mem.span(channel.name)) catch {}; // ignore too long
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CHANNEL_INFO => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                if (index < device_info.channel_count) {
                    const channel = &device_info.channels[index];
                    writer.writeByte(channel.channel_type) catch unreachable;
                    writer.writeByte(channel.unit_type) catch unreachable;
                    writer.writeInt(u16, channel.filler_bits, .big) catch unreachable;
                    writer.writeInt(u16, channel.data_bits, .big) catch unreachable;
                    writer.writeByte(channel.samples) catch unreachable;
                    writer.writeInt(i16, channel.bits_per_sample, .big) catch unreachable;
                    writer.writeInt(u32, @as(u32, @bitCast(channel.minimum)), .big) catch unreachable;
                    writer.writeInt(u32, @as(u32, @bitCast(channel.maximum)), .big) catch unreachable;
                    writer.writeInt(u32, @as(u32, @bitCast(channel.resolution)), .big) catch unreachable;
                    writer.writeByte(channel.chunk_count) catch unreachable;
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CHANNEL_COEFFICIENTS => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const start_index = reader.takeByte() catch 0;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                if (index < device_info.channel_count) {
                    const channel = &device_info.channels[index];
                    if (start_index <= channel.coefficients_length) { // allow equal to send 0 back
                        const coefficient_count = channel.coefficients_length - start_index;
                        const max_transfer_count = std.math.lossyCast(u8, device_info.max_outgoing_param_length / 4);
                        const transfer_count = @min(coefficient_count, max_transfer_count);

                        for (channel.coefficients[start_index .. start_index + transfer_count]) |coefficient| {
                            writer.writeInt(u32, @as(u32, @bitCast(coefficient)), .big) catch unreachable;
                        }
                    } else {
                        return error.BadIndex;
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CHANNEL_CHUNK => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const chunk_number = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                if (index < device_info.channel_count) {
                    const channel = &device_info.channels[index];
                    if (chunk_number < channel.chunk_count) {
                        const chunk_length = channel.chunk_lengths[chunk_number];
                        if (chunk_length > 0) {
                            writer.writeAll(channel.chunks[chunk_number][0..chunk_length]) catch {}; // ignore too long
                        }
                    } else {
                        return error.BadIndex;
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_CHANNEL_SPECIFIC => {
            // There's no good way to handle errors through a callback, and probably no one will ever need this anyway.
            return error.UnimplementedCommand;
        },
        c.CMD_GET_CHANNEL_CALIBRATION => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.channel_count_known != 0) {
                if (index < device_info.channel_count) {
                    if (device_info.channel_calibrations) |channel_calibrations| {
                        const calibration: ?*const c.AsphodelChannelCalibration_t = channel_calibrations[index];
                        if (calibration) |cal| {
                            writer.writeByte(std.math.lossyCast(u8, cal.base_setting_index)) catch unreachable;
                            writer.writeByte(std.math.lossyCast(u8, cal.resolution_setting_index)) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(cal.scale)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(cal.offset)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(cal.minimum)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(cal.maximum)), .big) catch unreachable;
                        }
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SUPPLY_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supply_count_known != 0) {
                const count = std.math.lossyCast(u8, device_info.supply_count);
                writer.writeByte(count) catch unreachable;
            } else {
                return &[1]u8{0}; // zero
            }
        },
        c.CMD_GET_SUPPLY_NAME => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supply_count_known != 0) {
                if (index < device_info.supply_count) {
                    const supply = &device_info.supplies[index];
                    writer.writeAll(std.mem.span(supply.name)) catch {}; // ignore too long
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SUPPLY_INFO => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supply_count_known != 0) {
                if (index < device_info.supply_count) {
                    const supply = &device_info.supplies[index];
                    writer.writeByte(supply.unit_type) catch unreachable;
                    writer.writeByte(supply.is_battery) catch unreachable;
                    writer.writeInt(i32, supply.nominal, .big) catch unreachable;
                    writer.writeInt(u32, @as(u32, @bitCast(supply.scale)), .big) catch unreachable;
                    writer.writeInt(u32, @as(u32, @bitCast(supply.offset)), .big) catch unreachable;
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_CHECK_SUPPLY => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supply_count_known != 0) {
                if (index < device_info.supply_count) {
                    if (device_info.supply_results) |supply_results| {
                        const result = &supply_results[index];
                        if (result.error_code == c.ASPHODEL_SUCCESS) {
                            writer.writeInt(i32, result.measurement, .big) catch unreachable;
                            writer.writeByte(result.result) catch unreachable;
                        } else {
                            return error.InvalidData;
                        }
                    } else {
                        // fallback
                        const supply = &device_info.supplies[index];
                        writer.writeInt(i32, supply.nominal, .big) catch unreachable;
                        writer.writeByte(0) catch unreachable;
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CTRL_VAR_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            const count: u8 = std.math.lossyCast(u8, internals.state.ctrl_vars.len);
            writer.writeByte(count) catch unreachable;
        },
        c.CMD_GET_CTRL_VAR_NAME => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.ctrl_vars.len) {
                const ctrl_var = &device_info.ctrl_vars[index];
                writer.writeAll(std.mem.span(ctrl_var.name)) catch {}; // ignore too long
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CTRL_VAR_INFO => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.ctrl_vars.len) {
                const ctrl_var = &device_info.ctrl_vars[index];
                writer.writeByte(ctrl_var.unit_type) catch unreachable;
                writer.writeInt(i32, ctrl_var.minimum, .big) catch unreachable;
                writer.writeInt(i32, ctrl_var.maximum, .big) catch unreachable;
                writer.writeInt(u32, @as(u32, @bitCast(ctrl_var.scale)), .big) catch unreachable;
                writer.writeInt(u32, @as(u32, @bitCast(ctrl_var.offset)), .big) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CTRL_VAR => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.ctrl_vars.len) {
                const value: i32 = internals.state.ctrl_vars[index];
                writer.writeInt(i32, value, .big) catch unreachable;
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_CTRL_VAR => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            const value = reader.takeInt(i32, .big) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (index < internals.state.ctrl_vars.len) {
                internals.state.ctrl_vars[index] = value;
                if (internals.callbacks.set_ctrl_var) |set_ctrl_var| {
                    set_ctrl_var(index, value, internals.callbacks.closure);
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SETTING_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_count_known != 0) {
                const count = std.math.lossyCast(u8, device_info.setting_count);
                writer.writeByte(count) catch unreachable;
            } else {
                return &[1]u8{0}; // zero
            }
        },
        c.CMD_GET_SETTING_NAME => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_count_known != 0) {
                if (index < device_info.setting_count) {
                    const setting = &device_info.settings[index];
                    writer.writeAll(std.mem.span(setting.name)) catch {}; // ignore too long
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SETTING_INFO => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_count_known != 0) {
                if (index < device_info.setting_count) {
                    const setting = &device_info.settings[index];
                    writer.writeByte(setting.setting_type) catch unreachable;
                    switch (setting.setting_type) {
                        c.SETTING_TYPE_BYTE, c.SETTING_TYPE_BOOLEAN, c.SETTING_TYPE_UNIT_TYPE, c.SETTING_TYPE_CHANNEL_TYPE => {
                            writer.writeInt(u16, setting.u.byte_setting.nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.byte_setting.nvm_word_byte) catch unreachable;
                        },
                        c.SETTING_TYPE_BYTE_ARRAY => {
                            writer.writeInt(u16, setting.u.byte_array_setting.nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.byte_array_setting.maximum_length) catch unreachable;
                            writer.writeInt(u16, setting.u.byte_array_setting.length_nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.byte_array_setting.length_nvm_word_byte) catch unreachable;
                        },
                        c.SETTING_TYPE_STRING => {
                            writer.writeInt(u16, setting.u.string_setting.nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.string_setting.maximum_length) catch unreachable;
                        },
                        c.SETTING_TYPE_INT32 => {
                            writer.writeInt(u16, setting.u.int32_setting.nvm_word, .big) catch unreachable;
                            writer.writeInt(i32, setting.u.int32_setting.minimum, .big) catch unreachable;
                            writer.writeInt(i32, setting.u.int32_setting.maximum, .big) catch unreachable;
                        },
                        c.SETTING_TYPE_INT32_SCALED => {
                            writer.writeInt(u16, setting.u.int32_scaled_setting.nvm_word, .big) catch unreachable;
                            writer.writeInt(i32, setting.u.int32_scaled_setting.minimum, .big) catch unreachable;
                            writer.writeInt(i32, setting.u.int32_scaled_setting.maximum, .big) catch unreachable;
                            writer.writeByte(setting.u.int32_scaled_setting.unit_type) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.int32_scaled_setting.scale)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.int32_scaled_setting.offset)), .big) catch unreachable;
                        },
                        c.SETTING_TYPE_FLOAT => {
                            writer.writeInt(u16, setting.u.float_setting.nvm_word, .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_setting.minimum)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_setting.maximum)), .big) catch unreachable;
                            writer.writeByte(setting.u.float_setting.unit_type) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_setting.scale)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_setting.offset)), .big) catch unreachable;
                        },
                        c.SETTING_TYPE_FLOAT_ARRAY => {
                            writer.writeInt(u16, setting.u.float_array_setting.nvm_word, .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_array_setting.minimum)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_array_setting.maximum)), .big) catch unreachable;
                            writer.writeByte(setting.u.float_array_setting.unit_type) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_array_setting.scale)), .big) catch unreachable;
                            writer.writeInt(u32, @as(u32, @bitCast(setting.u.float_array_setting.offset)), .big) catch unreachable;
                            writer.writeByte(setting.u.float_array_setting.maximum_length) catch unreachable;
                            writer.writeInt(u16, setting.u.float_array_setting.length_nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.float_array_setting.length_nvm_word_byte) catch unreachable;
                        },
                        c.SETTING_TYPE_CUSTOM_ENUM => {
                            writer.writeInt(u16, setting.u.custom_enum_setting.nvm_word, .big) catch unreachable;
                            writer.writeByte(setting.u.custom_enum_setting.nvm_word_byte) catch unreachable;
                            writer.writeByte(setting.u.custom_enum_setting.custom_enum_index) catch unreachable;
                        },
                        else => {
                            // unknown setting type, don't try to write anything more
                        },
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SETTING_DEFAULT => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_count_known != 0) {
                if (index < device_info.setting_count) {
                    const setting = &device_info.settings[index];
                    if (setting.default_bytes_length > 0) {
                        writer.writeAll(setting.default_bytes[0..setting.default_bytes_length]) catch {}; // ignore too long
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_CUSTOM_ENUM_COUNTS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.custom_enum_lengths) |custom_enum_lengths| {
                if (device_info.custom_enum_count > 0) {
                    writer.writeAll(custom_enum_lengths[0..device_info.custom_enum_count]) catch {}; // ignore too long
                }
            }
        },
        c.CMD_GET_CUSTOM_ENUM_VALUE_NAME => {
            const enum_index = reader.takeByte() catch return error.BadCmdLength;
            const enum_value = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.custom_enum_lengths) |custom_enum_lengths| {
                if (enum_index < device_info.custom_enum_count) {
                    const length: u8 = custom_enum_lengths[enum_index];
                    if (enum_value < length) {
                        // we've checked that these levels all exist in missingRequiredDeviceInfo()
                        const value = device_info.custom_enum_values[enum_index][enum_value];
                        writer.writeAll(std.mem.span(value)) catch {}; // ignore too long
                    } else {
                        return error.BadIndex;
                    }
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SETTING_CATEGORY_COUNT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_category_count_known != 0) {
                const count = std.math.lossyCast(u8, device_info.setting_category_count);
                writer.writeByte(count) catch unreachable;
            } else {
                return &[1]u8{0}; // zero
            }
        },
        c.CMD_GET_SETTING_CATEGORY_NAME => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_category_count_known != 0) {
                if (index < device_info.setting_category_count) {
                    const name = device_info.setting_category_names[index];
                    writer.writeAll(std.mem.span(name)) catch {}; // ignore too long
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_GET_SETTING_CATEGORY_SETTINGS => {
            const index = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.setting_category_count_known != 0) {
                if (index < device_info.setting_category_count) {
                    const length = device_info.setting_category_settings_lengths[index];
                    const settings = device_info.setting_category_settings[index];
                    writer.writeAll(settings[0..length]) catch {}; // ignore too long
                } else {
                    return error.BadIndex;
                }
            } else {
                return error.BadIndex;
            }
        },
        c.CMD_SET_DEVICE_MODE => {
            const mode = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_device_mode) |supports_device_mode| {
                if (supports_device_mode.* != 0) {
                    internals.state.device_mode = mode;
                    if (internals.callbacks.set_device_mode) |set_device_mode| {
                        set_device_mode(mode, internals.callbacks.closure);
                    }
                } else {
                    return error.UnimplementedCommand;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_DEVICE_MODE => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_device_mode) |supports_device_mode| {
                if (supports_device_mode.* != 0) {
                    writer.writeByte(internals.state.device_mode) catch unreachable;
                } else {
                    return error.UnimplementedCommand;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_ENABLE_RF_POWER => {
            const enable = reader.takeByte() catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_rf_power != 0) {
                internals.state.rf_power_enabled = enable != 0;
                if (internals.callbacks.set_rf_power) |set_rf_power| {
                    set_rf_power(enable, internals.callbacks.closure);
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RF_POWER_STATUS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_rf_power != 0) {
                writer.writeByte(if (internals.state.rf_power_enabled) 1 else 0) catch unreachable;
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RF_POWER_CTRL_VARS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_rf_power != 0) {
                if (device_info.rf_power_ctrl_var_count_known != 0) {
                    if (device_info.rf_power_ctrl_var_count > 0) {
                        const ctrl_vars = device_info.rf_power_ctrl_vars[0..device_info.rf_power_ctrl_var_count];
                        writer.writeAll(ctrl_vars) catch {}; // ignore too long
                    }
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_RESET_RF_POWER_TIMEOUT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_rf_power != 0) {
                // ignore
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_STOP_RADIO => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                stopRadio(internals);
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_START_RADIO_SCAN => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                stopRadio(internals);
                internals.state.radio_state = .scanning;
                if (internals.callbacks.start_radio_scan) |start_radio_scan| {
                    start_radio_scan(0, internals.callbacks.closure);
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_SCAN_RESULTS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                if (internals.callbacks.get_scan_results) |get_scan_results| {
                    const max_items = @divFloor(device_info.max_outgoing_param_length, 4);
                    if (internals.scan_result_buffer == null) {
                        const max_alloc_items = max_items;
                        const allocator: Allocator = internals.arena.allocator();
                        internals.scan_result_buffer = try allocator.alloc(c.AsphodelExtraScanResult_t, max_alloc_items);
                    }

                    std.debug.assert(internals.scan_result_buffer.?.len >= max_items);

                    const count = @min(max_items, get_scan_results(internals.scan_result_buffer.?.ptr, max_items, internals.callbacks.closure));
                    for (0..count) |i| {
                        const result = &internals.scan_result_buffer.?[i];
                        writer.writeInt(u32, result.serial_number, .big) catch unreachable;
                    }
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_CONNECT_RADIO => {
            const serial_number = reader.takeInt(u32, .big) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                stopRadio(internals);
                internals.state.radio_state = .{ .connecting = serial_number };
                if (internals.callbacks.connect_radio) |connect_radio| {
                    connect_radio(serial_number, 0, internals.callbacks.closure);
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_STATUS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                switch (internals.state.radio_state) {
                    .stopped => {
                        writer.writeByte(0) catch unreachable; // connected
                        writer.writeInt(u32, 0, .big) catch unreachable; // serial number
                        writer.writeByte(0) catch unreachable; // type
                        writer.writeByte(0) catch unreachable; // scanning
                    },
                    .scanning => {
                        writer.writeByte(0) catch unreachable; // connected
                        writer.writeInt(u32, 0, .big) catch unreachable; // serial number
                        writer.writeByte(0) catch unreachable; // type
                        writer.writeByte(1) catch unreachable; // scanning
                    },
                    .connecting => |serial_number| {
                        writer.writeByte(0) catch unreachable; // connected
                        writer.writeInt(u32, serial_number, .big) catch unreachable; // serial number
                        writer.writeByte(0) catch unreachable; // type
                        writer.writeByte(0) catch unreachable; // scanning
                    },
                    .connected => |connected| {
                        const serial_number, const protocol_type = connected;
                        writer.writeByte(1) catch unreachable; // connected
                        writer.writeInt(u32, serial_number, .big) catch unreachable; // serial number
                        writer.writeByte(protocol_type) catch unreachable; // type
                        writer.writeByte(0) catch unreachable; // scanning
                    },
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_CTRL_VARS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                if (device_info.radio_ctrl_var_count_known != 0) {
                    if (device_info.radio_ctrl_var_count > 0) {
                        const ctrl_vars = device_info.radio_ctrl_vars[0..device_info.radio_ctrl_var_count];
                        writer.writeAll(ctrl_vars) catch {}; // ignore too long
                    }
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_DEFAULT_SERIAL => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                if (device_info.radio_default_serial) |serial| {
                    writer.writeInt(u32, serial.*, .big) catch unreachable;
                } else {
                    writer.writeInt(u32, 0, .big) catch unreachable;
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_START_RADIO_SCAN_BOOT => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                stopRadio(internals);
                internals.state.radio_state = .scanning;
                if (internals.callbacks.start_radio_scan) |start_radio_scan| {
                    start_radio_scan(1, internals.callbacks.closure);
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_CONNECT_RADIO_BOOT => {
            const serial_number = reader.takeInt(u32, .big) catch return error.BadCmdLength;
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                stopRadio(internals);
                internals.state.radio_state = .{ .connecting = serial_number };
                if (internals.callbacks.connect_radio) |connect_radio| {
                    connect_radio(serial_number, 1, internals.callbacks.closure);
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_EXTRA_SCAN_RESULTS => {
            if (reader.discardRemaining() catch unreachable != 0) return error.BadCmdLength;
            if (device_info.supports_radio != 0) {
                if (internals.callbacks.get_scan_results) |get_scan_results| {
                    const max_items = @divFloor(device_info.max_outgoing_param_length, 6);
                    if (internals.scan_result_buffer == null) {
                        const max_alloc_items = @divFloor(device_info.max_outgoing_param_length, 4); // max for regular scan results
                        const allocator: Allocator = internals.arena.allocator();
                        internals.scan_result_buffer = try allocator.alloc(c.AsphodelExtraScanResult_t, max_alloc_items);
                    }

                    std.debug.assert(internals.scan_result_buffer.?.len >= max_items);

                    const count = @min(max_items, get_scan_results(internals.scan_result_buffer.?.ptr, max_items, internals.callbacks.closure));
                    for (0..count) |i| {
                        const result = &internals.scan_result_buffer.?[i];
                        writer.writeInt(u32, result.serial_number, .big) catch unreachable;
                        writer.writeByte(result.asphodel_type) catch unreachable;
                        writer.writeByte(result.device_mode) catch unreachable;
                    }
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_GET_RADIO_SCAN_POWER => {
            if (device_info.supports_radio != 0) {
                const byte_count: usize = reader.bufferedLen();
                if (byte_count == 0 or byte_count % 4 != 0) return error.BadCmdLength;
                const sn_count = byte_count / 4;
                if (internals.callbacks.get_scan_power) |get_scan_power| {
                    for (0..sn_count) |_| {
                        const serial_number = reader.takeInt(u32, .big) catch unreachable;
                        const power: i8 = get_scan_power(serial_number, internals.callbacks.closure);
                        writer.writeByte(@bitCast(power)) catch break;
                    }
                } else {
                    writer.splatByteAll(0x7F, sn_count) catch {}; // ignore too long
                }
            } else {
                return error.UnimplementedCommand;
            }
        },
        c.CMD_DO_RADIO_FIXED_TEST => {
            // not implemented
            return error.UnimplementedCommand;
        },
        c.CMD_DO_RADIO_SWEEP_TEST => {
            // not implemented
            return error.UnimplementedCommand;
        },
        // NOTE: remote commands are handled in handleRemoteCommand() instead
        c.CMD_GET_GPIO_PORT_COUNT => return &[1]u8{0}, // not supported
        c.CMD_GET_GPIO_PORT_NAME => return error.BadIndex, // not supported
        c.CMD_GET_GPIO_PORT_INFO => return error.BadIndex, // not supported
        c.CMD_GET_GPIO_PORT_VALUES => return error.BadIndex, // not supported
        c.CMD_SET_GPIO_PORT_MODES => return error.BadIndex, // not supported
        c.CMD_DISABLE_GPIO_PORT_OVERRIDES => {}, // not supported
        c.CMD_GET_BUS_COUNTS => return &[2]u8{ 0, 0 }, // not supported
        c.CMD_SET_SPI_CS_MODE => return error.BadIndex, // not supported
        c.CMD_DO_SPI_TRANSFER => return error.BadIndex, // not supported
        c.CMD_DO_I2C_WRITE => return error.BadIndex, // not supported
        c.CMD_DO_I2C_READ => return error.BadIndex, // not supported
        c.CMD_DO_I2C_WRITE_READ => return error.BadIndex, // not supported
        c.CMD_GET_INFO_REGION_COUNT => return &[1]u8{0}, // not supported
        c.CMD_GET_INFO_REGION_NAME => return error.BadIndex, // not supported
        c.CMD_GET_INFO_REGION => return error.BadIndex, // not supported
        c.CMD_GET_STACK_INFO => return &[8]u8{ 0, 0, 0, 0, 0, 0, 0, 0 }, // not supported
        else => return error.UnimplementedCommand,
    }

    return writer.buffered();
}

fn handleRemoteCommand(context: *Context, command: u8, reply_buffer: *[7]u8) error{UnimplementedCommand}![]const u8 {
    var writer = std.Io.Writer.fixed(reply_buffer);

    switch (command) {
        c.CMD_FLUSH => {
            // NOTE: this is handled here for remotes, but in handleCommand() for non-remotes
            if (context.remote_internals) |remote_internals| {
                flushState(remote_internals, true);
            } else {
                // ignore flush on disconnected remote to match behavior of WMRs
            }
        },
        c.CMD_STOP_REMOTE => {
            stopRadio(&context.main_internals);
        },
        c.CMD_RESTART_REMOTE => {
            if (context.main_internals.callbacks.restart_remote) |restart_remote| {
                restart_remote(c.CMD_RESTART_REMOTE, context.main_internals.callbacks.closure);
            }
        },
        c.CMD_GET_REMOTE_STATUS => {
            switch (context.main_internals.state.radio_state) {
                .stopped, .scanning => {
                    writer.writeByte(0) catch unreachable; // connected
                    writer.writeInt(u32, 0, .big) catch unreachable; // serial number
                    writer.writeByte(0) catch unreachable; // type
                },
                .connecting => |serial_number| {
                    writer.writeByte(0) catch unreachable; // connected
                    writer.writeInt(u32, serial_number, .big) catch unreachable; // serial number
                    writer.writeByte(0) catch unreachable; // type
                },
                .connected => |connected| {
                    const serial_number, const protocol_type = connected;
                    writer.writeByte(1) catch unreachable; // connected
                    writer.writeInt(u32, serial_number, .big) catch unreachable; // serial number
                    writer.writeByte(protocol_type) catch unreachable; // type
                },
            }
        },
        c.CMD_RESTART_REMOTE_APP => {
            if (context.main_internals.callbacks.restart_remote) |restart_remote| {
                restart_remote(c.CMD_RESTART_REMOTE_APP, context.main_internals.callbacks.closure);
            }
        },
        c.CMD_RESTART_REMOTE_BOOT => {
            if (context.main_internals.callbacks.restart_remote) |restart_remote| {
                restart_remote(c.CMD_RESTART_REMOTE_BOOT, context.main_internals.callbacks.closure);
            }
        },
        else => return error.UnimplementedCommand,
    }

    return writer.buffered();
}

fn handleString(writer: *std.Io.Writer, input: ?[*:0]const u8, default: AsphodelError![]const u8) AsphodelError!void {
    if (input) |value| {
        writer.writeAll(std.mem.span(value)) catch {}; // ignore too long
    } else {
        if (default) |value| {
            writer.writeAll(value) catch {}; // ignore too long
        } else |err| {
            return err;
        }
    }
}

fn parseProtocolVersion(protocol_version: []const u8) ?[2]u8 {
    var iterator = std.mem.splitScalar(u8, protocol_version, '.');
    const major_str = iterator.first();
    const minor_str = iterator.next() orelse return null;
    const subminor_str = iterator.next() orelse return null;
    if (iterator.next() != null) return null;

    const major = std.fmt.parseInt(u8, major_str, 10) catch return null;
    const minor = std.fmt.parseInt(u4, minor_str, 10) catch return null;
    const subminor = std.fmt.parseInt(u4, subminor_str, 10) catch return null;

    return .{ major, (@as(u8, minor) << 4) | subminor };
}

test "basic virtual device" {
    const device_info = c.AsphodelDeviceInfo_t{
        .max_incoming_param_length = 32,
        .max_outgoing_param_length = 32,
        .stream_packet_length = 32,
    };
    var device: ?*c.AsphodelDevice_t = null;
    var result = c.asphodel_create_virtual_device(&device_info, null, 1, &device);
    try std.testing.expectEqual(c.ASPHODEL_SUCCESS, result);
    defer device.?.free_device.?(device);

    result = device.?.open_device.?(device);
    try std.testing.expectEqual(c.ASPHODEL_SUCCESS, result);

    var protocol_version: u16 = undefined;
    result = c.asphodel_get_protocol_version_blocking(device, &protocol_version);
    try std.testing.expectEqual(c.ASPHODEL_SUCCESS, result);

    try std.testing.expectEqual(protocol_version, (c.ASPHODEL_PROTOCOL_VERSION_MAJOR << 8) | (c.ASPHODEL_PROTOCOL_VERSION_MINOR << 4) | c.ASPHODEL_PROTOCOL_VERSION_SUBMINOR);
}
