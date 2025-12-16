from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError

class customRegionCompleter(Completer):

    def __init__(self):
        self.regions = {
        # China Mainland
        "cn-shenzhen": "cn-shenzhen (深圳)",
        "cn-hangzhou": "cn-hangzhou (杭州)",
        "cn-beijing": "cn-beijing (北京)",
        "cn-shanghai": "cn-shanghai (上海)",
        "cn-qingdao": "cn-qingdao (青岛)",
        "cn-zhangjiakou": "cn-zhangjiakou (张家口)",
        "cn-huhehaote": "cn-huhehaote (呼和浩特)",
        "cn-wulanchabu": "cn-wulanchabu (乌兰察布)",
        "cn-chengdu": "cn-chengdu (成都)",
        "cn-heyuan": "cn-heyuan (河源)",
        "cn-guangzhou": "cn-guangzhou (广州)",
        "cn-fuzhou": "cn-fuzhou (福州)",
        "cn-wuhan-lr": "cn-wuhan-lr (武汉)",
        "cn-nanjing": "cn-nanjing (南京)",
        # Asia Pacific
        "ap-southeast-1": "ap-southeast-1 (新加坡)",
        "ap-southeast-3": "ap-southeast-3 (马来西亚吉隆坡)",
        "ap-southeast-5": "ap-southeast-5 (印度尼西亚雅加达)",
        "ap-southeast-6": "ap-southeast-6 (菲律宾马尼拉)",
        "ap-southeast-7": "ap-southeast-7 (泰国曼谷)",
        "ap-northeast-1": "ap-northeast-1 (日本东京)",
        "ap-northeast-2": "ap-northeast-2 (韩国首尔)",
        # US
        "us-east-1": "us-east-1 (美国弗吉尼亚)",
        "us-west-1": "us-west-1 (美国硅谷)",
        # Europe
        "eu-west-1": "eu-west-1 (英国伦敦)",
        "eu-central-1": "eu-central-1 (德国法兰克福)",
        
        "na-south-1": "na-south-1 (墨西哥)",
        "me-east-1": "me-east-1 (阿联酋迪拜)",
        
    }
        # 将字典转换为 (key, value) 元组列表供补全使用
        self.region_choices = list(self.regions.items())
        # print(self.region_choices)
    
    def get_completions(self, document: Document, complete_event):
        """实现模糊补全逻辑"""
        text = document.text_before_cursor.lower()
        
        for region, display in self.region_choices:
            # 模糊匹配：检查用户输入的字符是否按顺序出现在 region key 或 display 文本中
            if self._fuzzy_match(text, region.lower()) or self._fuzzy_match(text, display.lower()):
                yield Completion(
                    region,
                    start_position=-len(document.text_before_cursor),
                    display=display
                )
    
    def _fuzzy_match(self, pattern: str, text: str) -> bool:
        """模糊匹配算法：检查 pattern 中的字符是否按顺序出现在 text 中"""
        if not pattern:
            return True
        
        pattern_idx = 0
        for char in text:
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                pattern_idx += 1
        
        return pattern_idx == len(pattern)
    
    def get_valid_regions(self):
        """返回所有有效的区域名称列表"""
        return [region for region, _ in self.region_choices]


class customRegionValidator(Validator):
    """验证器：确保用户输入的区域名称有效"""
    
    def __init__(self, completer: customRegionCompleter):
        self.completer = completer
        self.valid_regions = completer.get_valid_regions()
    
    def validate(self, document: Document):
        """验证用户输入是否为有效的区域名称"""
        text = document.text.strip()
        
        if text and text not in self.valid_regions:
            raise ValidationError(
                message=f"无效的区域名称。请从补全列表中选择有效的区域。",
                cursor_position=len(text)
            )
    


if __name__ == "__main__":
    pass
