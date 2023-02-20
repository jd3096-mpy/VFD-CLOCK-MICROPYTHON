## 固件

系统基于micropython 1.191 官方固件构建

## 错误代码

- ERROR:1  wifi连接错误
- ERROR:2  路由器无网络连接


## 文件结构
经过优化固定在三个文件，实际上更新系统也就是更新这三个文件，其他的不会改的库已经编译到固件里
- CLOCK.py CLOCK类
- tools.py 各类模块驱动
- main.py 主程序入口
  

以下py文件基本不会动，直接编译进固件
- font5x7.py fb字库文件，每个字符为5bytes
- ~~ota.py OTA升级~~   此库占用内存较大，已弃用
- bmp280.py  气压计驱动
- ~~ahtx0.py  aht20 便宜就是王道，传感器数据也就图一乐 勿较真~~  因为VFD发热较大，因此如果板载传感器误差很高，没有意义，需要的可以通过扩展接口自行延长线添加，这样可以保证测量结果准确
- ntptime.py  我改过的ntp，可支持支持全球24时区
- drivers.py  VFD、按键、蜂鸣器、蓝牙驱动，因为体积较大直接封进固件

以下为c模块添加进固件
- ~~import smartconfig~~  AIRKISS功能被废弃，但是此模块依然保留在固件中，感兴趣的可以自己试试AIRKISS，亲测可用

以下为json格式的设置文件
- config.vfd

## 屏幕API文档
使用了大佬**reboot93**的显示驱动。

https://github.com/Reboot93/MicroPython-8MD-06INKM-display-driver