# Zero to Shipped submission tracker

Selected category: Commercial Potential. Selected lane: Startup. Required project tags: `#commercial-potential` and `#startup`. These still need to be applied in Builder Center.

## Source and deadline

Official Rules opened directly in Chromium on September 20, 2026 (page last updated September 18). The four criteria are Technical Innovation & Originality, Implementation Quality, Community/Market Impact, and Creativity & Storytelling, each 25%. The top 100 advance to human judging, which selects five winners.

- Event: https://builder.aws.com/build/hackathons/e83e84e5-4f4c-383b-bbe9-4a15ac195d55/zero-to-shipped?tab=about
- Rules: https://builder.aws.com/build/hackathons/e83e84e5-4f4c-383b-bbe9-4a15ac195d55/zero-to-shipped?tab=rules
- Connection guide: https://builder.aws.com/content/3JQdUYne1ujIvtoLgWiV7iBGklF/connect-your-ai-coding-agent-to-aws
- Deadline from supplied FAQ: October 2, 2026, 11:59 p.m. Pacific; October 3, 2026, 12:29 p.m. Sri Lanka time (Pacific daylight time).
- Target internal submission readiness: September 30, 2026.

## Eligibility and submission

- [x] Sri Lanka is absent from the official excluded-country list; residence is self-reported.
- [x] Participant self-reports age 19 (September 20, 2026).
- [ ] Confirm employment/household exclusions and one-entry requirement.
- [ ] Verify AWS Builder Center profile and contact email.
- [ ] Verify originality and no prior publication before the applicable eligibility window.
- [x] Publish live AWS app: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com
- [x] Verify public fictional demo and responsive browser flows.
- [x] Verify agent AWS connection through successful CLI and MCP identity calls.
- [ ] Capture visual evidence and confirm the event accepts the evidence format.
- [x] Prepare [Builder Center project draft](builder-center-project.md), development narrative, and demo instructions.
- [ ] Publish the Builder Center project.
- [x] Select Commercial Potential and Startup for the project direction.
- [ ] Apply `#commercial-potential` and `#startup` in Builder Center.
- [ ] Submit entry and save submission confirmation.
- [ ] Maintain live availability through judging and verification.

## Suggested project narrative — draft

**OrderProof: helpful support, with a record both sides can keep.**

Small businesses answer the same policy questions repeatedly, while customers repeat themselves during handoff and later struggle to establish what was said. OrderProof brings approved company knowledge, AI-assisted replies, an owner-operated human inbox, and a preserved conversation timeline into one embeddable support experience. Businesses can integrate a website widget, a hosted support page, a mobile WebView, or a custom API client.

The implementation uses Cognito for business sign-in, Lambda and API Gateway for the app/API, DynamoDB for isolated company data and transactionally appended events, Bedrock Nova Lite for grounded answer generation, and S3 governance retention for closed transcript versions. Customers can export their record. Source citations retain the passage used at answer time. The agent designed and implemented the interface, retrieval and handoff flow, access controls, tests, infrastructure, deployment, and debugging. Connection evidence is linked in this folder.

**Current disclosure:** the AWS account's Bedrock token quota blocks realistic live generation. The live app preserves messages and offers human support; mock model tests verify the integration, and the public demo uses labeled fictional responses. Resolve quota and complete real model evaluation before presenting AI quality as verified. Stripe is deferred; paid plans are proposals and selection does not charge or activate them. Mobile integrations are examples, not published native applications.

## Demo script

1. Open the public application and choose Explore the demo. Explain that the data and prepared answers are fictional.
2. Show approved company policies and answer citations.
3. Open a waiting conversation, join as the human agent, reply, and show the continuous timeline.
4. Show Install & connect: website, React, iOS, Android, hosted chat, and API.
5. For a real workspace, start a widget chat, request a human, reply from the inbox, close, verify, and export. Disclose the live AI quota blocker if unresolved.
6. Explain the server-enforced trial, low-traffic cost assumptions, and archive protection limits.

## Evidence and claims ledger

Verified: coding-agent CLI/MCP connectivity; deployed AWS app; 47 backend tests; browser flow/accessibility checks; live synthetic tenant isolation, knowledge persistence, human handoff/reply, closed S3 archive matching, transcript export, and non-billable plan preference. See `evidence/live-support-smoke.json`.

Pending: Bedrock account availability and live answer quality; real-user validation and measured business impact; Stripe billing; physical-device/native app verification; eligibility; Builder Center project and actual submission. The public site and coding-agent evidence address parts of the ship gate but do not establish reviewer acceptance.

Never claim a guaranteed top-three finish or prize. The supplied FAQ describes five category winners, not a published top-three award structure.

## Current backlog

- [x] Three-image README and architecture; main technology badges.
- [x] Public reviewer guide and administrator-controlled expiring reviewer access implemented.
- [x] Create a dedicated synthetic reviewer workspace, seed two approved policies, and verify its November 1 access grant through the authenticated API.
- [ ] Arrange judge access through an appropriate private channel and verify the final instructions.
- [ ] Restore Bedrock token allowance; fixed-passage evaluation currently blocked before any successful answers.
- [ ] Obtain participant-owned email domain if branded sender delivery is required; no domain is currently owned. Cognito default email remains the signup channel.
- [x] Check Sri Lanka against official country exclusions (not excluded).
- [ ] Collect actual customer validation; no fabricated impact metrics.
- [ ] Publish Builder Center project and save the submission confirmation.
