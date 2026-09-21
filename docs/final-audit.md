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

The latest recorded live integration run completed at **2026-09-20T09:47:55Z**. See [machine-readable results](evidence/live-support-smoke.json). Synthetic records remain subject to retention; temporary login identities were removed.

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

## Latest AI recheck

The fresh live workflow on September 20 again returned the explicit unavailable fallback. A separate Nova Lite Converse request in `us-west-2`, with `maxTokens=128`, returned `ThrottlingException: Too many tokens per day, please wait before trying again.` Live generated answers remain blocked. Explicitly limiting output tokens reduces quota reservation but does not resolve an exhausted or zero daily allowance. Handoff, record verification, and export passed again.

## Submission-readiness follow-up

- Category selected: Commercial Potential; lane selected: Startup. Builder Center publication and tags still pending.
- Official Rules reviewed in Chromium: Sri Lanka is not excluded, and self-reported age 19 meets the minimum. Employment/household and originality confirmations remain outstanding.
- Backend suite expanded to 49 passing tests, including prevention of self-issued reviewer grants and expiry enforcement.
- Public reviewer guide and bounded administrator-issued reviewer access implemented. A dedicated synthetic workspace is provisioned with two approved policies and a verified grant through November 1; judge access instructions must still be delivered appropriately.
- A five-case live model evaluation is prepared; it stops on the first quota failure and records zero completed cases, not a false pass.
- AWS accepted a Nova Lite cross-region TPM request; status PENDING. See evidence/quota-request.json. Approval and a successful model invocation remain required.
- The GitHub browser hang was isolated to accessibility traversal of sandboxed email iframes. Gallery checks now skip iframe traversal; each template is independently tested as a full document. GitHub-hosted CI completed successfully: https://github.com/srimonishan/orderproof-ai/actions/runs/35516627127.

## Demo transparency and pilot preparation — September 21, 2026

Persistent fictional-demo notices now appear across the workspace. The demo widget explicitly says its conversation is unsaved, and prepared answers are identified as non-Bedrock. The illustrative return policy is consistent across the workspace and widget. The pilot kit includes a blank observation sheet, consent and measurement guidance, and a report generator that rejects empty/synthetic inputs. The founder selected OrderProof itself: an internal usability protocol is prepared, but no human observations or independent market validation have been collected. Production readiness remains blocked by the unresolved AI quota and other release gates.

## Portable verification upgrade

67 tests pass locally after adding a standard-library offline transcript verifier. Coverage includes saved citation continuity after source deletion, exported JSON compatibility, tampered text/citations, ordering, final digests, and rewritten-chain rejection against a separately trusted digest. This improves verification portability; it is not cryptographic authorship or identity proof. A four-minute demonstration guide is available in `innovation-demo.md`.

Luna was tested on its model-specific Bedrock Mantle path: HTTP 401, `access_denied`, model unavailable for this account. Its nonzero quotas do not imply access. Live AI remains blocked; the deployed model is unchanged.

## Customer feedback release — September 21, 2026

Deployed to the existing AWS stack; CloudFormation reached UPDATE_COMPLETE. Optional post-closure resolution, helpfulness, and comment submission is available in the widget. Owners see responses in conversation details. Conditional writes prevent replacement; identical retries succeed. Feedback uses the conversation's expiry and remains separate from transcript events and the sealed archive. No additional AWS service was introduced.

Validation: 75 backend tests passed; JavaScript syntax, CloudFormation lint and security rules passed. Feedback mobile accessibility, failed-request retry preservation, reload persistence, and optional restart flow passed with mocked API fixtures. Existing support, authentication/email-preview, and legacy browser suites passed. Email preview tests do not establish real inbox delivery.

The deployed synthetic integration test verified feedback persistence, unchanged exported transcript and protected archive, tenant isolation, human handoff, and export. See `docs/evidence/live-support-smoke.json` (2026-09-21T18:14:23Z). The live AI attempt still returned unavailable fallback: this is not successful generated-answer evaluation.

The independent-business kit includes consent, comparable baselines, correction/retrieval observations, return usage, commercial interviews, and an owner-approved case-study template. No independent participant or impact results have been invented. Production approval remains outstanding while live AI evaluation and genuine pilot evidence are missing; submission and eligibility confirmations remain separate checklist items.

## Evidence-quality follow-up — September 22, 2026 (Sri Lanka)

Fixed business inbox polling to refresh newly submitted customer feedback even when message sequence and archive metadata do not change. The pilot reporting script now produces per-business phase breakdowns and explicit handoff/rating measurement counts; missing measurements remain missing. No participant results were created.

Validation: 76 backend tests, JavaScript syntax checks, and support browser/accessibility checks passed. Fresh Bedrock evaluation at 2026-09-21T19:25:10Z stopped on ThrottlingException (“Too many tokens per day”): 0 of 5 cases completed. The existing quota request remains CASE_OPENED, case 178991456400579. Successful live AI quality and independent business outcomes remain outstanding; no revised prize score is claimed.
