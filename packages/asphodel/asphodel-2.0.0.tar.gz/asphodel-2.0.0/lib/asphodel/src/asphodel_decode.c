/*
 * Copyright (c) 2017, Suprock Technologies
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

#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>

#include "unpack.h"

#include "asphodel.h"

#if defined(_MSC_VER) && _MSC_VER < 1900 // NOTE: 1900 is VS2015
#define INFINITY (DBL_MAX+DBL_MAX)
#define NAN (INFINITY-INFINITY)
#endif

#ifdef _WIN32
	// assuming WIN32 is little endian
	#include <intrin.h>
	#define be_to_native_32b(x) _byteswap_ulong(x)
	#define be_to_native_64b(x) _byteswap_uint64(x)
	#define le_to_native_32b(x) (x)
	#define le_to_native_64b(x) (x)
#else
	#ifdef __GNUC__
		#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
			#define be_to_native_32b(x) (x)
			#define be_to_native_64b(x) (x)
			#define le_to_native_32b(x) __builtin_bswap32(x)
			#define le_to_native_64b(x) __builtin_bswap64(x)
		#elif __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
			#define be_to_native_32b(x) __builtin_bswap32(x)
			#define be_to_native_64b(x) __builtin_bswap64(x)
			#define le_to_native_32b(x) (x)
			#define le_to_native_64b(x) (x)
		#else
			#error "Unsupported endianness!"
		#endif
	#else
		#include <arpa/inet.h> // for htonl and ntohl
	#endif
#endif

static __inline float read_be_float_value(const uint8_t *src)
{
	// casting from uint32_t* to float* would violate strict-aliasing rules
	union u {
		float f;
		uint32_t i;
	} u;
	memcpy(&u.i, src, 4);
	u.i = be_to_native_32b(u.i);
	return u.f;
}

static __inline float read_le_float_value(const uint8_t *src)
{
	// casting from uint32_t* to float* would violate strict-aliasing rules
	union u {
		float f;
		uint32_t i;
	} u;
	memcpy(&u.i, src, 4);
	u.i = le_to_native_32b(u.i);
	return u.f;
}

static __inline double read_be_double_value(const uint8_t *src)
{
	// casting from uint32_t* to float* would violate strict-aliasing rules
	union u {
		double f;
		uint64_t i;
	} u;
	memcpy(&u.i, src, 8);
	u.i = be_to_native_64b(u.i);
	return u.f;
}

static __inline double read_le_double_value(const uint8_t *src)
{
	// casting from uint32_t* to float* would violate strict-aliasing rules
	union u {
		double f;
		uint64_t i;
	} u;
	memcpy(&u.i, src, 8);
	u.i = le_to_native_64b(u.i);
	return u.f;
}

static void free_basic_decoder(AsphodelChannelDecoder_t *decoder)
{
	free(decoder->channel_name);

	free(decoder);
}

static void reset_basic_decoder(AsphodelChannelDecoder_t *decoder)
{
	// nothing to do
	(void)decoder; // suppress unused parameter warning
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double scale;
	double offset;
	double base_scale;
	double base_offset;

	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;

	double data[];
} LinearChannelDecoder_t;

static void decode_linear(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	LinearChannelDecoder_t *d = (LinearChannelDecoder_t*)decoder;
	size_t i;

	d->unpack(&buffer[d->unpack_byte_offset], d->data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i] = d->data[i] * d->scale + d->offset;
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void free_linear_decoder(AsphodelChannelDecoder_t *decoder)
{
	LinearChannelDecoder_t *d = (LinearChannelDecoder_t*)decoder;

	free_unpack(d->unpack, d->unpack_closure);

	free_basic_decoder(decoder);
}

static void set_linear_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	LinearChannelDecoder_t *d = (LinearChannelDecoder_t*)decoder;
	d->scale = d->base_scale * scale;
	d->offset = d->base_offset * scale + offset;
}

static int create_channel_decoder_linear(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	LinearChannelDecoder_t *d = (LinearChannelDecoder_t*)malloc(sizeof(LinearChannelDecoder_t) + sizeof(double) * channel_info->samples);
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed

		if (channel_info->samples * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned

		if (channel_info->samples * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_linear;
	d->decoder.free_decoder = free_linear_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_linear_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 1; // linear channels have only the main channel
	d->decoder.subchannel_names = &d->decoder.channel_name; // can cheat since there's only one subchannel
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->base_scale = channel_info->coefficients[0];
	d->base_offset = channel_info->coefficients[1];
	d->scale = d->base_scale;
	d->offset = d->base_offset;
	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double scale;
	double offset;
	double beta;
	double conversion_scale;
	double conversion_offset; // includes the -273.15
	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;

	double data[];
} NTCChannelDecoder_t;

static void decode_ntc(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	NTCChannelDecoder_t *d = (NTCChannelDecoder_t*)decoder;
	size_t i;

	d->unpack(&buffer[d->unpack_byte_offset], d->data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples; i++)
	{
		double x = d->data[i] * d->scale + d->offset;
		double ratio = (1 / x) - 1;

		if (ratio > 0)
		{
			// conversion_offset includes the -273.15
			// 1/(log(ratio)/d->beta + 1/298.15) + 273.15;
			d->data[i] = d->conversion_scale / (log(ratio) / d->beta + 1 / 298.15) + d->conversion_offset;
		}
		else
		{
			// domain error
			d->data[i] = NAN;
		}
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void free_ntc_decoder(AsphodelChannelDecoder_t *decoder)
{
	NTCChannelDecoder_t *d = (NTCChannelDecoder_t*)decoder;

	free_unpack(d->unpack, d->unpack_closure);

	free_basic_decoder(decoder);
}

static void set_ntc_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	NTCChannelDecoder_t *d = (NTCChannelDecoder_t*)decoder;
	d->conversion_scale = scale;
	d->conversion_offset = (scale * -273.15) + offset;
}

static int create_channel_decoder_ntc(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	NTCChannelDecoder_t *d = (NTCChannelDecoder_t*)malloc(sizeof(NTCChannelDecoder_t) + sizeof(double) * channel_info->samples);
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 3 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed

		if (channel_info->samples * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned

		if (channel_info->samples * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_ntc;
	d->decoder.free_decoder = free_ntc_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_ntc_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 1; // ntc channels have only the main channel
	d->decoder.subchannel_names = &d->decoder.channel_name; // can cheat since there's only one subchannel
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->scale = channel_info->coefficients[0];
	d->offset = channel_info->coefficients[1];
	d->beta = channel_info->coefficients[2];
	d->conversion_scale = 1.0;
	d->conversion_offset = -273.15;
	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

struct ArrayChannelHelperClosure_t;

typedef struct {
	AsphodelChannelDecoder_t decoder;
	size_t array_size;
	struct ArrayChannelHelperClosure_t *helper_closures;
	double *data;
	AsphodelChannelDecoder_t *array_decoders[];
} ArrayChannelDecoder_t;

typedef struct ArrayChannelHelperClosure_t {
	ArrayChannelDecoder_t *d;
	size_t subchannel_offset;
} ArrayChannelHelperClosure_t;

static void free_array_decoder(AsphodelChannelDecoder_t *decoder)
{
	ArrayChannelDecoder_t *d = (ArrayChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->array_size; i++)
	{
		d->array_decoders[i]->free_decoder(d->array_decoders[i]);
	}

	free(decoder->subchannel_names);

	free(decoder->channel_name);

	free(decoder);
}

static void reset_array_decoder(AsphodelChannelDecoder_t *decoder)
{
	ArrayChannelDecoder_t *d = (ArrayChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->array_size; i++)
	{
		d->array_decoders[i]->reset(d->array_decoders[i]);
	}
}

static void set_array_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	ArrayChannelDecoder_t *d = (ArrayChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->array_size; i++)
	{
		d->array_decoders[i]->set_conversion_factor(d->array_decoders[i], scale, offset);
	}
}

static void decode_array_helper(uint64_t counter, double *data, size_t samples, size_t subchannels, void * closure)
{
	ArrayChannelHelperClosure_t *c = (ArrayChannelHelperClosure_t*)closure;
	size_t i;
	size_t j;

	(void)counter; // suppress unused parameter warning

	for (i = 0; i < samples; i++)
	{
		for (j = 0; j < subchannels; j++)
		{
			double datapoint = data[i * subchannels + j];
			c->d->data[i * c->d->decoder.subchannels + j + c->subchannel_offset] = datapoint;
		}
	}
}

static void decode_array(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	ArrayChannelDecoder_t *d = (ArrayChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->array_size; i++)
	{
		d->array_decoders[i]->decode(d->array_decoders[i], counter, buffer);
	}

	if (d->decoder.callback)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, d->decoder.subchannels, d->decoder.closure);
	}
}

static int create_channel_decoder_array(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	ArrayChannelDecoder_t *d;
	const uint8_t *control_chunk;
	uint8_t array_size;
	uint8_t channel_type;
	uint16_t filler_bits;
	uint16_t data_bits;
	size_t array_chunks;
	size_t array_coefficients;
	size_t i;
	uint16_t array_bit_offset;
	size_t subchannel_index;

	// make sure the first chunk has at least 6 bytes
	if (channel_info->chunk_count < 1 || channel_info->chunk_lengths[0] < 6)
	{
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	control_chunk = channel_info->chunks[0];

	array_size = control_chunk[0];
	channel_type = control_chunk[1];
	filler_bits = ((uint16_t)control_chunk[2] << 8) | (uint16_t)control_chunk[3];
	data_bits = ((uint16_t)control_chunk[4] << 8) | (uint16_t)control_chunk[5];

	if (array_size == 0)
	{
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (array_size * (filler_bits + data_bits) > channel_info->data_bits)
	{
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->samples == 0)
	{
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	d = (ArrayChannelDecoder_t*)malloc(sizeof(ArrayChannelDecoder_t) + sizeof(AsphodelChannelDecoder_t*) * array_size);
	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	d->helper_closures = (ArrayChannelHelperClosure_t*)malloc(sizeof(ArrayChannelHelperClosure_t) * array_size);
	if (!d->helper_closures)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// the first set of chunks are the channel names, any after that belong to the channels
	if (channel_info->chunk_count > array_size + 1)
	{
		// simplified form of ((chunk_count - 1 - array_size) + (array_size - 1)) / array_size
		array_chunks = (channel_info->chunk_count - 2) / array_size;
	}
	else
	{
		array_chunks = 0;
	}

	array_coefficients = (channel_info->coefficients_length + array_size - 1) / array_size;

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_array;
	d->decoder.free_decoder = free_array_decoder;
	d->decoder.reset = reset_array_decoder;
	d->decoder.set_conversion_factor = set_array_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->decoder.subchannels = 0; // will be incremented inside the for loop
	d->array_size = array_size;

	array_bit_offset = channel_bit_offset + channel_info->filler_bits;

	for (i = 0; i < array_size; i++)
	{
		AsphodelChannelInfo_t array_info;
		int ret;

		if (channel_info->chunk_count > 1 + i)
		{
			array_info.name = channel_info->chunks[i + 1];
			array_info.name_length = channel_info->chunk_lengths[i + 1];
		}
		else
		{
			array_info.name = NULL;
			array_info.name_length = 0;
		}

		array_info.channel_type = channel_type;
		array_info.unit_type = channel_info->unit_type;
		array_info.filler_bits = filler_bits;
		array_info.data_bits = data_bits;
		array_info.samples = channel_info->samples;
		array_info.bits_per_sample = channel_info->bits_per_sample;

		// assign coefficients
		if ((i + 1) * array_coefficients <= channel_info->coefficients_length)
		{
			// full complement
			array_info.coefficients = &channel_info->coefficients[i * array_coefficients];
			array_info.coefficients_length = (uint8_t)array_coefficients;
		}
		else if (i * array_coefficients + 1 <= channel_info->coefficients_length)
		{
			// partial only
			array_info.coefficients = &channel_info->coefficients[i * array_coefficients];
			array_info.coefficients_length = (uint8_t)(channel_info->coefficients_length - (i * array_coefficients));
		}
		else
		{
			// none left
			array_info.coefficients = NULL;
			array_info.coefficients_length = 0;
		}

		// assign chunks
		if ((i + 1) * array_chunks + 1 + array_size <= channel_info->chunk_count)
		{
			// full complement
			array_info.chunks = &channel_info->chunks[i * array_chunks + 1 + array_size];
			array_info.chunk_lengths = &channel_info->chunk_lengths[i * array_chunks + 1 + array_size];
			array_info.chunk_count = (uint8_t)array_chunks;
		}
		else if (i * array_chunks + 1 + 1 + array_size <= channel_info->chunk_count)
		{
			// partial only
			array_info.chunks = &channel_info->chunks[i * array_chunks + 1 + array_size];
			array_info.chunk_lengths = &channel_info->chunk_lengths[i * array_chunks + 1 + array_size];
			array_info.chunk_count = (uint8_t)(channel_info->chunk_count - (i * array_chunks + 1 + array_size));
		}
		else
		{
			// none left
			array_info.chunks = NULL;
			array_info.chunk_lengths = NULL;
			array_info.chunk_count = 0;
		}

		// create a decoder for array_info
		ret = asphodel_create_channel_decoder(&array_info, array_bit_offset, &d->array_decoders[i]);
		if (ret != 0)
		{
			// error
			size_t j;

			for (j = 0; j < i; j++)
			{
				d->array_decoders[j]->free_decoder(d->array_decoders[j]);
			}

			free(d->decoder.channel_name);

			free(d);

			return ret;
		}

		// setup the helper's closure
		d->helper_closures[i].d = d;
		d->helper_closures[i].subchannel_offset = d->decoder.subchannels;
		d->array_decoders[i]->callback = decode_array_helper;
		d->array_decoders[i]->closure = &d->helper_closures[i];

		// increment things
		d->decoder.subchannels += d->array_decoders[i]->subchannels;
		array_bit_offset += filler_bits + data_bits;
	}

	d->decoder.subchannel_names = (char **)malloc(d->decoder.subchannels * sizeof(char *));
	if (d->decoder.subchannel_names == NULL)
	{
		// error
		for (i = 0; i < array_size; i++)
		{
			d->array_decoders[i]->free_decoder(d->array_decoders[i]);
		}

		free(d->decoder.channel_name);

		free(d);

		return ASPHODEL_NO_MEM;
	}

	d->data = (double *)malloc(sizeof(double) * d->decoder.subchannels * d->decoder.samples);
	if (!d->data)
	{
		// error
		for (i = 0; i < array_size; i++)
		{
			d->array_decoders[i]->free_decoder(d->array_decoders[i]);
		}

		free(d->decoder.channel_name);

		free(d->decoder.subchannel_names);
		free(d);

		return ASPHODEL_NO_MEM;
	}

	subchannel_index = 0;
	for (i = 0; i < array_size; i++)
	{
		size_t j;
		for (j = 0; j < d->array_decoders[i]->subchannels; j++)
		{
			d->decoder.subchannel_names[subchannel_index] = d->array_decoders[i]->subchannel_names[j];
			subchannel_index += 1;
		}
	}

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double scale;
	double offset;
	double base_scale;
	double base_offset;

	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;

	double neg_offset;
	char * subchannel_names[2];

	double data[];
} SlowStrainChannelDecoder_t;

static void decode_slow_strain(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	SlowStrainChannelDecoder_t *d = (SlowStrainChannelDecoder_t*)decoder;
	size_t i;

	d->unpack(&buffer[d->unpack_byte_offset], d->data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples * 2; i++)
	{
		if (i % 2 == 0)
		{
			d->data[i] = d->data[i] * d->scale + d->offset;
		}
		else
		{
			if (d->data[i] >= 0.0)
			{
				d->data[i] = sqrt(d->data[i]) * fabs(d->scale);
			}
			else
			{
				d->data[i] = sqrt(d->data[i] + d->neg_offset) * fabs(d->scale);
			}
		}
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 2, d->decoder.closure);
	}
}

static void free_slow_strain_decoder(AsphodelChannelDecoder_t *decoder)
{
	SlowStrainChannelDecoder_t *d = (SlowStrainChannelDecoder_t*)decoder;

	// d->subchannel_names[0] is a copy of d->decoder.channel_name, which is freed in free_basic_decoder()
	free(d->subchannel_names[1]);

	free_unpack(d->unpack, d->unpack_closure);

	free_basic_decoder(decoder);
}

static void set_slow_strain_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	SlowStrainChannelDecoder_t *d = (SlowStrainChannelDecoder_t*)decoder;
	d->scale = d->base_scale * scale;
	d->offset = d->base_offset * scale + offset;
}

static int create_channel_decoder_slow_strain(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	SlowStrainChannelDecoder_t *d = (SlowStrainChannelDecoder_t*)malloc(sizeof(SlowStrainChannelDecoder_t) + sizeof(double) * 2 * channel_info->samples);
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	char * std_name;
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed
		d->neg_offset = pow(2.0, -channel_info->bits_per_sample); // for converting signed to unsigned for variance

		if (channel_info->samples * 2 * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 2, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned
		d->neg_offset = 0.0; // not needed

		if (channel_info->samples * 2 * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 2, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// std_name will be "std(channel_name)"
	std_name = (char*)malloc(channel_info->name_length + 5 + 1);
	if (std_name == NULL)
	{
		free(d->decoder.channel_name);
		free(d);
		return ASPHODEL_NO_MEM;
	}

	std_name[0] = 's';
	std_name[1] = 't';
	std_name[2] = 'd';
	std_name[3] = '(';

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
		std_name[4 + i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';
	std_name[i + 4] = ')';
	std_name[i + 5] = '\0';

	d->subchannel_names[0] = d->decoder.channel_name;
	d->subchannel_names[1] = std_name;

	d->decoder.decode = decode_slow_strain;
	d->decoder.free_decoder = free_slow_strain_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_slow_strain_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 2;
	d->decoder.subchannel_names = d->subchannel_names;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->base_scale = channel_info->coefficients[0];
	d->base_offset = channel_info->coefficients[1];
	d->scale = d->base_scale;
	d->offset = d->base_offset;
	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

static int create_channel_decoder_fast_strain(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	// fast strain is basically a linear channel that accepts some extra channel-specific commands
	return create_channel_decoder_linear(channel_info, channel_bit_offset, decoder);
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double scale;
	double offset;
	double base_scale;
	double base_offset;

	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;

	double neg_offset;

	double data[];
} SlowAccelChannelDecoder_t;

static char * slow_accel_subchannel_names[6] = {
	"X",
	"Y",
	"Z",
	"std(X)",
	"std(Y)",
	"std(Z)",
};

static void decode_slow_accel(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	SlowAccelChannelDecoder_t *d = (SlowAccelChannelDecoder_t*)decoder;
	size_t i;

	d->unpack(&buffer[d->unpack_byte_offset], d->data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples * 6; i++)
	{
		if (i % 6 <= 2)
		{
			d->data[i] = d->data[i] * d->scale + d->offset;
		}
		else
		{
			if (d->data[i] >= 0.0)
			{
				d->data[i] = sqrt(d->data[i]) * fabs(d->scale);
			}
			else
			{
				d->data[i] = sqrt(d->data[i] + d->neg_offset) * fabs(d->scale);
			}
		}
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 6, d->decoder.closure);
	}
}

static void free_slow_accel_decoder(AsphodelChannelDecoder_t *decoder)
{
	SlowAccelChannelDecoder_t *d = (SlowAccelChannelDecoder_t*)decoder;

	free_unpack(d->unpack, d->unpack_closure);

	free_basic_decoder(decoder);
}

static void set_slow_accel_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	SlowAccelChannelDecoder_t *d = (SlowAccelChannelDecoder_t*)decoder;
	d->scale = d->base_scale * scale;
	d->offset = d->base_offset * scale + offset;
}

static int create_channel_decoder_slow_accel(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	SlowAccelChannelDecoder_t *d = (SlowAccelChannelDecoder_t*)malloc(sizeof(SlowAccelChannelDecoder_t) + sizeof(double) * 6 * channel_info->samples);
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed
		d->neg_offset = pow(2.0, -channel_info->bits_per_sample); // for converting signed to unsigned for variance

		if (channel_info->samples * 6 * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 6, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned
		d->neg_offset = 0.0; // not needed

		if (channel_info->samples * 6 * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 6, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_slow_accel;
	d->decoder.free_decoder = free_slow_accel_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_slow_accel_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 6;
	d->decoder.subchannel_names = slow_accel_subchannel_names;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->base_scale = channel_info->coefficients[0];
	d->base_offset = channel_info->coefficients[1];
	d->scale = d->base_scale;
	d->offset = d->base_offset;
	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	size_t byte_offset;
	double x_scale;
	double x_offset;
	double y_scale;
	double y_offset;
	double z_scale;
	double z_offset;
	double base_x_scale;
	double base_x_offset;
	double base_y_scale;
	double base_y_offset;
	double base_z_scale;
	double base_z_offset;
	double data[];
} PackedAccelChannelDecoder_t;

static char * packed_accel_subchannel_names[3] = {
	"X",
	"Y",
	"Z",
};

static void decode_packed_accel(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	PackedAccelChannelDecoder_t *d = (PackedAccelChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->decoder.samples; i++)
	{
		size_t byte_index = 5 * i + d->byte_offset;

		// unpack the data
		int16_t x = buffer[byte_index] | ((buffer[byte_index + 3] & 0x1F) << 8);
		int16_t y = buffer[byte_index + 1] | ((buffer[byte_index + 4] & 0x1F) << 8);
		int16_t z = buffer[byte_index + 2] | ((buffer[byte_index + 3] & 0xE0) << 3) | ((buffer[byte_index + 4] & 0x60) << 6);

		// turn 13-bit signed to 16-bit signed.
		x = (x ^ 0x1000) - 0x1000;
		y = (y ^ 0x1000) - 0x1000;
		z = (z ^ 0x1000) - 0x1000;

		d->data[i * 3] = (double)x * d->x_scale + d->x_offset;
		d->data[i * 3 + 1] = (double)y * d->y_scale + d->y_offset;
		d->data[i * 3 + 2] = (double)z * d->z_scale + d->z_offset;
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 3, d->decoder.closure);
	}
}

static void set_packed_accel_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	PackedAccelChannelDecoder_t *d = (PackedAccelChannelDecoder_t*)decoder;
	d->x_scale = d->base_x_scale * scale;
	d->x_offset = d->base_x_offset * scale + offset;
	d->y_scale = d->base_y_scale * scale;
	d->y_offset = d->base_y_offset * scale + offset;
	d->z_scale = d->base_z_scale * scale;
	d->z_offset = d->base_z_offset * scale + offset;
}

static int create_channel_decoder_packed_accel(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	PackedAccelChannelDecoder_t *d = (PackedAccelChannelDecoder_t*)malloc(sizeof(PackedAccelChannelDecoder_t) + sizeof(double) * 3 * channel_info->samples);
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make sure it conforms to the rudimentary decode function for packed_accels
	if (channel_info->bits_per_sample != -13 || (channel_bit_offset + channel_info->filler_bits) % 8 != 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->samples * 40 > channel_info->data_bits)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_packed_accel;
	d->decoder.free_decoder = free_basic_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_packed_accel_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 3;
	d->decoder.subchannel_names = packed_accel_subchannel_names;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	if (channel_info->coefficients_length >= 6)
	{
		d->base_x_scale = channel_info->coefficients[0];
		d->base_x_offset = channel_info->coefficients[1];
		d->base_y_scale = channel_info->coefficients[2];
		d->base_y_offset = channel_info->coefficients[3];
		d->base_z_scale = channel_info->coefficients[4];
		d->base_z_offset = channel_info->coefficients[5];
	}
	else
	{
		d->base_x_scale = channel_info->coefficients[0];
		d->base_x_offset = channel_info->coefficients[1];
		d->base_y_scale = channel_info->coefficients[0];
		d->base_y_offset = channel_info->coefficients[1];
		d->base_z_scale = channel_info->coefficients[0];
		d->base_z_offset = channel_info->coefficients[1];
	}
	d->x_scale = d->base_x_scale;
	d->x_offset = d->base_x_offset;
	d->y_scale = d->base_y_scale;
	d->y_offset = d->base_y_offset;
	d->z_scale = d->base_z_scale;
	d->z_offset = d->base_z_offset;
	d->byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;

	// NOTE: scale holds the pointer to the allocated big array (all other arrays are subarrays)

	double *scale; // scales for each bridge
	double *offset; // offsets for each bridge (never altered)
	double *base_scale; // original scales for each bridge

	double composite_offset;
	double base_offset; // original composite_offset

	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;

	size_t bridge_count;

	double *unpack_data; // holds the unpacked values (no composite, sequential)
	double *expanded_data; // holds the values to pass to the callback (with composite and interleaved)
} CompositeStrainChannelDecoder_t;

static void free_composite_strain_decoder(AsphodelChannelDecoder_t *decoder)
{
	CompositeStrainChannelDecoder_t *d = (CompositeStrainChannelDecoder_t*)decoder;
	size_t i;

	free_unpack(d->unpack, d->unpack_closure);

	free(d->scale); // the big array

	for (i = 0; i < decoder->subchannels; i++)
	{
		free(decoder->subchannel_names[i]);
	}
	free(decoder->subchannel_names);

	free(decoder->channel_name);

	free(decoder);
}

static void decode_composite_strain(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	CompositeStrainChannelDecoder_t *d = (CompositeStrainChannelDecoder_t*)decoder;
	size_t subchannel_count = d->bridge_count + 1;
	size_t i;
	size_t j;

	d->unpack(&buffer[d->unpack_byte_offset], d->unpack_data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples; i++)
	{
		double composite_value = d->composite_offset;

		for (j = 0; j < d->bridge_count; j++)
		{
			double bridge_value = d->unpack_data[j * d->decoder.samples + i] * d->scale[j] + d->offset[j];
			d->expanded_data[i * subchannel_count + 1 + j] = bridge_value;

			composite_value += bridge_value;
		}

		d->expanded_data[i * subchannel_count] = composite_value;
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->expanded_data, d->decoder.samples, subchannel_count, d->decoder.closure);
	}
}

static void set_composite_strain_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	CompositeStrainChannelDecoder_t *d = (CompositeStrainChannelDecoder_t*)decoder;
	size_t i;

	for (i = 0; i < d->bridge_count; i++)
	{
		d->scale[i] = d->base_scale[i] * scale;
	}

	d->composite_offset = d->base_offset * scale + offset;
}


static int create_channel_decoder_composite_strain(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	CompositeStrainChannelDecoder_t *d = (CompositeStrainChannelDecoder_t*)malloc(sizeof(CompositeStrainChannelDecoder_t));
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	size_t bridge_count;
	size_t i;
	double *big_array;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->chunk_count < 1)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->chunk_lengths[0] < 1)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	bridge_count = channel_info->chunks[0][0];

	if (bridge_count == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->coefficients_length < 1 + (3 * bridge_count) || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->chunk_count < (2 + 2 * bridge_count)) // first is control, then composite subchannel name, then bridge subchannel names, then bridge resistance chunks
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed

		if (bridge_count * channel_info->samples * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack((int)bridge_count * channel_info->samples, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned

		if (bridge_count * channel_info->samples * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack((int)bridge_count * channel_info->samples, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_composite_strain;
	d->decoder.free_decoder = free_composite_strain_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_composite_strain_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = bridge_count + 1;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;

	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;
	d->bridge_count = bridge_count;
	d->base_offset = channel_info->coefficients[bridge_count * 3];
	d->composite_offset = d->base_offset;

	big_array = (double*)malloc((3 * bridge_count + bridge_count * channel_info->samples + (bridge_count + 1) * channel_info->samples) * sizeof(double));
	if (big_array == NULL)
	{
		free(d->decoder.channel_name);
		free(d);
		return ASPHODEL_NO_MEM;
	}

	d->scale = big_array;
	d->offset = &big_array[bridge_count];
	d->base_scale = &big_array[bridge_count * 2];
	d->unpack_data = &big_array[bridge_count * 3];
	d->expanded_data = &big_array[bridge_count * 3 + bridge_count * channel_info->samples];

	// copy coefficients in
	for (i = 0; i < bridge_count; i++)
	{
		d->base_scale[i] = channel_info->coefficients[i * 3];
		d->scale[i] = d->base_scale[i];
		d->offset[i] = channel_info->coefficients[i * 3 + 1];
	}

	// create the subchannel name array
	d->decoder.subchannel_names = (char **)malloc((d->decoder.subchannels) * sizeof(char *));
	if (d->decoder.subchannel_names == NULL)
	{
		free(d->decoder.channel_name);
		free(d);

		return ASPHODEL_NO_MEM;
	}

	// create copies of the subchannel names (from the channel chunks)
	for (i = 0; i < d->decoder.subchannels; i++)
	{
		size_t string_length = channel_info->chunk_lengths[1 + i];
		d->decoder.subchannel_names[i] = (char *)malloc(string_length + 1);

		if (d->decoder.subchannel_names[i] == NULL)
		{
			// error
			size_t j;

			for (j = 0; j < i; j++)
			{
				free(d->decoder.subchannel_names[j]);
			}

			free(big_array);
			free(d->decoder.subchannel_names);
			free(d->decoder.channel_name);
			free(d);

			return ASPHODEL_NO_MEM;
		}

		memcpy(d->decoder.subchannel_names[i], channel_info->chunks[1 + i], string_length);

		d->decoder.subchannel_names[i][string_length] = '\0'; // null terminate
	}

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double x_scale;
	double x_offset;
	double y_scale;
	double y_offset;
	double z_scale;
	double z_offset;
	double base_x_scale;
	double base_x_offset;
	double base_y_scale;
	double base_y_offset;
	double base_z_scale;
	double base_z_offset;
	uint16_t unpack_byte_offset;
	unpack_func_t unpack;
	void *unpack_closure;
	double data[];
} LinearAccelChannelDecoder_t;

static char * linear_accel_subchannel_names[3] = {
	"X",
	"Y",
	"Z",
};

static void decode_linear_accel(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	LinearAccelChannelDecoder_t *d = (LinearAccelChannelDecoder_t*)decoder;
	size_t i;

	d->unpack(&buffer[d->unpack_byte_offset], d->data, d->unpack_closure);

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i * 3] = d->data[i * 3] * d->x_scale + d->x_offset;
		d->data[i * 3 + 1] = d->data[i * 3 + 1] * d->y_scale + d->y_offset;
		d->data[i * 3 + 2] = d->data[i * 3 + 2] * d->z_scale + d->z_offset;
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 3, d->decoder.closure);
	}
}

static void free_linear_accel_decoder(AsphodelChannelDecoder_t *decoder)
{
	LinearAccelChannelDecoder_t *d = (LinearAccelChannelDecoder_t*)decoder;

	free_unpack(d->unpack, d->unpack_closure);

	free_basic_decoder(decoder);
}

static void set_linear_accel_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	LinearAccelChannelDecoder_t *d = (LinearAccelChannelDecoder_t*)decoder;
	d->x_scale = d->base_x_scale * scale;
	d->x_offset = d->base_x_offset * scale + offset;
	d->y_scale = d->base_y_scale * scale;
	d->y_offset = d->base_y_offset * scale + offset;
	d->z_scale = d->base_z_scale * scale;
	d->z_offset = d->base_z_offset * scale + offset;
}

static int create_channel_decoder_linear_accel(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	LinearAccelChannelDecoder_t *d = (LinearAccelChannelDecoder_t*)malloc(sizeof(LinearAccelChannelDecoder_t) + sizeof(double) * 3 * channel_info->samples);
	uint16_t offset = (channel_bit_offset + channel_info->filler_bits) % 8;
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// find decode function
	if (channel_info->bits_per_sample < 0)
	{
		// signed

		if (channel_info->samples * 3 * -channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 3, -channel_info->bits_per_sample, 1, offset, &d->unpack_closure);
	}
	else
	{
		// unsigned

		if (channel_info->samples * 3 * channel_info->bits_per_sample > channel_info->data_bits)
		{
			free(d);
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}

		d->unpack = find_unpack(channel_info->samples * 3, channel_info->bits_per_sample, 0, offset, &d->unpack_closure);
	}

	if (d->unpack == NULL)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	d->decoder.decode = decode_linear_accel;
	d->decoder.free_decoder = free_linear_accel_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_linear_accel_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 3;
	d->decoder.subchannel_names = linear_accel_subchannel_names;
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	if (channel_info->coefficients_length >= 6)
	{
		d->base_x_scale = channel_info->coefficients[0];
		d->base_x_offset = channel_info->coefficients[1];
		d->base_y_scale = channel_info->coefficients[2];
		d->base_y_offset = channel_info->coefficients[3];
		d->base_z_scale = channel_info->coefficients[4];
		d->base_z_offset = channel_info->coefficients[5];
	}
	else
	{
		d->base_x_scale = channel_info->coefficients[0];
		d->base_x_offset = channel_info->coefficients[1];
		d->base_y_scale = channel_info->coefficients[0];
		d->base_y_offset = channel_info->coefficients[1];
		d->base_z_scale = channel_info->coefficients[0];
		d->base_z_offset = channel_info->coefficients[1];
	}
	d->x_scale = d->base_x_scale;
	d->x_offset = d->base_x_offset;
	d->y_scale = d->base_y_scale;
	d->y_offset = d->base_y_offset;
	d->z_scale = d->base_z_scale;
	d->z_offset = d->base_z_offset;
	d->unpack_byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

typedef struct {
	AsphodelChannelDecoder_t decoder;
	double scale;
	double offset;
	double base_scale;
	double base_offset;

	uint16_t byte_offset;

	double data[];
} FloatChannelDecoder_t;

static void decode_be_float32(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)decoder;
	size_t byte_index = d->byte_offset;
	size_t i;

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i] = read_be_float_value(&buffer[byte_index]) * d->scale + d->offset;
		byte_index += sizeof(float);
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void decode_le_float32(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)decoder;
	size_t byte_index = d->byte_offset;
	size_t i;

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i] = read_le_float_value(&buffer[byte_index]) * d->scale + d->offset;
		byte_index += sizeof(float);
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void decode_be_float64(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)decoder;
	size_t byte_index = d->byte_offset;
	size_t i;

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i] = read_be_double_value(&buffer[byte_index]) * d->scale + d->offset;
		byte_index += sizeof(double);
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void decode_le_float64(AsphodelChannelDecoder_t *decoder, uint64_t counter, const uint8_t *buffer)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)decoder;
	size_t byte_index = d->byte_offset;
	size_t i;

	for (i = 0; i < d->decoder.samples; i++)
	{
		d->data[i] = read_le_double_value(&buffer[byte_index]) * d->scale + d->offset;
		byte_index += sizeof(double);
	}

	if (d->decoder.callback != NULL)
	{
		d->decoder.callback(counter, d->data, d->decoder.samples, 1, d->decoder.closure);
	}
}

static void set_float_conversion_factor(AsphodelChannelDecoder_t *decoder, double scale, double offset)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)decoder;
	d->scale = d->base_scale * scale;
	d->offset = d->base_offset * scale + offset;
}

static int create_channel_decoder_float(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder, int16_t type_size)
{
	FloatChannelDecoder_t *d = (FloatChannelDecoder_t*)malloc(sizeof(FloatChannelDecoder_t) + sizeof(double) * channel_info->samples);
	size_t i;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	if (channel_info->coefficients_length < 2 || channel_info->samples == 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make sure we can decode it
	if (channel_info->bits_per_sample != type_size * -8 || (channel_bit_offset + channel_info->filler_bits) % 8 != 0)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	if (channel_info->samples * type_size * 8 > channel_info->data_bits)
	{
		free(d);
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}

	// make a copy of the channel name
	d->decoder.channel_name = (char*)malloc(channel_info->name_length + 1);
	if (d->decoder.channel_name == NULL)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// copy the string in
	for (i = 0; i < channel_info->name_length; i++)
	{
		d->decoder.channel_name[i] = channel_info->name[i];
	}
	d->decoder.channel_name[i] = '\0';

	// NOTE: d->decoder.decode is set in the calling function
	d->decoder.free_decoder = free_basic_decoder;
	d->decoder.reset = reset_basic_decoder;
	d->decoder.set_conversion_factor = set_float_conversion_factor;
	d->decoder.channel_bit_offset = channel_bit_offset;
	d->decoder.samples = channel_info->samples;
	d->decoder.subchannels = 1; // float channels have only the main channel
	d->decoder.subchannel_names = &d->decoder.channel_name; // can cheat since there's only one subchannel
	d->decoder.callback = NULL;
	d->decoder.closure = NULL;
	d->base_scale = channel_info->coefficients[0];
	d->base_offset = channel_info->coefficients[1];
	d->scale = d->base_scale;
	d->offset = d->base_offset;
	d->byte_offset = (channel_bit_offset + channel_info->filler_bits) / 8;

	*decoder = &d->decoder;

	return 0;
}

static int create_channel_decoder_be_float32(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	int ret = create_channel_decoder_float(channel_info, channel_bit_offset, decoder, sizeof(float));
	if (ret == 0)
	{
		(*decoder)->decode = decode_be_float32;
	}

	return ret;
}

static int create_channel_decoder_le_float32(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	int ret = create_channel_decoder_float(channel_info, channel_bit_offset, decoder, sizeof(float));
	if (ret == 0)
	{
		(*decoder)->decode = decode_le_float32;
	}

	return ret;
}

static int create_channel_decoder_be_float64(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	int ret = create_channel_decoder_float(channel_info, channel_bit_offset, decoder, sizeof(double));
	if (ret == 0)
	{
		(*decoder)->decode = decode_be_float64;
	}

	return ret;
}

static int create_channel_decoder_le_float64(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	int ret = create_channel_decoder_float(channel_info, channel_bit_offset, decoder, sizeof(double));
	if (ret == 0)
	{
		(*decoder)->decode = decode_le_float64;
	}

	return ret;
}

ASPHODEL_API int asphodel_create_channel_decoder(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, AsphodelChannelDecoder_t **decoder)
{
	switch (channel_info->channel_type)
	{
	case CHANNEL_TYPE_LINEAR:
		return create_channel_decoder_linear(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_NTC:
		return create_channel_decoder_ntc(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_ARRAY:
		return create_channel_decoder_array(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_SLOW_STRAIN:
		return create_channel_decoder_slow_strain(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_FAST_STRAIN:
		return create_channel_decoder_fast_strain(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_SLOW_ACCEL:
		return create_channel_decoder_slow_accel(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_PACKED_ACCEL:
		return create_channel_decoder_packed_accel(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_COMPOSITE_STRAIN:
		return create_channel_decoder_composite_strain(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_LINEAR_ACCEL:
		return create_channel_decoder_linear_accel(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_BIG_ENDIAN_FLOAT32:
		return create_channel_decoder_be_float32(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_BIG_ENDIAN_FLOAT64:
		return create_channel_decoder_be_float64(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_LITTLE_ENDIAN_FLOAT32:
		return create_channel_decoder_le_float32(channel_info, channel_bit_offset, decoder);
	case CHANNEL_TYPE_LITTLE_ENDIAN_FLOAT64:
		return create_channel_decoder_le_float64(channel_info, channel_bit_offset, decoder);
	default:
		return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
	}
}

ASPHODEL_API int asphodel_create_channel_decoder_checked(const AsphodelChannelInfo_t *channel_info, uint16_t channel_bit_offset, size_t stream_packet_length, AsphodelChannelDecoder_t **decoder)
{
	if (stream_packet_length != 0)
	{
		if (channel_bit_offset + channel_info->filler_bits + channel_info->data_bits > stream_packet_length * 8)
		{
			return ASPHODEL_CHANNEL_FORMAT_UNSUPPORTED;
		}
	}

	return asphodel_create_channel_decoder(channel_info, channel_bit_offset, decoder);
}

static void decode_stream(AsphodelStreamDecoder_t *decoder, const uint8_t *buffer)
{
	size_t i;
	uint64_t new_count;

	// decode the counter
	new_count = decoder->counter_decoder(&buffer[decoder->counter_byte_offset], decoder->last_count);

	// see if we lost any packets
	if (decoder->last_count + 1 != new_count)
	{
		if (decoder->lost_packet_callback)
		{
			decoder->lost_packet_callback(new_count, decoder->last_count, decoder->lost_packet_closure);
		}
	}

	decoder->last_count = new_count;

	for (i = 0; i < decoder->channels; i++)
	{
		AsphodelChannelDecoder_t *channel_decoder = decoder->decoders[i];

		// don't bother decoding channels without callbacks
		if (channel_decoder->callback)
		{
			channel_decoder->decode(channel_decoder, new_count, buffer);
		}
	}
}

static void free_stream_decoder(AsphodelStreamDecoder_t *decoder)
{
	size_t i;

	// free the channel decoders
	for (i = 0; i < decoder->channels; i++)
	{
		AsphodelChannelDecoder_t *channel_decoder = decoder->decoders[i];
		channel_decoder->free_decoder(channel_decoder);
	}

	free(decoder->decoders);
	free(decoder);
}

static void reset_stream(AsphodelStreamDecoder_t *decoder)
{
	size_t i;

	decoder->last_count = (uint64_t)(-1);

	for (i = 0; i < decoder->channels; i++)
	{
		AsphodelChannelDecoder_t *channel_decoder = decoder->decoders[i];
		channel_decoder->reset(channel_decoder);
	}
}

ASPHODEL_API int asphodel_create_stream_decoder(const AsphodelStreamAndChannels_t *info, uint16_t stream_bit_offset, AsphodelStreamDecoder_t **decoder)
{
	return asphodel_create_stream_decoder_checked(info, stream_bit_offset, 0, decoder);
}

ASPHODEL_API int asphodel_create_stream_decoder_checked(const AsphodelStreamAndChannels_t *info, uint16_t stream_bit_offset, size_t stream_packet_length, AsphodelStreamDecoder_t **decoder)
{
	AsphodelStreamInfo_t *stream_info = info->stream_info;
	AsphodelStreamDecoder_t *d = (AsphodelStreamDecoder_t*)malloc(sizeof(AsphodelStreamDecoder_t));
	AsphodelChannelDecoder_t **channel_decoders;
	AsphodelCounterDecoderFunc_t counter_decoder;
	size_t i;
	uint16_t bit_offset;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	channel_decoders = (AsphodelChannelDecoder_t **)malloc(sizeof(AsphodelChannelDecoder_t *) * stream_info->channel_count);
	if (!channel_decoders)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	// initialize bit_offset
	bit_offset = stream_info->filler_bits + stream_info->counter_bits + stream_bit_offset;

	// check that the counter bits fall within the stream_packet_length
	if (stream_packet_length != 0 && bit_offset > stream_packet_length * 8)
	{
		free(d);
		free(channel_decoders);
		return ASPHODEL_COUNTER_FORMAT_UNSUPPORTED;
	}

	counter_decoder = find_unwrap(stream_info->counter_bits, (stream_info->filler_bits + stream_bit_offset) % 8);
	if (!counter_decoder)
	{
		free(d);
		free(channel_decoders);
		return ASPHODEL_COUNTER_FORMAT_UNSUPPORTED;
	}

	// populate the struct values
	d->decode = decode_stream;
	d->free_decoder = free_stream_decoder;
	d->reset = reset_stream;
	d->last_count = (uint64_t)(-1);
	d->counter_byte_offset = (stream_info->filler_bits + stream_bit_offset) / 8;
	d->counter_decoder = counter_decoder;
	d->channels = stream_info->channel_count;
	d->decoders = channel_decoders;
	d->lost_packet_callback = NULL;
	d->lost_packet_closure = NULL;

	for (i = 0; i < stream_info->channel_count; i++)
	{
		int ret = asphodel_create_channel_decoder_checked(info->channel_info[i], bit_offset, stream_packet_length, &channel_decoders[i]);
		if (ret != 0)
		{
			// failed to create a channel decoder, free the already created ones and abort
			size_t j;
			for (j = 0; j < i; j++)
			{
				AsphodelChannelDecoder_t *channel_decoder = channel_decoders[j];
				channel_decoder->free_decoder(channel_decoder);
			}
			free(d);
			free(channel_decoders);
			return ret;
		}

		bit_offset += info->channel_info[i]->filler_bits + info->channel_info[i]->data_bits;
	}

	d->used_bits = bit_offset;
	*decoder = d;

	return 0;
}

static void decode_device(struct AsphodelDeviceDecoder_t *decoder, const uint8_t *buffer)
{
	size_t i;
	uint8_t id;

	// decode the counter
	id = decoder->id_decoder(&buffer[decoder->id_byte_offset]);

	// find the stream
	for (i = 0; i < decoder->streams; i++)
	{
		if (decoder->stream_ids[i] == id)
		{
			AsphodelStreamDecoder_t *stream_decoder = decoder->decoders[i];

			stream_decoder->decode(stream_decoder, buffer);

			return;
		}
	}

	// didn't find a stream
	if (decoder->unknown_id_callback != NULL)
	{
		decoder->unknown_id_callback(id, decoder->unknown_id_closure);
	}
}

static void free_device_decoder(struct AsphodelDeviceDecoder_t *decoder)
{
	size_t i;

	// free the stream decoders
	for (i = 0; i < decoder->streams; i++)
	{
		AsphodelStreamDecoder_t *stream_decoder = decoder->decoders[i];
		stream_decoder->free_decoder(stream_decoder);
	}

	free(decoder->decoders);
	free(decoder->stream_ids);
	free(decoder);
}

static void reset_device_decoder(struct AsphodelDeviceDecoder_t *decoder)
{
	size_t i;

	for (i = 0; i < decoder->streams; i++)
	{
		AsphodelStreamDecoder_t *stream_decoder = decoder->decoders[i];
		stream_decoder->reset(stream_decoder);
	}
}

ASPHODEL_API int asphodel_create_device_decoder(const AsphodelStreamAndChannels_t *info_array, uint8_t info_array_size, uint8_t filler_bits, uint8_t id_bits, AsphodelDeviceDecoder_t **decoder)
{
	return asphodel_create_device_decoder_checked(info_array, info_array_size, filler_bits, id_bits, 0, decoder);
}

ASPHODEL_API int asphodel_create_device_decoder_checked(const AsphodelStreamAndChannels_t *info_array, uint8_t info_array_size, uint8_t filler_bits, uint8_t id_bits, size_t stream_packet_length, AsphodelDeviceDecoder_t **decoder)
{
	AsphodelDeviceDecoder_t *d = (AsphodelDeviceDecoder_t*)malloc(sizeof(AsphodelDeviceDecoder_t));
	uint8_t *stream_ids;
	AsphodelStreamDecoder_t **stream_decoders;
	AsphodelIDDecoderFunc_t id_decoder;
	size_t i;
	uint16_t bit_offset;

	if (!d)
	{
		return ASPHODEL_NO_MEM;
	}

	stream_ids = (uint8_t*)malloc(sizeof(uint8_t) * info_array_size);
	if (!stream_ids)
	{
		free(d);
		return ASPHODEL_NO_MEM;
	}

	stream_decoders = (AsphodelStreamDecoder_t **)malloc(sizeof(AsphodelStreamDecoder_t *) * info_array_size);
	if (!stream_decoders)
	{
		free(d);
		free(stream_ids);
		return ASPHODEL_NO_MEM;
	}

	id_decoder = find_unpack_id(id_bits, filler_bits % 8);
	if (!id_decoder)
	{
		free(d);
		free(stream_ids);
		free(stream_decoders);
		return ASPHODEL_STREAM_ID_FORMAT_UNSUPPORTED;
	}

	// populate the struct values
	d->decode = decode_device;
	d->free_decoder = free_device_decoder;
	d->reset = reset_device_decoder;
	d->id_byte_offset = filler_bits / 8;
	d->id_decoder = id_decoder;
	d->streams = info_array_size;
	d->stream_ids = stream_ids;
	d->decoders = stream_decoders;
	d->unknown_id_callback = NULL;
	d->unknown_id_closure = NULL;

	// initialize bit_offset
	bit_offset = filler_bits + id_bits;

	d->used_bits = bit_offset; // initial setting

	// check that id_bits fall within the stream_packet_length
	if (stream_packet_length != 0 && bit_offset > stream_packet_length * 8)
	{
		free(d);
		free(stream_ids);
		free(stream_decoders);
		return ASPHODEL_STREAM_ID_FORMAT_UNSUPPORTED;
	}

	for (i = 0; i < info_array_size; i++)
	{
		int ret;

		stream_ids[i] = info_array[i].stream_id;

		ret = asphodel_create_stream_decoder_checked(&info_array[i], bit_offset, stream_packet_length, &stream_decoders[i]);
		if (ret != 0)
		{
			// failed to create a stream decoder, free the already created ones and abort
			size_t j;
			for (j = 0; j < i; j++)
			{
				AsphodelStreamDecoder_t *stream_decoder = stream_decoders[j];
				stream_decoder->free_decoder(stream_decoder);
			}
			free(d);
			free(stream_ids);
			free(stream_decoders);
			return ret;
		}

		// update used bits
		if (d->used_bits < stream_decoders[i]->used_bits)
		{
			d->used_bits = stream_decoders[i]->used_bits;
		}
	}

	*decoder = d;

	return 0;
}

ASPHODEL_API int asphodel_create_device_info_decoder(const AsphodelDeviceInfo_t *device_info,
    const uint8_t *active_streams, uint8_t active_streams_length, AsphodelDeviceDecoder_t **decoder)
{
	AsphodelStreamAndChannels_t *info_array;
	size_t i;
	int ret;

	if (device_info == NULL || active_streams == NULL || decoder == NULL || active_streams_length == 0)
	{
		return ASPHODEL_BAD_PARAMETER;
	}

	if (device_info->stream_count_known == 0 || device_info->channel_count_known == 0)
	{
		return ASPHODEL_BAD_PARAMETER;
	}


	info_array = (AsphodelStreamAndChannels_t*)malloc(sizeof(AsphodelStreamAndChannels_t) * active_streams_length);
	if (!info_array)
	{
		return ASPHODEL_NO_MEM;
	}

	for (i = 0; i < active_streams_length; i++)
	{
		// initialze the whole list to NULL before filling in a different loop
		// so we can do a partial free if necessary.
		info_array[i].channel_info = NULL;

		// make sure the stream indexes are valid
		if (active_streams[i] >= device_info->stream_count)
		{
			free(info_array);
			return ASPHODEL_BAD_PARAMETER;
		}

		info_array[i].stream_id = active_streams[i];
		info_array[i].stream_info = &device_info->streams[active_streams[i]];
	}

	for (i = 0; i < active_streams_length; i++)
	{
		AsphodelStreamAndChannels_t *info = &info_array[i];
		size_t j;

		if (info->stream_info->channel_count == 0)
		{
			// don't allocate anything for this stream
			continue;
		}

		info->channel_info = (AsphodelChannelInfo_t**)malloc(sizeof(AsphodelChannelInfo_t*) * info->stream_info->channel_count);
		if (!info->channel_info)
		{
			size_t k;
			for (k = 0; k < i; k++)
			{
				free(info_array[k].channel_info);
			}
			free(info_array);
			return ASPHODEL_NO_MEM;
		}

		for (j = 0; j < info->stream_info->channel_count; j++)
		{
			uint8_t channel_index = info->stream_info->channel_index_list[j];
			if (channel_index >= device_info->channel_count)
			{
				// channel does not exist
				size_t k;
				for (k = 0; k < i; k++)
				{
					free(info_array[k].channel_info);
				}
				free(info->channel_info);
				free(info_array);
				return ASPHODEL_BAD_PARAMETER;
			}
			info->channel_info[j] = &device_info->channels[channel_index];
		}
	}

	ret = asphodel_create_device_decoder_checked(info_array, active_streams_length, device_info->stream_filler_bits, device_info->stream_id_bits, device_info->stream_packet_length, decoder);

	// free everything
	for (i = 0; i < active_streams_length; i++)
	{
		free(info_array[i].channel_info);
	}
	free(info_array);

	return ret;
}

ASPHODEL_API int asphodel_get_streaming_counts(const AsphodelStreamAndChannels_t *info_array, uint8_t info_array_size,
		double response_time, double buffer_time, int *packet_count, int *transfer_count, unsigned int *timeout)
{
	size_t i;

	int internal_packet_count;
	int internal_transfer_count;
	unsigned int minimum_timeout = 0; // initialized only because some compilers aren't smart enough to figure out that all control paths set it explicitly

	double packets_per_response_time = 0.0;
	double packets_per_buffer_time = 0.0;

	if (info_array_size == 0 || response_time <= 0.0 || buffer_time <= 0.0)
	{
		return ASPHODEL_BAD_PARAMETER;
	}

	for (i = 0; i < info_array_size; i++)
	{
		AsphodelStreamInfo_t *stream_info = info_array[i].stream_info;
		double rate = stream_info->rate;
		double rate_diff = rate * (double)stream_info->rate_error;
		unsigned int stream_timeout;

		if (rate <= 0.0 || rate < rate_diff || rate_diff < 0.0)
		{
			return ASPHODEL_BAD_STREAM_RATE;
		}

		packets_per_response_time += (rate - rate_diff) * response_time;
		packets_per_buffer_time += (rate + rate_diff) * buffer_time;

		// 2 times the maximum packet interval, in millseconds (not seconds)
		stream_timeout = (unsigned int)ceil(2000.0 / (rate - rate_diff));

		if (i == 0)
		{
			minimum_timeout = stream_timeout;
		}
		else
		{
			if (minimum_timeout > stream_timeout)
			{
				minimum_timeout = stream_timeout;
			}
		}
	}

	internal_packet_count = (int)floor(packets_per_response_time);
	if (internal_packet_count <= 1)
	{
		internal_packet_count = 1;
	}

	internal_transfer_count = (int)ceil(packets_per_buffer_time / (double)internal_packet_count);
	if (internal_transfer_count <= 1)
	{
		internal_transfer_count = 1;
	}

	if (internal_packet_count != 1 && internal_transfer_count == 1)
	{
		// should have at least 2 transfers if it's not just one packet at a time
		internal_transfer_count = 2;
	}

	*packet_count = internal_packet_count;
	*transfer_count = internal_transfer_count;

	if (minimum_timeout > *timeout)
	{
		*timeout = minimum_timeout;
	}

	return 0;
}

ASPHODEL_API int asphodel_get_device_info_streaming_counts(const AsphodelDeviceInfo_t *device_info,
	double response_time, double buffer_time, int *packet_count, int *transfer_count, unsigned int *timeout)
{
	size_t i;

	int internal_packet_count;
	int internal_transfer_count;
	unsigned int minimum_timeout = 0; // initialized only because some compilers aren't smart enough to figure out that all control paths set it explicitly

	double packets_per_response_time = 0.0;
	double packets_per_buffer_time = 0.0;

	if (device_info->stream_count_known == 0 || device_info->stream_count == 0 || response_time <= 0.0 || buffer_time <= 0.0)
	{
		return ASPHODEL_BAD_PARAMETER;
	}

	for (i = 0; i < device_info->stream_count; i++)
	{
		AsphodelStreamInfo_t *stream_info = &device_info->streams[i];
		double rate = stream_info->rate;
		double rate_diff = rate * (double)stream_info->rate_error;
		unsigned int stream_timeout;

		if (rate <= 0.0 || rate < rate_diff || rate_diff < 0.0)
		{
			return ASPHODEL_BAD_STREAM_RATE;
		}

		packets_per_response_time += (rate - rate_diff) * response_time;
		packets_per_buffer_time += (rate + rate_diff) * buffer_time;

		// 2 times the maximum packet interval, in millseconds (not seconds)
		stream_timeout = (unsigned int)ceil(2000.0 / (rate - rate_diff));

		if (i == 0)
		{
			minimum_timeout = stream_timeout;
		}
		else
		{
			if (minimum_timeout > stream_timeout)
			{
				minimum_timeout = stream_timeout;
			}
		}
	}

	internal_packet_count = (int)floor(packets_per_response_time);
	if (internal_packet_count <= 1)
	{
		internal_packet_count = 1;
	}

	internal_transfer_count = (int)ceil(packets_per_buffer_time / (double)internal_packet_count);
	if (internal_transfer_count <= 1)
	{
		internal_transfer_count = 1;
	}

	if (internal_packet_count != 1 && internal_transfer_count == 1)
	{
		// should have at least 2 transfers if it's not just one packet at a time
		internal_transfer_count = 2;
	}

	*packet_count = internal_packet_count;
	*transfer_count = internal_transfer_count;

	if (minimum_timeout > *timeout)
	{
		*timeout = minimum_timeout;
	}

	return 0;
}
