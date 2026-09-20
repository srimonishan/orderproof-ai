# Branded transactional email and delivery audit

## Current state

Cognito verification/reset codes use `COGNITO_DEFAULT`. One real resend request to the owner's existing signup address was accepted by Cognito during the audit. A later Cognito read reported the owner's account CONFIRMED and email_verified=true. Account verification is now complete. Neither provider acceptance nor verified-account state reveals Inbox versus Spam placement.

In the app region, us-east-1, SES is healthy and sending-enabled but **not production-enabled**. It has no verified email identities; no Route 53 hosted zones were found. General customer sending and authenticated custom branding cannot be activated without an owned domain and DNS configuration. We have not purchased a domain, submitted an SES production request, changed DNS, or sent marketing emails.

AWS requires a DEVELOPER/SES email configuration for the custom `VerificationMessageTemplate.EmailMessage` field. The infrastructure therefore keeps the existing working default sender until verified sender parameters are supplied. Branded HTML is prepared and previewable; it is not falsely represented as the email currently sent by Cognito.

## What is implemented

- Four table-based, responsive HTML designs in OrderProof green (`#245e4c`): verification/reset code, welcome, human-handoff notice, closed-record notice.
- Plain-text counterparts, clear security instructions, HTTPS links, no external images or tracking pixels, escaped dynamic business names.
- A preview gallery at `/email-preview`. Sample codes are fictional.
- Conditional Cognito HTML configuration and sender permissions in CloudFormation. Defaults leave sending unchanged.
- Opt-in owner notices on enabling email notifications, customer human-handoff requests, and successfully archived closure. The target comes from Cognito, must be verified, and cannot be supplied as an arbitrary email in the request.
- No chat text, customer tokens, or transcript attachment is emailed. Notices link to the authenticated business workspace.
- Persistent per-event deduplication; at most five notices per owner per day and 200 application notices per month. These limits do not change Cognito's own account-email limits.
- Notices are best effort. A send accepted by SES is recorded as `accepted`, not `delivered`. Uncertain sends are not automatically retried, preventing duplicate notices. The in-app inbox remains authoritative.
- Improved signup/reset UI: masked delivery destination when returned, spam-folder guidance, resend cooldown, and tab-scoped pending-email recovery. Passwords/codes are never persisted.

These are workspace-owner notifications. Visitors do not currently supply verified email addresses, so visitor transcript emailing and visitor reply notifications are not implemented. Billing emails remain dependent on future Stripe integration. There is no marketing campaign feature.

## Required activation steps

1. Obtain the owner's sending domain and chosen sender; use us-east-1 to match the current app. Verify caller account and current SES identity state before changing anything.
2. Set up domain identity with DKIM. Add the exact DNS records returned by SES; never invent tokens. Configure a custom MAIL FROM subdomain and its SES-prescribed MX/SPF records. Review existing DNS records before changes; do not overwrite an existing SPF record or MX for an active mailbox domain.
3. Publish an appropriate DMARC policy after reviewing existing policy and alignment. Start with observation when needed, then tighten deliberately. Only add reporting addresses that the domain owner controls and approves.
4. Confirm identity verification, successful DKIM and custom MAIL FROM. While in sandbox, permitted recipients are (1) individually verified email identities, (2) the SES mailbox simulator, or (3) addresses at verified domains. A verified sender alone does not lift recipient restrictions.
5. Request production access with the reviewed transactional use case and the required owner's consent. No false business details or unverified claims should be supplied to AWS.
6. Configure bounce/complaint suppression and delivery/feedback monitoring before broad sending. Avoid logging bodies, tokens, or recipient lists. Use consented, narrowly scoped test recipients to inspect authentication headers.
7. Deploy with both `EmailIdentityArn` and `EmailFrom` populated. IAM is restricted to that identity and exact From address. `AppOrigin` controls authenticated notification links and the Cognito template URL. Never point it to a token-bearing URL.
8. Test sign-up, resend, wrong/expired code, successful confirmation, forgotten password, and password reset in an actual mailbox. Test opt-in/out and each transactional notice. Inspect Gmail/Outlook raw headers for SPF/DKIM/DMARC and actual Inbox/Spam placement. Verify that bounce/complaint feedback suppresses future sends.

HTML styling does not guarantee inbox placement. Authentication, sender reputation, recipient engagement, complaint levels, content, and mailbox-provider decisions all matter. No "never spam" or universal rendering guarantee is made.

## Sources

- [Cognito custom verification template requirements](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-cognito-userpool-verificationmessagetemplate.html)
- [Cognito message customization and reset-code templates](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-message-customizations.html)
- [SES email deliverability](https://docs.aws.amazon.com/ses/latest/dg/send-email-concepts-deliverability.html)
- [SES DMARC alignment](https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dmarc.html)
