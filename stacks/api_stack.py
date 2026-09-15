from aws_cdk import Stack
from constructs import Construct

from .constructs.network_construct import NetworkConstruct
from .constructs.auth_construct import AuthConstruct
from .constructs.api_construct import ApiConstruct

class ProtectedServerlessAiApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        network = NetworkConstruct(self, "NetworkModule")
        auth = AuthConstruct(self, "AuthModule")
        
        ApiConstruct(
            self, "ApiModule",
            vpc=network.vpc,
            authorizer=auth.authorizer
        )
