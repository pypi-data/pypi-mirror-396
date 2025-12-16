from typing import Set, Any, List

from hmd_schema_loader import LoaderException

from hmd_meta_types import Relationship, Noun
from .hmd_base_client import BaseClient


class RelationshipSupport:
    """
    The RelationshipSupport class provides generic support to pull the entity
    from a Relationship.
    """

    def __init__(self, clients: List[BaseClient] = []):
        self._clients = set()  # type: Set[BaseClient]
        for client in clients:
            self._clients.add(client)

    def register_client(self, client: BaseClient):
        self._clients.add(client)

    def _get_client_for_type(self, type_name: str):
        for client in self._clients:
            try:
                if client.loader.get(type_name):
                    return client
            except LoaderException:
                pass

        raise Exception(f"No client registered for type, {type_name}.")

    def ref_from(self, relationship: Relationship) -> Any:
        id_ = relationship.ref_from

        entity_name = relationship.ref_from_type().get_namespace_name()
        client = self._get_client_for_type(entity_name)

        result: Noun = client.get_cached_instance_by_id(entity_name, id_)
        if result is None:
            result = client.get_entity(entity_name, id_)

        if not relationship in result.from_rels[relationship.get_namespace_name()]:
            result.from_rels[relationship.get_namespace_name()].append(relationship)

        return result

    def ref_to(self, relationship: Relationship) -> Any:
        id_ = relationship.ref_to

        entity_name = relationship.ref_to_type().get_namespace_name()
        client = self._get_client_for_type(entity_name)

        result = client.get_cached_instance_by_id(entity_name, id_)
        if result is None:
            result = client.get_entity(entity_name, id_)

        if not relationship in result.to_rels[relationship.get_namespace_name()]:
            result.to_rels[relationship.get_namespace_name()].append(relationship)

        return result

    def pull_relationship_nouns(
        self, relationships: List[Relationship]
    ) -> List[Relationship]:
        if len(relationships) == 0:
            return relationships

        # cache the entities using the get_entities method for performance...
        entity_name = relationships[0].ref_to_type().get_namespace_name()
        client = self._get_client_for_type(entity_name)
        entities_to_pull = [
            rel.ref_to
            for rel in relationships
            if not client.get_cached_instance_by_id(entity_name, rel.ref_to)
        ]
        if entities_to_pull:
            client.get_entities(entity_name, entities_to_pull)

        entity_name = relationships[0].ref_from_type().get_namespace_name()
        client = self._get_client_for_type(entity_name)
        client.get_entities(entity_name, [rel.ref_from for rel in relationships])
        entities_to_pull = [
            rel.ref_from
            for rel in relationships
            if not client.get_cached_instance_by_id(entity_name, rel.ref_from)
        ]
        if entities_to_pull:
            client.get_entities(entity_name, entities_to_pull)

        for relationship in relationships:
            self.ref_to(relationship)
            self.ref_from(relationship)

        return relationships
