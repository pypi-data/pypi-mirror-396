const std = @import("std");

// Although this function looks imperative, note that its job is to
// declaratively construct a build graph that will be executed by an external
// runner.
pub fn build(b: *std.Build) !void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const static = b.option(bool, "static", "Build a static library instead of shared") orelse false;
    const disable_usb = b.option(bool, "disable_usb", "Support USB devices (requires libusb)") orelse false;
    const disable_tcp = b.option(bool, "disable_tcp", "Support TCP devices") orelse false;
    const build_examples = b.option(bool, "build_examples", "Support TCP devices") orelse true;
    const version_suffix: ?[]const u8 = b.option([]const u8, "version_suffix", "CI suffix (optional)");
    const skip_version_autogen = b.option(bool, "skip_version_autogen", "Skip version_autogen.h creation") orelse false;

    const lib_name: []const u8 = b.option([]const u8, "name", "Library output name") orelse "asphodel";

    const linkage: std.builtin.LinkMode = if (static) .static else .dynamic;

    // This creates a "module", which represents a collection of source files alongside
    // some compilation options, such as optimization mode and linked system libraries.
    // Every executable or library we compile will be based on one or more modules.
    const lib_mod = b.createModule(.{
        .target = target,
        .optimize = optimize,
        .pic = true,
        .root_source_file = b.path("src/root.zig"),
    });

    // Now, we will create a static library based on the module we created above.
    // This creates a `std.Build.Step.Compile`, which is the build step responsible
    // for actually invoking the compiler.
    const lib = b.addLibrary(.{
        .linkage = linkage,
        .name = lib_name,
        .root_module = lib_mod,
    });

    var c_flags: std.ArrayList([]const u8) = .empty;
    defer c_flags.deinit(b.allocator);
    try c_flags.appendSlice(b.allocator, &.{
        "-Wno-unused-parameter",
        "-Wall",
        "-Wextra",
    });
    if (optimize == .Debug) try c_flags.append(b.allocator, "-Werror");

    lib.root_module.addCSourceFiles(.{
        .root = b.path("src"),
        .files = &.{
            "asphodel_api.c",
            "asphodel_decode.c",
            "asphodel_device.c",
            "asphodel_device_type.c",
            "asphodel_unit_format.c",
            "asphodel_usb.c",
            "asphodel_tcp.c",
            "asphodel_version.c",
            "clock.c",
        },
        .flags = c_flags.items,
    });

    lib.root_module.addIncludePath(b.path("inc"));

    // add sqlite3 library
    lib.root_module.addCSourceFile(.{
        .file = b.path("sqlite3/sqlite3.c"),
        .flags = &.{
            "-DSQLITE_THREADSAFE=1",
            "-DSQLITE_OMIT_LOAD_EXTENSION",
            "-DSQLITE_OMIT_DEPRECATED",
            "-DSQLITE_DEFAULT_WAL_SYNCHRONOUS=1",
            "-DSQLITE_API=__attribute__((visibility(\"hidden\")))",
            "-fvisibility=hidden",
        },
    });
    lib.root_module.addIncludePath(b.path("sqlite3"));
    lib.root_module.addAnonymousImport("sqlite3", .{
        .root_source_file = b.path("sqlite3/sqlite3_header.zig"),
    });

    const build_info_tool = b.addExecutable(.{
        .name = "build-info",
        .root_module = b.createModule(.{
            .root_source_file = b.path("build-info.zig"),
            .target = b.graph.host,
            .link_libc = true,
        }),
    });

    const build_info_step = b.addRunArtifact(build_info_tool);
    build_info_step.has_side_effects = true; // get it to always rerun to update the timestamp
    if (version_suffix) |suffix| {
        build_info_step.addArg("--version-suffix");
        build_info_step.addArg(suffix);
    }
    build_info_step.addArg("--output-file");
    const version_autogen_h = build_info_step.addOutputFileArg("version_autogen.h");

    if (!skip_version_autogen) {
        lib.root_module.addIncludePath(version_autogen_h.dirname());
        lib.step.dependOn(&build_info_step.step);
    }

    const version_step = b.step("version_autogen", "Create version_autogen.h for reproducible build");
    version_step.dependOn(&b.addInstallFileWithDir(version_autogen_h, .prefix, "version_autogen.h").step);

    // add unpack library
    const unpack = b.dependency("unpack", .{
        .target = target,
        .static = true,
        .name = @as([]const u8, "unpack"),
    });
    lib.root_module.linkLibrary(unpack.artifact("unpack"));
    lib.root_module.addCMacro("UNPACK_STATIC_LIB", "");

    if (static) {
        lib.root_module.addCMacro("ASPHODEL_STATIC_LIB", "");
    }

    if (!disable_usb) {
        lib.root_module.addCMacro("ASPHODEL_USB_DEVICE", "");

        const libusb = b.dependency("libusb", .{
            .target = target,
            .optimize = .ReleaseFast,
            .@"system-libudev" = false,
        });
        const libusb_lib = libusb.artifact("usb");
        lib.root_module.linkLibrary(libusb_lib);

        // https://github.com/ziglang/zig/issues/24024
        if (target.result.os.tag.isDarwin()) {
            if (target.result.os.tag.isDarwin()) {
                const apple_sdk = @import("apple_sdk");
                try apple_sdk.addPaths(b, libusb_lib);
                try apple_sdk.addPaths(b, lib);
            }
        }
    }

    if (!disable_tcp) {
        lib.root_module.addCMacro("ASPHODEL_TCP_DEVICE", "");
        if (target.result.os.tag == .windows) {
            lib.root_module.linkSystemLibrary("ws2_32", .{});
            lib.root_module.linkSystemLibrary("iphlpapi", .{});
        }

        if (target.result.os.tag == .linux and optimize == .ReleaseSafe) {
            if (target.result.abi.isGnu()) {
                // Zig 0.15.1 has a bug when linking against glibc older than 2.42 in ReleaseSafe mode.
                // Undefined symbol __inet_pton_chk from using inet_pton() in asphodel_tcp.c.
                // This bug is fixed in Zig 0.15.2.
                // https://github.com/ziglang/zig/issues/24945
                const glibc_version = target.result.os.version_range.linux.glibc;
                if (glibc_version.major <= 2 and glibc_version.minor < 42) {
                    const zig_0151 = comptime std.SemanticVersion.parse("0.15.1") catch unreachable;
                    if (comptime @import("builtin").zig_version.order(zig_0151) != .gt) {
                        lib.root_module.addCMacro("_FORTIFY_SOURCE", "0");
                    }
                }
            }
        }
    }

    lib.root_module.addCMacro("ASPHODEL_API_EXPORTS", "");
    lib.setVersionScript(b.path("libasphodel.map"));

    if (target.result.os.tag != .windows and target.result.os.tag != .macos) {
        // add pthread library to non-windows non-mac systems
        lib.root_module.linkSystemLibrary("pthread", .{});
    }

    if (target.result.os.tag != .windows) {
        lib.root_module.linkSystemLibrary("m", .{});
    }

    lib.root_module.link_libc = true;

    // This declares intent for the library to be installed into the standard
    // location when the user invokes the "install" step (the default step when
    // running `zig build`).
    b.installArtifact(lib);

    // Creates a step for unit testing. This only builds the test executable
    // but does not run it.
    const lib_unit_tests = b.addTest(.{
        .root_module = lib_mod,
    });

    const run_lib_unit_tests = b.addRunArtifact(lib_unit_tests);

    // Similar to creating the run step earlier, this exposes a `test` step to
    // the `zig build --help` menu, providing a way for the user to request
    // running the unit tests.
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_lib_unit_tests.step);

    if (build_examples) {
        const json_parse = b.addExecutable(.{
            .name = "json_parse",
            .root_module = b.createModule(.{
                .root_source_file = b.path("examples/json_parse/json_parse.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        json_parse.root_module.addImport("asphodel", lib_mod);
        b.installArtifact(json_parse);

        const get_device_info = b.addExecutable(.{
            .name = "get_device_info",
            .root_module = b.createModule(.{
                .root_source_file = b.path("examples/get_device_info/get_device_info.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        get_device_info.root_module.addImport("asphodel", lib_mod);
        b.installArtifact(get_device_info);

        const virtual_device_test = b.addExecutable(.{
            .name = "virtual_device_test",
            .root_module = b.createModule(.{
                .root_source_file = b.path("examples/virtual_device_test/virtual_device_test.zig"),
                .target = target,
                .optimize = optimize,
            }),
        });
        virtual_device_test.root_module.addImport("asphodel", lib_mod);
        b.installArtifact(virtual_device_test);
    }
}
