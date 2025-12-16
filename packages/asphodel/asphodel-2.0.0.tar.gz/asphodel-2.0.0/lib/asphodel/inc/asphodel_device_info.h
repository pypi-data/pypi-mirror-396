/*
 * Copyright (c) 2025, Suprock Technologies
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#ifndef ASPHODEL_DEVICE_INFO_H_
#define ASPHODEL_DEVICE_INFO_H_

#include <stdint.h>
#include <stddef.h>
#include "asphodel_api.h"
#include "asphodel_ctrl_var.h"
#include "asphodel_device.h"
#include "asphodel_setting.h"
#include "asphodel_stream.h"
#include "asphodel_supply.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    // NOTE: these types directly match the types in asphodel_get_stream_rate_info()
    int available;
    int channel_index;
    int invert;
    float scale;
    float offset;
} AsphodelStreamRateInfo_t;

typedef struct {
    int error_code; // Return value from asphodel_check_supply()
    int32_t measurement; // only valid when error_code is ASPHODEL_SUCCESS
    uint8_t result; // only valid when error_code is ASPHODEL_SUCCESS
} AsphodelSupplyResult_t;

typedef struct AsphodelDeviceInfo_t {
    // all memory pointed to by this structure is owned by this structure and freed when free_device_info() is called.
    // It's semi-read only. Values may be changed at the whims of the user, but any pointers should not be modified.

    // free the memory used by this device info
    void (*free_device_info)(struct AsphodelDeviceInfo_t *device_info);

    // this information can be read from a device without any transfers
    const char *serial_number;
    const char *location_string;
    size_t max_incoming_param_length;
    size_t max_outgoing_param_length;
    size_t stream_packet_length;
    size_t remote_max_incoming_param_length; // only valid when supports_radio is true
    size_t remote_max_outgoing_param_length; // only valid when supports_radio is true
    size_t remote_stream_packet_length; // only valid when supports_radio is true
    uint8_t supports_bootloader; // boolean
    uint8_t supports_radio; // boolean
    uint8_t supports_remote; // boolean
    uint8_t supports_rf_power; // boolean

    // this information is required for correct caching
    const char *build_date;
    const char *build_info;
    const char *nvm_hash;
    uint8_t *nvm_modified; // pointer to boolean, null if not supported by device
    const char *setting_hash;
    const char *board_info_name;
    uint8_t board_info_rev;

    // disabled with ASPHODEL_NO_PROTOCOL_VERSION flag
    const char *protocol_version;

    // disabled with ASPHODEL_NO_CHIP_INFO flag
    const char *chip_family;
    const char *chip_id;
    const char *chip_model;

    // disabled with ASPHODEL_NO_BOOTLOADER_INFO flag
    const char *bootloader_info; // not cached

    // disabled with ASPHODEL_NO_RGB_OR_LED_INFO flag
    uint8_t rgb_count_known; // boolean: if 0, rgb_count is 0 but not actually known from device
    uint8_t led_count_known; // boolean: if 0, led_count is 0 but not actually known from device
    size_t rgb_count;
    size_t led_count;

    // disabled with ASPHODEL_NO_RGB_OR_LED_STATE or ASPHODEL_NO_RGB_OR_LED_INFO flag
    uint8_t (*rgb_settings)[3]; // not cached
    uint8_t *led_settings; // not cached

    // disabled with ASPHODEL_NO_REPO_DETAIL_INFO flag
    const char *commit_id; // if the device does not support this it will be "" instead of null
    const char *repo_branch; // if the device does not support this it will be "" instead of null
    const char *repo_name; // if the device does not support this it will be "" instead of null

    // disabled with ASPHODEL_NO_STREAM_INFO flag
    uint8_t stream_count_known; // boolean: if 0, stream_count, stream_filler_bits, stream_id_bits are 0 but not actually known from device
    uint8_t stream_filler_bits;
    uint8_t stream_id_bits;
    size_t stream_count;
    AsphodelStreamInfo_t *streams;

    // disabled with ASPHODEL_NO_STREAM_RATE_INFO or ASPHODEL_NO_STREAM_INFO flag
    AsphodelStreamRateInfo_t *stream_rates; // length set by stream_count

    // disabled with ASPHODEL_NO_CHANNEL_INFO flag
    uint8_t channel_count_known; // boolean: if 0, channel_count is 0 but not actually known from device
    size_t channel_count;
    AsphodelChannelInfo_t *channels;

    // disabled with ASPHODEL_NO_CHANNEL_CAL_INFO or ASPHODEL_NO_CHANNEL_INFO flag
    AsphodelChannelCalibration_t **channel_calibrations; // length set by channel_count

    // disabled with ASPHODEL_NO_SUPPLY_INFO flag
    uint8_t supply_count_known; // boolean: if 0, supply_count is 0 but not actually known from device
    size_t supply_count;
    AsphodelSupplyInfo_t *supplies;

    // disabled with ASPHODEL_NO_SUPPLY_RESULT or ASPHODEL_NO_SUPPLY_INFO flag
    AsphodelSupplyResult_t *supply_results; // not cached. length set by supply_count

    // disabled with ASPHODEL_NO_CTRL_VAR_INFO flag
    uint8_t ctrl_var_count_known; // boolean: if 0, ctrl_var_count is 0, but not actually known from device
    size_t ctrl_var_count;
    AsphodelCtrlVarInfo_t *ctrl_vars;

    // disabled with ASPHODEL_NO_CTRL_VAR_STATE or ASPHODEL_NO_CTRL_VAR_INFO flag
    int32_t *ctrl_var_states; // not cached

    // disabled with ASPHODEL_NO_SETTING_INFO flag
    uint8_t setting_count_known; // boolean: if 0, setting_count is 0, but not actually known from device
    size_t setting_count;
    AsphodelSettingInfo_t *settings;
    size_t custom_enum_count;
    uint8_t *custom_enum_lengths; // if this is null, then custom_enum_count is not known from the device
    const char ***custom_enum_values;

    // disabled with ASPHODEL_NO_SETTING_CATEGORY_INFO or ASPHODEL_NO_SETTING_INFO flag
    uint8_t setting_category_count_known; // boolean: if 0, setting_category_count is 0 but not actually known from device
    size_t setting_category_count;
    const char **setting_category_names;
    uint8_t *setting_category_settings_lengths;
    uint8_t **setting_category_settings;

    // disabled with ASPHODEL_NO_DEVICE_MODE flag
    uint8_t *supports_device_mode; // pointer to boolean, null if unknown

    // disabled with ASPHODEL_NO_DEVICE_MODE_STATE or ASPHODEL_NO_DEVICE_MODE flag
    uint8_t device_mode; // not cached

    // disabled with ASPHODEL_NO_RF_POWER_INFO flag
    uint8_t rf_power_ctrl_var_count_known; // boolean: if 0, rf_power_ctrl_var_count is 0 but not actually known from device
    size_t rf_power_ctrl_var_count;
    uint8_t *rf_power_ctrl_vars;

    // disabled with ASPHODEL_NO_RF_POWER_STATE flag
    uint8_t rf_power_enabled; // not cached. boolean

    // disabled with ASPHODEL_NO_RADIO_INFO flag
    uint8_t radio_ctrl_var_count_known; // boolean: if 0, radio_ctrl_var_count is 0 but not actually known from device
    size_t radio_ctrl_var_count;
    uint8_t *radio_ctrl_vars;
    uint32_t *radio_default_serial; // null if not fetched
    uint8_t *radio_scan_power_supported; // pointer to boolean, null if unknown

    // disabled with ASPHODEL_NVM_OPTIONAL flag
    size_t nvm_size; // if 0, nvm is not present
    const uint8_t *nvm;
    size_t tag_locations[6]; // will be all 0 if nvm is not present

    // disabled with ASPHODEL_NO_USER_TAG_INFO flag
    const char *user_tag_1;
    const char *user_tag_2;
} AsphodelDeviceInfo_t;

typedef struct AsphodelDeviceInfoCache_t AsphodelDeviceInfoCache_t;

// Return a file cache object that can be passed to asphodel_get_device_info(). This cache is backed by a SQLite
// database, and the same database file can be used simultaneously from multiple threads and processes. The cache object
// is also thread safe. The database file will be created if it does not exist.
//
// This cache is smart enough to handle NVM changes, firmware updates, and will always prioritize correct behavior.
//
// This cache object must be freed with asphodel_free_device_info_cache().
ASPHODEL_API int asphodel_get_device_info_file_cache(const char *path, AsphodelDeviceInfoCache_t **cache);

// Return a static cache object that can be passed to asphodel_get_device_info(). This cache is backed by a single
// JSON string, which is never modified, and can be used to create a seed for asphodel_get_device_info to work from.
// This should be used carefully to ensure that the JSON string came from the specific device (including specific
// firmware version, NVM state, etc) or is a carefully pruned string for the class of device. Otherwise the JSON values
// will replace the actual values reported from the device, which may cause unexpected behavior.
//
// The cache object is thread safe.
//
// This cache object will always return a result of "not found" for asphodel_get_cached_board_info().
//
// This cache object must be freed with asphodel_free_device_info_cache().
ASPHODEL_API int asphodel_get_device_info_static_cache(const char *json, AsphodelDeviceInfoCache_t **cache);

// Return a dynamic cache object that can be passed to asphodel_get_device_info(). This cache is meant to be used with
// a single device only, and this cache object is not thread safe. It saves any partial results for quicker loading of
// the device info after failures. The JSON string is optional, but if it's used then the same considerations apply as
// with the asphodel_get_device_info_static_cache() function.
//
// This cache type should not be used across NVM changes! If the device NVM is changed, the cache should be discarded.
//
// This cache object will always return a result of "not found" for asphodel_get_cached_board_info().
//
// This cache object must be freed with asphodel_free_device_info_cache().
ASPHODEL_API int asphodel_get_device_info_dynamic_cache(const char *json, AsphodelDeviceInfoCache_t **cache);

// For testing only: this will return the current state of a dynamic cache. The JSON string is still owned by the
// cache and the pointer and contents are only valid until the next cache operation.
ASPHODEL_API int asphodel_get_device_info_dynamic_cache_state(AsphodelDeviceInfoCache_t *cache, const char **json_out);

// Free a device info cache object created by asphodel_get_device_info_*_cache().
ASPHODEL_API void asphodel_free_device_info_cache(AsphodelDeviceInfoCache_t *cache);

#define ASPHODEL_NO_PROTOCOL_VERSION      (1u << 0)
#define ASPHODEL_NO_CHIP_INFO             (1u << 1)
#define ASPHODEL_NO_BOOTLOADER_INFO       (1u << 2)
#define ASPHODEL_NO_RGB_OR_LED_INFO       (1u << 3)
#define ASPHODEL_NO_RGB_OR_LED_STATE      (1u << 4) // is implied by ASPHODEL_NO_RGB_OR_LED_INFO
#define ASPHODEL_NO_REPO_DETAIL_INFO      (1u << 5)
#define ASPHODEL_NO_STREAM_INFO           (1u << 6)
#define ASPHODEL_NO_STREAM_RATE_INFO      (1u << 7) // is implied by ASPHODEL_NO_STREAM_INFO
#define ASPHODEL_NO_CHANNEL_INFO          (1u << 8)
#define ASPHODEL_NO_CHANNEL_CAL_INFO      (1u << 9) // is implied by ASPHODEL_NO_CHANNEL_INFO
#define ASPHODEL_NO_SUPPLY_INFO           (1u << 10)
#define ASPHODEL_NO_SUPPLY_RESULT         (1u << 11) // is implied by ASPHODEL_NO_SUPPLY_INFO
#define ASPHODEL_NO_CTRL_VAR_INFO         (1u << 12)
#define ASPHODEL_NO_CTRL_VAR_STATE        (1u << 13) // is implied by ASPHODEL_NO_CTRL_VAR_INFO
#define ASPHODEL_NO_SETTING_INFO          (1u << 14)
#define ASPHODEL_NO_SETTING_CATEGORY_INFO (1u << 15) // is implied by ASPHODEL_NO_SETTING_INFO
#define ASPHODEL_NO_DEVICE_MODE           (1u << 16)
#define ASPHODEL_NO_DEVICE_MODE_STATE     (1u << 17) // is implied by ASPHODEL_NO_DEVICE_MODE
#define ASPHODEL_NO_RF_POWER_INFO         (1u << 18)
#define ASPHODEL_NO_RF_POWER_STATE        (1u << 19) // is implied by ASPHODEL_NO_RF_POWER_INFO
#define ASPHODEL_NO_RADIO_INFO            (1u << 20)
#define ASPHODEL_NVM_OPTIONAL             (1u << 21) // will be less aggressive in fetching, but may still be fetched
#define ASPHODEL_NO_USER_TAG_INFO         (1u << 22)
#define ASPHODEL_NO_UNCACHED              (ASPHODEL_NO_RGB_OR_LED_STATE | ASPHODEL_NO_SUPPLY_RESULT | \
                                           ASPHODEL_NO_CTRL_VAR_STATE | ASPHODEL_NO_DEVICE_MODE_STATE | \
                                           ASPHODEL_NO_RF_POWER_STATE)

#define ASPHODEL_ACTIVE_SCAN_DEFAULT      0x3FFFFFu // bits 0-21. NOTE: does not exclude user tags (bit 22)

typedef void (*AsphodelDeviceInfoProgressCallback_t)(uint32_t finished, uint32_t total, const char *section_name, void *closure);

// Returns a device info structure by talking to the device. The cache parameter can be NULL, in which case the device
// will be queried for all information. If the cache parameter is not NULL, only the information that is missing will
// be queried from the device. Partial failures will have the cache populated with the acquired info, so incremental
// progress can be made.
//
// The callback, if provided, will be called periodically with a finished value that increases monotonically (but not
// necessarily in unit increments) toward the total. The total passed to successive callbacks will remain constant
// during the device_info call. The first callback may be issued with an arbitrary finished value. The final callback
// call will have finished equal to total, assuming no errors occurred. The callback will always be called from the
// same thread as the function call. The callback will be called at least once.
//
// The device_info structure must be freed with device_info->free_device_info(device_info).
ASPHODEL_API int asphodel_get_device_info(AsphodelDevice_t *device, AsphodelDeviceInfoCache_t *cache, uint32_t flags,
    AsphodelDeviceInfo_t **device_info, AsphodelDeviceInfoProgressCallback_t callback, void *closure);

// Query the cache for board info for a remote serial number. On success, found is set to 1 and rev/buffer are filled.
// On cache miss, found is set to 0 and rev/buffer are untouched.
ASPHODEL_API int asphodel_get_cached_board_info(AsphodelDeviceInfoCache_t *cache, uint32_t serial_number,
    uint8_t *found, uint8_t *rev, char *buffer, size_t buffer_size);

// Create a summary string for the device info. The string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_device_info_summary(const AsphodelDeviceInfo_t *device_info, const char **summary_out);

// Checks if two device infos have equal contents at all levels. Returns 1 if the two device infos are equal,
// 0 otherwise.
ASPHODEL_API uint8_t asphodel_device_info_equal(const AsphodelDeviceInfo_t *a,
    const AsphodelDeviceInfo_t *b);

// Checks if one device info is a subset of another. Returns 1 if the first device info is a subset of the second,
// 0 otherwise.
ASPHODEL_API uint8_t asphodel_device_info_is_subset(const AsphodelDeviceInfo_t *subset,
    const AsphodelDeviceInfo_t *superset);

#ifdef __cplusplus
}
#endif

#endif /* ASPHODEL_DEVICE_INFO_H_ */
