from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.fn = _lambda.Function(
            self, "RagChatbotFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../app")
        )