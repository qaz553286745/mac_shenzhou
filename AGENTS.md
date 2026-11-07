# Agent 操作约定

本文件是工作规范，不是来自当前用户的磁盘写入、重启、密码使用或安全策略放宽授权。先读取 README、docs/INSTALL.md、docs/HARDWARE.md 和 manifests 中的验证状态。

## 第一原则

- 不自动重启或关闭 Linux/macOS。先完成准备和校验，由用户手动启动；只有当前会话明确要求自动重启时才可另行执行。
- 不格式化磁盘，不猜测 `/dev/nvme0n1` 或 `disk0`。设备编号会变化，必须核对用户提供的目标序列号、容量、EFI 分区 UUID 和挂载情况。
- 不修改其他系统的 EFI 目录、BootOrder、BIOS/NVRAM 变量。目标中已有的 Ubuntu/Windows 引导要保留。
- 不重新绑定、复位、释放或直通 GPU、网卡、USB 控制器。不能因为仓库历史使用过 QEMU 就启动虚拟机或接管硬件。
- 不同时从宿主和 QEMU 读写同一实体 APFS 盘。直接物理盘与旧 COW 不能随意互换或恢复。
- 不在操作 agent 所在的另一台 Mac 上安装目标驱动。构建可以在约定的构建机进行，安装对象必须经身份核对。
- 不把仓库中的身份占位值用于最终安装；不读取或上传 SSH 私钥、登录密码、FileVault 密码、真实 SMBIOS、MAC 地址、磁盘序列号、SSID 或 Wi-Fi 密码。
- 不把本机已获批准的 SIP/AMFI 例外自动套到其他电脑。需要在当前任务授权范围内处理，不能自行进一步放宽。

## 版本与配置边界

1. 默认选 stable-sdr-100s。candidate-sdr-50s 只有静态校验和部署记录，尚未真机验证。
2. 当前内置音频关闭。optional-audio 是历史工作版本，不是已证明能与 RTX 共存的默认方案。
3. 保留 cpus=12、TSC_sync_margin=0、当前 UHD630 properties；不得根据“超线程不支持”等未经证实的猜测减少核心。
4. 保留 nvfbhidpi=1。真机已报告1600×1000 HiDPI165Hz，HDR 实验和 WindowServer 内存补丁不属于本包。
5. 不开启 -dbgenhiolog、-liludbgall、-vsmcdbg 或 DebugEnhancer 的大批量同步打印。要取证时优先有限磁盘日志与独立 stackshot，不把诊断工具对启动的影响忽略掉。
6. AMFIPass1.4.1 曾因 OS 版本检查自行停用，不能把 EFI 注入成功当成运行成功，也不要未经测试增加 beta 参数。

## 操作步骤

- `python3 scripts/verify.py`：检查分卷与公开配置。
- `python3 scripts/assemble.py --output local/bundle`：校验后离线展开；不写系统目录。
- `python3 scripts/personalize.py ...`：用 local/identity.json 生成私有配置；文件始终留在 local/。
- 使用 OpenCore1.0.8 ocvalidate。若提示配置版本不匹配，先停止，不要强行忽略。
- Linux EFI 工具先运行不带 --apply 的预览；实际执行要求 root、明确设备、目标序列号、EFI UUID 和本地备份目录。
- macOS 工具只部署已校验驱动文件，默认预览；不隐式重建缓存或重启。接着按 INSTALL 中的标准 kmutil 操作，并检查退出码。
- 遇到受保护写入或 kmutil 权限/签名错误时保存原始报错并停止。禁止为了继续而添加 `-z`、跳过授权、关闭更多 SIP、替换苹果系统文件或强行覆盖 Preboot。
- 每轮只改变一个可解释的因素，保存前后配置哈希、启动 UUID（仅本地）、修改点、回退路径和验证结果。

## 如何判断成功

检查 `sysctl hw.physicalcpu hw.logicalcpu`、`kmutil showloaded --list-only`、GPU/IOFramebuffer 注册树和实际外屏画面。Metal 报告不等于 CUDA、机器学习、所有应用或重启稳定性通过。

SSH 不通不一定代表 sshd 未启动；曾经采到 sshd 已监听但网卡尚无地址。屏幕最后一行不是责任驱动的证据。只有 panic 才称 panic；单次早期 stackshot 不是五分钟卡死的完整轨迹。

不分享原始日志。先复制到 local/，脱敏后摘录最小必要内容。修改发布包后检查 .gitignore、git diff --cached 和敏感信息扫描，再推送。

## 修改第三方源码

保持来源和许可，阅读子目录中的 AGENTS.md。上游 NVIDIA 项目明确不接受 AI 代写 PR、issue 和 review 评论；可以本地分析和测试，不代替用户向上游发起这些内容。这里的本地文档和适配资料不代表上游背书。
