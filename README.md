# Auto-ddns

一个可扩展的 DNS 管理工具。

## 安装 [![Downloads](https://pepy.tech/badge/auto-ddns)](https://pepy.tech/project/auto-ddns)

### 使用 pip/pipx 安装

在此之前请确保安装 `Python3.10` 及以上版本，并安装了 `pip`。
```shell
pip install auto-ddns[all]
```

如果想要尝试 Nightly 版本，可尝试（需确保使用`Python3.12`）
```shell
pip install git+https://github.com/zrr1999/auto-ddns@main
```

在此之前请确保安装了 `pipx`。
```shell
pipx install auto-ddns[all]
```

### 源码安装（需确保使用`Python3.12`）

```shell
git clone https://github.com/zrr1999/auto-ddns
cd auto-ddns
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
auto-ddns update --path ~/.config/auto-ddns/sdns.json
```
此时，你的解析记录就会增加一条 `test.mydomain.com` 的 CNAME 记录指向 `baidu.com` 。


## 维护者

@zrr1999

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/zrr1999/auto-ddns/issues/new) 或者提交一个 [Pull Request](https://github.com/zrr1999/auto-ddns/pulls/new)。

### 贡献者

感谢以下参与项目的人：

## 使用许可
[GNU](LICENSE) © Rongrui Zhan
