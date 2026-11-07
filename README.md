# 神舟 Z8-CU7NK · macOS Tahoe 安装与驱动记录

针对 **神舟 Z8-CU7NK / i7-10750H / RTX 2060 Mobile / 32 GB** 的 EFI、驱动运行文件、修改源码和 agent 操作资料。记录日期：2026-11-07。

这是同一台机器的实测资料，不是所有 Z8 系列笔记本通用的成品 EFI。公开配置已删除设备身份，必须先在本地填写自己的 SMBIOS。仓库不包含 macOS 安装镜像、苹果内核、系统文件、密码、SSH 密钥、无线网络预设或原始故障日志。

## 当前验证结果

| 项目 | 结果与边界 |
|---|---|
| 真机启动 | 关闭大量同步屏幕调试输出后，本轮成功进入桌面；尚未完成多次冷启动稳定性回归 |
| CPU | 系统识别 6 个物理核心、12 个逻辑线程；保留 `cpus=12` 和 `TSC_sync_margin=0` |
| Intel UHD 630 | 通过设备标识兼容配置，报告 Metal 3；内屏 1920×1080、144 Hz |
| RTX 2060 Mobile | 第三方 NullMoth 2.7.2 驱动，真机报告 Metal 3，外屏已实际点亮 |
| Type-C 外屏 | 真机报告渲染 3200×2000、逻辑 1600×1000 HiDPI、165 Hz；用户确认有正常画面 |
| NVIDIA 启动等待 | 100 秒固定等待已成功；50 秒仅写入待测，不能标成已验证 |
| 内置音频 | ALC293 + 自编译 VoodooHDA 3.6.8d1 曾验证扬声器和数字麦克风；**当前配置暂时停用**，没有完成与 RTX 同时启用的稳定性回归 |
| 键盘、触摸板、USB 鼠标 | 本机已能使用；USB 端口映射是本机专用 |
| 有线网络 | RealtekRTL8111 已工作，SSH 可用 |
| Intel 无线网络 | AX210 + itlwm / HeliPort；系统可能显示“以太网”，通过 HeliPort 搜索与连接 |
| 摄像头 | 内置 Chicony USB 摄像头，用户在 Photo Booth 确认有预览 |
| 蓝牙 | 当前相关 kext 关闭，没有交付可用性承诺 |
| HDR、CUDA、机器学习 | HDR 实验组件未安装；Metal 报告可用不等于 CUDA/PyTorch/MPS 或所有渲染程序均已验证 |
| 睡眠、唤醒、电池管理 | 不在本次已验证范围 |

**发布包还有一项单独的验证边界：** Lilu / VirtualSMC / 可选 VoodooHDA 的原始调试二进制含构建者本机路径，发布前移除了调试符号并重新 ad-hoc 签署；itlwm 的内嵌无线网络预设已清空并重新签署。脚本确认三个去符号驱动的 `__text` 指令段未改变、签名校验通过，但这些脱敏文件本身尚未再次真机启动。原机已成功的文件与公开脱敏产物不能混为同一次验证。

## 目录

```text
configs/       删除身份后的 EFI 配置模板
assets/        驱动和 EFI 压缩分卷，每卷不超过 32 MiB
manifests/     每卷、合并压缩包、展开文件的 SHA-256 及脱敏记录
sources/       固定版本上游源码、自编译源码与本地参考补丁
scripts/       校验、离线还原、生成私有配置和受控安装工具
docs/          硬件、安装、驱动构建、排错与发布边界
AGENTS.md      给自动化 agent 的工作规则
agent.md       agent 入口说明
local/         本地私有文件和还原产物，始终忽略提交
```

## 快速开始：仅准备文件，不修改系统

需要 Python 3.9+、完整克隆以及足够空间，展开运行库与源码建议预留 2 GB。

```bash
git clone git@github.com:qaz553286745/mac_shenzhou.git
cd mac_shenzhou
python3 scripts/verify.py
python3 scripts/assemble.py --output local/bundle
```

把 `docs/identity.example.json` 复制为 `local/identity.json`，使用你自己生成的 **MacBookPro16,1** SMBIOS 身份填写，不能借用他人的真实 Mac 序列号。然后生成私有配置：

```bash
python3 scripts/personalize.py --profile stable-sdr-100s \
  --identity local/identity.json --output local/config.plist
```

生成后用与本包对应的 **OpenCore 1.0.8 ocvalidate** 校验。仓库模板故意保留空序列号和全零 UUID/ROM，不能直接作为最终安装配置。

