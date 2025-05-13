from aws_cdk import Stack
from aws_cdk import aws_opensearchservice as opensearch
from constructs import Construct

class OpenSearchStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.domain = opensearch.Domain(
            self, "RagChatbotDomain",
            version=opensearch.EngineVersion.OPENSEARCH_2_3,
            domain_name="rag-chatbot",
            capacity=opensearch.CapacityConfig(
                data_nodes=1,
                data_node_instance_type="t3.small.search"
            ),
            ebs=opensearch.EbsOptions(
                enabled=True,
                volume_size=10
            )
        )