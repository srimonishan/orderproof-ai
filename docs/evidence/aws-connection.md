# Coding agent AWS connection evidence

Verification recorded: 2026-09-19T03:59:20Z.
Agent: Codex, operating in the OrderProof project workspace.

## Verified actions

1. Ran `aws --version` in the local shell: AWS CLI 2.36.28.
2. Ran `aws sts get-caller-identity` with network access: succeeded.
3. Called the configured AWS MCP connector's `aws___run_script` tool with a read-only STS `GetCallerIdentity` request: succeeded.
4. Verified both responses identified the same AWS account and IAM user.

Redacted response for public documentation:

```json
{
  "Account": "********0965",
  "Arn": "arn:aws:iam::********0965:user/reliefloop-ai-deployer"
}
```

Successful MCP execution evidence:

```json
{
  "status": "success",
  "api_calls": [
    {"service": "sts", "operation": "GetCallerIdentity", "status": "success"}
  ]
}
```

The initial sandboxed CLI attempt could not reach the STS endpoint. A network-enabled retry succeeded. The first MCP request used an unsupported lowercase operation name; retrying with `GetCallerIdentity` succeeded.

## What this proves

The coding agent successfully authenticated to AWS through the CLI and AWS MCP. This check does not establish deployment permissions, Bedrock model access, a browser console session, or acceptance of this artifact by hackathon reviewers.

## Evidence still to capture

- Screenshot or recording of the agent's successful AWS MCP call, with credentials and account identifiers redacted.
- Screenshot of the deployed OrderProof resources in the AWS console.
- Deployment output and live URL, plus dated public reachability checks.
- Recheck the event's exact evidence requirements before submission.

Never include access keys, session tokens, credential files, login URLs, or customer conversations in public evidence.
