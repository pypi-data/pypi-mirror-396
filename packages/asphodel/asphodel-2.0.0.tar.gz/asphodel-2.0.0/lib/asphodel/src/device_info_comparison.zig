const std = @import("std");
const c = @import("root.zig").c;

// For the purposes of this code, a subset is something that might be a valid state along the way of collecting the
// full superset information from the device. It will never have more information than the superset. Also, no floating
// point math happens at the device info level, so exact equality is used.

pub export fn asphodel_device_info_equal(a: *const c.AsphodelDeviceInfo_t, b: *const c.AsphodelDeviceInfo_t) u8 {
    const result = compareDeviceInfo(a, b, true);
    return if (result) 1 else 0;
}

pub export fn asphodel_device_info_is_subset(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t) u8 {
    const result = compareDeviceInfo(subset, superset, false);
    return if (result) 1 else 0;
}

fn compareDeviceInfo(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    if (!compareSimpleEqual(subset, superset)) return false;
    if (!compareAllStrings(subset, superset, check_equal)) return false;

    if (!compareRgb(subset, superset, check_equal)) return false;
    if (!compareLed(subset, superset, check_equal)) return false;
    if (!compareStreams(subset, superset, check_equal)) return false;
    if (!compareChannels(subset, superset, check_equal)) return false;
    if (!compareSupplies(subset, superset, check_equal)) return false;
    if (!compareCtrlVars(subset, superset, check_equal)) return false;
    if (!compareSettings(subset, superset, check_equal)) return false;
    if (!compareCustomEnums(subset, superset, check_equal)) return false;
    if (!compareSettingCategories(subset, superset, check_equal)) return false;
    if (!compareDeviceMode(subset, superset, check_equal)) return false;
    if (!compareRfPowerCtrlVars(subset, superset, check_equal)) return false;
    if (!compareRadioCtrlVars(subset, superset, check_equal)) return false;
    if (!compareRadioDetails(subset, superset, check_equal)) return false;
    if (!compareNvm(subset, superset, check_equal)) return false;

    return true;
}

fn compareSimpleEqual(a: *const c.AsphodelDeviceInfo_t, b: *const c.AsphodelDeviceInfo_t) bool {
    // these items must all be equal, regardless of whether we're checking equal or subset

    if (a.max_incoming_param_length != b.max_incoming_param_length) return false;
    if (a.max_outgoing_param_length != b.max_outgoing_param_length) return false;
    if (a.stream_packet_length != b.stream_packet_length) return false;
    if (a.supports_bootloader != b.supports_bootloader) return false;
    if (a.supports_radio != b.supports_radio) return false;
    if (a.supports_remote != b.supports_remote) return false;
    if (a.supports_rf_power != b.supports_rf_power) return false;

    if (a.supports_rf_power != 0) {
        if (a.rf_power_enabled != b.rf_power_enabled) return false;
    }

    if (a.supports_radio != 0) {
        // these are only valid if the device supports radio (not remote)
        if (a.remote_max_incoming_param_length != b.remote_max_incoming_param_length) return false;
        if (a.remote_max_outgoing_param_length != b.remote_max_outgoing_param_length) return false;
        if (a.remote_stream_packet_length != b.remote_stream_packet_length) return false;
    }

    // NVM modification state should be identical regardless of whether we're checking equal or subset
    if (!compareSingleElement(u8, a.nvm_modified, b.nvm_modified, true)) return false;

    return true;
}

fn compareSingleElement(comptime T: type, subset: ?*const T, superset: ?*const T, check_equal: bool) bool {
    if (subset) |subset_value| {
        if (superset) |superset_value| {
            // both exist, compare contents
            return subset_value.* == superset_value.*;
        } else {
            // subset exists, superset doesn't
            return false;
        }
    } else {
        if (superset == null) return true;
        return !check_equal;
    }
}

fn Comparable(comptime T: type) type {
    return union(enum) {
        unknown,
        length: usize,
        slice: []const T,
    };
}

fn toComparable(comptime T: type, count_known: u8, count: usize, pointer: ?[*]const T) Comparable(T) {
    if (count_known == 0) return .unknown;

    if (pointer) |pointer_value| {
        if (count > 0) {
            return .{ .slice = pointer_value[0..count] };
        } else {
            return .{ .length = 0 };
        }
    } else {
        return .{ .length = count };
    }
}

fn compareSimple(comptime T: type, subset: Comparable(T), superset: Comparable(T), check_equal: bool) bool {
    switch (superset) {
        .unknown => switch (subset) {
            .unknown => return true,
            .length => return false,
            .slice => return false,
        },
        .length => |superset_len| switch (subset) {
            .unknown => return !check_equal,
            .length => |subset_len| return superset_len == subset_len,
            .slice => return false,
        },
        .slice => |superset_slice| switch (subset) {
            .unknown => return !check_equal,
            .length => |subset_len| if (check_equal) return false else return subset_len == superset_slice.len,
            .slice => |subset_slice| {
                return std.mem.eql(T, subset_slice, superset_slice);
            },
        },
    }
}

