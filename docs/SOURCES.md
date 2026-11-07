# 源码、构建与发布边界

## 固定版本与职责

| 组件 | 用途 | 本包来源/状态 |
|---|---|---|
| OpenCore1.0.8 | UEFI引导、ACPI、设备属性、内核兼容配置 | EFI来自原机读取；不带个人config和NVRAM |
| Lilu1.7.2 | kext运行时补丁基础 | sources/Lilu-1.7.2-retry，增加最多12次、有界重试的磁盘转储；发布二进制去调试路径、重签 |
| VirtualSMC1.3.8 | 真机SMC仿真 | sources/VirtualSMC-1.3.8-boundary，增加T/M/S初始化边界标记；发布二进制去调试路径、重签 |
| WhateverGreen1.7.1 | 核显framebuffer及相关兼容 | EFI中包含，按模板加载 |
| CpuTscSync1.1.2 | 多核时钟同步兼容 | cpus=12与TSC_sync_margin=0来自本机工作配置 |
| NullMoth NVIDIA2.7.2 | RTX资源管理、framebuffer、加速与显示控制 | 上游tag v2.7.2 + 本地已验证SDR二进制；运行文件逐项哈希列于manifests |
| itlwm2.3.0 | Intel无线网络，配HeliPort | 清空WiFiConfig后重新签署，未发布个人网络 |
| VoodooHDA3.6.8d1 | 内置HDA控制器与ALC293 | 可选历史版本，当前关闭；源码保留诊断标记，未包含未安装的codec-mask改动 |

## NVIDIA代码与二进制不是一个未经修改的上游包

`sources/nvidia-v2.7.2/`是固定tag原始源码，tag提交为`18ba05f38b5eadea8b5ae05834bb51c61fb4c5c3`。其中自己的AGENTS.md及许可必须保留。

`sources/local-patches/`保存HiDPI属性保留补丁、scanout参考实现和SMC边界补丁。本地NVRMFB/NVAccel/NVRMAGDC发布产物来自HDR实验前保留的SDR版本，包含HiDPI/scanout与遥测隔离相关适配。默认运行包排除了HDR进程补丁、HDR候选与VM重启guard。

不要仅凭“版本号都是2.7.2”宣称从tag直接重建就逐字节等于本包。部分本地构建快照没有形成完整可复现的单一提交；仓库提供原始源码、参考修改和**确切发布二进制的SHA-256**，没有把这一缺口隐藏成可复现构建声明。后续应把本地差异整理为可审阅补丁，再做干净构建与实机回归。

四个核心二进制基线SHA-256：

```text
NVRM     29ac457487623fb6ec4d85fbb9e73f75e8e2c05ab53ef120f4ef739039705341
NVRMFB   567ef9f4d50c2587a4953074dac089419007810b2d74b043ba84975e734d93f3
NVAccel  3780bcd65db81dc3323faa244dee029298e333292f88fd00105256133feb2b64
NVRMAGDC 7ead8efd1ae3eb9702fdceed2ad1006ddb699e19b380ac466870fa99a146018d
```

## 如何自己构建

在另行指定的Mac构建机中使用已正确安装的Xcode/Command Line Tools与匹配SDK、内核头文件；先阅读各source目录README和build脚本。不要自动替用户接受Xcode许可。

Lilu与VirtualSMC保留对应Xcode项目；本地参考构建曾使用CLT、x86_64、fapple-kext及对应版本的Kernel SDK。VoodooHDA源码为传统内核扩展，必须链接目标系统匹配的IOAudioFamily/IOPCIFamily等接口，不能通过编译就自动适配任意新内核。

NVIDIA上游构建还依赖NVIDIA open-gpu-kernel-modules615.78.08、Mesa/NVK、Metal翻译与LLVM/Vulkan运行库。按固定版本获取依赖，保留各自许可。Turing TU106使用匹配的tu10x固件，不能把其他架构固件当成“更新驱动”任意替换。

为避免泄露构建目录，应在编译时使用`-ffile-prefix-map`/`-fdebug-prefix-map`等选项，并在发布前检查符号字符串。重新签署、删除符号或改变Info.plist都会改变哈希；确认指令段未变也不能替代开机验证。

## 许可与未收录内容

上游源码中的LICENSE/NOTICE和运行包`Library/NullMoth/licenses`均保留。NullMoth主项目为PolyForm Noncommercial1.0.0；LLVM、Mesa、NVIDIA固件和开源内核模块等按其自身条款处理，VoodooHDA包含其原许可。本仓库没有授予超出原许可的新权利。

未收录：苹果内核/KDK/系统二进制、完整macOS镜像、个人磁盘镜像、原始panic/stackshot、SSH凭据、FileVault信息、QEMU Apple SMC OSK、个人屏幕照片和聊天记录。

分卷只是为遵守GitHub单文件尺寸限制，不是加密或隐藏内容；每卷、合并包与展开结果均可校验。
