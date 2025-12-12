# Quick Start Guide

Get up and running with Claude Bedrock CLI in 5 minutes!

## Step 1: Install the CLI

```bash
pip install claude-bedrock-cli
```

That's it! The `claude-bedrock` command is now available globally.

## Step 2: Configure AWS

### Option A: Use AWS CLI (Recommended)
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

### Option B: Use Environment Variables

Create a `.env` file in your working directory:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

## Step 3: Enable Bedrock Model Access

1. Go to [AWS Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to: Bedrock → Model access
3. Click "Manage model access"
4. Enable "Claude 3.5 Sonnet"
5. Click "Save changes"

Wait a few seconds for approval (usually instant).

## Step 4: Run the CLI

```bash
claude-bedrock
```

That's it! The CLI will start and you can begin chatting with Claude.

## Step 5: Start Using Claude!

Try these commands:

```
> Hello! Can you help me create a Python script?

> Read the README.md file

> Search for all Python files in this directory

> Run ls to show me the files here
```

**Interactive Approvals:** When Claude wants to write files or run commands, you'll see:
- Preview of changes with line numbers and diffs
- Arrow key selection menu (↑↓ to navigate, Enter to confirm)
- Choose: Approve, Reject, or Approve All

## Common Issues

**"Access Denied"**
- Check AWS credentials are correct
- Verify Bedrock model access is enabled
- Check IAM permissions

**"Model Not Found"**
- Make sure you're using the right region (us-east-1)
- Verify model ID in .env matches an enabled model

**"No module named 'claude_cli'"**
- Run: `pip install -e .`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Try complex tasks like code refactoring
- Explore the `/todos` command for task tracking
- Customize the model in `.env`

## Cost Estimate

Typical usage costs (approximate):
- Simple question: $0.001 - $0.01
- File editing: $0.01 - $0.05
- Complex task: $0.05 - $0.20

These are estimates using Claude 3.5 Sonnet. Actual costs vary based on conversation length.

---

**That's it! You're ready to code with Claude using your AWS Bedrock subscription.** 🎉
