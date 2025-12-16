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


#ifndef CLOCK_H_
#define CLOCK_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>
#include "asphodel_api.h"

#ifdef _WIN32

#include <Windows.h>

typedef LARGE_INTEGER clock_time_t;
#else // # not _WIN32
typedef struct timespec clock_time_t;
#endif

#ifdef _WIN32
ASPHODEL_LOCAL void clock_init(void);
ASPHODEL_LOCAL void clock_deinit(void);
#else // # not _WIN32
#define clock_init()
#define clock_deinit()
#endif

ASPHODEL_LOCAL void clock_now(clock_time_t* now);
ASPHODEL_LOCAL void clock_get_end_time(clock_time_t* end_time, int milliseconds); // uses internal now
ASPHODEL_LOCAL void clock_get_end_time_from_now(clock_time_t* end_time, clock_time_t* now, int milliseconds);
ASPHODEL_LOCAL int clock_is_finished(clock_time_t* end_time); // uses internal now
ASPHODEL_LOCAL int clock_is_finished_now(clock_time_t* end_time, clock_time_t* now);
ASPHODEL_LOCAL int clock_milliseconds_remaining(clock_time_t* end_time); // uses internal now
ASPHODEL_LOCAL int clock_milliseconds_remaining_now(clock_time_t* end_time, clock_time_t* now);

#ifdef __cplusplus
}
#endif

#endif /* CLOCK_H_ */
