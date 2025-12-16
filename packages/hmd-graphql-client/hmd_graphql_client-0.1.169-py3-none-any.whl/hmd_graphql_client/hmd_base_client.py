from abc import ABC, abstractmethod
from typing import List, Dict
from collections import defaultdict

from hmd_schema_loader import DefaultLoader

from hmd_meta_types import Entity, Noun, Relationship


class BaseClient(ABC):
    def __init__(self, loader: DefaultLoader):
        self.loader = loader
        self.instance_cache = defaultdict(dict)

    def get_entity(self, entity_name: str, id_: str) -> Entity:
        """Retrieve an entity.

        Args:
            entity_name (str): The fully qualified entity name.
            id_ (int): The entity identifier.

        Returns:
            Entity: The entity referred to by the id.
        """
        return self.cache_instance(self._do_get_entity(entity_name, id_))

    @abstractmethod
    def _do_get_entity(self, entity_name: str, id_: str) -> Entity:
        pass

    def get_entities(self, entity_name: str, ids_: List[str]) -> List[Entity]:
        return [
            self.cache_instance(inst)
            for inst in self._do_get_entities(entity_name, ids_)
        ]

    @abstractmethod
    def _do_get_entities(self, entity_name: str, ids_: List[str]) -> List[Entity]:
        pass

    def search_entity(self, entity_name: str, filter_: dict = {}) -> List[Entity]:
        """Search for an entity of a specific type.

        Search for an entity of a specific type. Returns all entities of the
        type by default. The `search_filter` parameter can be used to filter the
        objects to return.

        :param entity_name: The fully qualified name of the entity.
        :param filter_: A map of filed name/value pairs to be used to filter the
                        returned entities.
        :return: A `list` of the entities that match the filter.
        """
        result = self._do_search_entity(entity_name, filter_)
        return [self.cache_instance(ent) for ent in result]

    @abstractmethod
    def _do_search_entity(self, entity_name: str, filter_: dict) -> List[Entity]:
        pass

    def delete_entity(self, entity_name: str, id_: str):
        self._do_delete_entity(entity_name, id_)

    @abstractmethod
    def _do_delete_entity(self, entity_name: str, id_: str):
        pass

    def upsert_entity(self, entity: Entity) -> Entity:
        return self.cache_instance(self._do_upsert_entity(entity))

    @abstractmethod
    def _do_upsert_entity(self, entity: Entity) -> Entity:
        pass

    def get_relationships_from(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        result = self._do_get_relationships_from(noun, relationship_type)
        return [self.cache_instance(res) for res in result]

    @abstractmethod
    def _do_get_relationships_from(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        pass

    def get_relationships_to(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        result = self._do_get_relationships_to(noun, relationship_type)
        return [self.cache_instance(res) for res in result]

    @abstractmethod
    def _do_get_relationships_to(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        pass

    def invoke_custom_operation(
        self, operation_name: str, payload: Dict, http_method: str = "POST"
    ) -> Dict:
        return self._do_invoke_custom_operation(operation_name, payload, http_method)

    @abstractmethod
    def _do_invoke_custom_operation(
        self, operation_name: str, payload: Dict, http_method: str = "POST"
    ):
        pass

    def upsert_entities(
        self, nouns: List[Noun] = [], relationships: List[Relationship] = []
    ) -> Dict[str, List[Entity]]:
        return self._do_upsert_entities(nouns, relationships)

    @abstractmethod
    def _do_upsert_entities(
        self, nouns: List[Noun], relationships: List[Relationship]
    ) -> Dict[str, List[Entity]]:
        pass

    def cache_instance(self, entity):
        if entity is None:
            return None
        result = self.get_cached_instance(entity)
        if not result:
            self.instance_cache[entity.__class__.get_namespace_name()][
                entity.identifier
            ] = entity
            result = entity
        elif result != entity:
            self.instance_cache[entity.__class__.get_namespace_name()][
                entity.identifier
            ] = entity
            result.set_equals(entity)

        return result

    def get_cached_instance(self, entity):
        return self.get_cached_instance_by_id(
            entity.__class__.get_namespace_name(), entity.identifier
        )

    def get_cached_instance_by_id(self, entity_name: str, id_: str):
        return self.instance_cache[entity_name].get(id_)
