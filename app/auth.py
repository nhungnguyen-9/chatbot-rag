import boto3
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError
from .config import (
    COGNITO_USER_POOL_ID,
    COGNITO_CLIENT_ID,
    COGNITO_CLIENT_SECRET,
    COGNITO_IDENTITY_POOL_ID,
)

def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    digest = hmac.new(client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name="ap-southeast-1")
        self.identity_client = boto3.client("cognito-identity", region_name="ap-southeast-1")
        self.user_pool_id = COGNITO_USER_POOL_ID
        self.client_id = COGNITO_CLIENT_ID
        self.client_secret = COGNITO_CLIENT_SECRET
        self.identity_pool_id = COGNITO_IDENTITY_POOL_ID

    def sign_up(self, username, password, email):
        try:
            secret_hash = get_secret_hash(username, self.client_id, self.client_secret)
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                SecretHash=secret_hash,
                UserAttributes=[
                    {'Name': 'email', 'Value': email}
                ]
            )
            return response
        except ClientError as e:
            raise Exception(f"Sign-up failed: {e}")

    def authenticate_user(self, username, password):
        try:
            secret_hash = get_secret_hash(username, self.client_id, self.client_secret)
            response = self.client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password,
                    "SECRET_HASH": secret_hash
                },
                ClientId=self.client_id
            )

            id_token = response["AuthenticationResult"]["IdToken"]

            identity_response = self.identity_client.get_id(
                IdentityPoolId=self.identity_pool_id,
                Logins={
                    f"cognito-idp.ap-southeast-1.amazonaws.com/{self.user_pool_id}": id_token
                }
            )
            identity_id = identity_response["IdentityId"]

            credentials_response = self.identity_client.get_credentials_for_identity(
                IdentityId=identity_id,
                Logins={
                    f"cognito-idp.ap-southeast-1.amazonaws.com/{self.user_pool_id}": id_token
                }
            )
            credentials = credentials_response["Credentials"]
            return {
                "id_token": id_token,
                "credentials": {
                    "access_key": credentials["AccessKeyId"],
                    "secret_key": credentials["SecretKey"],
                    "session_token": credentials["SessionToken"]
                }
            }

        except ClientError as e:
            raise Exception(f"Authentication failed: {e}")

    def get_user_info(self, access_token):
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except ClientError as e:
            raise Exception(f"Failed to get user info: {e}")
