---
type: note
created: 2026-07-22
source: Gemini 对话导出(2026-07-22,经 AI Exporter 保存;技术内容均为 AI 转述,未交叉核实)
checkable: true
verified: false
tags: [技术, 车机, Android, HMI, CAN]
---

# 车机技术基础——View、Android 框架、CAN 总线与网关隔离

HMI 设计师视角的技术底层扫盲:这些是设计稿背后系统真正运行的方式。

## View 是什么

View = UI 上一个视图组件/图层块。按钮、卡片(Aicy)、地图都是 View。在 Android 中所有显示元素都继承自 `android.view.View`。层级冲突(如 Aicy 卡片遮挡地图弹框)的本质是**Z 轴渲染优先级**问题:两个 View 的 elevation/z 值谁高谁压着谁。MVC/MVVM 架构里 View 只管显示和接收交互,不管数据和逻辑。

## 车机为什么用 Android

- **AAOS(Android Automotive OS)**:Google 专为汽车设计,可直接接入 CAN 总线控制硬件;代表:沃尔沃、极星、凯迪拉克。
- **AOSP 深度定制**:车企在开源底层上自建 Launcher 和 UI;代表:**Flyme Auto**(星纪魅族/吉利)、鸿蒙、蔚来/小鹏/理想。

选 Android 的原因:UI 渲染能力强(SurfaceFlinger/View System)、开发生态成熟、开源可随意裁剪。

车机通常双系统:安全驾驶部分(仪表/刹车/ADAS)用 **QNX 或实时 Linux**;中控娱乐屏用 **Android**。

## CAN 总线

CAN(Controller Area Network)= 车内各电子控制单元(ECU)互相通信的专用"局域网"。

- **广播机制**:发送方向总线广播,所有监听者自取所需——车速传感器广播"60 km/h",车门模块、空调、EPS 转向、音响、气囊各自按逻辑独立响应。
- **优先级仲裁**:刹车(高优先级)和空调(低优先级)同时发送→刹车先走,保行车安全。
- 车里通常多条 CAN 分域:动力域、底盘域、座舱域等,域间靠**网关**互联。

**车速信号触发了什么**:
- 底盘/安全:车门落锁(>15 km/h)、EPS 减少助力(方向盘变沉)、气囊调整触发阈值、悬架降低车身、大灯拉远焦距。
- 座舱域(车机):禁用全键盘/视频等高危操作;导航视角拉远;随速音量补偿(SCVC);仪表盘精简突出车速/限速。

## 网关(Central Gateway)

网关 ≠ CAN 总线。CAN 是"路",网关是"门"——独立 ECU,同时接多条域总线,是跨域数据的唯一枢纽。

隔离手段:
- **白名单**:只允许座舱域发特定指令(调温/开窗等),非法指令直接丢弃。
- **加密认证(SecOC)**:重要报文须带数字签名,密钥不对即拦截。
- **速率限制**:防软件 bug 或攻击狂发垃圾包堵总线,异常流量立即限流隔离座舱域。
- **单向只读**:车速等数据可流入车机展示,车机无法逆向修改底层传感器值。

座舱域接收车速信号同样须经网关——网关既是安全墙,也是整车状态数据(车速/档位/门窗)的唯一交通枢纽。

## 复核记录

- 2026-07-26:支持。关键技术陈述均查有可靠来源:AAOS 直连车辆 ECU/CAN 总线且不经手机投屏,代表车型 Volvo(XC40 Recharge)/Polestar(Polestar 2 为首发)/Cadillac(Lyriq)属实;CAN 总线仲裁"数值越小的标识符优先级越高、逐位竞争、非破坏性仲裁"机制准确;域架构(动力域/底盘域/座舱域等)经网关互联、网关作为跨域数据唯一枢纽的描述准确;SecOC(Secure Onboard Communication)用于报文签名认证、ECU 白名单(进程签名/端口白名单)、车速>15km/h 触发车门自动落锁(Kia/Hyundai/Honda/Genesis 等厂商说明书印证)、EPS 转向助力随车速联动等均有据可查。唯一未找到直接来源佐证的细节:NIO/小鹏/理想是否严格基于 AOSP 深度定制(搜索仅确认小鹏采用 ACCESS Twine 等第三方方案,未直接证实 AOSP 归属),这一点存疑但不影响整体结论。来源:https://grokipedia.com/page/Android_Automotive ,https://www.hms-networks.com/tech-blog/blogpost/hms-blog/2024/06/18/what-is-can-arbitration-and-how-does-this-work ,https://www.einfochips.com/blog/what-is-central-gateway-module-and-its-significance-in-automotive-world/ ,https://www.linkedin.com/pulse/secure-on-board-communication-automotive-sandeep-nagarajan ,https://ownersmanual.kia.com/full_webhelp/KA4KH/2026/en_US/topics/chapter5_5_6.html ,https://link.springer.com/article/10.1007/s42154-023-00266-9 。下次复核约 180 天后(2027-01 前后)。
