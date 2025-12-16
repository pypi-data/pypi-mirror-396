/*
 * Copyright (c) 2018, Suprock Technologies
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

#ifdef ASPHODEL_USB_DEVICE

#include <stdlib.h>
#include <stdio.h>
#include <libusb.h>
#include <string.h>

#include "snprintf.h" // for msvc++ compatibility

#include "asphodel.h"
#include "clock.h"
#include "mutex.h"
#include "serialize.h"

#define USB_ASPHODEL_VID 0xABCD
#define MAX_SERIAL_NUMBER_LENGTH 32

#define MAX_LOCATION_STRING_LENGTH 128

#define REMOTE_STATUS_TRANSFER_TIMEOUT 10000 // milliseconds

#define MAX_LIBUSB_VERSION_STRING_LENGTH 64

typedef struct {
	int number;
	int altsetting;
	int num_altsetting;
} InterfaceInfo_t;

typedef struct {
	Mutex_t mutex;
	libusb_device *usbdev;
	libusb_device_handle *devh;
	int open_count;
	int ref_count;
	InterfaceInfo_t *interface_info;
	int interface_count;
} USBSharedDevice_t;

typedef struct {
	AsphodelDevice_t *device;
	AsphodelTransferCallback_t callback;
	void * closure;
	uint8_t cmd;
} USBTransferClosure_t;

typedef struct USBControlTransfer_t {
	struct libusb_transfer *transfer;
	AsphodelDevice_t *device;
	USBTransferClosure_t *c; // only used on outgoing control transfers
	struct USBControlTransfer_t *next;
	struct USBControlTransfer_t **prev_next;
} USBControlTransfer_t;

typedef struct {
	struct libusb_transfer *transfer;
	AsphodelDevice_t *device;
	AsphodelStreamingCallback_t streaming_callback;
	int finished;
	void * streaming_closure;
} USBStreamTransfer_t;

typedef struct {
	Mutex_t mutex;

	int opened;
	int streaming;
	int connected;

	USBSharedDevice_t *shared_device;
	libusb_device_handle *devh;

	int interface_number;
	int interface_altsetting;
	int interface_num_altsetting;

	struct libusb_device_descriptor device_desc;

	struct libusb_config_descriptor *config_desc;

	const struct libusb_endpoint_descriptor *ctrl_in_ep;
	const struct libusb_endpoint_descriptor *ctrl_out_ep;
	const struct libusb_endpoint_descriptor *stream_ep;
	const struct libusb_endpoint_descriptor *status_ep; // only on remote devices
	uint8_t ctrl_in_ep_address;
	uint8_t ctrl_out_ep_address;
	uint8_t stream_ep_address;
	uint8_t status_ep_address; // only on remote devices
	uint8_t ctrl_in_ep_type;
	uint8_t ctrl_out_ep_type;
	uint8_t stream_ep_type;
	uint8_t status_ep_type; // only on remote devices
	size_t max_incoming_param_length;
	size_t max_outgoing_param_length;
	size_t stream_packet_length;
	size_t status_packet_length; // only on remote devices
	size_t control_packet_transfer_length;

	char * serial_number;

	int cmd_timeout; // millseconds

	USBControlTransfer_t *ctrl_list_head;

	// the device's stream data is protected by the libusb event lock (not the device lock),
	// so as to not require the device lock in the stream callback
	int stream_transfer_count;
	USBStreamTransfer_t *stream_transfer_array;
	int next_stream_transfer_index;

	USBTransferClosure_t *transaction_table[256];
	uint8_t last_transaction_id;

	struct libusb_transfer *status_transfer;
	AsphodelConnectCallback_t connect_callback;
	void * connect_closure;

	int remote_same_interface; // whether the remote device (if applicable) uses the same interface
} USBDeviceInfo_t;

typedef struct {
	// NOTE: same as BlockingClosure_t in asphodel_device.c
	int completed;
	int status;
} WaitForFinishClosure_t;


static void usb_error_report(AsphodelDevice_t *device, int error_code);
static int usb_get_transaction_id(AsphodelDevice_t *device, uint8_t *transaction_id, USBTransferClosure_t *c);
static void LIBUSB_CALL incoming_transfer_cb(struct libusb_transfer *transfer);
static int usb_open_device(AsphodelDevice_t * device);
static void usb_close_device_locked_half(AsphodelDevice_t *device, USBDeviceInfo_t *usb_info);
static void usb_close_device_unlocked_half(AsphodelDevice_t *device, USBDeviceInfo_t *usb_info);
static void usb_close_device(AsphodelDevice_t *device);
static void usb_free_device(AsphodelDevice_t *device);
static int usb_get_serial_number(AsphodelDevice_t *device, char *buffer, size_t buffer_size);
static void LIBUSB_CALL do_transfer_outgoing_callback(struct libusb_transfer *transfer);
static int usb_do_transfer(AsphodelDevice_t *device, uint8_t command, const uint8_t *params, size_t param_length, AsphodelTransferCallback_t callback, void * closure);
static void LIBUSB_CALL do_transfer_reset_callback(struct libusb_transfer *transfer);
static int usb_do_transfer_reset(AsphodelDevice_t *device, uint8_t command, const uint8_t *params, size_t param_length, AsphodelTransferCallback_t callback, void * closure);
static int usb_start_streaming_packets(AsphodelDevice_t *device, int packet_count, int transfer_count, unsigned int timeout, AsphodelStreamingCallback_t callback, void * closure);
static void usb_stop_streaming_packets_locked(USBDeviceInfo_t *usb_info);
static void usb_stop_streaming_packets(AsphodelDevice_t *device);
static int usb_get_stream_packets_blocking(AsphodelDevice_t *device, uint8_t *buffer, int *count, unsigned int timeout);
static size_t usb_get_max_incoming_param_length(AsphodelDevice_t * device);
static size_t usb_get_max_outgoing_param_length(AsphodelDevice_t * device);
static size_t usb_get_stream_packet_length(AsphodelDevice_t * device);
static int usb_reconnect_device(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device);
static int usb_reconnect_remote(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device);
static int usb_reconnect_remote_boot(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device);
static int usb_reconnect_remote_app(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device);
static int usb_poll_device(AsphodelDevice_t * device, int milliseconds, int *completed);


static libusb_context *ctx;
static char *backend_version_string = NULL;


static int usb_libusb_error_to_asphodel(int libusb_error_code)
{
	switch (libusb_error_code)
	{
	case LIBUSB_SUCCESS:
		return ASPHODEL_SUCCESS;
	case LIBUSB_ERROR_IO:
		return ASPHODEL_ERROR_IO;
	case LIBUSB_ERROR_INVALID_PARAM:
		return ASPHODEL_BAD_PARAMETER;
	case LIBUSB_ERROR_ACCESS:
		return ASPHODEL_ACCESS_ERROR;
	case LIBUSB_ERROR_NO_DEVICE:
		return ASPHODEL_NO_DEVICE;
	case LIBUSB_ERROR_NOT_FOUND:
		return ASPHODEL_NOT_FOUND;
	case LIBUSB_ERROR_BUSY:
		return ASPHODEL_BUSY;
	case LIBUSB_ERROR_TIMEOUT:
		return ASPHODEL_TIMEOUT;
	case LIBUSB_ERROR_OVERFLOW:
		return ASPHODEL_OVERFLOW;
	case LIBUSB_ERROR_PIPE:
		return ASPHODEL_PIPE_ERROR;
	case LIBUSB_ERROR_INTERRUPTED:
		return ASPHODEL_INTERRUPTED;
	case LIBUSB_ERROR_NO_MEM:
		return ASPHODEL_NO_MEM;
	case LIBUSB_ERROR_NOT_SUPPORTED:
		return ASPHODEL_NOT_SUPPORTED;
	default:
		return ASPHODEL_TRANSPORT_ERROR; // unknown LibUSB error
	}
}

static int usb_libusb_transfer_status_to_asphodel(int transfer_status)
{
	switch (transfer_status)
	{
	case LIBUSB_TRANSFER_COMPLETED:
		return ASPHODEL_SUCCESS;
	case LIBUSB_TRANSFER_ERROR:
		return ASPHODEL_ERROR_IO;
	case LIBUSB_TRANSFER_TIMED_OUT:
		return ASPHODEL_TIMEOUT;
	case LIBUSB_TRANSFER_CANCELLED:
		return ASPHODEL_CANCELLED;
	case LIBUSB_TRANSFER_STALL:
		return ASPHODEL_STALL;
	case LIBUSB_TRANSFER_NO_DEVICE:
		return ASPHODEL_NO_DEVICE;
	case LIBUSB_TRANSFER_OVERFLOW:
		return ASPHODEL_OVERFLOW;
	default:
		return ASPHODEL_TRANSPORT_ERROR; // unknown LibUSB transfer status
	}
}

static int usb_create_shared_device(libusb_device *usbdev, USBSharedDevice_t **shared_device, InterfaceInfo_t *interface_info, int interface_count)
{
	int ret;
	USBSharedDevice_t *new_shared_device = (USBSharedDevice_t*)malloc(sizeof(USBSharedDevice_t));
	size_t interface_info_size;

	if (new_shared_device == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	ret = mutex_init(&new_shared_device->mutex);
	if (ret != 0)
	{
		// error
		free(new_shared_device);
		return ret;
	}

	// no need to lock the mutex, as the shared device hasn't been passed anywhere

	interface_info_size = sizeof(InterfaceInfo_t) * interface_count;
	new_shared_device->interface_count = interface_count;
	new_shared_device->interface_info = (InterfaceInfo_t*)malloc(interface_info_size);
	if (new_shared_device->interface_info == NULL)
	{
		free(new_shared_device);
		return ASPHODEL_NO_MEM;
	}

	// copy the interface info
	memcpy(new_shared_device->interface_info, interface_info, interface_info_size);

	new_shared_device->usbdev = usbdev;
	new_shared_device->open_count = 0;
	new_shared_device->ref_count = 1; // start the shared device as referenced

	libusb_ref_device(new_shared_device->usbdev);

	*shared_device = new_shared_device;
	return 0;
}

static int usb_open_shared_device(USBSharedDevice_t *shared_device, libusb_device_handle **devh) // called with the libusb event lock held; THIS FUNCTION WILL UNLOCK LIBUSB EVENTS ON ANY FAILURE!
{
	int ret = 0;

	mutex_lock(shared_device->mutex);

	if (shared_device->open_count == 0)
	{
		ret = libusb_open(shared_device->usbdev, &shared_device->devh);

		if (ret == 0)
		{
			int i;
			int config;

			// check the configuration
			ret = libusb_get_configuration(shared_device->devh, &config);
			if (ret != 0)
			{
				// error
				libusb_unlock_events(ctx); // unlock before libusb_close(), but must unlock on any error
				libusb_close(shared_device->devh);
				mutex_unlock(shared_device->mutex);
				return usb_libusb_error_to_asphodel(ret);
			}

			// set the configuration, if necessary
			if (config != 1)
			{
				// all Asphodel USB devices have a bConfigurationValue of 1
				ret = libusb_set_configuration(shared_device->devh, 1);
				if (ret != 0)
				{
					// error
					libusb_unlock_events(ctx); // unlock before libusb_close(), but must unlock on any error
					libusb_close(shared_device->devh);
					mutex_unlock(shared_device->mutex);
					return usb_libusb_error_to_asphodel(ret);
				}
			}

			// claim interfaces
			for (i = 0; i < shared_device->interface_count; i++)
			{
				InterfaceInfo_t *interface_info = &shared_device->interface_info[i];

				// claim interface
				ret = libusb_claim_interface(shared_device->devh, interface_info->number);
				if (ret != 0)
				{
					// error

					int j;

					// release earlier interfaces
					for (j = 0; j < i; j++)
					{
						libusb_release_interface(shared_device->devh, shared_device->interface_info[j].number);
					}

					libusb_unlock_events(ctx); // unlock before libusb_close(), but must unlock on any error
					libusb_close(shared_device->devh);
					mutex_unlock(shared_device->mutex);
					return usb_libusb_error_to_asphodel(ret);
				}

				// set interface alt setting, if needed
				if (interface_info->num_altsetting > 1)
				{
					ret = libusb_set_interface_alt_setting(shared_device->devh, interface_info->number, interface_info->altsetting);
					if (ret != 0)
					{
						// error

						int j;

						libusb_release_interface(shared_device->devh, interface_info->number);

						// release earlier interfaces
						for (j = 0; j < i; j++)
						{
							libusb_release_interface(shared_device->devh, shared_device->interface_info[j].number);
						}

						libusb_unlock_events(ctx); // unlock before libusb_close(), but must unlock on any error
						libusb_close(shared_device->devh);
						mutex_unlock(shared_device->mutex);
						return usb_libusb_error_to_asphodel(ret);
					}
				}
			}
		}
		else
		{
			libusb_unlock_events(ctx); // must unlock on any error
			mutex_unlock(shared_device->mutex);
			return usb_libusb_error_to_asphodel(ret);
		}
	}

	shared_device->open_count += 1;

	*devh = shared_device->devh;

	mutex_unlock(shared_device->mutex);

	return usb_libusb_error_to_asphodel(ret);
}

static void usb_close_shared_device(USBSharedDevice_t *shared_device) // must be called without the libusb event lock held
{
	mutex_lock(shared_device->mutex);

	shared_device->open_count -= 1;
	if (shared_device->open_count == 0)
	{
		int i;

		// release interfaces
		for (i = 0; i < shared_device->interface_count; i++)
		{
			InterfaceInfo_t *interface_info = &shared_device->interface_info[i];
			libusb_release_interface(shared_device->devh, interface_info->number);
		}

		// close device
		libusb_close(shared_device->devh);
	}

	mutex_unlock(shared_device->mutex);
}

static void usb_ref_shared_device(USBSharedDevice_t *shared_device)
{
	mutex_lock(shared_device->mutex);

	shared_device->ref_count += 1;

	mutex_unlock(shared_device->mutex);
}

static void usb_unref_shared_device(USBSharedDevice_t *shared_device)
{
	mutex_lock(shared_device->mutex);

	shared_device->ref_count -= 1;
	if (shared_device->ref_count == 0)
	{
		mutex_unlock(shared_device->mutex);

		mutex_destroy(&shared_device->mutex);
		libusb_unref_device(shared_device->usbdev);
		free(shared_device);
	}
	else
	{
		mutex_unlock(shared_device->mutex);
	}
}

static void usb_error_report(AsphodelDevice_t *device, int error_code) // call with libusb lock and device lock held
{
	if (device->error_callback)
	{
		device->error_callback(device, error_code, device->error_closure);
	}
}

static int usb_get_transaction_id(AsphodelDevice_t *device, uint8_t *transaction_id, USBTransferClosure_t *c) // called with the device lock held
{
	uint8_t id;
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	id = usb_info->last_transaction_id + 1;
	while (1)
	{
		// don't use 0
		if (id == 0)
		{
			id = 1;
		}

		if (usb_info->transaction_table[id] == NULL)
		{
			// found an empty spot
			break;
		}

		if (id == usb_info->last_transaction_id)
		{
			// terminate with failure
			id = 0;
			break;
		}

		// increment
		id += 1;
	}

	if (id != 0)
	{
		usb_info->last_transaction_id = id;
		*transaction_id = id;
		usb_info->transaction_table[id] = c;

		return 0;
	}
	else
	{
		return ASPHODEL_FULL_TRANSACTION_TABLE;
	}
}

static int usb_handle_remote_connect(AsphodelDevice_t *device, int connected, uint32_t serial_number, uint8_t protocol_type) // must have the libusb and device lock held while calling
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	usb_info->connected = connected;
	if (connected)
	{
		// just in case, add the remote to the type (shouldn't be necessary)
		device->protocol_type = protocol_type | ASPHODEL_PROTOCOL_TYPE_REMOTE;

		// remove old serial number
		if (usb_info->serial_number != NULL)
		{
			free(usb_info->serial_number);
		}

		// allocate new serial number
		usb_info->serial_number = (char*)malloc(MAX_SERIAL_NUMBER_LENGTH);
		if (usb_info->serial_number == NULL)
		{
			return ASPHODEL_NO_MEM;
		}

		// write into new serial number
		snprintf(usb_info->serial_number, MAX_SERIAL_NUMBER_LENGTH, "WM%u", serial_number);
	}
	else
	{
		// remove any old protocol types assoicated with the device
		device->protocol_type = ASPHODEL_PROTOCOL_TYPE_REMOTE;

		// remove serial number
		if (usb_info->serial_number != NULL)
		{
			free(usb_info->serial_number);
			usb_info->serial_number = NULL;
		}
	}

	// call callback
	if (usb_info->connect_callback != NULL)
	{
		usb_info->connect_callback(0, connected, usb_info->connect_closure);
	}

	return 0;
}

static void LIBUSB_CALL remote_status_transfer_cb(struct libusb_transfer *transfer)
{
	int ret;
	AsphodelDevice_t *device = (AsphodelDevice_t*)transfer->user_data;
	USBDeviceInfo_t *usb_info;

	if (device == NULL)
	{
		// we've been cancelled, bail out
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		return;
	}

	usb_info = (USBDeviceInfo_t*)device->implementation_info;

	mutex_lock(usb_info->mutex);

	if (transfer->status == LIBUSB_TRANSFER_COMPLETED || transfer->status == LIBUSB_TRANSFER_TIMED_OUT)
	{
		if (transfer->actual_length == 0)
		{
			// ignore?
		}
		else if (transfer->actual_length == 1)
		{
			int connected = transfer->buffer[0];

			if (!connected)
			{
				ret = usb_handle_remote_connect(device, connected, 0, 0);
				if (ret != 0)
				{
					usb_error_report(device, ret);
				}
			}
			else
			{
				usb_error_report(device, ASPHODEL_MALFORMED_REPLY);
			}
		}
		else if (transfer->actual_length == 6)
		{
			int connected = transfer->buffer[0];
			uint32_t serial_number = read_32bit_value(&transfer->buffer[1]);
			uint8_t protocol_type = transfer->buffer[5];

			ret = usb_handle_remote_connect(device, connected, serial_number, protocol_type);
			if (ret != 0)
			{
				usb_error_report(device, ret);
			}
		}
		else
		{
			usb_error_report(device, ASPHODEL_MALFORMED_REPLY);
		}
	}
	else if (transfer->status == LIBUSB_TRANSFER_CANCELLED)
	{
		// Spurious cancel; can happen on windows when cancelling transfers on other endpoints. Reason not fully understood.
		// ignore and it will get resubmitted at the end of the function
	}
	else
	{
		// error
		usb_error_report(device, ASPHODEL_TRANSFER_ERROR);

		// free transfer & return
		usb_info->status_transfer = NULL;
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		mutex_unlock(usb_info->mutex);
		return;
	}

	if (usb_info->status_transfer == NULL)
	{
		// cancelled in the callback
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		mutex_unlock(usb_info->mutex);
		return;
	}
	else
	{
		// resubmit the trasfer
		ret = libusb_submit_transfer(transfer);
		if (ret != 0)
		{
			// error
			int error_code = usb_libusb_error_to_asphodel(ret);
			usb_error_report(device, error_code);

			usb_info->status_transfer = NULL;
			free(transfer->buffer);
			libusb_free_transfer(transfer);
			mutex_unlock(usb_info->mutex);
			return;
		}
	}

	mutex_unlock(usb_info->mutex);
}

static void wait_for_finish_cb(int status, void * closure)
{
	// NOTE: same as command_blocking_callback in asphodel_device.c
	WaitForFinishClosure_t *c = (WaitForFinishClosure_t *)closure;
	c->status = status;
	c->completed = 1;
}

static void LIBUSB_CALL wait_for_finish_libusb_cb(struct libusb_transfer *transfer)
{
	// NOTE: same as wait_for_finish_cb, but with libusb callback prototype
	WaitForFinishClosure_t *c = (WaitForFinishClosure_t *)transfer->user_data;
	c->status = 0; // can't easily map transfer status to error code. caller will need to check the transfer status themselves
	c->completed = 1;
}

static int wait_for_finish(WaitForFinishClosure_t *c) // called after submitting a non-blocking asphodel command, while holding the libusb event lock
{
	int ret;

	// set poll interval at 100ms
	struct timeval tv;
	tv.tv_sec = 0;
	tv.tv_usec = 100000;

	while (!c->completed)
	{
		ret = libusb_handle_events_locked(ctx, &tv);
		if (ret != 0)
		{
			return usb_libusb_error_to_asphodel(ret);
		}
	}

	return c->status;
}

// Open the device for usage. Must be called before any others.
static int usb_open_device(AsphodelDevice_t * device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->opened == 0)
	{
		WaitForFinishClosure_t flush_closure = { 0, 0 };
		struct timeval tv = {0, 0};
		int ret;

		ret = usb_open_shared_device(usb_info->shared_device, &usb_info->devh); // NOTE: if this fails it will unlock the libusb event lock
		if (ret != 0)
		{
			// error
			mutex_unlock(usb_info->mutex);
			// libusb_unlock_events(ctx); // already unlocked by usb_open_shared_device failure
			return ret;
		}

		// handle any pending events, non-blocking
		libusb_handle_events_locked(ctx, &tv);

		usb_info->opened = 1;

		// flush the device (need to use the non-blocking version because of locking around device->poll)
		ret = asphodel_flush(device, wait_for_finish_cb, &flush_closure);
		if (ret != 0)
		{
			usb_close_device_locked_half(device, usb_info);
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			usb_close_device_unlocked_half(device, usb_info);
			return ret;
		}

		// wait for asphodel_flush() to finish
		ret = wait_for_finish(&flush_closure);
		if (ret != 0)
		{
			usb_close_device_locked_half(device, usb_info);
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			usb_close_device_unlocked_half(device, usb_info);
			return ret;
		}

		// extra steps for a remote device
		if (asphodel_supports_remote_commands(device))
		{
			int connected;
			uint32_t serial_number;
			uint8_t protocol_type;
			uint8_t *status_buffer;
			WaitForFinishClosure_t status_closure = { 0, 0 };

			// get the remote status (need to use the non-blocking version because of locking around device->poll)
			ret = asphodel_get_remote_status(device, &connected, &serial_number, &protocol_type, wait_for_finish_cb, &status_closure);
			if (ret != 0)
			{
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return ret;
			}

			ret = wait_for_finish(&status_closure);
			if (ret != 0)
			{
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return ret;
			}

			// handle any callbacks
			ret = usb_handle_remote_connect(device, connected, serial_number, protocol_type);
			if (ret != 0)
			{
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return ret;
			}

			// allocate status transfer
			usb_info->status_transfer = libusb_alloc_transfer(0);
			if (usb_info->status_transfer == NULL)
			{
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return ASPHODEL_NO_MEM;
			}

			// allocate status buffer
			status_buffer = (uint8_t*)malloc(usb_info->status_packet_length);
			if (status_buffer == NULL)
			{
				libusb_free_transfer(usb_info->status_transfer);
				usb_info->status_transfer = NULL;
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return ASPHODEL_NO_MEM;
			}

			// fill status transfer
			libusb_fill_bulk_transfer(usb_info->status_transfer, usb_info->devh, usb_info->status_ep_address, status_buffer,
					(int)usb_info->status_packet_length, remote_status_transfer_cb, device, REMOTE_STATUS_TRANSFER_TIMEOUT);
			usb_info->status_transfer->type = usb_info->status_ep_type; // LIBUSB_TRANSFER_TYPE_INTERRUPT or LIBUSB_TRANSFER_TYPE_BULK

			// start the libusb transfer for the status endpoint
			ret = libusb_submit_transfer(usb_info->status_transfer);
			if (ret != 0)
			{
				libusb_free_transfer(usb_info->status_transfer);
				usb_info->status_transfer = NULL;
				free(status_buffer);
				usb_close_device_locked_half(device, usb_info);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				usb_close_device_unlocked_half(device, usb_info);
				return usb_libusb_error_to_asphodel(ret);
			}
		}
	}

	mutex_unlock(usb_info->mutex);
	libusb_unlock_events(ctx);
	return 0;
}

// assumes opened, and MUST be called with BOTH the libusb event lock and the device mutex.
// Call usb_close_device_unlocked_half() directly after this function finishes with locks released
static void usb_close_device_locked_half(AsphodelDevice_t *device, USBDeviceInfo_t *usb_info)
{
	struct timeval tv = { 0, 0 };
	USBControlTransfer_t *control_transfer;
	size_t i;

	if (usb_info->streaming)
	{
		usb_stop_streaming_packets_locked(usb_info);
	}

	usb_info->opened = 0;

	control_transfer = usb_info->ctrl_list_head;
	usb_info->ctrl_list_head = NULL;

	// cancel all control endpoint transfers
	while (control_transfer != NULL)
	{
		USBControlTransfer_t *next = control_transfer->next;
		struct libusb_transfer *transfer = control_transfer->transfer;

		if (transfer)
		{
			transfer->user_data = NULL;

			// don't care about the return value; there's nothing more to do in any case
			libusb_cancel_transfer(transfer);
		}

		free(control_transfer);

		// move to the next item in the list
		control_transfer = next;
	}

	// iterate through outstanding transaction IDs and perform their callbacks
	for (i = 0; i < 256; i++)
	{
		USBTransferClosure_t *c = usb_info->transaction_table[i];
		if (c != NULL)
		{
			usb_info->transaction_table[i] = NULL;
			if (c->callback)
			{
				c->callback(ASPHODEL_DEVICE_CLOSED, NULL, 0, c->closure);
			}
			free(c);
		}
	}

	// extra steps for a remote device
	if (asphodel_supports_remote_commands(device))
	{
		// stop the status endpoint transfer (if running)
		if (usb_info->status_transfer)
		{
			// mark the transfer as cancelled
			usb_info->status_transfer->user_data = NULL;

			// cancel the transfer
			libusb_cancel_transfer(usb_info->status_transfer);

			// remove it from the usb info (the callback will free the data)
			usb_info->status_transfer = NULL;
		}
	}

	// do a quick poll to allow any left over callbacks to cancel
	libusb_handle_events_locked(ctx, &tv);

	usb_info->devh = NULL;
}

// called directly after usb_close_device_locked_half, and MUST be called without either libusb event lock or device lock
static void usb_close_device_unlocked_half(AsphodelDevice_t *device, USBDeviceInfo_t *usb_info)
{
	(void)device; // ignore unused parameter; want to keep the prototype the same as locked_half

	usb_close_shared_device(usb_info->shared_device);
}

// Close the device and release any shared resources (e.g. usb handles, tcp sockets).
static void usb_close_device(AsphodelDevice_t *device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->opened)
	{
		usb_close_device_locked_half(device, usb_info);

		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);

		usb_close_device_unlocked_half(device, usb_info);
	}
	else
	{
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
	}
}

static void usb_free_device(AsphodelDevice_t *device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	// there should never be any contention for the device lock, as it's being freed
	// and not taking it makes usb_close_device() simpler to call without worrying about locking order

	if (usb_info->opened)
	{
		usb_close_device(device);
	}

	if (usb_info->serial_number)
	{
		free(usb_info->serial_number);
	}

	free((char*)device->location_string);

	if (usb_info->config_desc != NULL)
	{
		libusb_free_config_descriptor(usb_info->config_desc);
	}

	usb_unref_shared_device(usb_info->shared_device);

	mutex_destroy(&usb_info->mutex);

	free(usb_info);
	free(device);
}

static int get_serial_number_locked(libusb_device_handle *devh, uint8_t desc_index, char *sn_buffer, size_t sn_buffer_size) // called with the libusb event lock held
{
	int ret;
	WaitForFinishClosure_t closure;
	struct libusb_transfer *transfer;
	uint8_t local_buffer[LIBUSB_CONTROL_SETUP_SIZE + 255]; // according to libusb some devices can misbehave when asked for more than 255 bytes of descriptor
	uint16_t langid;
	uint8_t descriptor_len;
	uint8_t descriptor_index;
	size_t string_index;

	if (sn_buffer_size <= 1)
	{
		// not enough size to write in a serial number
		return ASPHODEL_BAD_PARAMETER;
	}

	if (desc_index == 0) // string descriptor 0 is the list of language ids, and not an actual string
	{
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	transfer = libusb_alloc_transfer(0);
	if (transfer == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	// do a request for the list of langids (descriptor index 0)
	closure.completed = 0;
	libusb_fill_control_setup(local_buffer, LIBUSB_ENDPOINT_IN, LIBUSB_REQUEST_GET_DESCRIPTOR, (uint16_t)((LIBUSB_DT_STRING << 8) | 0), 0, sizeof(local_buffer) - LIBUSB_CONTROL_SETUP_SIZE);
	libusb_fill_control_transfer(transfer, devh, local_buffer, wait_for_finish_libusb_cb, &closure, 1000);
	ret = libusb_submit_transfer(transfer);
	if (ret != 0)
	{
		libusb_free_transfer(transfer);
		return usb_libusb_error_to_asphodel(ret);
	}

	ret = wait_for_finish(&closure);
	if (ret != 0)
	{
		libusb_free_transfer(transfer);
		return usb_libusb_error_to_asphodel(ret);
	}

	if (transfer->status != LIBUSB_TRANSFER_COMPLETED)
	{
		if (transfer->status == LIBUSB_TRANSFER_TIMED_OUT)
		{
			ret = ASPHODEL_TIMEOUT;
		}
		else
		{
			// some other error
			ret = ASPHODEL_TRANSFER_ERROR;
		}
		libusb_free_transfer(transfer);
		return ret;
	}

	if (transfer->actual_length < 4) // too short
	{
		libusb_free_transfer(transfer);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	// get the first langid provided by the device (probably the only one)
	langid = (local_buffer[LIBUSB_CONTROL_SETUP_SIZE + 3] << 8) | local_buffer[LIBUSB_CONTROL_SETUP_SIZE + 2];

	// do a new request for
	closure.completed = 0;
	libusb_fill_control_setup(local_buffer, LIBUSB_ENDPOINT_IN, LIBUSB_REQUEST_GET_DESCRIPTOR, (uint16_t)((LIBUSB_DT_STRING << 8) | desc_index), langid, sizeof(local_buffer) - LIBUSB_CONTROL_SETUP_SIZE);
	libusb_fill_control_transfer(transfer, devh, local_buffer, wait_for_finish_libusb_cb, &closure, 1000);
	ret = libusb_submit_transfer(transfer);
	if (ret < 0)
	{
		libusb_free_transfer(transfer);
		return usb_libusb_error_to_asphodel(ret);
	}

	ret = wait_for_finish(&closure);
	if (ret != 0)
	{
		libusb_free_transfer(transfer);
		return usb_libusb_error_to_asphodel(ret);
	}

	if (transfer->status != LIBUSB_TRANSFER_COMPLETED)
	{
		if (transfer->status == LIBUSB_TRANSFER_TIMED_OUT)
		{
			ret = ASPHODEL_TIMEOUT;
		}
		else
		{
			// some other error
			ret = ASPHODEL_TRANSFER_ERROR;
		}
		libusb_free_transfer(transfer);
		return ret;
	}

	if (transfer->actual_length < 2) // too short
	{
		libusb_free_transfer(transfer);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	if (local_buffer[LIBUSB_CONTROL_SETUP_SIZE + 1] != LIBUSB_DT_STRING)
	{
		libusb_free_transfer(transfer);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	descriptor_len = local_buffer[LIBUSB_CONTROL_SETUP_SIZE + 0];

	if (descriptor_len != transfer->actual_length) // wrong size
	{
		libusb_free_transfer(transfer);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	// copy UTF-16 string to ascii buffer
	string_index = 0;
	for (descriptor_index = 2; descriptor_index < descriptor_len; descriptor_index += 2)
	{
		uint8_t high_byte = local_buffer[LIBUSB_CONTROL_SETUP_SIZE + descriptor_index + 1];
		uint8_t low_byte = local_buffer[LIBUSB_CONTROL_SETUP_SIZE + descriptor_index];

		if (string_index >= (sn_buffer_size - 1))
		{
			break;
		}

		if ((low_byte & 0x80) != 0 || high_byte != 0x00)
		{
			// not an ascii value
			sn_buffer[string_index] = '?';
		}
		else
		{
			sn_buffer[string_index] = (char)low_byte;
		}

		string_index += 1;
	}

	sn_buffer[string_index] = '\0';

	libusb_free_transfer(transfer);

	return 0;
}

// Copy the device's serial number (UTF-8 encoded) into the specified buffer.
// The copy will be null terminated, and use at most buffer_size bytes (including the null).
static int usb_get_serial_number(AsphodelDevice_t *device, char *buffer, size_t buffer_size)
{
	size_t i;
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (!usb_info->opened)
	{
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_DEVICE_CLOSED;
	}

	if (asphodel_supports_remote_commands(device))
	{
		// poll the device to make sure there's nothing (i.e. disconnect/connect) pending
		struct timeval tv = { 0, 0 };
		libusb_handle_events_locked(ctx, &tv);
	}

	if (usb_info->serial_number == NULL)
	{
		if (asphodel_supports_remote_commands(device))
		{
			// return an empty string
			buffer[0] = '\0';
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			return 0;
		}
		else
		{
			// fetch the serial number from the device
			int ret;
			char * serial_number = (char*)malloc(MAX_SERIAL_NUMBER_LENGTH);
			uint8_t desc_index = usb_info->device_desc.iSerialNumber;

			if (serial_number == NULL)
			{
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				return ASPHODEL_NO_MEM;
			}

			ret = get_serial_number_locked(usb_info->devh, desc_index, serial_number, MAX_SERIAL_NUMBER_LENGTH);
			if (ret != 0)
			{
				free(serial_number);
				mutex_unlock(usb_info->mutex);
				libusb_unlock_events(ctx);
				return ret;
			}
			usb_info->serial_number = serial_number;
		}
	}

	for (i = 0; i < buffer_size - 1; i++)
	{
		char ch = usb_info->serial_number[i];
		buffer[i] = ch;

		if (ch == '\0')
		{
			break;
		}
	}

	// make sure the buffer is null terminated
	buffer[i] = '\0';

	mutex_unlock(usb_info->mutex);
	libusb_unlock_events(ctx);

	return 0;
}

static void LIBUSB_CALL incoming_transfer_cb(struct libusb_transfer *transfer)
{
	USBControlTransfer_t *control_transfer = (USBControlTransfer_t*)transfer->user_data;
	AsphodelDevice_t *device;
	USBDeviceInfo_t *usb_info;

	if (control_transfer == NULL)
	{
		// we've been cancelled, bail out
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		return;
	}

	device = control_transfer->device;
	usb_info = (USBDeviceInfo_t*)device->implementation_info;

	mutex_lock(usb_info->mutex);

	if (transfer->status == LIBUSB_TRANSFER_COMPLETED)
	{
		if (transfer->actual_length == 0)
		{
			// ignore
		}
		else if (transfer->actual_length == 1)
		{
			// packet too short
			uint8_t transaction_id = transfer->buffer[0];
			USBTransferClosure_t *c;

			c = usb_info->transaction_table[transaction_id];
			usb_info->transaction_table[transaction_id] = NULL;

			if (c != NULL)
			{
				if (c->callback)
				{
					c->callback(ASPHODEL_MALFORMED_REPLY, NULL, 0, c->closure);
				}

				free(c);
			}
			else
			{
				usb_error_report(device, ASPHODEL_MALFORMED_REPLY);
			}
		}
		else
		{
			uint8_t transaction_id = transfer->buffer[0];
			USBTransferClosure_t *c;

			c = usb_info->transaction_table[transaction_id];
			usb_info->transaction_table[transaction_id] = NULL;

			if (c != NULL)
			{
				if (transfer->buffer[1] == c->cmd)
				{
					if (c->callback)
					{
						c->callback(0, &transfer->buffer[2], transfer->actual_length - 2, c->closure);
					}
				}
				else if (transfer->buffer[1] == CMD_REPLY_ERROR)
				{
					if (transfer->actual_length < 3)
					{
						// error packet is too short
						if (c->callback)
						{
							c->callback(ASPHODEL_MALFORMED_ERROR, NULL, 0, c->closure);
						}
					}
					else
					{
						uint8_t error_code = transfer->buffer[2];

						if (error_code == 0x00)
						{
							error_code = ERROR_CODE_UNSPECIFIED;
						}

						if (c->callback)
						{
							// pass the error parameters
							c->callback(error_code, &transfer->buffer[3], transfer->actual_length - 3, c->closure);
						}
					}
				}
				else
				{
					// got an unexpected command reply
					if (c->callback)
					{
						c->callback(ASPHODEL_MISMATCHED_COMMAND, NULL, 0, c->closure);
					}
				}

				free(c);
			}
			else
			{
				int ret;

				usb_error_report(device, ASPHODEL_MISMATCHED_TRANSACTION);

				// resubmit and hope for the actual response
				ret = libusb_submit_transfer(transfer);
				if (ret == 0)
				{
					// success, leave early so nothing gets freed
					mutex_unlock(usb_info->mutex);
					return;
				}
				else
				{
					usb_error_report(device, usb_libusb_error_to_asphodel(ret));
				}
			}
		}
	}
	else if (transfer->status != LIBUSB_TRANSFER_TIMED_OUT)
	{
		// error
		usb_error_report(device, ASPHODEL_TRANSFER_ERROR);
	}

	if (transfer->user_data != NULL) // make sure the transfer wasn't cancelled in a callback
	{
		// remove control transfer from the linked list
		*control_transfer->prev_next = control_transfer->next;
		if (control_transfer->next != NULL)
		{
			control_transfer->next->prev_next = control_transfer->prev_next;
		}

		free(control_transfer);

		if (usb_info->ctrl_list_head == NULL)
		{
			// check for timeouts; assume anything still in the transaction table has timed out
			size_t i;

			for (i = 0; i < 256; i++)
			{
				USBTransferClosure_t *c = usb_info->transaction_table[i];
				if (c != NULL)
				{
					usb_info->transaction_table[i] = NULL;
					if (c->callback)
					{
						c->callback(ASPHODEL_TIMEOUT, NULL, 0, c->closure);
					}
					free(c);
				}
			}
		}
	}

	free(transfer->buffer);
	libusb_free_transfer(transfer);

	mutex_unlock(usb_info->mutex);
}

static void LIBUSB_CALL do_transfer_outgoing_callback(struct libusb_transfer *transfer)
{
	USBControlTransfer_t *control_transfer = (USBControlTransfer_t*)transfer->user_data;
	AsphodelDevice_t *device;
	USBDeviceInfo_t *usb_info;

	if (control_transfer == NULL)
	{
		// we've been cancelled, bail out
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		return;
	}

	device = control_transfer->device;
	usb_info = (USBDeviceInfo_t*)device->implementation_info;

	mutex_lock(usb_info->mutex);

	if (transfer->status != LIBUSB_TRANSFER_COMPLETED)
	{
		// had an error

		USBTransferClosure_t *c = control_transfer->c;
		uint8_t transaction_id = transfer->buffer[0];

		// find the transaction ID and mark it as handled
		usb_info->transaction_table[transaction_id] = NULL;

		if (c->callback)
		{
			int error_code = usb_libusb_transfer_status_to_asphodel(transfer->status);
			c->callback(error_code, NULL, 0, c->closure);
		}

		free(c);

		if (transfer->user_data != NULL)
		{
			// weren't cancelled by the callback

			// mark the transfer as cancelled
			control_transfer->transfer = NULL;
		}

		// free the packet and transfer
		free(transfer->buffer);
		libusb_free_transfer(transfer);
	}
	else
	{
		// start an incoming transfer (can use the same control transfer & libusb transfer)
		int ret;
		USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)control_transfer->device->implementation_info;

		libusb_fill_bulk_transfer(transfer, usb_info->devh, usb_info->ctrl_in_ep_address, transfer->buffer,
				usb_info->ctrl_in_ep->wMaxPacketSize, incoming_transfer_cb, control_transfer, usb_info->cmd_timeout);
		transfer->type = usb_info->ctrl_in_ep_type; // LIBUSB_TRANSFER_TYPE_INTERRUPT or LIBUSB_TRANSFER_TYPE_BULK

		ret = libusb_submit_transfer(transfer);
		if (ret != 0)
		{
			// had an error

			USBTransferClosure_t *c = control_transfer->c;
			uint8_t transaction_id = transfer->buffer[0];

			// find the transaction ID and mark it as handled
			usb_info->transaction_table[transaction_id] = NULL;

			if (c->callback)
			{
				int error_code = usb_libusb_error_to_asphodel(ret);
				c->callback(error_code, NULL, 0, c->closure);
			}

			free(c);

			if (transfer->user_data != NULL)
			{
				// weren't cancelled by the callback

				// mark the transfer as cancelled
				control_transfer->transfer = NULL;
			}

			// free the packet and transfer
			free(transfer->buffer);
			libusb_free_transfer(transfer);
		}
	}

	mutex_unlock(usb_info->mutex);
}

// Start an Asphodel command transfer. The specified callback will be called when finished.
static int usb_do_transfer(AsphodelDevice_t *device, uint8_t command, const uint8_t *params, size_t param_length, AsphodelTransferCallback_t callback, void * closure)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	USBTransferClosure_t *c;
	USBControlTransfer_t *control_transfer;
	uint8_t transaction_id;
	int ret;
	struct libusb_transfer * outgoing_transfer;
	int packet_length = (int)param_length + 2;
	uint8_t *packet;

	// can't take the libusb lock in this function, because it is called in callbacks
	mutex_lock(usb_info->mutex);

	if (usb_info->opened == 0)
	{
		// not opened
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_DEVICE_CLOSED;
	}

	if (param_length > usb_info->max_outgoing_param_length)
	{
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	}

	// allocate the outgoing packet
	packet = (uint8_t*)malloc(usb_info->control_packet_transfer_length);
	if (packet == NULL)
	{
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	outgoing_transfer = libusb_alloc_transfer(0);
	if (outgoing_transfer == NULL)
	{
		free(packet);
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	c = (USBTransferClosure_t*)malloc(sizeof(USBTransferClosure_t));
	if (c == NULL)
	{
		free(packet);
		libusb_free_transfer(outgoing_transfer);
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	control_transfer = (USBControlTransfer_t*)malloc(sizeof(USBControlTransfer_t));
	if (control_transfer == NULL)
	{
		free(packet);
		libusb_free_transfer(outgoing_transfer);
		free(c);
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	c->device = device;
	c->callback = callback;
	c->closure = closure;
	c->cmd = command;

	// get the transaction id
	ret = usb_get_transaction_id(device, &transaction_id, c);
	if (ret != 0)
	{
		free(packet);
		free(c);
		free(control_transfer);
		libusb_free_transfer(outgoing_transfer);
		mutex_unlock(usb_info->mutex);
		return ret;
	}

	// copy data into the packet
	packet[0] = transaction_id;
	packet[1] = command;
	memcpy(&packet[2], params, param_length);

	// initialize the control transfer and insert it into the ctrl list
	control_transfer->transfer = outgoing_transfer;
	control_transfer->c = c;
	control_transfer->device = device;
	control_transfer->next = usb_info->ctrl_list_head;
	usb_info->ctrl_list_head = control_transfer;
	control_transfer->prev_next = &usb_info->ctrl_list_head;
	if (control_transfer->next != NULL)
	{
		control_transfer->next->prev_next = &control_transfer->next;
	}

	libusb_fill_bulk_transfer(outgoing_transfer, usb_info->devh, usb_info->ctrl_out_ep_address, packet, packet_length, do_transfer_outgoing_callback,
			control_transfer, usb_info->cmd_timeout);
	outgoing_transfer->type = usb_info->ctrl_out_ep_type; // LIBUSB_TRANSFER_TYPE_INTERRUPT or LIBUSB_TRANSFER_TYPE_BULK

	ret = libusb_submit_transfer(outgoing_transfer);
	if (ret != 0)
	{
		// unregister it in the transaction table
		usb_info->transaction_table[transaction_id] = NULL;

		free(packet);
		free(c);
		usb_info->ctrl_list_head = control_transfer->next;
		if (control_transfer->next != NULL)
		{
			control_transfer->next->prev_next = &usb_info->ctrl_list_head;
		}
		free(control_transfer);
		libusb_free_transfer(outgoing_transfer);
		mutex_unlock(usb_info->mutex);
		return usb_libusb_error_to_asphodel(ret);
	}

	mutex_unlock(usb_info->mutex);

	return 0;
}

static void LIBUSB_CALL do_transfer_reset_callback(struct libusb_transfer *transfer)
{
	USBTransferClosure_t *c = (USBTransferClosure_t*)transfer->user_data;
	int status;

	// really no need to lock anything, as this doesn't interact with the device at all

	if (transfer->status == LIBUSB_TRANSFER_TIMED_OUT)
	{
		status = ASPHODEL_TIMEOUT;
	}
	else if (transfer->status == LIBUSB_TRANSFER_CANCELLED)
	{
		status = ASPHODEL_TRANSFER_ERROR;
	}
	else if (transfer->status == LIBUSB_TRANSFER_OVERFLOW)
	{
		status = ASPHODEL_OVERFLOW;
	}
	else
	{
		status = 0;
	}

	if (c->callback != NULL)
	{
		c->callback(status, NULL, 0, c->closure);
	}

	// free the packet and transfer
	free(transfer->buffer);
	libusb_free_transfer(transfer);

	// free the closure;
	free(c);
}

// Start an Asphodel command transfer that does not return (e.g. reset, bootloader jump).
// The specified callback will be called when the transfer is finished.
static int usb_do_transfer_reset(AsphodelDevice_t *device, uint8_t command, const uint8_t *params, size_t param_length, AsphodelTransferCallback_t callback, void * closure)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	USBTransferClosure_t *c;
	int ret;
	struct libusb_transfer * outgoing_transfer;
	int packet_length = (int)param_length + 2;
	uint8_t *packet;

	// can't take the libusb lock in this function, because it is called in callbacks
	mutex_lock(usb_info->mutex);

	if (usb_info->opened == 0)
	{
		// not opened
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_DEVICE_CLOSED;
	}

	if (param_length > usb_info->max_outgoing_param_length)
	{
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	}

	// allocate the outgoing packet
	packet = (uint8_t*)malloc(packet_length);
	if (packet == NULL)
	{
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	outgoing_transfer = libusb_alloc_transfer(0);
	if (outgoing_transfer == NULL)
	{
		free(packet);
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	c = (USBTransferClosure_t*)malloc(sizeof(USBTransferClosure_t));
	if (c == NULL)
	{
		free(packet);
		libusb_free_transfer(outgoing_transfer);
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	c->device = device;
	c->callback = callback;
	c->closure = closure;
	c->cmd = command;

	// copy data into the packet
	packet[0] = 0; // use a fixed transaction id for reset commands, since there will be no reply
	packet[1] = command;
	memcpy(&packet[2], params, param_length);

	libusb_fill_bulk_transfer(outgoing_transfer, usb_info->devh, usb_info->ctrl_out_ep_address, packet, packet_length, do_transfer_reset_callback, c, usb_info->cmd_timeout);
	outgoing_transfer->type = usb_info->ctrl_out_ep_type; // LIBUSB_TRANSFER_TYPE_INTERRUPT or LIBUSB_TRANSFER_TYPE_BULK
	ret = libusb_submit_transfer(outgoing_transfer);
	if (ret != 0)
	{
		free(packet);
		free(c);
		libusb_free_transfer(outgoing_transfer);
		mutex_unlock(usb_info->mutex);
		return usb_libusb_error_to_asphodel(ret);
	}

	mutex_unlock(usb_info->mutex);

	return 0;
}

static void handle_stream_transfer(struct libusb_transfer *transfer)
{
	// NOTE: all checks are handled in the calling function
	USBStreamTransfer_t *stream_transfer = (USBStreamTransfer_t*)transfer->user_data;
	AsphodelDevice_t *device = stream_transfer->device;
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	// handle the data first, regardless of the status
	if (transfer->actual_length != 0)
	{
		if (transfer->actual_length % usb_info->stream_packet_length != 0)
		{
			if (stream_transfer->streaming_callback != NULL)
			{
				stream_transfer->streaming_callback(ASPHODEL_BAD_STREAM_PACKET_SIZE, NULL, 0, 0, stream_transfer->streaming_closure);
			}
			else
			{
				mutex_lock(usb_info->mutex);
				usb_error_report(device, ASPHODEL_BAD_STREAM_PACKET_SIZE);
				mutex_unlock(usb_info->mutex);
			}
		}
		else
		{
			if (stream_transfer->streaming_callback != NULL)
			{
				stream_transfer->streaming_callback(0, transfer->buffer, usb_info->stream_packet_length,
					transfer->actual_length / usb_info->stream_packet_length, stream_transfer->streaming_closure);
			}
		}
	}

	if (transfer->status == LIBUSB_TRANSFER_COMPLETED)
	{
		// nothing to do
	}
	else if (transfer->status == LIBUSB_TRANSFER_TIMED_OUT)
	{
		// NOTE: only treat as a timeout if it didn't contain data
		if (transfer->actual_length == 0)
		{
			if (stream_transfer->streaming_callback != NULL)
			{
				stream_transfer->streaming_callback(ASPHODEL_TIMEOUT, NULL, 0, 0, stream_transfer->streaming_closure);
			}
			else
			{
				mutex_lock(usb_info->mutex);
				usb_error_report(device, ASPHODEL_TIMEOUT);
				if (usb_info->streaming)
				{
					usb_stop_streaming_packets_locked(usb_info);
				}
				// NOTE: usb_stop_streaming_packets_locked() frees the transfer and its buffer, so nothing more to do
				mutex_unlock(usb_info->mutex);
				return;
			}
		}
	}
	else if (transfer->status == LIBUSB_TRANSFER_CANCELLED)
	{
		// Spurious cancel; can happen on windows when cancelling transfers on other endpoints. Reason not fully understood.
		// ignore and it will get resubmitted at the end of the function
	}
	else
	{
		// error; mark as cancelled
		stream_transfer->transfer = NULL;

		if (stream_transfer->streaming_callback != NULL)
		{
			stream_transfer->streaming_callback(ASPHODEL_TRANSFER_ERROR, NULL, 0, 0, stream_transfer->streaming_closure);
		}
		else
		{
			mutex_lock(usb_info->mutex);
			usb_error_report(device, ASPHODEL_TRANSFER_ERROR);
			mutex_unlock(usb_info->mutex);
		}

		free(transfer->buffer);
		libusb_free_transfer(transfer);
		return;
	}

	// see if the transfer should be resubmitted
	if (transfer->user_data == NULL)
	{
		// cancelled in the callback
		free(transfer->buffer);
		libusb_free_transfer(transfer);
	}
	else
	{
		int ret;

		// was not cancelled in the callback; submit the transfer again
		stream_transfer->finished = 0;
		ret = libusb_submit_transfer(transfer);
		if (ret != 0)
		{
			int error_code = usb_libusb_error_to_asphodel(ret);

			// got an error: mark as cancelled
			stream_transfer->transfer = NULL;

			if (stream_transfer->streaming_callback != NULL)
			{
				stream_transfer->streaming_callback(error_code, NULL, 0, 0, stream_transfer->streaming_closure);
			}
			else
			{
				mutex_lock(usb_info->mutex);
				usb_error_report(device, error_code);
				mutex_unlock(usb_info->mutex);
			}

			free(transfer->buffer);
			libusb_free_transfer(transfer);
		}
	}
}

static void LIBUSB_CALL stream_transfer_cb(struct libusb_transfer *transfer)
{
	USBStreamTransfer_t *stream_transfer = (USBStreamTransfer_t*)transfer->user_data;
	AsphodelDevice_t *device;
	USBDeviceInfo_t *usb_info;

	if (stream_transfer == NULL)
	{
		// we've been forcably cancelled, bail out
		free(transfer->buffer);
		libusb_free_transfer(transfer);
		return;
	}

	device = stream_transfer->device;
	usb_info = (USBDeviceInfo_t*)device->implementation_info;

	stream_transfer->finished = 1;

	if (&usb_info->stream_transfer_array[usb_info->next_stream_transfer_index] == stream_transfer)
	{
		// this is the transfer that we're waiting for
		handle_stream_transfer(transfer);

		if (usb_info->stream_transfer_array == NULL)
		{
			// streaming was cancelled in the callback
			return;
		}

		while (1)
		{
			USBStreamTransfer_t *next_stream_transfer;

			// increment the index
			usb_info->next_stream_transfer_index += 1;
			if (usb_info->next_stream_transfer_index >= usb_info->stream_transfer_count)
			{
				usb_info->next_stream_transfer_index = 0;
			}

			// see if the next transfer is finished and needs to be handled
			next_stream_transfer = &usb_info->stream_transfer_array[usb_info->next_stream_transfer_index];

			if (next_stream_transfer == stream_transfer)
			{
				// wrapped all the way around
				break;
			}

			if (next_stream_transfer->finished)
			{
				if (next_stream_transfer->transfer != NULL)
				{
					handle_stream_transfer(next_stream_transfer->transfer);
				}
			}
			else
			{
				// transfer is not yet finished; its callback will be called when it is ready
				break;
			}
		}
	}
}

// Start a continuous set of stream transfers. The specified callback will be called after each transfer is
// finished. The timeout is specified in milliseconds. The count specifies how many packets should be lumped
// together, if possible. The poll_device function must be called continually to receive data.
static int usb_start_streaming_packets(AsphodelDevice_t *device, int packet_count, int transfer_count, unsigned int timeout, AsphodelStreamingCallback_t callback, void * closure)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	int i;
	int bundle_size = packet_count * (int)usb_info->stream_packet_length;

	if (packet_count < 1 || transfer_count < 1)
	{
		return ASPHODEL_BAD_PARAMETER;
	}

	libusb_lock_events(ctx); // needed because stream callbacks don't use the device lock
	mutex_lock(usb_info->mutex);

	if (usb_info->opened == 0)
	{
		// not opened
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_DEVICE_CLOSED;
	}

	if (usb_info->streaming != 0)
	{
		// stop streaming, so it can be restarted
		usb_stop_streaming_packets_locked(usb_info);
	}

	usb_info->stream_transfer_array = (USBStreamTransfer_t*)malloc(sizeof(USBStreamTransfer_t) * transfer_count);
	if (usb_info->stream_transfer_array == NULL)
	{
		usb_info->stream_transfer_count = 0;
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NO_MEM;
	}
	usb_info->stream_transfer_count = transfer_count;

	// create transfers
	for (i = 0; i < transfer_count; i++)
	{
		uint8_t *buffer;
		USBStreamTransfer_t *stream_transfer = &usb_info->stream_transfer_array[i];
		struct libusb_transfer *transfer = libusb_alloc_transfer(0);

		if (transfer == NULL)
		{
			// out of memory (presumably)
			int j;

			for (j = 0; j < i; j++)
			{
				free(usb_info->stream_transfer_array[j].transfer->buffer);
				libusb_free_transfer(usb_info->stream_transfer_array[j].transfer);
			}
			free(usb_info->stream_transfer_array);
			usb_info->stream_transfer_array = NULL;
			usb_info->stream_transfer_count = 0;
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			return ASPHODEL_NO_MEM;
		}

		buffer = (uint8_t*)malloc(bundle_size);
		if (buffer == NULL)
		{
			int j;

			for (j = 0; j < i; j++)
			{
				free(usb_info->stream_transfer_array[j].transfer->buffer);
				libusb_free_transfer(usb_info->stream_transfer_array[j].transfer);
			}

			// also free the transfer for the present iteration (i.e. the one that has no packet)
			libusb_free_transfer(transfer);

			free(usb_info->stream_transfer_array);
			usb_info->stream_transfer_array = NULL;
			usb_info->stream_transfer_count = 0;
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			return ASPHODEL_NO_MEM;
		}

		stream_transfer->transfer = transfer;
		stream_transfer->device = device;
		stream_transfer->streaming_callback = callback;
		stream_transfer->streaming_closure = closure;

		libusb_fill_bulk_transfer(transfer, usb_info->devh, usb_info->stream_ep_address, buffer, bundle_size, stream_transfer_cb, stream_transfer, timeout);
		transfer->type = usb_info->stream_ep_type; // LIBUSB_TRANSFER_TYPE_INTERRUPT or LIBUSB_TRANSFER_TYPE_BULK
	}

	// start transfers
	usb_info->next_stream_transfer_index = 0;
	for (i = 0; i < transfer_count; i++)
	{
		int ret;

		usb_info->stream_transfer_array[i].finished = 0;
		ret = libusb_submit_transfer(usb_info->stream_transfer_array[i].transfer);
		if (ret != 0)
		{
			// error
			int j;
			for (j = 0; j < transfer_count; j++)
			{
				USBStreamTransfer_t *stream_transfer = &usb_info->stream_transfer_array[j];

				if (j < i)
				{
					struct libusb_transfer *transfer = stream_transfer->transfer;
					if (transfer != NULL)
					{
						transfer->user_data = NULL;

						// don't check the return value, because there's really nothing that can be done differently if it fails
						libusb_cancel_transfer(transfer);
					}
				}
				else
				{
					// the transfer was not yet submitted; free it
					free(stream_transfer->transfer->buffer);
					libusb_free_transfer(stream_transfer->transfer);
				}
			}

			free(usb_info->stream_transfer_array);
			usb_info->stream_transfer_array = NULL;
			usb_info->stream_transfer_count = 0;
			mutex_unlock(usb_info->mutex);
			libusb_unlock_events(ctx);
			return usb_libusb_error_to_asphodel(ret);
		}
	}

	usb_info->streaming = 1;

	mutex_unlock(usb_info->mutex);
	libusb_unlock_events(ctx);

	return 0;
}

static void usb_stop_streaming_packets_locked(USBDeviceInfo_t *usb_info) // assumes already streaming, and MUST be called with BOTH the libusb event lock and the device mutex
{
	int i;

	usb_info->streaming = 0;

	// cancel transfers (freeing will happen in their callbacks)
	for (i = 0; i < usb_info->stream_transfer_count; i++)
	{
		USBStreamTransfer_t *stream_transfer = &usb_info->stream_transfer_array[i];
		struct libusb_transfer *transfer = stream_transfer->transfer;

		if (transfer != NULL)
		{
			if (stream_transfer->finished)
			{
				// free the transfer
				free(transfer->buffer);
				libusb_free_transfer(transfer);
			}
			else
			{
				transfer->user_data = NULL;

				// don't check the return value, because there's really nothing that can be done differently if it fails
				libusb_cancel_transfer(transfer);
			}
		}
	}

	usb_info->stream_transfer_count = 0;
	free(usb_info->stream_transfer_array);
	usb_info->stream_transfer_array = NULL;
}

// Stop the transfers started with start_streaming_packets.
static void usb_stop_streaming_packets(AsphodelDevice_t *device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->streaming)
	{
		usb_stop_streaming_packets_locked(usb_info);
	}

	mutex_unlock(usb_info->mutex);
	libusb_unlock_events(ctx);
}

// Get streaming packets in a blocking fashion. Do not mix with start_streaming_packets(). The buffer must be able
// to hold at least count bytes. NOTE: count should be a multiple of get_stream_packet_length().
static int usb_get_stream_packets_blocking(AsphodelDevice_t *device, uint8_t *buffer, int *count, unsigned int timeout)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	int length = *count;

	if (usb_info->opened)
	{
		int ret = libusb_bulk_transfer(usb_info->devh, usb_info->stream_ep_address, buffer, length, count, timeout);

		if (ret == LIBUSB_ERROR_TIMEOUT)
		{
			// not really an error if we actually got some data
			if (*count != 0)
			{
				return ASPHODEL_SUCCESS;
			}
		}

		return usb_libusb_error_to_asphodel(ret);
	}
	else
	{
		return ASPHODEL_DEVICE_CLOSED;
	}
}

// Return the maximum length of the incoming parameters on this device.
static size_t usb_get_max_incoming_param_length(AsphodelDevice_t * device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	return usb_info->max_incoming_param_length;
}

// Return the maximum length of the outgoing parameters on this device.
static size_t usb_get_max_outgoing_param_length(AsphodelDevice_t * device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	return usb_info->max_outgoing_param_length;
}

// Return the size of individual stream packets. Data collected with read_stream_packets will be a multiple of
// this size.
static size_t usb_get_stream_packet_length(AsphodelDevice_t * device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	return usb_info->stream_packet_length;
}

// Set the connect callback. If the device is already connected, this will immediately call the callback. The
// callback will be called whenever the device experiences a connect or disconnect. Call this function with a NULL
// callback to remove any previously registered callback. This function is implemented for all device types, but
// really only makes sense in the context of remote devices. Non-remote devices will immediately call the callback
// with the connect parameter set. Non-remote devices will never have a disconnect event.
static int usb_set_connect_callback(AsphodelDevice_t * device, AsphodelConnectCallback_t callback, void * closure)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	if (!asphodel_supports_remote_commands(device))
	{
		// not a remote device, call the callback immediately (since it's already "connected")
		if (callback != NULL)
		{
			callback(0, 1, closure);
		}

		return 0;
	}

	mutex_lock(usb_info->mutex);

	usb_info->connect_callback = callback;
	usb_info->connect_closure = closure;

	if (usb_info->connected)
	{
		if (callback != NULL)
		{
			callback(0, 1, closure);
		}
	}

	mutex_unlock(usb_info->mutex);

	return 0;
}

static void usb_wait_for_connect_cb(int status, int connected, void * closure)
{
	WaitForFinishClosure_t *c = (WaitForFinishClosure_t*)closure;

	if (status != 0 || connected)
	{
		c->status = status;
		c->completed = 1;
	}
}

// This will wait for the device to be connected. NOTE: this will override any existing callback set with
// set_connect_callback(). This function is implemented for all device types, but really only makes sense in the
// context of remote devices. Non-remote devices will return immediately.
static int usb_wait_for_connect(AsphodelDevice_t * device, unsigned int timeout)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	WaitForFinishClosure_t c;
	clock_time_t deadline;

	if (!asphodel_supports_remote_commands(device))
	{
		// not a remote device, just return (since it's already "connected")
		return 0;
	}

	// init the deadline
	clock_get_end_time(&deadline, (int)timeout);

	c.status = ASPHODEL_TIMEOUT;
	c.completed = 0;

	mutex_lock(usb_info->mutex);
	if (usb_info->opened == 0)
	{
		mutex_unlock(usb_info->mutex);
		return ASPHODEL_DEVICE_CLOSED;
	}
	mutex_unlock(usb_info->mutex);

	// poll the device to make sure there's nothing pending
	device->poll_device(device, 1, NULL);

	// register the connect callback
	usb_set_connect_callback(device, usb_wait_for_connect_cb, &c);

	if (!c.completed)
	{
		// need to poll until finished or timed out
		while (1)
		{
			int remaining = clock_milliseconds_remaining(&deadline);

			if (remaining)
			{
				// poll the device for the timeout period (will abort early if completed)
				device->poll_device(device, remaining, &c.completed); // this is ok because we're not in a locked context

				if (c.completed)
				{
					// finished
					break;
				}
			}
			else
			{
				c.status = ASPHODEL_TIMEOUT;
				break;
			}
		}
	}

	// unregister the callback
	usb_set_connect_callback(device, NULL, NULL);

	return c.status;
}

// Get the various lengths for any remote device created from this radio device.
static int usb_get_remote_lengths(AsphodelDevice_t * device, size_t *max_incoming_param_length, size_t *max_outgoing_param_length, size_t *stream_packet_length)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;
	const struct libusb_interface *iface;
	const struct libusb_interface_descriptor *iface_desc;
	int interface_number;
	int interface_altsetting;
	const struct libusb_endpoint_descriptor *ctrl_in_ep;
	const struct libusb_endpoint_descriptor *ctrl_out_ep;
	const struct libusb_endpoint_descriptor *stream_ep;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (!asphodel_supports_radio_commands(device))
	{
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NOT_SUPPORTED;
	}

	// NOTE: the remote interface and endpoints have already been checked in create_usb_asphodel_device()

	if (usb_info->remote_same_interface)
	{
		interface_number = usb_info->interface_number;
		iface = &usb_info->config_desc->interface[interface_number];
		interface_altsetting = usb_info->interface_altsetting;

		iface_desc = &iface->altsetting[interface_altsetting];

		ctrl_in_ep = &iface_desc->endpoint[3];
		ctrl_out_ep = &iface_desc->endpoint[4];
		stream_ep = &iface_desc->endpoint[5];
	}
	else
	{
		interface_number = 1;
		iface = &usb_info->config_desc->interface[interface_number];
		interface_altsetting = 0;

		iface_desc = &iface->altsetting[interface_altsetting];

		ctrl_in_ep = &iface_desc->endpoint[0];
		ctrl_out_ep = &iface_desc->endpoint[1];
		stream_ep = &iface_desc->endpoint[2];
	}

	if (max_incoming_param_length != NULL)
	{
		*max_incoming_param_length = ctrl_in_ep->wMaxPacketSize - 4;
	}

	if (max_outgoing_param_length != NULL)
	{
		*max_outgoing_param_length = ctrl_out_ep->wMaxPacketSize - 3;
	}

	if (stream_packet_length != NULL)
	{
		*stream_packet_length = stream_ep->wMaxPacketSize;
	}

	mutex_unlock(usb_info->mutex);
	libusb_unlock_events(ctx);

	return 0;
}

// Return the radio's remote device. This function will return an error for non-radio devices. The device should be
// freed with free_device() as usual.
static int usb_get_remote_device(AsphodelDevice_t * device, struct AsphodelDevice_t **remote_device)
{
	int ret;
	AsphodelDevice_t *d;
	USBDeviceInfo_t *remote_usb_info;
	USBDeviceInfo_t *original_usb_info = (USBDeviceInfo_t*)device->implementation_info;
	char *location_string;
	size_t orig_location_len;
	const struct libusb_interface *iface;
	const struct libusb_interface_descriptor *iface_desc;

	libusb_lock_events(ctx);
	mutex_lock(original_usb_info->mutex);

	if (!asphodel_supports_radio_commands(device))
	{
		mutex_unlock(original_usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_BAD_PARAMETER;
	}

	d = (AsphodelDevice_t*)malloc(sizeof(AsphodelDevice_t));
	if (d == NULL)
	{
		// out of memory
		mutex_unlock(original_usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NO_MEM;
	}

	remote_usb_info = (USBDeviceInfo_t*)malloc(sizeof(USBDeviceInfo_t));
	if (remote_usb_info == NULL)
	{
		// out of memory
		free(d);
		mutex_unlock(original_usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NO_MEM;
	}

	ret = mutex_init(&remote_usb_info->mutex);
	if (ret != 0)
	{
		free(d);
		free(remote_usb_info);
		mutex_unlock(original_usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NO_MEM;
	}

	// make location string (add "-remote" to the original)
	orig_location_len = strlen(device->location_string);
	location_string = (char *)malloc(orig_location_len + 7 + 1);
	if (location_string == NULL)
	{
		free(d);
		mutex_destroy(&remote_usb_info->mutex);
		free(remote_usb_info);
		mutex_unlock(original_usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_NO_MEM;
	}
	memcpy(location_string, device->location_string, orig_location_len + 1);
	memcpy(&location_string[orig_location_len], "-remote", 7 + 1);

	// don't bother with remote_usb_info->device_desc, as it's only used for the serial number descriptor (i.e. not applicable)

	remote_usb_info->shared_device = original_usb_info->shared_device;
	usb_ref_shared_device(remote_usb_info->shared_device);

	remote_usb_info->config_desc = NULL;

	d->protocol_type = ASPHODEL_PROTOCOL_TYPE_REMOTE;
	d->location_string = location_string;
	d->open_device = usb_open_device;
	d->close_device = usb_close_device;
	d->free_device = usb_free_device;
	d->get_serial_number = usb_get_serial_number;
	d->do_transfer = usb_do_transfer;
	d->do_transfer_reset = usb_do_transfer_reset;
	d->start_streaming_packets = usb_start_streaming_packets;
	d->stop_streaming_packets = usb_stop_streaming_packets;
	d->get_stream_packets_blocking = usb_get_stream_packets_blocking;
	d->get_max_incoming_param_length = usb_get_max_incoming_param_length;
	d->get_max_outgoing_param_length = usb_get_max_outgoing_param_length;
	d->get_stream_packet_length = usb_get_stream_packet_length;
	d->poll_device = usb_poll_device;
	d->set_connect_callback = usb_set_connect_callback;
	d->wait_for_connect = usb_wait_for_connect;
	d->get_remote_device = usb_get_remote_device;
	d->reconnect_device = usb_reconnect_remote;
	d->error_callback = NULL;
	d->error_closure = NULL;
	d->reconnect_device_bootloader = usb_reconnect_remote_boot;
	d->reconnect_device_application = usb_reconnect_remote_app;
	d->implementation_info = remote_usb_info;
	d->transport_type = "usb";
	d->get_remote_lengths = usb_get_remote_lengths;
	memset(d->reserved, 0, sizeof(d->reserved));

	remote_usb_info->opened = 0;
	remote_usb_info->streaming = 0;
	remote_usb_info->connected = 0;
	remote_usb_info->devh = NULL;
	remote_usb_info->config_desc = NULL; // unneeded, not worth copying over
	remote_usb_info->serial_number = NULL;
	remote_usb_info->cmd_timeout = 300; // 3x default timeout
	memset(remote_usb_info->transaction_table, 0, sizeof(remote_usb_info->transaction_table));
	remote_usb_info->last_transaction_id = 0;
	remote_usb_info->ctrl_list_head = NULL;
	remote_usb_info->status_transfer = NULL;
	remote_usb_info->connect_callback = NULL;
	remote_usb_info->connect_closure = NULL;
	remote_usb_info->remote_same_interface = 0; // not applicable

	// NOTE: the remote interface and endpoints have already been checked in create_usb_asphodel_device()

	if (original_usb_info->remote_same_interface)
	{
		remote_usb_info->interface_number = original_usb_info->interface_number;
		iface = &original_usb_info->config_desc->interface[remote_usb_info->interface_number];
		remote_usb_info->interface_altsetting = original_usb_info->interface_altsetting;
		remote_usb_info->interface_num_altsetting = original_usb_info->interface_num_altsetting;
		iface_desc = &iface->altsetting[remote_usb_info->interface_altsetting];

		remote_usb_info->ctrl_in_ep = &iface_desc->endpoint[3];
		remote_usb_info->ctrl_out_ep = &iface_desc->endpoint[4];
		remote_usb_info->stream_ep = &iface_desc->endpoint[5];
		remote_usb_info->status_ep = &iface_desc->endpoint[6];
	}
	else
	{
		remote_usb_info->interface_number = 1;
		iface = &original_usb_info->config_desc->interface[remote_usb_info->interface_number];
		remote_usb_info->interface_altsetting = 0;
		remote_usb_info->interface_num_altsetting = iface->num_altsetting;
		iface_desc = &iface->altsetting[remote_usb_info->interface_altsetting];

		remote_usb_info->ctrl_in_ep = &iface_desc->endpoint[0];
		remote_usb_info->ctrl_out_ep = &iface_desc->endpoint[1];
		remote_usb_info->stream_ep = &iface_desc->endpoint[2];
		remote_usb_info->status_ep = &iface_desc->endpoint[3];
	}

	remote_usb_info->max_incoming_param_length = remote_usb_info->ctrl_in_ep->wMaxPacketSize - 4;
	remote_usb_info->max_outgoing_param_length = remote_usb_info->ctrl_out_ep->wMaxPacketSize - 3;
	remote_usb_info->stream_packet_length = remote_usb_info->stream_ep->wMaxPacketSize;
	remote_usb_info->status_packet_length = remote_usb_info->status_ep->wMaxPacketSize;

	// take the maximum length
	if (remote_usb_info->ctrl_in_ep->wMaxPacketSize > remote_usb_info->ctrl_out_ep->wMaxPacketSize)
	{
		remote_usb_info->control_packet_transfer_length = remote_usb_info->ctrl_in_ep->wMaxPacketSize;
	}
	else
	{
		remote_usb_info->control_packet_transfer_length = remote_usb_info->ctrl_out_ep->wMaxPacketSize;
	}

	remote_usb_info->ctrl_in_ep_address = remote_usb_info->ctrl_in_ep->bEndpointAddress;
	remote_usb_info->ctrl_out_ep_address = remote_usb_info->ctrl_out_ep->bEndpointAddress;
	remote_usb_info->stream_ep_address = remote_usb_info->stream_ep->bEndpointAddress;
	remote_usb_info->status_ep_address = remote_usb_info->status_ep->bEndpointAddress;

	remote_usb_info->ctrl_in_ep_type = remote_usb_info->ctrl_in_ep->bmAttributes & 0x03;
	remote_usb_info->ctrl_out_ep_type = remote_usb_info->ctrl_out_ep->bmAttributes & 0x03;
	remote_usb_info->stream_ep_type = remote_usb_info->stream_ep->bmAttributes & 0x03;
	remote_usb_info->status_ep_type = remote_usb_info->status_ep->bmAttributes & 0x03;

	*remote_device = d;

	mutex_unlock(original_usb_info->mutex);
	libusb_unlock_events(ctx);

	return 0;
}

// For internal use only. Used to convert non-blocking functions to blocking ones by calling this in a loop.
static int usb_poll_device(AsphodelDevice_t * device, int milliseconds, int *completed)
{
	int ret;
	struct timeval tv;
	tv.tv_sec = milliseconds / 1000;
	tv.tv_usec = (milliseconds % 1000) * 1000;

	(void)device; // suppress unused parameter warning

	ret = libusb_handle_events_timeout_completed(ctx, &tv, completed);
	return usb_libusb_error_to_asphodel(ret);
}

ASPHODEL_API int asphodel_usb_poll_devices(int milliseconds)
{
	int ret;
	struct timeval tv;
	tv.tv_sec = milliseconds / 1000;
	tv.tv_usec = (milliseconds % 1000) * 1000;

	ret = libusb_handle_events_timeout_completed(ctx, &tv, NULL);
	return usb_libusb_error_to_asphodel(ret);
}

ASPHODEL_API int asphodel_usb_init(void)
{
	int ret;

	clock_init();

	ret = libusb_init(&ctx);

	libusb_set_option(ctx, LIBUSB_OPTION_LOG_LEVEL, LIBUSB_LOG_LEVEL_INFO);

	return usb_libusb_error_to_asphodel(ret);
}

ASPHODEL_API void asphodel_usb_deinit(void)
{
	if (ctx)
	{
		libusb_exit(ctx);
		ctx = NULL;
	}

	clock_deinit();
}

static int create_usb_asphodel_device(libusb_device *usbdev, AsphodelDevice_t **device)
{
	int ret;
	AsphodelDevice_t *d = (AsphodelDevice_t*)malloc(sizeof(AsphodelDevice_t));
	USBDeviceInfo_t *usb_info;
	char *location_string;
	uint8_t bus_number;
	uint8_t port_numbers[7]; // maximum depth for USB 3.0 and below is 7
	int port_numbers_len;
	InterfaceInfo_t interface_info[2]; // 2 is the maximum number of interfaces to open for a device
	int interface_count = 0; // will be incremented

	struct libusb_config_descriptor *config;
	const struct libusb_interface *iface;
	const struct libusb_interface_descriptor *iface_desc;

	if (d == NULL)
	{
		// out of memory
		return ASPHODEL_NO_MEM;
	}

	usb_info = (USBDeviceInfo_t*)malloc(sizeof(USBDeviceInfo_t));

	if (usb_info == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	ret = mutex_init(&usb_info->mutex);
	if (ret != 0)
	{
		free(d);
		free(usb_info);
		return ASPHODEL_NO_MEM;
	}

	location_string = (char *)malloc(MAX_LOCATION_STRING_LENGTH);
	if (location_string == NULL)
	{
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		return ASPHODEL_NO_MEM;
	}

	ret = libusb_get_device_descriptor(usbdev, &usb_info->device_desc);
	if (ret != 0)
	{
		// error
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return usb_libusb_error_to_asphodel(ret);
	}

	// NOTE: all Asphodel USB devices have a bConfigurationValue of 1
	ret = libusb_get_config_descriptor_by_value(usbdev, 1, &config);
	if (ret != 0)
	{
		// error
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return usb_libusb_error_to_asphodel(ret);
	}

	// create a location string
	bus_number = libusb_get_bus_number(usbdev);
	port_numbers_len = libusb_get_port_numbers(usbdev, port_numbers, sizeof(port_numbers));
	if (port_numbers_len > 0)
	{
		// success
		int i;
		// format is USB:bus_number:portnum.portnum.portnum
		snprintf(location_string, MAX_LOCATION_STRING_LENGTH, "USB:%d:", bus_number);
		for (i = 0; i < port_numbers_len; i++)
		{
			size_t len = strlen(location_string);
			if (len + 1 >= MAX_LOCATION_STRING_LENGTH)
			{
				// already filled
				break;
			}

			if (i == 0)
			{
				snprintf(location_string + len, MAX_LOCATION_STRING_LENGTH - len, "%d", port_numbers[i]);
			}
			else
			{
				snprintf(location_string + len, MAX_LOCATION_STRING_LENGTH - len, ".%d", port_numbers[i]);
			}
		}
	}
	else
	{
		// error
		// format is USB:bus_number:ERROR
		snprintf(location_string, MAX_LOCATION_STRING_LENGTH, "USB:%d:ERROR", bus_number);
	}

	d->protocol_type = usb_info->device_desc.bDeviceProtocol & ~ASPHODEL_PROTOCOL_TYPE_REMOTE; // don't include remote, if it's set
	d->location_string = location_string;
	d->open_device = usb_open_device;
	d->close_device = usb_close_device;
	d->free_device = usb_free_device;
	d->get_serial_number = usb_get_serial_number;
	d->do_transfer = usb_do_transfer;
	d->do_transfer_reset = usb_do_transfer_reset;
	d->start_streaming_packets = usb_start_streaming_packets;
	d->stop_streaming_packets = usb_stop_streaming_packets;
	d->get_stream_packets_blocking = usb_get_stream_packets_blocking;
	d->get_max_incoming_param_length = usb_get_max_incoming_param_length;
	d->get_max_outgoing_param_length = usb_get_max_outgoing_param_length;
	d->get_stream_packet_length = usb_get_stream_packet_length;
	d->poll_device = usb_poll_device;
	d->set_connect_callback = usb_set_connect_callback;
	d->wait_for_connect = usb_wait_for_connect;
	d->get_remote_device = usb_get_remote_device;
	d->reconnect_device = usb_reconnect_device;
	d->error_callback = NULL;
	d->error_closure = NULL;
	d->reconnect_device_bootloader = usb_reconnect_device; // no special handling needed
	d->reconnect_device_application = usb_reconnect_device; // no special handling needed
	d->implementation_info = usb_info;
	d->transport_type = "usb";
	d->get_remote_lengths = usb_get_remote_lengths;
	memset(d->reserved, 0, sizeof(d->reserved));

	usb_info->opened = 0;
	usb_info->streaming = 0;
	usb_info->connected = 1;
	usb_info->devh = NULL;
	usb_info->config_desc = config;
	usb_info->serial_number = NULL;
	usb_info->cmd_timeout = 100; // default timeout
	memset(usb_info->transaction_table, 0, sizeof(usb_info->transaction_table));
	usb_info->last_transaction_id = 0;
	usb_info->ctrl_list_head = NULL;
	usb_info->status_transfer = NULL;
	usb_info->connect_callback = NULL;
	usb_info->connect_closure = NULL;

	// get the interface
	usb_info->interface_number = 0;
	if (config->bNumInterfaces <= usb_info->interface_number)
	{
		// not enough interfaces
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	// check the alternate settings on the interface
	iface = &config->interface[usb_info->interface_number];
	usb_info->interface_altsetting = 0;
	usb_info->interface_num_altsetting = iface->num_altsetting;
	if (iface->num_altsetting <= usb_info->interface_altsetting)
	{
		// not enough alternate settings
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	interface_info[interface_count].number = usb_info->interface_number;
	interface_info[interface_count].altsetting = usb_info->interface_altsetting;
	interface_info[interface_count].num_altsetting = usb_info->interface_num_altsetting;
	interface_count += 1;

	// check the number of endpoints on the interface
	iface_desc = &iface->altsetting[usb_info->interface_altsetting];
	if (iface_desc->bNumEndpoints < 3)
	{
		// not enough endpoints
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	usb_info->ctrl_in_ep = &iface_desc->endpoint[0];
	usb_info->ctrl_out_ep = &iface_desc->endpoint[1];
	usb_info->stream_ep = &iface_desc->endpoint[2];

	// there is an overhead of 2 bytes on the control endpoints
	usb_info->max_incoming_param_length = usb_info->ctrl_in_ep->wMaxPacketSize - 2;
	usb_info->max_outgoing_param_length = usb_info->ctrl_out_ep->wMaxPacketSize - 2;
	usb_info->stream_packet_length = usb_info->stream_ep->wMaxPacketSize;

	// take the maximum length
	if (usb_info->ctrl_in_ep->wMaxPacketSize > usb_info->ctrl_out_ep->wMaxPacketSize)
	{
		usb_info->control_packet_transfer_length = usb_info->ctrl_in_ep->wMaxPacketSize;
	}
	else
	{
		usb_info->control_packet_transfer_length = usb_info->ctrl_out_ep->wMaxPacketSize;
	}

	usb_info->ctrl_in_ep_address = usb_info->ctrl_in_ep->bEndpointAddress;
	usb_info->ctrl_out_ep_address = usb_info->ctrl_out_ep->bEndpointAddress;
	usb_info->stream_ep_address = usb_info->stream_ep->bEndpointAddress;

	if ((usb_info->ctrl_in_ep_address & 0x80) != LIBUSB_ENDPOINT_IN || (usb_info->ctrl_out_ep_address & 0x80) != LIBUSB_ENDPOINT_OUT ||
		(usb_info->stream_ep_address & 0x80) != LIBUSB_ENDPOINT_IN)
	{
		// an endpoint isn't the right direction
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	usb_info->ctrl_in_ep_type = usb_info->ctrl_in_ep->bmAttributes & 0x03;
	usb_info->ctrl_out_ep_type = usb_info->ctrl_out_ep->bmAttributes & 0x03;
	usb_info->stream_ep_type = usb_info->stream_ep->bmAttributes & 0x03;

	if ((usb_info->ctrl_in_ep_type != LIBUSB_TRANSFER_TYPE_INTERRUPT && usb_info->ctrl_in_ep_type != LIBUSB_TRANSFER_TYPE_BULK) ||
		(usb_info->ctrl_out_ep_type != LIBUSB_TRANSFER_TYPE_INTERRUPT && usb_info->ctrl_out_ep_type != LIBUSB_TRANSFER_TYPE_BULK) ||
		(usb_info->stream_ep_type != LIBUSB_TRANSFER_TYPE_INTERRUPT && usb_info->stream_ep_type != LIBUSB_TRANSFER_TYPE_BULK))
	{
		// an endpoint isn't the right type
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	if (asphodel_supports_radio_commands(d))
	{
		// check radio descriptors now rather than later

		const struct libusb_endpoint_descriptor *radio_in_ep;
		const struct libusb_endpoint_descriptor *radio_out_ep;
		const struct libusb_endpoint_descriptor *radio_stream_ep;
		const struct libusb_endpoint_descriptor *radio_status_ep;

		if ((usb_info->device_desc.bDeviceProtocol & ASPHODEL_PROTOCOL_TYPE_REMOTE) != 0)
		{
			// radio and remote are contained in the same interface
			usb_info->remote_same_interface = 1;

			if (iface_desc->bNumEndpoints < 7)
			{
				// not enough endpoints
				libusb_free_config_descriptor(config);
				free(d);
				mutex_destroy(&usb_info->mutex);
				free(usb_info);
				free(location_string);
				return ASPHODEL_INVALID_DESCRIPTOR;
			}

			radio_in_ep = &iface_desc->endpoint[3];
			radio_out_ep = &iface_desc->endpoint[4];
			radio_stream_ep = &iface_desc->endpoint[5];
			radio_status_ep = &iface_desc->endpoint[6];
		}
		else
		{
			// radio and remote are contained in different interfaces
			usb_info->remote_same_interface = 0;

			const struct libusb_interface *radio_iface;
			const struct libusb_interface_descriptor *radio_iface_desc;

			if (config->bNumInterfaces < 2)
			{
				// not enough interfaces
				libusb_free_config_descriptor(config);
				free(d);
				mutex_destroy(&usb_info->mutex);
				free(usb_info);
				free(location_string);
				return ASPHODEL_INVALID_DESCRIPTOR;
			}

			radio_iface = &config->interface[1];
			if (radio_iface->num_altsetting == 0)
			{
				// not enough alternate settings
				libusb_free_config_descriptor(config);
				free(d);
				mutex_destroy(&usb_info->mutex);
				free(usb_info);
				free(location_string);
				return ASPHODEL_INVALID_DESCRIPTOR;
			}

			// check the number of endpoints on the interface
			radio_iface_desc = &radio_iface->altsetting[0];
			if (radio_iface_desc->bNumEndpoints < 4)
			{
				// not enough endpoints
				libusb_free_config_descriptor(config);
				free(d);
				mutex_destroy(&usb_info->mutex);
				free(usb_info);
				free(location_string);
				return ASPHODEL_INVALID_DESCRIPTOR;
			}

			interface_info[interface_count].number = 1;
			interface_info[interface_count].altsetting = 0;
			interface_info[interface_count].num_altsetting = radio_iface->num_altsetting;
			interface_count += 1;

			radio_in_ep = &radio_iface_desc->endpoint[0];
			radio_out_ep = &radio_iface_desc->endpoint[1];
			radio_stream_ep = &radio_iface_desc->endpoint[2];
			radio_status_ep = &radio_iface_desc->endpoint[3];
		}

		if ((radio_in_ep->bEndpointAddress & 0x80) != LIBUSB_ENDPOINT_IN || (radio_out_ep->bEndpointAddress & 0x80) != LIBUSB_ENDPOINT_OUT ||
			(radio_stream_ep->bEndpointAddress & 0x80) != LIBUSB_ENDPOINT_IN || (radio_status_ep->bEndpointAddress & 0x80) != LIBUSB_ENDPOINT_IN)
		{
			// an endpoint isn't the right direction
			libusb_free_config_descriptor(config);
			free(d);
			mutex_destroy(&usb_info->mutex);
			free(usb_info);
			free(location_string);
			return ASPHODEL_INVALID_DESCRIPTOR;
		}

		if (((radio_in_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_INTERRUPT && (radio_in_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_BULK) ||
			((radio_out_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_INTERRUPT && (radio_out_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_BULK) ||
			((radio_stream_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_INTERRUPT && (radio_stream_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_BULK) ||
			((radio_status_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_INTERRUPT && (radio_status_ep->bmAttributes & 0x03) != LIBUSB_TRANSFER_TYPE_BULK))
		{
			// an endpoint isn't the right type
			libusb_free_config_descriptor(config);
			free(d);
			mutex_destroy(&usb_info->mutex);
			free(usb_info);
			free(location_string);
			return ASPHODEL_INVALID_DESCRIPTOR;
		}
	}
	else
	{
		usb_info->remote_same_interface = 0; // not applicable
	}

	ret = usb_create_shared_device(usbdev, &usb_info->shared_device, interface_info, interface_count);
	if (ret != 0)
	{
		libusb_free_config_descriptor(config);
		free(d);
		mutex_destroy(&usb_info->mutex);
		free(usb_info);
		free(location_string);
		return ret;
	}

	*device = d;

	return 0;
}

static int is_usb_asphodel_device(libusb_device *device)
{
	struct libusb_device_descriptor desc;
	int ret = libusb_get_device_descriptor(device, &desc);
	if (ret != 0)
	{
		// error; skip over this device
		return 0;
	}

	if (desc.idVendor == USB_ASPHODEL_VID)
	{
		// has the right VID: look more closely
		if (desc.bDeviceClass == ASPHODEL_USB_CLASS && desc.bDeviceSubClass == ASPHODEL_USB_SUBCLASS)
		{
			// has the Asphodel class & subclass. bDeviceProtocol is not checked here.
			return 1;
		}
	}

	return 0;
}

// This function will try to find another AsphodelDevice_t that has the same location string as the current device.
// This can be used after a device is reset or disconnected.
static int usb_reconnect_device(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device)
{
	libusb_device **list;
	ssize_t cnt;
	ssize_t i;

	cnt = libusb_get_device_list(ctx, &list);

	if (cnt < 0)
	{
		// error
		return usb_libusb_error_to_asphodel((int)cnt);
	}

	for (i = 0; i < cnt; i++)
	{
		libusb_device *usbdev = list[i];

		if (is_usb_asphodel_device(usbdev))
		{
			uint8_t bus_number;
			uint8_t port_numbers[7]; // maximum depth for USB 3.0 and below is 7
			int	port_numbers_len;
			char location_string[MAX_LOCATION_STRING_LENGTH];

			// create a location string
			bus_number = libusb_get_bus_number(usbdev);
			port_numbers_len = libusb_get_port_numbers(usbdev, port_numbers, sizeof(port_numbers));
			if (port_numbers_len > 0)
			{
				// success
				int i;
				// format is USB:bus_number:portnum.portnum.portnum
				snprintf(location_string, MAX_LOCATION_STRING_LENGTH, "USB:%d:", bus_number);
				for (i = 0; i < port_numbers_len; i++)
				{
					size_t len = strlen(location_string);
					if (len + 1 >= MAX_LOCATION_STRING_LENGTH)
					{
						// already filled
						break;
					}

					if (i == 0)
					{
						snprintf(location_string + len, MAX_LOCATION_STRING_LENGTH - len, "%d", port_numbers[i]);
					}
					else
					{
						snprintf(location_string + len, MAX_LOCATION_STRING_LENGTH - len, ".%d", port_numbers[i]);
					}
				}
			}
			else
			{
				// error
				continue;
			}

			// see if the string is the same as the existing device
			if (strcmp(location_string, device->location_string) == 0)
			{
				int ret = create_usb_asphodel_device(usbdev, reconnected_device);
				libusb_free_device_list(list, 1);
				return ret;
			}
		}
	}

	libusb_free_device_list(list, 1);

	return ASPHODEL_NOT_FOUND;
}

static int usb_reconnect_remote(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->opened)
	{
		WaitForFinishClosure_t closure = { 0, 0 };

		// need to use the non-blocking version because of locking around device->poll
		int ret = asphodel_restart_remote(device, wait_for_finish_cb, &closure);
		if (ret == 0)
		{
			ret = wait_for_finish(&closure);
		}

		*reconnected_device = device;

		// mark as disconnected
		if (usb_info->connected)
		{
			usb_handle_remote_connect(device, 0, 0, 0);
		}

		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);

		return ret;
	}
	else
	{
		// device isn't open; and we can't reconnect a remote the same way we could a normal USB device
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_DEVICE_CLOSED;
	}
}

static int usb_reconnect_remote_boot(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->opened)
	{
		WaitForFinishClosure_t closure = { 0, 0 };

		// need to use the non-blocking version because of locking around device->poll
		int ret = asphodel_restart_remote_boot(device, wait_for_finish_cb, &closure);
		if (ret == 0)
		{
			ret = wait_for_finish(&closure);
		}

		*reconnected_device = device;

		// mark as disconnected
		if (usb_info->connected)
		{
			usb_handle_remote_connect(device, 0, 0, 0);
		}

		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);

		return ret;
	}
	else
	{
		// device isn't open; and we can't reconnect a remote the same way we could a normal USB device
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_DEVICE_CLOSED;
	}
}

static int usb_reconnect_remote_app(struct AsphodelDevice_t * device, struct AsphodelDevice_t **reconnected_device)
{
	USBDeviceInfo_t *usb_info = (USBDeviceInfo_t*)device->implementation_info;

	libusb_lock_events(ctx);
	mutex_lock(usb_info->mutex);

	if (usb_info->opened)
	{
		WaitForFinishClosure_t closure = { 0, 0 };

		// need to use the non-blocking version because of locking around device->poll
		int ret = asphodel_restart_remote_app(device, wait_for_finish_cb, &closure);
		if (ret == 0)
		{
			ret = wait_for_finish(&closure);
		}

		*reconnected_device = device;

		// mark as disconnected
		if (usb_info->connected)
		{
			usb_handle_remote_connect(device, 0, 0, 0);
		}

		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);

		return ret;
	}
	else
	{
		// device isn't open; and we can't reconnect a remote the same way we could a normal USB device
		mutex_unlock(usb_info->mutex);
		libusb_unlock_events(ctx);
		return ASPHODEL_DEVICE_CLOSED;
	}
}

ASPHODEL_API int asphodel_usb_find_devices(AsphodelDevice_t **device_list, size_t *list_size)
{
	libusb_device **list;

	ssize_t cnt = libusb_get_device_list(ctx, &list);
	ssize_t i;

	size_t output_index = 0;
	size_t output_count = 0;

	if (cnt < 0)
	{
		// error
		return usb_libusb_error_to_asphodel((int)cnt);
	}

	for (i = 0; i < cnt; i++)
	{
		libusb_device *device = list[i];

		if (is_usb_asphodel_device(device))
		{
			if (output_index < *list_size)
			{
				// there's still room in device_list
				AsphodelDevice_t *d;
				int ret = create_usb_asphodel_device(device, &d);

				if (ret != 0)
				{
					// couldn't create the device for some reason

					if (ret == ASPHODEL_ACCESS_ERROR || ret == ASPHODEL_NOT_FOUND)
					{
						// it's probably being used by another program; skip it
						continue;
					}
					else
					{
						// error, abort
						size_t j;
						for (j = 0; j < output_index; j++)
						{
							device_list[j]->free_device(device_list[j]);
						}

						*list_size = 0;
						libusb_free_device_list(list, 1);
						return ret;
					}
				}

				device_list[output_index] = d;
				output_index += 1;
			}

			output_count += 1;
		}
	}

	*list_size = output_count;

	libusb_free_device_list(list, 1);

	return 0;
}

ASPHODEL_API const char * asphodel_usb_get_backend_version(void)
{
	if (backend_version_string == NULL)
	{
		const struct libusb_version * version_info;

		version_info = libusb_get_version();
		if (version_info == NULL)
		{
			return "unknown";
		}

		backend_version_string = (char*)malloc(MAX_LIBUSB_VERSION_STRING_LENGTH);
		if (backend_version_string == NULL)
		{
			return "out of memory";
		}

		snprintf(backend_version_string, MAX_LIBUSB_VERSION_STRING_LENGTH, "libusb-%d.%d.%d%s (nano: %d)",
			version_info->major, version_info->minor, version_info->micro, version_info->rc, version_info->nano);
	}

	return backend_version_string;
}

ASPHODEL_API int asphodel_usb_devices_supported(void)
{
	return 1;
}

#else // ASPHODEL_USB_DEVICE

#include "asphodel.h"

ASPHODEL_API int asphodel_usb_init(void)
{
	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API void asphodel_usb_deinit(void)
{
	return;
}

ASPHODEL_API int asphodel_usb_find_devices(AsphodelDevice_t **device_list, size_t *list_size)
{
	(void)device_list;
	(void)list_size;

	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API int asphodel_usb_poll_devices(int milliseconds)
{
	(void)milliseconds;

	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API const char * asphodel_usb_get_backend_version(void)
{
	return "none";
}

ASPHODEL_API int asphodel_usb_devices_supported(void)
{
	return 0;
}

#endif // ASPHODEL_USB_DEVICE
