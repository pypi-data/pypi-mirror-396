import json
from pathlib import Path
from typing import List, Literal

class DataManager:
    def __init__(self):
        self.data_dir = Path("data/image_summary")
        self.data_file = self.data_dir / "data.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        if not self.data_file.exists():
            self.data = {
                "whitelist": [],  # 开启外显的群号列表
                "local_quotes": [
                    "今日涩图[图片][图片][图片][图片]",
                    "群主泳装照[图片][图片][图片][图片]",
                    "我喜欢你",
                    "真是一对苦命鸳鸯啊",
                ],
                "source_mode": "local"  # "local" or "api"
            }
            self._save_data()
        else:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def _save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # --- 白名单管理 ---
    def set_group_state(self, group_id: int, enable: bool):
        if enable:
            if group_id not in self.data["whitelist"]:
                self.data["whitelist"].append(group_id)
        else:
            if group_id in self.data["whitelist"]:
                self.data["whitelist"].remove(group_id)
        self._save_data()

    def is_group_enabled(self, group_id: int) -> bool:
        return group_id in self.data["whitelist"]

    # --- 文案管理 ---
    def add_quote(self, quote: str):
        if quote not in self.data["local_quotes"]:
            self.data["local_quotes"].append(quote)
            self._save_data()

    def remove_quote(self, quote: str) -> bool:
        if quote in self.data["local_quotes"]:
            self.data["local_quotes"].remove(quote)
            self._save_data()
            return True
        return False

    def get_local_quotes(self) -> List[str]:
        return self.data["local_quotes"]

    # --- 模式切换 ---
    def set_source_mode(self, mode: Literal["local", "api"]):
        self.data["source_mode"] = mode
        self._save_data()

    def get_source_mode(self) -> str:
        return self.data.get("source_mode", "local")

data_manager = DataManager()