"""
Real-time demo using neuromeka_vfm Segmentation + PoseEstimation clients.
- Streams RGB/Depth from an attached RealSense
- Uses segmentation masks to register/track in FoundationPose
- Renders 3D bounding box + axes overlay in a window

Requirements:
- A running segmentation server (SAM2/GroundingDINO) reachable by ZeroMQ
- A running FoundationPose RPC server
- A connected RealSense camera (pyrealsense2 installed)
"""

import os
import time
from typing import Optional, Tuple

import cv2
import numpy as np
import pyrealsense2 as rs

from neuromeka_vfm import PoseEstimation, Segmentation


def to_homogeneous(pts: np.ndarray) -> np.ndarray:
    """Append 1.0 to points for homogeneous projection."""
    assert pts.ndim == 2, f"Expected (N,2|3), got {pts.shape}"
    return np.concatenate((pts, np.ones((pts.shape[0], 1))), axis=-1)


def draw_posed_3d_box(
    K: np.ndarray,
    img: np.ndarray,
    ob_in_cam: np.ndarray,
    bbox: np.ndarray,
    line_color=(0, 255, 0),
    linewidth=2,
) -> np.ndarray:
    """Project a 3D bbox onto the image."""

    def project_line(start, end, canvas):
        pts = np.stack((start, end), axis=0).reshape(-1, 3)
        pts = (ob_in_cam @ to_homogeneous(pts).T).T[:, :3]
        projected = (K @ pts.T).T
        uv = np.round(projected[:, :2] / projected[:, 2].reshape(-1, 1)).astype(int)
        return cv2.line(
            canvas,
            uv[0].tolist(),
            uv[1].tolist(),
            color=line_color,
            thickness=linewidth,
            lineType=cv2.LINE_AA,
        )

    min_xyz = bbox.min(axis=0)
    max_xyz = bbox.max(axis=0)
    xmin, ymin, zmin = min_xyz
    xmax, ymax, zmax = max_xyz

    for y in [ymin, ymax]:
        for z in [zmin, zmax]:
            start = np.array([xmin, y, z])
            end = start + np.array([xmax - xmin, 0, 0])
            img = project_line(start, end, img)

    for x in [xmin, xmax]:
        for z in [zmin, zmax]:
            start = np.array([x, ymin, z])
            end = start + np.array([0, ymax - ymin, 0])
            img = project_line(start, end, img)

    for x in [xmin, xmax]:
        for y in [ymin, ymax]:
            start = np.array([x, y, zmin])
            end = start + np.array([0, 0, zmax - zmin])
            img = project_line(start, end, img)
    return img


def project_point(pt: np.ndarray, K: np.ndarray, ob_in_cam: np.ndarray) -> np.ndarray:
    pt = pt.reshape(4, 1)
    projected = K @ ((ob_in_cam @ pt)[:3, :])
    projected = projected.reshape(-1)
    projected = projected / projected[2]
    return projected[:2].round().astype(int)


def draw_axes(
    img: np.ndarray,
    ob_in_cam: np.ndarray,
    scale: float,
    K: np.ndarray,
    thickness: int = 3,
    transparency: float = 0.0,
    is_input_rgb: bool = False,
) -> np.ndarray:
    """Overlay XYZ axes."""
    if is_input_rgb:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    origin = tuple(project_point(np.array([0, 0, 0, 1]), K, ob_in_cam))
    xx = tuple(project_point(np.array([scale, 0, 0, 1]), K, ob_in_cam))
    yy = tuple(project_point(np.array([0, scale, 0, 1]), K, ob_in_cam))
    zz = tuple(project_point(np.array([0, 0, scale, 1]), K, ob_in_cam))

    base = img.copy()
    next_img = cv2.arrowedLine(base.copy(), origin, xx, color=(0, 0, 255), thickness=thickness, line_type=cv2.LINE_AA)
    mask = np.linalg.norm(next_img - base, axis=-1) > 0
    base[mask] = base[mask] * transparency + next_img[mask] * (1 - transparency)

    next_img = cv2.arrowedLine(base.copy(), origin, yy, color=(0, 255, 0), thickness=thickness, line_type=cv2.LINE_AA)
    mask = np.linalg.norm(next_img - base, axis=-1) > 0
    base[mask] = base[mask] * transparency + next_img[mask] * (1 - transparency)

    next_img = cv2.arrowedLine(base.copy(), origin, zz, color=(255, 0, 0), thickness=thickness, line_type=cv2.LINE_AA)
    mask = np.linalg.norm(next_img - base, axis=-1) > 0
    base[mask] = base[mask] * transparency + next_img[mask] * (1 - transparency)

    if is_input_rgb:
        base = cv2.cvtColor(base.astype(np.uint8), cv2.COLOR_BGR2RGB)
    return base.astype(np.uint8)


