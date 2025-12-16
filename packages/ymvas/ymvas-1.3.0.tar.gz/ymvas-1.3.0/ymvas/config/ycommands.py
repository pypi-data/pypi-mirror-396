from functools import lru_cache
from typing import TYPE_CHECKING

from ymvas.utils.files import get_yaml
if TYPE_CHECKING:
    from ymvas.settings import Settings


class YCommandsSettings:

    def __init__(self, settings:"Settings") -> None:
        self.settings = settings
        self._data = get_yaml(settings.f_settings_commands)
    
    @property
    def data(self) -> dict:
        return self._data

    @property
    @lru_cache
    def ignore_dot_files(self) -> bool:
        return True
