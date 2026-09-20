# Installation and customer API

Production: https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com

Open **Install & connect** in a business workspace for snippets with its actual site ID. Website scripts, React, hosted support pages, and custom API clients share one tenant's knowledge and conversation inbox. The iOS and Android snippets load the hosted UI using WebViews; native application binaries and app-store releases are not included.

## Website / web application

1. Create a workspace, register the website's exact HTTPS origin, and approve company sources.
2. Place the generated script before `</body>`, once per page. Use the React lifecycle example for React applications.
3. If the host uses CSP, allow the production origin in `script-src`, `style-src`, and `frame-src`. The launcher stylesheet is external; no `unsafe-inline` is needed. The conversation runs in a same-origin iframe at the service origin, isolated from merchant CSS.
4. Test a question, request a person, join from the inbox, reply, close, verify, and export.

`window.OrderProof.open()`, `.close()`, and `.destroy()` control the installed launcher. Only one widget is supported per page. `data-site` is a public identifier, not a credential. Register www and non-www origins separately if both are used. An unregistered site's iframe is refused by `frame-ancestors`. This prevents unwanted framing; it is not API authentication or proof of website ownership.

Customer conversation tokens stay inside the iframe and are never posted to the host page. Session storage restores the conversation on reload in the current tab where the browser permits storage. Browser privacy controls can prevent persistence. The API token is a private capability: keep it out of URLs, logs, analytics, and public code. A lost token cannot be recovered using an unverified customer name.

## Standalone company support

Use the workspace's hosted chat URL as a Help link, a support screen, or a QR-code destination. This top-level page does not need to be framed in a registered origin. Each business has its own branding and knowledge. Custom domains and a separately packaged company application are not provisioned by this pilot.

## iOS and Android

Use the examples in Install & connect. Load only the HTTPS hosted URL, keep platform TLS validation enabled, and do not add a JavaScript-to-native bridge. Implement your app's navigation allowlist and external-link handling. A production native wrapper also needs platform-specific download/share handling for transcript exports, accessibility and real-device checks, offline UI, and lifecycle/session handling. The supplied snippets have not been compiled or tested on physical devices. An external browser support link is also supported.

References: [Apple WKWebView](https://developer.apple.com/documentation/webkit/wkwebview), [Android WebView](https://developer.android.com/develop/ui/views/layout/webapps/webview).

## Custom customer UI

Native apps or a server can call these JSON endpoints. A browser on a different origin needs its own same-origin backend proxy; public API CORS is deliberately not enabled. Never embed AWS or business-owner credentials in a customer application.

| Method | Path | Request / result |
|---|---|---|
| GET | `/public/support/sites/{siteId}` | Public business name, greeting, website, color |
| POST | `/public/support/sites/{siteId}/conversations` | `{name, category, consent:true}` → `{token, conversation}` |
| GET | `/public/support/conversations/{id}` | Current full timeline and state |
| POST | `/public/support/conversations/{id}/messages` | `{content, requestId}` → updated conversation |
| POST | `/public/support/conversations/{id}/handoff` | `{requestId}` → waiting state |
| GET | `/public/support/conversations/{id}/export` | Complete JSON transcript |
| GET | `/public/support/conversations/{id}/verify` | Chain verification and archive match when sealed |

All conversation endpoints require `X-Conversation-Token`. Categories: `general`, `orders`, `returns`, `payments`, `technical`. Display recording consent before starting. Use a UUID request ID per message; reuse the same ID only when retrying that exact operation. Message text: at most 2,000 characters. Poll no faster than every 10 seconds and stop polling in the background or after closure. The response's `mode` is `ai`, `waiting`, or `human`; only `human` means an agent has joined. `status:closed` is read-only.

Errors: 400 invalid input, 401 owner sign-in required, 402 expired trial, 404 missing/unauthorized resource, 409 conflict or closed record, 413 oversized upload, 429 usage/rate limit, 503 temporary service failure. On a timeout, retry the same message ID. A successful save can be followed by an explicit AI-unavailable response; never turn that into a fabricated policy answer.

## Current limits

One owner-operated human inbox per business; text handoff, no voice calling or multi-agent routing. Up to 250 events per conversation, 90-day history, closed S3 versions protected in governance mode for 30 days. Authorized AWS administrators with bypass permission can override retention. Object Lock protects the archived version, not every DynamoDB message from a privileged administrator. Hash chains detect inconsistencies; they do not independently prove identity.
