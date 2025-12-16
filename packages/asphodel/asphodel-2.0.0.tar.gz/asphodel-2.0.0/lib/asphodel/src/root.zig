pub const device_info = @import("device_info.zig");
pub const device_info_cache = @import("device_info_cache.zig");
pub const device_info_comparison = @import("device_info_comparison.zig");
pub const device_info_summary = @import("device_info_summary.zig");
pub const json = @import("json.zig");
pub const json_setting = @import("json_setting.zig");
pub const virtual_device = @import("virtual_device.zig");

comptime {
    _ = device_info;
    _ = device_info_cache;
    _ = device_info_comparison;
    _ = device_info_summary;
    _ = json;
    _ = json_setting;
    _ = virtual_device;
}

pub const c = @cImport({
    @cInclude("asphodel.h");
});

pub const version = @cImport({
    @cInclude("version_autogen.h");
});

pub const sqlite3 = @import("sqlite3");
