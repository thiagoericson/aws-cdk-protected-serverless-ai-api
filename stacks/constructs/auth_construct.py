from aws_cdk import (
    aws_cognito as cognito,
    aws_apigatewayv2_authorizers as authorizers,
)
from constructs import Construct

class AuthConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Pool de usuários no Amazon Cognito
        self.user_pool = cognito.UserPool(
            self, "ApiUserPool",
            user_pool_name="enterprise-api-user-pool",
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            # 1. Set to DESTROY the resource when runs the `cdk destroy`, even with user data (DON'T USE THAT IN REAL PRODUCTION ENV)
            removal_policy=RemovalPolicy.DESTROY,
            # 2. Force the user data exclusion on destroy stack (DON'T USE THAT IN REAL PRODUCTION ENV)
            auto_delete_users=True
        )

        # Client da aplicação
        self.user_pool_client = self.user_pool.add_client(
            "ApiUserPoolClient",
            user_pool_client_name="enterprise-api-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,  # Habilita USER_PASSWORD_AUTH
                admin_user_password=True,
            ),
        )

        # Authorizer JWT para o API Gateway
        self.authorizer = authorizers.HttpUserPoolAuthorizer(
            "UserPoolAuthorizer",
            self.user_pool,
            user_pool_clients=[self.user_pool_client]
        )
