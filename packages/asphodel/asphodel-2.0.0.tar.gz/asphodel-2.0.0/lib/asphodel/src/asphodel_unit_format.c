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

#include <stdlib.h>
#include <math.h>
#include <float.h>

#include "snprintf.h" // for msvc++ compatibility

#include "asphodel.h"

#if defined(_MSC_VER) && _MSC_VER < 1900 // NOTE: 1900 is VS2015
#define isfinite(x) _finite(x)
#define isnan(x) _isnan(x)
#endif

#ifdef _MSC_VER
// NOTE: MSVC 2015 formats "inf" correctly, but doesn't do "nan" and instead prints "nan(ind)"
#define NEED_STRING_CONVERSION // need to convert inf, -inf and nan to string representations manually; snprintf doesn't do it
#endif

#define MAX_FORMAT_SIZE 20 // maximum size for a snprintf string
#define MAX_UNIT_SIZE 32 // maximum size for a unit string (including prefixes)


typedef struct {
	AsphodelUnitFormatter_t unit_formatter;
	char *print_format_bare; // for snprintf; takes a dobule
	char *print_format_unit; // for snprintf; takes a dobule and a unit string
#ifdef NEED_STRING_CONVERSION
	const char *print_format_str_value;
#endif
} InternalUnitFormatter_t;

typedef enum {
	OUTPUT_ENCODING_ASCII,
	OUTPUT_ENCODING_UTF8,
	OUTPUT_ENCODING_HTML,
} OutputEncoding_t;

typedef struct BaseUnitInfo_t {
	uint8_t unit_type;
	const char * unit_ascii;
	const char * unit_utf8;
	const char * unit_html;
	int (*scale_function)(struct BaseUnitInfo_t *unit_info, char *buffer, size_t buffer_size, OutputEncoding_t encoding, double value, double *scale, double *offset);
} BaseUnitInfo_t;

typedef struct {
	BaseUnitInfo_t base;
	double scale;
	double offset;
} DerivedUnitInfo_t;

static int metric_prefix(BaseUnitInfo_t *unit_info, char *buffer, size_t buffer_size, OutputEncoding_t encoding, double value, double *scale, double *offset);

static BaseUnitInfo_t metric_units[] = {
	{UNIT_TYPE_LSB, "LSB", "LSB", "LSB", NULL},
	{UNIT_TYPE_PERCENT, "%", "%", "&#37;", NULL},
	{UNIT_TYPE_VOLT, "V", "V", "V", metric_prefix},
	{UNIT_TYPE_AMPERE, "A", "A", "A", metric_prefix},
	{UNIT_TYPE_WATT, "W", "W", "W", metric_prefix},
	{UNIT_TYPE_OHM, "Ohm", "\xe2\x84\xa6", "&#8486;", metric_prefix},
	{UNIT_TYPE_CELSIUS, "deg C", "\xc2\xb0""C", "&#176;C", NULL},
	{UNIT_TYPE_PASCAL, "Pa", "Pa", "Pa", metric_prefix},
	{UNIT_TYPE_NEWTON, "N", "N", "N", metric_prefix},
	{UNIT_TYPE_M_PER_S2, "m/s^2", "m/s\xc2\xb2", "m/s<sup>2</sup>", NULL},
	{UNIT_TYPE_M_PER_S, "m/s", "m/s", "m/s", NULL},
	{UNIT_TYPE_DB, "dB", "dB", "dB", NULL},
	{UNIT_TYPE_DBM, "dBm", "dBm", "dBm", NULL},
	{UNIT_TYPE_STRAIN, "strain", "strain", "strain", NULL},
	{UNIT_TYPE_HZ, "Hz", "Hz", "Hz", metric_prefix},
	{UNIT_TYPE_SECOND, "s", "s", "s", metric_prefix},
	{UNIT_TYPE_LSB_PER_CELSIUS, "LSB/C", "LSB/\xc2\xb0""C", "LSB/&#176;C", NULL},
	{UNIT_TYPE_GRAM_PER_S, "g/s", "g/s", "g/s", metric_prefix},
	{UNIT_TYPE_L_PER_S, "L/s", "L/s", "L/s", NULL},
    {UNIT_TYPE_NEWTON_METER, "N*m", "N\xe2\x8b\x85""m", "N&#8901;m", NULL},
	{UNIT_TYPE_METER, "m", "m", "m", metric_prefix},
	{UNIT_TYPE_GRAM, "g", "g", "g", metric_prefix},
	{UNIT_TYPE_M3_PER_S, "m^3/s", "m\xc2\xb3/s", "m<sup>3</sup>/s", NULL},
	{UNIT_TYPE_VOLT_PER_VOLT, "V/V", "V/V", "V/V", metric_prefix},
};

