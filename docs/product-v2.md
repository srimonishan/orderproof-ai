# OrderProof support platform — agreed direction, September 20, 2026

The owner expanded OrderProof from order extraction into a subscription-ready, embeddable business support platform. Preserve the original order functionality while adding:

1. A bottom-right website support widget with company branding and an installation snippet.
2. Company knowledge setup from uploaded documents, pasted policies, and public web pages. Social/LinkedIn content requires an accessible public page or an owner-supplied export; no login bypass or unsupported social scraping.
3. Answers retrieved from that company's knowledge, with source references, clarifying questions and an explicit unknown/handoff path.
4. Human-agent handoff into a business inbox; the customer remains in the same conversation. Never claim a human is connected until an authenticated agent takes over.
5. A preserved timeline of customer, AI, system and agent events. Corrections are new messages, not edits to history. Provide transcript export and verification.
6. An attractive, responsive business dashboard covering inbox, knowledge, widget installation, settings, usage and plans.
7. Monthly subscription plan controls. Live collection requires a payment provider account; no fake checkout or invented payment success.
8. AWS deployment, lowest practical model cost, and updated hackathon evidence.

Existing constraint: target under $10/month for the pilot; no prize credits have been verified. Do not introduce managed per-hour search infrastructure without a budget review.

## Pilot choices

One owner operates one business and acts as the human agent. Multi-agent teams and phone calls are not implied by the pilot handoff: this release supports live text handoff. Data-source isolation and server-side authorization are mandatory.

Knowledge retrieval is a bounded lexical passage index over each business's approved documents, feeding Amazon Bedrock. This is retrieval-augmented generation, not fine-tuning or an unbounded website crawler. Document contents are untrusted data. Source citations must refer to retrieved sources; an answer without supporting knowledge must escalate.

## Record integrity

Application users have no API for editing or deleting chat events. Events form a SHA-256 chain, and closed transcripts are versioned in a private S3 archive with 30-day governance retention. This is tamper-evident, not a promise that an AWS administrator with governance-bypass privileges can never alter anything. Customers are told their chat is recorded before starting. Operational retention and privacy controls must be visible.

## Completion evidence

Test actual tenant isolation, duplicate message handling, knowledge-source isolation, handoff, conflicting writes, transcript tampering, invalid website addresses, model failure, mobile overflow and keyboard access. Test actual deployed endpoints and clearly distinguish seeded walkthrough data from live behavior. Submission and customer-impact claims must be backed by evidence.

## Confirmed subscription and installation requirements

The owner requested a seven-day free trial and feature-based monthly plans, with Stripe connected after deployment. No payment collection is authorized through a provided Stripe account yet. Plan selection records a preference only. Website/React installation, standalone hosted support, iOS/Android WebView examples, and a documented customer REST API use the same tenant knowledge and history. Native packaged applications, multi-agent seats, and phone calls are outside this pilot implementation.
