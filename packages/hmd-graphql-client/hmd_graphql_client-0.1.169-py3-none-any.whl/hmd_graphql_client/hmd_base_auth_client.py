from typing import Callable, Optional
from hmd_schema_loader import DefaultLoader
from .hmd_base_client import BaseClient
from hmd_lib_auth.lambda_helper import is_token_expired


class BaseAuthClient(BaseClient):
    def __init__(
        self,
        loader: DefaultLoader,
        auth_token: str = None,
        expired_auth_token_callback: Callable = None,
    ):
        self.auth_token = auth_token
        self.expired_auth_token_callback = expired_auth_token_callback
        super().__init__(loader=loader)

    def get_auth_token(self) -> Optional[str]:
        token = self.auth_token

        if token and self.expired_auth_token_callback and is_token_expired(token):
            token = self.expired_auth_token_callback()

        return token
