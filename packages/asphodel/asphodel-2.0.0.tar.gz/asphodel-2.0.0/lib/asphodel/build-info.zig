const std = @import("std");
const ctime = @cImport({
    @cInclude("time.h");
});

fn run_git(allocator: std.mem.Allocator, argv: []const []const u8) ![]const u8 {
    const res = try std.process.Child.run(.{ .allocator = allocator, .argv = argv });

    allocator.free(res.stderr); // ignore stderr
    defer allocator.free(res.stdout);

    switch (res.term) {
        .Exited => |c| if (c != 0) return error.failed,
        else => return error.failed,
    }

    const value = std.mem.trimRight(u8, res.stdout, "\r\n");
    return try allocator.dupe(u8, value);
}

fn get_build_info(allocator: std.mem.Allocator, suffix: []const u8) ![]const u8 {
    const branch = try run_git(allocator, &[_][]const u8{ "git", "rev-parse", "--abbrev-ref", "HEAD" });
    defer allocator.free(branch);

    const hash = try run_git(allocator, &[_][]const u8{ "git", "describe", "--match", "InvalidTag", "--long", "--always", "--dirty=-x", "--abbrev=10" });
    defer allocator.free(hash);

    if (std.mem.eql(u8, branch, "master")) {
        // master branch
        const tag = try run_git(allocator, &[_][]const u8{ "git", "describe", "--abbrev=0", "--tags" });
        defer allocator.free(tag);

        return try std.fmt.allocPrint(allocator, "{s}-{s}{s}", .{ tag, hash, suffix });
    } else if (std.mem.startsWith(u8, branch, "release")) {
        // release candidate branch
        const after = branch["release".len..];

        if (after.len == 0) {
            // invalid, pretend it's a dev build
            return try std.fmt.allocPrint(allocator, "dev-{s}{s}", .{ hash, suffix });
        } else {
            if (after[0] == '-' or after[0] == '/') {
                return try std.fmt.allocPrint(allocator, "{s}rc-{s}{s}", .{ after[1..], hash, suffix });
            } else {
                return try std.fmt.allocPrint(allocator, "{s}rc-{s}{s}", .{ after, hash, suffix });
            }
        }
    } else if (std.mem.eql(u8, branch, "HEAD")) {
        // detached head; probably in a submodule
        // see if we can find a release tag for this exact commit
        const possible_tag = run_git(allocator, &[_][]const u8{ "git", "describe", "--exact-match", "--tags", "--match", "[0-9].[0-9]*" });

        if (possible_tag) |tag| {
            // found a version tag, so use that
            defer allocator.free(tag);
            return try std.fmt.allocPrint(allocator, "{s}-{s}{s}", .{ tag, hash, suffix });
        } else |_| {
            // no tag, assume develop branch
            return try std.fmt.allocPrint(allocator, "dev-{s}{s}", .{ hash, suffix });
        }
    } else {
        // develop and others
        return try std.fmt.allocPrint(allocator, "dev-{s}{s}", .{ hash, suffix });
    }
}

pub fn main() !void {
    var general_purpose_allocator = std.heap.GeneralPurposeAllocator(.{}){};
    defer std.debug.assert(general_purpose_allocator.deinit() == .ok);
    const gpa = general_purpose_allocator.allocator();

    const args = try std.process.argsAlloc(gpa);
    defer std.process.argsFree(gpa, args);

    var opt_version_suffix: ?[]const u8 = null;
    var opt_output_file_path: ?[]const u8 = null;

    {
        var i: usize = 1;
        while (i < args.len) : (i += 1) {
            const arg = args[i];
            if (std.mem.eql(u8, arg, "--version-suffix")) {
                i += 1;
                if (i >= args.len) fatal("expected arg after '{s}'", .{arg});
                if (opt_version_suffix != null) fatal("duplicated {s} argument", .{arg});
                opt_version_suffix = args[i];
            } else if (std.mem.eql(u8, arg, "--output-file")) {
                i += 1;
                if (i >= args.len) fatal("expected arg after '{s}'", .{arg});
                if (opt_output_file_path != null) fatal("duplicated {s} argument", .{arg});
                opt_output_file_path = args[i];
            } else {
                fatal("unknown argument '{s}'", .{arg});
            }
        }
    }

    const version_suffix = opt_version_suffix orelse "";
    const output_file_path = opt_output_file_path orelse fatal("missing --output-file", .{});

    // UTC ISO-8601
    var now: ctime.time_t = ctime.time(null);
    const tm = ctime.gmtime(&now);
    var date_buf: [21]u8 = undefined; // "YYYY-MM-DDTHH:MM:SSZ" + '\0'
    const date_len = ctime.strftime(&date_buf[0], date_buf.len, "%Y-%m-%dT%H:%M:%SZ", tm);
    const build_date = date_buf[0..date_len];

    const build_info: ?[]const u8 = get_build_info(gpa, version_suffix) catch null;
    defer if (build_info) |s| gpa.free(s);

    var output_file = std.fs.cwd().createFile(output_file_path, .{}) catch |err| {
        fatal("unable to open '{s}': {s}", .{ output_file_path, @errorName(err) });
    };
    defer output_file.close();

    var buffer: [1024]u8 = undefined;
    var file_writer = output_file.writer(&buffer);
    const writer = &file_writer.interface;

    const fmt =
        \\#ifndef VERSION_AUTOGEN_H_
        \\#define VERSION_AUTOGEN_H_
        \\
        \\#define BUILD_INFO_STR "{s}"
        \\#define BUILD_DATE_STR "{s}"
        \\
        \\#endif /* VERSION_AUTOGEN_H_ */
        \\
    ;

    try writer.print(fmt, .{ build_info orelse "<UNKNOWN>", build_date });
    try writer.flush();
}

fn fatal(comptime format: []const u8, args: anytype) noreturn {
    std.debug.print(format, args);
    std.process.exit(1);
}
