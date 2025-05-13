import boto3
from botocore.exceptions import ClientError
from .config import COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name="ap-southeast-1")
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID

    def authenticate_user(self, username, password):
        try:
            response = self.client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password
                },
                ClientId=self.client_id
            )
            return response["AuthenticationResult"]["AccessToken"]
        except ClientError as e:
            raise Exception(f"Authentication failed: {e}")

    def get_user_info(self, access_token):
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except ClientError as e:
            raise Exception(f"Failed to get user info: {e}")