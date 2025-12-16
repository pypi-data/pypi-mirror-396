const std = @import("std");
const c = @import("root.zig").c;
const json = @import("root.zig").json;
const sqlite3 = @import("root.zig").sqlite3;
const Allocator = std.mem.Allocator;

pub export fn asphodel_get_device_info_file_cache(path: [*:0]const u8, cache_out: *?*Cache) c_int {
    const cache = std.heap.c_allocator.create(Cache) catch return c.ASPHODEL_NO_MEM;

    var db: ?*sqlite3.sqlite3 = null;
    const ret = sqlite3.sqlite3_open_v2(
        path,
        &db,
        sqlite3.SQLITE_OPEN_READWRITE | sqlite3.SQLITE_OPEN_CREATE | sqlite3.SQLITE_OPEN_FULLMUTEX,
        null,
    );
    if (ret != sqlite3.SQLITE_OK or db == null) {
        std.heap.c_allocator.destroy(cache);
        _ = sqlite3.sqlite3_close(db); // ok if db is null
        return c.ASPHODEL_BAD_PARAMETER;
    }

    initDb(db.?) catch {
        std.heap.c_allocator.destroy(cache);
        _ = sqlite3.sqlite3_close(db);
        return c.ASPHODEL_ERROR_IO;
    };

    cache.* = .{ .file = db.? };
    cache_out.* = cache;

    return c.ASPHODEL_SUCCESS;
}

pub export fn asphodel_get_device_info_static_cache(json_in: [*:0]const u8, cache_out: *?*Cache) c_int {
    const cache = std.heap.c_allocator.create(Cache) catch return c.ASPHODEL_NO_MEM;
    const json_copy = std.heap.c_allocator.dupe(u8, std.mem.span(json_in)) catch {
        std.heap.c_allocator.destroy(cache);
        return c.ASPHODEL_NO_MEM;
    };

    cache.* = .{ .static = json_copy };
    cache_out.* = cache;

    return c.ASPHODEL_SUCCESS;
}

pub export fn asphodel_get_device_info_dynamic_cache(json_in: ?[*:0]const u8, cache_out: *?*Cache) c_int {
    const cache = std.heap.c_allocator.create(Cache) catch return c.ASPHODEL_NO_MEM;

    var json_copy: ?[*:0]const u8 = null;
    if (json_in) |s| {
        json_copy = std.heap.c_allocator.dupeZ(u8, std.mem.span(s)) catch {
            std.heap.c_allocator.destroy(cache);
            return c.ASPHODEL_NO_MEM;
        };
    }

    cache.* = .{ .dynamic = json_copy };
    cache_out.* = cache;

    return c.ASPHODEL_SUCCESS;
}

pub export fn asphodel_get_device_info_dynamic_cache_state(cache: *Cache, json_out: *?[*:0]const u8) c_int {
    switch (cache.*) {
        .file, .static => return c.ASPHODEL_BAD_PARAMETER,
        .dynamic => |opt_s| {
            json_out.* = opt_s;
            return c.ASPHODEL_SUCCESS;
        },
    }
}

pub export fn asphodel_free_device_info_cache(cache: *Cache) void {
    switch (cache.*) {
        .file => |db| {
            _ = sqlite3.sqlite3_close(db);
        },
        .static => |s| {
            std.heap.c_allocator.free(s);
        },
        .dynamic => |opt_s| {
            if (opt_s) |s| {
                std.heap.c_allocator.free(std.mem.span(s));
            }
        },
    }

    std.heap.c_allocator.destroy(cache);
}

pub export fn asphodel_get_cached_board_info(cache: *Cache, serial_number: u32, found: *u8, rev: ?*u8, buffer: ?[*:0]u8, buffer_size: usize) c_int {
    if (buffer != null and buffer_size < 1) return c.ASPHODEL_BAD_PARAMETER;

    switch (cache.*) {
        .file => |db| {
            const maybe_board_info = readBoardInfo(std.heap.c_allocator, db, serial_number) catch null;
            if (maybe_board_info) |board_info| {
                if (buffer) |buffer_out| {
                    const write_size = @min(buffer_size - 1, board_info.board_info_name.len);
                    @memcpy(buffer_out[0..write_size], board_info.board_info_name[0..write_size]);
                    buffer_out[write_size] = 0;
                }
                std.heap.c_allocator.free(board_info.board_info_name);

                if (rev) |rev_out| {
                    rev_out.* = board_info.board_info_rev;
                }

                found.* = 1;
                return c.ASPHODEL_SUCCESS;
            } else {
                found.* = 0;
                return c.ASPHODEL_SUCCESS;
            }
        },
        .static, .dynamic => {
            found.* = 0;
            return c.ASPHODEL_SUCCESS;
        },
    }
}