## 三个配置

| 模板 | 用途 | 验证情况 |
|---|---|---|
| `stable-sdr-100s.plist` | 核显 + RTX SDR + HiDPI，内置声卡关闭，固定等待 100 秒 | 原机成功启动基线；公开脱敏二进制另待回归 |
| `candidate-sdr-50s.plist` | 与基线相比仅增加 `nvrmsettle=50000` | 原机写入后尚未手动重启验证 |
| `recovery-igpu-audio-off.plist` | 在基线上加 `-nvoff -wegnoegpu`，优先用内屏排查 | 从成功基线派生的恢复候选；不是另一份已重复验证的配置 |

优先从 100 秒基线开始。50 秒成功后，也应分别检查冷启动、重启、外屏点亮和 HiDPI，不能只看一次进入桌面。

## 安装路线

先阅读 [安装说明](docs/INSTALL.md)，自动化操作还必须读取 [AGENTS.md](AGENTS.md)。

1. 用苹果官方完整安装程序准备安装介质；本仓库不提供系统镜像。
2. 核对主板、GPU、网卡和音频控制器；硬件不同就不要照搬 USB 映射和设备路径。
3. 完成私有 SMBIOS 配置，备份目标 EFI，保留可用的 Ubuntu/恢复入口。
4. Linux 只能部署 EFI。NVIDIA、Metal 运行库及音频 kext 的安装与内核集合更新在目标 macOS 中进行。
5. 用户已授权时才写盘；工具默认预览，明确 `--apply` 才执行。所有脚本均不重启机器、不格式化硬盘。
6. 由人在现场手动启动并验证，记录结果，不把静态校验当成启动成功。

## 为什么 NVIDIA 会倒计时 100 秒

本机驱动报告 BAR1 为 256 MB，并选择“BAR1 未重新安置”的保守分支，预留固定 100 秒。`85 s left` 表示已经等了约 15 秒，剩余 85 秒。成功那轮 `go(2)` 主要初始化仅 1874 ms，之后约 7 秒建立显示管线；这段倒计时不是该轮 GSP 超时。

`nvrmsettle=50000` 将固定等待改为 50 秒；它不减少 GSP 初始化和显示准备本身的时间。BAR1 是 CPU 可访问显存的窗口，RTX 2060 实际显存仍为 6 GB。不要为了压缩这个等待盲改 BIOS BAR 参数或强制复位 GPU。

## 重要排错结论

曾经出现停留白字、无 SSH 的启动失败。一次原始 stackshot 显示图形配置线程等待 `kernelmanagerd`，后者经过 X86PlatformPlugin / AppleSMC 进入 IOLog 与控制台打印路径。随后关闭 DebugEnhancer 注入与大量调试输出，真机成功进入桌面。**这支持“同步日志干扰启动”的排查方向，但单次快照不能证明所有历史失败都是同一个根因。**

声卡关闭后也发生过启动失败，因此没有把声卡定为唯一原因。当前先保留声卡关闭，后续恢复时单独做对照。

## 来源与许可

本项目是适配记录和分发整理，不声称这些第三方驱动由本仓库独立开发。NVIDIA 驱动来自 [nullmoth/nvidia-macos-driver](https://github.com/nullmoth/nvidia-macos-driver)，固定上游 `v2.7.2`，tag 对应提交 `18ba05f38b5eadea8b5ae05834bb51c61fb4c5c3`。这不是 NVIDIA 官方 macOS RTX 2060 驱动。

其他主要项目： [OpenCore](https://github.com/acidanthera/OpenCorePkg)、[Lilu](https://github.com/acidanthera/Lilu)、[VirtualSMC](https://github.com/acidanthera/VirtualSMC)、[WhateverGreen](https://github.com/acidanthera/WhateverGreen)、[CpuTscSync](https://github.com/acidanthera/CpuTscSync)、[itlwm / HeliPort](https://github.com/OpenIntelWireless)、[VoodooHDA](https://github.com/chris1111/VoodooHDA)。

第三方组件各自保留原许可；NullMoth 主项目采用 **PolyForm Noncommercial 1.0.0**，不能将整包重新标成 MIT 或承诺商业使用。NVIDIA 固件、Mesa、LLVM、VoodooHDA 等遵从各自附带许可。详见 [源码与许可说明](docs/SOURCES.md) 及展开后的 `rootfs/Library/NullMoth/licenses/`。
