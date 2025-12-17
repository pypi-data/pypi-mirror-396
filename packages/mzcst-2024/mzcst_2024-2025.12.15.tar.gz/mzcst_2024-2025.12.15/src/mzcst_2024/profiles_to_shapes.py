import ast
import logging
import typing

from . import interface
from .common import NEW_LINE, OPERATION_FAILED, OPERATION_SUCCESS, quoted
from .shape_operations import Solid

_logger = logging.getLogger(__name__)


class Extrude(Solid):
    def __init__(
        self,
        name: str,
        component: str = "",
        material: str = "Vacuum",
        *,
        properties: dict[str, str] = None,
    ):
        super().__init__(name, component, material,properties=properties)
        self._history_title = f"define extrude: {self._component}:{self._name}"

    def create(self, modeler: "interface.Model3D") -> "Extrude":
        """从属性列表新建挤压实体。

        Args:
            modeler (interface.Model3D): 建模环境。

        Returns:
            self (Extrude): self。
        """
        if not self._properties:
            _logger.error("No valid properties.")
        else:
            scmd1 = [
                "With Extrude",
                ".Reset",
                f'.Name "{self._name}"',
                f'.Component "{self._component}"',
                f'.Material "{self._material}"',
            ]
            cmd1 = NEW_LINE.join(scmd1)
            scmd2 = []
            for k, v in self._properties.items():
                scmd2.append("." + k + " " + v)
            cmd2 = NEW_LINE.join(scmd2)
            scmd3 = [
                ".Create",
                "End With",
            ]
            cmd3 = NEW_LINE.join(scmd3)
            cmd = NEW_LINE.join((cmd1, cmd2, cmd3))
            modeler.add_to_history(self._history_title, cmd)
        return self
