from abc import ABC, abstractmethod
from fractions import Fraction
import av
import numpy as np
import cv2


class CompressionStrategy(ABC):
    def __init__(self, first_frame):
        pass

    @abstractmethod
    def encode(self, frame):
        pass

    @abstractmethod
    def decode(self, payload):
        pass


class NoneStrategy(CompressionStrategy):
    def encode(self, frame):
        return frame

    def decode(self, payload):
        return payload


class H264LosslessCompression(CompressionStrategy):
    def __init__(self, first_frame):
        super().__init__(first_frame)
        self.fps = 20

    def _to_rgb3_and_flag(self, arr: np.ndarray):
        if arr.dtype != np.uint8:
            raise ValueError("Input must be uint8.")
        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = arr[:, :, 0]
        if arr.ndim == 2:
            rgb = np.repeat(arr[:, :, None], 3, axis=2)
            return rgb, True
        if arr.ndim == 3 and arr.shape[2] == 3:
            return arr, False
        raise ValueError("Array must be HxW, HxWx1, or HxWx3 (uint8).")

    def encode(self, arr: np.ndarray) -> bytes:
        rgb, is_mask = self._to_rgb3_and_flag(arr)
        h, w, _ = rgb.shape
        enc = av.CodecContext.create("libx264rgb", "w")
        enc.width = w
        enc.height = h
        enc.time_base = Fraction(1, self.fps)
        enc.pix_fmt = "rgb24"
        enc.options = {
            "crf": "0",
            "preset": "ultrafast",
            "g": "1",
            "keyint": "1",
        }
        enc.open()
        frame = av.VideoFrame.from_ndarray(rgb, format="rgb24")
        packets = []
        packets.extend(enc.encode(frame))
        packets.extend(enc.encode(None))
        if not packets:
            raise RuntimeError("H.264 encoder produced no packets.")
        bitstream = b"".join(bytes(p) for p in packets)
        header = b"\x01" if is_mask else b"\x00"
        return header + bitstream

    def decode(self, data: bytes) -> np.ndarray:
        if len(data) < 2:
            raise ValueError("Payload too short.")
        header = data[0]
        bitstream = data[1:]
        is_mask = (header == 0x01)
        dec = av.CodecContext.create("h264", "r")
        packet = av.packet.Packet(bitstream)
        frames = []
        frames.extend(dec.decode(packet))
        frames.extend(dec.decode(None))
        if not frames:
            raise RuntimeError("H.264 decoder produced no frames.")
        img3 = frames[0].to_ndarray(format="rgb24")
        if is_mask:
            return img3[..., :1]
        return img3


class PNGCompression(CompressionStrategy):
    def __init__(self, first_frame, compression_level=1):
        self.compression_level = compression_level

    def encode(self, arr):
        if arr.dtype != np.uint8:
            raise ValueError("Input must be uint8.")
        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = arr[:, :, 0]
        if arr.ndim == 2:
            img_to_encode = arr
        elif arr.ndim == 3 and arr.shape[2] == 3:
            img_to_encode = arr
        else:
            raise ValueError("Array must be HxW, HxWx1, or HxWx3 (uint8).")
        ok, buf = cv2.imencode(
            ".png",
            img_to_encode,
            [cv2.IMWRITE_PNG_COMPRESSION, int(self.compression_level)],
        )
        if not ok:
            raise RuntimeError("PNG encode failed.")
        return buf.tobytes()

    def decode(self, data):
        buf = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise RuntimeError("PNG decode failed.")
        if img.ndim == 2:
            return img[..., np.newaxis]
        if img.ndim == 3 and img.shape[2] == 3:
            return img
        raise ValueError(f"Unexpected PNG shape: {img.shape}")


class JPEGCompression(CompressionStrategy):
    def __init__(self, first_frame, quality=95):
        self.quality = quality

    def encode(self, arr):
        if arr.dtype != np.uint8:
            raise ValueError("Input must be uint8.")
        if arr.ndim == 3 and arr.shape[2] == 1:
            arr = arr[:, :, 0]
        if arr.ndim == 2:
            img_to_encode = arr
        elif arr.ndim == 3 and arr.shape[2] == 3:
            img_to_encode = arr
        else:
            raise ValueError("Array must be HxW, HxWx1, or HxWx3 (uint8).")
        ok, buf = cv2.imencode(
            ".jpg",
            img_to_encode,
            [cv2.IMWRITE_JPEG_QUALITY, int(self.quality)],
        )
        if not ok:
            raise RuntimeError("JPEG encode failed.")
        return buf.tobytes()

    def decode(self, data):
        buf = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise RuntimeError("JPEG decode failed.")
        if img.ndim == 2:
            return img[..., np.newaxis]
        if img.ndim == 3 and img.shape[2] == 3:
            return img
        raise ValueError(f"Unexpected JPEG shape: {img.shape}")


STRATEGIES = {
    "none": NoneStrategy,
    "h264": H264LosslessCompression,
    "png": PNGCompression,
    "jpeg": JPEGCompression,
}