fn compareWithFn(comptime T: type, subset: Comparable(T), superset: Comparable(T), check_equal: bool, compare: fn (subset: *const T, superset: *const T, check_equal: bool) bool) bool {
    switch (superset) {
        .unknown => switch (subset) {
            .unknown => return true,
            .length => return false,
            .slice => return false,
        },
        .length => |superset_len| switch (subset) {
            .unknown => return !check_equal,
            .length => |subset_len| return superset_len == subset_len,
            .slice => return false,
        },
        .slice => |superset_slice| switch (subset) {
            .unknown => return !check_equal,
            .length => |subset_len| if (check_equal) return false else return subset_len == superset_slice.len,
            .slice => |subset_slice| {
                if (subset_slice.len != superset_slice.len) return false;
                for (0..subset_slice.len) |i| {
                    const subset_element = &subset_slice[i];
                    const superset_element = &superset_slice[i];
                    if (!compare(subset_element, superset_element, check_equal)) return false;
                }
                return true;
            },
        },
    }
}

fn testComparableHelper(subset: Comparable(u8), superset: Comparable(u8), is_subset: bool, is_equal: bool) !void {
    // check symmetry first: should always be equal to itself and a subset of itself
    try std.testing.expect(compareSimple(u8, subset, subset, false));
    try std.testing.expect(compareSimple(u8, subset, subset, true));
    try std.testing.expect(compareSimple(u8, superset, superset, false));
    try std.testing.expect(compareSimple(u8, superset, superset, true));
    try std.testing.expect(compareWithFn(u8, subset, subset, false, compareByteElement));
    try std.testing.expect(compareWithFn(u8, subset, subset, true, compareByteElement));
    try std.testing.expect(compareWithFn(u8, superset, superset, false, compareByteElement));
    try std.testing.expect(compareWithFn(u8, superset, superset, true, compareByteElement));

    // direct subset comparison
    try std.testing.expectEqual(is_subset, compareSimple(u8, subset, superset, false));
    try std.testing.expectEqual(is_subset, compareWithFn(u8, subset, superset, false, compareByteElement));

    // reverse subset comparison: only true if they're equal
    try std.testing.expectEqual(is_equal, compareSimple(u8, superset, subset, false));
    try std.testing.expectEqual(is_equal, compareWithFn(u8, superset, subset, false, compareByteElement));

    // equal comparison, both directions
    try std.testing.expectEqual(is_equal, compareSimple(u8, subset, superset, true));
    try std.testing.expectEqual(is_equal, compareSimple(u8, superset, subset, true));
    try std.testing.expectEqual(is_equal, compareWithFn(u8, subset, superset, true, compareByteElement));
    try std.testing.expectEqual(is_equal, compareWithFn(u8, superset, subset, true, compareByteElement));
}

test "Comparable" {
    {
        // case 1: both unknown
        const a: Comparable(u8) = .unknown;
        const b: Comparable(u8) = .unknown;
        try testComparableHelper(a, b, true, true);
    }
    {
        // case 2: unknown vs length
        const subset: Comparable(u8) = .unknown;
        const superset: Comparable(u8) = .{ .length = 1 };
        try testComparableHelper(subset, superset, true, false);
    }
    {
        // case 3: unknown vs slice
        const subset: Comparable(u8) = .unknown;
        const superset: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        try testComparableHelper(subset, superset, true, false);
    }
    {
        // case 4a: both lengths, lengths match
        const a: Comparable(u8) = .{ .length = 1 };
        const b: Comparable(u8) = .{ .length = 1 };
        try testComparableHelper(a, b, true, true);
    }
    {
        // case 4b: both lengths, lengths different
        const a: Comparable(u8) = .{ .length = 1 };
        const b: Comparable(u8) = .{ .length = 2 };
        try testComparableHelper(a, b, false, false);
    }
    {
        // case 4c: both lengths, length zero
        const a: Comparable(u8) = .{ .length = 0 };
        const b: Comparable(u8) = .{ .length = 0 };
        try testComparableHelper(a, b, true, true);
    }
    {
        // case 5a: length vs slice, lengths match
        const subset: Comparable(u8) = .{ .length = 2 };
        const superset: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        try testComparableHelper(subset, superset, true, false);
    }
    {
        // case 5b: length vs slice, lengths different
        const a: Comparable(u8) = .{ .length = 1 };
        const b: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        try testComparableHelper(a, b, false, false);
    }
    {
        // case 6a: both slices, same contents
        const a: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        const b: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        try testComparableHelper(a, b, true, true);
    }
    {
        // case 6b: both slices, different lengths
        const a: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        const b: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2, 3 } };
        try testComparableHelper(a, b, false, false);
    }
    {
        // case 6c: both slices, same lengths, different contents
        const a: Comparable(u8) = .{ .slice = &[_]u8{ 1, 2 } };
        const b: Comparable(u8) = .{ .slice = &[_]u8{ 1, 3 } };
        try testComparableHelper(a, b, false, false);
    }
}

fn DeepComparable(comptime T: type) type {
    return union(enum) {
        unknown,
        count: usize,
        lengths: []const u8,
        slice: struct { lengths: []const u8, slice: []const ?[*]const T },
    };
}

