# Trial, billing, and release operations

The seven-day trial starts on first workspace creation and is enforced server-side. Trial allowances: 100 AI attempts per calendar month, 20 sources, 3 website origins. On expiry, reading/exporting saved records remains available; new messages, agent replies, and source creation stop. Closing/sealing existing conversations is still allowed.

Proposed monthly plans: Starter $19 (250 AI attempts, 10 sources, 1 origin), Growth $49 (1,000 attempts, 20 sources, 3 origins), Scale $99 (3,000 attempts, 50 sources, 5 origins). All currently include one owner-operated inbox, integrations, branding, exports, and 90-day history. Selecting a plan only records a preference. There is no checkout, charge, automatic renewal, or paid activation.

Before enabling Stripe: add server-created Checkout Sessions with a fixed allowlist of Stripe price IDs; verified webhook signatures; idempotent webhook processing; server-managed subscription status/period-end; customer portal; cancellation and failed-payment handling; and test-mode lifecycle checks. Never trust a browser-supplied plan or payment-success URL. Store credentials in managed secrets, not chat or source control. Review the shared AI cost ceiling before activating plans with larger allowances. This release does not claim Stripe integration is complete.

## Cost assumptions

`docs/evidence/cost-estimate.json` models low traffic without relying on free-tier eligibility: about $2.56/month, with a $5 planning allowance within the authorized $10 target. There is a shared 500 AI-attempt/month ceiling and 500 new support conversations/month, plus per-conversation and per-business limits. Static pages and polling also generate API/Lambda requests. These are usage controls, not an AWS billing hard cap. Tax, abusive traffic, changing rates, retained data, or unrelated resources may increase the account bill. No hackathon prize credits are assumed.

The implementation avoids always-on databases, NAT gateways, vector servers, and paid search clusters. Passage retrieval is lexical ranking over approved tenant documents, followed by Bedrock generation; this is a small-corpus retrieval implementation, not a managed Bedrock Knowledge Base or vector search deployment.

Recommended production observability beyond this budgeted pilot: S3 access logging, scoped CloudTrail object data events, request/error metrics and alarms, and tenant-level usage reporting. These incur request/logging charges and need a revised budget at larger scale. Current application/API operational logs have seven-day retention and omit intentional message-body/token logging.

## Bedrock account blocker (2026-09-20)

Nova Lite in us-west-2 is configured via Lambda IAM; no model API key is needed. Realistic calls return `ThrottlingException: Too many tokens per day`. The account's cross-region Nova Lite TPM quota is 0 (L-7C42E72A); a requested value of 10,000 was rejected because the quota service requires a value greater than its published default of 8,000,000. The on-demand daily quota was also 0 and non-adjustable in the prior check. No increase was accepted. Anthropic returned a location restriction and was not used.

The account owner must resolve Bedrock account/quota availability through the AWS Bedrock / Service Quotas console or AWS Support. Provide the exact region, model, quota codes, and errors above; request access suitable for this small capped pilot. Do not misrepresent the deployment location or bypass location restrictions. After access is enabled, run real grounded-answer evaluations and the live smoke test; if switching to an inference profile, update its model ID and IAM resource scope together. The app currently saves the question and explicitly offers human support when model invocation fails.

Final Nova Micro check: the AWS-listed `us.amazon.nova-micro-v1:0` inference profile also returned the daily-token throttle with a 64-output-token grounded policy question. Its daily quota L-D2912E70 and cross-region TPM quota L-DC7FF66C are both 0. See `evidence/bedrock-availability.json` for the timestamp and request ID. A ready-to-send account quota restoration request is in `aws-support-request.txt`; it has not been submitted.

The account also returned `SubscriptionRequiredException` for the AWS Support API: a Premium Support subscription is required for that API. No support plan was purchased and no case was sent. Use the AWS Support / Service Quotas web console with the prepared request; do not purchase a support upgrade merely to run this pilot.

Email audit additions: optional verified-owner transactional notices are capped at 200/month and 5/owner/day. The cost model includes a $0.05 email allowance. Cognito defaults remain active while branded SES sending awaits domain verification and production access. See `email-delivery.md`.
