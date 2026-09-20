# Reviewer access and demonstration

The public guide at `/review` explains the fictional walkthrough and the real end-to-end flow. It is accessible without login. The fictional walkthrough does not expire and must never be presented as a successful real model call.

For real evaluation, create a dedicated workspace containing only synthetic company data. Keep owner credentials out of the public repository. Use the normal customer widget for the customer side. Do not share the production business owner's account with judges.

An AWS administrator can grant an existing workspace bounded access:

```sh
python scripts/grant_review_access.py \
  --table YOUR_SUPPORT_TABLE \
  --owner-sub REVIEWER_COGNITO_SUB \
  --until 2026-11-01T00:00:00+00:00
```

This uses the administrator's local AWS credentials. There is no public grant endpoint. The script requires an existing profile and a deadline within 60 days. Normal profile updates cannot create or extend the grant, and optimistic version checking protects concurrent edits. The dashboard displays the reviewer deadline. The grant preserves trial AI/source/domain limits, global monthly limits, and request throttles; it does not enable billing.

A dedicated synthetic reviewer workspace has now been created, with two approved policies and a verified grant through November 1. Its credentials are stored privately on the operator machine, not in this repository. Creating the workspace does not deliver credentials to judges. Confirm the actual reviewer identity, grant deadline, available AI budget, and access instructions before submission. To revoke a grant, an administrator sets `reviewAccessUntil` to zero; the ordinary trial expiration still applies.

Run `scripts/smoke_support.py` to verify the real workflow and `scripts/evaluate_support.py` for a small fixed-passage grounding evaluation. The latter writes pass/fail/blocked evidence and stops on a service error. Its keyword checks complement manual review; they are not an accuracy certification.

Before judging, verify normal signup access, the reviewer's granted workspace, source ingestion, model response, citation, human reply, close, archive verification, and export. Keep the app deployed through the announced judging period. Monitor limits and errors; do not silently remove usage caps to keep a demo working.
