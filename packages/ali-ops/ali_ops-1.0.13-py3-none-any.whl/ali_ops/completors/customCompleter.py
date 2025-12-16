from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class CustomCompleter(Completer):
    """自定义补全器，支持从外部传入字典数据"""

    def __init__(self, choices: dict[str, str]):
        """
        初始化补全器
        :param choices: 补全选项字典，格式为 {key: display_text}
        """
        self.choices = choices
        self.choice_items = list(choices.items())

    def get_completions(self, document: Document, complete_event):
        """实现模糊补全逻辑"""
        text = document.text_before_cursor.lower()

        for key, display in self.choice_items:
            if self._fuzzy_match(text, key.lower()) or self._fuzzy_match(text, display.lower()):
                yield Completion(
                    key,
                    start_position=-len(document.text_before_cursor),
                    display=display
                )

    def _fuzzy_match(self, pattern: str, text: str) -> bool:
        """模糊匹配：检查 pattern 中的字符是否按顺序出现在 text 中"""
        if not pattern:
            return True

        pattern_idx = 0
        for char in text:
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                pattern_idx += 1

        return pattern_idx == len(pattern)

    def get_valid_keys(self) -> list[str]:
        """返回所有有效的 key 列表"""
        return list(self.choices.keys())


class CustomValidator(Validator):
    """验证器：确保用户输入的值有效"""

    def __init__(self, completer: CustomCompleter, error_msg: str = "无效的输入，请从补全列表中选择。"):
        self.completer = completer
        self.valid_keys = completer.get_valid_keys()
        self.error_msg = error_msg

    def validate(self, document: Document):
        """验证用户输入是否有效"""
        text = document.text.strip()

        if text and text not in self.valid_keys:
            raise ValidationError(
                message=self.error_msg,
                cursor_position=len(text)
            )



if __name__ == "__main__":
    from prompt_toolkit import prompt

    # 示例字典数据
    test_choices = {
        "apple": "apple (苹果)",
        "banana": "banana (香蕉)",
        "cherry": "cherry (樱桃)",
        "orange": "orange (橙子)",
    }

    completer = CustomCompleter(test_choices)
    validator = CustomValidator(completer, error_msg="请从水果列表中选择")

    result = prompt("请选择水果: ", completer=completer, validator=validator)
    print(f"你选择了: {result}")
