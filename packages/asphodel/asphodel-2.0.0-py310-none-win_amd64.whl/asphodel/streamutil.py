import time
from typing import Any, Sequence, TypedDict, Union, cast

import numpy
from numpy.typing import NDArray

import asphodel


class ChannelData(TypedDict):
    data: list[tuple[float, int, NDArray[numpy.float64]]]
    channel: asphodel.ChannelInfo
    channel_decoder: asphodel.ChannelDecoder


class ExtraChannelData(ChannelData):
    unknown_ids: int
    lost_packets: int
    stream: asphodel.StreamInfo
    stream_decoder: asphodel.StreamDecoder
    first_packet_time: float | None
    last_packet_time: float | None


class StreamData(TypedDict):
    lost_packets: int
    stream: asphodel.StreamInfo
    stream_decoder: asphodel.StreamDecoder
    channels: dict[int, ChannelData]
    first_packet_time: float | None
    last_packet_time: float | None
    start_time: float | None


class ExtraStreamData(StreamData):
    unknown_ids: int


class DeviceData(TypedDict):
    unknown_ids: int
    streams: dict[int, StreamData]


def stream_fixed_duration(
          device: asphodel.Device,
          cached_device: asphodel.Device | None = None,
          stream_ids: Sequence[int] | None = None,
          duration: float = 2.0) -> DeviceData:

    # tighter requirements than usual because this function will be used to
    # verify stream rates
    response_time = 0.005
    buffer_time = 0.05
    timeout = 1000

    device_data: DeviceData = {
        'unknown_ids': 0,
        'streams': {},
    }

    if cached_device is None:
        cached_device = device

    stream_count, filler_bits, id_bits = cached_device.get_stream_count()

    if stream_ids is None:
        # use all streams on the device
        stream_ids = list(range(stream_count))

    max_warm_up = 0.0

    # prepare the info list
    info_list: list[tuple[int, asphodel.StreamInfo,
                          list[asphodel.ChannelInfo]]] = []
    streams: list[asphodel.StreamInfo] = []
    for stream_id in stream_ids:
        stream_struct = cached_device.get_stream(stream_id)
        streams.append(stream_struct)

        max_warm_up = max(max_warm_up, stream_struct.warm_up_delay)

        channel_info_list: list[asphodel.ChannelInfo] = []
        for ch_index in stream_struct.channel_index_list:
            channel_info_list.append(cached_device.get_channel(ch_index))
        info_list.append((stream_id, stream_struct, channel_info_list))

    # create the device decoder
    device_decoder = asphodel.DeviceDecoder.create(
        info_list, filler_bits, id_bits)

    # create & register unknown id callback
    def unknown_id_callback(lost_id: int) -> None:
        device_data['unknown_ids'] += 1
    device_decoder.set_unknown_id_callback(unknown_id_callback)

    # create & register lost packet callback
    for stream_decoder, stream_id in zip(device_decoder.decoders,
                                         device_decoder.stream_ids):
        stream_data: StreamData = {
            'lost_packets': 0,
            'stream': stream_decoder.stream_info,
            'stream_decoder': stream_decoder,
            'channels': {},
            'first_packet_time': None,
            'last_packet_time': None,
            'start_time': None,
        }
        device_data['streams'][stream_id] = stream_data

        def lost_packet_callback(
                current: int, last: int,
                stream_data: StreamData = stream_data) -> None:
            lost = (current - last - 1) & 0xFFFFFFFFFFFFFFFF
            stream_data['lost_packets'] += lost

        stream_decoder.set_lost_packet_callback(lost_packet_callback)

        channel_ids = stream_decoder.stream_info.channel_index_list
        for channel_decoder, channel_id in zip(stream_decoder.decoders,
                                               channel_ids):
            channel_data: ChannelData = {
                'data': [],
                'channel': channel_decoder.channel_info,
                'channel_decoder': channel_decoder,
            }
            stream_data['channels'][channel_id] = channel_data

            def channel_callback(
                    counter: int, data: list[float], samples: int,
                    subchannels: int, channel_data: ChannelData = channel_data,
                    stream_data: StreamData = stream_data) -> None:
                now = time.time()
                d = numpy.array(data).reshape(samples, subchannels)
                channel_data['data'].append((now, counter, d))

                if stream_data['first_packet_time'] is None:
                    stream_data['first_packet_time'] = now
                stream_data['last_packet_time'] = now

            channel_decoder.set_callback(channel_callback)

    stream_counts = asphodel.get_streaming_counts(
        streams, response_time, buffer_time, timeout)

    # warm up the streams
    for stream_id in stream_ids:
        device.warm_up_stream(stream_id, True)

    time.sleep(max_warm_up)

    error_code = 0  # OK
    start_time: float | None = None

    def packet_callback(status: int, stream_packets: list[bytes]) -> None:
        if status != 0:
            nonlocal error_code
            error_code = status
        else:
            nonlocal start_time
            if start_time is None:
                start_time = time.monotonic()
            for packet in stream_packets:
                device_decoder.decode(packet)

    # start collecting packets
    device.start_streaming_packets(*stream_counts, callback=packet_callback)

    # enable the streams
    for stream_id in stream_ids:
        device.enable_stream(stream_id, True)

        stream_data = device_data['streams'][stream_id]
        stream_data['start_time'] = time.time()

        # disable warm up so we don't have to worry about it later
        device.warm_up_stream(stream_id, False)

    while error_code == 0:
        if start_time is not None:
            if time.monotonic() >= start_time + duration:
                break
        device.poll_device(100)

    # disable the streams
    for stream_id in stream_ids:
        device.enable_stream(stream_id, False)

    device.stop_streaming_packets()

    # do a final poll after stopping streaming to clean up
    device.poll_device(0)

    # make sure no error code was set
    asphodel.clib.asphodel_error_check(error_code)

    return device_data