static DerivedUnitInfo_t imperial_units[] = {
	{{UNIT_TYPE_CELSIUS, "deg F", "\xc2\xb0""F", "&#176;F", NULL}, 1.8, 32.0},
	{{UNIT_TYPE_PASCAL, "psi", "psi", "psi", NULL}, 0.000145037738, 0.0},
	{{UNIT_TYPE_NEWTON, "lbf", "lbf", "lbf", NULL}, 0.224808943, 0.0},
	{{UNIT_TYPE_M_PER_S, "ft/s", "ft/s", "ft/s", NULL}, 3.280839895013123, 0.0},
	{{UNIT_TYPE_M_PER_S2, "ft/s^2", "ft/s\xc2\xb2", "ft/s<sup>2</sup>", NULL}, 3.280839895013123, 0.0},
	{{UNIT_TYPE_GRAM_PER_S, "lb/s", "lb/s", "lb/s", NULL}, 0.0022046226218488, 0.0},
	{{UNIT_TYPE_L_PER_S, "gpm", "gpm", "gpm", NULL}, 15.850323074494, 0.0},
    {{UNIT_TYPE_NEWTON_METER, "lbf*ft", "lbf\xe2\x8b\x85""ft", "lbf&#8901;ft", NULL}, 0.737562148369551, 0.0},
	{{UNIT_TYPE_METER, "ft", "ft", "ft", NULL}, 3.280839895013123, 0.0},
	{{UNIT_TYPE_GRAM, "lb", "lb", "lb", NULL}, 0.0022046226218488, 0.0},
	{{UNIT_TYPE_M3_PER_S, "ft^3/s", "ft\xc2\xb3/s", "ft<sup>3</sup>/s", NULL}, 35.31466672148858, 0.0},
};

static const char * get_base_unit_string(BaseUnitInfo_t *unit_info, OutputEncoding_t encoding)
{
	if (encoding == OUTPUT_ENCODING_ASCII)
	{
		return unit_info->unit_ascii;
	}
	else if (encoding == OUTPUT_ENCODING_UTF8)
	{
		return unit_info->unit_utf8;
	}
	else // OUTPUT_ENCODING_HTML
	{
		return unit_info->unit_html;
	}
}

