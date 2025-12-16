
from alibabacloud_vpc20160428.client import Client as Vpc20160428Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import json

from ..client.client import ClientConf 
from ..validators.validators import validate_cidr_block
import questionary
from questionary import Choice

class VPC(object):
    """
    管理和配置阿里云VPC
    """

    def __init__(self):
        # self._ist_flag =ist 
        client_conf = ClientConf()
        if client_conf.config is None:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            self._client = None
            return
        
        self.region = client_conf.region
        client_conf.config.endpoint = f'vpc.{self.region}.aliyuncs.com'
        self._client = Vpc20160428Client(client_conf.config)
            

    def _vpc_init(self):
        """从阿里选择一个VPC然后信息同步到本实例"""
        res=VPC._getvpcs()
        vpcs = res.body.vpcs.vpc
        choise_list=[]
        for vpc in vpcs:
            choise_list.append(
                Choice(
                    title=vpc.vpc_id,
                    value=vpc.vpc_id,
                    description=f"{vpc.vpc_name} ({vpc.cidr_block}) {vpc.region_id} {vpc.status} "
                )
            )

        if not choise_list:
            print("当前区域没有可用的 VPC，请先创建 VPC")
            return
        
        choise_res=questionary.select("请选择VPC:",choise_list).ask()
        choise_id = choise_res
        # print(choise_id)
        
        # 根据 choise_id 找到 vpcs 当中对应的 vpc 然后把这个vpc的所有字段都变成VPC实例的属性 
        selected_vpc = None
        for vpc in vpcs:
            if vpc.vpc_id == choise_id:
                selected_vpc = vpc
                break
        
        if selected_vpc:
            self.vpc_id = selected_vpc.vpc_id
            self.vpc_name = selected_vpc.vpc_name
            self.cidr_block = selected_vpc.cidr_block
            self.region_id = selected_vpc.region_id
            self.status = selected_vpc.status
            self.vswitchs=[]
            if selected_vpc.v_switch_ids and selected_vpc.v_switch_ids.v_switch_id:
                # 延迟导入避免循环依赖
                from .vswitch import VSWITCH
                for vswitch_id in selected_vpc.v_switch_ids.v_switch_id:
                    self.vswitchs.append(VSWITCH(vswitch_id=vswitch_id, vpc_id=self.vpc_id))
                    self.vswitchs[-1]._pull_vsw_info()   # 从阿里云拉取交换机详细信息 
                    pass 


    def vswls(self):
        """
        列出当前VPC下的所有交换机，按可用区ID字母顺序排序
        """
        self._vpc_init()
        if not hasattr(self, 'vpc_id'):
            return
        
        # 按照 zone_id 字母顺序排序
        sorted_vswitchs = sorted(self.vswitchs, key=lambda vsw: vsw.zone_id)
        for _ in sorted_vswitchs:
            print(_)


    def vswadd(self):
        self._vpc_init()
        if not hasattr(self, 'vpc_id'):
            return
        
        from ..ecs.ecs import ECS 
        zones_dict = ECS.get_zones()
        
        # 构建可选区域列表
        choice_list = []
        for zone_id, zone_info in sorted(zones_dict.items()):
            choice_list.append(
                Choice(
                    title=zone_id,
                    value=zone_id,
                    description=zone_info
                )
            )
        
        if not choice_list:
            print("当前区域没有可用区")
            return
        
        # 让用户选择可用区
        selected_zone = questionary.select("请选择可用区:", choice_list).ask()
        if not selected_zone:
            print("取消操作")
            return
        
        # 询问用户输入 CIDR 块
        cidr_block = questionary.text(
            "请输入交换机的 CIDR 块 (例如: 10.10.1.0/24):",
            validate=lambda text: validate_cidr_block(text) or "CIDR 块格式不正确，请输入正确的格式 (例如: 10.10.1.0/24)"
        ).ask()
        
        if not cidr_block:
            print("取消操作")
            return
        
        # 询问用户输入交换机名称
        vswitch_name = questionary.text(
            "请输入交换机名称:",
            validate=lambda text: len(text) > 0 or "交换机名称不能为空"
        ).ask()
        
        if not vswitch_name:
            print("取消操作")
            return
        
        # 初始化 VSWITCH 实例
        from .vswitch import VSWITCH
        vswitch = VSWITCH(
            vswitch_name=vswitch_name,
            vswitch_id=None,
            vpc_id=self.vpc_id,
            zone_id=selected_zone,
            cidr_block=cidr_block
        )
        
        # 调用 _create_vsw 创建交换机
        try:
            vswitch._create_vsw()
            print(f"交换机创建成功: 名称={vswitch_name}, 可用区={selected_zone}, CIDR块={cidr_block}")
        except Exception as error:
            print(f"交换机创建失败: {error.message if hasattr(error, 'message') else str(error)}")
            if hasattr(error, 'data') and error.data.get("Recommend"):
                print(f"诊断建议: {error.data.get('Recommend')}")
            return 


    def vswdel(self):
        self._vpc_init()
        if not hasattr(self, 'vpc_id'):
            return
        
        # 获取 self.vswitchs 列表当中所有对象 然用户选择
        # 然后执行 用户选择的那个 VSWITCH 实例的  _del_vsw 方法
        if not self.vswitchs:
            print("当前 VPC 没有交换机")
            return
        
        # 构建选择列表
        choice_list = []
        # 按照 zone_id 排序
        sorted_vswitchs = sorted(self.vswitchs, key=lambda vsw: vsw.zone_id)
        for vsw in sorted_vswitchs:
            choice_list.append(
                Choice(
                    title=vsw.id,
                    value=vsw.id,
                    description=f"名字:{vsw.name} 区域:{vsw.zone_id} VPC:{vsw.vpc_id} CIDR块:{vsw.cidr_block}"
                )
            )
        
        # 让用户选择
        choice_res = questionary.select("请选择要删除的交换机:", choice_list).ask()
        if not choice_res:
            print("取消操作")
            return
        
        choice_id = choice_res
        
        # 找到对应的 VSWITCH 实例并执行删除
        for vsw in self.vswitchs:
            if vsw.id == choice_id:
                # 再次确认是否删除
                confirm = questionary.confirm(
                    f"确认删除交换机 {choice_id} ({vsw.name})？此操作不可恢复。",
                    default=False
                ).ask()
                
                if not confirm:
                    print("已取消删除操作")
                    return
                
                try:
                    vsw._del_vsw()
                    print(f"交换机 {choice_id} 删除成功")
                except Exception as error:
                    print(f"交换机删除失败: {error.message if hasattr(error, 'message') else str(error)}")
                    if hasattr(error, 'data') and error.data.get("Recommend"):
                        print(f"诊断建议: {error.data.get('Recommend')}")
                break

    @staticmethod
    def _getvpcs()-> vpc_20160428_models.DescribeVpcsResponse:
        """
        直接返回VPCS对象 因为可能会有不止一个地方需要使用这个对象
        """
        describe_vpcs_request = vpc_20160428_models.DescribeVpcsRequest(
            region_id=ClientConf().region 
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            ClientConf().config.endpoint = f'vpc.{ClientConf().region}.aliyuncs.com'
            res=Vpc20160428Client(ClientConf().config).describe_vpcs_with_options(describe_vpcs_request, runtime)
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
    
    @staticmethod
    def ls() -> None:
        """
        把vpcs 以人类可读的方式列出来
        """
        # 从 res 当中获取 Vpc信息并美化打印出来 包含 VpcId VpcName CidrBlock RegionId Status VswitchIds
        res = VPC._getvpcs()
        # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        vpcs = res.body.vpcs.vpc
        for vpc in vpcs:
            print(f"VPC ID: {vpc.vpc_id}")
            print(f"VPC 名称: {vpc.vpc_name}")
            print(f"CIDR 块: {vpc.cidr_block}")
            print(f"区域 ID: {vpc.region_id}")
            print(f"状态: {vpc.status}")
            print(f"交换机 IDs: {', '.join(vpc.v_switch_ids.v_switch_id) if vpc.v_switch_ids and vpc.v_switch_ids.v_switch_id else '无'}")
            print("-" * 50)

            

    