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


一个可扩展的 DNS 管理工具。

## 安装 [![Downloads](https://pepy.tech/badge/dns-manager)](https://pepy.tech/project/dns-manager)

### 使用 pip/pipx/uv 安装

在此之前请确保安装 Python3.10 及以上版本，并安装了 pip。
```shell
pip install dns-manager[all]
```

如果想要尝试 Nightly 版本，可尝试（需确保使用 Python3.12）
```shell
pip install git+https://github.com/zrr1999/dns-manager@main
```

在此之前请确保安装了 [pipx](https://github.com/pypa/pipx)/[uv](https://github.com/astral-sh/uv)。
```shell
pipx install dns-manager[all]
uv tool install dns-manager[all]
```

pipx/uv 会无感地为 dns-manager 创建一个虚拟环境，与其余环境隔离开，避免污染其他环境，
因此相对于 pip，pipx/uv 是更推荐的安装方式。

## 使用说明
### 基础示例
首先创建一个配置文件，例如类似 `examples/simple.toml` 文件中的内容，如下：
```toml
[test]
domain = "mydomain.com"
setter_name = "cloudflare"
records = [
    [
      "test",  # 也就是 test.mydomain.com 指向的路径
      "baidu.com"  # 解析值，目前只支持 A 记录和 CNAME 记录，会根据此处的值自动判断
    ]
]
```
然后执行以下命令：
```shell
dns-manager update examples/simple.toml
# dnsm update examples/simple.toml
```
此时，你的解析记录就会增加一条 `test.mydomain.com` 的 CNAME 记录指向 `baidu.com` 。

### 支持的 dns 提供商
本项目实现了一个 [lexicon](https://github.com/dns-lexicon/dns-lexicon) 的适配 Setter，
支持情况与其一致。

### 定时执行
你可以使用 [cronie](https://github.com/cronie-crond/cronie) 定时执行，例如
```
@reboot dnsm update ~/.config/dns-manager/config.toml
@hourly dnsm update ~/.config/dns-manager/config.toml
```

你可以通过下面的命令添加定时任务
```shell
(crontab -l 2>/dev/null; echo "@reboot dnsm update ~/.config/dns-manager/config.toml") | crontab
(crontab -l 2>/dev/null; echo "@hourly dnsm update ~/.config/dns-manager/config.toml") | crontab
```

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/zrr1999/dns-manager/issues/new) 或者提交一个 [Pull Request](https://github.com/zrr1999/dns-manager/pulls/new)。

### 贡献者

感谢以下参与项目的人：

## 使用许可
[GNU](LICENSE) © Rongrui Zhan