pub const Cache = union(enum) {
    file: *sqlite3.sqlite3,
    static: []const u8,
    dynamic: ?[*:0]const u8,

    pub fn fill(self: Cache, allocator: Allocator, device_info: *c.AsphodelDeviceInfo_t) !void {
        // save these values, as they've been fetched already, and the cache shouldn't overwrite them no matter what
        const build_date = device_info.build_date;
        const build_info = device_info.build_info;
        const nvm_hash = device_info.nvm_hash;
        const setting_hash = device_info.setting_hash;
        const board_info_rev = device_info.board_info_rev;
        const board_info_name = device_info.board_info_name;
        const nvm_modified = device_info.nvm_modified;
        defer {
            device_info.build_date = build_date;
            device_info.build_info = build_info;
            device_info.nvm_hash = nvm_hash;
            device_info.setting_hash = setting_hash;
            device_info.board_info_rev = board_info_rev;
            device_info.board_info_name = board_info_name;
            device_info.nvm_modified = nvm_modified;
        }

        switch (self) {
            .file => |db| {
                const setting_key = SettingKey.fromDeviceInfo(device_info);
                if (setting_key) |key| {
                    const maybe_json: ?[]const u8 = readSetting(allocator, db, key) catch null;
                    if (maybe_json) |s| {
                        try json.fillDeviceInfoFromJson(allocator, s, device_info, null);
                    }
                }

                const nvm_key = NvmKey.fromDeviceInfo(device_info);
                if (nvm_key) |key| {
                    const nvm: ?[]const u8 = readNvm(allocator, db, key) catch null;
                    if (nvm) |nvm_bytes| {
                        device_info.nvm_size = nvm_bytes.len;
                        device_info.nvm = nvm_bytes.ptr;
                    }
                }
            },
            .static => |s| {
                try json.fillDeviceInfoFromJson(allocator, s, device_info, null);
            },
            .dynamic => |opt_s| {
                if (opt_s) |s| {
                    try json.fillDeviceInfoFromJson(allocator, std.mem.span(s), device_info, null);
                }
            },
        }
    }

    pub fn save(self: *Cache, device_info: *const c.AsphodelDeviceInfo_t) !void {
        switch (self.*) {
            .file => |db| {
                const setting_key = SettingKey.fromDeviceInfo(device_info);
                if (setting_key) |key| {
                    var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
                    defer arena.deinit();
                    const json_out = try json.createJsonFromDeviceInfo(arena.allocator(), device_info, .{
                        .include_version = false,
                        .exclude_nvm = true,
                    });
                    writeSetting(db, key, json_out) catch {}; // ignore any errors
                }

                if (device_info.nvm_size != 0) {
                    const nvm_key = NvmKey.fromDeviceInfo(device_info);
                    if (nvm_key) |key| {
                        if (device_info.nvm) |nvm| {
                            writeNvm(db, key, nvm[0..device_info.nvm_size]) catch {}; // ignore any errors
                        }
                    }
                }

                const maybe_serial_number = parseSerialNumber(std.mem.span(device_info.serial_number));
                if (maybe_serial_number) |serial_number| {
                    writeBoardInfo(db, serial_number, device_info.board_info_name, device_info.board_info_rev) catch {}; // ignore any errors
                }
            },
            .static => {}, // nothing to do
            .dynamic => |old| {
                var arena = std.heap.ArenaAllocator.init(std.heap.raw_c_allocator);
                defer arena.deinit();
                const new_str = try json.createJsonFromDeviceInfo(arena.allocator(), device_info, .{ .include_version = false });
                const duplicate = try std.heap.c_allocator.dupeZ(u8, new_str);

                if (old) |old_str| {
                    std.heap.c_allocator.free(std.mem.span(old_str));
                }

                self.* = .{ .dynamic = duplicate.ptr };
            },
        }
    }
};

fn parseSerialNumber(serial_number: []const u8) ?u32 {
    var i: usize = 0;

    // skip any leading non-digits
    while (i < serial_number.len and !std.ascii.isDigit(serial_number[i])) : (i += 1) {}

    const start = i;

    // skip the digits

    while (i < serial_number.len and std.ascii.isDigit(serial_number[i])) : (i += 1) {}

    return std.fmt.parseUnsigned(u32, serial_number[start..i], 10) catch return null;
}

