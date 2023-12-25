from __future__ import annotations

from auto_ddns.set_dns.dnspod import Client


def test_update_dnspod():
    client = Client("bone6.com")
    assert client.classify_record("name1.group1") == ("name1.group1", "CNAME")
    assert client.classify_record("192.168.1.1") == ("192.168.1.1", "A")