fn toDeepComparable(comptime T: type, count_known: u8, count: usize, lengths: ?[*]const u8, pointer: ?[*]const ?[*]const T) DeepComparable(T) {
    if (count_known == 0) return .unknown;

    if (count == 0) return .{ .count = count };

    if (lengths) |lengths_value| {
        const lengths_slice = lengths_value[0..count];
        if (pointer) |pointer_value| {
            const slice = pointer_value[0..count];
            return .{ .slice = .{ .lengths = lengths_slice, .slice = slice } };
        } else {
            return .{ .lengths = lengths_slice };
        }
    } else {
        // only count is known
        return .{ .count = count };
    }
}

fn compareDeep(comptime T: type, subset: DeepComparable(T), superset: DeepComparable(T), check_equal: bool, compare: fn (subset: *const T, superset: *const T, check_equal: bool) bool) bool {
    switch (superset) {
        .unknown => switch (subset) {
            .unknown => return true,
            .count => return false,
            .lengths => return false,
            .slice => return false,
        },
        .count => |superset_count| switch (subset) {
            .unknown => return !check_equal,
            .count => |subset_count| return superset_count == subset_count,
            .lengths => return false,
            .slice => return false,
        },
        .lengths => |superset_lengths| switch (subset) {
            .unknown => return !check_equal,
            .count => |subset_count| if (check_equal) return false else return subset_count == superset_lengths.len,
            .lengths => |subset_lengths| return compareLengths(subset_lengths, superset_lengths, check_equal),
            .slice => return false,
        },
        .slice => |superset_values| switch (subset) {
            .unknown => return !check_equal,
            .count => |subset_count| if (check_equal) return false else return subset_count == superset_values.lengths.len,
            .lengths => |subset_lengths| if (check_equal) return false else return compareLengths(subset_lengths, superset_values.lengths, check_equal),
            .slice => |subset_values| {
                if (!compareLengths(subset_values.lengths, superset_values.lengths, check_equal)) return false; // lengths must match
                for (subset_values.lengths, 0..) |length, i| {
                    const maybe_subset_ptr: ?[*]const T = if (length == 0) null else subset_values.slice[i];
                    const maybe_superset_ptr: ?[*]const T = if (length == 0) null else superset_values.slice[i];
                    if (maybe_subset_ptr) |subset_ptr| {
                        if (maybe_superset_ptr) |superset_ptr| {
                            for (subset_ptr[0..length], superset_ptr[0..length]) |*subset_element, *superset_element| {
                                if (!compare(subset_element, superset_element, check_equal)) return false;
                            }
                        } else {
                            // subset exists, superset doesn't
                            return false;
                        }
                    } else {
                        if (maybe_superset_ptr != null) {
                            // subset doesn't exist, superset exists
                            if (check_equal) return false;
                        } else {
                            // both null: fine
                        }
                    }
                }
                return true;
            },
        },
    }
}

fn compareLengths(subset: []const u8, superset: []const u8, check_equal: bool) bool {
    if (check_equal) return std.mem.eql(u8, subset, superset);

    if (subset.len != superset.len) return false;
    for (subset, superset) |subset_element, superset_element| {
        if (subset_element == superset_element) continue;
        if (subset_element == 0) continue;
        return false;
    }

    return true;
}

fn testDeepComparableHelper(subset: DeepComparable(u8), superset: DeepComparable(u8), is_subset: bool, is_equal: bool) !void {
    // check symmetry first: should always be equal to itself and a subset of itself
    try std.testing.expect(compareDeep(u8, subset, subset, false, compareByteElement));
    try std.testing.expect(compareDeep(u8, subset, subset, true, compareByteElement));
    try std.testing.expect(compareDeep(u8, superset, superset, false, compareByteElement));
    try std.testing.expect(compareDeep(u8, superset, superset, true, compareByteElement));

    // direct subset comparison
    try std.testing.expectEqual(is_subset, compareDeep(u8, subset, superset, false, compareByteElement));

    // reverse subset comparison: only true if they're equal
    try std.testing.expectEqual(is_equal, compareDeep(u8, superset, subset, false, compareByteElement));

    // equal comparison, both directions
    try std.testing.expectEqual(is_equal, compareDeep(u8, subset, superset, true, compareByteElement));
    try std.testing.expectEqual(is_equal, compareDeep(u8, superset, subset, true, compareByteElement));
}

