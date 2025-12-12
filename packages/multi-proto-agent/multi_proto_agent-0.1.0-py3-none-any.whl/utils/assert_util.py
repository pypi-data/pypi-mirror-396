from datetime import datetime
import json
import os
import sys

from utils.trace_id_util import send_trace_id
from utils.translator import handle_rsp_data
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from utils.player import Player
from utils import log_print_util
from jsonpath_ng import parse
from utils.run_java_util import get_jsonpath_result_by_java

class AssertResult:
    
    def __init__(self, is_player_pass=False, value_dict={}, assert_msg=""):
        self.is_player_pass = is_player_pass
        self.value_dict = value_dict
        self.assert_msg = assert_msg

    def get_is_player_pass(self):
        return self.is_player_pass
    
    def get_value_dict(self):
        return self.value_dict
    
    def get_assert_msg(self):
        return self.assert_msg

def _get_assertion_handlers():
    """
    获取断言处理器映射表
    
    Returns:
        dict: 断言类型到处理器函数的映射字典
    """
    return {
        '==': handle_equal_assertion,
        '!=': handle_not_equal_assertion,
        'in': handle_in_assertion,
        'notIn': handle_not_in_assertion,
        'isNone': handle_is_none_assertion,
        'isNotNone': handle_is_not_none_assertion,
        '>': handle_is_bigger_assertion,
        '<': handle_is_less_assertion,
        '>=': handle_is_not_less_assertion,
        '<=': handle_is_not_bigger_assertion,
        'isGot': handle_is_got,
        'isNotGot': handle_is_not_got
    }

def get_supported_assertions():
    """
    获取所有支持的断言类型
    
    Returns:
        list: 支持的断言类型列表
    """
    return list(_get_assertion_handlers().keys())

def get_assert_result(actual_value, expected_value, assertion_type):
    handler = _get_assertion_handlers().get(assertion_type)
    if handler and assertion_type in ['isNone', 'isNotNone']:
        return handler(actual_value)
    elif handler and assertion_type in ['isGot', 'isNotGot']:
        return handler()
    elif handler:
        return handler(actual_value, expected_value)
    else:
        log_print_util.log_print(f"{assertion_type}断言不存在")
        return False
    
def handle_is_not_got():
    # 只要该方法被调用，就说明收到了对应的消息，因此返回False
    return False

def handle_is_got():
    # 只要该方法被调用，就说明收到了对应的消息，因此返回True
    return True

def handle_is_not_bigger_assertion(actual_value, expected_value):
    if not actual_value:
        return False
    try:
        return float(actual_value) <= float(expected_value)
    except ValueError:
        log_print_util.log_print(f"转换为浮点数时出现异常！actual_value={actual_value}，expected_value={expected_value}")
        return False

def handle_is_not_less_assertion(actual_value, expected_value):
    if not actual_value:
        return False
    try:
        return float(actual_value) >= float(expected_value)
    except ValueError:
        log_print_util.log_print(f"转换为浮点数时出现异常！actual_value={actual_value}，expected_value={expected_value}")
        return False

def handle_is_bigger_assertion(actual_value, expected_value):
    if not actual_value:
        return False
    try:
        return float(actual_value) > float(expected_value)
    except ValueError:
        log_print_util.log_print(f"转换为浮点数时出现异常！actual_value={actual_value}，expected_value={expected_value}")
        return False
    
def handle_is_less_assertion(actual_value, expected_value):
    if not actual_value:
        return False
    try:
        return float(actual_value) < float(expected_value)
    except ValueError:
        log_print_util.log_print(f"转换为浮点数时出现异常！actual_value={actual_value}，expected_value={expected_value}")
        return False

def handle_in_assertion(actual_value, expected_value):
    if not actual_value:
        return False
    if not isinstance(expected_value, list):
        if isinstance(expected_value, int) or isinstance(expected_value, float):
            expected_value = str(expected_value)
        if isinstance(actual_value, int) or isinstance(actual_value, float):
            actual_value = str(actual_value)
        #     return expected_value in str(actual_value)
        # else:
        return actual_value.__contains__(expected_value)
    else:
        actual_set = set(actual_value)
        expected_set = set(expected_value)
        return expected_set.issubset(actual_set)
    # if isinstance(actual_value, dict):
    #     return expected_value in actual_value
    # if not isinstance(actual_value, str):
    #     temp_actual_value = str(actual_value)
    # else:
    #     temp_actual_value = actual_value
    # if not isinstance(expected_value, str):
    #     temp_expected_value = str(expected_value)
    # else:
    #     temp_expected_value = expected_value
    # return temp_expected_value in temp_actual_value

def handle_not_in_assertion(actual_value, expected_value):
    return not handle_in_assertion(actual_value, expected_value)
    
def handle_not_equal_assertion(actual_value, expect_value):
    return not handle_equal_assertion(actual_value, expect_value)
    
