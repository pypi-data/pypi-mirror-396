class Logger:
    def __init__(self, cls):
        print(f"装饰器初始化: {cls.__name__}")
        self.cls = cls
        self.instances = []
    
    def __call__(self, *args, **kwargs):
        print(f"创建 {self.cls.__name__} 实例")
        instance = self.cls(*args, **kwargs)
        self.instances.append(instance)
        return instance

@Logger
class Person:
    def __init__(self, name):
        self.name = name
        print(f"Person 初始化: {name}")


if __name__=="__main__":
    p1 = Person("Alice")
    p2 = Person("Bob")
    print(p1.name, p2.name)
    print(Person.instances)
    