from bizyairsdk import tensor_to_bytesio

from .trd_nodes_base import BizyAirTrdApiBaseNode


class Kling_2_1_T2V_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2.1 Text To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model_name": (["kling-v2-1-master"], {"default": "kling-v2-1-master"}),
                "duration": ([5, 10], {"default": 5}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            }
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2-1-master")
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        if prompt is None or prompt.strip() == "":
            raise ValueError("Prompt is required")
        if len(prompt) > 2500 or len(negative_prompt) > 2500:
            raise ValueError(
                "Prompt and negative prompt must be less than 2500 characters"
            )
        data = {
            "model_name": model,
            "negative_prompt": negative_prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "prompt": prompt,
        }
        return data, "kling-v2-1"

    def handle_outputs(self, outputs):
        return (outputs[0][0],)


class Kling_2_1_I2V_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2.1 Image To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame_image": ("IMAGE", {"tooltip": "首帧图片"}),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model_name": (
                    ["kling-v2-1-std", "kling-v2-1-pro", "kling-v2-1-master"],
                    {"default": "kling-v2-1-std"},
                ),
                "duration": ([5, 10], {"default": 5}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            },
            "optional": {
                "last_frame_image": ("IMAGE", {"tooltip": "末帧图片，只有pro支持"}),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2-1-std")
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        first_frame_image = kwargs.get("first_frame_image", None)
        last_frame_image = kwargs.get("last_frame_image", None)
        if first_frame_image is None:
            raise ValueError("First frame image is required")
        if len(prompt) > 2500 or len(negative_prompt) > 2500:
            raise ValueError(
                "Prompt and negative prompt must be less than 2500 characters"
            )
        # 上传图片
        url = self.upload_file(
            tensor_to_bytesio(image=first_frame_image, total_pixels=4096 * 4096),
            f"{prompt_id}_first.png",
            headers,
        )
        data = {
            "model_name": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "first_frame_image": url,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }
        if last_frame_image is not None:
            last_frame_image_url = self.upload_file(
                tensor_to_bytesio(image=last_frame_image, total_pixels=4096 * 4096),
                f"{prompt_id}_last.png",
                headers,
            )
            data["last_frame_image"] = last_frame_image_url
        return data, "kling-v2-1"

    def handle_outputs(self, outputs):
        return (outputs[0][0],)


# class Kling_2_1_PRO_I2V_API(BizyAirTrdApiBaseNode):
#     NODE_DISPLAY_NAME = "Kling 2.1 Pro Image To Video"
#     RETURN_TYPES = ("VIDEO",)
#     RETURN_NAMES = ("video",)
#     CATEGORY = "☁️BizyAir/External APIs/Kling"

#     @classmethod
#     def INPUT_TYPES(cls):
#         return {
#             "required": {
#                 "first_frame_image": ("IMAGE", {"tooltip": "首帧图片"}),
#                 "prompt": (
#                     "STRING",
#                     {
#                         "multiline": True,
#                         "default": "",
#                     },
#                 ),
#                 "negative_prompt": (
#                     "STRING",
#                     {
#                         "multiline": True,
#                         "default": "",
#                     },
#                 ),
#                 "model_name": (["kling-v2-1", "kling-v2-1-master"], {"default": "kling-v2-1"}),
#                 "duration": ([5, 10], {"default": 5}),
#                 "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
#             },
#             "optional": {
#                 "last_frame_image": ("IMAGE", {"tooltip": "末帧图片"}),
#             },
#         }

#     def handle_inputs(self, headers, prompt_id, **kwargs):
#         model = kwargs.get("model_name", "kling-v2-1")
#         prompt = kwargs.get("prompt", "")
#         negative_prompt = kwargs.get("negative_prompt", "")
#         duration = kwargs.get("duration", 5)
#         aspect_ratio = kwargs.get("aspect_ratio", "16:9")
#         first_frame_image = kwargs.get("first_frame_image", None)
#         last_frame_image = kwargs.get("last_frame_image", None)
#         if first_frame_image is None:
#             raise ValueError("First frame image is required")
#         if len(prompt) > 2500 or len(negative_prompt) > 2500:
#             raise ValueError("Prompt and negative prompt must be less than 2500 characters")
#         # 上传图片
#         first_frame_image_url = self.upload_file(
#             tensor_to_bytesio(image=first_frame_image, total_pixels=4096 * 4096),
#             f"{prompt_id}_first.png",
#             headers,
#         )
#         data = {
#             "model_name": model,
#             "prompt": prompt,
#             "negative_prompt": negative_prompt,
#             "first_frame_image": first_frame_image_url,
#             "duration": duration,
#             "aspect_ratio": aspect_ratio,
#         }
#         if model == "kling-v2-1":
#             data["mode"] = "pro"
#         if last_frame_image is not None:
#             last_frame_image_url = self.upload_file(
#                 tensor_to_bytesio(image=last_frame_image, total_pixels=4096 * 4096),
#                 f"{prompt_id}_last.png",
#                 headers,
#             )
#             data["last_frame_image"] = last_frame_image_url
#         return data, model

#     def handle_outputs(self, outputs):
#         return (outputs[0][0],)


class Kling_2_5_I2V_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2.5 Image To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame_image": ("IMAGE", {"tooltip": "首帧图片"}),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model_name": (["kling-v2-5-turbo"], {"default": "kling-v2-5-turbo"}),
                "duration": ([5, 10], {"default": 5}),
            },
            "optional": {
                "last_frame_image": ("IMAGE", {"tooltip": "末帧图片"}),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2-5-turbo")
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        duration = kwargs.get("duration", 5)
        first_frame_image = kwargs.get("first_frame_image", None)
        last_frame_image = kwargs.get("last_frame_image", None)
        if first_frame_image is None:
            raise ValueError("First frame image is required")
        if len(prompt) > 2500 or len(negative_prompt) > 2500:
            raise ValueError(
                "Prompt and negative prompt must be less than 2500 characters"
            )
        # 上传图片
        url = self.upload_file(
            tensor_to_bytesio(image=first_frame_image, total_pixels=4096 * 4096),
            f"{prompt_id}_first.png",
            headers,
        )
        data = {
            "model_name": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "duration": duration,
            "first_frame_image": url,
        }
        if last_frame_image is not None:
            last_frame_image_url = self.upload_file(
                tensor_to_bytesio(image=last_frame_image, total_pixels=4096 * 4096),
                f"{prompt_id}_last.png",
                headers,
            )
            data["last_frame_image"] = last_frame_image_url
        return data, "kling-v2-5"

    def handle_outputs(self, outputs):
        return (outputs[0][0],)


class Kling_2_6_T2V_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2.6 Text To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "sound": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "是否开启声音",
                    },
                ),
                "model_name": (["kling-v2-6"], {"default": "kling-v2-6"}),
                "duration": ([5, 10], {"default": 5}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2-6")
        prompt = kwargs.get("prompt", "")
        sound = kwargs.get("sound", False)
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        if len(prompt) > 1000:
            raise ValueError("Prompt must be less than 1000 characters")
        data = {
            "model_name": model,
            "prompt": prompt,
            "sound": sound,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }
        return data, "kling-v2-6"

    def handle_outputs(self, outputs):
        return (outputs[0][0],)


class Kling_2_6_I2V_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2.6 Image To Video"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_frame_image": ("IMAGE", {"tooltip": "首帧图片"}),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "sound": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "是否开启声音",
                    },
                ),
                "model_name": (["kling-v2-6"], {"default": "kling-v2-6"}),
                "duration": ([5, 10], {"default": 5}),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2-6")
        prompt = kwargs.get("prompt", "")
        sound = kwargs.get("sound", False)
        duration = kwargs.get("duration", 5)
        first_frame_image = kwargs.get("first_frame_image", None)
        if first_frame_image is None:
            raise ValueError("First frame image is required")
        if len(prompt) > 1000:
            raise ValueError("Prompt must be less than 1000 characters")
        # 上传图片
        url = self.upload_file(
            tensor_to_bytesio(image=first_frame_image, total_pixels=4096 * 4096),
            f"{prompt_id}.png",
            headers,
        )
        data = {
            "model_name": model,
            "prompt": prompt,
            "sound": sound,
            "duration": duration,
            "urls": [url],
        }
        return data, "kling-v2-6"

    def handle_outputs(self, outputs):
        return (outputs[0][0],)


