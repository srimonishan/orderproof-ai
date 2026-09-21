# Demonstrate policy evidence that survives change

OrderProof’s focused differentiator is continuity between the policy passage used for an answer, human follow-up, and a portable conversation record. This is a product design claim, not a claim that no competitor has similar capabilities.

## Four-minute demonstration

1. Approve a policy with a 30-day returns window. In a real customer conversation, ask a supported question. Show the actual source passage attached to the answer. If Bedrock is unavailable, stop the AI demonstration and disclose that limitation.
2. Withdraw or remove that source. Explain that future retrieval cannot use it, while the historical answer retains its original passage and source digest. Do not claim that a later policy changes what was previously said.
3. Request a person, reply in the same thread, close it, verify the archive, and export the JSON transcript.
4. Verify that export on a separate machine with no AWS credentials:

```sh
python scripts/verify_transcript.py exported-record.json
python scripts/verify_transcript.py exported-record.json --expected-digest TRUSTED_FINAL_DIGEST
```

5. Make a copy and alter an event's text or citation. Verification should fail. Use synthetic records for this demonstration and label them as such.

## What verification establishes

The verifier checks contiguous event sequence, previous hashes, event contents including saved source references, and the final digest. The trusted-digest option additionally compares against a digest obtained through an independent trusted channel. Save the digest separately when acquiring the original record.

A consistent chain alone does not prove authorship: someone can rewrite the entire chain and recompute its hashes. The independent digest is essential for detecting that attack. Top-level metadata is not authenticated by this format. The offline tool does not query S3, authenticate customer identity, establish factual accuracy, verify clock accuracy, or prove that AWS administrators could not bypass governance retention. It does not use digital signatures or a third-party timestamp authority.

## Evidence, not presentation tricks

Automated tests cover changed messages, citations, missing/reordered events, final-digest changes, wholly rewritten chains, fictional export rejection, and compatibility with real application export serialization. A backend test also proves a previously saved citation remains after the source is removed. Mock-model tests establish these storage behaviors; successful live generated answers still require separate Bedrock evaluation.

## Improve the other judging criteria

- Implementation: run the full test suite and a real deployed flow; publish failures and unresolved limits.
- Market impact: recruit a consenting independent business for the existing pilot protocol. Student Builder Group peers may provide voluntary usability feedback; label peer feedback separately from business adoption and do not imply AWS endorsement.
- Storytelling: show one customer problem, the source at answer time, the human resolution, and the portable record. Use actual counts and attributed feedback only with permission.

No scoring increase is automatic. Judges must assess the completed evidence against the official rubric.
