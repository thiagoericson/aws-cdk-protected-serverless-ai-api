import os
import json
import boto3

bedrock = boto3.client("bedrock-runtime")

def handler(event, context):
    guardrail_id = os.environ["GUARDRAIL_ID"]
    guardrail_version = os.environ["GUARDRAIL_VERSION"]

    body = json.loads(event.get("body", "{}"))
    user_prompt = body.get("prompt", "Hello")

    try:
        # Invocação do Bedrock passando as credenciais do Guardrail importado
        response = bedrock.converse(
            modelId="us.amazon.nova-lite-v1:0",
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            guardrailConfig={
                "guardrailIdentifier": guardrail_id,
                "guardrailVersion": guardrail_version,
                "trace": "enabled"
            }
        )
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"response": response["output"]["message"]["content"][0]["text"]})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
