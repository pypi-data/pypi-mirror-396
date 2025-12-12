# robox-sdk-lite

# robox-sdk-lite目录结构


<https://github.com/PacoLijt/robox-sdk-lite>


\
```javascript

robox-sdk-lite
├── roio_proto.py           # RoIO协议和消息定义
├── roio_client.py          # RoIOClient类的实现， __main__方法实现了从stdin获取输入消息后publish出去的功能
├── roio_echo_client.py     # 实现了被publish到的消息的原样echo回去的RoIO Client实现样例
├── roio_pub_meter.py       # 以1000byte包大小，目标200Hz的频率publish的性能测试工具
├── roio_sub_meter.py       # 跑在roio_pub_meter.py对端接收和统计包数量的工具，pub_meter发送的数量跟sub_meter应该对上
├── roio_agent_mock.py      # 一个模拟RoIO Agent的类，用于测试RoIOClient， 纯本地模拟RoIO Agent收到pub消息后，发给订阅者，这里没有通过RoDN的传递消息的过程
├── Logger.py               # 日志功能依赖
├── __init__.py
└── UdpSocket.py            # UDP socket功能依赖
```


# 概述

robox-sdk-lite主要提供RoIOClient类，供用户开发与RoIO远程控制机器人交互的程序。

RoIOClient是一个面向实时通信场景设计的客户端类，主要用于与RoIO Agent建立UDP通信，对RoIO channel进行subscribe/unsubscribe，定期subscription的自动心跳保活， 并对接收到的publish消息，按用户定义的回调函数进行处理。适用于需要点对点实时交互的应用场景（如即时通讯、监控数据上报、机器人控制，游戏客户端等）。


下图展示了一个方向publish消息到另外一个方向的过程，只要通信双方约定好通道号(channelId)， 就能够实现相互发送消息，比如把从RCA到Robot方向的控制消息放到channelId==1, 把反方向的状态回报放到channel==2

或者按channelId区分控制的关节等。

```mermaidjs

sequenceDiagram
  participant A as RoIO-Client1<br>(Cust Controller)
  participant B as RoIO-Agent1<br>(RoCA)
  participant C as RoIO-Agent2<br>(RoBOX)
  participant D as RoIO-Client2<br>(Cust Robot Control Unit)
  autonumber
  B --> C: RoDN establish remote tunnel
  D -->> C: Subscribe to channel 0
  C -->> D: Subscribe Success
  A -->> B: publish to channel 0: [bytes]
  B -->> A: publish ack
  B -->> C: PUB channel 0: [bytes]
  C -->> D: publish channel 0: [bytes]
  D -->> C: publish ack
  
  
```


# SDK使用方法

## 安装和引入

通过pip安装

```python
pip install robox_sdk_lite
```

在python3代码通如下代码引入

```python
 from robox_sdk_lite.roio_client import RoIOClient
```


## 初始化RoIOClient


```python
`class RoIOClient(Thread):
    def __init__(self,
                 target: Tuple[str, int] = (os.getenv('ROIO_HOST', '127.0.0.1'), #target参数为roio_agent的udp端口 
                                         int(os.getenv('ROIO_PORT', '3333'))), 
                 max_queue_size: int = 5,  # 可配置的队列容量，一般不用动
                 udp_timeout: int = 1,  # 一般ROIO Client和Agent在局域网内, 响应时间一般不会超过1秒, 所以设置timeout为1秒
                 pub_no_ack = False  # 不用动
                 ):
```

一般全部按默认的来即可

```python
roio_cli = RoIOClient()  # 全部按默认参数来            
```

### RoIO相关环境变量

| 环境变量名 | 含义 | 默认值 |
|----|----|----|
| ROIO_HOST | RoIOClient连接的RoIO-Agent的Hostname或者IP地址 | 127.0.0.1 |
| ROIO_PORT | RoIOClient连接的RoIO-Agent的端口号 | 3333 |
| CH_ID | meter测试和echo测试用的channel号，收发两端要一致才能通信成功用户自己实现的RoIO-Client不需要依赖这个环境变量，可以自行选择0-255之间的通道号 | 0 |


## 通道(Channel)

RoIO支持0-255 256个通道，超过这个范围的channel_id会报错，通道类似于ROS里面的topic,是消息路由的逻辑区分单位，roio client通过订阅和发布到指定的通道进行通信

```python
#roio_proto.py

CHANNEL_RANGE=range(0x00, 0x100)   # 0-255
```

## Subscribe到通道


调用该方法后，本端RoIO Agent收到远端发来的对应Channel的消息后，会PUBLISH给Subsribed的RoIO Client

该调用成功返回True,否则返回False

该调用成功后，会把回调方法注册到RoIOClient对象内部数据结构，对象每次收到对应channel的消息就会调用回调进行处理。

同时，RoIOClient内部的订阅保活机制，也会保证每隔一定周期向roio_agent发送一次该channel的订阅保活，直到用户对该channel做了Unsuscribe解除订阅。

```python

class RoIOClient(Thread):
...
    def subscribe_to_channel(self, channel_id,    # 订阅的channel_id, 0-255
            callback:Optional[Callable[[int, RoIOMsg], None]]=None  # 收到订阅消息的处理回调方法，如果传None,
                                                                    # 会用默认的处理方式，只打印到sdout
         ):

        ...
```

### 订阅消息处理回调方法callback

这个方法传入了channel_id和消息的字节流，以下是样例

```python
    echo_client = RoIOClient()

    def echo_func(ch_id, bs):
        """"定义把消息原样发回去的行为"""
        logger.info(f"ECHO: {ch_id}, {bs}")
        # time.sleep(1)  # 延迟一会儿再echo
        echo_client.publish_to_channel(ch_id, bs)

    echo_client.subscribe_to_channel(CHANNEL_ID, echo_func)
    echo_client.start()  # 启动RoIOClient对象的处理线程
    ...
    echo_client.stop()   # 结束所有线程
```


## Unsubscribe通道

RoIOClient可以反订阅一条channel，这样以后就不会收到这个channel的消息

这个方法有幂等性，所以也可以用来探测roio_agent是否存活，比如判断机器人是否受控的时候，可以通过调用unsubscribe_to_channel(255)判断返回值是否为True测试

```python
class RoIOClient(Thread):
...
   def unsubscribe_to_channel(self, channel_id):
   ...
```

## Publish发布字节流到通道


调用该方法后，SDK会把消息PUBLISH给本端RoIO Agent, RoIO Agent负责发送给远端RoIO Agent， RoIO Agent再PUBLISH给subscribe在对应ChannelID上的远端RoIO Client


```python
 class RoIOClient(Thread):
...
    def publish_to_channel(self, 
    channel_id, 
    bs   #字节流，不要超过MTU, 一般最大大约是1400 BYTES上下
    ):
...
```


## Start/Stop RoIOClient对象

RoIOClient内部有3个线程，

* roio-msgloop线程负责udp socket消息的收发，
* roio-keepalive线程负责定期保活已有的subscribption
* roio-processor线程负责收到PUBLISH的消息调用用户注册的回调方法处理

需要通过start/stop函数来启动/停止所有线程， 注意停止后不能重新start，需要重新初始化一个RoIOClient对象再start