static int metric_prefix(BaseUnitInfo_t *unit_info, char *buffer, size_t buffer_size, OutputEncoding_t encoding, double value, double *scale, double *offset)
{
	const char *unit_str = get_base_unit_string(unit_info, encoding);
	const char *prefix;

	value = fabs(value);
	*offset = 0.0;

	if (!isfinite(value))
	{
		// special case of infinite
		prefix = "";
		*scale = 1.0;
	}
	else if (value < 1e15 && value >= 1e12)
	{
		prefix = "T";
		*scale = 1e-12;
	}
	else if (value >= 1e9)
	{
		prefix = "G";
		*scale = 1e-9;
	}
	else if (value >= 1e6)
	{
		prefix = "M";
		*scale = 1e-6;
	}
	else if (value >= 1e3)
	{
		prefix = "k";
		*scale = 1e-3;
	}
	else if (value >= 1)
	{
		prefix = "";
		*scale = 1.0;
	}
	else if (value >= 1e-3)
	{
		prefix = "m";
		*scale = 1e3;
	}
	else if (value >= 1e-6)
	{
		if (encoding == OUTPUT_ENCODING_ASCII)
		{
			prefix = "u";
		}
		else if (encoding == OUTPUT_ENCODING_UTF8)
		{
			prefix = "\xC2\xB5";
		}
		else // OUTPUT_ENCODING_HTML
		{
			prefix = "&#181;";
		}

		*scale = 1e6;
	}
	else if (value >= 1e-9)
	{
		prefix = "n";
		*scale = 1e9;
	}
	else if (value >= 1e-12)
	{
		prefix = "p";
		*scale = 1e12;
	}
	else if (value >= 1e-15)
	{
		prefix = "f";
		*scale = 1e15;
	}
	else
	{
		// value is way outside reasonable bounds
		prefix = "";
		*scale = 1.0;
	}

	return snprintf(buffer, buffer_size, "%s%s", prefix, unit_str);
}

static BaseUnitInfo_t * get_base_unit(uint8_t unit_type, int use_metric, double *scale, double *offset)
{
	BaseUnitInfo_t *base_unit = NULL;

	if (!use_metric)
	{
		// find an imperial unit
		size_t i;
		for (i = 0; i < sizeof(imperial_units) / sizeof(imperial_units[0]); i++)
		{
			if (imperial_units[i].base.unit_type == unit_type)
			{
				DerivedUnitInfo_t *imperial_unit = &imperial_units[i];
				*scale = imperial_unit->scale;
				*offset = imperial_unit->offset;
				return &imperial_unit->base;
			}
		}
	}

	if (base_unit == NULL)
	{
		// find a metric unit
		size_t i;
		for (i = 0; i < sizeof(metric_units)/sizeof(metric_units[0]); i++)
		{
			if (metric_units[i].unit_type == unit_type)
			{
				*scale = 1.0;
				*offset = 0.0;
				return &metric_units[i];
			}
		}
	}

	return NULL; // UNIT_TYPE_NONE or other unknown unit
}

static void create_bare_format(char *buffer, size_t buffer_size, double resolution)
{
	resolution = fabs(resolution * 1.001); // round up a bit; makes the rest of the computations simpler

	if (resolution == 0.0)
	{
		// fall back to a default
		// 7 is the approximate number of decimal digits present in a C float
		snprintf(buffer, buffer_size, "%%.7g");
	}
	else
	{
		int digits = (int)ceil(-log10(resolution));
		if (digits >= 0)
		{
			snprintf(buffer, buffer_size, "%%.%df", digits);
		}
		else
		{
			snprintf(buffer, buffer_size, "%%.0f");
		}
	}
}

static void create_unit_format(char *buffer, size_t buffer_size, double resolution)
{
	char format[MAX_FORMAT_SIZE];

	create_bare_format(format, MAX_FORMAT_SIZE, resolution);
	snprintf(buffer, buffer_size, "%s %%s", format);
}

static int format_bare(struct AsphodelUnitFormatter_t *formatter, char *buffer, size_t buffer_size, double value)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;
#ifdef NEED_STRING_CONVERSION
	if (isfinite(value))
	{
#endif
		return snprintf(buffer, buffer_size, u->print_format_bare, value);
#ifdef NEED_STRING_CONVERSION
	}
	else
	{
		if (isnan(value))
		{
			return snprintf(buffer, buffer_size, "nan");
		}
		else
		{
			if (value > 0)
			{
				return snprintf(buffer, buffer_size, "inf");
			}
			else
			{
				return snprintf(buffer, buffer_size, "-inf");
			}
		}
	}
#endif
}

