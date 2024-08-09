__all__ = [
    "Proxy", "Rule", "Scheme"
]

import json
from typing import Iterable


class Proxy:
    def __init__(self, proxy: str):
        self.proxy = proxy


class Rule:
    def __init__(self, rules: Iterable[str] | str, proxies: Iterable[Proxy] | Proxy):
        self.rules = [rule.replace(".", r"\.").replace("*", ".*")
                      for rule in rules] if isinstance(rules, Iterable) \
            else [rules.replace(".", r"\.").replace("*", ".*")]
        self.proxies = ";".join([proxy.proxy for proxy in proxies]) if isinstance(proxies, Iterable) \
            else proxies.proxy


class Scheme:
    def __init__(self, title: str, *rules: Rule):
        self.title = title
        self.rules = rules

    def jsonify(self) -> bytes:
        return json.dumps([[rule.rules, rule.proxies] for rule in self.rules]).encode()
