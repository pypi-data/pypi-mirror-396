from pydantic import BaseModel

class Config(BaseModel):
    # 默认API地址
    xhs_api_url: str = "https://xhsapi.qzz.io/xhs"

