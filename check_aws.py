#!/usr/bin/env python3
"""
AWS Credentials Checker for O-Zone MVP

This script helps verify your AWS setup for the hackathon.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("O-Zone AWS Credentials Checker")
print("=" * 60)
print()

# Check 1: Environment variables
print("📋 Step 1: Checking environment variables...")
aws_region = os.getenv("AWS_REGION")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

if not aws_region:
    print("❌ AWS_REGION not set in .env file")
    sys.exit(1)
else:
    print(f"✅ AWS_REGION: {aws_region}")

if not aws_access_key:
    print("❌ AWS_ACCESS_KEY_ID not set in .env file")
    sys.exit(1)
else:
    print(f"✅ AWS_ACCESS_KEY_ID: {aws_access_key[:10]}...")

if not aws_secret_key:
    print("❌ AWS_SECRET_ACCESS_KEY not set in .env file")
    sys.exit(1)
else:
    print(f"✅ AWS_SECRET_ACCESS_KEY: {aws_secret_key[:10]}...")

print()

# Check 2: boto3 installed
print("📦 Step 2: Checking boto3 installation...")
try:
    import boto3
    print(f"✅ boto3 installed (version {boto3.__version__})")
except ImportError:
    print("❌ boto3 not installed. Run: pip install boto3")
    sys.exit(1)

print()

# Check 3: AWS credentials valid
print("🔐 Step 3: Validating AWS credentials...")
try:
    sts = boto3.client('sts', region_name=aws_region)
    identity = sts.get_caller_identity()
    print(f"✅ Credentials valid!")
    print(f"   Account: {identity['Account']}")
    print(f"   User ARN: {identity['Arn']}")
except Exception as e:
    print(f"❌ Credentials invalid: {e}")
    sys.exit(1)

print()

# Check 4: Bedrock access
print("🤖 Step 4: Checking Amazon Bedrock access...")
try:
    bedrock = boto3.client('bedrock', region_name=aws_region)
    models = bedrock.list_foundation_models()
    
    # Check for Claude 3.5 Sonnet
    claude_models = [m for m in models['modelSummaries'] 
                     if 'claude-3-5-sonnet' in m['modelId'].lower()]
    
    if claude_models:
        print(f"✅ Bedrock access confirmed!")
        print(f"   Found {len(models['modelSummaries'])} total models")
        print(f"   Claude 3.5 Sonnet: Available")
    else:
        print(f"⚠️  Bedrock accessible but Claude 3.5 Sonnet not found")
        print(f"   Available models: {len(models['modelSummaries'])}")
        print(f"   You may need to request model access")
except Exception as e:
    print(f"❌ Bedrock access error: {e}")
    print(f"   Ask hackathon organizers to enable Bedrock access")
    sys.exit(1)

print()

# Check 5: Test Bedrock invocation
print("🧪 Step 5: Testing Bedrock model invocation...")
try:
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
    
    # Simple test prompt
    import json
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello from O-Zone!' in exactly 5 words."
            }
        ]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Using inference profile
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    ai_response = response_body['content'][0]['text']
    
    print(f"✅ Bedrock invocation successful!")
    print(f"   AI Response: {ai_response}")
except Exception as e:
    print(f"❌ Bedrock invocation failed: {e}")
    print(f"   This might be a permissions or model access issue")
    sys.exit(1)

print()
print("=" * 60)
print("🎉 All checks passed! Your AWS setup is ready!")
print("=" * 60)
print()
print("Next steps:")
print("1. Run the app: streamlit run src/app.py")
print("2. Try a location: San Francisco, Los Angeles, etc.")
print("3. Get AI-powered recommendations!")
print()
