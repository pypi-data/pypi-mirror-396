from typing import Any
from urllib.parse import urlparse

from expecting.core import Expecting


class ExpectingURL(Expecting):

    def __init__(self, **components: str):
        self.components = components

    def __eq__(self, other: Any) -> bool:
        try:
            url = urlparse(other)
            for component, value in self.components.items():
                if getattr(url, component) != value:
                    return False
            return bool(url.netloc or (url.scheme and url.path))
        except (ValueError, AttributeError):
            return False

    def __repr__(self) -> str:
        components = {
            'scheme': '*',
            'netloc': '*',
            'path': '*',
            'params': '*',
            'query': '*',
            'fragment': '*',
        }
        components.update(self.components)

        return "~= URL [{scheme}://{netloc}{path};{params}?{query}#{fragment}]".format(**components)

def with_scheme(scheme: str) -> Expecting:
    return ExpectingURL(scheme=scheme)


def with_netloc(netloc: str) -> Expecting:
    return ExpectingURL(netloc=netloc)


def with_path(path: str) -> Expecting:
    return ExpectingURL(path=path)


def with_query(query: str) -> Expecting:
    return ExpectingURL(query=query)


def with_fragment(fragment: str) -> Expecting:
    return ExpectingURL(fragment=fragment)


def with_components(**components: str) -> Expecting:
    return ExpectingURL(**components)


def any() -> Expecting:
    return ExpectingURL()


__all__ = [
    'with_scheme',
    'with_netloc',
    'with_path',
    'with_query',
    'with_fragment',
    'with_components',
    'any',
]
