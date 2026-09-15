#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.api_stack import ProtectedServerlessAiApiStack

app = cdk.App()

ProtectedServerlessAiApiStack(
    app, 
    "ProtectedServerlessAiApiStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION")
    )
)

app.synth()
