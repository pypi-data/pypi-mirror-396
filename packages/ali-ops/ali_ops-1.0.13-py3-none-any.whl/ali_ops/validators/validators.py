import re


def validate_cidr_block(cidr: str) -> bool:
    """
    验证 CIDR 块格式是否正确 (例如: 10.10.1.0/24)
    
    Args:
        cidr: CIDR 块字符串
        
    Returns:
        bool: 格式正确返回 True，否则返回 False
    """
    if not cidr:
        return False
    
    # 匹配 x.x.x.x/x 格式
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$'
    match = re.match(pattern, cidr)
    
    if not match:
        return False
    
    # 验证 IP 地址的每个部分是否在 0-255 范围内
    ip_parts = [int(match.group(i)) for i in range(1, 5)]
    if not all(0 <= part <= 255 for part in ip_parts):
        return False
    
    # 验证子网掩码是否在 0-32 范围内
    prefix_length = int(match.group(5))
    if not 0 <= prefix_length <= 32:
        return False
    
    return True