static int format_ascii(struct AsphodelUnitFormatter_t *formatter, char *buffer, size_t buffer_size, double value)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

#ifdef NEED_STRING_CONVERSION
	if (isfinite(value))
	{
#endif
		return snprintf(buffer, buffer_size, u->print_format_unit, value, u->unit_formatter.unit_ascii);
#ifdef NEED_STRING_CONVERSION
	}
	else
	{
		const char *str;

		if (isnan(value))
		{
			str = "nan";
		}
		else
		{
			if (value > 0)
			{
				str = "inf";
			}
			else
			{
				str = "-inf";
			}
		}

		return snprintf(buffer, buffer_size, u->print_format_str_value, str, u->unit_formatter.unit_ascii);
	}
#endif
}

static int format_utf8(struct AsphodelUnitFormatter_t *formatter, char *buffer, size_t buffer_size, double value)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

#ifdef NEED_STRING_CONVERSION
	if (isfinite(value))
	{
#endif
	return snprintf(buffer, buffer_size, u->print_format_unit, value, u->unit_formatter.unit_utf8);
#ifdef NEED_STRING_CONVERSION
	}
	else
	{
		const char *str;

		if (isnan(value))
		{
			str = "nan";
		}
		else
		{
			if (value > 0)
			{
				str = "inf";
			}
			else
			{
				str = "-inf";
			}
		}

		return snprintf(buffer, buffer_size, u->print_format_str_value, str, u->unit_formatter.unit_utf8);
	}
#endif
}

static int format_html(struct AsphodelUnitFormatter_t *formatter, char *buffer, size_t buffer_size, double value)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

#ifdef NEED_STRING_CONVERSION
	if (isfinite(value))
	{
#endif
	return snprintf(buffer, buffer_size, u->print_format_unit, value, u->unit_formatter.unit_html);
#ifdef NEED_STRING_CONVERSION
	}
	else
	{
		const char *str;

		if (isnan(value))
		{
			str = "nan";
		}
		else
		{
			if (value > 0)
			{
				str = "inf";
			}
			else
			{
				str = "-inf";
			}
		}

		return snprintf(buffer, buffer_size, u->print_format_str_value, str, u->unit_formatter.unit_html);
	}
#endif
}

static void free_unknown_unit_formatter(struct AsphodelUnitFormatter_t *formatter)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

	free(u->print_format_bare);
	free(u);
}

static void free_scaled_unit_formatter(struct AsphodelUnitFormatter_t *formatter)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

	free((void*)u->unit_formatter.unit_ascii);
	free((void*)u->unit_formatter.unit_utf8);
	free((void*)u->unit_formatter.unit_html);
	free(u->print_format_bare);
	free(u->print_format_unit);
	free(u);
}

static void free_unscaled_unit_formatter(struct AsphodelUnitFormatter_t *formatter)
{
	InternalUnitFormatter_t *u = (InternalUnitFormatter_t*)formatter;

	free(u->print_format_bare);
	free(u->print_format_unit);
	free(u);
}

