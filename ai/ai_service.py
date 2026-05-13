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
    )

    MODELS: Dict[str, dict] = {
        "bm_cell_segmentation": {
            "name": "BM细胞分割",
            "url": _DEFAULT_URL,
            "timeout": 120,
        },
    }

    def __init__(self) -> None:
        self._current_model_name: Optional[str] = None
        available = list(self.MODELS.keys())
        if available:
            self._current_model_name = available[0]

    def get_available_models(self) -> List[str]:
        return list(self.MODELS.keys())

    def set_model(self, name: str) -> None:
        if name not in self.MODELS:
            raise ValueError(f"Unknown model: {name}")
        self._current_model_name = name

    @property
    def current_model(self) -> Optional[str]:
        return self._current_model_name

    def health_check(self, timeout: int = 5) -> bool:
        if self._current_model_name is None:
            return False
        cfg = self.MODELS[self._current_model_name]
        health_url = cfg["url"].rsplit("/predict_from_array/", 1)[0] + "/health"
        try:
            req = urllib.request.Request(health_url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "healthy"
        except Exception:
            return False

    def predict(self, image: Image.Image, file_name: str = "image.jpg") -> List[Dict]:
        if self._current_model_name is None:
            raise RuntimeError("No model selected")
        cfg = self.MODELS[self._current_model_name]

        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        payload = json.dumps({
            "file_name": file_name,
            "image_base64": image_base64,
        }).encode("utf-8")

        req = urllib.request.Request(
            cfg["url"], data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=cfg.get("timeout", 120)) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise ValueError(f"Server error ({e.code}): {body}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot reach AI server: {e.reason}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response")

        if not data.get("success", False):
            raise ValueError(data.get("detail", "unknown error"))
        return data.get("result", {}).get("data", {}).get("shapes", [])
