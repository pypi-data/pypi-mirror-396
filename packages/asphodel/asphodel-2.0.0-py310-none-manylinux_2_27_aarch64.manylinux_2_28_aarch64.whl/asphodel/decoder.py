from collections.abc import Callable
from ctypes import (POINTER, c_double, c_int, c_uint, c_uint8, c_void_p, cast,
                    pointer)
from ctypes import _Pointer  # pyright: ignore
from typing import Any

from .clib import (AsphodelChannelDecoder, AsphodelDecodeCallback,
                   AsphodelDeviceDecoder, AsphodelLostPacketCallback,
                   AsphodelStreamDecoder, AsphodelUnknownIDCallback,
                   ChannelInfo, StreamAndChannels, StreamInfo, lib)

InfoListEntry = tuple[int, StreamInfo, list[ChannelInfo]]


class ChannelDecoder:
    def __init__(self, decoder: AsphodelChannelDecoder,
                 channel_info: ChannelInfo,
                 stream_decoder: "StreamDecoder | None" = None) -> None:
        self._decoder = decoder
        self.channel_info = channel_info
        self.stream_decoder = stream_decoder  # keep a reference
        self.auto_free = False if stream_decoder else True

        # copy settings out of the decoder
        self.channel_bit_offset = self._decoder.channel_bit_offset
        self.samples = self._decoder.samples
        try:
            self.channel_name = self._decoder.channel_name.decode("utf-8")
        except UnicodeDecodeError:
            self.channel_name = "<ERROR>"
        self.subchannels = self._decoder.subchannels
        self.subchannel_names: list[str] = []
        for i in range(self.subchannels):
            try:
                name_bytes: bytes = self._decoder.subchannel_names[i]
                self.subchannel_names.append(name_bytes.decode("utf-8"))
            except UnicodeDecodeError:
                self.subchannel_names.append("<ERROR>")

    def __del__(self) -> None:
        if self.auto_free:
            self._decoder.free_decoder(self._decoder)

    def __reduce__(self) -> tuple[Any, ...]:
        if self._decoder.callback:
            raise Exception("Cannot reduce channel decoder with callback")
        args = (self.channel_info, self._decoder.channel_bit_offset)
        return (ChannelDecoder.create, args)

    def reset(self) -> None:
        self._decoder.reset(self._decoder)

    def decode(self, counter: int, buffer: bytes) -> None:
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, counter, b)

    def set_conversion_factor(self, scale: float, offset: float) -> None:
        self._decoder.set_conversion_factor(
            self._decoder, scale, offset)

    def set_callback(
            self, cb: Callable[[int, list[float], int, int], None]) -> None:
        # void (*)(uint64_t counter, double *data, size_t samples,
        #          size_t subchannels, void * closure)
        def callback(counter: int, data: "_Pointer[c_double]", samples: int,
                     subchannels: int, closure: c_void_p) -> None:
            data_size = samples * subchannels
            d: list[float] = data[0:data_size]
            try:
                cb(counter, d, samples, subchannels)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = AsphodelDecodeCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.callback = c_cb

    @classmethod
    def create(cls, channel_info: ChannelInfo,
               bit_offset: int,
               stream_packet_length: int | None = None) -> "ChannelDecoder":
        if stream_packet_length is None:
            stream_packet_length = 0
        decoder_ptr = POINTER(AsphodelChannelDecoder)()
        lib.asphodel_create_channel_decoder_checked(
            channel_info, bit_offset, stream_packet_length, decoder_ptr)
        return ChannelDecoder(decoder_ptr.contents, channel_info)


class StreamDecoder:
    def __init__(self, decoder: AsphodelStreamDecoder,
                 stream_info: StreamInfo,
                 channel_info_list: list[ChannelInfo],
                 bit_offset: int,
                 device_decoder: "DeviceDecoder | None" = None) -> None:
        self._decoder = decoder
        self.stream_info = stream_info
        self._channel_info_list = channel_info_list.copy()
        self.bit_offset = bit_offset
        self.device_decoder = device_decoder  # keep a reference
        self.auto_free = False if device_decoder else True

        # copy some values out
        self.counter_byte_offset = self._decoder.counter_byte_offset
        self.used_bits = self._decoder.used_bits
        self.channels = self._decoder.channels
        self.decoders: list[ChannelDecoder] = []
        for i in range(self.channels):
            d = ChannelDecoder(self._decoder.decoders[i].contents,
                               channel_info_list[i], self)
            self.decoders.append(d)

    def __del__(self) -> None:
        if self.auto_free:
            self._decoder.free_decoder(self._decoder)

    def __reduce__(self) -> tuple[Any, ...]:
        if self._decoder.lost_packet_callback:
            raise Exception("Cannot reduce stream decoder with callback")
        for d in self.decoders:
            if d._decoder.callback:  # pyright: ignore
                raise Exception("Cannot reduce channel decoder with callback")
        args = (self.stream_info, self._channel_info_list, self.bit_offset)
        return (StreamDecoder.create, args)

    def reset(self) -> None:
        self._decoder.reset(self._decoder)

    @property
    def last_count(self) -> int:
        return self._decoder.last_count

    def decode(self, buffer: bytes) -> None:
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, cast(b, POINTER(c_uint8)))

    def set_lost_packet_callback(self, cb: Callable[[int, int], None]) -> None:
        def callback(current: int, last: int, closure: c_void_p) -> None:
            try:
                cb(current, last)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = AsphodelLostPacketCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.lost_packet_callback = c_cb

    @classmethod
    def create(cls, stream_info: StreamInfo,
               channel_info_list: list[ChannelInfo],
               bit_offset: int,
               stream_packet_length: int | None = None) -> "StreamDecoder":
        if stream_packet_length is None:
            stream_packet_length = 0
        decoder_ptr = POINTER(AsphodelStreamDecoder)()
        array_type = POINTER(ChannelInfo) * len(channel_info_list)
        channel_array = array_type(*(pointer(c) for c in channel_info_list))
        stream_and_channels = StreamAndChannels()
        stream_and_channels.stream_info = pointer(stream_info)
        stream_and_channels.channel_info = cast(
            channel_array, POINTER(POINTER(ChannelInfo)))
        lib.asphodel_create_stream_decoder_checked(
            stream_and_channels, bit_offset, stream_packet_length, decoder_ptr)
        return StreamDecoder(
            decoder_ptr.contents, stream_info, channel_info_list, bit_offset)


