# AWS deployment verification

Public application: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com
Installation guide: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com/integrations
Widget demonstration: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com/integration-demo

The `orderproof-prod` stack reached UPDATE_COMPLETE in us-east-1. Existing user pool and original order table were preserved. Added a support metadata table, separate event table, private S3 transcript archive, and scoped application permissions. No unrelated stacks were modified.

Validation:
- 47 Python backend tests passed.
- CloudFormation lint and four custom security rules passed.
- JavaScript syntax checks passed.
- Public AWS browser flows passed for landing, business demo, human reply/closure, knowledge, plans, settings, records, installation, customer widget, website embed, and mobile layout.
- Automated WCAG A/AA checks found no violations in the tested screens; this is not a full accessibility certification.
- The original order-confirmation browser regression passed at `/orders`.
- See `live-support-smoke.json` for the actual AWS API smoke-test result, model availability outcome, and timestamp.

Screenshots under `screenshots/` show the public AWS application with clearly labeled fictional demo data. They are not screenshots of the AWS management console. Agent CLI/MCP authentication evidence is separate. A browser-console screenshot and confirmation that the hackathon accepts the evidence format remain pending.

The deployment is reachable. Bedrock generation remains dependent on the account's quota being restored; no artificial/demo reply is represented as a live model result. Stripe is deferred by the owner's instruction. No Builder Center entry has been submitted.

Final audit update: deployment includes branded email previews, disabled-until-configured SES support, verified-owner notification safeguards, verification UX improvements, and model availability reporting. See `email-audit.json` and `../final-audit.md` for actual readiness and blockers.

## Reviewer release — September 20, 2026

CloudFormation update completed for the existing stack. Added `/review`, bounded administrator-granted workspace access, transparent access status in the UI, and a five-case Bedrock evaluation script. 49 Python tests passed. Live deployed browser checks and synthetic handoff/archive/export workflow passed. Dedicated synthetic reviewer sign-in, grant, and approved sources were verified. Bedrock generation still returned its quota fallback; the accepted quota request remains a separate AWS decision.
