"""Unit tests for :func:`parse_proxy` / :func:`parse_proxy_list`."""

from __future__ import annotations

import pytest
from avitoapi import Proxy, parse_proxy, parse_proxy_list
from avitoapi.exceptions import ProxyParseError


def test_full_url_with_auth():
    proxy = parse_proxy("http://user:pass@1.2.3.4:8080/")
    assert isinstance(proxy, Proxy)
    assert str(proxy.url) == "http://user:pass@1.2.3.4:8080/"


def test_socks5_scheme():
    proxy = parse_proxy("socks5://10.0.0.1:1080")
    assert str(proxy.url).startswith("socks5://10.0.0.1:1080")


def test_host_port_shorthand_defaults_to_http():
    proxy = parse_proxy("1.2.3.4:8080")
    assert str(proxy.url).startswith("http://1.2.3.4:8080")


def test_host_port_user_pass_legacy_format():
    proxy = parse_proxy("1.2.3.4:8080:bob:secret")
    assert "bob:secret@1.2.3.4:8080" in str(proxy.url)


def test_user_pass_at_host_port():
    proxy = parse_proxy("bob:secret@1.2.3.4:8080")
    assert "bob:secret@1.2.3.4:8080" in str(proxy.url)


def test_dict_input():
    proxy = parse_proxy(
        {"host": "1.2.3.4", "port": 8080, "user": "bob", "password": "secret"},
    )
    assert "bob:secret@1.2.3.4:8080" in str(proxy.url)


def test_invalid_port_rejected():
    with pytest.raises(ProxyParseError):
        parse_proxy("1.2.3.4:99999")


def test_unknown_scheme_rejected():
    with pytest.raises(ProxyParseError):
        parse_proxy("ftp://1.2.3.4:8080")


def test_blank_string_rejected():
    with pytest.raises(ProxyParseError):
        parse_proxy("")


def test_unsupported_type_rejected():
    with pytest.raises(ProxyParseError):
        parse_proxy(123)  # type: ignore[arg-type]


def test_parse_list_skips_blank_and_comments():
    text = """
# this is a comment
1.2.3.4:8080
http://10.0.0.1:3128

5.6.7.8:9090
"""
    proxies = parse_proxy_list(text)
    assert len(proxies) == 3


def test_parse_list_skip_invalid_flag():
    proxies = parse_proxy_list(["1.2.3.4:8080", "garbage", "5.6.7.8:9090"], skip_invalid=True)
    assert len(proxies) == 2


def test_parse_list_propagates_errors_by_default():
    with pytest.raises(ProxyParseError):
        parse_proxy_list(["1.2.3.4:8080", "garbage"])


def test_proxy_instance_returned_as_is():
    original = parse_proxy("1.2.3.4:8080")
    again = parse_proxy(original)
    assert again is original


def test_label_override():
    proxy = parse_proxy("1.2.3.4:8080", label="primary")
    assert proxy.label == "primary"
