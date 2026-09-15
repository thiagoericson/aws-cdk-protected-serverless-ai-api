from pathlib import Path
from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_ec2 as ec2,
)
from constructs import Construct

SRC_DIR = str(Path(__file__).parent.parent / "src")

class ApiConstruct(Construct):
    def __init__(
        self, scope: Construct, id: str, 
        vpc: ec2.IVpc, authorizer, table, bucket, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Leitura dos parâmetros exportados pelo Repositório 1 via SSM
        guardrail_id = ssm.StringParameter.value_for_string_parameter(
            self, "/shared/guardrail/id"
        )
        guardrail_version = ssm.StringParameter.value_for_string_parameter(
            self, "/shared/guardrail/version"
        )

        # Lambda executada em Subnet Privada
        self.handler = lambda_.Function(
            self, "ProtectedAiApiHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=lambda_.Code.from_asset(SRC_DIR),
            timeout=Duration.seconds(30),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            environment={
                "GUARDRAIL_ID": guardrail_id,
                "GUARDRAIL_VERSION": guardrail_version,
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        # Permissão para chamar o Bedrock usando o Guardrail
        self.handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel", 
                    "bedrock:ApplyGuardrail",
                    "bedrock:InvokeModelWithResponseStream",
                    "kms:Decrypt"
                ],
                resources=["*"]
            )
        )

        table.grant_read_write_data(self.handler)
        bucket.grant_read_write(self.handler)

        # API Gateway HTTP com rota protegida por Cognito
        self.http_api = apigw.HttpApi(self, "ProtectedHttpApi")

        self.http_api.add_routes(
            path="/chat",
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration("LambdaIntegration", self.handler),
            authorizer=authorizer
        )
