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

#include <stdlib.h>
#include <limits.h>

#include "asphodel.h"
#include "clock.h"

#ifdef _WIN32

static LARGE_INTEGER clock_freq;

ASPHODEL_LOCAL void clock_init(void)
{
	QueryPerformanceFrequency(&clock_freq);
}

ASPHODEL_LOCAL void clock_deinit(void)
{
	// need to do init/deinit counting if anything ever needs to go here, since both USB and TCP call this
}

ASPHODEL_LOCAL void clock_now(clock_time_t* now)
{
	QueryPerformanceCounter(now);
}

ASPHODEL_LOCAL void clock_get_end_time(clock_time_t* end_time, int milliseconds)
{
	clock_time_t now;
	QueryPerformanceCounter(&now);

	end_time->QuadPart = now.QuadPart + (milliseconds * clock_freq.QuadPart) / 1000;
}

ASPHODEL_LOCAL void clock_get_end_time_from_now(clock_time_t* end_time, clock_time_t* now, int milliseconds)
{
	end_time->QuadPart = now->QuadPart + (milliseconds * clock_freq.QuadPart) / 1000;
}

ASPHODEL_LOCAL int clock_is_finished(clock_time_t* end_time)
{
	clock_time_t now;
	QueryPerformanceCounter(&now);

	return (end_time->QuadPart <= now.QuadPart);
}

ASPHODEL_LOCAL int clock_is_finished_now(clock_time_t* end_time, clock_time_t* now)
{
	return (end_time->QuadPart <= now->QuadPart);
}

ASPHODEL_LOCAL int clock_milliseconds_remaining(clock_time_t* end_time)
{
	clock_time_t now;
	QueryPerformanceCounter(&now);

	if (now.QuadPart < end_time->QuadPart)
	{
		LARGE_INTEGER diff;
		diff.QuadPart = end_time->QuadPart - now.QuadPart;
		diff.QuadPart = (diff.QuadPart * 1000) / clock_freq.QuadPart;
		if (diff.QuadPart >= INT_MAX)
		{
			return INT_MAX;
		}
		else
		{
			return (int)diff.QuadPart;
		}
	}
	else
	{
		return 0;
	}
}

ASPHODEL_LOCAL int clock_milliseconds_remaining_now(clock_time_t* end_time, clock_time_t* now)
{
	if (now->QuadPart < end_time->QuadPart)
	{
		LARGE_INTEGER diff;
		diff.QuadPart = end_time->QuadPart - now->QuadPart;
		diff.QuadPart = (diff.QuadPart * 1000) / clock_freq.QuadPart;
		if (diff.QuadPart >= INT_MAX)
		{
			return INT_MAX;
		}
		else
		{
			return (int)diff.QuadPart;
		}
	}
	else
	{
		return 0;
	}
}

#else // # not _WIN32

#include <time.h>

ASPHODEL_LOCAL void clock_now(clock_time_t* now)
{
	clock_gettime(CLOCK_MONOTONIC, now);
}

ASPHODEL_LOCAL void clock_get_end_time(clock_time_t* end_time, int milliseconds)
{
	clock_gettime(CLOCK_MONOTONIC, end_time);
	end_time->tv_sec += milliseconds / 1000;
	end_time->tv_nsec += (milliseconds % 1000) * 1000000;
	if (end_time->tv_nsec > 1000000000)
	{
		end_time->tv_nsec -= 1000000000;
		end_time->tv_sec += 1;
	}
}

ASPHODEL_LOCAL void clock_get_end_time_from_now(clock_time_t* end_time, clock_time_t* now, int milliseconds)
{
	end_time->tv_sec = now->tv_sec + milliseconds / 1000;
	end_time->tv_nsec = now->tv_nsec + (milliseconds % 1000) * 1000000;
	if (end_time->tv_nsec > 1000000000)
	{
		end_time->tv_nsec -= 1000000000;
		end_time->tv_sec += 1;
	}
}

ASPHODEL_LOCAL int clock_is_finished(clock_time_t* end_time)
{
	clock_time_t now;
	clock_gettime(CLOCK_MONOTONIC, &now);

	if (now.tv_sec == end_time->tv_sec)
	{
		return (now.tv_nsec >= end_time->tv_nsec);
	}
	else if (now.tv_sec < end_time->tv_sec)
	{
		return 0;
	}
	else
	{
		return 1;
	}
}

ASPHODEL_LOCAL int clock_is_finished_now(clock_time_t* end_time, clock_time_t* now)
{
	if (now->tv_sec == end_time->tv_sec)
	{
		return (now->tv_nsec >= end_time->tv_nsec);
	}
	else if (now->tv_sec < end_time->tv_sec)
	{
		return 0;
	}
	else
	{
		return 1;
	}
}

ASPHODEL_LOCAL int clock_milliseconds_remaining(clock_time_t* end_time)
{
	clock_time_t now;
	clock_gettime(CLOCK_MONOTONIC, &now);

	if (now.tv_sec == end_time->tv_sec)
	{
		if (now.tv_nsec < end_time->tv_nsec)
		{
			return (int)((end_time->tv_nsec - now.tv_nsec) / 1000000L);
		}
		else
		{
			return 0;
		}
	}
	else if (now.tv_sec < end_time->tv_sec)
	{
		time_t seconds = (end_time->tv_sec - now.tv_sec);
		if (seconds >= (INT_MAX / 1000) - 1)
		{
			// prevent overflow
			return INT_MAX;
		}
		return ((int)seconds * 1000) + (int)((end_time->tv_nsec - now.tv_nsec) / 1000000L);
	}
	else
	{
		return 0;
	}
}

ASPHODEL_LOCAL int clock_milliseconds_remaining_now(clock_time_t* end_time, clock_time_t* now)
{
	if (now->tv_sec == end_time->tv_sec)
	{
		if (now->tv_nsec < end_time->tv_nsec)
		{
			return (int)((end_time->tv_nsec - now->tv_nsec) / 1000000L);
		}
		else
		{
			return 0;
		}
	}
	else if (now->tv_sec < end_time->tv_sec)
	{
		time_t seconds = (end_time->tv_sec - now->tv_sec);
		if (seconds >= (INT_MAX / 1000) - 1)
		{
			// prevent overflow
			return INT_MAX;
		}
		return ((int)seconds * 1000) + (int)((end_time->tv_nsec - now->tv_nsec) / 1000000L);
	}
	else
	{
		return 0;
	}
}

#endif