ASPHODEL_API AsphodelUnitFormatter_t* asphodel_create_unit_formatter(uint8_t unit_type, double minimum, double maximum, double resolution, int use_metric)
{
	InternalUnitFormatter_t *u;
	double max_value = fabs(minimum) > fabs(maximum) ? fabs(minimum) : fabs(maximum);
	double scale = 1.0;
	double offset = 0.0;
	BaseUnitInfo_t *base_unit;

	u = (InternalUnitFormatter_t*)malloc(sizeof(InternalUnitFormatter_t));
	if (u == NULL)
	{
		// out of memory
		return NULL;
	}

	u->unit_formatter.format_bare = format_bare;
	u->unit_formatter.format_ascii = format_ascii;
	u->unit_formatter.format_utf8 = format_utf8;
	u->unit_formatter.format_html = format_html;

	base_unit = get_base_unit(unit_type, use_metric, &scale, &offset);
	if (base_unit == NULL)
	{
		// unknown unit
		u->unit_formatter.free = free_unknown_unit_formatter;
		u->unit_formatter.unit_ascii = "";
		u->unit_formatter.unit_utf8 = "";
		u->unit_formatter.unit_html = "";
		u->unit_formatter.conversion_scale = scale;
		u->unit_formatter.conversion_offset = offset;

		u->print_format_bare = (char *)malloc(MAX_FORMAT_SIZE);
		if (u->print_format_bare == NULL)
		{
			// out of memory
			free(u);
			return NULL;
		}

		create_bare_format(u->print_format_bare, MAX_FORMAT_SIZE, resolution);
		u->print_format_unit = u->print_format_bare; // no units available
#ifdef NEED_STRING_CONVERSION
		u->print_format_str_value = "%s";
#endif
	}
	else
	{
		if (base_unit->scale_function != NULL)
		{
			double scaled_max = max_value * scale + offset;
			double s_scale;
			double s_offset;

			u->unit_formatter.free = free_scaled_unit_formatter;
			u->unit_formatter.unit_ascii = (char *)malloc(MAX_UNIT_SIZE);
			u->unit_formatter.unit_utf8 = (char *)malloc(MAX_UNIT_SIZE);
			u->unit_formatter.unit_html = (char *)malloc(MAX_UNIT_SIZE);
			u->print_format_bare = (char *)malloc(MAX_FORMAT_SIZE);
			u->print_format_unit = (char *)malloc(MAX_FORMAT_SIZE);

			if (u->unit_formatter.unit_ascii == NULL || u->unit_formatter.unit_utf8 == NULL || u->unit_formatter.unit_html == NULL ||
					u->print_format_bare == NULL || u->print_format_unit == NULL)
			{
				// out of memory
				if (u->unit_formatter.unit_ascii != NULL)
				{
					free((void*)u->unit_formatter.unit_ascii);
				}

				if (u->unit_formatter.unit_utf8 != NULL)
				{
					free((void*)u->unit_formatter.unit_utf8);
				}

				if (u->unit_formatter.unit_html != NULL)
				{
					free((void*)u->unit_formatter.unit_html);
				}

				if (u->print_format_bare != NULL)
				{
					free(u->print_format_bare);
				}

				if (u->print_format_unit != NULL)
				{
					free(u->print_format_unit);
				}

				free(u);
				return NULL;
			}

			// these just overwrite the scales and offsets, so it's ok to call them 3 times
			base_unit->scale_function(base_unit, (char*)u->unit_formatter.unit_ascii, MAX_UNIT_SIZE, OUTPUT_ENCODING_ASCII, scaled_max, &s_scale, &s_offset);
			base_unit->scale_function(base_unit, (char*)u->unit_formatter.unit_utf8, MAX_UNIT_SIZE, OUTPUT_ENCODING_UTF8, scaled_max, &s_scale, &s_offset);
			base_unit->scale_function(base_unit, (char*)u->unit_formatter.unit_html, MAX_UNIT_SIZE, OUTPUT_ENCODING_HTML, scaled_max, &s_scale, &s_offset);

			u->unit_formatter.conversion_scale = scale * s_scale;
			u->unit_formatter.conversion_offset = offset * s_scale + s_offset;
		}
		else
		{
			u->unit_formatter.free = free_unscaled_unit_formatter;
			u->unit_formatter.unit_ascii = base_unit->unit_ascii;
			u->unit_formatter.unit_utf8 = base_unit->unit_utf8;
			u->unit_formatter.unit_html = base_unit->unit_html;

			u->print_format_bare = (char *)malloc(MAX_FORMAT_SIZE);
			u->print_format_unit = (char *)malloc(MAX_FORMAT_SIZE);

			if (u->print_format_bare == NULL || u->print_format_unit == NULL)
			{
				// out of memory
				if (u->print_format_bare != NULL)
				{
					free(u->print_format_bare);
				}

				if (u->print_format_unit != NULL)
				{
					free(u->print_format_unit);
				}

				free(u);
				return NULL;
			}

			u->unit_formatter.conversion_scale = scale;
			u->unit_formatter.conversion_offset = offset;
		}

		create_bare_format(u->print_format_bare, MAX_FORMAT_SIZE, resolution * u->unit_formatter.conversion_scale);
		create_unit_format(u->print_format_unit, MAX_FORMAT_SIZE, resolution * u->unit_formatter.conversion_scale);
#ifdef NEED_STRING_CONVERSION
		u->print_format_str_value = "%s %s";
#endif
	}

	return &u->unit_formatter;
}

