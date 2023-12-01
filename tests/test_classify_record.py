from __future__ import annotations

from auto_ddns.update_dnspod import classify_record


def test_classify_record():
    assert classify_record("name1.group1") == ("name1.group1", "CNAME")
    assert classify_record("192.168.1.1") == ("192.168.1.1", "A")
