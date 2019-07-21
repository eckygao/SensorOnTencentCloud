# SensorOnTencentCloud

本说明用于指导在线甲醛监测系统搭建

**缩写说明**

Rpi - Rapspberry Pi

## 最终效果

**终端展示**

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/rpi_1.png)

**云端展示**

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/yuntu_1.gif)

## 准备工作

### 设备准备

**硬件部分**

- Rpi（Rapspberry Pi 3B+）
- 传感器（UART 甲醛传感器）
- OLED（I2C OLED屏）

示例传感器 UART通信格式

| 字节顺序 | 说明 | 数值 |
| - | - | - |
| 0 | 起始位 | 0xFF |
| 1 | 气体名称 CH2O | 0x17 |
| 2 | 单位 ppb | 0x04 |
| 3 | 小数位数 | 0x00 |
| 4 | 气体浓度 高位 | 0x00 |
| 5 | 气体浓度 低位 | 0x25 |
| 6 | 满量程 高位 | 0x13 |
| 7 | 满量程 低位 | 0x88 |
| 8 | 校验值 | 0x25 |

**软件部分**

- Rpi操作系统（ [raspbian](https://www.raspberrypi.org/downloads/raspbian/) 使用 lite 版）
- 腾讯云账号 （ [腾讯云](https://cloud.tencent.com) ）

### 代码说明

**本地代码**

| 路径 | 说明 |
| - | - |
| client_package/ | 云API网关 SDK文件夹 |
| client_package/readme.md | SDK下载与使用说明 |
| data/* | 配置文件 | 
| lib/* | 封装库 |
| flusholed.py | OLED显示 |
| getdata.py | 传感器读取与数据记录 |
| init.sh | 环境初始化 安装依赖 |
| reload.sh | 计划任务 拉起异常退出进程 |
| sync_apigw.py | 同步数据上云 |

**云端代码**

| 路径 | 说明 |
| - | - |
| cloud/scf.py | 无服务器云函数 代码 |

**架构示意图**

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/demo_sotc_structure.png)

## 具体搭建

此环节分为三个部分：

- 终端搭建
- 云端搭建
- 终端上报云端联调

_注1: 无云端部分时，终端搭建完成后，即可进行本地监测_
_注2: 云端部分是通用接口，可按接口格式，上报并展示其它监测数据_

**核心接口格式**

获取云端最新数据时间戳

```
{
	'type':'getindex'
}
```

上报数据

```
{
	'type':'putdata',
	'data':
	[
		{'utime':12345678,'udata':0.01},
		{'utime':12345679,'udata':0.01},
		...
	]
}
```

_注：网络交互与签名，由API网关SDK实现，上述格式仅为核心数据部分。_

### 终端搭建

#### Rpi系统安装与环境准备

- 依照 [安装指引](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) 安装Rpi操作系统
- 对Rpi进行基础配置，使可接入互联网（具体方式请自行搜索）
- clone 代码至 Rpi (**路径可自定，此处示例为 /sotc 下同**)
- 执行 init.sh 安装 pymysql库、OLED操作库及APISDK依赖库

#### 硬件接线与配置

1. RPI GPIO图示

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/rpi_2.jpg)

2. 接线示意图

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/demo_sotc_rpi_gpio.png)

3. 接线说明

| 传感器 | Rpi |
| - | - |
| Pin4(5V) | Pin2(5V) |
| Pin3(GND) | Pin6(GND) |
| Pin6(UART-TxD) | Pin10(UART-RxD) |

_注：本次使用传感器，硬件接口是1.25mm端子，Rpi是2.5mm端子，使用了 7P1.25转2.5杜邦线，进行连接_

| OLED | Rpi |
| - | - |
| VCC | Pin1(3.3V) |
| SDA | Pin3(SDA) |
| SCL | Pin5(SCL) |
| GND | Pin9(GND) |

4. 开启I2C接口

按下图示意打开I2C接口

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/openi2c_1.png)
![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/openi2c_2.png)
![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/openi2c_3.png)

测试执行

```
i2cdetect -y 1
```

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/i2cdetect_1.png)

看到 3C 即识别硬件成功

_注：UART默认开启，无需配置_

#### 本地监测与展示

1. 本地测试

执行脚本

```
nptdate cn.ntp.org.cn
/sotc/getdata.py &
sleep 3
/sotc/flusholed.py &
```

此时OLED应有显示数据。

_注1：必须及时对时，避免时间偏差，影响数据可用性_

_注2：电化学传感器有预热时间，预热时间内数据不稳定_

2. 添加启动项

编辑 /etc/rc.local 

```
nptdate cn.ntp.org.cn
/sotc/getdata.py &
sleep 3
/sotc/flusholed.py &
```

3. 添加计划任务

编辑 /etc/crontab

```
*/1 * * * * root /sotc/reload.sh
```

此部分用于进程异常中止后的拉起。

_注：基于时间成本与应用环境考虑，未使用守护进程或服务形态_

### 云端搭建

#### 云数据库

访问 [云数据库 控制台](https://console.cloud.tencent.com/cdb) 建立库表

_表结构_

```sql
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `sensordata` (
  `id` int(11) NOT NULL,
  `stime` timestamp NULL DEFAULT NULL,
  `utype` int(11) NOT NULL DEFAULT '0',
  `udata` float NOT NULL,
  `sdata` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `sensordata`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `sensordata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;
```

| 字段 | 说明 |
| - | - |
| id | 自增主键 |
| stime | 监测时间 |
| udata | 监测数据 |
| utype | 监测类型（用于后续扩展） |
| sdata | 监测数据（用于后续扩展） |

#### 无服务器云函数

访问 [云函数 控制台](https://console.cloud.tencent.com/scf) 建立函数服务

- 新建服务
- 配置代码 （录入 cloud/scf.py 中代码）
- 配置触发方式 （选择API网关触发，配置内容见下节）
- 等待调用

_注：由于后续使用API网关触发，可后续联调_

#### 云API网关

访问 [API网关 控制台](https://console.cloud.tencent.com/apigateway) 配置网关服务，如由上节云函数部分配置触发，则API网关服务已经建立，仅需调整配置，以及下载使用API网关SDK。

具体操作可参考 client_package/readme.md

#### 腾讯云图

访问 [云图 控制台](https://console.cloud.tencent.com/yuntu) 配置展示部分

1. 使用说明

> 新建大屏 -\> 拖选组件 -\> 点击数据栏 -\> 选择数据库 -\> 填写SQL -\> 开启自动更新 -\> 预览 -\> 发布

2. 操作示例图

![](https://github.com/eckygao/SensorOnTencentCloud/blob/master/images/yuntu_2.png)

3. 组件配置信息

- 最新同步时间 - 通用文本

```
select concat('最新同步时间 ',stime) as value from sensordata order by id desc limit 1
```

- 国标系数比 - 水位图

```
select round((udata)/0.08*100, 2) as value from sensordata order by id desc limit 1
```

- 实时读数 - 基本条形图

```
select round(udata, 3) as x, '' as y from sensordata order by id desc limit 1
```

- 10分钟数据 - 基本折线图

```
select * from (select id, round(udata, 3) as y, date_format(stime, '%H:%i:%S') as x, utype as s from sensordata order by id desc limit 360) as t1 order by id asc
```

- 7天数据 - 基本折线图

```
select distinct (dt), round(AVG(udata),3) as y, dt as x, '0' as s from (select id, date_format(stime, '%Y-%m-%d %H') as dt, udata from sensordata order by id desc limit 604800) as t1 group by dt order by dt ASC
```

### 终端上报云端联调

1. 执行脚本

```
/sotc/sync_apigw.py
```

此时云数据库应新增数据，云图应有展示。

_注1：如积累数据量过大，API网关可能会有超时，但数据应该能正常录入。_

_注2：未进行分批上传的原因，也是时间成本与工作环境考量，可自行更改。_

2. 添加计划任务

编辑 /etc/crontab

```
*/1 * * * * root /sotc/sync_apigw.py
```

此部分用于每分钟同步数据。