class Kling_2_T2I_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2 Text To Image"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model_name": (["kling-v2"], {"default": "kling-v2"}),
                "aspect_ratio": (
                    ["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"],
                    {"default": "16:9"},
                ),
                "resolution": (["1K", "2K"], {"default": "1K"}),
                "variants": ("INT", {"default": 1, "min": 1, "max": 9}),
                "image_fidelity": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2")
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        resolution = kwargs.get("resolution", "1K").lower()
        variants = kwargs.get("variants", 1)
        image_fidelity = kwargs.get("image_fidelity", 0.5)
        if len(prompt) > 2500 or len(negative_prompt) > 2500:
            raise ValueError(
                "Prompt and negative prompt must be less than 2500 characters"
            )
        data = {
            "model_name": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "variants": variants,
            "image_fidelity": image_fidelity,
        }
        return data, "kling-v2"

    def handle_outputs(self, outputs):
        images = self.combine_images(outputs[1])
        return (images,)


class Kling_2_I2I_API(BizyAirTrdApiBaseNode):
    NODE_DISPLAY_NAME = "Kling 2 Image To Image"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    CATEGORY = "☁️BizyAir/External APIs/Kling"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "输入图片"}),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "model_name": (["kling-v2"], {"default": "kling-v2"}),
                "aspect_ratio": (
                    ["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"],
                    {"default": "16:9"},
                ),
                "resolution": (["1K"], {"default": "1K"}),
                "variants": ("INT", {"default": 1, "min": 1, "max": 9}),
                "image_fidelity": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    def handle_inputs(self, headers, prompt_id, **kwargs):
        model = kwargs.get("model_name", "kling-v2")
        prompt = kwargs.get("prompt", "")
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        resolution = kwargs.get("resolution", "1K").lower()
        variants = kwargs.get("variants", 1)
        image = kwargs.get("image", None)
        image_fidelity = kwargs.get("image_fidelity", 0.5)
        if image is None:
            raise ValueError("Image is required")
        if len(prompt) > 2500:
            raise ValueError("Prompt must be less than 2500 characters")
        # 上传图片
        image_url = self.upload_file(
            tensor_to_bytesio(image=image, total_pixels=4096 * 4096),
            f"{prompt_id}.png",
            headers,
        )
        data = {
            "model_name": model,
            "prompt": prompt,
            "image": image_url,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "variants": variants,
            "image_fidelity": image_fidelity,
        }
        return data, "kling-v2"

    def handle_outputs(self, outputs):
        images = self.combine_images(outputs[1])
        return (images,)
