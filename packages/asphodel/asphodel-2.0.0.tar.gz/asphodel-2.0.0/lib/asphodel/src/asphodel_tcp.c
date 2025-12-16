/*
 * Copyright (c) 2019, Suprock Technologies
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

#ifdef ASPHODEL_TCP_DEVICE

#ifdef _WIN32
	// must be defined before including any headers
	#ifndef WINVER
		#define WINVER _WIN32_WINNT_VISTA
	#endif // WINVER
	#ifndef _WIN32_WINNT
		#define _WIN32_WINNT _WIN32_WINNT_VISTA
	#endif // _WIN32_WINNT
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <WinSock2.h>
#include <Ws2ipdef.h>
#include <Ws2tcpip.h>
#include <iphlpapi.h>
typedef SOCKET TCP_SOCKET_TYPE;
#define TCP_CLOSE_FUNC closesocket
#define TCP_POLL_FUNC WSAPoll
typedef ULONG nfds_t;
#else
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <ifaddrs.h>
#include <netinet/tcp.h>
#include <unistd.h>
#include <poll.h>
#include <fcntl.h>
#include <netdb.h>
typedef int TCP_SOCKET_TYPE;
#define INVALID_SOCKET -1
#define TCP_CLOSE_FUNC close
#define TCP_POLL_FUNC poll
#endif

#include "asphodel.h"
#include "clock.h"
#include "mutex.h"
#include "serialize.h"
#include "snprintf.h" // for msvc++ compatibility


#define ASPHODEL_MULTICAST_ADDRESS_IPV4 "224.0.6.150"
#define ASPHODEL_MULTICAST_ADDRESS_IPV6 "ff02::6:96"
#define ASPHODEL_MULTICAST_PORT 5760
#define INQUIRY_TIMEOUT_MS 10
#define MAX_ADVERT_PACKET_SIZE 512

#define MAX_LOCATION_STRING_LENGTH 128
#define MAX_REMOTE_SERIAL_NUMBER_LENGTH 16

#define MIN_SUPPORTED_PARAM_LEN 24

#define DEVICE_CONNECT_TIMEOUT_MS 1000
#define DEVICE_CMD_TIMEOUT_MS 1000
#define REMOTE_CMD_TIMEOUT_MS (DEVICE_CMD_TIMEOUT_MS + 100)
#define NO_OP_INTERVAL_MS 20

#define ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD    0x00
#define ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM 0x01
#define ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD    0x02
#define ASPHODEL_TCP_MSG_TYPE_REMOTE_STREAM 0x03
#define ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY 0x06

#define RX_BUFFER_SIZE 65537 // 2 byte length + 65535 byte data
#ifdef __APPLE__
	#define RCVBUF_SIZE 131072
#else
	#define RCVBUF_SIZE 8388608
#endif

typedef struct TCPCommandClosure_t {
	struct TCPCommandClosure_t* next;

	AsphodelTransferCallback_t callback;
	void* closure;
	uint8_t cmd;
	uint8_t seq;
	clock_time_t timeout;
} TCPCommandClosure_t;

typedef struct {
	AsphodelStreamingCallback_t callback; // NULL means not streaming
	void* closure;

	size_t packet_length; // set when the device is allocated

	uint8_t* buffer;
	size_t buffer_size;
	size_t buffer_index;

	int timeout_ms;
	clock_time_t next_timeout;
} TCPStreamingInfo_t;

typedef struct {
	Mutex_t mutex;

	int opened;
	int remote_opened;
	int refcount; // how many devices refer to this info instance

	struct sockaddr_storage udpaddr;
	socklen_t udpaddr_len;
	struct sockaddr_storage tcpaddr;
	socklen_t tcpaddr_len;

	TCP_SOCKET_TYPE fd;
	uint8_t* recv_buffer;
	size_t recv_index;

	uint8_t* raw_advert; // pointers in advert point into here
	Asphodel_TCPAdvInfo_t advert;

	uint8_t cmd_seq;
	TCPCommandClosure_t* cmd_head;
	TCPCommandClosure_t* remote_cmd_head;
	clock_time_t next_no_op;

	TCPStreamingInfo_t streaming_info;
	TCPStreamingInfo_t remote_streaming_info;

	char remote_serial_number[MAX_REMOTE_SERIAL_NUMBER_LENGTH];
	int remote_connected;
	AsphodelConnectCallback_t remote_connect_callback;
	void* remote_connect_closure;
	AsphodelDevice_t* remote_device; // needed to set protocol_type on remote connect

	int reconnect_timeout;
} TCPDeviceInfo_t;

typedef struct {
	// NOTE: same as BlockingClosure_t in asphodel_device.c
	int completed;
	int status;
} WaitForFinishClosure_t;


static int tcp_create_device(struct sockaddr* udpaddr, socklen_t udpaddr_len, struct sockaddr* tcpaddr, socklen_t tcpaddr_len,
		const uint8_t* advert, size_t advert_len, int reconnect_timeout, AsphodelDevice_t** device);
static int tcp_connect_device(struct sockaddr* udpaddr, socklen_t udpaddr_len, int timeout, const char* serial, AsphodelDevice_t **device);

// mutex ordering: always poll_list_mutex then device mutex
static Mutex_t poll_list_mutex;
static nfds_t poll_list_size;
static struct pollfd* poll_fds;
static TCPDeviceInfo_t** poll_infos;


static int tcp_last_error(void)
{
#ifdef _WIN32
	int error = WSAGetLastError();
	switch (error)
	{
	case WSANOTINITIALISED:
		return ASPHODEL_UNINITIALIZED;
	case WSAENETDOWN:
	case WSAENETUNREACH:
	case WSAEHOSTUNREACH:
		return ASPHODEL_UNREACHABLE;
	case WSAEACCES:
	case WSAECONNREFUSED:
		return ASPHODEL_ACCESS_ERROR;
	case WSAEINTR:
		return ASPHODEL_CANCELLED;
	case WSAEINVAL:
	case WSAEFAULT:
	case WSAENOTCONN:
	case WSAEADDRNOTAVAIL:
	case WSAEAFNOSUPPORT:
	case WSAEDESTADDRREQ:
	case WSAEISCONN:
	case WSAEINVALIDPROVIDER:
	case WSAEINVALIDPROCTABLE:
	case WSAEPROTONOSUPPORT:
	case WSAEPROTOTYPE:
	case WSAEPROVIDERFAILEDINIT:
	case WSAESOCKTNOSUPPORT:
	case WSAENOTSOCK:
	case WSAEOPNOTSUPP:
	case WSAESHUTDOWN:
	case WSAEADDRINUSE:
		return ASPHODEL_BAD_PARAMETER;
	case WSAENOBUFS:
	case WSAEMFILE:
		return ASPHODEL_NO_RESOURCES;
	case WSAEINPROGRESS:
	case WSAEWOULDBLOCK:
	case WSAEALREADY:
		return ASPHODEL_BUSY;
	case WSAEMSGSIZE:
		return ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	case WSAECONNABORTED:
	case WSAECONNRESET:
	case WSAENETRESET:
		return ASPHODEL_ERROR_IO;
	case WSAETIMEDOUT:
		return ASPHODEL_TIMEOUT;
	default:
		return ASPHODEL_TRANSPORT_ERROR;
	}
#else
	int error = errno;
	switch (error)
	{
	case EACCES:
	case EPERM:
		return ASPHODEL_ACCESS_ERROR;
	case EFAULT:
	case EBADF:
	case EINVAL:
	case EISCONN:
	case ENOTCONN:
	case ENOTSOCK:
	case EOPNOTSUPP:
	case EDESTADDRREQ:
	case EALREADY:
	case EPROTOTYPE:
	case ENOENT:
	case ENOTDIR:
		return ASPHODEL_BAD_PARAMETER;
	case EINTR:
		return ASPHODEL_CANCELLED;
	case EMFILE:
	case ENFILE:
	case ENOBUFS:
	case ENOMEM:
	case EADDRNOTAVAIL:
	case EADDRINUSE:
		return ASPHODEL_NO_RESOURCES;
	case EAGAIN:
#if EAGAIN != EWOULDBLOCK
	case EWOULDBLOCK:
#endif
	case EINPROGRESS:
		return ASPHODEL_BUSY;
	case ECONNRESET:
	case ECONNREFUSED:
		return ASPHODEL_ERROR_IO;
	case EMSGSIZE:
		return ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	case EPIPE:
		return ASPHODEL_PIPE_ERROR;
	case EAFNOSUPPORT:
	case EPROTONOSUPPORT:
		return ASPHODEL_NOT_SUPPORTED;
	case ETIMEDOUT:
		return ASPHODEL_TIMEOUT;
	case ENETUNREACH:
	case EHOSTUNREACH:
	case ENETDOWN:
		return ASPHODEL_UNREACHABLE;
	default:
		return ASPHODEL_TRANSPORT_ERROR;
	}
#endif
}

static int tcp_poll_list_add(TCPDeviceInfo_t* tcp_info) // call with both poll_list_mutex and device lock
{
	nfds_t new_poll_list_size = poll_list_size + 1;
	struct pollfd* new_poll_fds;
	TCPDeviceInfo_t** new_poll_infos;

	new_poll_fds = (struct pollfd*)malloc(sizeof(struct pollfd) * new_poll_list_size);
	if (new_poll_fds == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	new_poll_infos = (TCPDeviceInfo_t**)malloc(sizeof(TCPDeviceInfo_t*) * new_poll_list_size);
	if (new_poll_infos == NULL)
	{
		free(new_poll_fds);
		return ASPHODEL_NO_MEM;
	}

	// copy old list into new
	memcpy(new_poll_fds, poll_fds, poll_list_size * sizeof(struct pollfd));
	memcpy(new_poll_infos, poll_infos, poll_list_size * sizeof(TCPDeviceInfo_t*));

	// add to the end
	new_poll_infos[poll_list_size] = tcp_info;
	new_poll_fds[poll_list_size].fd = tcp_info->fd;
	new_poll_fds[poll_list_size].events = POLLIN;

	// free the old list and move the new one in
	free(poll_fds);
	free(poll_infos);
	poll_list_size = new_poll_list_size;
	poll_fds = new_poll_fds;
	poll_infos = new_poll_infos;

	return ASPHODEL_SUCCESS;
}

static void tcp_poll_list_remove(TCPDeviceInfo_t* tcp_info) // call with both poll_list_mutex and device lock
{
	nfds_t new_poll_list_size = poll_list_size - 1;
	nfds_t i;

	// find the tcp_info and move everything down
	for (i = 0; i < poll_list_size; i++)
	{
		if (poll_infos[i] == tcp_info)
		{
			break;
		}
	}

	// didn't find it, bail out
	if (i == poll_list_size)
	{
		return;
	}

	if (i < poll_list_size)
	{
		// not the last entry, so we have to do actual work
		size_t entries_to_move = new_poll_list_size - i;
		memmove(&poll_fds[i], &poll_fds[i + 1], entries_to_move * sizeof(struct pollfd));
		memmove(&poll_infos[i], &poll_infos[i + 1], entries_to_move * sizeof(TCPDeviceInfo_t*));
	}

	poll_list_size = new_poll_list_size;
}

static int tcp_open_socket(TCPDeviceInfo_t* tcp_info) // call with both poll_list_mutex and device lock
{
	struct pollfd fds;
	int value;
	int ret;

	// allocate the receive buffer
	tcp_info->recv_buffer = (uint8_t*)malloc(RX_BUFFER_SIZE);
	if (tcp_info->recv_buffer == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	// open the socket
	tcp_info->fd = socket(tcp_info->tcpaddr.ss_family, SOCK_STREAM, IPPROTO_TCP);
	if (tcp_info->fd == INVALID_SOCKET)
	{
		ret = tcp_last_error();
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}

	// set the socket to non-blocking
#ifdef _WIN32
	u_long mode = 1;
	ret = ioctlsocket(tcp_info->fd, FIONBIO, &mode);
#else
	int flags = fcntl(tcp_info->fd, F_GETFL, 0);
	ret = fcntl(tcp_info->fd, F_SETFL, flags | O_NONBLOCK);
#endif
	if (ret != 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}

	ret = connect(tcp_info->fd, (struct sockaddr*)&tcp_info->tcpaddr, tcp_info->tcpaddr_len);
	if (ret != 0)
	{
#ifdef _WIN32
		int error = WSAGetLastError();
		if (error != WSAEWOULDBLOCK)
#else
		int error = errno;
		if (error != EINPROGRESS)
#endif
		{
			ret = tcp_last_error();
			TCP_CLOSE_FUNC(tcp_info->fd);
			tcp_info->fd = INVALID_SOCKET;
			free(tcp_info->recv_buffer);
			tcp_info->recv_buffer = NULL;
			return ret;
		}
	}

	// wait for connect
	fds.fd = tcp_info->fd;
	fds.events = POLLOUT;
	ret = TCP_POLL_FUNC(&fds, 1, DEVICE_CONNECT_TIMEOUT_MS);
	if (ret < 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}
	else if (ret == 0)
	{
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ASPHODEL_TIMEOUT;
	}

	// disable Nagle algorithm
	value = 1;
	ret = setsockopt(tcp_info->fd, IPPROTO_TCP, TCP_NODELAY, (void*)&value, sizeof(int));
	if (ret != 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}

	// increase OS's buffer size
	value = RCVBUF_SIZE;
	ret = setsockopt(tcp_info->fd, SOL_SOCKET, SO_RCVBUF, (void*)&value, sizeof(int));
	if (ret != 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}

	// add to poll list
	ret = tcp_poll_list_add(tcp_info);
	if (ret != 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(tcp_info->fd);
		tcp_info->fd = INVALID_SOCKET;
		free(tcp_info->recv_buffer);
		tcp_info->recv_buffer = NULL;
		return ret;
	}

	return ASPHODEL_SUCCESS;
}

static void tcp_close_socket(TCPDeviceInfo_t* tcp_info) // call with both poll_list_mutex and device lock
{
	// remove from list
	tcp_poll_list_remove(tcp_info);

	TCP_CLOSE_FUNC(tcp_info->fd);
	tcp_info->fd = INVALID_SOCKET;

	free(tcp_info->recv_buffer);
	tcp_info->recv_buffer = NULL;
}

static int tcp_socket_send(TCPDeviceInfo_t* tcp_info, const uint8_t* header, size_t header_length, const uint8_t* extra, size_t extra_length) // call with device lock
{
#ifdef _WIN32
	int ret;

	DWORD bytes_sent;
	WSABUF data[2] = {
		{
			.buf = (void*)header,
			.len = (ULONG)header_length,
		},
		{
			.buf = (void*)extra,
			.len = (ULONG)extra_length,
		},
	};

	if (extra_length == 0)
	{
		ret = WSASend(tcp_info->fd, data, 1, &bytes_sent, 0, NULL, NULL);
	}
	else
	{
		ret = WSASend(tcp_info->fd, data, 2, &bytes_sent, 0, NULL, NULL);
	}

	if (ret != 0)
	{
		// error
		return tcp_last_error();
	}

	return ASPHODEL_SUCCESS;
#else
	int ret;

	struct iovec data[2] = {
		{
			.iov_base = (void*)header,
			.iov_len = header_length,
		},
		{
			.iov_base = (void*)extra,
			.iov_len = extra_length,
		},
	};

	struct msghdr msg = {
		.msg_name = NULL,
		.msg_namelen = 0,
		.msg_iov = &data[0],
		.msg_iovlen = 2, // will be shortened if extra_length is 0
		.msg_control = 0,
		.msg_controllen = 0,
		.msg_flags = 0,
	};

	if (extra_length == 0)
	{
		msg.msg_iovlen = 1;
	}

	ret = sendmsg(tcp_info->fd, &msg , 0);

	if (ret < 0)
	{
		// error
		return tcp_last_error();
	}

	return ASPHODEL_SUCCESS;
#endif
}

static void tcp_handle_remote_connect(TCPDeviceInfo_t* tcp_info, uint32_t serial_number, uint8_t protocol_type) // call with device lock
{
	tcp_info->remote_connected = 1;

	if (tcp_info->remote_device)
	{
		// add ASPHODEL_PROTOCOL_TYPE_REMOTE just in case (shouldn't be necessary)
		tcp_info->remote_device->protocol_type = protocol_type | ASPHODEL_PROTOCOL_TYPE_REMOTE;
	}

	// write into new serial number
	snprintf(tcp_info->remote_serial_number, MAX_REMOTE_SERIAL_NUMBER_LENGTH, "WM%u", serial_number);

	// call callback
	if (tcp_info->remote_connect_callback != NULL)
	{
		tcp_info->remote_connect_callback(ASPHODEL_SUCCESS, 1, tcp_info->remote_connect_closure);
	}
}

static void tcp_handle_remote_disconnect(TCPDeviceInfo_t* tcp_info) // call with device lock
{
	if (tcp_info->remote_connected == 0)
	{
		// already disconnected
		return;
	}

	tcp_info->remote_connected = 0;

	// remove any old protocol types assoicated with the device
	if (tcp_info->remote_device)
	{
		// add ASPHODEL_PROTOCOL_TYPE_REMOTE just in case (shouldn't be necessary)
		tcp_info->remote_device->protocol_type = ASPHODEL_PROTOCOL_TYPE_REMOTE;
	}

	// remove serial number
	tcp_info->remote_serial_number[0] = '\0';

	// call callback
	if (tcp_info->remote_connect_callback != NULL)
	{
		tcp_info->remote_connect_callback(ASPHODEL_SUCCESS, 0, tcp_info->remote_connect_closure);
	}
}

static void tcp_handle_command(TCPCommandClosure_t** head, const uint8_t* buffer, size_t buffer_length, size_t maximum_param_length) // call with device lock
{
	TCPCommandClosure_t* cmd = *head;
	const uint8_t* params = &buffer[2];
	size_t param_length = buffer_length - 2;
	int status;

	if (cmd == NULL)
	{
		// this is an error condition, but there's really no one that can be told about it
		return;
	}

	if (buffer_length < 2)
	{
		// too short
		status = ASPHODEL_MALFORMED_REPLY;
		param_length = 0;
	}
	else if (buffer[0] != cmd->seq)
	{
		// wrong sequence number; look through the list to find a matching command

		int found = 0;
		TCPCommandClosure_t* first = cmd;
		cmd = cmd->next; // we've already checked cmd, so start on next

		while (cmd != NULL)
		{
			if (cmd->seq == buffer[0])
			{
				// found it
				found = 1;
				break;
			}
			else
			{
				cmd = cmd->next;
			}
		}

		if (found)
		{
			// pop all the earlier entries off the list
			while (first != cmd)
			{
				TCPCommandClosure_t* next = first->next;

				if (first->callback)
				{
					first->callback(ASPHODEL_MISMATCHED_TRANSACTION, NULL, 0, first->closure);
				}

				free(first);

				first = next;
			}

			*head = cmd;

			// handle the cmd normally
			tcp_handle_command(head, buffer, buffer_length, maximum_param_length);

			// we've already handled everything
			return;
		}
		else
		{
			cmd = first;

			// do the usual error handling
			status = ASPHODEL_MISMATCHED_TRANSACTION;
			param_length = 0;
		}
	}
	else if (buffer[1] == cmd->cmd)
	{
		// everything is ok
		status = ASPHODEL_SUCCESS;
	}
	else if (buffer[1] == CMD_REPLY_ERROR)
	{
		if (buffer_length < 3)
		{
			// error response is too short
			status = ASPHODEL_MALFORMED_ERROR;
			param_length = 0;
		}
		else
		{
			status = buffer[2];
			if (status == 0x00)
			{
				status = ERROR_CODE_UNSPECIFIED;
			}

			params = &buffer[3];
			param_length = buffer_length - 3;
		}
	}
	else
	{
		// wrong cmd
		status = ASPHODEL_MISMATCHED_COMMAND;
		param_length = 0;
	}

	if (param_length > maximum_param_length)
	{
		// too long
		status = ASPHODEL_BAD_REPLY_LENGTH;
		param_length = 0;
	}

	// remove the cmd from the list
	*head = cmd->next;

	// do callback last, as it may do things with the device (e.g. stop streaming or send new commands)
	if (cmd->callback)
	{
		cmd->callback(status, params, param_length, cmd->closure);
	}

	free(cmd);
}

static void tcp_handle_stream(TCPStreamingInfo_t* streaming_info, const uint8_t* buffer, size_t buffer_length) // call with device lock
{
	if (streaming_info->callback == NULL || buffer_length == 0)
	{
		return;
	}

	while (buffer_length > 0)
	{
		size_t remaining_space = streaming_info->buffer_size - streaming_info->buffer_index;

		if (buffer_length < remaining_space)
		{
			// won't fill the buffer
			memcpy(&streaming_info->buffer[streaming_info->buffer_index], buffer, buffer_length);
			streaming_info->buffer_index += buffer_length;
			break;
		}
		else
		{
			// will fill the rest of the buffer
			memcpy(&streaming_info->buffer[streaming_info->buffer_index], buffer, remaining_space);

			// do the callback
			streaming_info->callback(ASPHODEL_SUCCESS, streaming_info->buffer, streaming_info->packet_length, streaming_info->buffer_size / streaming_info->packet_length, streaming_info->closure);

			if (streaming_info->callback == NULL)
			{
				// stopped streaming in the callback
				return;
			}

			streaming_info->buffer_index = 0;
			buffer += remaining_space;
			buffer_length -= remaining_space;
		}
	}

	// update timeout
	clock_get_end_time(&streaming_info->next_timeout, streaming_info->timeout_ms);
}

static int tcp_check_command_timeouts(TCPCommandClosure_t** head, clock_time_t* now) // call with device lock, returns ms to next timeout (0 means no next timeout)
{
	TCPCommandClosure_t* first = *head;
	TCPCommandClosure_t* cmd = first;
	int timeout = 0;

	while (cmd != NULL)
	{
		timeout = clock_milliseconds_remaining_now(&cmd->timeout, now);

		if (timeout == 0)
		{
			// timed out, make the list start after this node and keep checking
			TCPCommandClosure_t* next = cmd->next;
			cmd = next;
			*head = next;
		}
		else
		{
			// found one not timed out, stop iteration
			break;
		}
	}

	// now that we're done iterating the list, we can call the callbacks (in case they want to modify the list)
	while (first != cmd)
	{
		TCPCommandClosure_t* next = first->next;

		if (first->callback)
		{
			first->callback(ASPHODEL_TIMEOUT, NULL, 0, first->closure);
		}

		free(first);

		first = next;
	}

	return timeout;
}

static int tcp_check_no_op_timeouts(TCPDeviceInfo_t* tcp_info, clock_time_t* now)
{
	int timeout;

	if (tcp_info->cmd_head == NULL && tcp_info->remote_cmd_head == NULL)
	{
		return 0; // no need for no ops
	}

	if (tcp_info->advert.tcp_version <= 1)
	{
		// doesn't support no ops
		return 0;
	}

	timeout = clock_milliseconds_remaining_now(&tcp_info->next_no_op, now);

	if (timeout == 0)
	{
		uint8_t header[2] = { 0, 0 }; // no op

		// set the next no op time
		clock_get_end_time_from_now(&tcp_info->next_no_op, now, NO_OP_INTERVAL_MS);

		// can't do anything with the return value
		(void)tcp_socket_send(tcp_info, header, sizeof(header), NULL, 0);

		return NO_OP_INTERVAL_MS;
	}
	else
	{
		return timeout;
	}
}

static int tcp_check_stream_timeouts(TCPStreamingInfo_t* streaming_info, clock_time_t* now) // call with device lock, returns ms to next timeout (0 means no next timeout)
{
	int timeout;

	if (streaming_info->callback == NULL)
	{
		return 0; // not streaming
	}

	timeout = clock_milliseconds_remaining_now(&streaming_info->next_timeout, now);

	if (timeout == 0)
	{
		// timed out

		if (streaming_info->buffer_index != 0)
		{
			// got some data; handle that first
			streaming_info->callback(ASPHODEL_SUCCESS, streaming_info->buffer, streaming_info->packet_length, streaming_info->buffer_index / streaming_info->packet_length, streaming_info->closure);
			streaming_info->buffer_index = 0;
		}

		streaming_info->callback(ASPHODEL_TIMEOUT, NULL, 0, 0, streaming_info->closure);

		if (streaming_info->callback == NULL)
		{
			// stopped streaming in the callback
			return 0;
		}
		else
		{
			clock_get_end_time_from_now(&streaming_info->next_timeout, now, streaming_info->timeout_ms);
			return streaming_info->timeout_ms;
		}
	}
	else
	{
		return timeout;
	}
}

static void tcp_cancel_commands(TCPCommandClosure_t** head, int status) // call with device lock
{
	TCPCommandClosure_t* node = *head;
	while (node != NULL)
	{
		TCPCommandClosure_t* next = node->next;

		// call the callback (NOTE: the device is closed, so callbacks can't modify the list while we're interating)
		if (node->callback)
		{
			node->callback(status, NULL, 0, node->closure);
		}

		// free the node
		free(node);

		// iterate to the next in the list
		node = next;
	}

	// mark the list as empty
	*head = NULL;
}

static void tcp_stop_streaming(TCPStreamingInfo_t* streaming_info, int status) // call with device lock
{
	if (streaming_info->buffer)
	{
		if (streaming_info->callback != NULL)
		{
			if (streaming_info->buffer_index != 0)
			{
				// process any left over data
				streaming_info->callback(ASPHODEL_SUCCESS, streaming_info->buffer, streaming_info->packet_length,
					streaming_info->buffer_index / streaming_info->packet_length, streaming_info->closure);
			}

			if (status != ASPHODEL_SUCCESS)
			{
				// do the error callback
				streaming_info->callback(status, NULL, 0, 0, streaming_info->closure);
			}
		}

		streaming_info->callback = NULL;

		free(streaming_info->buffer);
		streaming_info->buffer = NULL;
		streaming_info->buffer_size = 0;
	}
	else
	{
		streaming_info->callback = NULL;
	}
}

static int tcp_start_streaming(TCPStreamingInfo_t* streaming_info, int packet_count,
	unsigned int timeout, AsphodelStreamingCallback_t callback, void* closure) // call with device lock
{
	size_t buffer_size;

	tcp_stop_streaming(streaming_info, ASPHODEL_SUCCESS);

	if (callback == NULL)
	{
		// nothing to do
		return ASPHODEL_SUCCESS;
	}

	if (streaming_info->packet_length == 0)
	{
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	if (packet_count <= 0 || packet_count > 32768)
	{
		// NOTE: packet_count > 32768 can cause overflows
		return ASPHODEL_BAD_PARAMETER;
	}

	buffer_size = (size_t)packet_count * streaming_info->packet_length;

	streaming_info->buffer = (uint8_t*)malloc(buffer_size);
	if (streaming_info->buffer == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	streaming_info->callback = callback;
	streaming_info->closure = closure;
	streaming_info->buffer_size = buffer_size;
	streaming_info->buffer_index = 0;
	streaming_info->timeout_ms = timeout;
	clock_get_end_time(&streaming_info->next_timeout, timeout);

	return ASPHODEL_SUCCESS;
}

static int tcp_check_timeouts(TCPDeviceInfo_t* tcp_info, clock_time_t* now) // call with device lock, returns ms to next timeout (0 means no next timeout)
{
	int timeout = 0;
	int ret;

	ret = tcp_check_command_timeouts(&tcp_info->cmd_head, now);
	if (ret != 0 && (timeout == 0 || ret < timeout))
	{
		timeout = ret;
	}

	ret = tcp_check_command_timeouts(&tcp_info->remote_cmd_head, now);
	if (ret != 0 && (timeout == 0 || ret < timeout))
	{
		timeout = ret;
	}

	ret = tcp_check_no_op_timeouts(tcp_info, now);
	if (ret != 0 && (timeout == 0 || ret < timeout))
	{
		timeout = ret;
	}

	ret = tcp_check_stream_timeouts(&tcp_info->streaming_info, now);
	if (ret != 0 && (timeout == 0 || ret < timeout))
	{
		timeout = ret;
	}

	ret = tcp_check_stream_timeouts(&tcp_info->remote_streaming_info, now);
	if (ret != 0 && (timeout == 0 || ret < timeout))
	{
		timeout = ret;
	}

	return timeout;
}

static int tcp_get_socket_data(TCPDeviceInfo_t* tcp_info, size_t max_read) // call with device lock, with device and/or remote open
{
	int ret;

	if (max_read == 0)
	{
		return 1; // read "enough"
	}

	ret = (int)recv(tcp_info->fd, (char*)&tcp_info->recv_buffer[tcp_info->recv_index], (int)max_read, 0);
	if (ret < 0)
	{
		// got an error
#ifdef _WIN32
		int error = WSAGetLastError();
		if (error == WSAEWOULDBLOCK)
		{
			// non blocking socket didn't collect enough data, not a real error
			return 0; // not enough data
		}
#else
		int error = errno;
		if (error == EAGAIN || error == EWOULDBLOCK)
		{
			// non blocking socket didn't collect enough data, not a real error
			return 0; // not enough data
		}
#endif

		// if we got to this point then it must be a serious error, and it needs to be reported
		error = tcp_last_error();
		tcp_cancel_commands(&tcp_info->cmd_head, error);
		tcp_stop_streaming(&tcp_info->streaming_info, error);
		return 0; // not enough data
	}
	else if (ret == 0)
	{
		// socket is closed (gracefully)
		tcp_cancel_commands(&tcp_info->cmd_head, ASPHODEL_ERROR_IO);
		tcp_stop_streaming(&tcp_info->streaming_info, ASPHODEL_ERROR_IO);
		return 0; // not enough data
	}
	else
	{
		// got some data
		tcp_info->recv_index += ret;
		if (max_read == (size_t)ret)
		{
			return 1; // read enough
		}
		else
		{
			return 0; // not enough data
		}
	}
}

static void tcp_poll_device_single_pass(TCPDeviceInfo_t* tcp_info) // call with device lock, with device and/or remote open
{
	while (1)
	{
		if (tcp_info->recv_index < 2)
		{
			// need to read the length
			size_t length_bytes_remaining = 2 - tcp_info->recv_index;
			if (!tcp_get_socket_data(tcp_info, length_bytes_remaining))
			{
				// not enough data received
				return;
			}
		}
		else if (tcp_info->recv_index >= 2)
		{
			// have the length, need to collect enough data
			size_t desired_length = read_16bit_value(&tcp_info->recv_buffer[0]);
			size_t data_bytes_remaining = 2 + desired_length - tcp_info->recv_index;
			if (!tcp_get_socket_data(tcp_info, data_bytes_remaining))
			{
				// not enough data received
				return;
			}

			// process the now complete data
			if (desired_length == 0)
			{
				// no op, reset index and move on
				tcp_info->recv_index = 0;
			}
			else
			{
				switch (tcp_info->recv_buffer[2])
				{
				case ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD:
					tcp_handle_command(&tcp_info->cmd_head, &tcp_info->recv_buffer[3], desired_length - 1,
						tcp_info->advert.max_incoming_param_length);
					break;
				case ASPHODEL_TCP_MSG_TYPE_DEVICE_STREAM:
					tcp_handle_stream(&tcp_info->streaming_info, &tcp_info->recv_buffer[3], desired_length - 1);
					break;
				case ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD:
					tcp_handle_command(&tcp_info->remote_cmd_head, &tcp_info->recv_buffer[3], desired_length - 1,
						tcp_info->advert.remote_max_incoming_param_length);
					break;
				case ASPHODEL_TCP_MSG_TYPE_REMOTE_STREAM:
					tcp_handle_stream(&tcp_info->remote_streaming_info, &tcp_info->recv_buffer[3], desired_length - 1);
					break;
				case ASPHODEL_TCP_MSG_TYPE_REMOTE_NOTIFY:
					if (desired_length == 6)
					{
						// connect
						uint32_t serial_number = read_32bit_value(&tcp_info->recv_buffer[3]);
						uint8_t protocol_type = tcp_info->recv_buffer[7];
						tcp_handle_remote_connect(tcp_info, serial_number, protocol_type);
					}
					else if (desired_length == 1)
					{
						// no data means disconnect
						tcp_handle_remote_disconnect(tcp_info);
					}
					break;
				default:
					break;
				}

				tcp_info->recv_index = 0;
			}
		}
	}
}

static int tcp_poll_device(AsphodelDevice_t* device, int milliseconds, int* completed)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	clock_time_t deadline;

	if (completed != NULL && *completed)
	{
		// done early
		return ASPHODEL_SUCCESS;
	}

	clock_get_end_time(&deadline, milliseconds);

	while (1)
	{
		clock_time_t now;
		int remaining;
		int next_timeout;

		mutex_lock(tcp_info->mutex);

		if (tcp_info->opened || tcp_info->remote_opened)
		{
			clock_now(&now);
			tcp_poll_device_single_pass(tcp_info);
			next_timeout = tcp_check_timeouts(tcp_info, &now);
		}
		else
		{
			// device isn't open
			mutex_unlock(tcp_info->mutex);
			break;
		}

		if (completed != NULL && *completed)
		{
			mutex_unlock(tcp_info->mutex);
			break;
		}

		remaining = clock_milliseconds_remaining_now(&deadline, &now);
		if (remaining == 0)
		{
			// no time left
			mutex_unlock(tcp_info->mutex);
			break;
		}
		else
		{
			int ret;
			struct pollfd fds;
			int poll_time;

			if (next_timeout == 0 || remaining < next_timeout)
			{
				poll_time = remaining;
			}
			else
			{
				poll_time = next_timeout;
			}

			fds.fd = tcp_info->fd;
			fds.events = POLLIN;

			mutex_unlock(tcp_info->mutex);

			// wait for poll_time, or an event
			ret = TCP_POLL_FUNC(&fds, 1, poll_time);
			if (ret < 0)
			{
				// seems like a serious error
				return tcp_last_error();
			}
			else if (ret == 0)
			{
				// timed out
				break;
			}
			else
			{
				// loop around to process the socket data
				continue;
			}
		}
	}

	return ASPHODEL_SUCCESS;
}

static int tcp_open_device(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(poll_list_mutex);
	mutex_lock(tcp_info->mutex);

	if (tcp_info->opened == 0)
	{
		if (tcp_info->remote_opened == 0)
		{
			ret = tcp_open_socket(tcp_info);
			if (ret != ASPHODEL_SUCCESS)
			{
				mutex_unlock(tcp_info->mutex);
				mutex_unlock(poll_list_mutex);
				return ret;
			}
		}

		tcp_info->opened = 1;
	}

	mutex_unlock(tcp_info->mutex);
	mutex_unlock(poll_list_mutex);

	return ASPHODEL_SUCCESS;
}

static void tcp_close_device(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(poll_list_mutex);
	mutex_lock(tcp_info->mutex);

	if (tcp_info->opened)
	{
		tcp_info->opened = 0;

		tcp_cancel_commands(&tcp_info->cmd_head, ASPHODEL_DEVICE_CLOSED);
		tcp_stop_streaming(&tcp_info->streaming_info, ASPHODEL_DEVICE_CLOSED); // no error

		if (tcp_info->remote_opened == 0)
		{
			tcp_close_socket(tcp_info);
		}
	}

	mutex_unlock(tcp_info->mutex);
	mutex_unlock(poll_list_mutex);
}

static int tcp_open_remote(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret = ASPHODEL_SUCCESS;
	int opened_socket = 0;

	mutex_lock(poll_list_mutex);
	mutex_lock(tcp_info->mutex);

	// an open call means this is the "official" remote device
	tcp_info->remote_device = device;

	if (tcp_info->remote_opened == 0)
	{
		int remote_connected;
		uint32_t remote_serial_number;
		uint8_t remote_protocol_type;

		if (tcp_info->opened == 0)
		{
			ret = tcp_open_socket(tcp_info);
			if (ret != ASPHODEL_SUCCESS)
			{
				mutex_unlock(tcp_info->mutex);
				mutex_unlock(poll_list_mutex);
				return ret;
			}
			opened_socket = 1;
		}

		tcp_info->remote_opened = 1;

		ret = asphodel_get_remote_status_blocking(device, &remote_connected, &remote_serial_number, &remote_protocol_type);
		if (ret != ASPHODEL_SUCCESS)
		{
			tcp_info->remote_opened = 0;
			if (opened_socket)
			{
				tcp_close_socket(tcp_info);
			}
			mutex_unlock(tcp_info->mutex);
			mutex_unlock(poll_list_mutex);
			return ret;
		}

		if (remote_connected)
		{
			tcp_handle_remote_connect(tcp_info, remote_serial_number, remote_protocol_type);
		}
		else
		{
			tcp_handle_remote_disconnect(tcp_info);
		}
	}

	mutex_unlock(tcp_info->mutex);
	mutex_unlock(poll_list_mutex);

	return ret;
}

static void tcp_close_remote(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(poll_list_mutex);
	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_opened)
	{
		tcp_info->remote_opened = 0;

		tcp_handle_remote_disconnect(tcp_info);
		tcp_cancel_commands(&tcp_info->remote_cmd_head, ASPHODEL_DEVICE_CLOSED);
		tcp_stop_streaming(&tcp_info->remote_streaming_info, ASPHODEL_DEVICE_CLOSED);

		if (tcp_info->opened == 0)
		{
			tcp_close_socket(tcp_info);
		}
	}

	mutex_unlock(tcp_info->mutex);
	mutex_unlock(poll_list_mutex);
}

static void tcp_free_device(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(poll_list_mutex);
	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_device == device)
	{
		tcp_info->remote_device = NULL;
	}

	tcp_info->refcount -= 1;

	if (tcp_info->refcount == 0)
	{
		// can unlock the mutex at this point; no other references exist
		mutex_unlock(tcp_info->mutex);

		if (tcp_info->remote_opened)
		{
			tcp_close_remote(device);
		}

		if (tcp_info->opened)
		{
			tcp_close_device(device);
		}

		// free tcp_info
		mutex_destroy(&tcp_info->mutex);
		free(tcp_info->raw_advert);
		free(tcp_info);
	}
	else
	{
		mutex_unlock(tcp_info->mutex);
	}

	// free device struct
	free((void*)device->location_string);
	free(device);

	mutex_unlock(poll_list_mutex);
}

static int tcp_device_get_serial_number(AsphodelDevice_t* device, char* buffer, size_t buffer_size)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	size_t i;

	mutex_lock(tcp_info->mutex);

	for (i = 0; i < buffer_size - 1; i++)
	{
		char ch = tcp_info->advert.serial_number[i];
		buffer[i] = ch;

		if (ch == '\0')
		{
			break;
		}
	}

	// make sure the buffer is null terminated
	buffer[i] = '\0';

	mutex_unlock(tcp_info->mutex);

	return ASPHODEL_SUCCESS;
}

static int tcp_remote_get_serial_number(AsphodelDevice_t* device, char* buffer, size_t buffer_size)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	size_t i;

	mutex_lock(tcp_info->mutex);

	if (!tcp_info->remote_opened)
	{
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_DEVICE_CLOSED;
	}

	// poll the device once to see if there's any connect/disconnect pending (will set remote_serial_number)
	tcp_poll_device(device, 0, NULL);

	for (i = 0; i < buffer_size - 1; i++)
	{
		char ch = tcp_info->remote_serial_number[i];
		buffer[i] = ch;

		if (ch == '\0')
		{
			break;
		}
	}

	// make sure the buffer is null terminated
	buffer[i] = '\0';

	mutex_unlock(tcp_info->mutex);

	return ASPHODEL_SUCCESS;
}

static int tcp_do_transfer(TCPDeviceInfo_t* tcp_info, TCPCommandClosure_t** head, uint8_t control_byte, uint8_t command,
	const uint8_t* params, uint16_t param_length, AsphodelTransferCallback_t callback, void* closure, int timeout) // call with device lock
{
	clock_time_t now;
	TCPCommandClosure_t* cmd;
	uint8_t header[5];
	int ret;

	cmd = (TCPCommandClosure_t*)malloc(sizeof(TCPCommandClosure_t));
	if (cmd == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	clock_now(&now);

	// setup the structure
	cmd->next = NULL;
	cmd->callback = callback;
	cmd->closure = closure;
	cmd->cmd = command;
	cmd->seq = tcp_info->cmd_seq;
	clock_get_end_time_from_now(&cmd->timeout, &now, timeout);

	// increment sequence (a cmd_seq of 0 is reserved)
	tcp_info->cmd_seq += 1;
	if (tcp_info->cmd_seq == 0)
	{
		tcp_info->cmd_seq = 1;
	}

	// set the next noop time
	clock_get_end_time_from_now(&tcp_info->next_no_op, &now, NO_OP_INTERVAL_MS);

	// prepare the header
	write_16bit_value(&header[0], param_length + 3); // 3 bytes for control_byte, seq, command
	header[2] = control_byte;
	header[3] = cmd->seq;
	header[4] = command;

	// send header + params
	ret = tcp_socket_send(tcp_info, header, sizeof(header), params, param_length);
	if (ret != ASPHODEL_SUCCESS)
	{
		free(cmd);
		return ret;
	}

	// add cmd to the back of the list
	while (*head != NULL)
	{
		head = &(*head)->next;
	}
	*head = cmd;

	return ASPHODEL_SUCCESS;
}

static int tcp_device_do_transfer(AsphodelDevice_t* device, uint8_t command, const uint8_t* params,
	size_t param_length, AsphodelTransferCallback_t callback, void* closure)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(tcp_info->mutex);

	if (param_length > tcp_info->advert.max_outgoing_param_length || param_length > (0xFFFF - 3))
	{
		ret = ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	}
	else
	{
		if (tcp_info->opened)
		{
			ret = tcp_do_transfer(tcp_info, &tcp_info->cmd_head, ASPHODEL_TCP_MSG_TYPE_DEVICE_CMD,
				command, params, (uint16_t)param_length, callback, closure, DEVICE_CMD_TIMEOUT_MS);
		}
		else
		{
			ret = ASPHODEL_DEVICE_CLOSED;
		}
	}

	mutex_unlock(tcp_info->mutex);

	return ret;
}

static int tcp_device_do_transfer_reset(AsphodelDevice_t* device, uint8_t command, const uint8_t* params,
	size_t param_length, AsphodelTransferCallback_t callback, void* closure)
{
	int ret;

	ret = tcp_device_do_transfer(device, command, params, param_length, NULL, NULL);

	if (ret == ASPHODEL_SUCCESS && callback)
	{
		callback(ASPHODEL_SUCCESS, NULL, 0, closure);
	}

	return ret;
}

static int tcp_remote_do_transfer(AsphodelDevice_t* device, uint8_t command, const uint8_t* params,
	size_t param_length, AsphodelTransferCallback_t callback, void* closure)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(tcp_info->mutex);

	if (param_length > tcp_info->advert.remote_max_outgoing_param_length || param_length > (0xFFFF - 3))
	{
		ret = ASPHODEL_OUTGOING_PACKET_TOO_LONG;
	}
	else
	{
		if (tcp_info->remote_opened)
		{
			ret = tcp_do_transfer(tcp_info, &tcp_info->remote_cmd_head, ASPHODEL_TCP_MSG_TYPE_REMOTE_CMD,
				command, params, (uint16_t)param_length, callback, closure, REMOTE_CMD_TIMEOUT_MS);
		}
		else
		{
			ret = ASPHODEL_DEVICE_CLOSED;
		}
	}

	mutex_unlock(tcp_info->mutex);

	return ret;
}

static int tcp_remote_do_transfer_reset(AsphodelDevice_t* device, uint8_t command, const uint8_t* params,
	size_t param_length, AsphodelTransferCallback_t callback, void* closure)
{
	int ret;

	ret = tcp_remote_do_transfer(device, command, params, param_length, NULL, NULL);

	if (ret == ASPHODEL_SUCCESS && callback)
	{
		callback(ASPHODEL_SUCCESS, NULL, 0, closure);
	}

	return ret;
}

static int tcp_device_start_streaming_packets(AsphodelDevice_t* device, int packet_count, int transfer_count,
	unsigned int timeout, AsphodelStreamingCallback_t callback, void* closure)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	(void)transfer_count; // not used

	mutex_lock(tcp_info->mutex);

	if (tcp_info->opened)
	{
		ret = tcp_start_streaming(&tcp_info->streaming_info, packet_count, timeout, callback, closure);
	}
	else
	{
		ret = ASPHODEL_DEVICE_CLOSED;
	}
	mutex_unlock(tcp_info->mutex);

	return ret;
}

static void tcp_device_stop_streaming_packets(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(tcp_info->mutex);
	tcp_stop_streaming(&tcp_info->streaming_info, ASPHODEL_SUCCESS);
	mutex_unlock(tcp_info->mutex);
}

static int tcp_remote_start_streaming_packets(AsphodelDevice_t* device, int packet_count, int transfer_count,
	unsigned int timeout, AsphodelStreamingCallback_t callback, void* closure)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	(void)transfer_count; // not used

	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_opened)
	{
		ret = tcp_start_streaming(&tcp_info->remote_streaming_info, packet_count, timeout, callback, closure);
	}
	else
	{
		ret = ASPHODEL_DEVICE_CLOSED;
	}

	mutex_unlock(tcp_info->mutex);

	return ret;
}

static void tcp_remote_stop_streaming_packets(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(tcp_info->mutex);
	tcp_stop_streaming(&tcp_info->remote_streaming_info, ASPHODEL_SUCCESS);
	mutex_unlock(tcp_info->mutex);
}

typedef struct {
	uint8_t* buffer;
	volatile size_t count;
	size_t filled;
	volatile int status;
	int completed;
} StreamBlockingClosure_t;

static void stream_packets_blocking_cb(int status, const uint8_t* stream_data, size_t packet_size, size_t packet_count, void* c)
{
	StreamBlockingClosure_t* closure = (StreamBlockingClosure_t*)c;
	size_t copy_length;

	// check for errors
	closure->status = status;
	if (status != ASPHODEL_SUCCESS)
	{
		return;
	}

	// determine size to copy
	copy_length = packet_size * packet_count;
	if (copy_length > closure->count)
	{
		copy_length = closure->count;
	}

	if (copy_length)
	{
		memcpy(&closure->buffer[closure->filled], stream_data, copy_length);
		closure->count -= copy_length;
		closure->filled += copy_length;
	}

	if (closure->count == 0)
	{
		closure->completed = 1;
	}
}

static int tcp_get_stream_packets_blocking(AsphodelDevice_t* device, uint8_t* buffer, int* count, unsigned int timeout)
{
	StreamBlockingClosure_t closure;
	clock_time_t deadline;

	int ret;
	int packet_count;
	int packet_size = (int)device->get_stream_packet_length(device);

	closure.buffer = buffer;
	closure.count = *count;
	closure.filled = 0;
	closure.status = ASPHODEL_SUCCESS;
	closure.completed = 0;

	// number of packets needed to get *count bytes (rounded up)
	packet_count = (*count + packet_size - 1) / packet_size;

	device->start_streaming_packets(device, packet_count, 1, timeout, stream_packets_blocking_cb, &closure);

	clock_get_end_time(&deadline, (int)timeout);
	while (closure.status == ASPHODEL_SUCCESS && closure.count)
	{
		int remaining = clock_milliseconds_remaining(&deadline);
		if (remaining)
		{
			tcp_poll_device(device, remaining, &closure.completed);
		}
		else
		{
			break;
		}
	}

	device->stop_streaming_packets(device);

	if (closure.status != ASPHODEL_SUCCESS)
	{
		ret = closure.status;
	}
	else if (closure.filled)
	{
		*count = (int)closure.filled;
		ret = ASPHODEL_SUCCESS;
	}
	else
	{
		ret = ASPHODEL_TIMEOUT;
	}

	return ret;
}

static size_t tcp_device_get_max_incoming_param_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->advert.max_incoming_param_length;
}

static size_t tcp_device_get_max_outgoing_param_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->advert.max_outgoing_param_length;
}

static size_t tcp_device_get_stream_packet_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->streaming_info.packet_length;
}

static size_t tcp_remote_get_max_incoming_param_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->advert.remote_max_incoming_param_length;
}

static size_t tcp_remote_get_max_outgoing_param_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->advert.remote_max_outgoing_param_length;
}

static size_t tcp_remote_get_stream_packet_length(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return tcp_info->remote_streaming_info.packet_length;
}

static int tcp_device_set_connect_callback(AsphodelDevice_t* device, AsphodelConnectCallback_t callback, void* closure)
{
	(void)device;

	// not a remote device, call the callback immediately (since it's already "connected")

	if (callback != NULL)
	{
		callback(ASPHODEL_SUCCESS, 1, closure);
	}

	return ASPHODEL_SUCCESS;
}

static int tcp_device_wait_for_connect(AsphodelDevice_t* device, unsigned int timeout)
{
	(void)device;
	(void)timeout;

	// not a remote device, just return (since it's already "connected")

	return ASPHODEL_SUCCESS;
}

static int tcp_remote_set_connect_callback(AsphodelDevice_t* device, AsphodelConnectCallback_t callback, void* closure)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(tcp_info->mutex);

	tcp_info->remote_connect_callback = callback;
	tcp_info->remote_connect_closure = closure;

	if (tcp_info->remote_connected)
	{
		if (callback != NULL)
		{
			callback(ASPHODEL_SUCCESS, 1, closure);
		}
	}

	mutex_unlock(tcp_info->mutex);

	return ASPHODEL_SUCCESS;
}

static void tcp_wait_for_connect_cb(int status, int connected, void* closure)
{
	WaitForFinishClosure_t* c = (WaitForFinishClosure_t*)closure;

	if (status != 0 || connected)
	{
		c->status = status;
		c->completed = 1;
	}
}

static int tcp_remote_wait_for_connect(AsphodelDevice_t* device, unsigned int timeout)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	WaitForFinishClosure_t c;
	clock_time_t deadline;

	// init the deadline
	clock_get_end_time(&deadline, (int)timeout);

	c.status = ASPHODEL_TIMEOUT;
	c.completed = 0;

	mutex_lock(tcp_info->mutex);
	if (tcp_info->remote_opened == 0)
	{
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_DEVICE_CLOSED;
	}
	mutex_unlock(tcp_info->mutex);

	// poll the device to make sure there's nothing pending
	device->poll_device(device, 1, NULL);

	// register the connect callback
	device->set_connect_callback(device, tcp_wait_for_connect_cb, &c);

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
	device->set_connect_callback(device, NULL, NULL);

	return c.status;
}

static int tcp_advertisement_serial_matches(const uint8_t* advert, size_t advert_len, const char* serial_number)
{
	size_t index;

	if (advert_len < 16)
	{
		// too short (even with all strings empty)
		return 0;
	}

	index = 9; // serial number field starts at fixed offset 9

	while (1)
	{
		char c = *serial_number;
		serial_number += 1;

		if (c != (char)advert[index])
		{
			// doesn't match
			return 0;
		}
		else if (c == '\0')
		{
			// end of string, must match
			return 1;
		}

		index += 1;
		if (index == advert_len)
		{
			// ran to the end of the packet
			return 0;
		}
	}
}

static int tcp_reconnect_device(AsphodelDevice_t* device, AsphodelDevice_t** reconnected_device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	return tcp_connect_device((struct sockaddr*)&tcp_info->udpaddr, tcp_info->udpaddr_len, tcp_info->reconnect_timeout, tcp_info->advert.serial_number, reconnected_device);
}

static int tcp_reconnect_remote(AsphodelDevice_t* device, AsphodelDevice_t** reconnected_device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_opened)
	{
		ret = asphodel_restart_remote_blocking(device);

		*reconnected_device = device;

		// mark as disconnected
		tcp_handle_remote_disconnect(tcp_info);
	}
	else
	{
		ret = ASPHODEL_DEVICE_CLOSED;
	}

	mutex_unlock(tcp_info->mutex);
	return ret;
}

static int tcp_reconnect_remote_bootloader(AsphodelDevice_t* device, AsphodelDevice_t** reconnected_device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_opened)
	{
		ret = asphodel_restart_remote_boot_blocking(device);

		*reconnected_device = device;

		// mark as disconnected
		tcp_handle_remote_disconnect(tcp_info);
	}
	else
	{
		ret = ASPHODEL_DEVICE_CLOSED;
	}

	mutex_unlock(tcp_info->mutex);
	return ret;
}

static int tcp_reconnect_remote_application(AsphodelDevice_t* device, AsphodelDevice_t** reconnected_device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	int ret;

	mutex_lock(tcp_info->mutex);

	if (tcp_info->remote_opened)
	{
		ret = asphodel_restart_remote_app_blocking(device);

		*reconnected_device = device;

		// mark as disconnected
		tcp_handle_remote_disconnect(tcp_info);
	}
	else
	{
		ret = ASPHODEL_DEVICE_CLOSED;
	}

	mutex_unlock(tcp_info->mutex);
	return ret;
}

static int tcp_get_remote_lengths(AsphodelDevice_t * device, size_t *max_incoming_param_length, size_t *max_outgoing_param_length, size_t *stream_packet_length)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;

	mutex_lock(tcp_info->mutex);

	if (!asphodel_supports_radio_commands(device))
	{
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_NOT_SUPPORTED;
	}

	if (max_incoming_param_length != NULL)
	{
		*max_incoming_param_length = tcp_info->advert.remote_max_incoming_param_length;
	}

	if (max_outgoing_param_length != NULL)
	{
		*max_outgoing_param_length = tcp_info->advert.remote_max_outgoing_param_length;
	}

	if (stream_packet_length != NULL)
	{
		*stream_packet_length = tcp_info->advert.remote_stream_packet_length;
	}

	mutex_unlock(tcp_info->mutex);

	return ASPHODEL_SUCCESS;
}

static int tcp_get_remote_device_invalid(AsphodelDevice_t* device, AsphodelDevice_t** remote_device)
{
	(void)device;
	(void)remote_device;
	return ASPHODEL_NOT_SUPPORTED;
}

static int tcp_get_remote_device(AsphodelDevice_t* device, AsphodelDevice_t** remote_device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	AsphodelDevice_t* d;
	char* location_string;
	size_t orig_location_len;

	mutex_lock(tcp_info->mutex);

	if (!asphodel_supports_radio_commands(device))
	{
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_BAD_PARAMETER;
	}

	d = (AsphodelDevice_t*)malloc(sizeof(AsphodelDevice_t));
	if (d == NULL)
	{
		// out of memory
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_NO_MEM;
	}

	// make location string (add "-remote" to the original)
	orig_location_len = strlen(device->location_string);
	location_string = (char*)malloc(orig_location_len + 7 + 1);
	if (location_string == NULL)
	{
		free(d);
		mutex_unlock(tcp_info->mutex);
		return ASPHODEL_NO_MEM;
	}
	memcpy(location_string, device->location_string, orig_location_len + 1);
	memcpy(&location_string[orig_location_len], "-remote", 7 + 1);

	// setup the device
	d->protocol_type = ASPHODEL_PROTOCOL_TYPE_REMOTE;
	d->location_string = location_string;
	d->open_device = tcp_open_remote;
	d->close_device = tcp_close_remote;
	d->free_device = tcp_free_device;
	d->get_serial_number = tcp_remote_get_serial_number;
	d->do_transfer = tcp_remote_do_transfer;
	d->do_transfer_reset = tcp_remote_do_transfer_reset;
	d->start_streaming_packets = tcp_remote_start_streaming_packets;
	d->stop_streaming_packets = tcp_remote_stop_streaming_packets;
	d->get_stream_packets_blocking = tcp_get_stream_packets_blocking;
	d->get_max_incoming_param_length = tcp_remote_get_max_incoming_param_length;
	d->get_max_outgoing_param_length = tcp_remote_get_max_outgoing_param_length;
	d->get_stream_packet_length = tcp_remote_get_stream_packet_length;
	d->poll_device = tcp_poll_device;
	d->set_connect_callback = tcp_remote_set_connect_callback;
	d->wait_for_connect = tcp_remote_wait_for_connect;
	d->get_remote_device = tcp_get_remote_device_invalid;
	d->reconnect_device = tcp_reconnect_remote;
	d->error_callback = NULL;
	d->error_closure = NULL;
	d->reconnect_device_bootloader = tcp_reconnect_remote_bootloader;
	d->reconnect_device_application = tcp_reconnect_remote_application;
	d->implementation_info = tcp_info;
	d->transport_type = "tcp";
	d->get_remote_lengths = tcp_get_remote_lengths;
	memset(d->reserved, 0, sizeof(d->reserved));

	tcp_info->refcount += 1;

	mutex_unlock(tcp_info->mutex);

	*remote_device = d;

	return ASPHODEL_SUCCESS;
}

ASPHODEL_API int asphodel_tcp_init(void)
{
	clock_init();

#ifdef _WIN32
	WSADATA wsaData;
	if (WSAStartup(MAKEWORD(2, 2), &wsaData) < 0)
	{
		return ASPHODEL_TRANSPORT_ERROR;
	}
#endif

	mutex_init(&poll_list_mutex);
	poll_list_size = 0;
	poll_fds = NULL;
	poll_infos = NULL;

	return ASPHODEL_SUCCESS;
}

ASPHODEL_API void asphodel_tcp_deinit(void)
{
	mutex_destroy(&poll_list_mutex);
	poll_list_size = 0;
	free(poll_fds);
	poll_fds = NULL;
	free(poll_infos);
	poll_infos = NULL;

#ifdef _WIN32
	WSACleanup();
#endif

	clock_deinit();
}

static int tcp_get_host_address(const char* host, uint16_t port, int socket_family, int ai_flags, struct sockaddr* addr, socklen_t *addrlen)
{
	char service_name[16];
	struct addrinfo hints;
	struct addrinfo *result = NULL;
	int ret;

	snprintf(service_name, sizeof(service_name), "%d", port);

	memset(&hints, 0, sizeof(hints));
	hints.ai_family = socket_family;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_protocol = IPPROTO_UDP;
	hints.ai_flags = AI_NUMERICSERV | ai_flags;
	ret = getaddrinfo(host, service_name, &hints, &result);
	if (ret != 0)
	{
		// getaddrinfo is the only place these specific errors come up
		switch (ret)
		{
		case EAI_AGAIN:
			return ASPHODEL_BUSY;
		case EAI_BADFLAGS://  invalid value for ai_flags
		case EAI_FAMILY://    ai_family not supported
		case EAI_SERVICE://   servname not supported for ai_socktype
		case EAI_SOCKTYPE://  ai_socktype not supported
			return ASPHODEL_BAD_PARAMETER;
		case EAI_FAIL://      non - recoverable failure in name resolution
			return ASPHODEL_TRANSPORT_ERROR;
		case EAI_MEMORY:
			return ASPHODEL_NO_MEM;
		case EAI_NONAME://   hostname or servname not provided, or not known
			return ASPHODEL_NOT_FOUND;
#ifdef EAI_SYSTEM
		case EAI_SYSTEM:
			return tcp_last_error();
#endif
		default:
			return ASPHODEL_BAD_PARAMETER;
		}
	}

	if (result == NULL)
	{
		// shouldn't happen
		return ASPHODEL_TRANSPORT_ERROR;
	}

	if (*addrlen < (socklen_t)result->ai_addrlen)
	{
		// not enough room
		return ASPHODEL_BAD_PARAMETER;
	}

	memcpy(addr, result->ai_addr, result->ai_addrlen);
	*addrlen = (socklen_t)result->ai_addrlen;

	freeaddrinfo(result);

	return ASPHODEL_SUCCESS;
}

static int tcp_parse_string(const uint8_t* advert, size_t advert_len, size_t* index, char** dest_str)
{
	char* str = (char*)&advert[*index];
	size_t remaining_bytes = advert_len - *index;
	size_t str_length;

	if (remaining_bytes == 0)
	{
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	str_length = strnlen(str, remaining_bytes);

	if (str_length == remaining_bytes)
	{
		// ran to the end of the packet with no null terminator
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	*index += str_length + 1; // +1 for null terminator
	*dest_str = str;

	return ASPHODEL_SUCCESS;
}

static int tcp_parse_advertisement(const uint8_t* advert, size_t advert_len, Asphodel_TCPAdvInfo_t* dest,
	struct sockaddr_storage* udpaddr, socklen_t *udpaddr_len, struct sockaddr_storage* tcpaddr, socklen_t *tcpaddr_len)
{
	// NOTE: see also tcp_advertisement_serial_matches for other advertisement packet parsing

	size_t incoming_cmd_buffer_size;
	size_t outgoing_cmd_buffer_size;
	size_t index;
	int ret;

	if (advert_len < 16)
	{
		// too short (even with all strings empty)
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	dest->tcp_version = advert[0];
	dest->connected = advert[1];

	size_t field_a = read_16bit_value(&advert[2]);
	size_t field_b = read_16bit_value(&advert[4]);

	if (field_a == 0)
	{
		// packet contains a proxy redirect

		if (field_b < 5 || advert_len < 16 + field_b)
		{
			// too short
			return ASPHODEL_INVALID_DESCRIPTOR;
		}

		uint16_t udp_port = read_16bit_value(&advert[6]);
		uint16_t tcp_port = read_16bit_value(&advert[8]);

		size_t host_index = 10;
		char * host;
		ret = tcp_parse_string(advert, advert_len, &host_index, &host);
		if (ret != ASPHODEL_SUCCESS)
		{
			return ret;
		}

		*udpaddr_len = sizeof(struct sockaddr_storage);
		ret = tcp_get_host_address(host, udp_port, udpaddr->ss_family, AI_NUMERICHOST, (struct sockaddr*)udpaddr, udpaddr_len);
		if (ret != ASPHODEL_SUCCESS)
		{
			return ret;
		}

		*tcpaddr_len = sizeof(struct sockaddr_storage);
		ret = tcp_get_host_address(host, tcp_port, tcpaddr->ss_family, AI_NUMERICHOST, (struct sockaddr*)tcpaddr, tcpaddr_len);
		if (ret != ASPHODEL_SUCCESS)
		{
			return ret;
		}

		// move the pointer to the new location
		advert += field_b;
		advert_len -= field_b;
		incoming_cmd_buffer_size = read_16bit_value(&advert[2]);
		outgoing_cmd_buffer_size = read_16bit_value(&advert[4]);
	}
	else
	{
		incoming_cmd_buffer_size = field_a;
		outgoing_cmd_buffer_size = field_b;
	}

	dest->stream_packet_length = read_16bit_value(&advert[6]);
	dest->protocol_type = advert[8];

	if (incoming_cmd_buffer_size < (MIN_SUPPORTED_PARAM_LEN + 2) ||
		outgoing_cmd_buffer_size < (MIN_SUPPORTED_PARAM_LEN + 2))
	{
		// incoming_cmd_buffer_size and outgoing_cmd_buffer_size aren't big enough
		return ASPHODEL_INVALID_DESCRIPTOR;
	}

	dest->max_incoming_param_length = incoming_cmd_buffer_size - 2;
	dest->max_outgoing_param_length = outgoing_cmd_buffer_size - 2;

	index = 9;
	ret = tcp_parse_string(advert, advert_len, &index, &dest->serial_number);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	dest->board_rev = advert[index];
	index += 1;

	ret = tcp_parse_string(advert, advert_len, &index, &dest->board_type);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	ret = tcp_parse_string(advert, advert_len, &index, &dest->build_info);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	ret = tcp_parse_string(advert, advert_len, &index, &dest->build_date);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	ret = tcp_parse_string(advert, advert_len, &index, &dest->user_tag1);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	ret = tcp_parse_string(advert, advert_len, &index, &dest->user_tag2);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	if ((dest->protocol_type & ASPHODEL_PROTOCOL_TYPE_RADIO) != 0)
	{
		if (index + 6 > advert_len)
		{
			// not long enough
			return ASPHODEL_INVALID_DESCRIPTOR;
		}

		size_t remote_incoming_cmd_buffer_size;
		size_t remote_outgoing_cmd_buffer_size;

		remote_incoming_cmd_buffer_size = read_16bit_value(&advert[index]);
		remote_outgoing_cmd_buffer_size = read_16bit_value(&advert[index + 2]);
		dest->remote_stream_packet_length = read_16bit_value(&advert[index + 4]);

		if (remote_incoming_cmd_buffer_size < (MIN_SUPPORTED_PARAM_LEN + 2) ||
			remote_outgoing_cmd_buffer_size < (MIN_SUPPORTED_PARAM_LEN + 2))
		{
			// remote_max_incoming_param_length and remote_max_outgoing_param_length aren't big enough
			return ASPHODEL_INVALID_DESCRIPTOR;
		}

		dest->remote_max_incoming_param_length = remote_incoming_cmd_buffer_size;
		dest->remote_max_outgoing_param_length = remote_outgoing_cmd_buffer_size;

		index += 6;
	}
	else
	{
		dest->remote_max_incoming_param_length = 0;
		dest->remote_max_outgoing_param_length = 0;
		dest->remote_stream_packet_length = 0;
	}

	return ASPHODEL_SUCCESS;
}

static char* tcp_create_location_string(struct sockaddr* addr, socklen_t addrlen)
{
	char* buffer;
	char* hbuf;
	char sbuf[NI_MAXSERV]; // small enough to be on the stack
	int ret;

	buffer = (char*)malloc(MAX_LOCATION_STRING_LENGTH);
	if (buffer == NULL)
	{
		return NULL;
	}

	hbuf = (char*)malloc(NI_MAXHOST);
	if (buffer == NULL)
	{
		free(buffer);
		return NULL;
	}

	ret = getnameinfo(addr, addrlen, hbuf, NI_MAXHOST, sbuf, sizeof(sbuf), NI_NUMERICHOST | NI_NUMERICSERV);
	if (ret != 0)
	{
		free(buffer);
		free(hbuf);
		return NULL;
	}

	if (addr->sa_family == AF_INET6)
	{
		snprintf(buffer, MAX_LOCATION_STRING_LENGTH, "TCP:[%s]:%s", hbuf, sbuf);
	}
	else
	{
		snprintf(buffer, MAX_LOCATION_STRING_LENGTH, "TCP:%s:%s", hbuf, sbuf);
	}

	free(hbuf);

	return buffer;
}

static int tcp_create_device(struct sockaddr* udpaddr, socklen_t udpaddr_len, struct sockaddr* tcpaddr, socklen_t tcpaddr_len,
		const uint8_t* advert, size_t advert_len, int reconnect_timeout, AsphodelDevice_t** device)
{
	AsphodelDevice_t* d;
	TCPDeviceInfo_t* tcp_info;
	int ret;

	d = (AsphodelDevice_t*)malloc(sizeof(AsphodelDevice_t));
	if (d == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	tcp_info = (TCPDeviceInfo_t*)malloc(sizeof(TCPDeviceInfo_t));
	if (tcp_info == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	tcp_info->raw_advert = (uint8_t*)malloc(advert_len);
	if (tcp_info->raw_advert == NULL)
	{
		free(tcp_info);
		free(d);
		return ASPHODEL_NO_MEM;
	}

	memcpy(tcp_info->raw_advert, advert, advert_len);
	memcpy(&tcp_info->udpaddr, udpaddr, udpaddr_len);
	tcp_info->udpaddr_len = udpaddr_len;
	memcpy(&tcp_info->tcpaddr, tcpaddr, tcpaddr_len);
	tcp_info->tcpaddr_len = tcpaddr_len;
	ret = tcp_parse_advertisement(tcp_info->raw_advert, advert_len, &tcp_info->advert, &tcp_info->udpaddr, &tcp_info->udpaddr_len, &tcp_info->tcpaddr, &tcp_info->tcpaddr_len);
	if (ret != ASPHODEL_SUCCESS)
	{
		free(tcp_info->raw_advert);
		free(tcp_info);
		free(d);
		return ret;
	}

	d->location_string = tcp_create_location_string(tcpaddr, tcpaddr_len);
	if (d->location_string == NULL)
	{
		free(tcp_info->raw_advert);
		free(tcp_info);
		free(d);
		return ASPHODEL_NO_MEM;
	}

	ret = mutex_init(&tcp_info->mutex);
	if (ret != ASPHODEL_SUCCESS)
	{
		free((void*)d->location_string);
		free(tcp_info->raw_advert);
		free(tcp_info);
		free(d);
		return ret;
	}

	// setup the device
	d->protocol_type = tcp_info->advert.protocol_type;
	// d->location_string is set above
	d->open_device = tcp_open_device;
	d->close_device = tcp_close_device;
	d->free_device = tcp_free_device;
	d->get_serial_number = tcp_device_get_serial_number;
	d->do_transfer = tcp_device_do_transfer;
	d->do_transfer_reset = tcp_device_do_transfer_reset;
	d->start_streaming_packets = tcp_device_start_streaming_packets;
	d->stop_streaming_packets = tcp_device_stop_streaming_packets;
	d->get_stream_packets_blocking = tcp_get_stream_packets_blocking;
	d->get_max_incoming_param_length = tcp_device_get_max_incoming_param_length;
	d->get_max_outgoing_param_length = tcp_device_get_max_outgoing_param_length;
	d->get_stream_packet_length = tcp_device_get_stream_packet_length;
	d->poll_device = tcp_poll_device;
	d->set_connect_callback = tcp_device_set_connect_callback;
	d->wait_for_connect = tcp_device_wait_for_connect;
	d->get_remote_device = tcp_get_remote_device;
	d->reconnect_device = tcp_reconnect_device;
	d->error_callback = NULL;
	d->error_closure = NULL;
	d->reconnect_device_bootloader = tcp_reconnect_device;
	d->reconnect_device_application = tcp_reconnect_device;
	d->implementation_info = tcp_info;
	d->transport_type = "tcp";
	d->get_remote_lengths = tcp_get_remote_lengths;
	memset(d->reserved, 0, sizeof(d->reserved));

	// setup tcp info
	tcp_info->opened = 0;
	tcp_info->remote_opened = 0;
	tcp_info->refcount = 1;
	tcp_info->fd = INVALID_SOCKET;
	tcp_info->recv_buffer = NULL;
	tcp_info->recv_index = 0;

	tcp_info->cmd_seq = 1;
	tcp_info->cmd_head = NULL;
	tcp_info->remote_cmd_head = NULL;

	tcp_info->streaming_info.callback = NULL;
	tcp_info->streaming_info.closure = NULL;
	tcp_info->streaming_info.packet_length = tcp_info->advert.stream_packet_length;
	tcp_info->streaming_info.buffer = NULL;
	tcp_info->streaming_info.buffer_size = 0;
	tcp_info->streaming_info.buffer_index = 0;
	tcp_info->streaming_info.timeout_ms = 0;

	tcp_info->remote_streaming_info.callback = NULL;
	tcp_info->remote_streaming_info.closure = NULL;
	tcp_info->remote_streaming_info.packet_length = tcp_info->advert.remote_stream_packet_length;
	tcp_info->remote_streaming_info.buffer = NULL;
	tcp_info->remote_streaming_info.buffer_size = 0;
	tcp_info->remote_streaming_info.buffer_index = 0;
	tcp_info->remote_streaming_info.timeout_ms = 0;

	tcp_info->remote_serial_number[0] = '\0';
	tcp_info->remote_connected = 0;
	tcp_info->remote_connect_callback = NULL;
	tcp_info->remote_connect_closure = NULL;
	tcp_info->remote_device = NULL;

	tcp_info->reconnect_timeout = reconnect_timeout;

	// return the device
	*device = d;
	return ASPHODEL_SUCCESS;
}

static int tcp_send_multicast_packet(int socket_family, TCP_SOCKET_TYPE fd)
{
	struct sockaddr_storage dest_addr;
	uint8_t send_msg[] = "\0\0Asphodel";
	int ret;
	socklen_t dest_addr_size;

	// write library version into packet
	write_16bit_value(&send_msg[0], asphodel_get_library_protocol_version());

	// initialize send address
	memset(&dest_addr, 0, sizeof(dest_addr));
	dest_addr.ss_family = socket_family;

	if (socket_family == AF_INET)
	{
		dest_addr_size = sizeof(struct sockaddr_in);

		((struct sockaddr_in*)&dest_addr)->sin_port = htons(ASPHODEL_MULTICAST_PORT);

		ret = inet_pton(socket_family, ASPHODEL_MULTICAST_ADDRESS_IPV4, &((struct sockaddr_in*)&dest_addr)->sin_addr);
		if (ret != 1)
		{
			ret = tcp_last_error();
			return ret;
		}
	}
	else if (socket_family == AF_INET6)
	{
		dest_addr_size = sizeof(struct sockaddr_in6);

		((struct sockaddr_in6*)&dest_addr)->sin6_port = htons(ASPHODEL_MULTICAST_PORT);

		ret = inet_pton(socket_family, ASPHODEL_MULTICAST_ADDRESS_IPV6, &((struct sockaddr_in6*)&dest_addr)->sin6_addr);
		if (ret != 1)
		{
			ret = tcp_last_error();
			return ret;
		}
	}
	else
	{
		// invalid socket_family
		return ASPHODEL_BAD_PARAMETER;
	}

	// enumerate the interfaces and send one packet for each
#ifdef _WIN32
	// this code is modified from the example code for GetAdaptersAddresses()
	PIP_ADAPTER_ADDRESSES pAddresses = NULL;
	ULONG outBufLen = 15000;
	ULONG flags = GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER | GAA_FLAG_SKIP_FRIENDLY_NAME;
	ULONG i = 0;
	DWORD dwRetVal;
	do
	{
		// allocate
		pAddresses = (IP_ADAPTER_ADDRESSES *)malloc(outBufLen);
		if (pAddresses == NULL)
		{
			return ASPHODEL_NO_MEM;
		}

		// call GetAdaptersAddresses
		dwRetVal = GetAdaptersAddresses(socket_family, flags, NULL, pAddresses, &outBufLen);

		if (dwRetVal == ERROR_BUFFER_OVERFLOW)
		{
			// not enough memory, try again
			free(pAddresses);
		}
		else
		{
			// success
			break;
		}

		i += 1;
	} while ((dwRetVal == ERROR_BUFFER_OVERFLOW) && (i < 3));

	// figure out the return value
	if (dwRetVal == NO_ERROR)
	{
		// keep going
	}
	else if (dwRetVal == ERROR_ADDRESS_NOT_ASSOCIATED || dwRetVal == ERROR_NO_DATA)
	{
		// didn't get any addresses
		free(pAddresses);

		// send to just the default address
		if (socket_family == AF_INET)
		{
			DWORD value = 0;
			ret = setsockopt(fd, IPPROTO_IP, IP_MULTICAST_IF, (void*)&value, sizeof(value));
			if (ret != 0)
			{
				ret = tcp_last_error();
				return ret;
			}
		}
		else if (socket_family == AF_INET6)
		{
			DWORD value = 0;
			ret = setsockopt(fd, IPPROTO_IPV6, IPV6_MULTICAST_IF, (void*)&value, sizeof(value));
			if (ret != 0)
			{
				ret = tcp_last_error();
				return ret;
			}
		}

		ret = sendto(fd, (const char *)send_msg, sizeof(send_msg), 0, (struct sockaddr*)&dest_addr, dest_addr_size);
		if (ret < 0)
		{
			ret = tcp_last_error();
			return ret;
		}

		return ASPHODEL_SUCCESS;
	}
	else if (dwRetVal == ERROR_BUFFER_OVERFLOW || dwRetVal == ERROR_NOT_ENOUGH_MEMORY)
	{
		free(pAddresses);
		return ASPHODEL_NO_MEM;
	}
	else if (dwRetVal == ERROR_INVALID_PARAMETER)
	{
		free(pAddresses);
		return ASPHODEL_BAD_PARAMETER;
	}
	else
	{
		free(pAddresses);
		return ASPHODEL_TRANSPORT_ERROR;
	}
	PIP_ADAPTER_ADDRESSES pCurrAddresses = pAddresses;
	while (pCurrAddresses != NULL)
	{
		if (pCurrAddresses->OperStatus != IfOperStatusUp || pCurrAddresses->NoMulticast)
		{
			pCurrAddresses = pCurrAddresses->Next;
			continue;
		}

		if (socket_family == AF_INET)
		{
			DWORD value = htonl(pCurrAddresses->IfIndex);
			ret = setsockopt(fd, IPPROTO_IP, IP_MULTICAST_IF, (void*)&value, sizeof(value));
			if (ret != 0)
			{
				ret = tcp_last_error();
				free(pAddresses);
				return ret;
			}
		}
		else if (socket_family == AF_INET6)
		{
			DWORD value = pCurrAddresses->Ipv6IfIndex;
			ret = setsockopt(fd, IPPROTO_IPV6, IPV6_MULTICAST_IF, (void*)&value, sizeof(value));
			if (ret != 0)
			{
				ret = tcp_last_error();
				free(pAddresses);
				return ret;
			}
		}

		// send the packet. NOTE: return value ignored because there's nothing we can do about errors on specific interfaces
		(void)sendto(fd, (const char *)send_msg, sizeof(send_msg), 0, (struct sockaddr*)&dest_addr, dest_addr_size);

		pCurrAddresses = pCurrAddresses->Next;
	}

	free(pAddresses);
#else
	// get a list of interfaces
	struct ifaddrs *ifaddr, *ifa;
	if (getifaddrs(&ifaddr) == -1)
	{
		return tcp_last_error();
	}

	// interate through the interfaces
	for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next)
	{
		if (ifa->ifa_addr == NULL ||
			ifa->ifa_addr->sa_family != socket_family ||
			(ifa->ifa_flags & IFF_UP) == 0 ||
			(ifa->ifa_flags & IFF_MULTICAST) == 0)
		{
			continue;
		}

		if (socket_family == AF_INET)
		{
			// set the source address
			struct sockaddr_in *address = (struct sockaddr_in *)ifa->ifa_addr;
			ret = setsockopt(fd, IPPROTO_IP, IP_MULTICAST_IF, &address->sin_addr, sizeof(address->sin_addr));
			if (ret != 0)
			{
				ret = tcp_last_error();
				freeifaddrs(ifaddr);
				return ret;
			}
		}
		else if (socket_family == AF_INET6)
		{
			// get the interface index
			int ifindex = if_nametoindex(ifa->ifa_name);

			// set the dest scope
			((struct sockaddr_in6 *)&dest_addr)->sin6_scope_id = ifindex;

			// set the source interface
			ret = setsockopt(fd, IPPROTO_IPV6, IPV6_MULTICAST_IF, (void*)&ifindex, sizeof(ifindex));
			if (ret != 0)
			{
				ret = tcp_last_error();
				freeifaddrs(ifaddr);
				return ret;
			}
		}

		// send the packet. NOTE: return value ignored because there's nothing we can do about errors on specific interfaces
		(void)sendto(fd, (const char *)send_msg, sizeof(send_msg), 0, (struct sockaddr*)&dest_addr, dest_addr_size);
	}

	// free memory returned by getifaddrs()
	freeifaddrs(ifaddr);
#endif
	return ASPHODEL_SUCCESS;
}

static void tcp_filter_device(AsphodelDevice_t **existing_device, AsphodelDevice_t *new_device, uint32_t flags)
{
	TCPDeviceInfo_t* existing_tcp_info = (TCPDeviceInfo_t*)(*existing_device)->implementation_info;
	TCPDeviceInfo_t* new_tcp_info = (TCPDeviceInfo_t*)new_device->implementation_info;
	int prefer_ipv4 = ((flags & ASPHODEL_TCP_FILTER_PREFER_IPV4) != 0);
	int prefer_existing;

	if (prefer_ipv4 && existing_tcp_info->tcpaddr.ss_family == AF_INET)
	{
		prefer_existing = 1;
	}
	else if (!prefer_ipv4 && existing_tcp_info->tcpaddr.ss_family == AF_INET6)
	{
		prefer_existing = 1;
	}
	else if (prefer_ipv4 && new_tcp_info->tcpaddr.ss_family == AF_INET)
	{
		prefer_existing = 0;
	}
	else if (!prefer_ipv4 && new_tcp_info->tcpaddr.ss_family == AF_INET6)
	{
		prefer_existing = 0;
	}
	else
	{
		// not clear what happened here
		prefer_existing = 1;
	}

	if (prefer_existing)
	{
		// free new device
		new_device->free_device(new_device);
	}
	else
	{
		// free existing device
		(*existing_device)->free_device(*existing_device);

		// move the new pointer into the existing one
		*existing_device = new_device;
	}
}

ASPHODEL_API int asphodel_tcp_find_devices(AsphodelDevice_t** device_list, size_t* list_size)
{
	return asphodel_tcp_find_devices_filter(device_list, list_size, ASPHODEL_TCP_FILTER_DEFAULT);
}

ASPHODEL_API int asphodel_tcp_find_devices_filter(AsphodelDevice_t **device_list, size_t *list_size, uint32_t flags)
{
	TCP_SOCKET_TYPE fd4 = INVALID_SOCKET; // ipv4
	TCP_SOCKET_TYPE fd6 = INVALID_SOCKET; // ipv6
	struct pollfd fds[2];
	nfds_t nfds;
	clock_time_t deadline;
	int remaining_ms;
	int saved_error = ASPHODEL_SUCCESS;
	size_t count = 0;
	int ret;

	// check flags
	if ((flags & ~0x7) != 0)
	{
		// set unknown bits
		return ASPHODEL_BAD_PARAMETER;
	}
	else if ((flags & ASPHODEL_TCP_FILTER_RETURN_ALL) != 0 && (flags & ~ASPHODEL_TCP_FILTER_RETURN_ALL) != 0)
	{
		// set ASPHODEL_TCP_FILTER_RETURN_ALL and other bits
		return ASPHODEL_BAD_PARAMETER;
	}

	// ipv4 setup
	if ((flags & 0x3) != ASPHODEL_TCP_FILTER_ONLY_IPV6)
	{
		int ignore_error = (flags & 0x3) != ASPHODEL_TCP_FILTER_ONLY_IPV4;

		// create ipv4 UDP socket
		fd4 = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
		if (fd4 == INVALID_SOCKET)
		{
			ret = tcp_last_error();
			if (!ignore_error)
			{
				return ret;
			}
		}
		else
		{
			// send the inquiry packet on ipv4
			ret = tcp_send_multicast_packet(AF_INET, fd4); // NOTE: will implicitly bind to INADDR_ANY
			if (ret != ASPHODEL_SUCCESS)
			{
				TCP_CLOSE_FUNC(fd4);
				fd4 = INVALID_SOCKET;
				if (!ignore_error)
				{
					return ret;
				}
			}
		}
	}

	// ipv6 setup
	if ((flags & 0x3) != ASPHODEL_TCP_FILTER_ONLY_IPV4)
	{
		int ignore_error = (flags & 0x3) != ASPHODEL_TCP_FILTER_ONLY_IPV6;

		// create ipv6 UDP socket
		fd6 = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP);
		if (fd6 == INVALID_SOCKET)
		{
			ret = tcp_last_error();
			if (!ignore_error)
			{
				// NOTE: not ignoring errors means no ipv4, so no cleanup needed
				return ret;
			}
		}
		else
		{
			// send the inquiry packet on ipv6
			ret = tcp_send_multicast_packet(AF_INET6, fd6); // NOTE: will implicitly bind to INADDR_ANY
			if (ret != ASPHODEL_SUCCESS)
			{
				TCP_CLOSE_FUNC(fd6);
				fd6 = INVALID_SOCKET;
				if (!ignore_error)
				{
					// NOTE: not ignoring errors means no ipv4, so no cleanup needed
					return ret;
				}
			}
		}
	}

	// setup file descriptor array for poll
	if (fd4 == INVALID_SOCKET && fd6 == INVALID_SOCKET)
	{
		// nothing worked
		return ret;
	}
	else if (fd6 == INVALID_SOCKET)
	{
		fds[0].fd = fd4;
		fds[0].events = POLLIN;
		nfds = 1;
	}
	else if (fd4 == INVALID_SOCKET)
	{
		fds[0].fd = fd6;
		fds[0].events = POLLIN;
		nfds = 1;
	}
	else
	{
		fds[0].fd = fd4;
		fds[0].events = POLLIN;
		fds[1].fd = fd6;
		fds[1].events = POLLIN;
		nfds = 2;
	}

	remaining_ms = INQUIRY_TIMEOUT_MS;
	clock_get_end_time(&deadline, remaining_ms);
	while (1)
	{
		ret = TCP_POLL_FUNC(fds, nfds, remaining_ms);
		if (ret < 0)
		{
			ret = tcp_last_error();

			if (fd4 != INVALID_SOCKET)
			{
				TCP_CLOSE_FUNC(fd4);
			}

			if (fd6 != INVALID_SOCKET)
			{
				TCP_CLOSE_FUNC(fd6);
			}

			return ret;
		}
		else if (ret == 0)
		{
			// timed out
			break;
		}
		else
		{
			for (size_t i = 0; i < 2; i++)
			{
				if ((fds[i].revents & POLLIN) == 0)
				{
					// nothing happened on this fd
					continue;
				}

				char advert[MAX_ADVERT_PACKET_SIZE];
				struct sockaddr_storage recv_addr;
				socklen_t addrlen = sizeof(recv_addr);
				ret = (int)recvfrom(fds[i].fd, advert, sizeof(advert), 0, (struct sockaddr*)&recv_addr, &addrlen);

				if (ret == 0 || ret > MAX_ADVERT_PACKET_SIZE)
				{
					// not a valid length, ignore
				}
				else if (ret < 0)
				{
					ret = tcp_last_error();
					if (ret != ASPHODEL_OUTGOING_PACKET_TOO_LONG)
					{
						// save the error to return if there are no devices available, ignore otherwise
						saved_error = ret;
					}
				}
				else
				{
					// valid, length is held in ret
					if (count < *list_size)
					{
						// check for duplicate addresses and serial numbers already in the list
						size_t i;
						int ignore = 0;
						int existing_sn = 0;

						for (i = 0; i < count; i++)
						{
							AsphodelDevice_t* device = device_list[i];
							TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
							if (memcmp(&tcp_info->tcpaddr, &recv_addr, addrlen) == 0)
							{
								// duplicate addresses can happen with two NICs attached to the same network
								ignore = 1;
								break;
							}
							else if ((flags & ASPHODEL_TCP_FILTER_RETURN_ALL) == 0)
							{
								if (tcp_advertisement_serial_matches((uint8_t*)advert, ret, tcp_info->advert.serial_number))
								{
									existing_sn = 1;
									break;
								}
							}
						}

						if (!ignore)
						{
							// create a unicast udp destination address using the multicast port, not the response port
							AsphodelDevice_t *new_device;
							struct sockaddr_storage udpaddr;
							memcpy(&udpaddr, &recv_addr, addrlen);

							if (udpaddr.ss_family == AF_INET6)
							{
								((struct sockaddr_in6*)&udpaddr)->sin6_port = htons(ASPHODEL_MULTICAST_PORT);
							}
							else if (udpaddr.ss_family == AF_INET)
							{
								((struct sockaddr_in*)&udpaddr)->sin_port = htons(ASPHODEL_MULTICAST_PORT);
							}
							else
							{
								// who knows? just carry on, I guess
							}

							ret = tcp_create_device((struct sockaddr*)&udpaddr, addrlen, (struct sockaddr*)&recv_addr, addrlen, (uint8_t*)advert, ret, INQUIRY_TIMEOUT_MS, &new_device);
							if (ret != ASPHODEL_SUCCESS)
							{
								// save the error to return if there are no devices available, ignore otherwise
								saved_error = ret;
							}
							else
							{
								if (existing_sn)
								{
									// will free one or the other
									tcp_filter_device(&device_list[i], new_device, flags);
								}
								else
								{
									device_list[i] = new_device;
									count += 1;
								}
							}
						}
					}
					else
					{
						// don't have space for it, but assume it represents a valid device
						count += 1;
					}
				}
			}
		}

		remaining_ms = clock_milliseconds_remaining(&deadline);
		if (remaining_ms == 0)
		{
			break;
		}
	}

	// clean up sockets
	if (fd4 != INVALID_SOCKET)
	{
		TCP_CLOSE_FUNC(fd4);
	}

	if (fd6 != INVALID_SOCKET)
	{
		TCP_CLOSE_FUNC(fd6);
	}

	*list_size = count;
	if (count == 0)
	{
		return saved_error;
	}
	else
	{
		return ASPHODEL_SUCCESS;
	}
}

static int tcp_connect_device(struct sockaddr* udpaddr, socklen_t udpaddr_len, int timeout, const char* serial, AsphodelDevice_t **device)
{
	TCP_SOCKET_TYPE fd;
	uint8_t send_msg[] = "\0\0Asphodel";
	struct pollfd fds;
	clock_time_t deadline;
	int remaining_ms;
	int ret;

	// create UDP socket
	fd = socket(udpaddr->sa_family, SOCK_DGRAM, IPPROTO_UDP);
	if (fd == INVALID_SOCKET)
	{
		return tcp_last_error();
	}

	// send the inquiry packet (will implicitly bind to INADDR_ANY)
	write_16bit_value(&send_msg[0], asphodel_get_library_protocol_version());
	ret = sendto(fd, (const char *)send_msg, sizeof(send_msg), 0, udpaddr, udpaddr_len);
	if (ret < 0)
	{
		ret = tcp_last_error();
		TCP_CLOSE_FUNC(fd);
		return ret;
	}

	fds.fd = fd;
	fds.events = POLLIN;
	remaining_ms = timeout;
	clock_get_end_time(&deadline, remaining_ms);
	while (1)
	{
		ret = TCP_POLL_FUNC(&fds, 1, remaining_ms);
		if (ret < 0)
		{
			ret = tcp_last_error();
			TCP_CLOSE_FUNC(fd);
			return ret;
		}
		else if (ret == 0)
		{
			// timed out
			break;
		}
		else
		{
			char advert[MAX_ADVERT_PACKET_SIZE];
			struct sockaddr_storage recv_addr;
			socklen_t addrlen = sizeof(recv_addr);
			ret = (int)recvfrom(fd, advert, sizeof(advert), 0, (struct sockaddr*)&recv_addr, &addrlen);

			if (ret == 0 || ret > MAX_ADVERT_PACKET_SIZE)
			{
				// not a valid length, ignore
			}
			else if (ret < 0)
			{
				// error
				ret = tcp_last_error();
				if (ret != ASPHODEL_OUTGOING_PACKET_TOO_LONG)
				{
					TCP_CLOSE_FUNC(fd);
					return ret;
				}
			}
			else
			{
				// valid, length is held in ret

				if (serial == NULL || tcp_advertisement_serial_matches((uint8_t*)advert, ret, serial))
				{
					// found the right one (or just the first one, when serial is NULL)
					TCP_CLOSE_FUNC(fd);

					return tcp_create_device(udpaddr, udpaddr_len, (struct sockaddr*)&recv_addr, addrlen, (uint8_t*)advert, ret, timeout, device);
				}
			}
		}

		remaining_ms = clock_milliseconds_remaining(&deadline);
		if (remaining_ms == 0)
		{
			break;
		}
	}

	// clean up socket
	TCP_CLOSE_FUNC(fd);

	return ASPHODEL_TIMEOUT;
}

ASPHODEL_API int asphodel_tcp_create_device(const char* host, uint16_t port, int timeout, const char* serial, AsphodelDevice_t **device)
{
	struct sockaddr_storage addr;
	socklen_t addrlen = sizeof(addr);
	int ret;

	if (timeout < INQUIRY_TIMEOUT_MS)
	{
		timeout = INQUIRY_TIMEOUT_MS;
	}

	if (port == 0)
	{
		port = ASPHODEL_MULTICAST_PORT;
	}

	ret = tcp_get_host_address(host, port, PF_UNSPEC, 0, (struct sockaddr*)&addr, &addrlen);
	if (ret != ASPHODEL_SUCCESS)
	{
		return ret;
	}

	return tcp_connect_device((struct sockaddr*)&addr, addrlen, timeout, serial, device);
}

ASPHODEL_API int asphodel_tcp_poll_devices(int milliseconds)
{
	clock_time_t deadline;
	int ret;

	clock_get_end_time(&deadline, milliseconds);

	mutex_lock(poll_list_mutex);

	while (1)
	{
		nfds_t i;
		clock_time_t now;
		int remaining;
		int next_timeout = 0;

		clock_now(&now);

		for (i = 0; i < poll_list_size; i++)
		{
			TCPDeviceInfo_t* tcp_info = poll_infos[i];
			mutex_lock(tcp_info->mutex);

			if (tcp_info->opened || tcp_info->remote_opened)
			{
				tcp_poll_device_single_pass(tcp_info);
				ret = tcp_check_timeouts(tcp_info, &now);
				if (ret != 0 && (next_timeout == 0 || ret < next_timeout))
				{
					next_timeout = ret;
				}
			}

			mutex_unlock(tcp_info->mutex);
		}

		remaining = clock_milliseconds_remaining_now(&deadline, &now);
		if (remaining == 0)
		{
			// no time left
			break;
		}
		else
		{
			int poll_time;

			if (next_timeout == 0 || remaining < next_timeout)
			{
				poll_time = remaining;
			}
			else
			{
				poll_time = next_timeout;
			}

			// wait for poll_time, or an event
			ret = TCP_POLL_FUNC(poll_fds, poll_list_size, poll_time);
			if (ret < 0)
			{
				// seems like a serious error
				mutex_unlock(poll_list_mutex);
				return tcp_last_error();
			}
			else if (ret == 0)
			{
				// timed out
				break;
			}
			else
			{
				// loop around to process the data
				continue;
			}
		}
	}

	mutex_unlock(poll_list_mutex);

	return ASPHODEL_SUCCESS;
}

ASPHODEL_API Asphodel_TCPAdvInfo_t* asphodel_tcp_get_advertisement(AsphodelDevice_t* device)
{
	TCPDeviceInfo_t* tcp_info = (TCPDeviceInfo_t*)device->implementation_info;
	return &tcp_info->advert;
}

ASPHODEL_API int asphodel_tcp_devices_supported(void)
{
	return 1;
}

#else // ASPHODEL_TCP_DEVICE

#include "asphodel.h"

ASPHODEL_API int asphodel_tcp_init(void)
{
	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API void asphodel_tcp_deinit(void)
{
	return;
}

ASPHODEL_API int asphodel_tcp_find_devices(AsphodelDevice_t** device_list, size_t* list_size)
{
	(void)device_list;
	(void)list_size;

	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API int asphodel_tcp_create_device(const char* host, uint16_t port, int timeout, const char* serial, AsphodelDevice_t **device)
{
	(void)host;
	(void)port;
	(void)timeout;
	(void)serial;
	(void)device;

	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API int asphodel_tcp_poll_devices(int milliseconds)
{
	(void)milliseconds;

	return ASPHODEL_NOT_SUPPORTED;
}

ASPHODEL_API int asphodel_tcp_devices_supported(void)
{
	return 0;
}

#endif // ASPHODEL_TCP_DEVICE
