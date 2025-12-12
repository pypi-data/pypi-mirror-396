# Installation Guide

Complete installation instructions for Claude Bedrock CLI.

## Prerequisites

### 1. Python

You need Python 3.8 or higher.

Check your Python version:
```bash
python --version
# or
python3 --version
```

If you don't have Python, install it:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Mac**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### 2. AWS Account

You need an AWS account with:
- Bedrock service access
- Claude model access enabled
- Valid credentials (Access Key ID and Secret Access Key)

### 3. Git (Optional)

To clone the repository:
```bash
git clone <repository-url>
cd claude-bedrock-cli
```

## Installation Methods

### Method 1: Local Development Install (Recommended)

This method is best for development and customization.

```bash
# Navigate to the project directory
cd claude-bedrock-cli

# Install in editable mode
pip install -e .

# Verify installation
claude-bedrock --help
```

### Method 2: Direct Install

Install dependencies directly:

```bash
cd claude-bedrock-cli
pip install -r requirements.txt

# Run using Python module
python -m claude_cli.main
```

### Method 3: Virtual Environment (Best Practice)

Use a virtual environment to avoid conflicts:

```bash
cd claude-bedrock-cli

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .

# Run
claude-bedrock
```

## AWS Configuration

### Method 1: AWS CLI (Recommended)

If you have AWS CLI installed:

```bash
aws configure
```

Enter:
- AWS Access Key ID: `YOUR_ACCESS_KEY`
- AWS Secret Access Key: `YOUR_SECRET_KEY`
- Default region name: `us-east-1`
- Default output format: `json`

### Method 2: Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Method 3: IAM Role (For EC2/ECS)

If running on AWS infrastructure, attach an IAM role with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    }
  ]
}
```

## Enable Bedrock Model Access

### Step 1: Navigate to Bedrock Console

Go to: https://console.aws.amazon.com/bedrock/

### Step 2: Request Model Access

1. Click "Model access" in the left sidebar
2. Click "Manage model access" button
3. Find "Anthropic" in the list
4. Check the boxes for:
   - Claude 3.5 Sonnet
   - Claude 3 Opus (optional)
   - Claude 3 Haiku (optional)
5. Click "Request model access"
6. Wait for approval (usually instant)

### Step 3: Verify Access

```bash
# List available models (requires AWS CLI)
aws bedrock list-foundation-models --region us-east-1
```

## Verify Installation

### Test 1: Check Installation

```bash
# If installed via setup.py
claude-bedrock --help

# Or run directly
python -m claude_cli.main --help
```

### Test 2: Test AWS Connection

Create a test script `test_bedrock.py`:

```python
import boto3
import json

client = boto3.client('bedrock-runtime', region_name='us-east-1')

try:
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        })
    )
    print("✅ Bedrock connection successful!")
    print(json.loads(response['body'].read()))
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python test_bedrock.py
```

### Test 3: Run Claude CLI

```bash
claude-bedrock

# Or
python -m claude_cli.main
```

Type: `Hello!` and press Enter. You should get a response from Claude.

## Platform-Specific Instructions

### Windows

```powershell
# Install Python from python.org
# Open PowerShell as Administrator

cd claude-bedrock-cli
python -m venv venv
venv\Scripts\activate
pip install -e .

# Run
claude-bedrock

# Or use the batch file
.\run.bat
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Install CLI
cd claude-bedrock-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run
claude-bedrock

# Or use the shell script
chmod +x run.sh
./run.sh
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Install CLI
cd claude-bedrock-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run
claude-bedrock

# Or use the shell script
chmod +x run.sh
./run.sh
```

## Docker Installation (Optional)

Create a Docker image:

```bash
# Build
docker build -t claude-bedrock-cli .

# Run
docker run -it --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-east-1 \
  -v $(pwd):/workspace \
  claude-bedrock-cli --working-dir /workspace
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["claude-bedrock"]
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'claude_cli'"

**Solution:**
```bash
pip install -e .
```

### Issue: "AWS credentials not found"

**Solutions:**
1. Run `aws configure`
2. Create `.env` file with credentials
3. Check environment variables: `echo $AWS_ACCESS_KEY_ID`

### Issue: "Access Denied" when calling Bedrock

**Solutions:**
1. Verify model access is enabled in Bedrock Console
2. Check IAM permissions
3. Verify region is correct (us-east-1)
4. Test with AWS CLI:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

### Issue: "Model not found"

**Solutions:**
1. Check model ID in `.env` matches exactly
2. Verify model is available in your region
3. Try a different model ID:
   ```env
   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

### Issue: "Rate limit exceeded"

**Solution:**
This means you're making too many requests. Wait a few seconds and try again.

### Issue: "Timeout errors"

**Solutions:**
1. Check internet connection
2. Try a different AWS region
3. Increase timeout in code if needed

### Issue: Dependencies installation fails

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies one by one
pip install boto3
pip install anthropic
pip install rich
pip install prompt-toolkit
pip install click
pip install pyyaml
pip install python-dotenv
```

## Updating

To update to the latest version:

```bash
cd claude-bedrock-cli
git pull  # If using git
pip install -e . --upgrade
```

## Uninstalling

```bash
pip uninstall claude-bedrock-cli

# Or if installed in editable mode
cd claude-bedrock-cli
pip uninstall -e .

# Remove configuration files
rm .env
rm .claude_history
rm .claude_prompt_history
```

## Next Steps

After installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for a quick guide
2. Check [EXAMPLES.md](EXAMPLES.md) for usage examples
3. Review [README.md](README.md) for full documentation

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review the [README.md](README.md) troubleshooting section
3. Verify AWS credentials and Bedrock access
4. Check AWS Bedrock documentation
5. Test with the simple bedrock test script above

---

Happy coding with Claude! 🚀
