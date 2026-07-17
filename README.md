# dns-manager

<p align="center">
   <a href="https://python.org/" target="_blank"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/dns-manager?logo=python&style=flat-square"></a>
   <a href="https://pypi.org/project/dns-manager/" target="_blank"><img src="https://img.shields.io/pypi/v/dns-manager?style=flat-square" alt="pypi"></a>
   <a href="https://pypi.org/project/dns-manager/" target="_blank"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/dns-manager?style=flat-square"></a>
   <a href="LICENSE"><img alt="LICENSE" src="https://img.shields.io/pypi/l/dns-manager?style=flat-square"></a>
   <br/>
   <a href="https://codecov.io/gh/zrr-lab/dns-manager" ><img src="https://codecov.io/gh/zrr-lab/dns-manager/graph/badge.svg?token=l0m6mbJfad"/></a>
   <a href="https://codspeed.io/zrr-lab/dns-manager"><img src="https://img.shields.io/endpoint?url=https://codspeed.io/badge.json" alt="CodSpeed Badge"/></a>
   <br/>
   <a href="https://github.com/astral-sh/uv"><img alt="uv" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&style=flat-square"></a>
   <a href="https://github.com/astral-sh/ruff"><img alt="ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square"></a>
   <a href="https://gitmoji.dev"><img alt="Gitmoji" src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67?style=flat-square"></a>
</p>


一个专注于 DDNS 的 DNS 记录同步工具。它从公网接口或本地网络设备获取动态 IP，
并通过 [Lexicon](https://github.com/AnalogJ/lexicon) 将对应的 A/AAAA 记录同步到 DNS 提供商。

## 安装 [![Downloads](https://pepy.tech/badge/dns-manager)](https://pepy.tech/project/dns-manager)

### 使用 pip/pipx/uv 安装

在此之前请确保使用 Python 3.12 或更高版本，并安装了 pip。
```shell
pip install dns-manager
```

如果想要尝试 Nightly 版本，可使用：
```shell
pip install git+https://github.com/zrr1999/dns-manager@main
```

在此之前请确保安装了 [pipx](https://github.com/pypa/pipx)/[uv](https://github.com/astral-sh/uv)。
```shell
pipx install dns-manager
uv tool install dns-manager
```

pipx/uv 会无感地为 dns-manager 创建一个虚拟环境，与其余环境隔离开，避免污染其他环境，
因此相对于 pip，pipx/uv 是更推荐的安装方式。

## 使用说明

### DDNS 配置

默认配置路径为 `~/.config/dns-manager/config.toml`。例如：

```toml
[home]
domain = "mydomain.com"
setter_name = "cloudflare"
records = [
    [
      "home",
      "public:https://api.ipify.org"
    ]
]
```

也支持同等结构的 `.json` 配置。未指定 `records_files` 时，会自动尝试加载与主配置同目录、同后缀的
`records.toml` / `records.json`（文件不存在则跳过）。records 文件与主配置共用同一字段形状：

```toml
records = [
    ["office", "public:https://api64.ipify.org"]
]
ignore = ["mail"]
```

`ignore` 里的主机名不会被同步，远端同名记录也不会被当成 unmanaged 告警。

`public:` 后面是返回单个 IPv4 或 IPv6 地址的 HTTP 接口。dns-manager 会在每轮同步时
重新获取地址，并根据响应选择 A 或 AAAA 记录。单个来源应保持稳定的地址族；双栈场景应分别配置
固定返回 IPv4 与 IPv6 的来源。

也可以使用：

- `snmp:<interface>`：从网关接口读取地址
- `default:v4` / `default:v6`：取本机默认出网地址
- `local:v4` / `local:v6`：取本机主机名对应地址；可用 `local:v4:1` 选择第 N 个地址

Lexicon 从环境变量读取提供商凭据。例如 Cloudflare 使用：

```shell
export LEXICON_CLOUDFLARE_AUTH_TOKEN=your-token
```

先执行一次同步以检查配置与凭据：

```shell
dnsm update
# 或使用其他配置路径
dnsm update ./examples/simple.toml
```

### Daemon 模式

`daemon` 会在前台立即同步一次，随后按固定间隔继续同步：

```shell
dnsm daemon --interval 300
# 或使用其他配置路径
dnsm daemon ./examples/simple.toml --interval 300
```

daemon 不会 fork、脱离终端或写入 PID 文件，适合直接交给 systemd、launchd、容器或其他
进程管理器托管。收到 SIGINT/SIGTERM 后，它会在当前同步结束后退出；再次发送信号可强制立即退出。
配置在启动时读取，修改后需重启进程。

### 支持的 DNS 提供商
本项目实现了一个 [lexicon](https://github.com/dns-lexicon/dns-lexicon) 的适配 Setter，
支持情况与其一致。

### Cron 方式

如果不需要常驻进程，也可以用 cron 调用一次性同步：

```
@hourly dnsm update ~/.config/dns-manager/config.toml
```

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/zrr1999/dns-manager/issues/new) 或者提交一个 [Pull Request](https://github.com/zrr1999/dns-manager/pulls/new)。

### 贡献者

感谢以下参与项目的人：

## 使用许可
[GNU](LICENSE) © Rongrui Zhan
