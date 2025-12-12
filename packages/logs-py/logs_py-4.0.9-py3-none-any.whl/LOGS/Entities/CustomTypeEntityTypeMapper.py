from enum import Enum
from typing import TYPE_CHECKING, Type

from LOGS.Entities.CustomFieldModels import CustomTypeEntityType
from LOGS.Entity.EntityWithIntId import IEntityWithIntId

if TYPE_CHECKING:
    from LOGS.Entity.EntityWithIntId import IEntityWithIntId


class CustomFieldValueType(Enum):
    CustomField = "CustomField"
    CustomTypeSection = "CustomTypeSection"


class CustomTypeEntityTypeMapper:
    @classmethod
    def getClass(cls, entityType: CustomTypeEntityType) -> Type["IEntityWithIntId"]:
        mapping = {
            CustomTypeEntityType.Sample: cls.Sample(),
            CustomTypeEntityType.Dataset: cls.Dataset(),
            CustomTypeEntityType.InventoryItem: cls.InventoryItem(),
            CustomTypeEntityType.Project: cls.Project(),
            CustomTypeEntityType.Person: cls.Person(),
        }
        result = mapping.get(entityType, None)
        if result is None:
            raise Exception(f"Unknown entity type '{entityType.name}'.")
        return result

    @classmethod
    def Sample(cls):
        from LOGS.Entities.Sample import Sample

        return Sample

    @classmethod
    def Dataset(cls):
        from LOGS.Entities.Dataset import Dataset

        return Dataset

    @classmethod
    def InventoryItem(cls):
        from LOGS.Entities.InventoryItem import InventoryItem

        return InventoryItem

    @classmethod
    def Project(cls):
        from LOGS.Entities.Project import Project

        return Project

    @classmethod
    def Person(cls):
        from LOGS.Entities.Person import Person

        return Person
