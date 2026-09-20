# OrderProof release audit

Audit date: September 20, 2026. Status: **deployed pilot; not approved for general production release**.

Live application: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com

## Results

| Area | Evidence and result | Release implication |
| --- | --- | --- |
| AWS workflow | Live synthetic test passed workspace creation, source storage, tenant isolation, customer messages, retries, handoff, owner reply, archive verification, and export. | Core workflow verified for the tested scenarios. |
| AI generation | Bedrock rejected realistic requests with a daily token quota error. Both inspected Nova paths reported zero relevant quotas. | **Blocked.** No successful live grounded-answer quality claim. |
| Retrieval | Unit tests cover approved sources, common word variants, and source validation; live knowledge storage passed. | Retrieval logic tested; end-to-end generated answers still require evaluation. |
| Failure handling | Live model failure preserves the message and offers human support; readiness status reflects the failure. | Tested fallback works. |
| Authentication | Cognito account is confirmed and email verified; mocked browser flows cover verification and reset. | Account verification observed; inbox placement is unverified. |
| Email design | HTML and plain-text templates implemented, escaped, branded, and previewable. | Design is prepared. |
| Customer email delivery | No verified SES sender identity; account remains in sandbox. Custom Cognito HTML configuration is conditional and inactive. | **Blocked** until domain and delivery setup. No guarantee against spam placement. |
| Billing | Trial limits enforced; selecting a plan cannot activate paid access. | Stripe deliberately deferred. Do not advertise working paid checkout. |
| Record integrity | Hash-chain checks and exact S3 archive version/checksum verification passed. | Governance retention is administrator-bypassable; not absolute immutability. |
| UI | Desktop and narrow mobile browser journeys plus automated accessibility checks passed in the recorded audit. | Manual assistive-technology and broader device testing remain. |
| Integrations | Website embed and hosted demo exercised. iOS/Android examples supplied. | Native device builds are not tested or supplied. |
| Dependencies | Recorded deployed Python dependency audit found no known vulnerabilities. | Point-in-time result, not a comprehensive security assessment. |
| GitHub CI | Credential-free workflow and dependency updates prepared. | Hosted CI must run after publication; no passing badge claimed. |

## Test scope

The recorded Python suite contains 47 passing tests. Coverage includes tenant isolation, source approval, malformed model responses, timeouts, usage limits, retry conflicts, transcript tampering, protected archive versions, SSRF restrictions, and notification recipient verification/deduplication.

Browser checks cover the fictional demo workspace, owner inbox, knowledge, settings, plans, records, installation, customer handoff, embed, mobile layout, mocked authentication, and email previews. Fictional demo responses are not Bedrock outputs.

The latest recorded live integration run completed at **2026-09-20T06:35:21Z**. See [machine-readable results](evidence/live-support-smoke.json). Synthetic records remain subject to retention; temporary login identities were removed.

## Required before production

1. Restore Bedrock account quota using the [prepared support request](aws-support-request.txt). Re-run realistic model calls and evaluate supported answers, missing knowledge, citations, prompt injection, latency, and fallback behavior.
2. Configure an owned sending domain, verify SES identity and DKIM, configure SPF/custom MAIL FROM and DMARC, obtain production access, and activate the conditional email configuration. Follow the [email guide](email-delivery.md).
3. Verify signup and password-reset delivery in actual target mailboxes, including headers and spam placement. Test bounce and complaint handling. AWS acceptance alone is not proof of delivery.
4. Exercise an actual customer website and intended mobile devices. Complete manual keyboard/screen-reader checks and business acceptance testing.
5. Validate operational alerts, recovery procedures, support ownership, realistic load, and cost behavior before wider traffic. Current small-pilot tests do not establish scale capacity or availability guarantees.
6. Keep paid activation disabled until Stripe is connected and its subscription/webhook lifecycle is tested.

## Evidence

The final local rerun passed all 47 Python tests, cfn-lint, four Guard rules, JavaScript syntax checks, and all three browser suites. The deployed authentication/email browser suite also passed with mocked Cognito calls; it sent no email.

- [Final rerun results](evidence/final-local-checks.json)

- [Deployment record](evidence/deployment.md)
- [Live integration results](evidence/live-support-smoke.json)
- [Bedrock availability](evidence/bedrock-availability.json)
- [Email configuration audit](evidence/email-audit.json)
- [Dependency audit](evidence/dependency-audit.json)
- [Cost assumptions](evidence/cost-estimate.json)

No production certification, guaranteed inbox placement, or completed real AI evaluation is claimed. Repository preparation does not publish a GitHub repository.
