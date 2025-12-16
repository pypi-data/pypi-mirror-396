import collections.abc
import numpy
import numpy.typing
import torch
import typing

class VideoDecoder:
    """Video decoder with NvCodec acceleration."""
    def __init__(self, gpu_id: typing.SupportsInt, codec: str) -> None:
        """__init__(self: _decoder.VideoDecoder, gpu_id: typing.SupportsInt, codec: str) -> None

        Create a video decoder instance.

        Args:
            gpuid (int): GPU device ID to use for decoding.
            codec (int): Codec of the video stream to be decoded which contains h265, hevc, h264, av1, v9.
        """
    def codec(self) -> str:
        """codec(self: _decoder.VideoDecoder) -> str

        Video codec format being decoded
        """
    def decode_to_np(self, video_path: str, frame_index: typing.SupportsInt) -> numpy.typing.NDArray[numpy.uint8]:
        """decode_to_np(self: _decoder.VideoDecoder, video_path: str, frame_index: typing.SupportsInt) -> numpy.typing.NDArray[numpy.uint8]

        Decode a single frame from a video file.

        This function decodes a single frame from a video file using the provided demuxer and decoder objects.

        Args:
            video_path (str): The path to the video file to be decoded.
            frame_index (int): The index of the frame to be decoded.

        Returns:
            A numpy object representing the decoded frame.

        Raises:
            RuntimeError: if there are issues such as file opening failure, decoding failure, or target frame not found.
        """
    def decode_to_nps(self, video_path: str, frame_indices: collections.abc.Sequence[typing.SupportsInt]) -> list[numpy.typing.NDArray[numpy.uint8]]:
        """decode_to_nps(self: _decoder.VideoDecoder, video_path: str, frame_indices: collections.abc.Sequence[typing.SupportsInt]) -> list[numpy.typing.NDArray[numpy.uint8]]

        Decode multiple frames from a video file.

        This function decodes multiple frames from a video file using the provided demuxer and decoder objects.

        Args:
            video_path (str): The path to the video file to be decoded.
            frame_indices (list): The indices of the frames to be decoded.

        Returns:
            A list of numpy arrays representing the decoded frames.

        Raises:
            RuntimeError: if there are issues such as file opening failure, decoding failure, or target frame not found.
        """
    def decode_to_tensor(self, video_path: str, frame_index: typing.SupportsInt) -> torch.Tensor:
        """decode_to_tensor(self: _decoder.VideoDecoder, video_path: str, frame_index: typing.SupportsInt) -> torch.Tensor

        Decode a single frame from a video file.

        This function decodes a single frame from a video file using the provided demuxer and decoder objects.

        Args:
            video_path (str): The path to the video file to be decoded.
            frame_index (int): The index of the frame to be decoded.

        Returns:
            A torch object representing the decoded frame.

        Raises:
            RuntimeError: if there are issues such as file opening failure, decoding failure, or target frame not found.
        """
    def gpu_id(self) -> int:
        """gpu_id(self: _decoder.VideoDecoder) -> int

        ID of the GPU being used for decoding
        """
