import abc

from requests_toolbelt.sessions import BaseUrlSession

from .base import Adapter


class APIAdapter(Adapter, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_base_url(self) -> str: ...

    def get_session(self) -> BaseUrlSession:
        return BaseUrlSession(self.get_base_url())
