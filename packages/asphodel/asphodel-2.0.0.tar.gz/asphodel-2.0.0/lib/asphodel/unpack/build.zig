const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});

    const static = b.option(bool, "static", "Build a static library instead of shared") orelse false;

    const default_lib_name = if (static) "unpack" else switch (target.result.os.tag) {
        .windows => switch (target.result.ptrBitWidth()) {
            64 => "Unpack64",
            32 => "Unpack32",
            else => "unpack",
        },
        else => "unpack",
    };

    const lib_name: []const u8 = b.option([]const u8, "name", "Library output name") orelse default_lib_name;

    const linkage: std.builtin.LinkMode = if (static) .static else .dynamic;

    const lib_mod = b.createModule(.{
        .target = target,
        .optimize = .ReleaseFast,
        .pic = true,
    });

    const lib = b.addLibrary(.{
        .linkage = linkage,
        .name = lib_name,
        .root_module = lib_mod,
    });

    const c_flags = &[_][]const u8{
        "-Wno-unused-parameter",
        "-Wall",
        "-Wextra",
    };

    lib.addCSourceFiles(.{
        .root = b.path("src"),
        .files = &.{
            "unpack_id.c",
            "unpack.c",
            "unwrap.c",
        },
        .flags = c_flags,
    });

    inline for (0..33) |i| {
        lib.addCSourceFile(.{
            .file = b.path(b.fmt("src/unpack{}.c", .{i})),
            .flags = c_flags,
        });
    }

    lib.addIncludePath(b.path("inc"));
    if (static) {
        lib.root_module.addCMacro("UNPACK_STATIC_LIB", "");
    }
    lib.root_module.addCMacro("UNPACK_API_EXPORTS", "");
    lib.linkLibC();

    lib.installHeadersDirectory(b.path("inc"), "", .{});

    b.installArtifact(lib);
}