test "DeepComparable" {
    {
        // case 1: both unknown
        const a: DeepComparable(u8) = .unknown;
        const b: DeepComparable(u8) = .unknown;
        try testDeepComparableHelper(a, b, true, true);
    }
    {
        // case 2: unknown vs count
        const subset: DeepComparable(u8) = .unknown;
        const superset: DeepComparable(u8) = .{ .count = 1 };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 3: unknown vs lengths
        const subset: DeepComparable(u8) = .unknown;
        const superset: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 4: unknown vs slice
        const subset: DeepComparable(u8) = .unknown;
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 5a: both counts, counts match
        const a: DeepComparable(u8) = .{ .count = 1 };
        const b: DeepComparable(u8) = .{ .count = 1 };
        try testDeepComparableHelper(a, b, true, true);
    }
    {
        // case 5b: both counts, counts different
        const a: DeepComparable(u8) = .{ .count = 1 };
        const b: DeepComparable(u8) = .{ .count = 2 };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 5c: both counts, counts zero
        const a: DeepComparable(u8) = .{ .count = 0 };
        const b: DeepComparable(u8) = .{ .count = 0 };
        try testDeepComparableHelper(a, b, true, true);
    }
    {
        // case 6a: count vs lengths, counts match
        const subset: DeepComparable(u8) = .{ .count = 2 };
        const superset: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 6b: count vs lengths, counts different
        const a: DeepComparable(u8) = .{ .count = 1 };
        const b: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 7a: count vs slice, counts match
        const subset: DeepComparable(u8) = .{ .count = 2 };
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 7b: count vs slice, counts different
        const a: DeepComparable(u8) = .{ .count = 1 };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 8a: both lengths, same contents
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        const b: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        try testDeepComparableHelper(a, b, true, true);
    }
    {
        // case 8b: both lengths, different counts
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        const b: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2, 3 } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 8c: both lengths, same counts, different length contents
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        const b: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 3 } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 8c: both lengths, same counts, some lengths zero
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 0 } };
        const b: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        try testDeepComparableHelper(a, b, true, false);
    }
    {
        // case 9a: lengths vs slice, same lengths
        const subset: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 2 } };
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 9b: lengths vs slice, different counts
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{1} };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 9c: lengths vs slice, different lengths contents
        const a: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 3 } };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 9d: lengths vs slice, some lengths zero
        const subset: DeepComparable(u8) = .{ .lengths = &[_]u8{ 1, 0 } };
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 10a: slice vs slice, same contents
        const a: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, true, true);
    }
    {
        // case 10b: slice vs slice, different counts
        const a: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{1},
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
            },
        } };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 10c: slice vs slice, different lengths
        const a: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 1 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{0x88}).ptr,
            },
        } };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 10d: slice vs slice, different contents
        const a: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0, 0x99 }).ptr,
            },
        } };
        const b: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(a, b, false, false);
    }
    {
        // case 10e: slice vs slice, same contents, some missing
        const subset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                null,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
    {
        // case 10e: slice vs slice, same contents, some lengths zero
        const subset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 0, 2 },
            .slice = &[_]?[*]const u8{
                null,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        const superset: DeepComparable(u8) = .{ .slice = .{
            .lengths = &[_]u8{ 1, 2 },
            .slice = &[_]?[*]const u8{
                (&[_]u8{0x77}).ptr,
                (&[_]u8{ 0x88, 0x99 }).ptr,
            },
        } };
        try testDeepComparableHelper(subset, superset, true, false);
    }
}

fn compareByteElement(subset: *const u8, superset: *const u8, check_equal: bool) bool {
    _ = check_equal; // irrelevant for this function
    return subset.* == superset.*;
}

test "compareByteElement" {
    const a: u8 = 1;
    const b: u8 = 1;
    const x: u8 = 2;
    try std.testing.expect(compareByteElement(&a, &a, false));
    try std.testing.expect(compareByteElement(&a, &a, true));
    try std.testing.expect(compareByteElement(&a, &b, false));
    try std.testing.expect(compareByteElement(&a, &b, true));
    try std.testing.expect(!compareByteElement(&a, &x, false));
    try std.testing.expect(!compareByteElement(&a, &x, true));
}

fn compareString(subset_str: ?[*:0]const u8, superset_str: ?[*:0]const u8, check_equal: bool) bool {
    if (subset_str) |subset| {
        if (superset_str) |superset| {
            // both have strings, so they must be equal
            return std.mem.eql(u8, std.mem.span(subset), std.mem.span(superset));
        } else {
            // subset exists, superset doesn't
            return false;
        }
    } else {
        if (superset_str == null) return true;
        return !check_equal;
    }
}

fn compareStringWrapper(subset: *const ?[*:0]const u8, superset: *const ?[*:0]const u8, check_equal: bool) bool {
    return compareString(subset.*, superset.*, check_equal);
}

test "compareString" {
    try std.testing.expect(compareString(null, null, false));
    try std.testing.expect(compareString(null, null, true));
    try std.testing.expect(compareString(null, "foo", false));
    try std.testing.expect(!compareString(null, "foo", true));
    try std.testing.expect(!compareString("foo", null, false));
    try std.testing.expect(!compareString("foo", null, true));
    try std.testing.expect(compareString("foo", "foo", false));
    try std.testing.expect(compareString("foo", "foo", true));
    try std.testing.expect(!compareString("foo", "bar", false));
    try std.testing.expect(!compareString("foo", "bar", true));
}

