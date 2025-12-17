import os
import sys
import yaml
from utils.log_print_util import log_print


def add_python_protos_to_path():
    """将python_protos目录及其所有子目录添加到Python路径中"""
    python_protos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'python_protos')
    python_protos_path = os.path.abspath(python_protos_path)
    if os.path.exists(python_protos_path):
        # 添加python_protos根目录
        sys.path.append(python_protos_path)
        
        # 遍历python_protos下的所有子目录并添加到路径
        for item in os.listdir(python_protos_path):
            item_path = os.path.join(python_protos_path, item)
            if os.path.isdir(item_path):
                sys.path.append(item_path)

#这个方法用于读取protos_config.yaml文件，将其中的键值对设置为环境变量
def set_protos_config():
    # 读取proto的包名
    with open('./data/protos_config.yaml', 'r', encoding='utf-8') as f:
        protos_config_data = yaml.safe_load(f)
    for key, value in protos_config_data.items():
        os.environ[key] = value

def get_env_options():
    """获取环境选项列表，用于前端下拉选择框
    返回格式: [{"value": "env_key", "label": "env_name"}, ...]
    """
    try:
        with open('./data/test_config.yaml', 'r', encoding='utf-8') as f:
            env_data = yaml.safe_load(f)
        if not env_data or 'env' not in env_data:
            return []
        options = []
        for env_key, env_config in env_data['env'].items():
            env_name = env_config.get('env_name', env_key)
            options.append({"value": env_key, "label": env_name})
        return options
    except Exception as e:
        log_print(f"读取环境配置失败: {str(e)}")
        return []

def set_config(env_type):
    # 设置测试环境信息
    with open('./data/test_config.yaml', 'r', encoding='utf-8') as f:
        env_data = yaml.safe_load(f)
    if not env_type or env_type == "" or not env_data['env'].get(env_type):
        log_print("不是接口测试覆盖的环境，终止测试！")
        exit(0)
    # os.environ['env_type'] = env_type
    # 遍历cmd_env下的所有属性，并设置环境变量
    for key, value in env_data['env'][env_type].items():
        os.environ[key] = str(value)  # 确保值是字符串类型
    # 读取protos_config.yaml文件，将其中的键值对设置为环境变量
    set_protos_config()