fn initDb(db: *sqlite3.sqlite3) !void {
    var result: c_int = undefined;

    const init_sql =
        \\PRAGMA journal_mode = WAL;
        \\PRAGMA synchronous = NORMAL;
        \\PRAGMA busy_timeout = 250;
    ;

    result = sqlite3.sqlite3_exec(db, init_sql.ptr, null, null, null);
    if (result != sqlite3.SQLITE_OK) {
        return error.FailedToInitDb;
    }

    result = sqlite3.sqlite3_exec(db, "BEGIN IMMEDIATE;", null, null, null);
    if (result != sqlite3.SQLITE_OK) {
        return error.FailedToInitDb;
    }

    errdefer _ = sqlite3.sqlite3_exec(db, "ROLLBACK;", null, null, null);

    // get the user version
    var user_version_statement: ?*sqlite3.sqlite3_stmt = null;
    result = sqlite3.sqlite3_prepare_v2(db, "PRAGMA user_version;", -1, &user_version_statement, null);
    defer _ = sqlite3.sqlite3_finalize(user_version_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK or user_version_statement == null) {
        return error.FailedToInitDb;
    }
    result = sqlite3.sqlite3_step(user_version_statement);
    if (result != sqlite3.SQLITE_ROW) {
        return error.FailedToInitDb;
    }
    const user_version = sqlite3.sqlite3_column_int(user_version_statement, 0);

    if (user_version == 0) {
        // fresh db, needs to create tables
        const create_tables_sql =
            \\CREATE TABLE IF NOT EXISTS settings (
            \\  setting_hash TEXT NOT NULL,
            \\  build_info TEXT NOT NULL,
            \\  build_date TEXT NOT NULL,
            \\  board_info_name TEXT NOT NULL,
            \\  board_info_rev INTEGER NOT NULL,
            \\  value_json TEXT NOT NULL,
            \\  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
            \\  last_access_at INTEGER,
            \\  PRIMARY KEY (setting_hash, build_info, build_date, board_info_name, board_info_rev)
            \\) STRICT, WITHOUT ROWID;
            \\
            \\CREATE TABLE IF NOT EXISTS nvm (
            \\  nvm_hash TEXT NOT NULL,
            \\  board_info_name TEXT NOT NULL,
            \\  board_info_rev INTEGER NOT NULL,
            \\  value_blob BLOB NOT NULL,
            \\  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
            \\  last_access_at INTEGER,
            \\  PRIMARY KEY (nvm_hash, board_info_name, board_info_rev)
            \\) STRICT, WITHOUT ROWID;
            \\
            \\CREATE TABLE IF NOT EXISTS board_info (
            \\  serial_number INTEGER NOT NULL,
            \\  board_info_name TEXT NOT NULL,
            \\  board_info_rev INTEGER NOT NULL,
            \\  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
            \\  last_access_at INTEGER,
            \\  PRIMARY KEY (serial_number)
            \\) STRICT, WITHOUT ROWID;
            \\
            \\PRAGMA user_version = 1;
        ;

        result = sqlite3.sqlite3_exec(db, create_tables_sql.ptr, null, null, null);
        if (result != sqlite3.SQLITE_OK) {
            return error.FailedToInitDb;
        }
    } else {
        // carry on
    }

    result = sqlite3.sqlite3_exec(db, "COMMIT;", null, null, null);
    if (result != sqlite3.SQLITE_OK) {
        return error.FailedToInitDb;
    }
}

const SettingKey = struct {
    setting_hash: [*:0]const u8,
    build_info: [*:0]const u8,
    build_date: [*:0]const u8,
    board_info_name: [*:0]const u8,
    board_info_rev: u8,

    fn fromDeviceInfo(device_info: *const c.AsphodelDeviceInfo_t) ?SettingKey {
        if (device_info.setting_hash == null) return null; // device is too old to support this command
        return SettingKey{
            .setting_hash = device_info.setting_hash,
            .build_info = device_info.build_info,
            .build_date = device_info.build_date,
            .board_info_name = device_info.board_info_name,
            .board_info_rev = device_info.board_info_rev,
        };
    }
};

