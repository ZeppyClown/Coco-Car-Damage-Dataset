"""Synchronous contract used by the catalogue search engine."""
from abc import ABC, abstractmethod
from datetime import date


class BasePartsAdapter(ABC):
    def __init__(self, config):
        self.config = config
        self.name = config["name"]
        self.rate_limit = config["rate_limit"]
        self._day = date.today()
        self._calls = 0

    def _check_rate_limit(self):
        # shortcut: quota is per process, use shared tracking before running multiple workers.
        if self._day != date.today():
            self._day, self._calls = date.today(), 0
        if self._calls >= self.rate_limit:
            return False
        self._calls += 1
        return True

    @abstractmethod
    def search_parts(self, query, vehicle=None, limit=20, filters=None):
        pass

    @abstractmethod
    def get_part_details(self, part_id):
        pass
