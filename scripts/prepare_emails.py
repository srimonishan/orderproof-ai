"""Generate reviewable mail previews and sync the optional Cognito HTML template."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from mail_templates import render, KINDS
base='https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com'
for kind in KINDS:
    data=render(kind,base,'Evergreen Studio (fictional preview)', '123456')
    for ext,field in [('html','html'),('txt','text')]:
        (ROOT/'docs/email-previews'/f'{kind}.{ext}').write_text(data[field])
    (ROOT/'backend/static'/f'email-{kind}.html').write_text(data['html'])
# Explicit markers keep this generator from rewriting other infrastructure fields.
p=ROOT/'template.yaml';s=p.read_text()
start='      # BEGIN BRANDED VERIFICATION TEMPLATE\n';end='      # END BRANDED VERIFICATION TEMPLATE\n'
if start in s:
    data=render('verification',base)
    data['html']=data['html'].replace(base,'${AppOrigin}')
    block=start+'      VerificationMessageTemplate:\n        DefaultEmailOption: CONFIRM_WITH_CODE\n        EmailSubject: !If [UseSesEmail, "Your OrderProof verification code", !Ref "AWS::NoValue"]\n        EmailMessage: !If\n          - UseSesEmail\n          - !Sub |\n'+''.join('            '+line+'\n' for line in data['html'].splitlines())+'          - !Ref "AWS::NoValue"\n'+end
    a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:];p.write_text(s)
print('Four HTML/text previews generated. Cognito HTML is conditional on verified SES configuration.')
