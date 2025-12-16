
from ..config.config import CONFIG
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials import models as credential_models
from alibabacloud_tea_openapi import models as open_api_models

from ..decorators.singleton import Singleton

@Singleton
class ClientConf(object):
    def __init__(self):

        current_config = CONFIG().curprof()
        if current_config is None:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            self.config = None
            return

        # 使用配置文件中的凭证信息创建 credential
        credential_config = credential_models.Config(
            type='access_key',
            access_key_id=current_config["access_key_id"],
            access_key_secret=current_config["access_key_secret"]
        )
        credential = CredentialClient(credential_config)

        config = open_api_models.Config(
            credential=credential
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Vpc
        self.region = current_config["region_id"] 
        self.config = config 



if __name__=="__main__":
    client1 = ClientConf()
    client2 = ClientConf()
    print(client1 is client2)  # True

    # 获取VPC客户端
    print(client1.client)
    print(ClientConf().region)
    pass