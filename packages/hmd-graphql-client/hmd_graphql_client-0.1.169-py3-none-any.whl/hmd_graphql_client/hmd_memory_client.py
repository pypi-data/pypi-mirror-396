from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Type

from dateutil.parser import isoparse
from hmd_schema_loader import DefaultLoader

from hmd_meta_types import Entity, Noun, Relationship
from hmd_entity_storage import gen_new_key

from .hmd_base_client import BaseClient


class MemoryClient(BaseClient):
    def __init__(self, loader: DefaultLoader, data: Dict = {}):
        super().__init__(loader=loader)
        self.data = data
        if self.data:
            load_data(loader, self, self.data)

    def _do_get_entity(self, entity_name: str, id_: int) -> Entity:
        entity = self.instance_cache[entity_name].get(id_)
        if not entity:
            raise Exception(f"Entity of type {entity_name} with id {id_} not found.")
        return entity

    def _do_get_entities(self, entity_name: str, ids_: List[str]) -> List[Entity]:
        result = []
        for id_ in ids_:
            entity = self.instance_cache[entity_name].get(id_)
            if not entity:
                raise Exception(
                    f"Entity of type {entity_name} with id {id_} not found."
                )
            result.append(entity)
        return result

    def _do_search_entity(self, entity_name: str, filter_: dict) -> List[Entity]:
        if filter_ and len(filter_) not in [0, 3]:
            raise Exception(
                "Only simple equality filtering is supported in MemoryClient"
            )

        if len(filter_) == 0:
            return self.instance_cache[entity_name].values()
        else:
            return [
                entity
                for entity in self.instance_cache[entity_name].values()
                if filter_["value"] == getattr(entity, filter_["attribute"], None)
            ]

    def _do_upsert_entity(self, entity: Entity) -> Entity:
        if not entity.identifier:
            entity.identifier = gen_new_key()
            entity._created = datetime.utcnow()
        entity._updated = datetime.utcnow()
        if isinstance(entity, Relationship):
            if isinstance(entity.ref_to, Noun):
                entity.ref_to = entity.ref_to.identifier
            if isinstance(entity.ref_from, Noun):
                entity.ref_from = entity.ref_from.identifier
        return entity

    def _do_delete_entity(self, entity_name: str, id_: int):
        if entity_name in self.instance_cache:
            if id_ in self.instance_cache[entity_name]:
                del self.instance_cache[entity_name][id_]

    def _do_get_relationships_from(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        noun = self.get_cached_instance(noun)  # type: Noun
        if not noun:
            raise Exception(
                f"No entity of type {noun.get_namespace_name()} with id {noun.identifier}"
            )
        return [
            rel
            for rel in self.instance_cache[relationship_type].values()
            if noun.identifier
            == (
                rel.ref_from.identifier
                if isinstance(rel.ref_from, Noun)
                else rel.ref_from
            )
        ]

    def _do_get_relationships_to(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        noun = self.get_cached_instance(noun)  # type: Noun
        if not noun:
            raise Exception(
                f"No entity of type {noun.get_namespace_name()} with id {noun.identifier}"
            )
        return [
            rel
            for rel in self.instance_cache[relationship_type].values()
            if noun.identifier
            == (rel.ref_to.identifier if isinstance(rel.ref_to, Noun) else rel.ref_to)
        ]

    def _do_invoke_custom_operation(
        self, operation_name: str, payload: Dict, http_method: str = "POST"
    ):
        raise Exception("Custom operations not supported in MemoryClient")

    def _do_upsert_entities(self, nouns, relationships):
        raise Exception("Bulk Upsert not supported in MemoryClient")

    def get_data(self):
        result = {"nouns": defaultdict(list), "relationships": defaultdict(list)}

        for type_ in self.instance_cache:
            for id, entity in self.instance_cache[type_].items():
                if issubclass(self.loader.get_class(type_), Noun):
                    result["nouns"][type_].append(entity.serialize(encode_blobs=False))
                else:
                    result["relationships"][type_].append(
                        entity.serialize(encode_blobs=False)
                    )

        return result

    def dump_data(self):
        nouns = defaultdict(list)
        relationships = defaultdict(list)
        for type in self.instance_cache:
            if issubclass(self.loader.get_class(type), Noun):
                obj: Noun
                for obj in self.instance_cache[type].values():
                    nouns[type].append(obj.serialize(encode_blobs=False))
            else:
                obj: Relationship
                for obj in self.instance_cache[type].values():
                    relationships[type].append(obj.serialize(encode_blobs=False))

        return {"nouns": dict(nouns), "relationships": dict(relationships)}


def fix_iso_dates(entity_data, entity_loader_data):
    for name, field_dev in entity_loader_data["entity_def"]["attributes"].items():
        if field_dev["type"] == "timestamp":
            if name in entity_data:
                entity_data[name] = isoparse(entity_data[name])
    pass


def load_data(loader: DefaultLoader, client: MemoryClient, data: Dict):
    nouns = defaultdict(dict)
    relationships = defaultdict(list)
    for type_name in data["nouns"]:
        entity_loader_data = loader.get(type_name)  # type: Dict
        entity_type = loader.get_class(type_name)  # type: Type[Noun]

        for entity_data in data["nouns"][type_name]:
            if "tmp_id" in entity_data:
                tmp_id = entity_data["tmp_id"]
                del entity_data["tmp_id"]
            elif "identifier" not in entity_data:
                raise Exception('Nouns require either "tmp_id" or "identifier".')
            else:
                tmp_id = entity_data["identifier"]
            fix_iso_dates(entity_data, entity_loader_data)
            entity = client.upsert_entity(entity_type(**entity_data))
            nouns[type_name][tmp_id] = entity

    for type_name in data["relationships"]:
        entity_type = loader.get_class(type_name)  # type: Type[Relationship]

        ref_from_type = entity_type.ref_from_type()
        ref_to_type = entity_type.ref_to_type()

        for entity_data in data["relationships"][type_name]:
            ref_from = nouns[ref_from_type.get_namespace_name()].get(
                entity_data["ref_from"], None
            )
            if not ref_from:
                raise Exception(
                    f"No entity of type, {ref_from_type.get_namespace_name()}, with tmp_id {entity_data['ref_from']}"
                )

            ref_to = nouns[ref_to_type.get_namespace_name()].get(
                entity_data["ref_to"], None
            )
            if not ref_to:
                raise Exception(
                    f"No entity of type, {ref_to_type.get_namespace_name()}, with tmp_id {entity_data['ref_to']}"
                )

            del entity_data["ref_from"]
            del entity_data["ref_to"]
            client.upsert_entity(
                entity_type(
                    ref_from=ref_from.identifier,
                    ref_to=ref_to.identifier,
                    **entity_data,
                )
            )
    pass
