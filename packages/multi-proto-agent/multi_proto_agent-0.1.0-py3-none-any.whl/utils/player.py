import os
import queue
import time
import threading
from business.mahjong.python_protos.share import Base_pb2
from utils import translator
from utils.tcp_util import TcpClient
from utils.websocket_util import WebSocketClient
from utils.log_print_util import log_print
from utils.trace_id_util import generate_trace_id


class Player:
    """玩家类，封装玩家相关的所有属性和方法"""
    
    def __init__(self, account_id, role_name=None, role_uid=None, protocol_type='ws'):
        """初始化玩家对象
        Args:
            account_id: 账号ID
            role_name: 角色名称（可选）
            role_uid: 角色UID（可选）
            protocol_type: 协议类型，支持'tcp'和'websocket'（默认为'ws'）
        """
        self.rsp_queue = None
        self.account_id = account_id
        self.role_name = role_name
        self.role_uid = role_uid
        self.ap_address = None
        self.secret_key = None
        self.protocol_type = protocol_type.lower()
        if self.protocol_type not in ['tcp', 'ws', 'wss']:
            raise ValueError("协议类型必须是'tcp'、'ws'或'wss'")
        self.player_client = None
        self.list_of_mapping_of_req_and_trace_id = []
        self.exit_flag = False
        self.receiver_thread = None
        self.heartbeat_interval = int(os.environ.get('heartbeat_interval', 30))
    
    # 响应队列相关方法
    def get_rsp_queue(self):
        """获取响应队列"""
        return self.rsp_queue
    
    def set_rsp_queue(self, rsp_queue):
        """设置响应队列"""
        self.rsp_queue = rsp_queue
    
    # 账号ID相关方法
    def get_account_id(self):
        """获取账号ID"""
        return self.account_id
    
    def set_account_id(self, account_id):
        """设置账号ID"""
        self.account_id = account_id
    
    # 角色名称相关方法
    def get_role_name(self):
        """获取角色名称"""
        return self.role_name
        
    def set_role_name(self, role_name):
        """设置角色名称"""
        self.role_name = role_name
    
    # 角色UID相关方法
    def get_role_uid(self):
        """获取角色UID"""
        return self.role_uid

    def set_role_uid(self, role_uid):
        """设置角色UID"""
        self.role_uid = role_uid
    
    # 服务器地址相关方法
    def get_ap_address(self):
        """获取服务器地址"""
        return self.ap_address
    
    def set_ap_address(self, ap_address):
        """设置服务器地址"""
        self.ap_address = ap_address
    
    # 密钥相关方法
    def get_secret_key(self):
        """获取密钥"""
        return self.secret_key
    
    def set_secret_key(self, secret_key):
        """设置密钥"""
        self.secret_key = secret_key
    
    # 协议类型相关方法
    def get_protocol_type(self):
        """获取协议类型"""
        return self.protocol_type
    
    def set_protocol_type(self, protocol_type):
        """设置协议类型"""
        protocol_type = protocol_type.lower()
        if protocol_type not in ['tcp', 'ws', 'wss']:
            raise ValueError("协议类型必须是'tcp'、'ws'或'wss'")
        self.protocol_type = protocol_type
    
    # 玩家客户端相关方法
    def get_player_client(self):
        """获取玩家客户端"""
        return self.player_client
    
    def set_player_client(self, player_client):
        """设置玩家客户端"""
        self.player_client = player_client
    
    # 请求和追踪ID映射相关方法
    def get_list_of_mapping_of_req_and_trace_id(self):
        """获取请求和追踪ID的映射"""
        return self.list_of_mapping_of_req_and_trace_id
        
    def set_list_of_mapping_of_req_and_trace_id(self, list_of_mapping_of_req_and_trace_id):
        """设置请求和追踪ID的映射"""
        self.list_of_mapping_of_req_and_trace_id = list_of_mapping_of_req_and_trace_id
    
    # 根据请求消息名，获取最早的请求和追踪ID的映射，并从列表中移除
    def pop_earliest_trace_id_by_req_name(self, req_msg_name):
        """根据请求消息名，获取最早的请求和追踪ID的映射，并从列表中移除"""
        for mapping in self.list_of_mapping_of_req_and_trace_id:
            if req_msg_name in mapping:
                trace_id = mapping[req_msg_name]
                self.list_of_mapping_of_req_and_trace_id.remove(mapping)
                return trace_id
        return ""
    
    # 退出标志相关方法
    def get_exit_flag(self):
        """获取退出标志"""
        return self.exit_flag
    
    def set_exit_flag(self, exit_flag):
        """设置退出标志"""
        self.exit_flag = exit_flag
    
    # 接收线程相关方法
    def get_receiver_thread(self):
        """获取接收线程"""
        return self.receiver_thread
    
    def set_receiver_thread(self, receiver_thread):
        """设置接收线程"""
        self.receiver_thread = receiver_thread
    
    # 心跳间隔相关方法
    def get_heartbeat_interval(self):
        """获取心跳间隔"""
        return self.heartbeat_interval
    
    def set_heartbeat_interval(self, heartbeat_interval):
        """设置心跳间隔"""
        self.heartbeat_interval = int(heartbeat_interval)
    
    def connect(self, max_retry_times=3):
        """建立连接
        Args:
            address: 服务器地址，始终是字符串格式
            secret_key: 密钥
        Returns:
            bool: 连接是否成功
        """
        address = self.ap_address
        if not address:
            log_print(f"{self.account_id}警告：未指定服务器地址，连接失败。")
            return False
        secret_key = self.secret_key
        if not secret_key:
            log_print(f"{self.account_id}警告：未指定密钥，连接失败。")
            return False
        try:
            # 确保address是字符串格式
            if not isinstance(address, str):
                address = str(address)
                log_print(f"{self.account_id}警告：address不是字符串，已转换。")
            log_print(f"{self.account_id}使用提供的地址和密钥进行连接。")
            if self.protocol_type == 'tcp':
                log_print(f"{self.account_id}开始建立TCP连接。")
                # 解析TCP地址字符串为IP和端口
                try:
                    if ':' in address:
                        ip, port_str = address.rsplit(':', 1)
                        port = int(port_str)
                        tcp_address = (ip, port)
                    else:
                        log_print(f"{self.account_id}TCP地址格式错误，需要包含端口号。")
                        return False
                except ValueError:
                    log_print(f"{self.account_id}TCP地址解析失败：{address}")
                    return False
                # 使用get_tcp_connection获取封装的TcpClient实例
                self.player_client = TcpClient(length_prefix_bytes=int(os.environ.get('tcp_length_prefix_bytes', 2)))
                retry_times = 0
                while not self.player_client.is_connected and retry_times < max_retry_times:
                    self.player_client.connect(tcp_address)
                    if self.player_client and self.player_client.is_connected:
                        log_print(f"{self.account_id}TCP连接建立成功.")
                        self.rsp_queue = self.player_client.message_queue
                        # 启动心跳线程
                        self.start_heartbeat_thread()
                        break
                    retry_times += 1
                    time.sleep(1)
                if not self.player_client.is_connected:
                    log_print(f"{self.account_id}TCP连接建立失败，重试次数已达最大限制。")
                    return False
            elif self.protocol_type in ['ws', 'wss']:
                log_print(f"{self.account_id}开始建立WebSocket连接。")
                # 直接使用字符串格式的WebSocket地址
                ws_url = address
                # 如果地址不以ws://或wss://开头，添加ws://前缀
                if not ws_url.startswith(('ws://', 'wss://')):
                    ws_url = f"{self.protocol_type}://{ws_url}"
                self.player_client = WebSocketClient(length_prefix_bytes=int(os.environ.get('ws_length_prefix_bytes', 2)))
                retry_times = 0
                while not self.player_client.is_connected and retry_times < max_retry_times:
                    self.player_client.connect(ws_url, secret_key)
                    if self.player_client and self.player_client.is_connected:
                        log_print(f"{self.account_id}WebSocket连接建立成功.")
                        self.rsp_queue = self.player_client.message_queue
                        # 启动心跳线程
                        self.start_heartbeat_thread()
                        break
                    retry_times += 1
                    time.sleep(1)
                if not self.player_client.is_connected:
                    log_print(f"{self.account_id}WebSocket连接建立失败，重试次数已达最大限制。")
                    return False
            return True
        except Exception as e:
            log_print(f"{self.account_id}连接过程中发生异常：{e}")
            return False
    
    def send_request(self, req_msg_name, req_obj, is_heartbeat=False) -> bool:
        """发送请求"""
        try:
            if not is_heartbeat:
                trace_id = generate_trace_id()
                self.list_of_mapping_of_req_and_trace_id.append({req_msg_name: trace_id})
            else:
                trace_id = ""
            req_data = translator.handle_send_data(req_msg_name, req_obj, trace_id)
            if hasattr(self, 'player_client') and self.player_client and self.player_client.is_connected:
                # log_print(f"{self.account_id}将发送{self.protocol_type}请求 {req_msg_name}，trace_id={trace_id}: {translator.get_string_of_req_obj(req_obj)}")
                result = self.player_client.send(req_data)
                # if not is_heartbeat and result:
                #     log_print(f"{self.account_id}发送{self.protocol_type}请求{req_msg_name}，trace_id={trace_id}: {translator.get_string_of_req_obj(req_obj)}")
                return result
            else:
                log_print(f"{self.account_id}的{self.protocol_type}客户端未初始化或未连接，无法发送请求{req_msg_name}")
                return False
        except Exception as e:
            log_print(f"{self.account_id}发送{self.protocol_type}请求{req_msg_name} 异常: {e}")
            return False
    
    def receive_response(self):
        """接收响应"""
        try:
            rsp_data = self.rsp_queue.get(block=False)
            log_print(f"rsp_data:{rsp_data}")
            return rsp_data
        except queue.Empty:
            # 队列为空是正常的，继续循环
            return None
        except Exception as e:  # 捕获所有异常
            log_print(f"{self.account_id}接收响应异常：{e}")
            return None
    
    def tear_down(self):
        """清理资源"""
        log_print(f"{self.account_id}开始善后清理。。。")
        self.exit_flag = True
        
        # 等待心跳线程结束
        if hasattr(self, 'heartbeat_thread') and self.heartbeat_thread and self.heartbeat_thread.is_alive():
            try:
                # 设置超时时间，避免线程卡住导致无法退出
                self.heartbeat_thread.join(timeout=2.0)  # 等待最多2秒
                log_print(f"{self.account_id} 心跳线程已结束。")
            except Exception as e:
                log_print(f"{self.account_id} 等待心跳线程结束异常: {e}")
        
        if hasattr(self, 'player_client') and self.player_client:
            self.player_client.close()
            self.player_client = None
            log_print(f"{self.account_id}的{self.protocol_type}连接已关闭!")
        else:
            log_print(f"{self.account_id}的未建立{self.protocol_type}连接，无连接需关闭。")
        log_print(f"{self.account_id} 资源清理完成!")
    
    def start_heartbeat_thread(self):
        """启动心跳线程，固定间隔发送一次心跳包"""
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_thread_func)
        self.heartbeat_thread.daemon = True  # 设置为守护线程，主线程结束时自动退出
        self.heartbeat_thread.start()
        log_print(f"{self.account_id} 心跳线程已启动，每{self.heartbeat_interval}秒发送一次心跳包。")
    
    def _heartbeat_thread_func(self, heartbeat_class_name = "Base.ReqHeartbeat", heartbeat_obj = Base_pb2.ReqHeartbeat()):
        """心跳线程执行函数"""
        last_timestamp_of_heartbeat = int(time.time())  # 记录上次发送心跳的时间戳
        while not self.exit_flag and heartbeat_obj:
            try:
                current_timestamp = int(time.time())
                # 检查距离上一次发送心跳的时间差是否大于设置的心跳间隔
                if current_timestamp - last_timestamp_of_heartbeat >= self.heartbeat_interval:
                    req_obj = heartbeat_obj
                    self.send_request(heartbeat_class_name, req_obj, is_heartbeat=True)
                    last_timestamp_of_heartbeat = current_timestamp  # 更新上次发送时间
                # 无论是否发送心跳，都等待1秒再进入下一次循环
                time.sleep(1)
            except Exception as e:
                log_print(f"{self.account_id} 心跳线程执行异常: {e}")
                # 发生异常时短暂等待后继续尝试
                time.sleep(1)