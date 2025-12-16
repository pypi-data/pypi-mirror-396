from typing import Optional, Sequence
import numpy as np

from .pickle_client import PickleClient


class PoseEstimation:
    """
    Client for FoundationPose pickle RPC server.
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        import os

        host = host or os.environ.get("FPOSE_HOST", "localhost")
        port = port or int(os.environ.get("FPOSE_PORT", "5557"))
        self.client = PickleClient(host, port)

    def init(
        self,
        mesh_path: str,
        apply_scale: float = 1.0,
        force_apply_color: bool = False,
        apply_color: Sequence[float] = (160, 160, 160),
        est_refine_iter: int = 10,
        track_refine_iter: int = 3,
        min_n_views: int = 40,
        inplane_step: int = 60,
    ):
        return self.client.send_data(
            {
                "operation": "init",
                "mesh_path": mesh_path,
                "apply_scale": apply_scale,
                "force_apply_color": force_apply_color,
                "apply_color": list(apply_color),
                "est_refine_iter": est_refine_iter,
                "track_refine_iter": track_refine_iter,
                "min_n_views": min_n_views,
                "inplane_step": inplane_step,
            }
        )

    def register(
        self,
        rgb: np.ndarray,
        depth: np.ndarray,
        mask: np.ndarray,
        K: np.ndarray,
        iteration: int = None,
        check_vram: bool = True,
    ):
        payload = {
            "operation": "register",
            "rgb": rgb,
            "depth": depth,
            "mask": mask,
            "K": K,
            "check_vram": bool(check_vram),
        }
        if iteration is not None:
            payload["iteration"] = iteration
        return self.client.send_data(payload)

    def track(self, rgb: np.ndarray, depth: np.ndarray, K: np.ndarray, iteration: int = None, bbox_xywh=None):
        payload = {
            "operation": "track",
            "rgb": rgb,
            "depth": depth,
            "K": K,
            "bbox_xywh": bbox_xywh,
        }
        if iteration is not None:
            payload["iteration"] = iteration
        return self.client.send_data(payload)

    def reset(self):
        return self.client.send_data({"operation": "reset"})

    def reset_object(self):
        """Re-run server-side reset_object/make_rotation_grid with cached mesh from init."""
        return self.client.send_data({"operation": "reset_object"})

    def close(self):
        self.client.close()


# Backward-compat alias
FoundationPoseClient = PoseEstimation
