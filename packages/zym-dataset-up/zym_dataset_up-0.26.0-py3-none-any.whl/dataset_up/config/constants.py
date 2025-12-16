import os 

VERSION = "0.26.0"
NAME = "zym-dataset-up"

# 默认的配置路径
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), f".{NAME}")

# 默认配置文件名称
DEFAULT_CLI_CONFIG_FILE_NAME = "config.json"

DEFAULT_CLI_TOKEN_FILE_NAME = "token.json"

# version
DEFAULT_CLI_VERSION_FILE_NAME = "version.json"


AK_ENV_NAME = "DATASET_UP_SDK_AK"
SK_ENV_NAME = "DATASET_UP_SDK_SK"


#SERVER_URL = "http://120.92.51.36:31801/api/sdk-srv/v5/api/data/sdkService/"
#TASK_URL = "http://120.92.51.36:31801/api/sdk-srv/v5/api/data/sdkService/operate/"
#GET_TOKEN_URL = "http://120.92.51.36:31801/api/user-srv/userAccessKey/v1/getAccessToken"

#SERVER_URL = "http://127.0.0.1:8081/api/data/sdkService/"
#GET_TOKEN_URL = "http://120.92.51.36:31801/api/user-srv/userAccessKey/v1/getAccessToken"


#SERVER_URL = "http://platform-aiintegration-dev.baai.ac.cn/api/sdk-srv/v5/api/data/sdkService/"
#TASK_URL = "http://platform-aiintegration-dev.baai.ac.cn/api/sdk-srv/v5/api/data/sdkService/operate/"
#GET_TOKEN_URL = "http://platform-aiintegration-dev.baai.ac.cn/api/user-srv/userAccessKey/v1/getAccessToken"


SERVER_URL = "https://platform-aiintegration-mutitest.baai.ac.cn/api/sdk-srv/v5/api/data/sdkService/"
TASK_URL = "https://platform-aiintegration-mutitest.baai.ac.cn/api/data-bff/sdkService/v5/"
GET_TOKEN_URL = "https://platform-aiintegration-mutitest.baai.ac.cn/api/user-srv/userAccessKey/v1/getAccessToken"


#SERVER_URL = "https://www.beaicloud.com/api/sdk-srv/v5/api/data/sdkService/"
#TASK_URL = "https://www.beaicloud.com/api/data-bff/sdkService/v5/"
#GET_TOKEN_URL = "https://www.beaicloud.com/api/user-srv/userAccessKey/v1/getAccessToken"

#SERVER_URL = "https://platform-aiintegration-dx2.baai.ac.cn/api/sdk-srv/v5/api/data/sdkService/"
#GET_TOKEN_URL = "https://platform-aiintegration-dx2.baai.ac.cn/api/user-srv/userAccessKey/v1/getAccessToken"


UPLOAD_URL = "upload/"
OPERATE_URL = "operate/"

TIMEOUT = (20, 30)
UPLOAD_TIMEOUT = (60, None)

