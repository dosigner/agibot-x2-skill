"""Offline fixture: bytes supplied by a reviewed RGB-D callback."""


def describe_frame(rgb: bytes, depth: bytes, timestamp_ns: int) -> dict:
    return {
        "timestamp_ns": timestamp_ns,
        "rgb_bytes": len(rgb),
        "depth_bytes": len(depth),
    }
