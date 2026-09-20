"""Small, table-based transactional emails; no tracking pixels or external images."""
from html import escape
from urllib.parse import urlsplit

KINDS = {
    'verification': ('Your OrderProof verification code', 'One small step. A secure start.', 'Use the code below to finish the account action you requested in OrderProof.'),
    'welcome': ('Your OrderProof workspace is ready', 'Great support starts here.', 'Your workspace is ready. Add your company knowledge, approve your sources, and install your support widget.'),
    'handoff': ('A customer is waiting in your OrderProof inbox', 'Your human touch is needed.', 'A customer requested a person. Open your inbox to read the conversation and join when you are ready.'),
    'closed': ('Your OrderProof conversation record is ready', 'The conversation. Kept together.', 'A support conversation has been closed and archived. Sign in to review, verify, or export its preserved record.'),
}


def render(kind, base_url, business='Your business', code='{####}'):
    if kind not in KINDS:
        raise ValueError('Unknown transactional email type')
    url = urlsplit(base_url)
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
        raise ValueError('Email links must use the HTTPS application origin')
    base_url = base_url.rstrip('/')
    subject, title, intro = KINDS[kind]
    verification = kind == 'verification'
    button = 'Return to OrderProof' if verification else 'Open your workspace' if kind == 'welcome' else 'Open your inbox'
    link = base_url + '/app'
    detail = ('<p style="margin:24px 0;padding:20px 12px;background:#edf5ef;border:1px solid #cadfd1;border-radius:10px;text-align:center;font-size:32px;font-weight:700;letter-spacing:6px;color:#173f31;">' + escape(code) + '</p><p style="font-size:14px;line-height:1.7;color:#53675d;">Use the most recent code. Never share it with anyone, including support. If it has expired, request a new code in the app.</p>') if verification else '<p style="margin:24px 0;padding:16px;background:#edf5ef;border-left:3px solid #245e4c;line-height:1.7;color:#173f31;">Workspace: <strong>' + escape(business) + '</strong><br>No private conversation content is included in this email.</p>'
    footer = 'If you did not request this code, you can ignore this email. No action is needed.' if verification else 'You receive this transactional update because email notifications are enabled for your workspace. Manage them in Settings.'
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{escape(subject)}</title></head><body style="margin:0;padding:0;background:#f4f7f5;color:#20352b;font-family:Arial,Helvetica,sans-serif;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{escape(intro)}</div>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f7f5;"><tr><td align="center" style="padding:32px 12px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:580px;border:1px solid #dbe6de;border-radius:16px;background:#ffffff;overflow:hidden;">
<tr><td style="padding:26px 30px;background:#245e4c;color:#ffffff;font-size:24px;font-weight:700;letter-spacing:-.5px;">OrderProof<span style="display:block;margin-top:8px;font-size:13px;font-weight:400;letter-spacing:0;color:#ffffff;">Support, with a record.</span></td></tr>
<tr><td style="padding:30px;"><p style="margin:0 0 12px;color:#53675d;font-size:12px;font-weight:700;letter-spacing:1px;">{'ACCOUNT SECURITY' if verification else 'YOUR BUSINESS WORKSPACE'}</p><h1 style="margin:0 0 16px;font-size:28px;line-height:1.25;letter-spacing:-.7px;">{escape(title)}</h1><p style="margin:0;font-size:16px;line-height:1.8;color:#435a4d;">{escape(intro)}</p>{detail}
<table role="presentation" cellspacing="0" cellpadding="0"><tr><td bgcolor="#245e4c" style="border-radius:8px;"><a href="{escape(link, quote=True)}" style="display:inline-block;padding:15px 22px;border:1px solid #245e4c;border-radius:8px;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;">{button}</a></td></tr></table>
<p style="margin:26px 0 0;font-size:13px;line-height:1.7;color:#53675d;">{escape(footer)}</p></td></tr>
<tr><td style="padding:20px 30px;border-top:1px solid #e3ebe6;font-size:12px;line-height:1.8;color:#53675d;">OrderProof · Helpful answers. Human connection.<br><a href="{escape(base_url+'/privacy', quote=True)}" style="color:#245e4c;">Privacy &amp; retention</a> · This is an automated message; replies are not monitored.</td></tr></table>
<p style="max-width:550px;margin:18px auto 0;color:#53675d;font-size:12px;line-height:1.7;">If the button does not work, open <a href="{escape(link, quote=True)}" style="color:#245e4c;overflow-wrap:anywhere;">{escape(link)}</a>.</p>
</td></tr></table></body></html>'''
    html = html.replace('<a href=', '<a target="_blank" rel="noopener noreferrer" href=')
    text = '\n\n'.join([subject, title, intro, ('Your code: ' + code) if verification else ('Workspace: ' + business), 'Never share your verification code.' if verification else 'No private conversation content is included in this email.', button + ': ' + link, footer, 'Privacy: ' + base_url + '/privacy'])
    return {'subject': subject, 'html': html, 'text': text}
