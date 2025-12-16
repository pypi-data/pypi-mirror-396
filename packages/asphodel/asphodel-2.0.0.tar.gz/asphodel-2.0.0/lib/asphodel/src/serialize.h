/*
 * Copyright (c) 2015, Suprock Technologies
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

#ifndef SERIALIZE_H_
#define SERIALIZE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <string.h> // for memcpy

#if !defined(htonl) && !defined(htons) && !defined(ntohl) && !defined(ntohs)
	#ifdef _WIN32
		// assuming WIN32 is little endian
		#include <intrin.h>
		#define htonl(x) _byteswap_ulong(x)
		#define htons(x) _byteswap_ushort(x)
		#define ntohl(x) _byteswap_ulong(x)
		#define ntohs(x) _byteswap_ushort(x)
	#else
		#ifdef __GNUC__
			#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
				#define htonl(x) x
				#define htons(x) x
				#define ntohl(x) x
				#define ntohs(x) x
			#elif __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
				#define htonl(x) __builtin_bswap32(x)
				#define htons(x) __builtin_bswap16(x)
				#define ntohl(x) __builtin_bswap32(x)
				#define ntohs(x) __builtin_bswap16(x)
			#else
				#error "Unsupported endianness!"
			#endif
		#else
			#include <arpa/inet.h> // for htonl and ntohl
		#endif
	#endif
#endif

static __inline void write_32bit_value(uint8_t *dest, uint32_t value)
{
	uint32_t net_value = htonl(value);
	memcpy(dest, &net_value, 4);
}

static __inline void write_16bit_value(uint8_t *dest, uint16_t value)
{
	uint16_t net_value = htons(value);
	memcpy(dest, &net_value, 2);
}

static __inline void write_float_value(uint8_t *dest, float value)
{
	// casting from float* to uint32_t* would violate strict-aliasing rules
	union u {
		float f;
		uint32_t i;
	} u;
	u.f = value;
	u.i = htonl(u.i);
	memcpy(dest, &u.i, 4);
}

static __inline uint32_t read_32bit_value(const uint8_t *src)
{
	uint32_t net_value;
	memcpy(&net_value, src, 4);
	return ntohl(net_value);
}

static __inline uint16_t read_16bit_value(const uint8_t *src)
{
	uint16_t net_value;
	memcpy(&net_value, src, 2);
	return ntohs(net_value);
}

static __inline float read_float_value(const uint8_t *src)
{
	// casting from uint32_t* to float* would violate strict-aliasing rules
	union u {
		float f;
		uint32_t i;
	} u;
	memcpy(&u.i, src, 4);
	u.i = ntohl(u.i);
	return u.f;
}

#ifdef __cplusplus
}
#endif

#endif /* SERIALIZE_H_ */
