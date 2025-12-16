

import fire 
import webbrowser
from .config.config import CONFIG
from .vpc.vpc import VPC 
from .ecs.ecs import ECS 
from .ecs.securityGroup import SECGROUP
from .ecs.ecsImage import IMG 


class ENTRY(object):
    """这是一个非官方的阿里云命令行工具
    
    这个工具的能力其实是非常简单的
    只能操作几个有限的资源 但是他有自己的优势
    就是操作非常简单 上手非常快 几乎没有心智负担 不用去记任何的参数
    """
    
    def __init__(self):
        # 使用装饰器创建VPC访问控制代理
        self.vpc = VPC()
        self.ecs = ECS()
        self.sgp= SECGROUP()
        self.config = CONFIG()
        self.imge = IMG() 
    
    def _open(self):
        """使用系统默认浏览器打开阿里云 API 文档"""
        webbrowser.open("https://api.aliyun.com/api/Ecs/")
    

def main() -> None:
    try:
        fire.Fire(ENTRY)
    except KeyboardInterrupt:
        print("\n操作已取消")
        exit(0)
    # except Exception as e:
    #     print(f"\n程序执行出错: {str(e)}")
    #     print("请检查您的输入参数或网络连接")
    #     exit(1)


