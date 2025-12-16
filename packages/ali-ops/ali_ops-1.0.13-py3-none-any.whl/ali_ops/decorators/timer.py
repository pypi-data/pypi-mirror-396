
import time
import functools

class Timer:
    def __init__(self, func):
        self.func = func
        # 保持原函数的元数据
        functools.update_wrapper(self, func)
        self.call_count = 0
        self.total_time = 0
        
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        start_time = time.time()
        
        try:
            result = self.func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            self.total_time += execution_time
            print(f"{self.func.__name__} 执行时间: {execution_time:.4f}秒")
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'call_count': self.call_count,
            'total_time': self.total_time,
            'average_time': self.total_time / self.call_count if self.call_count > 0 else 0
        }

@Timer
def slow_function():
    time.sleep(1)
    return "完成"


if __name__=="__main__":
    slow_function()
    slow_function()
    print(slow_function.get_stats())
