
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from ..client.client import ClientConf
import json  
from alibabacloud_tea_util.client import Client as UtilClient
import questionary
from questionary import Choice

class SECGROUP(object):
    
    def __init__(self):
        # 使用 ClientConf 单例获取已配置好凭证的 config
        client_conf = ClientConf()
        if client_conf.config is None:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            self.__client = None
            return
        
        self.region = client_conf.region
        client_conf.config.endpoint = f'ecs.{self.region}.aliyuncs.com'
        self.__client = Ecs20140526Client(client_conf.config)
        # self.sgp_id = None 


    @staticmethod
    def _getsgp():
        if ClientConf().config is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        try:
            describe_security_groups_request = ecs_20140526_models.DescribeSecurityGroupsRequest(
                region_id=ClientConf().region 
            )
            runtime = util_models.RuntimeOptions()
            ClientConf().config.endpoint = f'ecs.{ClientConf().region}.aliyuncs.com'
            res = Ecs20140526Client(ClientConf().config).describe_security_groups_with_options(describe_security_groups_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res 
        except Exception as error:
            # 判断是否为阿里云 SDK 异常
            if hasattr(error, 'data') and error.data:
                print(f"阿里云建议: {error.data.get('Recommend')}")
            if hasattr(error, 'message'):
                print(f"错误信息: {error.message}")
            else:
                print(f"获取安全组列表失败: {error}")

    @staticmethod
    def _getsgp_list():
        res=SECGROUP._getsgp()
        body = res.body
        security_groups = body.security_groups.security_group
        if not security_groups:
            print("当前区域没有安全组")
            return
        
        # 遍历security_groups并返回安全组ID列表
        return [sg.security_group_id for sg in security_groups]

    @staticmethod 
    def ls(block=False):
        """列出当前区域的安全组信息"""
        res = SECGROUP._getsgp()
        if res is None:
            return
        
        body = res.body
        security_groups = body.security_groups.security_group
        
        if not security_groups:
            print("当前区域没有安全组")
            return
        
        print(f"\n区域: {body.region_id}  共 {body.total_count} 个安全组\n")
        
        if not block:
            # 单行显示模式
            for sg in security_groups:
                create_time = sg.creation_time.replace('T', ' ').replace('Z', '')
                print(f"{sg.security_group_id} | {sg.security_group_name} | 规则:{sg.rule_count} | {create_time} | {sg.vpc_id}")
        else:
            # 多行显示模式
            for sg in security_groups:
                create_time = sg.creation_time.replace('T', ' ').replace('Z', '')
                print(f"安全组ID: {sg.security_group_id}")
                print(f"名称:     {sg.security_group_name}")
                print(f"规则数:   {sg.rule_count}")
                print(f"创建时间: {create_time}")
                print(f"VPC ID:   {sg.vpc_id}")
                print("-" * 50)

    def _init_sgp(self):
        """通过交互式选择初始化安全组信息"""
        res = SECGROUP._getsgp()
        if res is None:
            return
        body = res.body
        security_groups = body.security_groups.security_group
        if not security_groups:
            print("当前区域没有安全组")
            return
        
        # 构建选择列表
        choice_list = []
        for sg in security_groups:
            choice_list.append(
                Choice(
                    title=sg.security_group_id,
                    value=sg.security_group_id,
                    description=f"{sg.security_group_name} (规则数: {sg.rule_count}) VPC: {sg.vpc_id}"
                )
            )
        
        # 让用户选择安全组
        choice_res = questionary.select("请选择安全组:", choice_list).ask()
        choice_id = choice_res
        
        # 根据选择的ID找到对应的安全组对象
        selected_sg = None
        for sg in security_groups:
            if sg.security_group_id == choice_id:
                selected_sg = sg
                break
        
        # 将安全组的所有有价值信息设置为实例属性
        if selected_sg:
            self.security_group_id = selected_sg.security_group_id
            self.security_group_name = selected_sg.security_group_name
            self.security_group_type = selected_sg.security_group_type
            self.vpc_id = selected_sg.vpc_id
            self.description = selected_sg.description if hasattr(selected_sg, 'description') else ''
            self.creation_time = selected_sg.creation_time
            self.rule_count = selected_sg.rule_count
            self.resource_group_id = selected_sg.resource_group_id if hasattr(selected_sg, 'resource_group_id') else ''
            self.service_managed = selected_sg.service_managed if hasattr(selected_sg, 'service_managed') else False
            
            # 如果有标签信息也保存
            if hasattr(selected_sg, 'tags') and selected_sg.tags:
                self.tags = selected_sg.tags
            else:
                self.tags = []
        
    
    def _get_sgp_attr(self):
        self._init_sgp()
        client = self.__client
        describe_security_group_attribute_request = ecs_20140526_models.DescribeSecurityGroupAttributeRequest(
            region_id=self.region,
            security_group_id=self.security_group_id
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res=client.describe_security_group_attribute_with_options(describe_security_group_attribute_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res 
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


    def lsattr(self,block=False):
        """显示安全组的详细属性信息"""
        res = self._get_sgp_attr()
        if res is None:
            return
        
        # 从 to_map() 获取字典格式的数据
        data = res.to_map()
        body = data.get('body', {})
        
        # 打印基本信息
        print("\n安全组详细信息")
        print("=" * 60)
        print(f"安全组ID:   {body.get('SecurityGroupId', 'N/A')}")
        print(f"名称:       {body.get('SecurityGroupName', 'N/A')}")
        print(f"描述:       {body.get('Description', '无')}")
        print(f"VPC ID:     {body.get('VpcId', 'N/A')}")
        print(f"区域:       {body.get('RegionId', 'N/A')}")
        print(f"内部访问策略: {body.get('InnerAccessPolicy', 'N/A')}")
        print("=" * 60)
        
        # 打印规则
        permissions = body.get('Permissions', {})
        permission_list = permissions.get('Permission', [])
        
        if permission_list:
            print(f"\n安全组规则 (共 {len(permission_list)} 条):")
            
            if block:
                # 块状显示（纵向）
                print("-" * 60)
                for idx, rule in enumerate(permission_list, 1):
                    create_time = rule.get('CreateTime', '').replace('T', ' ').replace('Z', '')
                    print(f"\n规则 {idx}:")
                    print(f"  规则ID:       {rule.get('SecurityGroupRuleId', 'N/A')}")
                    print(f"  方向:         {rule.get('Direction', 'N/A')}")
                    print(f"  协议:         {rule.get('IpProtocol', 'N/A')}")
                    print(f"  端口范围:     {rule.get('PortRange', 'N/A')}")
                    print(f"  授权对象:     {rule.get('SourceCidrIp') or rule.get('SourceGroupId') or 'N/A'}")
                    print(f"  策略:         {rule.get('Policy', 'N/A')}")
                    print(f"  优先级:       {rule.get('Priority', 'N/A')}")
                    print(f"  创建时间:     {create_time}")
                    if rule.get('Description'):
                        print(f"  描述:         {rule.get('Description')}")
            else:
                # 横向显示（每条规则一行）
                print(f"{'序号':<4} {'方向':<8} {'协议':<6} {'端口':<12} {'授权对象':<18} {'策略':<8} {'优先级':<6} {'创建时间':<20}")
                print("-" * 100)
                for idx, rule in enumerate(permission_list, 1):
                    direction = rule.get('Direction', 'N/A')
                    protocol = rule.get('IpProtocol', 'N/A')
                    port_range = rule.get('PortRange', 'N/A')
                    source = rule.get('SourceCidrIp') or rule.get('SourceGroupId') or 'N/A'
                    policy = rule.get('Policy', 'N/A')
                    priority = str(rule.get('Priority', 'N/A'))
                    create_time = rule.get('CreateTime', '').replace('T', ' ').replace('Z', '')
                    
                    print(f"{idx:<4} {direction:<8} {protocol:<6} {port_range:<12} {source:<18} {policy:<8} {priority:<6} {create_time:<20}")
        else:
            print("\n安全组规则: 无")
        
        print("\n" + "=" * 60) 