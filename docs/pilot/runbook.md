# Promise retrieval pilot: operating checklist

**Current status: prepared; no independent participants or results confirmed.**

This pilot measures OrderProof's existing support handoff and conversation records. It does not add a new product category or require Stripe. While Bedrock access is blocked, label sessions as human-support and record-usability tests. Do not claim generated-answer accuracy or AI savings.

## Prepare a private evidence folder

```sh
mkdir -p pilot-data
cp docs/pilot/participant-register-template.csv pilot-data/participants.csv
cp docs/pilot/observations-template.csv pilot-data/observations.csv
cp docs/pilot/followup-template.csv pilot-data/followups.csv
cp docs/pilot/case-study-template.md pilot-data/case-study.md
```

`pilot-data/` is excluded from Git. Keep consent and identity mappings private. Use business IDs B01, B02, B03 in measurements. Never store passwords, conversation tokens, or customer payment information in research sheets.

## 1. Confirm an independent owner

Use the [invitation](owner-invitation.md). Start with one real business; three is a practical target, not a scoring rule. Record its type, recurring problem, relationship to the founder, consent evidence, observation dates, and publication permissions in the participant register. Blank permission means no permission. OrderProof itself does not count as an independent business.

## 2. Agree on comparable tasks before timing

Have the owner select non-sensitive examples of:

- Finding an earlier promise about a return, delivery, or service.
- Continuing a customer conversation after a handoff.
- Retrieving and exporting the complete conversation.

For each task, define a comparable baseline task using the owner's current tools. Record difficulty and starting information in the task-review sheet. Alternate task order where practical. Do not teach the answer during the baseline and call faster recall a product benefit.

Start handling time when the operator receives the task; stop when it is completed or the agreed time limit expires. Start retrieval time when the operator begins looking for the earlier statement. Record failures and elapsed time at abandonment. Handoff delay runs from the request for a person to the first human reply; leave duration blank when no reply arrives and record the failure separately. Do not invent a zero duration.

## 3. Observe and record

Use one row per business/task/phase in `observations.csv`. Record actual answer origin (`human`, `bedrock`, `fallback`). Baselines use `human`; prepared demos are excluded.

The added fields are optional for compatibility with older sheets:

| Field | Allowed values / interpretation |
| --- | --- |
| `retrieval_success` | `yes`, `no`, or `na`; finding the correct earlier statement, checked by the observer |
| `retrieval_seconds` | Nonnegative measured seconds for an attempted retrieval, including failed attempts; blank if unmeasured |
| `repeated_questions` | Nonnegative whole number of questions asking for information already in the conversation during handoff; blank if not observed |

Record context and failures privately in the task-review sheet. Retrieval success and export success are separate outcomes. A helpfulness rating does not prove resolution or factual correctness.

Generate a descriptive report only after collecting actual consented observations:

```sh
python scripts/pilot_report.py pilot-data/observations.csv --output pilot-data/report.json
```

The report shows per-business and pooled baseline/product results, failures, and measurement denominators. It does not infer causal savings from unmatched tasks or independently validate consent. An empty sheet fails instead of producing results.

## 4. Observe return usage and commercial feedback

Agree on a follow-up date with the owner. Record whether they used the product independently before the follow-up, what task they performed, and how this was established. Separate scheduled testing from voluntary use. Record no return usage honestly; absence of a reply is unknown, not a rejection or a success.

Show the actual proposed subscription plan and price. Record currency, price, whether it is acceptable, reasons for continued use or non-use, and adoption blockers. Do not activate billing. Statements of interest are not paying customers or revenue.

## 5. Create one owner-approved case study

Fill the [case-study template](case-study-template.md) using the recorded counts and durations. Include baseline and product sample sizes, origin of answers, failures, missing observations, return use, commercial feedback, and limitations. Keep raw customer text private. Ask the owner to approve the exact quote, attribution, and final public version separately. No approval means the material stays private.

## Completion checklist

- [ ] Independent owner and consent verified by the pilot operator.
- [ ] Comparable tasks and timing boundaries documented before measurement.
- [ ] Baseline and product observations collected, including failures.
- [ ] Retrieval, export, handoff and repeated-question outcomes recorded where observed.
- [ ] Follow-up distinguishes voluntary use, scheduled tests, and unknown outcomes.
- [ ] Commercial feedback includes the actual price shown and adoption barriers.
- [ ] Case study reviewed and publication permission recorded.
- [ ] AI claims match actual successful model access; synthetic tests are excluded.

These remain unchecked until evidence exists. This checklist supports honest evaluation; it does not guarantee a judging score.