fn compareAllStrings(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    // check all the device info strings
    if (!compareString(subset.serial_number, superset.serial_number, check_equal)) return false;
    if (!compareString(subset.location_string, superset.location_string, check_equal)) return false;
    if (!compareString(subset.build_date, superset.build_date, check_equal)) return false;
    if (!compareString(subset.build_info, superset.build_info, check_equal)) return false;
    if (!compareString(subset.nvm_hash, superset.nvm_hash, check_equal)) return false;
    if (!compareString(subset.setting_hash, superset.setting_hash, check_equal)) return false;
    if (!compareString(subset.protocol_version, superset.protocol_version, check_equal)) return false;
    if (!compareString(subset.chip_family, superset.chip_family, check_equal)) return false;
    if (!compareString(subset.chip_id, superset.chip_id, check_equal)) return false;
    if (!compareString(subset.chip_model, superset.chip_model, check_equal)) return false;
    if (!compareString(subset.bootloader_info, superset.bootloader_info, check_equal)) return false;
    if (!compareString(subset.commit_id, superset.commit_id, check_equal)) return false;
    if (!compareString(subset.repo_branch, superset.repo_branch, check_equal)) return false;
    if (!compareString(subset.repo_name, superset.repo_name, check_equal)) return false;
    if (!compareString(subset.user_tag_1, superset.user_tag_1, check_equal)) return false;
    if (!compareString(subset.user_tag_2, superset.user_tag_2, check_equal)) return false;

    // check the board info string, and compare the revs only if both have strings
    if (!compareString(subset.board_info_name, superset.board_info_name, check_equal)) return false;
    if (subset.board_info_name != null and superset.board_info_name != null) {
        if (subset.board_info_rev != superset.board_info_rev) return false;
    }

    return true;
}

fn compareRgb(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_rgb = toComparable([3]u8, subset.rgb_count_known, subset.rgb_count, subset.rgb_settings);
    const superset_rgb = toComparable([3]u8, superset.rgb_count_known, superset.rgb_count, superset.rgb_settings);
    if (!compareSimple([3]u8, subset_rgb, superset_rgb, check_equal)) return false;

    return true;
}

fn compareLed(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_led = toComparable(u8, subset.led_count_known, subset.led_count, subset.led_settings);
    const superset_led = toComparable(u8, superset.led_count_known, superset.led_count, superset.led_settings);
    if (!compareSimple(u8, subset_led, superset_led, check_equal)) return false;

    return true;
}

fn compareStreams(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_streams = toComparable(c.AsphodelStreamInfo_t, subset.stream_count_known, subset.stream_count, subset.streams);
    const superset_streams = toComparable(c.AsphodelStreamInfo_t, superset.stream_count_known, superset.stream_count, superset.streams);
    if (!compareWithFn(c.AsphodelStreamInfo_t, subset_streams, superset_streams, check_equal, compareStream)) return false;

    const subset_stream_rates = toComparable(c.AsphodelStreamRateInfo_t, subset.stream_count_known, subset.stream_count, subset.stream_rates);
    const superset_stream_rates = toComparable(c.AsphodelStreamRateInfo_t, superset.stream_count_known, superset.stream_count, superset.stream_rates);
    if (!compareWithFn(c.AsphodelStreamRateInfo_t, subset_stream_rates, superset_stream_rates, check_equal, compareStreamRate)) return false;

    if (subset.stream_count_known != 0 and superset.stream_count_known != 0) {
        // if the counts are known then these must be identical
        if (subset.stream_filler_bits != superset.stream_filler_bits) return false;
        if (subset.stream_id_bits != superset.stream_id_bits) return false;
    }

    return true;
}

fn compareStream(subset: *const c.AsphodelStreamInfo_t, superset: *const c.AsphodelStreamInfo_t, check_equal: bool) bool {
    if (subset.filler_bits != superset.filler_bits) return false;
    if (subset.counter_bits != superset.counter_bits) return false;
    if (subset.rate != superset.rate) return false; // shouldn't be NaN
    if (subset.rate_error != superset.rate_error) return false; // shouldn't be NaN
    if (subset.warm_up_delay != superset.warm_up_delay) return false; // shouldn't be NaN

    const subset_index_list = toComparable(u8, @intFromBool(subset.channel_count != 0), subset.channel_count, subset.channel_index_list);
    const superset_index_list = toComparable(u8, @intFromBool(superset.channel_count != 0), superset.channel_count, superset.channel_index_list);
    if (!compareSimple(u8, subset_index_list, superset_index_list, check_equal)) return false;

    return true;
}

fn compareStreamRate(a: *const c.AsphodelStreamRateInfo_t, b: *const c.AsphodelStreamRateInfo_t, check_equal: bool) bool {
    _ = check_equal; // irrelevant for this function

    if (a.available != b.available) return false;
    if (a.available == 0) return true; // ignore the rest of the fields

    if (a.channel_index != b.channel_index) return false;
    if (a.invert != b.invert) return false;
    if (a.scale != b.scale) return false; // shouldn't be NaN
    if (a.offset != b.offset) return false; // shouldn't be NaN

    return true;
}

fn compareChannels(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_channels = toComparable(c.AsphodelChannelInfo_t, subset.channel_count_known, subset.channel_count, subset.channels);
    const superset_channels = toComparable(c.AsphodelChannelInfo_t, superset.channel_count_known, superset.channel_count, superset.channels);
    if (!compareWithFn(c.AsphodelChannelInfo_t, subset_channels, superset_channels, check_equal, compareChannel)) return false;

    const subset_channel_calibrations = toComparable(?*c.AsphodelChannelCalibration_t, subset.channel_count_known, subset.channel_count, subset.channel_calibrations);
    const superset_channel_calibrations = toComparable(?*c.AsphodelChannelCalibration_t, superset.channel_count_known, superset.channel_count, superset.channel_calibrations);
    if (!compareWithFn(?*c.AsphodelChannelCalibration_t, subset_channel_calibrations, superset_channel_calibrations, check_equal, compareChannelCalibration)) return false;

    return true;
}

