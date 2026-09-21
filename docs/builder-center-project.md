# OrderProof: support that keeps its word

Tags: `#commercial-potential` `#startup`

Live application: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com
Reviewer guide: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com/review
Repository: https://github.com/srimonishan/orderproof-ai

## The problem

For a small online business, a simple return question can become a fragmented exchange: a bot quotes a policy, a person takes over, and the customer later needs to find what was said. OrderProof keeps the answer, handoff, and record together.

## What I built

OrderProof is an embeddable support workspace. A business approves its own policies, installs a website widget, and manages customer conversations in one inbox. The model integration retrieves relevant approved passages and validates source identifiers. A person can join the same conversation. On closure, the service creates a versioned archive that can be checked against the conversation’s hash chain. The customer can export the transcript too. An offline Python verifier checks exported event and citation integrity without AWS credentials; a separately trusted digest is necessary to detect a wholly rewritten chain. Historical citations survive source removal, while future retrieval excludes the removed source.

The distinctive workflow is not simply storing messages: it connects the source passage used for an answer, the subsequent human conversation, and the preserved result. The resulting record is tamper-evident within its documented verification scope; it is not an independent proof of identity, legal certification, or an archive that no administrator can alter.

## How it runs on AWS

API Gateway and Python Lambda serve the interface and API. Cognito authenticates businesses. DynamoDB isolates business knowledge and records events transactionally. S3 provides private, versioned transcript archives with 30-day governance retention. Amazon Bedrock Nova Lite is the configured model, invoked through IAM. AWS SAM defines the deployment.

The retrieval layer uses bounded lexical search for small company knowledge collections. It is not a managed Knowledge Base or a vector database. Website and React integration examples, hosted chat, and mobile WebView examples are provided.

## How the coding agent helped

I worked with the coding agent on the product requirements, interface, retrieval and human handoff, access controls, infrastructure, deployment, and debugging. The agent used AWS CLI and AWS MCP connectivity, implemented automated tests, and recorded deployment and live integration evidence. The development process included explicit verification of failure behavior, tenant isolation, retry handling, and archive integrity rather than relying only on screenshots.

Connection evidence: `docs/evidence/aws-connection.md`. Acceptance of the evidence format must be checked against the event’s Rules.

## What is verified—and what is not

Live tests verify approved knowledge storage, tenant isolation, customer-message persistence, idempotent retries, human handoff and reply, closed-record integrity, S3 archive matching, and transcript export. Automated tests cover retrieval selection and model-response validation.

**Current blocker:** the AWS account reports zero daily Nova token quotas. Live model calls return a token quota error. The deployed application explicitly saves the message and offers human support. The public demo labels its prepared responses as fictional. Successful live AI quality is not claimed; this disclosure must remain until model access is restored and live evaluation passes.

Stripe is intentionally deferred; selecting a proposed plan does not charge or activate a subscription. Reviewer access can be granted for a bounded period while retaining usage limits. Native mobile apps, voice calling, and multiple support staff roles are not implemented.

## Startup direction

The initial audience is small online businesses with recurring shipping and return-policy questions and a single support owner. The product hypothesis is that keeping answers, handoffs, and records together reduces repeated explanations and makes follow-up easier. The seven-day trial and proposed subscription tiers provide an initial commercial model, not evidence of revenue or product-market fit.

Next validation: observe real businesses handling policy questions, measure how often answers require correction, time a handoff, and check whether both sides can locate and export the record. No customer adoption, revenue, or time-saving measurements are claimed yet. A consent-based pilot protocol, blank observation sheet, and report generator are prepared in `docs/pilot/`; actual participation and results remain pending.

## Short demonstration

1. Show the approved returns policy.
2. Ask a policy question in the customer widget and inspect the source reference when model access works; otherwise disclose and demonstrate the fallback.
3. Request a person and reply from the owner inbox.
4. Close the conversation, verify it, and export the transcript.
5. Show the installation snippet and explain the operating limits.

This is a prepared project draft, not evidence that a Builder Center submission has been published or accepted.
