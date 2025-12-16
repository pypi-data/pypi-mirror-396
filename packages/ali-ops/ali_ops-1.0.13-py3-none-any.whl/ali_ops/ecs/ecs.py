

from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import json
from ..client.client import ClientConf



class ECS(object): 
    """
    阿里云ECS服务
    """
    
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
    

    def istadd(self):
        # region 初始化和导入
        from ..vpc.vpc import VPC 
        import questionary
        from questionary import Choice
        
        vpc=VPC()
        vpc._vpc_init()
        if not hasattr(vpc, 'vpc_id'):
            return
        # endregion
        
        # region 选择交换机
        # 构建 vswitch 选择列表，按 zone_id 排序
        sorted_vswitchs = sorted(vpc.vswitchs, key=lambda vsw: vsw.zone_id)
        choice_list = []
        for vsw in sorted_vswitchs:
            choice_list.append(
                Choice(
                    title=vsw.id,
                    value=vsw.id,
                    description=f"名称:{vsw.name} 可用区:{vsw.zone_id} CIDR:{vsw.cidr_block}"
                )
            )
        
        if not choice_list:
            print("当前 VPC 没有可用的交换机，请先创建交换机")
            return
        
        # 询问用户选择 vswitch
        selected_vswitch_id = questionary.select("请选择交换机:", choice_list).ask()
        if not selected_vswitch_id:
            print("取消操作")
            return
        
        # 根据选择的 vswitch_id 找到对应的 vswitch 对象
        selected_vswitch = None
        for vsw in vpc.vswitchs:
            if vsw.id == selected_vswitch_id:
                selected_vswitch = vsw
                break
        
        # 获取选定 vswitch 的 zone_id
        zone_id = selected_vswitch.zone_id
        # endregion
        
        # region 选择实例规格
        # 获取该可用区的实例规格列表
        instance_types = self.list_instance_types(zone_id=zone_id)
        if not instance_types:
            print("未找到可用的实例规格")
            return
        
        # 构建实例规格字典供 CustomCompleter 使用
        from ..completors.customCompleter import CustomCompleter, CustomValidator
        from prompt_toolkit import prompt
        
        instance_type_dict = {itype: itype for itype in sorted(instance_types)}
        completer = CustomCompleter(instance_type_dict)
        validator = CustomValidator(completer, error_msg="请从实例规格列表中选择")
        
        # 让用户选择实例规格
        selected_instance_type = prompt(
            "请选择实例规格 (支持模糊搜索TAB补全): ",
            completer=completer,
            validator=validator
        ).strip()
        
        if not selected_instance_type:
            print("取消操作")
            return
        
        print(f"已选择实例规格: {selected_instance_type}")
        # endregion

        # region 配置私网IP地址
        private_ip_address = questionary.text(
            f"请输入私网IP地址 (CIDR范围: {selected_vswitch.cidr_block}, 留空则自动分配): "
        ).ask()
        
        # 如果用户留空，则设置为None让系统自动分配
        if not private_ip_address or private_ip_address.strip() == "":
            private_ip_address = None
            print("将自动分配私网IP地址")
        else:
            private_ip_address = private_ip_address.strip()
            print(f"已设置私网IP地址: {private_ip_address}")
        # endregion
        
        # region 选择安全组
        from .securityGroup import SECGROUP
        
        # 获取安全组详细信息用于构建选择列表
        sgp_res = SECGROUP._getsgp()
        if sgp_res is None or not sgp_res.body.security_groups.security_group:
            print("未找到可用的安全组")
            return   
        
        # 构建安全组选择列表，只包含与选定VPC匹配的安全组
        sg_choice_list = []
        for sg in sgp_res.body.security_groups.security_group:
            # 只添加属于选定VPC的安全组
            if sg.vpc_id == vpc.vpc_id:
                sg_choice_list.append(
                    Choice(
                        title=sg.security_group_id,
                        value=sg.security_group_id,
                        description=f"名称:{sg.security_group_name} 规则数:{sg.rule_count} VPC:{sg.vpc_id}"
                    )
                )
        
        if not sg_choice_list:
            print("当前 VPC 没有可用的安全组，请先创建安全组")
            return
        
        # 让用户多选安全组
        selected_security_group_ids = questionary.checkbox(
            "请选择安全组 (空格选择/取消，回车确认):",
            choices=sg_choice_list
        ).ask()
        
        if not selected_security_group_ids:
            print("未选择安全组，取消操作")
            return
        
        print(f"已选择 {len(selected_security_group_ids)} 个安全组: {', '.join(selected_security_group_ids)}")
        # endregion
        
        # region 选择镜像
        from ..utils.utils import image_choices
        
        image_choice_list = []
        for image_id, description in image_choices.items():
            image_choice_list.append(
                Choice(
                    title=image_id,
                    value=image_id,
                    description=description
                )
            )
        
        selected_image_id = questionary.select(
            "请选择镜像:",
            choices=image_choice_list
        ).ask()
        
        if not selected_image_id:
            print("未选择镜像，取消操作")
            return
        
        print(f"已选择镜像: {selected_image_id}")
        # endregion
        
        # region 配置实例密码
        selected_password = questionary.password(
            "请输入实例密码 (留空使用默认密码 ggmm12LPP!):"
        ).ask()
        
        if not selected_password or selected_password.strip() == "":
            selected_password = "ggmm12LPP!"
            print("将使用默认密码")
        else:
            selected_password = selected_password.strip()
            print("已设置自定义密码")
        # endregion
        
        # region 选择系统盘类型
        # 使用 _get_available_systemdisk_type 函数获取可用的系统盘类型
        available_disk_types = self._get_available_systemdisk_type_by_zone(
            instance_type=selected_instance_type,
            zone_id=zone_id
        )
        
        if not available_disk_types:
            print("未找到可用的系统盘类型，取消操作")
            return
        
        # 构建系统盘类型选择列表
        disk_category_choices = []
        disk_type_descriptions = {
            "cloud_essd": "ESSD云盘",
            "cloud_efficiency": "高效云盘",
            "cloud_ssd": "SSD云盘",
            "cloud": "普通云盘",
            "cloud_auto": "ESSD AutoPL云盘",
            "cloud_essd_entry": "ESSD Entry云盘"
        }
        
        for disk_info in available_disk_types:
            disk_type = disk_info['value']
            min_size = disk_info['min']
            max_size = disk_info['max']
            base_description = disk_type_descriptions.get(disk_type, disk_type)
            description = f"{base_description} (容量范围: {min_size}-{max_size}GB)"
            
            disk_category_choices.append(
                Choice(title=disk_type, value=disk_type, description=description)
            )
        
        selected_disk_category = questionary.select(
            "请选择系统盘类型:",
            choices=disk_category_choices
        ).ask()
        
        if not selected_disk_category:
            print("未选择系统盘类型，取消操作")
            return
        
        print(f"已选择系统盘类型: {selected_disk_category}")
        # endregion
        
        # region 配置系统盘大小
        selected_disk_size = questionary.text(
            "请输入系统盘大小(GB) (留空使用默认值30GB):"
        ).ask()
        
        if not selected_disk_size or selected_disk_size.strip() == "":
            selected_disk_size = "30"
            print("将使用默认系统盘大小: 30GB")
        else:
            selected_disk_size = selected_disk_size.strip()
            print(f"已设置系统盘大小: {selected_disk_size}GB")
        # endregion
        
        # region 创建实例
        self._creat_instance(
            v_switch_id=selected_vswitch_id,
            instance_type=selected_instance_type,
            image_id=selected_image_id,
            security_group_ids=selected_security_group_ids,
            password=selected_password,
            instance_name='test',
            private_ip_address=private_ip_address,
            system_disk_category=selected_disk_category,
            system_disk_size=selected_disk_size
        )
        # endregion 
        
    
    def _creat_instance(
        self,
        v_switch_id: str,
        instance_type: str,
        image_id: str,
        security_group_ids: list[str],
        password: str='ggmm12LPP!',
        instance_name: str='test',
        private_ip_address: str = None,
        system_disk_category: str = 'cloud_essd',
        system_disk_size: str = '30'
    ):
        """
        创建按量付费实例 或者竞价实例
        https://api.aliyun.com/api/Ecs/2014-05-26/RunInstances
        
        
        参数:
            v_switch_id: 交换机ID
            instance_type: 实例规格类型
            image_id: 镜像ID
            security_group_ids: 安全组ID列表
            password: 实例密码
            instance_name: 实例名称
            private_ip_address: 私网IP地址（可选）
            system_disk_category: 系统盘类型（可选，默认为 'cloud_essd')
            system_disk_size: 系统盘大小（可选，默认为 '30')
        """
        if self.__client is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        
        private_dns_name_options = ecs_20140526_models.RunInstancesRequestPrivateDnsNameOptions(
            hostname_type='IpBased',
            enable_instance_id_dns_arecord=True,
            enable_instance_id_dns_aaaarecord=True,
            enable_ip_dns_arecord=True,
            enable_ip_dns_ptr_record=True
        )
        image_options = ecs_20140526_models.RunInstancesRequestImageOptions(
            login_as_non_root=True
        )
        system_disk = ecs_20140526_models.RunInstancesRequestSystemDisk(
            category=system_disk_category,
            size=system_disk_size
        )
        run_instances_request = ecs_20140526_models.RunInstancesRequest(
            instance_charge_type='PostPaid',  # 后付费实例 和PrePaid 相对
            region_id=self.region,
            v_switch_id=v_switch_id,
            private_ip_address=private_ip_address,
            instance_type=instance_type,
            spot_strategy='SpotAsPriceGo', # 最优方式就是系统自动出价 
            spot_interruption_behavior='Stop',
            image_id=image_id,
            system_disk=system_disk,
            internet_charge_type='PayByTraffic',
            internet_max_bandwidth_out=100,
            security_group_ids=security_group_ids,
            password=password,
            image_options=image_options,
            instance_name=instance_name,
            private_dns_name_options=private_dns_name_options
            
        )
        runtime = util_models.RuntimeOptions()
        try:
            res=self.__client.run_instances_with_options(run_instances_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        except Exception as error:
            print(error.message)
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)





    @staticmethod
    def _getecs():
        if ClientConf().config is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return

        describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
            region_id=ClientConf().region
        )
        runtime = util_models.RuntimeOptions()
        ClientConf().config.endpoint = f'ecs.{ClientConf().region}.aliyuncs.com'
        res=Ecs20140526Client(ClientConf().config).describe_instances_with_options(describe_instances_request, runtime)
        
        # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        return res 

    @staticmethod
    def _getecs_filter():
        if ClientConf().config is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return

        describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(
            region_id=ClientConf().region,
            # zone_id='cn-shenzhen-f',
        )
        runtime = util_models.RuntimeOptions()
        ClientConf().config.endpoint = f'ecs.{ClientConf().region}.aliyuncs.com'
        res=Ecs20140526Client(ClientConf().config).describe_instances_with_options(describe_instances_request, runtime)
        
        print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
        # return res 

    @staticmethod
    def ls(block=True) -> None:
        """
        列出当前region下的所有ECS实例
        """
        try:
            res=ECS._getecs()
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))

            # 找出 res.body.Instances.Instance 当中的所有 instance 
            # 然后 针对每个 instance 列出他们的  
            #   InstanceId PublicIpAddress InstanceName InstanceType InternetChargeType 
            #   RegionId PrimaryIpAddress ImageId  SecurityGroupIds VSwitchId  VpcId
            instances = res.body.instances.instance
            for instance in instances:
                # 获取主私网IP
                primary_ip = ""
                if instance.network_interfaces and instance.network_interfaces.network_interface:
                    primary_ip = instance.network_interfaces.network_interface[0].primary_ip_address
                
                # 获取交换机ID和专有网络ID
                vswitch_id = ""
                vpc_id = ""
                if instance.vpc_attributes:
                    vswitch_id = instance.vpc_attributes.v_switch_id
                    vpc_id = instance.vpc_attributes.vpc_id
                
                if block:
                    # 多行输出模式
                    print(f"实例ID: {instance.instance_id}")
                    print(f"实例状态: {instance.status}")
                    print(f"公网IP: {instance.public_ip_address}")
                    print(f"实例名称: {instance.instance_name}")
                    print(f"实例规格: {instance.instance_type}")
                    print(f"网络计费类型: {instance.internet_charge_type}")
                    print(f"地域ID: {instance.region_id}")
                    print(f"主私网IP: {primary_ip}")
                    print(f"镜像ID: {instance.image_id}")
                    print(f"安全组ID: {instance.security_group_ids}")
                    print(f"交换机ID: {vswitch_id}")
                    print(f"专有网络ID: {vpc_id}")
                    print("-" * 50)
                else:
                    # 单行输出模式
                    print(f"实例ID: {instance.instance_id} | 状态: {instance.status} | 公网IP: {instance.public_ip_address} | 私网IP: {primary_ip} | 规格: {instance.instance_type} | 名称: {instance.instance_name} | 镜像: {instance.image_id} | 安全组: {instance.security_group_ids} | 交换机: {vswitch_id} ")


        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(f"Error occurred: {str(error)}")
            # 如果是阿里云SDK的异常，尝试获取更多信息
            if hasattr(error, 'data') and error.data:
                print(f"Recommend: {error.data.get('Recommend', 'No recommendation available')}")
            UtilClient.assert_as_string(str(error))


    def stop(self):
        """
        停止ECS实例，通过交互式选择要停止的后付费实例
        """
        if self.__client is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        
        import questionary
        from questionary import Choice
        
        # 获取当前region下的所有实例
        try:
            res = self._getecs()
            if res is None or not res.body.instances.instance:
                print("当前region下没有可用的实例")
                return
            
            instances = res.body.instances.instance
            
            # 过滤出后付费实例并构建选择列表
            choice_list = []
            for instance in instances:
                # 只选择后付费实例
                if instance.instance_charge_type != "PostPaid":
                    continue
                
                # 获取主私网IP
                primary_ip = ""
                if instance.network_interfaces and instance.network_interfaces.network_interface:
                    primary_ip = instance.network_interfaces.network_interface[0].primary_ip_address
                
                # 获取公网IP
                public_ip = instance.public_ip_address.ip_address[0] if instance.public_ip_address.ip_address else "无"
                
                choice_list.append(
                    Choice(
                        title=instance.instance_id,
                        value=instance.instance_id,
                        description=f"名称:{instance.instance_name} 状态:{instance.status} 公网IP:{public_ip} 私网IP:{primary_ip} 计费:{instance.instance_charge_type}"
                    )
                )
            
            if not choice_list:
                print("当前region下没有后付费实例")
                return
            
            # 让用户选择要停止的实例
            selected_instance_id = questionary.select(
                "请选择要停止的后付费实例:",
                choices=choice_list
            ).ask()
            
            if not selected_instance_id:
                print("取消操作")
                return
            
            # 执行停止操作
            stop_instance_request = ecs_20140526_models.StopInstanceRequest(
                instance_id=selected_instance_id
            )
            runtime = util_models.RuntimeOptions()
            
            self.__client.stop_instance_with_options(stop_instance_request, runtime)
            print(f"实例 {selected_instance_id} 停止请求已发送")
            
        except Exception as error:
            print(f"停止实例失败: {error.message}")
            if hasattr(error, 'data') and error.data:
                print(f"诊断建议: {error.data.get('Recommend')}")
            UtilClient.assert_as_string(error.message)


    def istdel(self):
        """
        删除ECS实例，通过交互式选择要删除的后付费实例
        """
        if self.__client is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        
        import questionary
        from questionary import Choice
        
        # 获取当前region下的所有实例
        try:
            res = self._getecs()
            if res is None or not res.body.instances.instance:
                print("当前region下没有可用的实例")
                return
            
            instances = res.body.instances.instance
            
            # 过滤出后付费实例并构建选择列表
            choice_list = []
            for instance in instances:
                # 只选择后付费实例
                if instance.instance_charge_type != "PostPaid":
                    continue
                
                # 获取主私网IP
                primary_ip = ""
                if instance.network_interfaces and instance.network_interfaces.network_interface:
                    primary_ip = instance.network_interfaces.network_interface[0].primary_ip_address
                
                # 获取公网IP
                public_ip = instance.public_ip_address.ip_address[0] if instance.public_ip_address.ip_address else "无"
                
                choice_list.append(
                    Choice(
                        title=instance.instance_id,
                        value=instance.instance_id,
                        description=f"名称:{instance.instance_name} 状态:{instance.status} 公网IP:{public_ip} 私网IP:{primary_ip} 计费:{instance.instance_charge_type}"
                    )
                )
            
            if not choice_list:
                print("当前region下没有后付费实例")
                return
            
            # 让用户选择要删除的实例
            selected_instance_id = questionary.select(
                "请选择要删除的后付费实例:",
                choices=choice_list
            ).ask()
            
            if not selected_instance_id:
                print("取消操作")
                return
            
            # 二次确认
            confirm = questionary.confirm(
                f"确认要删除实例 {selected_instance_id} 吗？此操作不可恢复！",
                default=False
            ).ask()
            
            if not confirm:
                print("取消删除操作")
                return
            
            # 执行删除操作
            delete_instance_request = ecs_20140526_models.DeleteInstanceRequest(
                instance_id=selected_instance_id
            )
            runtime = util_models.RuntimeOptions()
            
            delete_res = self.__client.delete_instance_with_options(delete_instance_request, runtime)
            print(f"实例 {selected_instance_id} 删除操作已执行")
            # return delete_res
            
        except Exception as error:
            print(f"删除实例失败: {error.message}")
            if hasattr(error, 'data') and error.data:
                print(f"诊断建议: {error.data.get('Recommend')}")
            UtilClient.assert_as_string(error.message)


    def _get_available_systemdisk_type(self, instance_type):
        """
        获取指定实例规格的可用系统盘类型
        
        参数:
            instance_type: 实例规格类型
        
        返回: 
            API响应对象
        """
        # https://api.aliyun.com/api/Ecs/2014-05-26/DescribeAvailableResource
        
        client = self.__client
        describe_available_resource_request = ecs_20140526_models.DescribeAvailableResourceRequest(
            region_id=self.region,
            instance_charge_type='PostPaid',
            spot_strategy='SpotAsPriceGo',
            destination_resource='SystemDisk',
            instance_type=instance_type
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = client.describe_available_resource_with_options(describe_available_resource_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res
        except Exception as error:
            print(f"获取系统盘类型失败: {error.message}")
            if hasattr(error, 'data') and error.data:
                print(f"诊断建议: {error.data.get('Recommend')}")
            UtilClient.assert_as_string(error.message)
            return None
    
    def _get_available_systemdisk_type_by_zone(self, instance_type, zone_id):
        """
        根据实例规格和可用区ID获取可用的系统盘类型详细信息
        
        参数:
            instance_type: 实例规格类型
            zone_id: 可用区ID
        
        返回:
            包含磁盘类型详细信息的字典列表，每个字典包含: value, min, max
        """
        res = self._get_available_systemdisk_type(instance_type)
        if res is None:
            return []
        
        disk_types_info = []
        # 遍历可用区和资源信息
        if res.body.available_zones and res.body.available_zones.available_zone:
            for zone in res.body.available_zones.available_zone:
                # 只处理匹配的可用区
                if zone.zone_id != zone_id:
                    continue
                
                if zone.available_resources and zone.available_resources.available_resource:
                    for resource in zone.available_resources.available_resource:
                        if resource.supported_resources and resource.supported_resources.supported_resource:
                            for supported in resource.supported_resources.supported_resource:
                                # 检查资源状态是否可用
                                if supported.status == "Available" and supported.value:
                                    # 检查是否已存在
                                    existing = next((item for item in disk_types_info if item['value'] == supported.value), None)
                                    if not existing:
                                        disk_types_info.append({
                                            'value': supported.value,
                                            'min': supported.min,
                                            'max': supported.max
                                        })
        
        print(f"可用区 {zone_id} 的实例规格 {instance_type} 支持 {len(disk_types_info)} 种系统盘类型")
        return disk_types_info


    
    @staticmethod
    def _get_instance_type():
        # https://api.aliyun.com/api/Ecs/2014-05-26/DescribeAvailableResource 
        # 三种后付费实例类型 1,正常的按量付费 2,竞价实例  3,设置价格上限的抢占式实例 
        describe_available_resource_request = ecs_20140526_models.DescribeAvailableResourceRequest(
            region_id=ClientConf().region,
            destination_resource='InstanceType',
            instance_charge_type='PostPaid',
            spot_strategy='SpotAsPriceGo'
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            ClientConf().config.endpoint = f'ecs.{ClientConf().region}.aliyuncs.com'
            res=Ecs20140526Client(ClientConf().config).describe_available_resource_with_options(describe_available_resource_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            return res 
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
    
    def list_instance_types(self, zone_id=None):
        """
        列出可用的实例规格类型
        
        参数:
            zone_id: 可用区ID（可选），如果提供则只返回该可用区的实例规格
        
        返回:
            包含所有可用 instance_type 的列表
        """
        try:
            res = ECS._get_instance_type()
            if res is None:
                return []
            
            instance_types = []
            # 遍历可用区和资源信息
            if res.body.available_zones and res.body.available_zones.available_zone:
                for zone in res.body.available_zones.available_zone:
                    # 如果指定了 zone_id，则只处理匹配的可用区
                    if zone_id and zone.zone_id != zone_id:
                        continue
                    
                    if zone.available_resources and zone.available_resources.available_resource:
                        for resource in zone.available_resources.available_resource:
                            if resource.supported_resources and resource.supported_resources.supported_resource:
                                for supported in resource.supported_resources.supported_resource:
                                    if supported.value and supported.value not in instance_types:
                                        instance_types.append(supported.value)
            
            # 打印可用的实例类型
            if zone_id:
                print(f"可用区 {zone_id} 共找到 {len(instance_types)} 种可用实例规格:")
            else:
                print(f"共找到 {len(instance_types)} 种可用实例规格:")
            
            # for instance_type in sorted(instance_types):
            #     print(f"  - {instance_type}")
            
            return instance_types
            
        except Exception as error:
            print(f"获取实例规格失败: {str(error)}")
            if hasattr(error, 'data') and error.data:
                print(f"建议: {error.data.get('Recommend', '无')}")
            return []

    def _get_regions(self):
        # 列出阿里云所有可用的region id 和对应的 本地叫法  
        client = self.__client
        describe_regions_request = ecs_20140526_models.DescribeRegionsRequest(
            instance_charge_type='PostPaid',
            resource_type='instance'
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res=client.describe_regions_with_options(describe_regions_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            # 这里需要返回一个字典  key是 res的 body.Regions.Region.RegionId 然后value是 body.Regions.Region.RegionId 加上 body.Regions.Region.LocalName
            
            regions_dict = {}
            if res.body.regions and res.body.regions.region:
                for region in res.body.regions.region:
                    regions_dict[region.region_id] = f"{region.region_id} {region.local_name}"
            
            return regions_dict
            
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
            
    @staticmethod
    def get_zones():
        # 列出当前配置文件当中配置的region 当中有几个区域
        client_conf = ClientConf()
        client_conf.config.endpoint = f'ecs.{client_conf.region}.aliyuncs.com'
        client = Ecs20140526Client(client_conf.config)
        describe_zones_request = ecs_20140526_models.DescribeZonesRequest(
            region_id=client_conf.region,
            verbose=False,
            instance_charge_type='PostPaid'
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res=client.describe_zones_with_options(describe_zones_request, runtime)
            # print(json.dumps(res.to_map(), indent=2, ensure_ascii=False))
            # 这里需要返回一个字典  key是 Zones.Zone.ZoneId  他的value是  ZoneId 加 LocalName 加 ZoneType
            
            zones_dict = {}
            if res.body.zones and res.body.zones.zone:
                for zone in res.body.zones.zone:
                    zones_dict[zone.zone_id] = f"{zone.zone_id} {zone.local_name} {zone.zone_type}"
            
            return zones_dict
            
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)