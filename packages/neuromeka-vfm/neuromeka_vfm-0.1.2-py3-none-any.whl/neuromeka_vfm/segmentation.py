import time
from typing import Union, List
import numpy as np

from .pickle_client import PickleClient
from .compression import STRATEGIES


class Segmentation:
    """
    Client for realtime segmentation/tracking server (ZeroMQ pickle RPC).
    """

    def __init__(self, hostname, port, compression_strategy="none", benchmark=False):
        self.first_frame_registered = False
        self.client = PickleClient(hostname, port)
        self.tracking_object_ids = []
        self.current_frame_masks = {}
        self.image_prompt_names = set()
        if compression_strategy in STRATEGIES:
            self.compression_strategy_name = compression_strategy
        else:
            raise ValueError(f"Only valid compression strategies are {list(STRATEGIES.keys())}")
        self.benchmark = benchmark
        if self.benchmark:
            self.call_time = {"add_image_prompt": 0, "register_first_frame": 0, "get_next": 0}
            self.call_count = {"add_image_prompt": 0, "register_first_frame": 0, "get_next": 0}

    def switch_compression_strategy(self, compression_strategy):
        if compression_strategy in STRATEGIES:
            self.compression_strategy_name = compression_strategy
        else:
            raise ValueError(f"Only valid compression strategies are {list(STRATEGIES.keys())}")

    def reset(self):
        self.first_frame_registered = False
        self.tracking_object_ids = []
        self.current_frame_masks = {}
        self.encoder = None
        if self.benchmark:
            self.call_time = {"add_image_prompt": 0, "register_first_frame": 0, "get_next": 0}
            self.call_count = {"add_image_prompt": 0, "register_first_frame": 0, "get_next": 0}

    def add_image_prompt(self, object_name, object_image):
        if self.benchmark:
            start = time.time()
        data = {"operation": "add_image_prompt", "object_name": object_name, "object_image": object_image}
        response = self.client.send_data(data)
        if response.get("result") == "SUCCESS":
            self.image_prompt_names.add(object_name)
        if self.benchmark:
            self.call_time["add_image_prompt"] += time.time() - start
            self.call_count["add_image_prompt"] += 1
        return response

    def register_first_frame(self, frame: np.ndarray, prompt: Union[str, List[str]], use_image_prompt: bool = False):
        if self.benchmark:
            start = time.time()
        prompt_to_send = prompt
        if use_image_prompt:
            prompt_list = prompt if isinstance(prompt, list) else [prompt]
            missing = [p for p in prompt_list if p not in self.image_prompt_names]
            if missing:
                raise ValueError(f"Image prompt(s) not registered: {missing}. Call add_image_prompt first.")
            prompt_to_send = prompt_list
        self.compression_strategy = STRATEGIES[self.compression_strategy_name](frame)
        data = {
            "operation": "start",
            "prompt": prompt_to_send,
            "frame": self.compression_strategy.encode(frame),
            "use_image_prompt": use_image_prompt,
            "compression_strategy": self.compression_strategy_name,
        }
        response = self.client.send_data(data)
        if response.get("result") == "SUCCESS":
            self.first_frame_registered = True
            self.tracking_object_ids = response["data"]["obj_ids"]
            masks = {}
            for i, obj_id in enumerate(self.tracking_object_ids):
                mask = self.compression_strategy.decode(response["data"]["masks"][i])
                if np.any(mask):
                    masks[obj_id] = mask
            self.current_frame_masks = masks
            if self.benchmark:
                self.call_time["register_first_frame"] += time.time() - start
                self.call_count["register_first_frame"] += 1
            return True
        else:
            if self.benchmark:
                self.call_time["register_first_frame"] += time.time() - start
                self.call_count["register_first_frame"] += 1
            return False

    def get_next(self, frame: np.ndarray):
        if not self.first_frame_registered:
            print("Segmentation: register_first_frame must be called first")
            return None
        if self.benchmark:
            start = time.time()
        response = self.client.send_data({"operation": "get_next", "frame": self.compression_strategy.encode(frame)})
        if response.get("result") == "SUCCESS":
            masks = {}
            for i, obj_id in enumerate(self.tracking_object_ids):
                mask = self.compression_strategy.decode(response["data"]["masks"][i])
                if np.any(mask):
                    masks[obj_id] = mask
            self.current_frame_masks = masks
            if self.benchmark:
                self.call_time["get_next"] += time.time() - start
                self.call_count["get_next"] += 1
            return masks
        if self.benchmark:
            self.call_time["get_next"] += time.time() - start
            self.call_count["get_next"] += 1
        return None

    def finish(self):
        if not self.first_frame_registered:
            print("Warning: Segmentation: register_first_frame must be called first")
        self.first_frame_registered = False
        self.tracking_object_ids = []
        self.current_frame_masks = {}

    def close(self):
        """Close underlying ZeroMQ socket/context."""
        try:
            self.finish()
        finally:
            self.client.close()


# Backward-compat alias
NrmkRealtimeSegmentation = Segmentation
