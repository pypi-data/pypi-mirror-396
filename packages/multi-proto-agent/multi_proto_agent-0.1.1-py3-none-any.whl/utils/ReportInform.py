import os
import json
import yaml
import os
import json
import requests
import csv

# 获取结果数据
def getJsonData(filePath):
    fileName = "/history/history-trend.json"
    fullPath = filePath + fileName
    with open(fullPath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 提取结果
def getResult(data):
    if isinstance(data, list) and len(data) > 0:
        data_dict = data[0].get('data', {})
        failed = data_dict.get('failed', 0)
        passed = data_dict.get('passed', 0)
        total = data_dict.get('total', 0)
        return failed, passed, total
    else:
        return None, None, None

# 通知群机器人
def sendMsgToBot(web_hook_url, data):
    headers = {"Content-Type":"application/json"} 
    response = requests.post(web_hook_url, headers=headers, json=data) 
    return response    

def getErrorDetail(FilePath):
    FileName = '/data/behaviors.csv'
    FullPath = FilePath + FileName
    # 读取原始文件
    with open(FullPath, 'r', encoding='utf-8') as file:
        lines = csv.DictReader(file)
        result = []
        for row in lines:
            # 检查FAILED字段是否不为0
            if row['FAILED'] and row['FAILED'].strip() != '0':
                # 记录EPIC字段和FAILED字段的内容
                result.append({'EPIC': row['EPIC'], 'FAILED': row['FAILED']})
        epic_failed_dict = {}
        for item in result:
            epic = item['EPIC']
            failed = int(item['FAILED'])
            if epic in epic_failed_dict:
                epic_failed_dict[epic] += failed
            else:
                epic_failed_dict[epic] = failed
        # 打印结果
        result = [{'EPIC': key, 'FAILED': str(value)} for key, value in epic_failed_dict.items()]
        epic_failed_content = "   ".join([f"{item['EPIC']}: {item['FAILED']}" for item in result])
    return epic_failed_content

if __name__ == "__main__":
    with open('./data/report_url.yaml', 'r', encoding='utf-8') as f:
        url = yaml.safe_load(f)
    file_path_list = url['REPORTER_URL_LIST']
    # file_path = "C:\\Users\\niexuyang\\Desktop\\InterfaceTestReport\\report_2024_11_26-10_51"
    # file_path = r'\\192.168.61.175\wtshare\InterfaceTestReport\report_2024_11_21-20_25'
    test_plan_summary_list = url['TEST_PLAN_SUMMARY_LIST']
    test_env = url['TEST_ENV']
    test_env_name = url['TEST_ENV_NAME']
    destination_path = r'\\wt-qa-share.digi-sky.com\wtshare\InterfaceTestReport'
    content = f'<font color="info">{test_env_name}({test_env})接口测试完成，共进行{len(file_path_list)}轮测试，</font>请相关同事注意。'
    total_failed = 0
    for file_path in file_path_list:
        data = getJsonData(file_path)
        failed, passed, total = getResult(data)
        total_failed += failed
        # 生成报告地址
        folderName = os.path.basename(file_path)
        reportURL = os.path.join(destination_path, folderName).replace("\\", "\\\\")
        test_plan_summary = test_plan_summary_list[file_path_list.index(file_path)]
        if failed != 0:
            detail = getErrorDetail(file_path)
            error_detail = f'\n各模块失败数如下：<font color="warning">\n{detail}</font>'
        else:
            error_detail = ""
        rounds = file_path_list.index(file_path) + 1
        print(f"第{rounds}轮测试报告：{reportURL}/index.html")
        temp_content = f'---\n{rounds}、<font color="info">第{rounds}轮测试：{test_plan_summary}：</font>\n用例数:<font color=eecomment">{total}</font>\n通过:<font color="info">{passed}</font>\n失败:<font color="warning">{failed}</font>{error_detail}\n报告地址：{reportURL}/index.html'
        content = content+"\n"+temp_content
    body = {
    "msgtype": "markdown",
        "markdown": {
            "content": content+'\n---\n报告打开方式：右键Chrome浏览器，选择属性，添加目标启动参数"--allow-file-access-from-files"，访问报告地址。'
        }
    }
    web_hook_url_list = [
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b92a90c6-bc61-465f-a2e2-cbd09da92f1c",# QM组
        # "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=771522d9-819f-4665-a698-92cce2dd285a",# 大厅架构改造预研
    ]
    if total_failed !=0:
        for web_hook_url in web_hook_url_list:
            sendMsgToBot(web_hook_url, body)
    else:
        print("无失败用例，不需要发送。")