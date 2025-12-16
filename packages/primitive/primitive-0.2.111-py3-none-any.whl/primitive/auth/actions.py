from gql import gql

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from ..utils.config import read_config_file, update_config_file
from .graphql.queries import whoami_query
from .graphql.mutations import authentication_token_create


class Auth(BaseAction):
    @guard
    def whoami(self):
        query = gql(whoami_query)

        result = self.primitive.session.execute(query, get_execution_result=True)

        return result

    def setup_config(
        self,
        token: str,
        host: str = "api.primitive.tech",
        transport: str = "https",
    ):
        full_config = read_config_file()
        new_host_config = {
            "token": token,
            "transport": transport,
        }

        if existing_host_config := full_config.get(host, None):
            full_config[host] = {**existing_host_config, **new_host_config}
        else:
            full_config[host] = new_host_config
        update_config_file(new_config=full_config)

    @guard
    def create_token(self, key_name: str):
        mutation = gql(authentication_token_create)
        variables = {"input": {"keyName": key_name}}

        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )

        return result

    @guard
    async def acreate_token(self, key_name: str):
        mutation = gql(authentication_token_create)
        variables = {"input": {"keyName": key_name}}

        result = await self.primitive.session.execute_async(
            mutation, variable_values=variables, get_execution_result=True
        )

        return result
