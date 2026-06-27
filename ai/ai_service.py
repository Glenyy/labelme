import base64
import io
import json
import os
import urllib.request
import urllib.error
from typing import Dict, List, Optional
from PIL import Image


class AIService:
    _DEFAULT_URL = os.environ.get(
        "AI_SERVER_URL",
        "http://127.0.0.1:3200/predict_from_array/"
    )  # 默认AI服务器URL


    MODELS: Dict[str, dict] = {
        "bm_cell_segmentation": {
            "name": "BM细胞分割",
            "url": _DEFAULT_URL,
            "timeout": 120,
        },
    }

    def __init__(self) -> None:
        self._current_model_name: Optional[str] = None  # 当前选中的模型名称
        available = list(self.MODELS.keys())  # 可用模型名称列表
        if available:  # 如果有可用模型，默认选择第一个模型
            self._current_model_name = available[0]

    def get_available_models(self) -> List[str]:  # 获取可用模型名称列表
        return list(self.MODELS.keys())

    def set_model(self, name: str) -> None:  # 设置当前选中的模型名称
        if name not in self.MODELS:
            raise ValueError(f"Unknown model: {name}")
        self._current_model_name = name

    @property
    def current_model(self) -> Optional[str]:  # 获取当前选中的模型名称
        return self._current_model_name

    def health_check(self, timeout: int = 5) -> bool:  # 检查当前选中模型的健康状态
        if self._current_model_name is None:
            return False
        cfg = self.MODELS[self._current_model_name]  # 获取当前选中模型的配置
        health_url = cfg["url"].rsplit("/predict_from_array/", 1)[0] + "/health"  # 构建健康检查URL
        try:
            req = urllib.request.Request(health_url, method="GET")  # 构建request请求对象
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # 发送GET请求，获取响应
                data = json.loads(resp.read().decode("utf-8"))  # 解析响应体为JSON格式
                return data.get("status") == "healthy"  # 检查模型状态是否为健康
        except Exception:
            return False

    def predict(self, image: Image.Image, file_name: str = "image.jpg") -> List[Dict]:  # 负责把当前画布上的图片发送给 AI 服务器，拿回标注数据
        """
        1. 检查模型 — 确认已选择模型（current_model），否则抛异常
        2. RGB 转换 — 如果图片是 RGBA/P 模式，先转为 RGB（JPEG 不支持 RGBA）
        3. Base64 编码 — 将 PIL Image 保存为 JPEG 字节流，再编码为 base64 字符串
        4. HTTP POST — 将 {"file_name": "xxx.jpg", "image_base64": "..."} 发送到模型服务器（默认127.0.0.1:3200/predict_from_array/）
        5. 解析响应 — 从返回的 JSON 中提取 result.data.shapes 列表
        6. 错误处理 — HTTP 错误、连接失败、JSON 解析失败等都会转为明确异常，供上层 UI 弹窗提示
        """
        if self._current_model_name is None:
            raise RuntimeError("No model selected")
        cfg = self.MODELS[self._current_model_name]

        if image.mode not in ("RGB", "L"):  # 如果图片不是RGB或L模式，先转换为RGB
            image = image.convert("RGB")

        buffer = io.BytesIO()  # 创建一个字节流对象，用于存储图片数据
        image.save(buffer, format="JPEG")  # 将图片保存为JPEG格式，转换为字节流
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")  # 将字节流编码为base64字符串

        payload = json.dumps({
            "file_name": file_name,
            "image_base64": image_base64,
        }).encode("utf-8")  # 将JSON数据编码为UTF-8字节流

        req = urllib.request.Request(
            cfg["url"], data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )  # 构建POST请求，将图片数据编码为JSON格式

        try:  # 尝试发送POST请求
            with urllib.request.urlopen(req, timeout=cfg.get("timeout", 120)) as resp:  # 发送POST请求，获取响应
                data = json.loads(resp.read().decode("utf-8"))  # 解析响应为JSON格式
        except urllib.error.HTTPError as e:  # 处理HTTP错误
            body = e.read().decode("utf-8", errors="replace")
            raise ValueError(f"Server error ({e.code}): {body}")
        except urllib.error.URLError as e:  # 处理连接错误
            raise ConnectionError(f"Cannot reach AI server: {e.reason}")
        except json.JSONDecodeError:  # 处理JSON解析错误
            raise ValueError("Invalid JSON response")

        if not data.get("success", False):  # 如果服务器返回的success字段为False，抛出异常
            raise ValueError(data.get("detail", "unknown error"))
        return data.get("result", {}).get("data", {}).get("shapes", [])  # 返回标注数据列表
