import random
import string
# 生成指定长度的随机字符串，由数字和字母组成
def generate_random_string(length=6):
    """生成指定长度的随机字符串，由数字和字母组成"""
    characters = string.ascii_letters + string.digits  # 字母和数字
    return ''.join(random.choice(characters) for i in range(length))
# 生成指定Unicode范围的随机字符串
def generate_random_string_with_specific_unicode_range(unicode_ranges, length):
    sensitive_word_list = [
        "gm"
    ]
    try_times = 0
    while try_times < 5:
        random_string = ''
        for _ in range(length):
            # 随机选择一个Unicode范围
            unicode_range = random.choice(unicode_ranges)
            # 随机生成Unicode码，然后转换为字符
            random_char = chr(random.randint(unicode_range[0], unicode_range[1]))
            random_string += random_char
        does_contain_sensitive_word = False
        for sensitive_word in sensitive_word_list:
            if sensitive_word in random_string.lower():
                does_contain_sensitive_word = True
                break
        if does_contain_sensitive_word:
            try_times += 1
        else:
            return random_string
# 生成指定Unicode列表的随机字符串
def generate_random_string_with_specific_unicode_list(unicode_list, length):
    random_string = ''
    for _ in range(length):
        # 随机生成Unicode码，然后转换为字符
        random_char = chr(random.choice(unicode_list))
        random_string += random_char
    return random_string
# 生成符号字符串
def generate_symbol_string(length=2):
    symbol_unicode_ranges = [
        (0x0021, 0x002F), # 标点符号
        (0x003A, 0x0040), # 标点符号
        (0x005B, 0x0060), # 标点符号
        (0x007B, 0x007E)  # 标点符号
    ]
    return generate_random_string_with_specific_unicode_range(symbol_unicode_ranges, length)
# 生成简体中文字符串
def generate_simplified_chinese_string(length=2):
    # 简体中文的Unicode范围
    chinese_unicode_ranges = [(0x4E00, 0x9FFF)]
    return generate_random_string_with_specific_unicode_range(chinese_unicode_ranges, length)
# 生成繁体中文字符串
def generate_traditional_chinese_string(length=2):
    # 繁体中文的Unicode范围
    traditional_chinese_unicode_ranges = [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),
        (0x20000, 0x2A6DF)
    ]
    return generate_random_string_with_specific_unicode_range(traditional_chinese_unicode_ranges, length)
# 生成日语字符串
def generate_japanese_string(length):
    japanese_unicode_ranges = [
        (0x3040, 0x309F), # 平假名
        (0x30A0, 0x30FF), # 片假名
        (0x4E00, 0x9FCF)  # 汉字
    ]
    # 生成指定长度的日语文字字符串
    return generate_random_string_with_specific_unicode_range(japanese_unicode_ranges, length)
# 生成韩语字符串
def generate_korean_string(length):
    korean_unicode_ranges = [
        (0xAC00, 0xD7A3), # 韩文字母
        (0x4E00, 0x9FCF)  # 韩语使用的汉字
    ]
    return generate_random_string_with_specific_unicode_range(korean_unicode_ranges, length)
# 生成大写拉丁字母字符串
def generate_upper_latin_string(length):
    upper_latin_unicode_ranges = [
        (0x0041, 0x005A)
    ]
    return generate_random_string_with_specific_unicode_range(upper_latin_unicode_ranges, length)
# 生成小写拉丁字母字符串
def generate_lower_latin_string(length):
    lower_latin_unicode_ranges = [
        (0x0061, 0x007A)
    ]
    return generate_random_string_with_specific_unicode_range(lower_latin_unicode_ranges, length)
# 生成小写俄语西里尔字母字符串
def generate_lower_russian_cyrillic_string(length):
    lower_russian_cyrillic_unicode_ranges = [
        (0x0430, 0x044F)
    ]
    return generate_random_string_with_specific_unicode_range(lower_russian_cyrillic_unicode_ranges, length)

# 生成大写俄语西里尔字母字符串
def generate_upper_russian_cyrillic_string(length):
    upper_russian_cyrillic_ranges = [
        (0x0410, 0x042F)
    ]
    return generate_random_string_with_specific_unicode_range(upper_russian_cyrillic_ranges, length)
# 生成数字字符串
def generate_digit_string(length):
    digit_ranges = [
        (0x0030, 0x0039)
    ]
    return generate_random_string_with_specific_unicode_range(digit_ranges, length)
# 生成随机整数
def generate_random_int(min_value=0, max_value=100):
    """生成指定范围内的随机整数，默认为0-100"""
    return random.randint(min_value, max_value)
# 生成大写特殊拉丁字母字符串
def generate_upper_special_latin_string(length):
    upper_latin_unicode_list = [0x0178,0x0152,0x00DF,0x00DC,0x00DB,0x00DA,0x00D9,0x00D6,0x00D5,0x00D4,0x00D3,0x00D1,0x00CF,0x00CE,0x00CD,0x00CB,0x00CA,0x00C9,0x00C8,0x00C7,0x00C4,0x00C3,0x00C2,0x00C1,0x00C0]
    return generate_random_string_with_specific_unicode_list(upper_latin_unicode_list, length)
# 生成小写特殊拉丁字母字符串
def generate_lower_special_latin_string(length):
    lower_latin_unicode_list = [0x0153,0x00FF,0x00FC,0x00FB,0x00FA,0x00F9,0x00F6,0x00F5,0x00F4,0x00F3,0x00F1,0x00EF,0x00EE,0x00ED,0x00EB,0x00EA,0x00E9,0x00E8,0x00E7,0x00E4,0x00E3,0x00E2,0x00E1,0x00E0]
    return generate_random_string_with_specific_unicode_list(lower_latin_unicode_list, length)
# 生成半角转全角字符串
def halfwidth_to_fullwidth(halfwidth_str):
    return ''.join(chr(ord(c) + 0xFEE0) if 'a' <= c <= 'z' or 'A' <= c <= 'Z' else c for c in halfwidth_str)

# 生成指定长度的混合字符串（中文、拉丁字母、标点符号、数字）
def generate_mixed_string_with_length(target_length, char_types=None):
    """
    生成指定长度的混合字符串，包含随机的中文、拉丁字母、标点符号和数字
    所有字符统一按1个字符长度计算
    
    Args:
        target_length (int): 目标字符串长度
        char_types (list, optional): 指定要使用的字符类型列表，默认为None（使用所有类型）
            支持的字符类型：
            - 'chinese': 简体中文字符
            - 'upper_latin': 大写拉丁字母
            - 'lower_latin': 小写拉丁字母
            - 'symbols': 标点符号
            - 'digits': 数字字符
            示例：['chinese', 'digits'] 表示只使用中文和数字
        
    Returns:
        str: 生成的混合字符串
    """
    if target_length <= 0:
        return ""
    
    # 字符类型到生成函数的映射
    char_generators = {
        'chinese': generate_simplified_chinese_string,
        'upper_latin': generate_upper_latin_string,
        'lower_latin': generate_lower_latin_string,
        'symbols': generate_symbol_string,
        'digits': generate_digit_string
    }
    
    # 如果未指定字符类型，使用所有类型
    if char_types is None:
        char_types = list(char_generators.keys())
    
    # 如果字符类型列表为空，返回空字符串
    if not char_types:
        return ""
    
    result = ""
    
    # 生成字符直到达到目标长度
    while len(result) < target_length:
        # 从指定的字符类型中随机选择
        char_type = random.choice(char_types)
        # 通过映射获取对应的生成函数并调用
        if char_type in char_generators:
            result += char_generators[char_type](1)
    
    return result