fn compareChannel(subset: *const c.AsphodelChannelInfo_t, superset: *const c.AsphodelChannelInfo_t, check_equal: bool) bool {
    if (subset.channel_type != superset.channel_type) return false;
    if (subset.unit_type != superset.unit_type) return false;
    if (subset.filler_bits != superset.filler_bits) return false;
    if (subset.data_bits != superset.data_bits) return false;
    if (subset.samples != superset.samples) return false;
    if (subset.bits_per_sample != superset.bits_per_sample) return false;
    if (subset.minimum != superset.minimum) return false; // shouldn't be NaN
    if (subset.maximum != superset.maximum) return false; // shouldn't be NaN
    if (subset.resolution != superset.resolution) return false; // shouldn't be NaN

    const subset_name = toComparable(u8, @intFromBool(subset.name_length != 0), subset.name_length, subset.name);
    const superset_name = toComparable(u8, @intFromBool(superset.name_length != 0), superset.name_length, superset.name);
    if (!compareSimple(u8, subset_name, superset_name, check_equal)) return false;

    const subset_coefficients = toComparable(f32, @intFromBool(subset.coefficients_length != 0), subset.coefficients_length, subset.coefficients);
    const superset_coefficients = toComparable(f32, @intFromBool(superset.coefficients_length != 0), superset.coefficients_length, superset.coefficients);
    if (!compareSimple(f32, subset_coefficients, superset_coefficients, check_equal)) return false;

    // chunk count is returned with the channel info, so it's always known
    const subset_chunks = toDeepComparable(u8, 1, subset.chunk_count, subset.chunk_lengths, subset.chunks);
    const superset_chunks = toDeepComparable(u8, 1, superset.chunk_count, superset.chunk_lengths, superset.chunks);
    if (!compareDeep(u8, subset_chunks, superset_chunks, check_equal, compareByteElement)) return false;

    return true;
}

fn compareChannelCalibration(a: *const ?*const c.AsphodelChannelCalibration_t, b: *const ?*const c.AsphodelChannelCalibration_t, check_equal: bool) bool {
    _ = check_equal; // irrelevant for this function

    // in this case, either both need to be null or both need to be non-null

    if (a.*) |subset_calibration| {
        if (b.*) |superset_calibration| {
            if (subset_calibration.base_setting_index != superset_calibration.base_setting_index) return false;
            if (subset_calibration.resolution_setting_index != superset_calibration.resolution_setting_index) return false;
            if (subset_calibration.scale != superset_calibration.scale) return false; // shouldn't be NaN
            if (subset_calibration.offset != superset_calibration.offset) return false; // shouldn't be NaN
            if (subset_calibration.minimum != superset_calibration.minimum) return false; // shouldn't be NaN
            if (subset_calibration.maximum != superset_calibration.maximum) return false; // shouldn't be NaN
            return true;
        } else {
            // a exists, b doesn't
            return false;
        }
    } else {
        if (b.* != null) {
            // a doesn't exist, b exists
            return false;
        } else {
            // both null: fine
            return true;
        }
    }
}

fn compareSupplies(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_supplies = toComparable(c.AsphodelSupplyInfo_t, subset.supply_count_known, subset.supply_count, subset.supplies);
    const superset_supplies = toComparable(c.AsphodelSupplyInfo_t, superset.supply_count_known, superset.supply_count, superset.supplies);
    if (!compareWithFn(c.AsphodelSupplyInfo_t, subset_supplies, superset_supplies, check_equal, compareSupply)) return false;

    const subset_supply_results = toComparable(c.AsphodelSupplyResult_t, subset.supply_count_known, subset.supply_count, subset.supply_results);
    const superset_supply_results = toComparable(c.AsphodelSupplyResult_t, superset.supply_count_known, superset.supply_count, superset.supply_results);
    if (!compareWithFn(c.AsphodelSupplyResult_t, subset_supply_results, superset_supply_results, check_equal, compareSupplyResult)) return false;

    return true;
}

fn compareSupply(subset: *const c.AsphodelSupplyInfo_t, superset: *const c.AsphodelSupplyInfo_t, check_equal: bool) bool {
    if (subset.unit_type != superset.unit_type) return false;
    if (subset.is_battery != superset.is_battery) return false;
    if (subset.nominal != superset.nominal) return false;
    if (subset.scale != superset.scale) return false; // shouldn't be NaN
    if (subset.offset != superset.offset) return false; // shouldn't be NaN

    const subset_name = toComparable(u8, @intFromBool(subset.name_length != 0), subset.name_length, subset.name);
    const superset_name = toComparable(u8, @intFromBool(superset.name_length != 0), superset.name_length, superset.name);
    if (!compareSimple(u8, subset_name, superset_name, check_equal)) return false;

    return true;
}

