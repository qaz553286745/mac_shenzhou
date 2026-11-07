# 安装与恢复

## 0. 安装对象与版本

适用记录：Z8-CU7NK，i7-10750H/UHD630/RTX2060Mobile/ALC293，OpenCore1.0.8，macOS Tahoe Darwin25.6.0（本次机器报告build25G332）。不要把同一商品名的不同主板视为相同硬件。新机器先读 HARDWARE.md 和 AGENTS.md。

本包是引导/驱动资料，不是系统镜像。完整安装程序应从苹果官方获取；在兼容Mac上用对应安装程序的 `createinstallmedia` 制作介质。清空U盘或SSD需要当前用户明确指定目标；本仓库脚本没有格式化功能。首次磁盘分区和FileVault解锁由人在现场完成。

## 1. 还原与个性化

```bash
python3 scripts/verify.py
python3 scripts/assemble.py --output local/bundle
mkdir -p local
cp docs/identity.example.json local/identity.json
# 私下填写自己的MacBookPro16,1身份，文件不上传、不贴进聊天。
python3 scripts/personalize.py --profile stable-sdr-100s \
  --identity local/identity.json --output local/config.plist
```

用官方OpenCore1.0.8包中的ocvalidate校验 `local/config.plist`。可以从 [OpenCore发布页](https://github.com/acidanthera/OpenCorePkg/releases) 获取匹配版本。新的序列号/UUID应在首次设置前准备；不要在已绑定Apple服务的系统中随意轮换。

初次启动可以选择 recovery-igpu-audio-off 配置，通过内屏进入目标macOS安装NVIDIA文件；不同配置不能使用不同的SMBIOS身份。恢复配置不会自动降低或恢复安全策略。

无线管理工具HeliPort.app不在本包中，从 [OpenIntelWireless/HeliPort官方发布页](https://github.com/OpenIntelWireless/HeliPort/releases) 获取。itlwm通常不会在系统原生Wi-Fi面板中提供网络搜索；清空的WiFiConfig需要由本机的HeliPort重新配置，不能从仓库恢复个人网络。

## 2. 在Ubuntu部署EFI

先只读运行 `lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,PARTUUID,MOUNTPOINTS`，核对目标盘，不保存到公开仓库。设备编号会变化；4TB不保证始终是nvme0或disk0。

```bash
python3 scripts/deploy_efi_linux.py --bundle local/bundle --config local/config.plist \
  --efi-device /dev/disk/by-partuuid/YOUR_EFI_UUID \
  --expected-serial YOUR_TARGET_SERIAL --expected-efi-uuid YOUR_EFI_UUID
```

这是预览。核对当前用户的写入授权及ocvalidate结果后，在Ubuntu上用root执行相同命令并加 `--apply`。它检查序列号、EFI UUID、vfat格式、未挂载状态和QEMU进程；先完整备份原EFI到 `local/backups/`，再写BOOT/OC，核对其他系统目录未变。

工具可能保留原EFI中未覆盖的旧文件，以免误删用户资料；实际加载以新config为准。出现失败时先保留现场和备份，不能继续反复覆盖。脚本不写BootOrder，不重启，也不格式化。

## 3. 在目标macOS安装NVIDIA运行文件

先确认 `uname -s` 是Darwin、目标系统版本与Data卷身份正确，并确认是在目标神舟或明确隔离的维护环境，而非操作agent所在的另一台Mac。

本包运行文件位于：

- `local/bundle/rootfs/Library/Extensions/{NVRM,NVRMFB,NVAccel,NVRMAGDC}.kext`
- `local/bundle/rootfs/Library/GPUBundles/`（Metal、NVK、Vulkan、编译运行库）
- `local/bundle/rootfs/Library/NullMoth/`（固件、许可、版本信息）

先备份每个已存在的目标，不直接覆盖不同版本。安装计划由下面命令生成，只输出命令，不执行：

```bash
python3 scripts/plan_macos_install.py --bundle local/bundle
```

该计划使用ditto保留目录结构和运行库的相对符号链接，再设root:wheel与不可被普通用户写入的权限。不要只复制四个kext而漏掉运行库/固件；不要混装不同项目版本或自行换另一代GSP固件。

执行写入前需要当前任务对目标系统的明确授权，以及对本配置所含签名限制例外的授权。公开配置沿用了原机批准的 `csr-active-config=470A0000`、AMFI启动参数和SecureBootModel配置；这些例外会降低系统保护，不代表对另一台机器已获批准。

EFI包含AMFIPass1.4.1，但原机日志显示它因系统版本检测自动停用。不要把“文件存在/注入成功”解释成它已工作；当前成功基线另有AMFI参数。不要未经单独测试给它添加beta参数或扩大例外。

文件部署和签名检查完成后，用正常管理员授权更新内核集合：

```bash
sudo /usr/bin/kmutil install --volume-root / --update-all --update-preboot
```

检查返回值与实际输出。若缺对应KDK、签名拒绝或Preboot更新失败，停下来处理具体报错，不自动加 `-z`、force、更多SIP例外或手工覆盖缓存。复制文件成功不等于缓存已更新；磁盘上的kext不等于当前已加载版本。

本资料不复制苹果BootKC/SystemKC/Preboot缓存。必须由目标系统为其当前build和驱动生成，不能拿另一轮成功开机的缓存或虚拟机缓存盲目覆盖。

## 4. 手动启动验证

由人在现场选择目标OpenCore → Macintosh HD并解锁。先用内屏判断启动，确认外屏输入源正确。

```bash
sysctl hw.physicalcpu hw.logicalcpu kern.bootargs
kmutil showloaded --list-only
system_profiler SPDisplaysDataType SPAudioDataType
ioreg -r -c NVRM -d 1 -l -w0
```

检查NVRM显示`nvrm-autogo=up`、`display armed`、100000ms等待；50秒候选应显示50000ms。确认实体外屏文字和鼠标正常，而不是只看注册树。系统报告HiDPI渲染3200×2000、逻辑1600×1000@165Hz是本机已出现过的组合，不保证任意外屏/线材也有该模式。

“85秒剩余”是100秒固定等待的中间提示；总启动时间还包括其他服务。50秒候选预计省50秒，但需要重复冷启动/重启验证。

## 5. 音频是独立的后续实验

默认`PciRoot(0x0)/Pci(0x1F,0x3)`的`device-id=ffff0000`使内置声卡不匹配VoodooHDA。只有确认图形启动稳定、备份成功配置后，才考虑单独移除该覆盖并安装 `optional-audio/VoodooHDA.kext`。

历史版本为3.6.8d1，ALC293曾有扬声器声音和数字麦克风电平。不要换本仓库未默认发布的3.6.8d2 codec-mask候选或嵌入另一份IOAudioFamily的新VoodooHDA版本；曾出现过IOAudioControl重复类问题。禁止同时盲开AppleALC、SimpleHDA和VoodooHDA。

## 6. 失败与恢复

静止白字并不一定是panic，倒计时也不是卡死。超过约5分钟、没有新进展且SSH不通时，可由人手动回Ubuntu。先提取日志并核对本轮UUID，避免重复旧配置测试。

恢复时使用本地EFI备份；没有必要重装系统或清空4TB。不要在当前Mac不能启动时自动启动接管GPU的QEMU。若需维护VM，另行核对物理盘唯一写入者，使用单独的VM EFI；真机VirtualSMC和QEMU isa-applesmc的关系不同，不能直接复制VM EFI给真机。
