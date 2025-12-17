"""
NewEntity domain model and its repository implementation.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, Generic, TypeVar

from enn_iot_oc.infrastructure.repository.single_repo_base import SingleRepoBase
from enn_iot_oc.infrastructure.repository.multi_repo_base import MultiRepoBase
from enn_iot_oc.util.string_util import parse_object, parse_array

__all__ = ["NewEntity", "NewEntityRepoImpl"]

T = TypeVar('T')

# 定义基类 - 确保使用Generic[T]
NewEntityRepoBase = MultiRepoBase[T]

#------------- Domain Model -------------
@dataclass
class NewEntity:
    """
    NewEntity
    """

    id: str = ""
    name: str = ""
    value: int = 0
    ref_id: str = ""
    r: str = ""

#------------- Repository Implementation -------------
class NewEntityRepoImpl(NewEntityRepoBase[NewEntity]):
    """
    NewEntity
    """
    def __init__(self, eo_id: str = "", instance_id: str = "") -> None:
        """
        初始化方法
        """
        super().__init__(model_code="new_entity", eo_id=eo_id, instance_id=instance_id, id_field="id")

    def to_domain(self, row: Dict[str, Any]) -> NewEntity:
        """
        将数据库行转换为领域模型
        """
        return NewEntity(
            id=parse_object(row.get("id"), str),
            name=parse_object(row.get("name"), str),
            value=parse_object(row.get("value"), int),
            ref_id=parse_object(row.get("ref_id"), str),
            r=parse_object(row.get("r"), str),
        )

    def from_domain(self, entity) -> Dict[str, Any]:
        """
        将领域模型转换为数据库行
        """
        from dataclasses import asdict, is_dataclass
        result = {
            "id": getattr(entity, "id", None),
            "name": getattr(entity, "name", None),
            "value": getattr(entity, "value", None),
            "ref_id": getattr(entity, "ref_id", None),
            "r": getattr(entity, "r", None),
        }
        return result

    def empty_object(self) -> NewEntity:
        """
        创建一个空的领域模型对象
        """
        return NewEntity(
            id="",
            name="",
            value=0,
            ref_id="",
            r="",
        )

    def extract_id(self, entity) -> str:
        """
        提取ID值
        """
        return getattr(entity, "id", "")
