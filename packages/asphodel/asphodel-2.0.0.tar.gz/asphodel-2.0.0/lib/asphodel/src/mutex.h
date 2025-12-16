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

#ifndef MUTEX_H_
#define MUTEX_H_

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32

#include <Windows.h>
#include "asphodel.h"

typedef CRITICAL_SECTION * Mutex_t;

static __inline int mutex_init(Mutex_t *mutex)
{
	Mutex_t m;

	m = (Mutex_t)malloc(sizeof(*m));
	if (m == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	InitializeCriticalSection(m);

	*mutex = m;

	return ASPHODEL_SUCCESS;
}

static __inline void mutex_destroy(Mutex_t *mutex)
{
	DeleteCriticalSection(*mutex);
	free(*mutex);
	*mutex = NULL;
}

static __inline void mutex_lock(Mutex_t mutex)
{
	EnterCriticalSection(mutex);
}

static __inline void mutex_unlock(Mutex_t mutex)
{
	LeaveCriticalSection(mutex);
}

#else // #ifdef _WIN32

#include <errno.h>
#include <pthread.h>
#include "asphodel.h"

typedef pthread_mutex_t* Mutex_t;

static __inline int mutex_init(Mutex_t *mutex)
{
	int ret;
	pthread_mutex_t *m;
	pthread_mutexattr_t attr;

	m = malloc(sizeof(pthread_mutex_t));
	if (m == NULL)
	{
		return ASPHODEL_NO_MEM;
	}

	ret = pthread_mutexattr_init(&attr);
	if (ret != 0)
	{
		free(m);
		if (ret == ENOMEM)
		{
			return ASPHODEL_NO_MEM;
		}
		else
		{
			return ASPHODEL_BAD_PARAMETER;
		}
	}

	ret = pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
	if (ret != 0)
	{
		free(m);
		pthread_mutexattr_destroy(&attr);
		return ASPHODEL_BAD_PARAMETER;
	}

	ret = pthread_mutex_init(m, &attr);
	if (ret != 0)
	{
		free(m);
		pthread_mutexattr_destroy(&attr);
		if (ret == ENOMEM)
		{
			return ASPHODEL_NO_MEM;
		}
		else
		{
			return ASPHODEL_BAD_PARAMETER;
		}
	}

	ret = pthread_mutexattr_destroy(&attr);
	if (ret != 0)
	{
		pthread_mutex_destroy(m);
		free(m);
		return ASPHODEL_BAD_PARAMETER;
	}

	*mutex = m;
	return ASPHODEL_SUCCESS;
}

static __inline void mutex_destroy(Mutex_t *mutex)
{
	pthread_mutex_destroy(*mutex);
	free(*mutex);
	*mutex = NULL;
}

static __inline void mutex_lock(Mutex_t mutex)
{
	pthread_mutex_lock(mutex);
}

static __inline void mutex_unlock(Mutex_t mutex)
{
	pthread_mutex_unlock(mutex);
}

#endif // #ifdef _WIN32

#ifdef __cplusplus
}
#endif

#endif /* MUTEX_H_ */
