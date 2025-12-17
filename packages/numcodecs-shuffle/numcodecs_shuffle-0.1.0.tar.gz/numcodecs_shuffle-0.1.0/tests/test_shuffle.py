import numcodecs
import numcodecs.registry
import numpy as np


def test_from_config():
    codec = numcodecs.registry.get_codec(dict(id="shuffle.typed-byte"))
    assert codec.__class__.__name__ == "TypedByteShuffleCodec"
    assert codec.__class__.__module__ == "numcodecs_shuffle"


def check_roundtrip(data: np.ndarray):
    codec = numcodecs.registry.get_codec(dict(id="shuffle.typed-byte"))

    encoded = codec.encode(data)

    assert encoded.dtype == data.dtype
    assert encoded.shape == data.shape

    decoded = codec.decode(encoded)

    assert decoded.dtype == data.dtype
    assert decoded.shape == data.shape

    assert np.array_equal(decoded, data, equal_nan=True)
    assert np.all(np.signbit(decoded) == np.signbit(data))


def test_roundtrip():
    check_roundtrip(np.zeros(tuple()))
    check_roundtrip(np.zeros((0,)))
    check_roundtrip(np.arange(256).astype(np.int8).reshape(16, 16))
    check_roundtrip(np.arange(1000).reshape(10, 10, 10))
    check_roundtrip(np.array([np.inf, -np.inf, np.nan, -np.nan, 0.0, -0.0]))


def test_example():
    codec = numcodecs.registry.get_codec(dict(id="shuffle.typed-byte"))

    data = np.array(
        [0xAABBCCDD, 0xAABBCCDD, 0xAABBCCDD, 0xAABBCCDD],
        dtype=np.dtype(np.uint32).newbyteorder(">"),
    )

    encoded = codec.encode(data)

    assert encoded.dtype == data.dtype
    assert encoded.shape == data.shape
    assert np.all(encoded == np.array([0xAAAAAAAA, 0xBBBBBBBB, 0xCCCCCCCC, 0xDDDDDDDD]))

    decoded = codec.decode(encoded)

    assert decoded.dtype == data.dtype
    assert decoded.shape == data.shape
    assert np.all(decoded == data)
