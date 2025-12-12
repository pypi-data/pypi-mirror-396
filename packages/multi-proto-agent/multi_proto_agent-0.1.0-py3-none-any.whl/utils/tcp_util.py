import os
import socket
import struct
import threading
import queue
import time
import socket
from utils.log_print_util import log_print


class TcpClient:
    """TCP客户端类，封装TCP连接的所有操作"""
    
    def __init__(self, length_prefix_bytes=2):
        self.socket = None
        self.is_connected = False
        self.server_address = None
        self.receive_thread = None
        self.message_queue = queue.Queue()
        self.exit_flag = False
        self.on_message_callback = None
        self.on_error_callback = None
        self.on_close_callback = None
        self.length_prefix_bytes = length_prefix_bytes  # 长度前缀字节数，默认为2，0表示持续接收
        
    def connect(self, address, timeout=5, auto_start_receiver=True):
        """建立TCP连接
        
        Args:
            address (tuple): 服务器地址和端口，格式为(ip, port)
            timeout (int): 连接超时时间（秒）
            auto_start_receiver (bool): 是否自动启动接收线程
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 重置状态
            self.exit_flag = False
            
            # 保存服务器地址
            self.server_address = address
            
            # 创建TCP/IP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 设置超时
            self.socket.settimeout(timeout)
            
            # 连接到服务器
            self.socket.connect(address)
            
            # 连接成功后设置一个合理的超时，避免接收线程永久阻塞
            self.socket.settimeout(1.0)  # 1秒超时

            # 自动启动接收线程
            if auto_start_receiver:
                self.start_receive_thread()
            self.is_connected = True
            log_print(f"----TCP连接成功: {address[0]}:{address[1]}")
            return True
        except Exception as e:
            log_print(f"----TCP连接异常: {str(e)}")
            self.close()
            return False
    
    def start_receive_thread(self):
        """启动接收线程"""
        if self.is_connected and self.socket and not self.receive_thread:
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            log_print("----TCP接收线程已启动")
    
    def _receive_loop(self):
        """接收消息的主循环，在单独线程中运行"""
        
        while not self.exit_flag and self.is_connected and self.socket:
            
            try:
                # 尝试接收消息（带超时）
                data = self.receive_with_header()
                if data:
                    # 将消息放入队列
                    self.message_queue.put(data)
                    log_print(f"----TCP消息已放入队列，长度: {len(data)}")
                    
                    # 调用回调函数（如果设置了）
                    if self.on_message_callback:
                        try:
                            self.on_message_callback(data)
                        except Exception as e:
                            log_print(f"----TCP消息回调异常: {str(e)}")
                elif self.socket is None or not self.is_connected:
                    # 连接已关闭，退出循环
                    break
            except socket.timeout:
                # 超时异常，继续循环
                continue
            except Exception as e:
                log_print(f"----TCP接收循环异常: {str(e)}")
                # 调用错误回调（如果设置了）
                if self.on_error_callback:
                    try:
                        self.on_error_callback(e)
                    except Exception as ex:
                        log_print(f"----TCP错误回调异常: {str(ex)}")
                # 发生异常时退出循环
                break
        
        # 接收线程结束时的清理
        if not self.exit_flag:
            self.close()
            # 调用关闭回调（如果设置了）
            if self.on_close_callback:
                try:
                    self.on_close_callback()
                except Exception as e:
                    log_print(f"----TCP关闭回调异常: {str(e)}")
        
        self.receive_thread = None
        log_print("----TCP接收线程已停止")
    
    def send(self, data):
        """发送数据到TCP服务器
        
        Args:
            data (bytes): 要发送的数据
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_connected or self.socket is None:
            log_print("----TCP未连接，无法发送数据")
            return False
        try:
            if self.length_prefix_bytes > 0:
                # 添加指定字节数的长度前缀（大端序）
                if self.length_prefix_bytes == 2:
                    length_prefix = struct.pack(">H", len(data))
                    log_print(f"----TCP需发送数据长度: {len(data)}")
                    log_print(f"----TCP发送数据长度前缀(2字节): {length_prefix}")
                elif self.length_prefix_bytes == 4:
                    length_prefix = struct.pack(">I", len(data))
                    log_print(f"----TCP需发送数据长度: {len(data)}")
                    log_print(f"----TCP发送数据长度前缀(4字节): {length_prefix}")
                else:
                    raise ValueError(f"不支持的长度前缀字节数: {self.length_prefix_bytes}")
                full_data = length_prefix + data
            else:
                # 如果长度前缀为0，则直接发送数据
                full_data = data
            self.socket.sendall(full_data)
            log_print(f"----TCP发送的数据: {full_data}")
            log_print(f"----TCP发送数据成功，长度: {len(full_data)}")
            return True
        except Exception as e:
            log_print(f"----TCP发送数据异常: {str(e)}")
            self.close()
            return False
    
    def receive_all(self, expected_length) -> bytes:
        """从TCP服务器接收指定长度的数据
        
        Args:
            expected_length (int): 期望接收的数据长度
            
        Returns:
            bytes: 接收到的数据，如果连接关闭或发生错误则返回None
        """
        if not self.is_connected or self.socket is None:
            log_print("----TCP未连接，无法接收数据")
            return None
        
        try:
            data = b""
            while len(data) < expected_length:
                chunk = self.socket.recv(expected_length - len(data))
                if not chunk:  # 连接被关闭
                    log_print("----TCP连接已关闭")
                    self.close()
                    return None
                data += chunk
            log_print(f"----TCP接收完整数据成功，长度: {len(data)}")
            return data
        except Exception as e:
            log_print(f"----TCP接收完整数据异常: {str(e)}")
            self.close()
            return None
    
    def receive_with_header(self) -> bytes:
        """接收带有长度前缀的数据
        
        Returns:
            bytes: 接收到的实际数据，如果连接关闭或发生错误则返回None
        """
        if self.length_prefix_bytes == 2:
            data_length = struct.unpack(">H", self.length_prefix_bytes)[0]
        elif self.length_prefix_bytes == 4:
            data_length = struct.unpack(">I", self.length_prefix_bytes)[0]
        else:
            log_print(f"----不支持的长度前缀字节数: {self.length_prefix_bytes}")
            return None
        return self.receive_all(data_length)
    
    def _receive_until_timeout(self):
        """持续接收数据，直到1秒内没有新数据
        
        Returns:
            bytes: 接收到的所有数据，如果连接关闭或发生错误则返回None
        """
        if not self.is_connected or self.socket is None:
            log_print("----TCP未连接，无法接收数据")
            return None
        
        try:
            all_data = b""
            last_receive_time = time.time()
            
            # 设置socket超时为0.1秒，这样可以定期检查是否超时
            original_timeout = self.socket.gettimeout()
            self.socket.settimeout(0.1)
            
            while time.time() - last_receive_time < 1.0 and not self.exit_flag:
                try:
                    chunk = self.socket.recv(8192)
                    if chunk:
                        all_data += chunk
                        last_receive_time = time.time()
                    else:
                        # 连接被关闭
                        log_print("----TCP连接已关闭")
                        self.close()
                        break
                except socket.timeout:
                    # 超时，继续检查是否达到1秒无数据
                    continue
                except Exception as e:
                    log_print(f"----TCP接收数据块异常: {str(e)}")
                    break
            
            # 恢复原始超时设置
            self.socket.settimeout(original_timeout)
            
            if all_data:
                log_print(f"----TCP持续接收数据成功，总长度: {len(all_data)}")
            return all_data if all_data else None
        except Exception as e:
            log_print(f"----TCP持续接收数据异常: {str(e)}")
            self.close()
            return None
    
    def close(self):
        """关闭TCP连接"""
        # 设置退出标志
        self.exit_flag = True
        
        # 等待接收线程结束（如果正在运行）
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2.0)  # 最多等待2秒
            
            
        if self.socket is not None:
            try:
                self.socket.close()
                log_print("----TCP连接已关闭")
            except Exception as e:
                log_print(f"----TCP关闭异常: {str(e)}")
            finally:
                self.socket = None
                self.is_connected = False
                self.receive_thread = None
    
    def get_is_connected(self):
        """获取连接状态
        
        Returns:
            bool: 当前连接状态
        """
        return self.is_connected
    
    def set_callbacks(self, on_message=None, on_error=None, on_close=None):
        """设置回调函数
        
        Args:
            on_message (callable): 接收到消息时的回调函数，参数为data
            on_error (callable): 发生错误时的回调函数，参数为exception
            on_close (callable): 连接关闭时的回调函数，无参数
        """
        self.on_message_callback = on_message
        self.on_error_callback = on_error
        self.on_close_callback = on_close
        
    def queue_size(self):
        """获取消息队列的大小
        
        Returns:
            int: 队列中的消息数量
        """
        return self.message_queue.qsize()


