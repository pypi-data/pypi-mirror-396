"""
[`TypedByteShuffleCodec`][.TypedByteShuffleCodec] for the [`numcodecs`][numcodecs] buffer compression API.
"""

__all__ = ["TypedByteShuffleCodec"]

from typing import TypeVar

import numcodecs.compat
import numcodecs.registry
import numpy as np
from numcodecs.abc import Codec

T = TypeVar("T", bound=np.number, covariant=True)
""" Any numpy [`number`][numpy.number] data type (covariant). """

S = TypeVar("S", bound=tuple[int, ...], covariant=True)
""" Any array shape (covariant). """


class TypedByteShuffleCodec(Codec):
    __slots__ = ()

    codec_id: str = "shuffle.typed-byte"  # type: ignore

    def encode(self, buf: np.ndarray[S, np.dtype[T]]) -> np.ndarray[S, np.dtype[T]]:
        """
        Shuffles the bytes in the `buf`fer array while keeping the same shape
        and data type. The shuffle size is based on the byte size of the data
        type. Shuffling can make typed data such as arrays of integers or
        floating point numbers easier to compress for a general-purpose
        byte-based compressor.

        For instance, the big-endian 32bit integer array
        `[0xaabbccdd, 0xaabbccdd, 0xaabbccdd, 0xaabbccdd]` is shuffled to
        `[0xaaaaaaaa, 0xbbbbbbbb, 0xcccccccc, 0xdddddddd]`.

        Parameters
        ----------
        buf : np.ndarray[S, np.dtype[T]]
            Array to be shuffled.

        Returns
        -------
        enc : np.ndarray[S, np.dtype[T]]
            Shuffled array with the same shape and dtype.
        """
        buf = numcodecs.compat.ensure_contiguous_ndarray(buf, flatten=False)
        return (
            numcodecs.Shuffle(elementsize=buf.dtype.itemsize)
            .encode(buf)
            .view(buf.dtype)
            .reshape(buf.shape)
        )

    def decode(
        self,
        buf: np.ndarray[S, np.dtype[T]],
        out: None | np.ndarray[S, np.dtype[T]] = None,
    ) -> np.ndarray[S, np.dtype[T]]:
        """
        Undoes the shuffling of the bytes in the `buf`fer array.

        Since the shuffle size is based on the byte size of the data, the
        `buf`fer and `out` arrays must have the same data type as the array
        that was originally shuffled in [`encode`][..encode].

        For instance, the big-endian 32bit integer array
        `[0xaaaaaaaa, 0xbbbbbbbb, 0xcccccccc, 0xdddddddd]` is un-shuffled back
        to `[0xaabbccdd, 0xaabbccdd, 0xaabbccdd, 0xaabbccdd]`.

        Parameters
        ----------
        buf : np.ndarray[S, np.dtype[T]]
            Array to be un-shuffled.
        out : None | np.ndarray[S, np.dtype[T]]
            Writeable array to store decoded data with the same shape and dtype.

        Returns
        -------
        dec : np.ndarray[S, np.dtype[T]]
            Un-shuffled array with the same shape and dtype.
        """

        buf = numcodecs.compat.ensure_contiguous_ndarray(buf, flatten=False)
        if out is not None:
            out = numcodecs.compat.ensure_contiguous_ndarray(out, flatten=False)
            assert out.dtype == buf.dtype
            out = out.view(buf.dtype).reshape(buf.shape)
        return (
            numcodecs.Shuffle(elementsize=buf.dtype.itemsize)
            .decode(buf, out=out)
            .view(buf.dtype)
            .reshape(buf.shape)
        )


numcodecs.registry.register_codec(TypedByteShuffleCodec)