ASPHODEL_API AsphodelUnitFormatter_t* asphodel_create_custom_unit_formatter(double scale, double offset, double resolution, const char *unit_ascii,
		const char *unit_utf8, const char *unit_html)
{
	double scaled_resolution;
	InternalUnitFormatter_t *u;

	u = (InternalUnitFormatter_t*)malloc(sizeof(InternalUnitFormatter_t));
	if (u == NULL)
	{
		// out of memory
		return NULL;
	}

	u->unit_formatter.format_bare = format_bare;
	u->unit_formatter.conversion_scale = scale;
	u->unit_formatter.conversion_offset = offset;

	// allocate the necessary buffers
	u->unit_formatter.free = free_scaled_unit_formatter;
	u->unit_formatter.unit_ascii = (char *)malloc(MAX_UNIT_SIZE);
	u->unit_formatter.unit_utf8 = (char *)malloc(MAX_UNIT_SIZE);
	u->unit_formatter.unit_html = (char *)malloc(MAX_UNIT_SIZE);
	u->print_format_bare = (char *)malloc(MAX_FORMAT_SIZE);
	u->print_format_unit = (char *)malloc(MAX_FORMAT_SIZE);

	if (u->unit_formatter.unit_ascii == NULL || u->unit_formatter.unit_utf8 == NULL || u->unit_formatter.unit_html == NULL ||
			u->print_format_bare == NULL || u->print_format_unit == NULL)
	{
		// out of memory
		if (u->unit_formatter.unit_ascii != NULL)
		{
			free((void*)u->unit_formatter.unit_ascii);
		}

		if (u->unit_formatter.unit_utf8 != NULL)
		{
			free((void*)u->unit_formatter.unit_utf8);
		}

		if (u->unit_formatter.unit_html != NULL)
		{
			free((void*)u->unit_formatter.unit_html);
		}

		if (u->print_format_bare != NULL)
		{
			free(u->print_format_bare);
		}

		if (u->print_format_unit != NULL)
		{
			free(u->print_format_unit);
		}

		free(u);
		return NULL;
	}

	// ascii unit
	if (unit_ascii == NULL || *unit_ascii == '\0')
	{
		// no unit: null terminate and use the bare formatter
		((char*)u->unit_formatter.unit_ascii)[0] = '\0';
		u->unit_formatter.format_ascii = format_bare;
	}
	else
	{
		snprintf((char*)u->unit_formatter.unit_ascii, MAX_UNIT_SIZE, "%s", unit_ascii);
		u->unit_formatter.format_ascii = format_ascii;
	}

	// utf8 unit
	if (unit_utf8 == NULL || *unit_utf8 == '\0')
	{
		// no unit: null terminate and use the bare formatter
		((char*)u->unit_formatter.unit_utf8)[0] = '\0';
		u->unit_formatter.format_utf8 = format_bare;
	}
	else
	{
		snprintf((char*)u->unit_formatter.unit_utf8, MAX_UNIT_SIZE, "%s", unit_utf8);
		u->unit_formatter.format_utf8 = format_utf8;
	}

	// html unit
	if (unit_html == NULL || *unit_html == '\0')
	{
		// no unit: null terminate and use the bare formatter
		((char*)u->unit_formatter.unit_html)[0] = '\0';
		u->unit_formatter.format_html = format_bare;
	}
	else
	{
		snprintf((char*)u->unit_formatter.unit_html, MAX_UNIT_SIZE, "%s", unit_html);
		u->unit_formatter.format_html = format_html;
	}

	scaled_resolution = fabs(scale * resolution);

	create_bare_format(u->print_format_bare, MAX_FORMAT_SIZE, scaled_resolution);
	create_unit_format(u->print_format_unit, MAX_FORMAT_SIZE, scaled_resolution);
#ifdef NEED_STRING_CONVERSION
	u->print_format_str_value = "%s %s";
#endif

	return &u->unit_formatter;
}

