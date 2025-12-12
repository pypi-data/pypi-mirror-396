"""AWS Bedrock client for Claude API"""

import json
import os
import boto3
from typing import Dict, List, Any, Optional
from botocore.config import Config


class BedrockClient:
    """Client for interacting with Claude via AWS Bedrock"""

    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """Initialize Bedrock client

        Args:
            model_id: Claude model ID (e.g., anthropic.claude-3-5-sonnet-20241022-v2:0)
            region: AWS region (defaults to us-east-1)
            aws_access_key_id: AWS access key (optional if using AWS CLI config)
            aws_secret_access_key: AWS secret key (optional if using AWS CLI config)
        """
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        # Configure boto3 client
        config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )

        session_kwargs = {}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs = {
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
            }

        self.client = boto3.client(
            "bedrock-runtime",
            config=config,
            **session_kwargs
        )

    def send_message(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 1.0,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send a message to Claude via Bedrock

        Args:
            messages: List of message dictionaries
            system: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            tools: List of tool definitions

        Returns:
            Response dictionary from Claude
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system:
            request_body["system"] = system

        if tools:
            request_body["tools"] = tools

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())
            return response_body

        except Exception as e:
            raise Exception(f"Bedrock API error: {str(e)}")

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 1.0,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """Stream a conversation with Claude

        Args:
            messages: List of message dictionaries
            system: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            tools: List of tool definitions

        Yields:
            Response chunks from Claude
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system:
            request_body["system"] = system

        if tools:
            request_body["tools"] = tools

        try:
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                yield chunk

        except Exception as e:
            raise Exception(f"Bedrock streaming error: {str(e)}")
