# 硬件与驱动对应

| 硬件 | 本机记录 | 驱动/配置 |
|---|---|---|
| 笔记本 | Hasee 神舟 Z8-CU7NK，Insyde BIOS1.07.06wTHZX | MacBookPro16,1 SMBIOS 模型，身份必须自己生成 |
| CPU | Intel Core i7-10750H，Comet Lake-H，6C/12T | CpuTscSync1.1.2；cpus=12；TSC_sync_margin=0；SSDT-PLUG |
| 内存 | 32GB DDR4，BIOS曾显示2667MHz | 不需要独立 RAM 驱动 |
| 核显 | Intel UHD630，真实8086:9bc4 | spoof device-id3e9b；AAPL,ig-platform-id00009b3e；WhateverGreen1.7.1 |
| 独显 | NVIDIA GeForce RTX2060 Mobile，10de:1f15，TU106，6GB | NVRM/NVRMFB/NVAccel/NVRMAGDC2.7.2；NVIDIA615.78.08固件及对应 Metal/NVK 运行库 |
| 内屏 | 1920×1080，144Hz | Intel 驱动；不是 RTX 直连内屏方案 |
| 外屏 | 实测 Type-C，物理2560×1600、165Hz | 3200×2000渲染缓冲，逻辑1600×1000HiDPI；SDR |
| 内置声卡控制器 | Intel PCH HDA8086:06c8，PCI00:1f.3 | VoodooHDA3.6.8d1，当前通过设备IDffff暂不匹配 |
| 音频 codec | Realtek ALC293，codec0为10ec0293；另有Intel显示音频codec2 | 历史测试扬声器发声、数字麦克风电平变化；当前均暂时停用 |
| 有线网络 | Realtek RTL8111/8168系列 | RealtekRTL8111 3.0.4，不能当所有网卡通用驱动 |
| 无线网络 | Intel AX210 | itlwm2.3.0 + HeliPort；公开包无网络密码预设 |
| 蓝牙 | AX210对应USB蓝牙8087:0032 | IntelBluetoothFirmware / IntelBTPatcher / BlueToolFixup当前关闭 |
| 内置键盘 | PS/2 | VoodooPS2Controller2.3.7及键盘插件 |
| 触摸板 | I2C HID，具体面板芯片不在本记录的已确认清单 | VoodooI2C2.9.1 + GPIO/Services/Input + VoodooI2CHID |
| 摄像头 | Chicony内置USB摄像头 | Apple UVC；Photo Booth曾看到画面 |
| 存储 | NVMe SSD，macOS位于独立约4TB盘，另盘保留Linux | NVMeFix1.1.3；不公开序列号、分区UUID |
| USB | 本机定制HaseeUSBMap1.0，外接鼠标曾位于HS06、蓝牙位于HS08 | 不要在不同主板/不同端口布局上当通用映射 |

EFI还包含Lilu1.7.2自定义有界日志重试、VirtualSMC1.3.8带边界标记、RestrictEvents1.1.6。禁用项目仍可能随EFI二进制包保留，以配置Enabled为准；不能看到文件就认定已加载。

## BIOS

本机照片曾确认：SATA Mode=AHCI、SGX=Disabled、UEFI OS Fast Boot=Disabled；VT-d当时为Enabled。使用当前EFI的映射器相关quirk，不把VT-d是否开启视为所有故障的解释。

使用UEFI启动。Secure Boot、CSM等项目需按实际菜单核对，不猜测隐藏菜单。未找到CFG Lock可见选项，当前配置保留相关兼容处理；禁止运行未知setup_var偏移或刷改BIOS解锁。不要为了NVIDIA倒计时盲目打开/强制调整Resizable BAR。
