from pydantic import BaseModel

class Config(BaseModel):
    # 默认API地址
    xhs_api_url: str = "https://xhsapi.qzz.io/xhs"
    
    # 兼容PydanticV2的配置写法：忽略多余的配置项
    class Config:
        extra = "ignore"

