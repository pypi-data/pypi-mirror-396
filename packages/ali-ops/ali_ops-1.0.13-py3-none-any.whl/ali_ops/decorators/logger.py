
import pprint

class LogDecorator:
    def __init__(self, log_level="INFO", prefix=""):
        """初始化装饰器参数"""
        self.log_level = log_level
        self.prefix = prefix
        print(f"步骤1: 装饰器初始化，参数: level={log_level}, prefix={prefix}")


    def __call__(self, cls):
        """装饰器被调用，接收目标类"""
        print(f"步骤2: 装饰器调用，接收类: {cls.__name__}")
        pprint.pprint(cls.__dict__, indent=2, width=80)
        pprint.pprint(dir(cls), indent=2, width=80)
        
        # 保存原始的__init__方法
        original_init = cls.__init__
        
        # 捕获装饰器实例的属性
        decorator_prefix = self.prefix
        decorator_log_level = self.log_level
        
        def new_init(instance, *args, **kwargs):
            print(f"{decorator_prefix}[{decorator_log_level}] 创建 {cls.__name__} 实例")
            original_init(instance, *args, **kwargs)
        
        # 替换__init__方法
        cls.__init__ = new_init
        
        # 添加新方法
        def log_method(instance, message):
            print(f"{decorator_prefix}[{decorator_log_level}] {cls.__name__}: {message}")
        
        cls.log = log_method
        
        print(f"步骤3: 类装饰完成，返回修改后的类")
        return cls

# 使用装饰器
@LogDecorator(log_level="DEBUG", prefix=">>> ")
class User:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, I'm {self.name}"


if __name__=="__main__":
    user = User("Alice")
    user.log("用户已创建")
    print(user.greet())  # 输出: "Hello, I'm Alice