static int format_value(char *buffer, size_t buffer_size, uint8_t unit_type, double resolution, int use_metric, double value, OutputEncoding_t encoding)
{
	double scale = 1.0;
	double offset = 0.0;
	BaseUnitInfo_t *base_unit;

	base_unit = get_base_unit(unit_type, use_metric, &scale, &offset);

#ifdef NEED_STRING_CONVERSION
	if (isfinite(value))
	{
#endif
		if (base_unit == NULL)
		{
			// unknown unit
			char print_format[MAX_FORMAT_SIZE];
			create_bare_format(print_format, MAX_FORMAT_SIZE, resolution);
			return snprintf(buffer, buffer_size, print_format, value);
		}
		else
		{
			value = value * scale + offset;
			resolution = resolution * scale;
			if (base_unit->scale_function != NULL)
			{
				char print_format[MAX_FORMAT_SIZE];
				char unit_buffer[MAX_UNIT_SIZE];
				base_unit->scale_function(base_unit, unit_buffer, MAX_UNIT_SIZE, encoding, value, &scale, &offset);
				value = value * scale + offset;
				resolution = resolution * scale;
				create_unit_format(print_format, MAX_FORMAT_SIZE, resolution);
				return snprintf(buffer, buffer_size, print_format, value, unit_buffer);
			}
			else
			{
				const char *unit_str = get_base_unit_string(base_unit, encoding);
				char print_format[MAX_FORMAT_SIZE];
				create_unit_format(print_format, MAX_FORMAT_SIZE, resolution);
				return snprintf(buffer, buffer_size, print_format, value, unit_str);
			}
		}
#ifdef NEED_STRING_CONVERSION
	}
	else
	{
		const char *str;

		if (isnan(value))
		{
			str = "nan";
		}
		else
		{
			if (value > 0)
			{
				str = "inf";
			}
			else
			{
				str = "-inf";
			}
		}

		if (base_unit == NULL)
		{
			// unknown unit
			return snprintf(buffer, buffer_size, str);
		}
		else
		{
			const char *unit_str = get_base_unit_string(base_unit, encoding);
			return snprintf(buffer, buffer_size, "%s %s", str, unit_str);
		}
	}
#endif
}

ASPHODEL_API int asphodel_format_value_ascii(char *buffer, size_t buffer_size, uint8_t unit_type, double resolution, int use_metric, double value)
{
	return format_value(buffer, buffer_size, unit_type, resolution, use_metric, value, OUTPUT_ENCODING_ASCII);
}

ASPHODEL_API int asphodel_format_value_utf8(char *buffer, size_t buffer_size, uint8_t unit_type, double resolution, int use_metric, double value)
{
	return format_value(buffer, buffer_size, unit_type, resolution, use_metric, value, OUTPUT_ENCODING_UTF8);
}

ASPHODEL_API int asphodel_format_value_html(char *buffer, size_t buffer_size, uint8_t unit_type, double resolution, int use_metric, double value)
{
	return format_value(buffer, buffer_size, unit_type, resolution, use_metric, value, OUTPUT_ENCODING_HTML);
}
