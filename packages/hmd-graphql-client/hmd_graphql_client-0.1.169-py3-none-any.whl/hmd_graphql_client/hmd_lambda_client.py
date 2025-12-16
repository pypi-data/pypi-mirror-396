from json import dumps, loads
from typing import List, Dict, Callable

from boto3 import Session
from dateutil.parser import isoparse

from hmd_cli_tools.hmd_cli_tools import get_account_session
from hmd_meta_types import Relationship, Noun, Entity
from hmd_schema_loader import DefaultLoader
from .hmd_base_auth_client import BaseAuthClient


class LambdaClient(BaseAuthClient):
    """A BaseClient implementation that executes by directly invoking a lambda function.

    Cross-account execution is supported with the assume_role_info parameter.

    """

    def __init__(
        self,
        lambda_name: str,
        loader: DefaultLoader,
        assume_role_info: Dict[str, str] = None,
        invocation_type: str = "RequestResponse",
        auth_token: str = None,
        expired_auth_token_callback: Callable = None,
    ):
        """Constructor

        :param lambda_name: The name of the lambda function to call.
        :param loader: A `DefaultLoader` instance to
        :param assume_role_info: The account and role to assume prior to function execution.

        The form of the `assume_role_info` is::

            {
              "account": "123456789",
              "role": "role_name"
            }
        """
        self.lambda_name = lambda_name
        self.assume_role_info = assume_role_info
        self.invocation_type = invocation_type
        super().__init__(loader, auth_token, expired_auth_token_callback)

    def _call_lambda(self, payload: Dict):
        session = Session()
        if self.assume_role_info:
            session = get_account_session(
                session, self.assume_role_info["account"], self.assume_role_info["role"]
            )

        if self.auth_token:
            payload["headers"] = {"Authorization": self.get_auth_token()}

        # Add "resource" and "requestContext" to payload so FastAPI based services can properly handle event.
        if "resource" not in payload:
            payload["resource"] = {}

        if "requestContext" not in payload:
            payload["requestContext"] = {}

        lambda_client = session.client("lambda")
        lambda_result = lambda_client.invoke(
            FunctionName=self.lambda_name,
            Payload=dumps(payload),
            InvocationType=self.invocation_type,
        )

        # This shouldn't happen because we catch exceptions and return from the lambda
        # Still...
        status_code = 200 if self.invocation_type == "RequestResponse" else 202
        if lambda_result["StatusCode"] != status_code:
            raise Exception(lambda_result["Payload"])

        if self.invocation_type == "RequestResponse":
            # The result payload should be a dict with "statusCode" and "body"
            result_payload = loads(lambda_result["Payload"].read())
            if result_payload.get("statusCode") != 200:
                raise Exception(result_payload["body"])

            return loads(result_payload.get("body", "{}"))

    def _do_get_entity(self, entity_name: str, id: int):
        response = self._call_lambda(
            {"path": f"/api/{entity_name}/{id}", "httpMethod": "GET", "body": None}
        )

        return Entity.deserialize(self.loader.get_class(entity_name), response)

    def _do_get_entities(self, entity_name: str, ids_: List[str]):
        response = self._call_lambda(
            {"path": f"/api/instances/{entity_name}", "httpMethod": "GET", "body": ids_}
        )

        return [
            Entity.deserialize(self.loader.get_class(entity_name), resp)
            for resp in response
        ]

    def _do_search_entity(self, entity_name: str, filter_: dict = {}) -> List[Entity]:
        response = self._call_lambda(
            {
                "path": f"/api/{entity_name}",
                "httpMethod": "POST",
                "body": dumps(filter_),
            }
        )

        entity = self.loader.get_class(entity_name)
        return [Entity.deserialize(entity, data) for data in response]

    def _do_delete_entity(self, entity_name: str, id: int):
        response = self._call_lambda(
            {"path": f"/api/{entity_name}/{id}", "httpMethod": "DELETE", "body": None}
        )

    def _do_upsert_entity(self, entity: Entity):
        response = self._call_lambda(
            {
                "path": f"/api/{entity.get_namespace_name()}",
                "httpMethod": "PUT",
                "body": dumps(entity.serialize()),
            }
        )

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

        response = self._call_lambda(
            {
                "path": f"/api/{relationship_type}/{sidea}/{noun.identifier}",
                "httpMethod": "GET",
                "body": None,
            }
        )

        rels = []
        for rel in response:
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
        return self._call_lambda(
            {
                "path": f"/apiop/{operation_name}",
                "httpMethod": http_method,
                "body": dumps(payload),
            }
        )

    def _do_upsert_entities(self, nouns: List[Noun], relationships: List[Relationship]):
        return self._call_lambda(
            {
                "path": f"/api/entities",
                "httpMethod": "PUT",
                "body": dumps(
                    {
                        "nouns": [n.serialize(include_schema=True) for n in nouns],
                        "relationships": [
                            r.serialize(include_schema=True) for r in relationships
                        ],
                    }
                ),
            }
        )
