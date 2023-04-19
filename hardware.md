## 硬件清单
- 第一版豪华版：猛堆料，包括什么RGB灯，滚轮编码器，蜂鸣器，RTC，都上了，就为了验证哪些使用
- 第二版精简版：核心功能WIFI时钟，保留的只有拨动开关、光敏，屏幕用裸屏，成本最低，一块板子搞定、预留4pin接口
- 第三版早鸟版：还是保留了RTC电路，下部打算做低配高配双配置

## 硬件原理图

待确定稳定版后放出

## 硬件BOM

待确定稳定版后放出

## GPIO

| Function         | IO Pin | 备注                        |
| ---------------- | ------ | --------------------------- |
| RTC_Interrupt    | IO5    | PCF8563                     |
| 光敏电阻_ADC     | IO6    |                             |
| Button_1         | IO7    |                             |
| Button_2 (Boot)  | IO0    | 启动模式选择                |
| Button_3 (EN)    | N/A    | ESP32_RESET                 |
| Buzzer           | IO8    | 蜂鸣器                      |
| VFD_DIN (MOSI)   | IO9    |                             |
| VFD_CLK          | IO10   |                             |
| VFD_CS           | IO11   |                             |
| VFD_RESET        | IO12   |                             |
| VFD_EN           | IO13   | 需要拉高，拉高后给 VFD 供电 |
| RGB_LED (WS2812) | IO14   | 彩灯                        |
| I2C_SDA          | IO41   | 见下面 I2C 设备列表         |
| I2C_SCL          | IO42   | 见下面 I2C 设备列表         |

## I2C Addresses（只留了PCF8563）

| Device  | Address    | 备注            |
| ------- | ---------- | --------------- |
| PCF8563 | 81 (0x51)  | RTC             |
