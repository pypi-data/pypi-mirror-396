from typing import List
from pydantic import BaseModel, Field

class Config(BaseModel):
    # API文案源列表
    image_summary_apis: List[str] = Field(
        default=[
            "https://v1.hitokoto.cn/?encode=text",
            "https://api.shadiao.pro/du",
            "https://api.shadiao.pro/chp"
        ]
    )
    # 是否开启调试模式（输出详细日志）
    image_summary_debug: bool = False