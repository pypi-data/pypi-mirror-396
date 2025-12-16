
from ctypes import POINTER, c_char_p, c_uint8, create_string_buffer

from .clib import AsphodelDeviceInfoCache, lib


class Cache:
    MAX_STRING_LENGTH = 128

    def __init__(self, cache: AsphodelDeviceInfoCache) -> None:
        self.cache = cache

    def __del__(self) -> None:
        cache = getattr(self, "cache", None)
        if cache:
            del self.cache
            lib.asphodel_free_device_info_cache(cache)

    @staticmethod
    def file_cache(path: str) -> "Cache":
        path_bytes = path.encode("utf-8")
        cache_ptr = POINTER(AsphodelDeviceInfoCache)()
        lib.asphodel_get_device_info_file_cache(path_bytes, cache_ptr)
        return Cache(cache_ptr.contents)

    @staticmethod
    def static_cache(json: str) -> "Cache":
        json_bytes = json.encode("utf-8")
        cache_ptr = POINTER(AsphodelDeviceInfoCache)()
        lib.asphodel_get_device_info_static_cache(json_bytes, cache_ptr)
        return Cache(cache_ptr.contents)

    @staticmethod
    def dynamic_cache(json: str | None = None) -> "Cache":
        json_bytes: bytes | None
        if json:
            json_bytes = json.encode("utf-8")
        else:
            json_bytes = None
        cache_ptr = POINTER(AsphodelDeviceInfoCache)()
        lib.asphodel_get_device_info_dynamic_cache(json_bytes, cache_ptr)
        return Cache(cache_ptr.contents)

    def get_dynamic_cache_state(self) -> str | None:
        out = c_char_p()
        lib.asphodel_get_device_info_dynamic_cache_state(self.cache, out)
        out_bytes = out.value
        if not out_bytes:
            return None
        return out_bytes.decode("utf-8")

    def get_board_info(self, serial_number: int) -> tuple[str, int] | None:
        found = c_uint8()
        rev = c_uint8()
        buffer = create_string_buffer(self.MAX_STRING_LENGTH)
        lib.asphodel_get_cached_board_info(
            self.cache, serial_number, found, rev, buffer, len(buffer))
        if (found.value == 0):
            return None
        else:
            return (buffer.value.decode("utf-8"), rev.value)