fn readSetting(allocator: Allocator, db: *sqlite3.sqlite3, setting_key: SettingKey) !?[]const u8 {
    const select_sql =
        \\SELECT value_json
        \\FROM settings
        \\WHERE setting_hash=? AND build_info=? AND build_date=? AND board_info_name=? AND board_info_rev=?
    ;

    const update_sql =
        \\UPDATE settings
        \\SET last_access_at=unixepoch()
        \\WHERE setting_hash=? AND build_info=? AND build_date=? AND board_info_name=? AND board_info_rev=?
    ;

    var select_statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, select_sql, -1, &select_statement, null);
    defer _ = sqlite3.sqlite3_finalize(select_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(select_statement, 1, setting_key.setting_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(select_statement, 2, setting_key.build_info, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(select_statement, 3, setting_key.build_date, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(select_statement, 4, setting_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(select_statement, 5, setting_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;

    var update_statement: ?*sqlite3.sqlite3_stmt = null;
    result = sqlite3.sqlite3_prepare_v2(db, update_sql, -1, &update_statement, null);
    defer _ = sqlite3.sqlite3_finalize(update_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(update_statement, 1, setting_key.setting_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(update_statement, 2, setting_key.build_info, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(update_statement, 3, setting_key.build_date, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(update_statement, 4, setting_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(update_statement, 5, setting_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(select_statement);
    if (result == sqlite3.SQLITE_DONE) return null; // not found
    if (result != sqlite3.SQLITE_ROW) return error.FailedToExecuteStatement;

    const text: [*]const u8 = @ptrCast(sqlite3.sqlite3_column_text(select_statement, 0));
    const text_len: usize = @intCast(sqlite3.sqlite3_column_bytes(select_statement, 0));
    const json_str = try allocator.dupeZ(u8, text[0..text_len]);

    _ = sqlite3.sqlite3_step(update_statement); // ignore any errors on the update

    return json_str;
}

fn writeSetting(db: *sqlite3.sqlite3, setting_key: SettingKey, value: [:0]const u8) !void {
    const sql =
        \\INSERT INTO settings(
        \\  setting_hash, build_info, build_date, board_info_name, board_info_rev,
        \\  value_json, last_access_at
        \\) VALUES (?,?,?,?,?,?,unixepoch())
        \\ON CONFLICT(setting_hash, build_info, build_date, board_info_name, board_info_rev)
        \\DO UPDATE SET
        \\  value_json=excluded.value_json,
        \\  last_access_at=unixepoch();
    ;

    var statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, sql, -1, &statement, null);
    defer _ = sqlite3.sqlite3_finalize(statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(statement, 1, setting_key.setting_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 2, setting_key.build_info, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 3, setting_key.build_date, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 4, setting_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(statement, 5, setting_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 6, value, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(statement);
    if (result != sqlite3.SQLITE_DONE) return error.FailedToExecuteStatement;
}

const NvmKey = struct {
    nvm_hash: [*:0]const u8,
    board_info_name: [*:0]const u8,
    board_info_rev: u8,

    fn fromDeviceInfo(device_info: *const c.AsphodelDeviceInfo_t) ?NvmKey {
        if (device_info.nvm_hash == null) return null; // device is too old to support this command
        if (device_info.nvm_modified == null) return null; // can't tell if the NVM is valid
        if (device_info.nvm_modified.* != 0) return null; // NVM has been modified
        return NvmKey{
            .nvm_hash = device_info.nvm_hash,
            .board_info_name = device_info.board_info_name,
            .board_info_rev = device_info.board_info_rev,
        };
    }
};

fn readNvm(allocator: Allocator, db: *sqlite3.sqlite3, nvm_key: NvmKey) !?[]const u8 {
    const select_sql =
        \\SELECT value_blob
        \\FROM nvm
        \\WHERE nvm_hash=? AND board_info_name=? AND board_info_rev=?
    ;

    const update_sql =
        \\UPDATE nvm
        \\SET last_access_at=unixepoch()
        \\WHERE nvm_hash=? AND board_info_name=? AND board_info_rev=?
    ;

    var select_statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, select_sql, -1, &select_statement, null);
    defer _ = sqlite3.sqlite3_finalize(select_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(select_statement, 1, nvm_key.nvm_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(select_statement, 2, nvm_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(select_statement, 3, nvm_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;

    var update_statement: ?*sqlite3.sqlite3_stmt = null;
    result = sqlite3.sqlite3_prepare_v2(db, update_sql, -1, &update_statement, null);
    defer _ = sqlite3.sqlite3_finalize(update_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(update_statement, 1, nvm_key.nvm_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(update_statement, 2, nvm_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(update_statement, 3, nvm_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(select_statement);
    if (result == sqlite3.SQLITE_DONE) return null; // not found
    if (result != sqlite3.SQLITE_ROW) return error.FailedToExecuteStatement;

    const blob: [*]const u8 = @ptrCast(sqlite3.sqlite3_column_blob(select_statement, 0));
    const blob_len: usize = @intCast(sqlite3.sqlite3_column_bytes(select_statement, 0));
    const nvm = try allocator.dupe(u8, blob[0..blob_len]);

    _ = sqlite3.sqlite3_step(update_statement); // ignore any errors on the update

    return nvm;
}

fn writeNvm(db: *sqlite3.sqlite3, nvm_key: NvmKey, value: []const u8) !void {
    const sql =
        \\INSERT INTO nvm(
        \\  nvm_hash, board_info_name, board_info_rev, value_blob, last_access_at
        \\) VALUES (?,?,?,?,unixepoch())
        \\ON CONFLICT(nvm_hash, board_info_name, board_info_rev)
        \\DO UPDATE SET
        \\  value_blob=excluded.value_blob,
        \\  last_access_at=unixepoch();
    ;

    var statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, sql, -1, &statement, null);
    defer _ = sqlite3.sqlite3_finalize(statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_text(statement, 1, nvm_key.nvm_hash, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 2, nvm_key.board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(statement, 3, nvm_key.board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_blob(statement, 4, value.ptr, @intCast(value.len), sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(statement);
    if (result != sqlite3.SQLITE_DONE) return error.FailedToExecuteStatement;
}

const BoardInfo = struct {
    board_info_name: []const u8,
    board_info_rev: u8,
};

fn readBoardInfo(allocator: Allocator, db: *sqlite3.sqlite3, serial_number: u32) !?BoardInfo {
    const select_sql =
        \\SELECT board_info_name, board_info_rev
        \\FROM board_info
        \\WHERE serial_number=?
    ;

    const update_sql =
        \\UPDATE board_info
        \\SET last_access_at=unixepoch()
        \\WHERE serial_number=?
    ;

    var select_statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, select_sql, -1, &select_statement, null);
    defer _ = sqlite3.sqlite3_finalize(select_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_int64(select_statement, 1, serial_number) != sqlite3.SQLITE_OK) return error.FailedToBind;

    var update_statement: ?*sqlite3.sqlite3_stmt = null;
    result = sqlite3.sqlite3_prepare_v2(db, update_sql, -1, &update_statement, null);
    defer _ = sqlite3.sqlite3_finalize(update_statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_int64(update_statement, 1, serial_number) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(select_statement);
    if (result == sqlite3.SQLITE_DONE) return null; // not found
    if (result != sqlite3.SQLITE_ROW) return error.FailedToExecuteStatement;

    const text: [*]const u8 = @ptrCast(sqlite3.sqlite3_column_text(select_statement, 0));
    const text_len: usize = @intCast(sqlite3.sqlite3_column_bytes(select_statement, 0));
    const name = try allocator.dupe(u8, text[0..text_len]);
    const rev = std.math.cast(u8, sqlite3.sqlite3_column_int(select_statement, 1)) orelse return error.BadValue;

    _ = sqlite3.sqlite3_step(update_statement); // ignore any errors on the update

    return .{ .board_info_name = name, .board_info_rev = rev };
}

fn writeBoardInfo(db: *sqlite3.sqlite3, serial_number: u32, board_info_name: [*:0]const u8, board_info_rev: u8) !void {
    const sql =
        \\INSERT INTO board_info(
        \\  serial_number, board_info_name, board_info_rev, last_access_at
        \\) VALUES (?,?,?,unixepoch())
        \\ON CONFLICT(serial_number) DO UPDATE SET
        \\  board_info_name=excluded.board_info_name,
        \\  board_info_rev=excluded.board_info_rev,
        \\  last_access_at=unixepoch();
    ;

    var statement: ?*sqlite3.sqlite3_stmt = null;
    var result = sqlite3.sqlite3_prepare_v2(db, sql, -1, &statement, null);
    defer _ = sqlite3.sqlite3_finalize(statement); // register cleanup before the error check
    if (result != sqlite3.SQLITE_OK) return error.FailedToPrepareStatement;

    if (sqlite3.sqlite3_bind_int64(statement, 1, serial_number) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_text(statement, 2, board_info_name, -1, sqlite3.SQLITE_TRANSIENT) != sqlite3.SQLITE_OK) return error.FailedToBind;
    if (sqlite3.sqlite3_bind_int(statement, 3, board_info_rev) != sqlite3.SQLITE_OK) return error.FailedToBind;

    result = sqlite3.sqlite3_step(statement);
    if (result != sqlite3.SQLITE_DONE) return error.FailedToExecuteStatement;
}
