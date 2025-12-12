import threading
import time
import queue
import struct
from websocket import WebSocketApp, ABNF
from utils.log_print_util import log_print

class WebSocketClient:
    """WebSocket客户端类，封装WebSocket连接的所有操作"""
    
    def __init__(self, length_prefix_bytes=2):
        self.ws = None
        self.is_connected = False
        self.message_queue = queue.Queue()  # 消息队列，用于存储收到的消息
        self.exit_flag = False
        self.url = None
        self.headers = None
        self.length_prefix_bytes = length_prefix_bytes  # 长度前缀字节数，默认为0，0表示不处理长度前缀
    
    def connect(self, ws_url, secret_key=None):
        """建立WebSocket连接
        
        Args:
            ws_url (str): WebSocket服务器地址
            secret_key (str): 连接密钥
            headers (dict): 连接头信息
            auto_start_receiver (bool): 是否自动启动接收线程
            
        Returns:
            bool: 连接是否成功
        """
        self.url = ws_url
        self.headers = ["Connection: Upgrade",
                        "Upgrade: websocket",
                        "Sec-WebSocket-Version: 13",
                        f"Sec-WebSocket-Key: {secret_key}"]
        try:
            # 重置状态
            self.exit_flag = False
            
            # 创建WebSocket连接
            self.ws = WebSocketApp(
                self.url,
                # header=self.headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 创建独立线程用于建立WebSocket连接
            self.thread = threading.Thread(target=self._connect_and_listen)
            self.thread.daemon = True
            self.thread.start()
            
            # 等待连接建立，设置超时时间
            timeout = 3  # 3秒超时
            start_time = time.time()
            while not self.is_connected and time.time() - start_time < timeout:
                time.sleep(0.1)
                
            return self.is_connected
        except Exception as e:
            log_print(f"----WebSocket连接异常: {str(e)}")
            self.close()
            return False
    
    def _connect_and_listen(self):
        """在独立线程中建立连接并监听消息"""
        try:
            self.ws.run_forever(ping_interval=1.5, ping_timeout=0.5, ping_payload="ping")
        except Exception as e:
            if not self.exit_flag:
                log_print(f"----WebSocket监听异常: {str(e)}")
        finally:
            if not self.exit_flag:
                self.close()
    

    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        self.is_connected = True
        log_print(f"----WebSocket连接已打开")
    
    def _on_message(self, ws, message):
        """WebSocket接收消息回调"""
        if self.length_prefix_bytes > 0 and isinstance(message, bytes):
            # 如果设置了长度前缀且消息是二进制数据，则去掉长度前缀
            if len(message) >= self.length_prefix_bytes:
                # 从消息中去掉长度前缀
                actual_message = message[self.length_prefix_bytes:]
                self.message_queue.put(actual_message)  # 将去掉前缀后的消息放入队列
                # log_print(f"----WebSocket收到消息，去掉{self.length_prefix_bytes}字节长度前缀后: {actual_message}")
            else:
                # 消息长度不足，直接放入队列
                self.message_queue.put(message)
                # log_print(f"----WebSocket收到消息(长度不足，未去前缀): {message}")
        else:
            # 不需要处理长度前缀，直接放入队列
            self.message_queue.put(message)
            # log_print(f"----WebSocket收到消息: {message}")
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        if not self.exit_flag:
            log_print(f"----WebSocket错误: {str(error)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭回调"""
        if not self.exit_flag:
            log_print(f"----WebSocket连接关闭: code={close_status_code}, reason={close_msg}")
        self.is_connected = False
    
    def send(self, message_bytes:bytes):
        """发送消息到WebSocket服务器"""
        if not self.is_connected or self.ws is None:
            log_print("----WebSocket未连接，无法发送消息")
            return False
        try:
            # 处理字符串消息添加长度前缀
            if self.length_prefix_bytes > 0:
                # 添加长度前缀
                if self.length_prefix_bytes == 2:
                    length_prefix = struct.pack(">H", len(message_bytes))
                elif self.length_prefix_bytes == 4:
                    length_prefix = struct.pack(">I", len(message_bytes))
                else:
                    raise ValueError(f"不支持的长度前缀字节数: {self.length_prefix_bytes}")
                # 组合长度前缀和消息体
                full_message = length_prefix + message_bytes
                # log_print(f"----WebSocket发送消息的长度前缀: {length_prefix.hex()}")
                # log_print(f"----WebSocket发送消息(带长度前缀)，原始长度: {len(message_bytes)}，总长度: {len(length_prefix + message_bytes)}")
                # 以二进制形式发送
                self.ws.send(full_message, opcode=ABNF.OPCODE_BINARY)
                # log_print(f"----WebSocket发送消息(带长度前缀): {message_bytes.hex()}")
            else:
                # 不需要添加长度前缀，直接发送
                self.ws.send(message_bytes)
                # log_print(f"----WebSocket发送消息(不带前缀): {message_bytes.hex()}")
            return True
        except Exception as e:
            log_print(f"----WebSocket发送消息异常: {str(e)}")
            return False
    
    def send_binary(self, binary_data:bytes):
        """发送二进制数据到WebSocket服务器"""
        if not self.is_connected or self.ws is None:
            log_print("----WebSocket未连接，无法发送二进制数据")
            return False
        try:
            # 处理二进制数据添加长度前缀
            if self.length_prefix_bytes > 0:
                # 添加长度前缀
                if self.length_prefix_bytes == 2:
                    length_prefix = struct.pack(">H", len(binary_data))
                elif self.length_prefix_bytes == 4:
                    length_prefix = struct.pack(">I", len(binary_data))
                else:
                    raise ValueError(f"不支持的长度前缀字节数: {self.length_prefix_bytes}")
                # 组合长度前缀和二进制数据
                full_data = length_prefix + binary_data
                # 发送带长度前缀的二进制数据
                self.ws.send(full_data, opcode=ABNF.OPCODE_BINARY)
                log_print(f"----WebSocket发送二进制数据(带长度前缀)，原始长度: {len(binary_data)}，总长度: {len(full_data)}")
            else:
                # 不需要添加长度前缀，直接发送
                self.ws.send(binary_data, opcode=ABNF.OPCODE_BINARY)
                log_print(f"----WebSocket发送二进制数据，长度: {len(binary_data)}")
            return True
        except Exception as e:
            log_print(f"----WebSocket发送二进制数据异常: {str(e)}")
            return False
    
    def close(self):
        """关闭WebSocket连接"""
        if not self.exit_flag:
            self.exit_flag = True
            try:
                # 等待连接线程结束
                if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
                    self.thread.join(timeout=2)
                
                # 关闭WebSocket连接
                if self.ws:
                    self.ws.close()
                
                log_print("----WebSocket连接已关闭")
            except Exception as e:
                log_print(f"----WebSocket关闭异常: {str(e)}")
            finally:
                self.ws = None
                self.is_connected = False
                # 清理线程引用
                if hasattr(self, 'thread'):
                    self.thread = None


# def get_websocket_connection(ws_url, headers=None):
#     """创建并返回一个WebSocket连接"""
#     ws_client = WebSocketClient()
#     if ws_client.connect(ws_url, headers):
#         return ws_client
#     else:
#         ws_client.close()
#         raise Exception(f"Failed to establish WebSocket connection to {ws_url}")

if __name__ == "__main__":
    # 示例用法
    # 创建WebSocket客户端
    ws_client = WebSocketClient()
    
    # 这里需要替换为实际的WebSocket服务器地址
    # ws_url = "ws://echo.websocket.org"
    # ws_client.connect(ws_url)
    
    # 保持程序运行一段时间以接收消息
    # time.sleep(10)
    
    # 关闭连接
    # ws_client.close()