# def get_tcp_connection(address, timeout=5):
#     """创建并返回一个TCP连接
#     Args:
#         address (tuple): 服务器地址和端口，格式为(ip, port)
#         timeout (int): 连接超时时间（秒）
#     Returns:
#         TcpClient: TCP客户端实例，已连接到服务器
#     Raises:
#         Exception: 当连接失败时抛出异常
#     """
#     tcp_client = TcpClient(length_prefix_bytes=int(os.environ.get('length_prefix_bytes', 2)))
#     if tcp_client.connect(address, timeout):
#         return tcp_client
#     else:
#         raise Exception(f"Failed to establish TCP connection to {address[0]}:{address[1]}")

if __name__ == "__main__":
    # 示例用法
    try:
        # 这里需要替换为实际的服务器地址
        # server_address = ('127.0.0.1', 8080)
        # tcp_socket = get_tcp_connection(server_address)
        # print("TCP连接成功")
        # 
        # # 发送测试数据
        # tcp_socket.send(b"Hello TCP!")
        # 
        # # 接收响应
        # response = tcp_socket.recv(1024)
        # print(f"接收到响应: {response}")
        # 
        # # 关闭连接
        # tcp_socket.close()
        
        print("TCP工具类测试完成")
    except Exception as e:
        print(f"测试失败: {e}")