def handle_equal_assertion(actual_value, expect_value):
    try:
        type_of_expect_value = type(expect_value)
        converted_actual_value = type_of_expect_value(actual_value)
        return converted_actual_value == expect_value
    except ValueError:
        log_print_util.log_print(f"类型转换出错：actual_value={actual_value}，类型为{type(actual_value)}；expect_value={expect_value}，类型为{type_of_expect_value}")
        return False
    
def handle_is_none_assertion(actual_value):
    return actual_value is None

def handle_is_not_none_assertion(actual_value):
    return actual_value is not None

def is_player_passed_with_and_gate(player: Player, assertion_dict, trace_id="", trace_desc="", max_timeout=5, is_isNotGot_assertion=False) -> AssertResult:
    """
    一、支持的断言方式(不在以下方式之内的，统一返回False)：\n
    1、==，判断actual_value与expected_value的值是否相等\n
    2、!=，判断actual_value与expected_value的值是否不相等\n
    3、in，判断actual_value是否包含expected_value\n
    4、>，actual_value的值 > expected_value的值\n
    5、>=，actual_value的值 >= expected_value的值\n
    6、<，actual_value的值 < expected_value的值\n
    7、<=，actual_value的值 <= expected_value的值\n
    8、isNone，actual_value为空，此时expected_value可不传入\n
    9、isNotNone，actual_value不为空，此时expected_value可不传入\n
    10、notIn，判断actual_value不包含expected_value\n
    11、isGot，判断在max_timeout时间内是否有收到对应的消息,此时expected_value可不传入\n
    12、isNotGot，判断在max_timeout时间内是否一直没有收到对应的消息,此时expected_value可不传入\n
    二、提取响应参数\n
    根据jsonpath_of_value_to_get提取响应参数的值，将其赋值给name_of_value_to_get。\n
    三、示例：\n
    对RspMatchSuccceed消息，断言LevelServerAddr不为空，同时提取LevelServerAddr赋值给level_server_addr：\n
    assertion_dict = {
        "Match.RspMatchSuccceed": {
            # 断言规则列表
            "assertion_rule_list": [
                {
                    "json_path":"$.LevelServerAddr",
                    "expect_value":"",
                    "assertion_type":"isNotNone"
                }
            ],
            # 提取响应参数列表
            "value_to_get_list": [
                {
                    "jsonpath_of_value_to_get": "$.LevelServerAddr",
                    "name_of_value_to_get": "level_server_addr"
                }
            ]
        }
    }
    返回的assert_result，包括is_player_pass和value_dict:\n
    is_player_pass：以account_id为粒度的断言结果。\n
    value_dict：根据value_to_get_list提取的参数的dict，key为name_of_value_to_get。
    """
    rsp_queue = player.get_rsp_queue()
    account_id = player.account_id
    is_player_pass = False
    values_dict = {}
    expect_class_name_list = list(assertion_dict.keys())
    log_print_util.log_print(f"==============玩家{account_id}预期收到的消息：{expect_class_name_list}。")
    start_timestamp =  datetime.now().timestamp() * 1000
    assert_msg = ""
    while len(expect_class_name_list)>0 and (datetime.now().timestamp() * 1000 - start_timestamp <= max_timeout * 1000):
        if rsp_queue.empty():
            if is_isNotGot_assertion:
                is_player_pass = True
            assert_msg = "未收到任何消息！" if assert_msg == "" else assert_msg
            continue
        else:
            rsp_data = rsp_queue.get()
            rsp_msg = handle_rsp_data(rsp_data)
            # 如果handle_rsp_data返回None，跳过这条消息继续处理下一条
            if rsp_msg is None:
                assert_msg = "收到的消息无法解析！" if assert_msg == "" else assert_msg
                continue
            rsp_class_name = next(iter(rsp_msg.keys()))
            # 如果收到预期外的RspErrorCode，直接返回失败
            if rsp_class_name == "ClientCommon.RspErrorCode" and rsp_class_name not in expect_class_name_list:
                is_player_pass = False
                log_print_util.log_print(f"==============玩家{account_id}收到错误码：{rsp_msg}。")
                break
            # 将收到的消息与expect_class_name_list中的元素进行比对，如果是需要断言的消息，返回断言结果和提取的值，如果不是，则获取下一条，直到遍历所有元素或超时
            elif rsp_class_name not in expect_class_name_list:
                log_print_util.log_print(f"==============玩家{account_id}收到的不是预期的响应：{rsp_msg}，继续取下一条消息。")
                continue
            else:
                # 如果是需要断言的消息，从expect_class_name_list中删除对应消息，并遍历该消息所有断言规则，有一条不通过，则停止遍历，断言结果记录为不通过。
                log_print_util.log_print(f"==============玩家{account_id}收到需要断言的响应：{rsp_msg}，开始断言。。。。")
                expect_class_name_list.remove(rsp_class_name)
                assertion_rule_list = assertion_dict[rsp_class_name]["assertion_rule_list"]
                temp_result = True
                for assertion_rule in assertion_rule_list:
                    json_path = assertion_rule['json_path']
                    # logPrint.log_print(json_path)
                    expect_value = assertion_rule.get('expect_value', None)
                    # logPrint.log_print(expect_value)
                    assertion_type = assertion_rule['assertion_type']
                    # 如果是isGot或isNotGot断言，直接调用对应的处理方法
                    if assertion_type == 'isNotGot':
                        is_isNotGot_assertion = True
                        temp_result = get_assert_result(None, None, assertion_type)
                        is_player_pass = temp_result
                        if not temp_result:
                            assert_msg = f"{rsp_class_name}的断言失败，对应的断言规则是{assertion_rule}，预期是无法收到对应的消息，但实际收到了{rsp_class_name}：{rsp_msg[rsp_class_name]}。"
                            break
                    if "length()" in json_path or "@" in json_path:
                        jsonpath_result = get_jsonpath_result_by_java(rsp_msg[rsp_class_name], json_path)
                        if "net.minidev.json.JSONArray" == type(jsonpath_result).__name__:
                            actual_value = jsonpath_result[0] if len(jsonpath_result)>0 else None
                        else:
                            actual_value = jsonpath_result
                    else:
                        jsonpath_expr = parse(json_path)
                        matches = jsonpath_expr.find(json.loads(rsp_msg[rsp_class_name]))
                        if not matches:
                            actual_value = None
                        elif len(matches) == 1:
                            actual_value = matches[0].value
                        else:
                            actual_value = [match.value for match in matches]
                    temp_result = temp_result and get_assert_result(actual_value, expect_value, assertion_type)
                    if not temp_result:
                        assert_msg = f"{rsp_class_name}的断言失败，actual_value={actual_value}，类型为{type(actual_value)}；expect_value={expect_value}，类型为{type(expect_value)}；对应的断言规则是{assertion_rule}。"
                        break
                if temp_result:
                    assert_msg = f"{rsp_class_name}断言成功。"
                log_print_util.log_print(f"玩家{account_id}对{rsp_class_name}的断言结果：{assert_msg}")
                is_player_pass = temp_result
                # 断言通过的前提下，遍历value_to_get_list，获取所有需要提取的值，并以key:value的形式，在断言结果中返回。如果找不到对应的值，返回的value为None。
                value_to_get_list = assertion_dict[rsp_class_name].get("value_to_get_list")
                if is_player_pass and value_to_get_list and len(value_to_get_list)>0:
                    for value_to_get in value_to_get_list:
                        jsonpath_of_value_to_get = value_to_get["jsonpath_of_value_to_get"]
                        if "length()" in jsonpath_of_value_to_get or "@" in jsonpath_of_value_to_get:
                            jsonpath_result = get_jsonpath_result_by_java(rsp_msg[rsp_class_name], jsonpath_of_value_to_get)
                            if "net.minidev.json.JSONArray" == type(jsonpath_result).__name__:
                                values_dict[value_to_get["name_of_value_to_get"]] = jsonpath_result[0] if len(jsonpath_result)>0 else None
                            else:
                                values_dict[value_to_get["name_of_value_to_get"]] = jsonpath_result
                        else:
                            jsonpath_of_value_to_get_expr = parse(jsonpath_of_value_to_get)
                            matches = jsonpath_of_value_to_get_expr.find(json.loads(rsp_msg[rsp_class_name]))
                            values_dict[value_to_get["name_of_value_to_get"]] = matches[0].value if matches else None
    if len(expect_class_name_list)>0:
        assert_msg = f"{assert_msg}以下消息未收到：{expect_class_name_list}。"
    if is_isNotGot_assertion:
        is_player_pass = is_player_pass and len(expect_class_name_list)>0
    else:
        is_player_pass = is_player_pass and len(expect_class_name_list)==0
    if is_player_pass:
        log_print_util.log_print("==============玩家"+account_id+"断言成功："+assert_msg)
    else:
        trace_id_report_url = os.getenv('trace_id_report_url')
        if trace_id != "" and trace_id_report_url is not None and trace_id_report_url != "":
            response = send_trace_id(trace_id_report_url, trace_id, f"{trace_desc}玩家{account_id}断言失败：{assert_msg}")
            assert_msg = assert_msg + "已上报trace_id："+response.text
        log_print_util.log_print("==============玩家"+account_id+"断言失败："+assert_msg)
    assert_result = AssertResult(is_player_pass=is_player_pass, value_dict=values_dict, assert_msg=assert_msg)
    return assert_result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="断言工具")
    parser.add_argument("--list-assertions", action="store_true", help="列出所有支持的断言类型")
    
    args = parser.parse_args()
    
    if args.list_assertions:
        assertions = get_supported_assertions()
        print("当前支持的断言类型:")
        for assertion in assertions:
            print(f"  {assertion}")