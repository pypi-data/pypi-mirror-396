from typing import List, Dict, Any, Tuple

from hmd_meta_types import Entity, Noun, Relationship

from hmd_entity_storage.engines.base_engine import BaseEngine
from hmd_schema_loader import DefaultLoader
from .hmd_base_client import BaseClient


class DbEngineClient(BaseClient):
    def __init__(self, db_engine: BaseEngine, loader: DefaultLoader):
        self.db_engine = db_engine
        super().__init__(loader=loader)

    def _do_get_entity(self, entity_name: str, id_: str) -> Entity:
        return self.db_engine.get_entity(self.loader.get_class(entity_name), id_)

    def _do_get_entities(self, entity_name: str, ids_: List[str]) -> List[Entity]:
        return self.db_engine.get_entities(self.loader.get_class(entity_name), ids_)

    def _do_search_entity(self, entity_name: str, filter_: dict = {}) -> List[Entity]:
        return self.db_engine.search_entities(
            self.loader.get_class(entity_name), filter_
        )

    def _do_delete_entity(self, entity_name: str, id_: int):
        self.db_engine.delete_entity(self.loader.get_class(entity_name), id_)

    def _do_upsert_entity(self, entity: Entity):
        return self.db_engine.put_entity(entity)

    def _do_get_relationships_from(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        return self.db_engine.get_relationships_from(
            self.loader.get_class(relationship_type), noun.identifier
        )

    def _do_get_relationships_to(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        return self.db_engine.get_relationships_to(
            self.loader.get_class(relationship_type), noun.identifier
        )

    def _do_invoke_custom_operation(
        self, operation_name: str, payload: Dict, http_method: str
    ):
        raise NotImplemented()

    def _do_upsert_entities(self, nouns: List[Noun], relationships: List[Relationship]):
        return self.db_engine.upsert_entities(
            {"nouns": nouns, "relationships": relationships}
        )

    def native_query_nouns(self, query: Any, data: Dict) -> List[Noun]:
        raw_results = self.db_engine.native_query_nouns(query, data)
        return [
            self.cache_instance(
                Entity.deserialize(self.loader.get_class(raw_result[0]), raw_result[1])
            )
            for raw_result in raw_results
        ]

    def native_query_relationships(self, query: Any, data: Dict) -> List[Relationship]:
        raw_results = self.db_engine.native_query_relationships(query, data)
        return [
            self.cache_instance(
                Entity.deserialize(self.loader.get_class(raw_result[0]), raw_result[1])
            )
            for raw_result in raw_results
        ]
