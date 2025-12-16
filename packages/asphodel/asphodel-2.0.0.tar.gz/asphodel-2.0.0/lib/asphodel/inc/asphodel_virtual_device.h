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

#ifndef ASPHODEL_VIRTUAL_DEVICE_H_
#define ASPHODEL_VIRTUAL_DEVICE_H_

#include <stdint.h>
#include <stddef.h>
#include "asphodel_api.h"
#include "asphodel_device.h"
#include "asphodel_device_info.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    // NOTE: all of the callbacks in this structure are filled by the user. All are optional. Callbacks will be invoked
    // from the thread calling the device function(s), as there are no internal threads driving things.

    // This may be set by the user and will be passed to each of the callbacks when they are called.
    void * closure;

    // Called whenever the device is opened. Will only be called if the device was closed before.
    void (*open_device)(void * closure);

    // Called whenever the device is closed. Will only be called if the device was open before.
    void (*close_device)(void * closure);

    // Called whenever the device is flushed, or reset.
    void (*flush_device)(void * closure);

    // Called when the device receives a set rgb command.
    void (*set_rgb)(size_t index, const uint8_t values[3], uint8_t instant, void * closure);

    // Called when the device receives a set led command.
    void (*set_led)(size_t index, uint8_t value, uint8_t instant, void * closure);

    // Called when the device receives a stream enable or stream warm up command.
    void (*set_stream_state)(size_t index, uint8_t enable, uint8_t warm_up, void * closure);

    // Called when the device receives a set ctrl var command.
    void (*set_ctrl_var)(size_t index, int32_t value, void * closure);

    // Called when the device receives a set device mode command.
    void (*set_device_mode)(uint8_t mode, void * closure);

    // Called when the device receives a set rf power command.
    void (*set_rf_power)(uint8_t enable, void * closure);

    // Called when the device starts a radio scan
    void (*start_radio_scan)(uint8_t bootloader, void * closure);

    // Called when the device stops its radio scan
    void (*stop_radio_scan)(void * closure);

    // Called when the device receives a connect radio command.
    void (*connect_radio)(uint32_t serial_number, uint8_t bootloader, void * closure);

    // Called when the device disconnects the radio any time after a connect command. Can originate from the remote.
    void (*disconnect_radio)(void * closure);

    // Called (on the radio) when the remote receives a restart remote command. The exact command will be passed as a
    // parameter (i.e. CMD_RESTART_REMOTE, CMD_RESTART_REMOTE_APP, or CMD_RESTART_REMOTE_BOOT).
    void (*restart_remote)(uint8_t command, void * closure);

    // Called when the device receives a command querying scan results. The results array will be as long as the
    // maximum number of scan results that can be tranferred. The callback should fill as many results as possible and
    // return the number filled. To simplify implementations, this is called for both CMD_GET_RADIO_SCAN_RESULTS and
    // CMD_GET_RADIO_EXTRA_SCAN_RESULTS.
    size_t (*get_scan_results)(AsphodelExtraScanResult_t *results, size_t results_length, void * closure);

    // Called when the device receives a command querying scan power for a particular serial number. This may be called
    // multiple times for a single query. The callback should return the power in dBm (usually negative). If the serial
    // number is unknown (e.g. no space in lookup table), return 127 (0x7F).
    int8_t (*get_scan_power)(uint32_t serial_number, void * closure);

    // Extra space allocated to allow backwards compatibility in future library versions. Initialize to zero.
    void * reserved[10];
} AsphodelVirtualDeviceCallbacks_t;

// Create a "virtual" device that will return the values from the supplied device_info. The callbacks can be used to
// customize the behavior of the device. The device_info must live at least as long as the device, and should not be
// modified. The callbacks struct, if provided, must live at least as long as the device.
//
// If allow_fallback_values is set to 1 then the implementation will provide fallback values for some kinds of missing
// information in the device_info (e.g. chip_id) that should be provided by compliant devices. If allow_fallback_values
// is set to 0 then the create function will instead return an error if the device_info is missing any of these values.
//
// The returned device must be freed with device->free_device(device) as usual.
ASPHODEL_API int asphodel_create_virtual_device(const AsphodelDeviceInfo_t *device_info,
    const AsphodelVirtualDeviceCallbacks_t *callbacks, uint8_t allow_fallback_values, AsphodelDevice_t **device);

// remote_device_info can be null to disconnect the remote device.
//
// If remote_device_info is not null, then this attaches a remote device to the main device (must be a radio). The
// remote device can be used in the usual way through the device->get_remote_device() function. The serial_number
// parameter is necessary for proper responses to things like CMD_GET_RADIO_STATUS. If the remote_device_info is null
// then this will disconnect the remote device (and the serial_number parameter will be ignored).
//
// The callbacks (optional) can be used to customize the behavior of the remote device.
//
// The remote_device_info must live at least as long as the next call to asphodel_set_virtual_remote_device() or both
// the radio and remote devices are freed, and the device info should not be modified during that time.
//
// The allow_fallback_values has the same meaning as in asphodel_create_virtual_device().
ASPHODEL_API int asphodel_set_virtual_remote_device(AsphodelDevice_t *device, uint32_t serial_number,
    const AsphodelDeviceInfo_t *remote_device_info, const AsphodelVirtualDeviceCallbacks_t *callbacks,
    uint8_t allow_fallback_values);

// Send packets to the streaming callback (if any) on an open device. The buffer_length must be a multiple of the
// stream packet length. The buffer passed to the callback may be split into multiple chunks if the callback was
// registered with a smaller packet count. No attempt will be made to coalesce chunks smaller than the packet count
// into larger groups. The buffer_length must be greater than zero. Internally, any device state is ignored, so
// filtering on active streams must be done externally.
ASPHODEL_API int asphodel_submit_virtual_device_packets(AsphodelDevice_t *device, const uint8_t *buffer,
    size_t buffer_length);

// Sets the maximum number of transfers (do_transfer/do_transfer_reset calls) that can be sent to this device before it
// will return an error. This is used for testing purposes. If the limit is set to 1, then the next transfer will
// behave normally, but the one after will return ASPHODEL_TRANSPORT_ERROR. If the limit is set to 0, then the next
// transfer will return ASPHODEL_TRANSPORT_ERROR.
ASPHODEL_API int asphodel_set_virtual_transfer_limit(AsphodelDevice_t *device, uint64_t remaining_transfers);

// Returns the number of transfers that can be performed before the device returns an error. By comparing before and
// after, the number of transfers can be measured (assuming the limit is set sufficiently high). When the virtual
// device is created, this limit is set to UINT64_MAX.
ASPHODEL_API int asphodel_get_virtual_transfer_limit(AsphodelDevice_t *device, uint64_t *remaining_transfers);

#ifdef __cplusplus
}
#endif


#endif /* ASPHODEL_VIRTUAL_DEVICE_H_ */
