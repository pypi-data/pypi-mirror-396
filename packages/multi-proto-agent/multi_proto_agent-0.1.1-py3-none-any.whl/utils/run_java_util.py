import os
import jpype
import atexit

def get_jsonpath_result_by_java(json_string, jsonpath):
    if not jpype.isJVMStarted():
        jpype.startJVM(jpype.getDefaultJVMPath(),
                    "-Dfile.encoding=UTF-8",
                    f"-Djava.class.path={os.getcwd()}/tools/jsonpath-for-python-test-jar-with-dependencies.jar",
                    "--enable-native-access=ALL-UNNAMED",
                    )
    java_class_JsonpathUtil = jpype.JClass('com.digisky.JsonpathUtil')
    result = java_class_JsonpathUtil.getObjectByJsonpath(json_string, jsonpath)
    atexit.register(jpype.shutdownJVM)
    return result
if __name__ == '__main__':
    json = "{\"AllTaskList\":[{\"TaskType\":\"TASK_CHALLENGE\",\"TaskList\":[]},{\"TaskType\":\"TASK_DAILY\",\"TaskList\":[{\"TaskId\":21003,\"TaskCanBeReset\":true,\"TaskType\":\"TASK_DAILY\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"WhichWeek\":0},{\"TaskId\":21004,\"TaskCanBeReset\":true,\"TaskType\":\"TASK_DAILY\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"WhichWeek\":0},{\"TaskId\":21002,\"TaskCanBeReset\":true,\"TaskType\":\"TASK_DAILY\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"WhichWeek\":0},{\"TaskId\":21005,\"TaskCanBeReset\":true,\"TaskType\":\"TASK_DAILY\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"WhichWeek\":0}]},{\"TaskType\":\"TASK_SEASON\",\"TaskList\":[{\"TaskId\":22001,\"WhichWeek\":1,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false},{\"TaskId\":22002,\"WhichWeek\":1,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false},{\"TaskId\":22003,\"WhichWeek\":1,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false},{\"TaskId\":22004,\"WhichWeek\":2,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false},{\"TaskId\":22005,\"WhichWeek\":2,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false},{\"TaskId\":22006,\"WhichWeek\":2,\"TaskType\":\"TASK_SEASON\",\"TaskProgress\":0,\"TaskFinished\":false,\"TaskRewardClaimed\":false,\"TaskCanBeReset\":false}]},{\"TaskType\":\"TASK_ACTIVITY\",\"TaskList\":[]}]}"
    result = get_jsonpath_result_by_java(json,"$.AllTaskList[?(@.TaskList.length()>0)].TaskList[0].TaskId")
    print(result)
    print(type(result).__name__)
