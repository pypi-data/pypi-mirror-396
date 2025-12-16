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

#ifndef ASPHODEL_JSON_H_
#define ASPHODEL_JSON_H_

#include <stdint.h>
#include <stddef.h>
#include "asphodel_api.h"
#include "asphodel_device_info.h"
#include "asphodel_setting.h"
#include "asphodel_stream.h"

#ifdef __cplusplus
extern "C" {
#endif

// Convert a JSON string into a device info structure. The device_info structure must be freed with
// device_info->free_device_info(device_info).
//
// If excess_out is not NULL, it will be filled with a pointer to a string containing excess values (if any) in a JSON
// object. No excess items returns a "{}". The string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_device_info_from_json(const char *json, AsphodelDeviceInfo_t **device_info_out,
    const char **excess_out);

// Convert a device info structure into a JSON string. The JSON string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_json_from_device_info(const AsphodelDeviceInfo_t *device_info, const char **json_out);


// Converts a JSON string into a stream info. The struct must be freed with asphodel_free_json_stream().
ASPHODEL_API int asphodel_get_stream_info_from_json(const char *json, AsphodelStreamInfo_t **stream_info_out);
ASPHODEL_API void asphodel_free_json_stream(AsphodelStreamInfo_t *stream_info); // structs created from JSON only

// Converts a stream info into a JSON string. The JSON string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_json_from_stream_info(const AsphodelStreamInfo_t *stream_info, const char **json_out);


// Converts a JSON string into a channel info. The struct must be freed with asphodel_free_json_channel().
ASPHODEL_API int asphodel_get_channel_info_from_json(const char *json, AsphodelChannelInfo_t **channel_info_out);
ASPHODEL_API void asphodel_free_json_channel(AsphodelChannelInfo_t *channel_info); // structs created from JSON only

// Converts a channel info into a JSON string. The JSON string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_json_from_channel_info(const AsphodelChannelInfo_t *channel_info, const char **json_out);


// Converts a JSON string into a setting info. The struct must be freed with asphodel_free_json_setting().
ASPHODEL_API int asphodel_get_setting_info_from_json(const char *json, AsphodelSettingInfo_t **setting_info_out);
ASPHODEL_API void asphodel_free_json_setting(AsphodelSettingInfo_t *setting_info); // structs created from JSON only

// Converts a setting info into a JSON string. The JSON string must be freed with asphodel_free_string().
ASPHODEL_API int asphodel_get_json_from_setting_info(const AsphodelSettingInfo_t *setting_info, const char **json_out);


// Frees a string returned by any of the various string functions.
ASPHODEL_API void asphodel_free_string(const char *str);


// Write a setting from a JSON string. The setting name and JSON string must be UTF-8 encoded and null terminated. The
// nvm_buffer must be (at least) as large the nvm_size of the device_info. If the NVM size is missing or too short for
// the settings then this function will return ASPHODEL_BAD_PARAMETER. Invalid JSON will cause this to return
// ASPHODEL_BAD_PARAMETER. If the setting name can't be matched to a setting this will return ASPHODEL_NOT_FOUND. If
// the shape of the JSON is invalid for the setting then this will return ASPHODEL_INVALID_SETTING_VALUE.
//
// This function will not modify the nvm_buffer if it returns an error.
ASPHODEL_API int asphodel_write_setting(AsphodelDeviceInfo_t *device_info, const char *setting_name, const char *json,
	uint8_t *nvm_buffer);

// Write multiple settings from a single JSON object string, with the setting names as keys. The JSON string must be
// UTF-8 encoded and null terminated. The nvm_buffer must be (at least) as large the nvm_size of the device_info. If
// the NVM size is missing or too short for the settings then this function will return ASPHODEL_BAD_PARAMETER. Invalid
// JSON will cause this to return ASPHODEL_BAD_PARAMETER. If any setting name can't be matched to a setting this will
// return ASPHODEL_NOT_FOUND. If the shape of the JSON is invalid for the setting then this will return
// ASPHODEL_INVALID_SETTING_VALUE.
//
// This function will continue to write settings even if it encounters an ASPHODEL_INVALID_SETTING_VALUE or
// ASPHODEL_NOT_FOUND. If the application doesn't care about missing or invalid settings then it can treat those errors
// as ASPHODEL_SUCCESS.
//
// This function may have modified the nvm_buffer by the time it returns an error.
ASPHODEL_API int asphodel_write_settings(AsphodelDeviceInfo_t *device_info, const char *json, uint8_t *nvm_buffer);

#ifdef __cplusplus
}
#endif

#endif /* ASPHODEL_JSON_H_ */
