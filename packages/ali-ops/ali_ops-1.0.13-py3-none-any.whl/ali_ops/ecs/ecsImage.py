
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import json
from datetime import datetime, timedelta
from ..client.client import ClientConf

class IMG:
    def __init__(self):
        # 使用 ClientConf 单例获取已配置好凭证的 config
        client_conf = ClientConf()
        if client_conf.config is None:
            print("配置文件不存在, 请使用ali config regen 命令生成配置文件。")
            self.__client = None
            return
        
        client_conf.config.endpoint = f'ecs.{client_conf.region}.aliyuncs.com'
        self.__client = Ecs20140526Client(client_conf.config)

    
    @staticmethod
    def _get_images():
        if ClientConf().config is None:
            print("ECS客户端未初始化，请先配置阿里云凭证")
            return
        
        ClientConf().config.endpoint = f'ecs.{ClientConf().region}.aliyuncs.com'
        client = Ecs20140526Client(ClientConf().config)
        # 计算三个月前的时间
        x_days_ago = datetime.utcnow() - timedelta(days=90)
        creation_start_time = x_days_ago.strftime('%Y-%m-%dT%H:%MZ')
        filter_0 = ecs_20140526_models.DescribeImagesRequestFilter(
            key='CreationStartTime',
            value=creation_start_time
        )
        describe_images_request = ecs_20140526_models.DescribeImagesRequest(
            region_id=ClientConf().region,
            status='Available',
            # ostype='linux',
            architecture='x86_64',
            image_owner_alias='system',
            is_support_io_optimized=True,
            is_support_cloudinit=True,
            action_type='CreateEcs',
            page_size=100,
            filter=[
                filter_0
            ]
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            res=client.describe_images_with_options(describe_images_request, runtime)
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
    def ls(platform="Ubuntu"):
        """
        列出指定平台的可用镜像
        
        Args:
            platform: 操作系统平台名称，如 "Ubuntu", "CentOS", "Debian" 等
        """
        res = IMG._get_images()
        if res is None:
            return
        
        # 获取镜像列表
        images = res.body.images.image if res.body and res.body.images else []
        
        # 筛选匹配指定平台的镜像
        matched_images = []
        for img in images:
            # 检查镜像名称或平台字段是否包含指定的平台关键字（不区分大小写）
            image_name = getattr(img, 'image_name', '') or ''
            platform_name = getattr(img, 'platform', '') or ''
            os_name = getattr(img, 'osname_en', '') or ''
            
            if platform.lower() in image_name.lower() or \
               platform.lower() in platform_name.lower() or \
               platform.lower() in os_name.lower():
                matched_images.append(img)
                # print(img)
        
        # 打印结果
        if not matched_images:
            print(f"未找到包含 '{platform}' 的镜像")
            return
        
        # 提取镜像ID和创建时间并排序
        image_info_list = [
            {
                'image_id': getattr(img, 'image_id', ''),
                'creation_time': getattr(img, 'creation_time', '')
            }
            for img in matched_images if getattr(img, 'image_id', '')
        ]
        image_info_list.sort(key=lambda x: x['creation_time'], reverse=True)
        
        print(f"\n找到 {len(image_info_list)} 个 {platform} 相关镜像:\n")
        for info in image_info_list:
            print(f"{info['image_id']} (创建时间: {info['creation_time']})")




    def _get_self_images():
        pass 