class DeviceDecoder:
    def __init__(self, decoder: AsphodelDeviceDecoder,
                 info_list: list[InfoListEntry], filler_bits: int,
                 id_bits: int) -> None:
        self._decoder = decoder
        self._info_list = info_list.copy()
        self._filler_bits = filler_bits
        self._id_bits = id_bits
        bit_offset = self._filler_bits + self._id_bits

        # copy some values out
        self.id_byte_offset = self._decoder.id_byte_offset
        self.used_bits = self._decoder.used_bits
        self.streams = self._decoder.streams
        self.stream_ids = self._decoder.stream_ids[0:self.streams]

        self.decoders: list[StreamDecoder] = []
        for i in range(self.streams):
            d = StreamDecoder(
                self._decoder.decoders[i].contents, info_list[i][1],
                info_list[i][2], bit_offset, self)
            self.decoders.append(d)

    def __del__(self) -> None:
        self._decoder.free_decoder(self._decoder)

    def __reduce__(self) -> tuple[Any, ...]:
        if self._decoder.unknown_id_callback:
            raise Exception("Cannot reduce device decoder with callback")
        for d in self.decoders:
            if d._decoder.lost_packet_callback:  # pyright: ignore
                raise Exception("Cannot reduce stream decoder with callback")
            for cd in d.decoders:
                if cd._decoder.callback:  # pyright: ignore
                    raise Exception(
                        "Cannot reduce channel decoder with callback")
        args = (self._info_list, self._filler_bits, self._id_bits)
        return (DeviceDecoder.create, args)

    def reset(self) -> None:
        self._decoder.reset(self._decoder)

    def decode(self, buffer: bytes) -> None:
        b = (c_uint8 * len(buffer)).from_buffer_copy(buffer)
        self._decoder.decode(self._decoder, cast(b, POINTER(c_uint8)))

    def set_unknown_id_callback(self, cb: Callable[[int], None]) -> None:
        def callback(lost_id: int, closure: c_void_p) -> None:
            try:
                cb(lost_id)
            except Exception:
                pass  # nothing can be done about it here
        c_cb = AsphodelUnknownIDCallback(callback)
        self._callback = c_cb  # save a reference
        self._decoder.unknown_id_callback = c_cb

    @classmethod
    def create(cls, info_list: list[InfoListEntry], filler_bits: int,
               id_bits: int,
               stream_packet_length: int | None = None) -> "DeviceDecoder":
        """
        info_list is a sequence of tuples of (stream_id, stream_info,
        channel_info_list).
        """
        if stream_packet_length is None:
            stream_packet_length = 0
        decoder_ptr = POINTER(AsphodelDeviceDecoder)()
        array_size = len(info_list)
        info_array = (StreamAndChannels * array_size)()
        for i, (stream_id, stream_info, ch_info_list) in enumerate(info_list):
            info_array[i].stream_id = stream_id
            info_array[i].stream_info = pointer(stream_info)
            array_type = POINTER(ChannelInfo) * len(ch_info_list)
            ch_array = array_type(*(pointer(c) for c in ch_info_list))
            info_array[i].channel_info = cast(
                ch_array, POINTER(POINTER(ChannelInfo)))
        lib.asphodel_create_device_decoder_checked(
            info_array, array_size, filler_bits, id_bits, stream_packet_length,
            decoder_ptr)
        return DeviceDecoder(
            decoder_ptr.contents, info_list, filler_bits, id_bits)


def get_streaming_counts(streams: list[StreamInfo],
                         response_time: float, buffer_time: float,
                         timeout: int) -> tuple[int, int, int]:
    """
    returns (packet_count, transfer_count, timeout)
    """
    packet_count = c_int()
    transfer_count = c_int()
    timeout_io = c_uint(timeout)
    array_size = len(streams)
    info_array = (StreamAndChannels * array_size)()
    for i, stream_info in enumerate(streams):
        info_array[i].stream_info = pointer(stream_info)
    lib.asphodel_get_streaming_counts(
        info_array, array_size, response_time, buffer_time, packet_count,
        transfer_count, timeout_io)
    return (packet_count.value, transfer_count.value, timeout_io.value)
