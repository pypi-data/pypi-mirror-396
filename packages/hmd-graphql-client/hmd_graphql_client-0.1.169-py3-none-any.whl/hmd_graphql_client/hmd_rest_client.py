from json import JSONDecodeError
from typing import List, Dict, Callable, Tuple

import requests
from dateutil.parser import isoparse
from requests.compat import urljoin

from hmd_meta_types import Relationship, Noun, Entity
from hmd_schema_loader import DefaultLoader
from .hmd_base_auth_client import BaseAuthClient


def handle_error(response):
    if response.status_code != 200:
        try:
            result = response.json()
        except JSONDecodeError as ex:
            result = {"message": response.text}
        raise Exception(result["message"] if "message" in result else result)


class RestClient(BaseAuthClient):
    def __init__(
        self,
        base_url: str,
        loader: DefaultLoader,
        api_key: str = None,
        auth_token: str = None,
        expired_auth_token_callback: Callable = None,
        extra_headers: Dict[str, str] = None,
        client_certs: Tuple[str, str] = None,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.extra_headers = extra_headers or {}
        self.client_cert = client_certs
        super().__init__(loader, auth_token, expired_auth_token_callback)

    def _get_headers(self):
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        if self.auth_token:
            headers["Authorization"] = self.get_auth_token()
        elif self.client_cert:
            headers["Authorization"] = "certs"
        if self.extra_headers:
            headers.update(self.extra_headers)
        return {"headers": headers} if headers else {}

    def _do_get_entity(self, entity_name: str, id: int):
        r = requests.get(
            urljoin(f"{self.base_url}", f"api/{entity_name}/{id}"),
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)
        response = r.json()
        return Entity.deserialize(self.loader.get_class(entity_name), response)

    def _do_get_entities(self, entity_name: str, ids_: List[str]):
        r = requests.post(
            urljoin(f"{self.base_url}", f"api/instances/{entity_name}"),
            json=ids_,
            **self._get_headers(),
            cert=self.client_cert,
        )
        handle_error(r)
        response = r.json()
        return [
            Entity.deserialize(self.loader.get_class(entity_name), resp)
            for resp in response
        ]

    def _do_search_entity(self, entity_name: str, filter_: dict = {}) -> List[Entity]:
        r = requests.post(
            urljoin(f"{self.base_url}", f"api/{entity_name}"),
            json=filter_,
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)

        response = r.json()
        entity = self.loader.get_class(entity_name)
        return [Entity.deserialize(entity, data) for data in response]

    def _do_delete_entity(self, entity_name: str, id: int):
        r = requests.delete(
            urljoin(f"{self.base_url}", f"api/{entity_name}/{id}"),
            **self._get_headers(),
            cert=self.client_cert,
        )
        handle_error(r)

    def _do_upsert_entity(self, entity: Entity):
        r = requests.put(
            urljoin(f"{self.base_url}", f"api/{type(entity).get_namespace_name()}"),
            json=entity.serialize(),
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)

        response = r.json()
        entity.identifier = response["identifier"]
        if "_created" in response:
            entity._created = isoparse(response["_created"])
        if "_updated" in response:
            entity._updated = isoparse(response["_updated"])
        return entity

    def _get_relationships(
        self, from_to: str, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        assert from_to in ["from", "to"], f'Invalid "from_to": {from_to}'

        # verify the relationship type matches the entity...
        sidea = from_to
        sideb = "from" if from_to == "to" else "to"

        relationship_class = self.loader.get_class(relationship_type)
        assert getattr(relationship_class, f"ref_{sidea}_type")() == type(noun)

        r = requests.get(
            urljoin(
                f"{self.base_url}",
                f"api/{relationship_type}/{sidea}/{noun.identifier}",
            ),
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)

        response = r.json()

        rels = []
        data = response
        for rel in data:
            rels.append(Entity.deserialize(relationship_class, rel))

        return rels

    def _do_get_relationships_from(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        return self._get_relationships("from", noun, relationship_type)

    def _do_get_relationships_to(
        self, noun: Noun, relationship_type: str
    ) -> List[Relationship]:
        return self._get_relationships("to", noun, relationship_type)

    def _do_invoke_custom_operation(
        self, operation_name: str, payload: Dict, http_method: str = "POST"
    ):
        r = requests.request(
            http_method,
            urljoin(f"{self.base_url}", f"apiop/{operation_name}"),
            json=payload,
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)

        response = r.json()
        return response

    def _do_upsert_entities(self, nouns: List[Noun], relationships: List[Relationship]):
        r = requests.put(
            urljoin(f"{self.base_url}", f"api/entities"),
            json={
                "nouns": [n.serialize(include_schema=True) for n in nouns],
                "relationships": [
                    r.serialize(include_schema=True) for r in relationships
                ],
            },
            **self._get_headers(),
            cert=self.client_cert,
            timeout=30,
        )
        handle_error(r)

        response = r.json()
        return response
