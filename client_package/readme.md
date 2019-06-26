# 说明

这是你的SDK文件夹，需自行下载你的APISDK，放置于此文件夹。

下文以 __服务名__ 为 __sensor_data__ 的API服务为例，进行说明。

----

### 下载路径
 [API网关 控制台](https://console.cloud.tencent.com/apigateway/service) -> 点击 __服务名__ sensor_data -> 点击 __API文档/SDK__ -> 点击 __下载SDK__
 
### 相关操作

- 将SDK包中 __client_package__ 文件夹下内容，放置于此目录下
- 修改 api/sensor\_data_api.py 填写密钥信息

```
SecretId =  ""    #!!!!!!!在此填入SecretId!!!!!!!
SecretKey = ""    #!!!!!!!在此填入SecretKey!!!!!!
```

### 参考效果

文件夹结构

```
__init__.py
api_client.py
configuration.py
rest.py

api:
__init__.py
sensor_data_api.py

models:
__init__.py
```