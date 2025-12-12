import hashlib
from collections import OrderedDict
import importlib
import os
from google.protobuf import json_format 
from utils.log_print_util import log_print
from business.mahjong.python_protos.share.Base_pb2 import BaseMsg, TraceInfo


def get_api_signature(nonce, body):
    SortedBody = OrderedDict(sorted(body.items()))
    Data = []
    for key, value in SortedBody.items():
        Data.append(str(key))
        Data.append(str(value))
    Data.append("dafjsdkaljfasdlkjg")
    Data.append(nonce)
    DataStr = ''.join(Data)
    Signature = hashlib.md5(DataStr.encode()).hexdigest()
    return Signature


def deserialize_proto_object(proto_msg_name, bytes_data):
    try:
        module_name, class_name = proto_msg_name.rsplit('.', 1)
        proto_package = os.environ.get(module_name, "")
        # log_print(f"反序列化{proto_msg_name}，模块名：{module_name}，类名：{class_name}, 包名：{proto_package}")
        # Dynamic import module
        module = importlib.import_module(proto_package)
        # Get msg class
        proto_class = getattr(module, class_name)
        # Parse msg
        proto_instance = proto_class()
        proto_instance.ParseFromString(bytes_data)
        return proto_instance
    except Exception as e:
        log_print(f"{proto_msg_name}反序列化异常: {e}")
    return None 

def handle_send_data(proto_msg_name, obj_to_send, trace_id=""):
    serialized_proto_obj_data = obj_to_send.SerializeToString()
    BaseMsg_obj = BaseMsg(
        MsgName=proto_msg_name,
        MsgBody=serialized_proto_obj_data,
        TraceInfo=TraceInfo(sTraceID=trace_id)
    )
    serialized_base_msg_data = BaseMsg_obj.SerializeToString()
    # 对BaseMsg_obj序列化后的数据进行base64编码
    # ReqData = base64.b64encode(ReqData)
    return serialized_base_msg_data

def handle_rsp_data(rsp_data):
    # 对rsp_string进行base64解码
    # decode_bytes = base64.b64decode(rsp_string)
    # log_print(rsp_data)
    BaseMsg = deserialize_proto_object("Base.BaseMsg", rsp_data)
    if BaseMsg is None:
        log_print("警告: BaseMsg 反序列化失败，返回空响应")
        return None
        
    proto_obj_recieved = deserialize_proto_object(BaseMsg.MsgName, BaseMsg.MsgBody)
    if proto_obj_recieved is None:
        log_print(f"警告: {BaseMsg.MsgName} 反序列化失败，返回空响应")
        return None
    
    # proto to string
    json_string = json_format.MessageToJson(proto_obj_recieved, ensure_ascii=False, always_print_fields_with_no_presence=True)
    rsp_msg = {BaseMsg.MsgName: json_string, "trace_id": BaseMsg.TraceInfo.sTraceID}
    return rsp_msg

def get_string_of_req_obj(req_obj):
    return json_format.MessageToJson(req_obj, ensure_ascii=False, always_print_fields_with_no_presence = True)