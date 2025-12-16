
class MyDecorator:
    def __init__(self, func):
        """初始化时接收被装饰的函数"""
        self.func = func
        
    def __call__(self, *args, **kwargs):
        """使实例可调用，实现装饰逻辑"""
        print("装饰器执行前")
        result = self.func(*args, **kwargs)
        print("装饰器执行后")
        return result

# 使用装饰器
@MyDecorator
def hello(name):
    print(f"Hello, {name}!")

# 等价于: hello = MyDecorator(hello)