def setup_realsense(
    rgb_shape: Tuple[int, int] = (960, 540),
    depth_shape: Tuple[int, int] = (640, 480),
    fps: int = 30,
) -> Tuple[rs.pipeline, rs.align, float, np.ndarray]:
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, rgb_shape[0], rgb_shape[1], rs.format.bgr8, fps)
    config.enable_stream(rs.stream.depth, depth_shape[0], depth_shape[1], rs.format.z16, fps)

    profile = pipeline.start(config)
    align_to_color = rs.align(rs.stream.color)

    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
    intr = color_stream.get_intrinsics()
    cam_K = np.array(
        [[intr.fx, 0.0, intr.ppx], [0.0, intr.fy, intr.ppy], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    print("Intrinsics W,H:", intr.width, intr.height)
    print("cam_K:\n", cam_K)
    print("Depth scale:", depth_scale)
    if depth_sensor.supports(rs.option.min_distance):
        print("min_distance:", depth_sensor.get_option(rs.option.min_distance))
    if depth_sensor.supports(rs.option.max_distance):
        print("max_distance:", depth_sensor.get_option(rs.option.max_distance))

    return pipeline, align_to_color, depth_scale, cam_K


def to_binary_mask(mask_obj: Optional[object]) -> Optional[np.ndarray]:
    """Normalize mask outputs (dict/array) to a single uint8 binary mask."""
    if mask_obj is None:
        return None
    if isinstance(mask_obj, dict):
        if not mask_obj:
            return None
        mask_arrays = [np.asarray(m) for m in mask_obj.values() if m is not None]
        if not mask_arrays:
            return None
        mask_arrays = [np.squeeze(m) for m in mask_arrays]
        mask = np.zeros_like(mask_arrays[0], dtype=np.uint8)
        for m in mask_arrays:
            mask |= (np.asarray(m) > 0).astype(np.uint8)
        if mask.ndim > 2:
            mask = np.squeeze(mask)
        return mask.astype(np.uint8)

    mask_arr = np.asarray(mask_obj)
    if mask_arr.ndim > 2:
        mask_arr = np.squeeze(mask_arr)
    if mask_arr.ndim > 2:
        mask_arr = mask_arr[..., 0]
    return (mask_arr > 0).astype(np.uint8)


def bbox_to_mask(bbox_xywh, shape_hw) -> Optional[np.ndarray]:
    """Convert xywh bbox to a binary mask."""
    if bbox_xywh is None:
        return None
    x, y, w, h = bbox_xywh
    h_img, w_img = shape_hw
    if w <= 0 or h <= 0:
        return None
    mask = np.zeros((h_img, w_img), dtype=np.uint8)
    x0, y0 = int(x), int(y)
    x1, y1 = min(w_img, x0 + int(w)), min(h_img, y0 + int(h))
    mask[y0:y1, x0:x1] = 1
    return mask


def overlay_mask(img_rgb: np.ndarray, mask: Optional[np.ndarray]) -> np.ndarray:
    if mask is None:
        return img_rgb
    mask_bool = mask.astype(bool)
    if not np.any(mask_bool):
        return img_rgb
    overlay = img_rgb.copy()
    overlay_color = np.array([0, 255, 0], dtype=overlay.dtype)
    overlay[mask_bool] = (
        0.6 * overlay[mask_bool].astype(np.float32) + 0.4 * overlay_color.astype(np.float32)
    ).astype(overlay.dtype)
    return overlay


def bbox_from_mask(mask_np: np.ndarray):
    erosion_size = 5
    kernel = np.ones((erosion_size, erosion_size), np.uint8)
    mask_np = cv2.erode(mask_np.astype(np.uint8), kernel, iterations=1)

    rows = np.any(mask_np, axis=1)
    cols = np.any(mask_np, axis=0)
    if np.any(rows) and np.any(cols):
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
    else:
        bbox = [-1, -1, 0, 0]
    return bbox


def main():
    mesh_path = os.environ.get("FPOSE_MESH_PATH", "/app/modules/foundation_pose/mesh/drug_box.stl")
    fpose_host = os.environ.get("FPOSE_HOST", "192.168.10.69")
    fpose_port = int(os.environ.get("FPOSE_PORT", "5557"))
    seg_host = os.environ.get("SEG_HOST", "192.168.10.69")
    seg_port = int(os.environ.get("SEG_PORT", "5432"))
    seg_prompt = os.environ.get("SEG_PROMPT", "piece")
    seg_ref_image = os.environ.get("SEG_REF_IMAGE", "piece.jpg")
    seg_compression = os.environ.get("SEG_COMPRESSION", "none")

    pipeline, align_to_color, depth_scale, cam_K = setup_realsense()

    print("Init detector. path", seg_ref_image)
    detector = Segmentation(seg_host, seg_port, compression_strategy=seg_compression)
    use_image_prompt = False
    if os.path.exists(seg_ref_image):
        ref_img = cv2.imread(seg_ref_image)
        if ref_img is not None:
            ref_rgb = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
            detector.add_image_prompt(seg_prompt, ref_rgb)
            use_image_prompt = True
            print(f"Loaded image prompt '{seg_ref_image}' for '{seg_prompt}'")
        else:
            print(f"Failed to load reference image at {seg_ref_image}, falling back to text prompt.")
    else:
        print(f"Reference image {seg_ref_image} not found; using text prompt only.")

    print("Init FP")
    pose = PoseEstimation(host=fpose_host, port=fpose_port)
    init_resp = pose.init(
        mesh_path=mesh_path,
        apply_scale=float(os.environ.get("FPOSE_APPLY_SCALE", "1.0")),
        force_apply_color=os.environ.get("FPOSE_FORCE_APPLY_COLOR", "false").lower() == "true",
        apply_color=tuple(map(float, os.environ.get("FPOSE_APPLY_COLOR", "160,160,160").split(","))),
        est_refine_iter=int(7),
        track_refine_iter=int(3),
        min_n_views=int(5),
        inplane_step=int(150),
    )
    if init_resp.get("result") != "SUCCESS":
        print("Init failed:", init_resp)
        return
    to_origin = np.asarray(init_resp["data"]["to_origin"])
    bbox = np.asarray(init_resp["data"]["bbox"])

    initialized = False
    current_pose = None
    current_mask = None

    cv2.namedWindow("neuromeka_vfm Pose Demo", cv2.WINDOW_NORMAL)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            frames = align_to_color.process(frames)
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            color_bgr = np.asanyarray(color_frame.get_data())
            depth = np.asanyarray(depth_frame.get_data()).astype(np.float32)
            depth *= depth_scale
            depth[(depth < 0.001) | np.isinf(depth)] = 0
            color = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB)

            if not initialized:
                tic = time.time()
                if detector.register_first_frame(color, seg_prompt, use_image_prompt=use_image_prompt):
                    detector.get_next(color)
                    init_mask_raw = detector.current_frame_masks
                else:
                    init_mask_raw = None
                    print("First segmentation failed.")
                    cv2.imshow("neuromeka_vfm Pose Demo", color_bgr)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
                    continue

                init_mask = to_binary_mask(init_mask_raw)
                if init_mask is None:
                    print("No mask returned on first frame.")
                    continue
                mask_uint8 = init_mask.astype(np.uint8) * 255

                resp = pose.register(rgb=color, depth=depth, mask=mask_uint8, K=cam_K, iteration=7)
                if resp.get("result") != "SUCCESS":
                    print("Register failed:", resp)
                    continue
                current_pose = np.asarray(resp["data"]["pose"])
                current_mask = init_mask
                initialized = True
                print(f"Registration: {time.time() - tic:.4f}s")
            else:
                tic = time.time()
                detector.get_next(color)
                current_mask_raw = detector.current_frame_masks
                current_mask = to_binary_mask(current_mask_raw)
                bbox_xywh = bbox_from_mask(current_mask) if current_mask is not None else None
                if bbox_xywh is not None and (bbox_xywh[2] <= 0 or bbox_xywh[3] <= 0):
                    bbox_xywh = None
                resp = pose.track(rgb=color, depth=depth, K=cam_K, iteration=3, bbox_xywh=bbox_xywh)
                if resp.get("result") != "SUCCESS":
                    print("Track failed:", resp)
                    continue
                data = resp.get("data", {})
                current_pose = np.asarray(data.get("pose"))
                print(f"Track: {time.time() - tic:.4f}s")

            pose_np = current_pose[0] if current_pose.ndim == 3 else current_pose
            center_pose = pose_np @ np.linalg.inv(to_origin)
            vis_rgb = overlay_mask(color, current_mask)
            vis_rgb = draw_posed_3d_box(cam_K, img=vis_rgb, ob_in_cam=center_pose, bbox=bbox)
            vis_rgb = draw_axes(
                vis_rgb,
                ob_in_cam=center_pose,
                scale=0.1,
                K=cam_K,
                thickness=3,
                transparency=0,
                is_input_rgb=True,
            )

            vis_bgr = cv2.cvtColor(vis_rgb, cv2.COLOR_RGB2BGR)
            cv2.imshow("neuromeka_vfm Pose Demo", vis_bgr)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except KeyboardInterrupt:
        pass
    finally:
        detector.close()
        pipeline.stop()
        cv2.destroyAllWindows()
        pose.close()


if __name__ == "__main__":
    main()
