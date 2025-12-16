
from alibabacloud_vpc20160428.client import Client as Vpc20160428Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from ..client.client import ClientConf
from .vpc import VPC 

class VSWITCH(VPC):
    def __init__(
        self,
        vswitch_id=None,
        vswitch_name=None,
        vpc_id=None,
        name=None,
        zone_id=None,
        cidr_block=None,
        status=None,
        available_ip_address_count=None,
        creation_time=None,
        description=None
    ):
        super().__init__()
        self.id = vswitch_id
        self.vswitch_name=vswitch_name
        self.vpc_id = vpc_id 
        self.name = name
        self.zone_id = zone_id
        self.cidr_block = cidr_block
        self.status = status
        self.available_ip_address_count = available_ip_address_count
        self.creation_time = creation_time
        self.description = description

    @staticmethod
    def _getvsw(vswitch_id):
        describe_vswitch_attributes_request = vpc_20160428_models.DescribeVSwitchAttributesRequest(
            region_id=ClientConf().region ,
            v_switch_id=vswitch_id
        )
        runtime = util_models.RuntimeOptions()
        try:
            ClientConf().config.endpoint = f'vpc.{ClientConf().region}.aliyuncs.com'
            res=Vpc20160428Client(ClientConf().config).describe_vswitch_attributes_with_options(describe_vswitch_attributes_request, runtime)
            # 这里调用的接口名称是  DescribeVSwitchAttributes
            # 返回的res是json格式 这里先打印成人类可读的形式
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res 
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        pass

    def _pull_vsw_info(self):
        res = self._getvsw(self.id)
        if res:
            self.name = res.body.v_switch_name
            self.zone_id = res.body.zone_id
            self.cidr_block = res.body.cidr_block
            self.status = res.body.status
            self.available_ip_address_count = res.body.available_ip_address_count
            self.creation_time = res.body.creation_time
            self.description = res.body.description if hasattr(res.body, 'description') else None


    def __str__(self):
        # 调用 _getvsw 并把返回值填充到 self 当中
        self._pull_vsw_info()
        return f"VSwitchId: {self.id}, VSwitchName: {self.name},  ZoneId: {self.zone_id}, CidrBlock: {self.cidr_block},   VpcId: {self.vpc_id},"


    def _create_vsw(self):
        client = self._client 
        create_vswitch_request = vpc_20160428_models.CreateVSwitchRequest(
            region_id=self.region,
            zone_id=self.zone_id,
            vpc_id=self.vpc_id,
            cidr_block=self.cidr_block,
            v_switch_name=self.vswitch_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            client.create_vswitch_with_options(create_vswitch_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        pass
    
    
    def _del_vsw(self):
        client = self._client
        delete_vswitch_request = vpc_20160428_models.DeleteVSwitchRequest(
            region_id=self.region,
            v_switch_id=self.id
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            client.delete_vswitch_with_options(delete_vswitch_request, runtime)
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)