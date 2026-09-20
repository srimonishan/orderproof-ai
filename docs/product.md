# OrderProof product specification

## Promise

Share the conversation. Get an order you can trust.

The product converts an uploaded or pasted customer conversation into a reviewable order, resolves ambiguity, and records customer confirmation of a specific revision.

## Complete first release

1. Public landing page and a clearly labeled sample walkthrough requiring no registration.
2. Seller authentication and private order workspace.
3. Paste conversation text or upload a text export; impose explicit size limits.
4. AI extracts order fields with exact source quotations and message references.
5. Separate confirmed requests, tentative inquiries, changes, and unresolved questions.
6. Seller reviews and edits details, with explicit attribution for manual edits.
7. Save draft and publish a limited customer confirmation page.
8. Customer confirms a specific revision or requests changes.
9. Editing a shared order creates a new revision and invalidates prior confirmation for the current revision.
10. Order dashboard shows status, agreed fulfillment date, and outstanding questions.
11. Seller can delete orders and revoke shared links.

Images, voice transcription, direct messaging integrations, payments, and automated outgoing messages are subsequent features unless the core release is complete and verified.

## Correctness and privacy requirements

- Missing dates, prices, quantities, and AM/PM stay unresolved; never invent them.
- Requests for prices do not become purchases.
- A change must retain its original source and supersede the earlier value visibly.
- Source quotations must exist in the submitted conversation; validate model output server-side.
- Conversation content is untrusted data, never executable instructions.
- Model failures must surface as failures; no silent fabricated AI results.
- Customer pages expose order details only, not raw private conversations.
- All seller operations enforce ownership on the server.
- Confirmation is tied to an immutable revision; stale requests cannot confirm newer content.
- Share links use unguessable tokens and can expire or be revoked.
- No raw conversations or tokens in application logs.
- Public sample data is fictional and visibly labeled.
- Model usage has per-user limits and bounded input/output sizes.

## Acceptance scenarios

- Saturday changes to Sunday: latest date wins, change is visible.
- 'Sunday at 4': AM/PM question remains unresolved.
- 'What would adding cupcakes cost?': cupcakes remain an inquiry.
- No price given: price remains blank until seller supplies it.
- Customer confirms revision 1, seller edits revision 2: current order needs reconfirmation.
- Old share link cannot approve revision 2.
- A different seller cannot read or modify the order.
- Deleted or revoked orders cannot be accessed through former links.
- Extraction failure retains the user's input and supports retry.
- Main flow works on mobile and using keyboard navigation.

## Validation

Ask five sellers to demonstrate anonymized past orders. Record consent, actual completion time, extraction corrections, and whether they return to use the product. Publish only measured results. No customer interviews or impact metrics have been collected yet.