def filter_stream_data(device_data: DeviceData,
                       stream_id: int) -> ExtraStreamData:
    stream_data = cast(dict[str, Any],
                       device_data['streams'][stream_id].copy())
    stream_data.update({k: v for k, v in device_data.items()
                        if k != "streams" and not k.startswith("_")})
    return cast(ExtraStreamData, stream_data)


def filter_channel_data(device_data: DeviceData, stream_id: int,
                        channel_id: int) -> ExtraChannelData:
    stream_data = filter_stream_data(device_data, stream_id)
    channel_data = cast(dict[str, Any],
                        stream_data['channels'][channel_id].copy())
    channel_data.update({k: v for k, v in stream_data.items()
                         if k != 'channels' and not k.startswith("_")})
    return cast(ExtraChannelData, channel_data)


def unpack_streaming_data(
        data: list[tuple[float, int, NDArray[numpy.float64]]]) -> \
            tuple[NDArray[numpy.float64], NDArray[numpy.float64]]:
    last_index = None
    indexes: list[NDArray[numpy.float64]] = []
    chunks: list[NDArray[numpy.float64]] = []

    for _timestamp, index, chunk in data:
        if last_index is not None:
            next_index = last_index + 1
            if index != next_index:
                # create a short nan array to insert into the chunks
                nans = [numpy.nan] * chunk.shape[-1]
                nan_chunk = numpy.array(nans, ndmin=2)
                indexes.append(numpy.array(next_index, ndmin=1,
                                           dtype=numpy.float64))
                chunks.append(nan_chunk)
        last_index = index

        samples = chunk.shape[0]
        indexes.append(numpy.linspace(index, index + 1, num=samples,
                                      endpoint=False, dtype=numpy.float64))
        chunks.append(chunk)

    index_array: NDArray[numpy.float64]
    if indexes:
        index_array = numpy.concatenate(indexes)
    else:
        index_array = numpy.array([])

    data_array: NDArray[numpy.float64]
    if chunks:
        data_array = numpy.concatenate(chunks)
    else:
        data_array = numpy.array([])

    return (index_array, data_array)


def get_average_measurement(device_data: DeviceData, stream_id: int,
                            channel_id: int) -> NDArray[numpy.float64]:
    stream_data = device_data['streams'][stream_id]
    channel_data = stream_data['channels'][channel_id]
    unpacked_data = unpack_streaming_data(channel_data['data'])
    values = unpacked_data[1]
    result: NDArray[numpy.float64] = numpy.nanmean(values, axis=0)
    return result


class StreamingCache:
    caches: dict[asphodel.Device, DeviceData] = {}

    def __init__(self, cached_device: asphodel.Device,
                 stream: asphodel.StreamInfo | None = None,
                 stream_id: int | None = None,
                 channel: asphodel.ChannelInfo | None = None,
                 channel_id: int | None = None) -> None:
        # NOTE: the cached device shouldn't be used for any streaming
        self.cached_device = cached_device
        self.stream = stream
        self.stream_id = stream_id
        self.channel = channel
        self.channel_id = channel_id

    def __call__(self, device: asphodel.Device) -> \
            Union[DeviceData, ExtraStreamData, ExtraChannelData]:
        device_data = self.caches.get(self.cached_device, None)

        if device_data is None:
            # get new data
            device_data = stream_fixed_duration(device, self.cached_device)

            # clean up after; formerly part of stream_fixed_duration()
            device.flush()

            # save it to the cache
            self.caches[self.cached_device] = device_data

        # see if the stream data is still valid
        stale_objs = cast(
            set["StreamingCache"],
            device_data.setdefault('_stale_objs', set()))  # type: ignore

        if self in stale_objs:
            # get new data
            device_data = stream_fixed_duration(device, self.cached_device)

            # clean up after; formerly part of stream_fixed_duration()
            device.flush()

            stale_objs.clear()
            device_data['_stale_objs'] = stale_objs  # type: ignore

            # save it to the cache
            self.caches[self.cached_device] = device_data
        else:
            # mark the current object as stale; next call will give new data
            stale_objs.add(self)

        if self.stream_id is None:
            return device_data
        elif self.channel_id is None:
            return filter_stream_data(device_data, self.stream_id)
        else:
            return filter_channel_data(
                device_data, self.stream_id, self.channel_id)
