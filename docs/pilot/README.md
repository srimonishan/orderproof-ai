# Real-business pilot

Status: **prepared, not started**. The founder named OrderProof as the participant; see [internal usability pilot](orderproof-internal-pilot.md). This is not an independent business pilot. No business participation, customer demand, measured savings, or successful live AI outcomes are claimed.

Start with the [step-by-step pilot runbook](runbook.md), which links consent records, measurement sheets, follow-up, and publication approval.

## 1. Recruit consenting independent businesses

Use the [owner invitation and 20-minute session](owner-invitation.md) to start with one consenting owner. This is a draft for personal outreach; no message has been sent.

Aim for three independent owners using the [business pilot kit](business-pilot-kit.md), with private consent records, follow-up observations, commercial interviews, and an approved case study. This is a practical target, not an official requirement.

Each owner should operate a real small business with recurring policy questions and agree to evaluate OrderProof. Record the business type, consent date, pilot dates, and operator privately. Agree what may be published; do not publish names, quotes, customer content, or identifying details without permission. No invitations have been sent by the coding agent.

Use a separate real business workspace and approved company policies. Do not use Evergreen fictional data or the reviewer test account as market evidence. The owner can test with non-sensitive task descriptions before involving actual customers. Label staff usability sessions as staff feedback, not customer adoption.

## 2. Define comparable tasks before measuring

Select common tasks such as a return-policy question, a shipping question, an unknown order question requiring a person, and retrieving a previous conversation. Record task categories and their difficulty privately. Observe the owner's existing process first, then the same types of tasks with OrderProof. Aim for at least ten observations per phase as an initial usability sample, not a statistically representative result. Report the actual counts even if lower.

Measure active handling time consistently in seconds. Handoff time runs from the request for a person until the first human reply. Record whether the task was resolved, whether an exported record was obtained, and an optional 1–5 owner helpfulness rating. Do not exclude failures or only select successful examples.

## 3. Separate AI readiness from support usability

While Bedrock is quota-blocked, only conduct a clearly described **human-handoff and record-usability pilot**. Record generated-answer origin as `fallback`, not `bedrock`. This phase cannot validate AI accuracy or AI time savings.

After quota approval, run `scripts/evaluate_support.py`, inspect its outputs manually, and verify real retrieval through the deployed widget. Then let the owner review every pilot AI answer against the approved policy. Record citation correctness and any unsupported promise. Immediately pause AI-facing customer testing if it invents a policy or claims to issue a refund or perform another unsupported action.

## 4. Collect observations without customer content

Copy `observations-template.csv` into an ignored `pilot-data/` directory. Use anonymous business and task IDs. The sheet has no fields for emails, names, chat text, order numbers, or credentials. Keep the raw data private. `owner_consent=yes` and `environment=live` are operator declarations; the script cannot independently prove either.

Field values:

- `phase`: `baseline` or `orderproof`; baseline answer origin must be `human`.
- `answer_origin`: `human`, `bedrock`, or `fallback`. Demo/prepared answers are ineligible.
- `resolved`: `yes` or `no`.
- `citation_correct`: `yes`, `no`, or `na`; use `na` unless a real Bedrock answer was reviewed.
- `export_success`: `yes`, `no`, or `na`.
- `handling_seconds`: a measured nonnegative duration, not an estimate.
- `handoff_seconds`: measured duration, or blank if no handoff occurred.
- `owner_rating`: 1–5, or blank if not collected.

```sh
mkdir -p pilot-data
cp docs/pilot/observations-template.csv pilot-data/observations.csv
# Fill observations.csv with actual consented observations first.
python scripts/pilot_report.py pilot-data/observations.csv --output pilot-data/report.json
```

An empty sheet fails rather than generating invented results. The report includes denominators, separates answer origins, and reports missing measurements as null. It includes both pooled and per-business phase results, plus explicit counts of handoff durations and owner ratings. A missing measurement is not counted as zero; a business without baseline observations has an empty baseline summary. It does not infer a savings percentage or causation from unmatched task samples.

## 5. Ask for actual business feedback

Record the owner's answers privately, in their own words:

1. Which recurring support problem, if any, did this help with?
2. What was confusing or slower than the existing process?
3. Could you locate a promise and export the complete record?
4. Which responses needed correction or a person?
5. Would you continue using it next week? Why or why not?
6. At the proposed subscription price, would you actually consider paying? What would need to change?
7. May we publish an attributed or anonymous quote? Record the exact scope of permission.

Interest is not revenue. A positive survey answer is not a paying customer. Staff tests are not proof of customer adoption.

## 6. Release decision

The owner reviews the report and unresolved failures before wider traffic. Suggested pilot acceptance checks: no unresolved access-control or record-integrity failures; no unreviewed unsupported policy promises; tested handoff and exports; usable signup; and live grounded answers verified before claiming AI readiness. These are project release checks, not official hackathon scoring thresholds.

A genuine pilot report is one piece of evidence. It does not by itself establish production readiness, market fit, or a prize outcome. Bedrock availability, operational recovery, delivery setup, and the remaining release audit still apply.

## Publication template — fill only from evidence

“Between [dates], [number] consenting businesses completed [baseline count] baseline and [product count] OrderProof observations. Median measured handling times were [values], with [resolved/observed] tasks resolved. [number] answers were generated by Bedrock; [number] used fallback. Owners reported [approved feedback]. The sample was small and task difficulty was not controlled, so these results do not establish causal savings.”

## Optional customer feedback

After closure, the live widget offers resolution (Yes / Partly / No), helpfulness (1–5), and an optional comment. Submitting is optional; downloading the record and starting another conversation remain available. The business can read feedback in the conversation details. Feedback is stored separately with the conversation access expiry, cannot be replaced through the API, and does not modify the sealed transcript. Ratings are self-reported and do not prove accuracy or independent business adoption.
