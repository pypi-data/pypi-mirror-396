import lzma
import struct
from typing import Any, Iterable

import asphodel


def load_batch(
        files: Iterable[str]) -> tuple[dict[float, str], bytes]:
    """
    returns (file_times, header) where file_times is a dictonary of
    timestamp:filename
    * header is JSON data for creating a DeviceInfo object.
    * filename is the absolute path to the file location.
    * timestamp is the floating point time of the first packet in the file.
    """

    first_file_bytes_and_timestamp: tuple[bytes, float] | None = None
    header_out: bytes = b""

    file_times: dict[float, str] = {}

    for filename in files:
        with lzma.LZMAFile(filename, "rb") as f:
            # read the header
            header_leader = struct.unpack(">dI", f.read(12))
            header_timestamp: float = header_leader[0]
            header_bytes = f.read(header_leader[1])

            if len(header_bytes) == 0:
                raise Exception("Empty header in {}!".format(filename))

            # read the first packet's datetime
            first_packet_timestamp: float = struct.unpack(">d", f.read(8))[0]

            if first_file_bytes_and_timestamp is None:
                first_file_bytes_and_timestamp = (
                    header_bytes, header_timestamp)

                header_out = header_bytes
            else:
                if (first_file_bytes_and_timestamp !=
                        (header_bytes, header_timestamp)):
                    # error
                    raise Exception(
                        "Headers do not match on {}!".format(filename))

            if first_packet_timestamp in file_times:
                f2 = file_times[first_packet_timestamp]
                m = f"Timestamps overlap between files {filename} and {f2}"
                raise Exception(m)

            file_times[first_packet_timestamp] = filename

    if not header_out:
        raise Exception("No file parsed")

    return (file_times, header_out)


def load_batches(
        files: Iterable[str]) -> list[tuple[dict[float, str], bytes]]:
    """
    returns [(file_times, header)] where file_times is a dictonary of
    timestamp:filename
    * header is JSON data for creating a DeviceInfo object.
    * filename is the absolute path to the file location.
    * timestamp is the floating point time of the first packet in the file
    """

    batches: dict[tuple[float, bytes], dict[float, str]] = {}

    for filename in files:
        with lzma.LZMAFile(filename, "rb") as f:
            # read the header
            header_leader = struct.unpack(">dI", f.read(12))
            header_timestamp: float = header_leader[0]
            header_bytes = f.read(header_leader[1])

            if len(header_bytes) == 0:
                raise Exception("Empty header in {}!".format(filename))

            # read the first packet's datetime
            first_packet_timestamp: float = struct.unpack(">d", f.read(8))[0]

            header_key = (header_timestamp, header_bytes)
            if header_key not in batches:
                # first file in this batch
                file_times = {first_packet_timestamp: filename}
                batches[header_key] = file_times
            else:
                file_times = batches[header_key]
                if first_packet_timestamp in file_times:
                    f2 = file_times[first_packet_timestamp]
                    m = f"Timestamps overlap between files {filename} and {f2}"
                    raise Exception(m)
                file_times[first_packet_timestamp] = filename

    results: list[tuple[dict[float, str], bytes]] = []
    for (_timestamp, header_bytes), file_times in sorted(batches.items()):
        results.append((file_times, header_bytes))

    return results


def parse_packets(filename: str) -> Iterable[tuple[bytes, float]]:
    """
    yields (packet_bytes, timestamp) for each group of packet_bytes in
    the file
    * packet_bytes is a group of packets collected at the same time, always a
      multiple of the device's stream packet size
    * timestamp is the floating point time for when the bytes were collected
    """

    packet_leader = struct.Struct(">dI")

    with lzma.LZMAFile(filename, "rb") as f:
        # read the header
        header_leader = struct.unpack(">dI", f.read(12))
        f.read(header_leader[1])

        while True:
            leader_bytes = f.read(packet_leader.size)

            if not leader_bytes:
                return  # file is finished

            leader = packet_leader.unpack(leader_bytes)
            packet_timestamp: float = leader[0]
            packet_bytes = f.read(leader[1])

            yield (packet_bytes, packet_timestamp)


def create_decoder(
        header: dict[str, Any]) -> asphodel.DeviceDecoder:
    info_list: list[tuple[int, asphodel.StreamInfo,
                          list[asphodel.ChannelInfo]]] = []
    for stream_id in header['streams_to_activate']:
        stream: asphodel.StreamInfo = header['streams'][stream_id]
        indexes = stream.channel_index_list

        if len(indexes) > 0:
            channel_list = [header['channels'][ch_id] for ch_id in indexes]
            info_list.append((stream_id, stream, channel_list))

    # create the device decoder
    decoder = asphodel.DeviceDecoder.create(
        info_list, header['stream_filler_bits'], header['stream_id_bits'])

    return decoder
