# dns-manager

一个可扩展的 DNS 管理工具。

## 安装 [![Downloads](https://pepy.tech/badge/dns-manager)](https://pepy.tech/project/dns-manager)

### 使用 pip/pipx/uv 安装

在此之前请确保安装 Python3.10 及以上版本，并安装了 pip。
```shell
pip install dns-manager[all]
```

如果想要尝试 Nightly 版本，可尝试（需确保使用`Python3.12`）
```shell
pip install git+https://github.com/zrr1999/dns-manager@main
```

在此之前请确保安装了 [pipx](https://github.com/pypa/pipx)/[uv](https://github.com/astral-sh/uv)。
```shell
pipx install dns-manager[all]
uv tool install dns-manager[all]
```

pipx/uv 会类似 Homebrew 无感地为 yutto 创建一个虚拟环境，与其余环境隔离开，避免污染 pip 的环境，
因此相对于 pip，pipx/uv 是更推荐的安装方式（uv 会比 pipx 更快些～）。

### 源码安装（需确保使用`Python3.12`）

```shell
git clone https://github.com/zrr1999/dns-manager
cd dns-manager
pip install .
```

## 使用说明
首先创建一个配置文件，例如 `sdns.json`，内容如下：
```json
{
  "domain": "mydomain.com",
  "records": [
    [
      "test", // 也就是 test.mydomain.com 指向的路径
      "baidu.com" // 解析值，目前只支持 A 记录和 CNAME 记录，会根据此处的值自动判断
    ],
  ]
}
```
然后执行以下命令：
```shell
dns-manager update --path ~/.config/dns-manager/sdns.json
```
此时，你的解析记录就会增加一条 `test.mydomain.com` 的 CNAME 记录指向 `baidu.com` 。

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

## 维护者

@zrr1999

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/zrr1999/dns-manager/issues/new) 或者提交一个 [Pull Request](https://github.com/zrr1999/dns-manager/pulls/new)。

### 贡献者

感谢以下参与项目的人：

## 使用许可
[GNU](LICENSE) © Rongrui Zhan
