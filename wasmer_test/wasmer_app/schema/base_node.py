from typing import ClassVar, Dict, Type, Optional


class PlainTextNode:
    _registry: ClassVar[Dict[str, Type]] = {}

    @classmethod
    def from_global_id(cls, global_id: str) -> tuple[str, str]:
        try:
            type_alias, _id = global_id.split("_", 1)
        except ValueError:
            raise ValueError(f"Invalid global ID format: {global_id}")
        if type_alias not in cls._registry:
            raise ValueError(f"Invalid global ID")
        return cls._registry[type_alias], _id

    @classmethod
    async def resolve_node(cls, node_id: str, _, type_: Type) -> Optional[object]:
        return await type_.resolve_node(node_id)

    @classmethod
    def register_type(cls, alias):
        def wrapped(type_: Type):
            cls._registry[alias] = type_
            return type_
        return wrapped

    @classmethod
    async def resolve(cls, global_id: str, info) -> Optional["User|DeployedApp"]:
        type_, node_id = cls.from_global_id(global_id)
        return await cls.resolve_node(global_id, info, type_)