fn compareSupplyResult(subset: *const c.AsphodelSupplyResult_t, superset: *const c.AsphodelSupplyResult_t, check_equal: bool) bool {
    _ = check_equal; // irrelevant for this function

    if (subset.error_code != superset.error_code) return false;

    if (subset.error_code == c.ASPHODEL_SUCCESS) {
        if (subset.measurement != superset.measurement) return false;
        if (subset.result != superset.result) return false;
    }

    return true;
}

fn compareCtrlVars(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_ctrl_vars = toComparable(c.AsphodelCtrlVarInfo_t, subset.ctrl_var_count_known, subset.ctrl_var_count, subset.ctrl_vars);
    const superset_ctrl_vars = toComparable(c.AsphodelCtrlVarInfo_t, superset.ctrl_var_count_known, superset.ctrl_var_count, superset.ctrl_vars);
    if (!compareWithFn(c.AsphodelCtrlVarInfo_t, subset_ctrl_vars, superset_ctrl_vars, check_equal, compareCtrlVar)) return false;

    const subset_states = toComparable(i32, subset.ctrl_var_count_known, subset.ctrl_var_count, subset.ctrl_var_states);
    const superset_states = toComparable(i32, superset.ctrl_var_count_known, superset.ctrl_var_count, superset.ctrl_var_states);
    if (!compareSimple(i32, subset_states, superset_states, check_equal)) return false;

    return true;
}

fn compareCtrlVar(subset: *const c.AsphodelCtrlVarInfo_t, superset: *const c.AsphodelCtrlVarInfo_t, check_equal: bool) bool {
    // compare fixed fields first
    if (subset.unit_type != superset.unit_type) return false;
    if (subset.minimum != superset.minimum) return false;
    if (subset.maximum != superset.maximum) return false;
    if (subset.scale != superset.scale) return false; // shouldn't be NaN
    if (subset.offset != superset.offset) return false; // shouldn't be NaN

    const subset_name = toComparable(u8, @intFromBool(subset.name_length != 0), subset.name_length, subset.name);
    const superset_name = toComparable(u8, @intFromBool(superset.name_length != 0), superset.name_length, superset.name);
    if (!compareSimple(u8, subset_name, superset_name, check_equal)) return false;

    return true;
}

fn compareSettings(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_settings = toComparable(c.AsphodelSettingInfo_t, subset.setting_count_known, subset.setting_count, subset.settings);
    const superset_settings = toComparable(c.AsphodelSettingInfo_t, superset.setting_count_known, superset.setting_count, superset.settings);
    if (!compareWithFn(c.AsphodelSettingInfo_t, subset_settings, superset_settings, check_equal, compareSetting)) return false;

    return true;
}

fn compareSetting(subset: *const c.AsphodelSettingInfo_t, superset: *const c.AsphodelSettingInfo_t, check_equal: bool) bool {
    if (subset.setting_type != superset.setting_type) return false;

    const setting_type = subset.setting_type;

    if (setting_type == c.SETTING_TYPE_BYTE or
        setting_type == c.SETTING_TYPE_BOOLEAN or
        setting_type == c.SETTING_TYPE_UNIT_TYPE or
        setting_type == c.SETTING_TYPE_CHANNEL_TYPE)
    {
        if (!compareSettingUnionFields(c.AsphodelByteSetting_t, subset.u.byte_setting, superset.u.byte_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_BYTE_ARRAY) {
        if (!compareSettingUnionFields(c.AsphodelByteArraySetting_t, subset.u.byte_array_setting, superset.u.byte_array_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_STRING) {
        if (!compareSettingUnionFields(c.AsphodelStringSetting_t, subset.u.string_setting, superset.u.string_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_INT32) {
        if (!compareSettingUnionFields(c.AsphodelInt32Setting_t, subset.u.int32_setting, superset.u.int32_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_INT32_SCALED) {
        if (!compareSettingUnionFields(c.AsphodelInt32ScaledSetting_t, subset.u.int32_scaled_setting, superset.u.int32_scaled_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_FLOAT) {
        if (!compareSettingUnionFields(c.AsphodelFloatSetting_t, subset.u.float_setting, superset.u.float_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_FLOAT_ARRAY) {
        if (!compareSettingUnionFields(c.AsphodelFloatArraySetting_t, subset.u.float_array_setting, superset.u.float_array_setting)) return false;
    } else if (setting_type == c.SETTING_TYPE_CUSTOM_ENUM) {
        if (!compareSettingUnionFields(c.AsphodelCustomEnumSetting_t, subset.u.custom_enum_setting, superset.u.custom_enum_setting)) return false;
    } else {
        return false; // couldn't compare them
    }

    const subset_name = toComparable(u8, @intFromBool(subset.name_length != 0), subset.name_length, subset.name);
    const superset_name = toComparable(u8, @intFromBool(superset.name_length != 0), superset.name_length, superset.name);
    if (!compareSimple(u8, subset_name, superset_name, check_equal)) return false;

    const subset_default_bytes = toComparable(u8, @intFromBool(subset.default_bytes_length != 0), subset.default_bytes_length, subset.default_bytes);
    const superset_default_bytes = toComparable(u8, @intFromBool(superset.default_bytes_length != 0), superset.default_bytes_length, superset.default_bytes);
    if (!compareSimple(u8, subset_default_bytes, superset_default_bytes, check_equal)) return false;

    return true;
}

fn compareSettingUnionFields(comptime T: type, a: T, b: T) bool {
    inline for (@typeInfo(T).@"struct".fields) |field| {
        if (@field(a, field.name) != @field(b, field.name)) return false;
    }

    return true;
}

fn compareCustomEnums(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_custom_enum_values = toDeepComparable(?[*:0]const u8, @intFromBool(subset.custom_enum_lengths != null), subset.custom_enum_count, subset.custom_enum_lengths, subset.custom_enum_values);
    const superset_custom_enum_values = toDeepComparable(?[*:0]const u8, @intFromBool(superset.custom_enum_lengths != null), superset.custom_enum_count, superset.custom_enum_lengths, superset.custom_enum_values);
    if (!compareDeep(?[*:0]const u8, subset_custom_enum_values, superset_custom_enum_values, check_equal, compareStringWrapper)) return false;

    return true;
}

fn compareSettingCategories(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_category_lengths = toComparable(u8, subset.setting_category_count_known, subset.setting_category_count, subset.setting_category_settings_lengths);
    const superset_category_lengths = toComparable(u8, superset.setting_category_count_known, superset.setting_category_count, superset.setting_category_settings_lengths);
    if (!compareSimple(u8, subset_category_lengths, superset_category_lengths, check_equal)) return false;

    const subset_category_names = toComparable(?[*:0]const u8, subset.setting_category_count_known, subset.setting_category_count, subset.setting_category_names);
    const superset_category_names = toComparable(?[*:0]const u8, superset.setting_category_count_known, superset.setting_category_count, superset.setting_category_names);
    if (!compareWithFn(?[*:0]const u8, subset_category_names, superset_category_names, check_equal, compareStringWrapper)) return false;

    const subset_category_settings = toDeepComparable(u8, subset.setting_category_count_known, subset.setting_category_count, subset.setting_category_settings_lengths, subset.setting_category_settings);
    const superset_category_settings = toDeepComparable(u8, superset.setting_category_count_known, superset.setting_category_count, superset.setting_category_settings_lengths, superset.setting_category_settings);
    if (!compareDeep(u8, subset_category_settings, superset_category_settings, check_equal, compareByteElement)) return false;

    return true;
}

fn compareDeviceMode(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    if (subset.supports_device_mode) |subset_supports_device_mode| {
        if (superset.supports_device_mode) |superset_supports_device_mode| {
            // both exist, compare contents
            if (subset_supports_device_mode.* != superset_supports_device_mode.*) return false;
            if (subset_supports_device_mode.* != 0 and subset.device_mode != superset.device_mode) return false;
            return true;
        } else {
            // subset exists, superset doesn't
            return false;
        }
    } else {
        if (superset.supports_device_mode == null) return true;
        return !check_equal;
    }
}

fn compareRfPowerCtrlVars(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_ctrl_vars = toComparable(u8, subset.rf_power_ctrl_var_count_known, subset.rf_power_ctrl_var_count, subset.rf_power_ctrl_vars);
    const superset_ctrl_vars = toComparable(u8, superset.rf_power_ctrl_var_count_known, superset.rf_power_ctrl_var_count, superset.rf_power_ctrl_vars);
    if (!compareSimple(u8, subset_ctrl_vars, superset_ctrl_vars, check_equal)) return false;

    return true;
}

fn compareRadioCtrlVars(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_ctrl_vars = toComparable(u8, subset.radio_ctrl_var_count_known, subset.radio_ctrl_var_count, subset.radio_ctrl_vars);
    const superset_ctrl_vars = toComparable(u8, superset.radio_ctrl_var_count_known, superset.radio_ctrl_var_count, superset.radio_ctrl_vars);
    if (!compareSimple(u8, subset_ctrl_vars, superset_ctrl_vars, check_equal)) return false;

    return true;
}
fn compareRadioDetails(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    if (!compareSingleElement(u32, subset.radio_default_serial, superset.radio_default_serial, check_equal)) return false;
    if (!compareSingleElement(u8, subset.radio_scan_power_supported, superset.radio_scan_power_supported, check_equal)) return false;

    return true;
}

fn compareNvm(subset: *const c.AsphodelDeviceInfo_t, superset: *const c.AsphodelDeviceInfo_t, check_equal: bool) bool {
    const subset_nvm = toComparable(u8, @intFromBool(subset.nvm_size != 0), subset.nvm_size, subset.nvm);
    const superset_nvm = toComparable(u8, @intFromBool(superset.nvm_size != 0), superset.nvm_size, superset.nvm);
    if (!compareSimple(u8, subset_nvm, superset_nvm, check_equal)) return false;

    const subset_tags = toComparable(usize, @intFromBool(subset.nvm_size != 0), 6, &subset.tag_locations);
    const superset_tags = toComparable(usize, @intFromBool(superset.nvm_size != 0), 6, &superset.tag_locations);
    if (!compareSimple(usize, subset_tags, superset_tags, check_equal)) return false;

    return true;
}
