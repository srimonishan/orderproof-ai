"""Live synthetic smoke test. No real customer information or account tokens are printed.
Creates two temporary Cognito accounts with delivery suppressed, then removes them.
Synthetic closed records follow the configured archive retention.
"""
import json
import secrets
import time
import urllib.request
import urllib.error
from pathlib import Path
import boto3
from botocore.config import Config

REGION='us-east-1'
BASE='https://tapuxp0ed4.execute-api.us-east-1.amazonaws.com'
POOL='us-east-1_EbvzwRyHZ'
CLIENT='67r178a93qs97na9mpfm7dm412'
auth=boto3.client('cognito-idp',region_name=REGION,config=Config(retries={'total_max_attempts':2}))
created=[];checks=[]

def req(path,method='GET',data=None,jwt=None,token=None,expected=200):
    time.sleep(.35)
    headers={'Content-Type':'application/json'}
    if jwt:headers['Authorization']='Bearer '+jwt
    if token:headers['X-Conversation-Token']=token
    request=urllib.request.Request(BASE+path,method=method,headers=headers,data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(request,timeout=40) as r:code=r.status;value=json.load(r)
    except urllib.error.HTTPError as e:code=e.code;value=json.load(e)
    assert code==expected,(method,path,code,value)
    return value

def account():
    email='orderproof-smoke-'+secrets.token_hex(5)+'@example.invalid'
    password='Aa1!'+secrets.token_urlsafe(24)
    auth.admin_create_user(UserPoolId=POOL,Username=email,MessageAction='SUPPRESS',UserAttributes=[{'Name':'email','Value':email},{'Name':'email_verified','Value':'true'}]);created.append(email)
    auth.admin_set_user_password(UserPoolId=POOL,Username=email,Password=password,Permanent=True)
    result=auth.initiate_auth(ClientId=CLIENT,AuthFlow='USER_PASSWORD_AUTH',AuthParameters={'USERNAME':email,'PASSWORD':password})
    return result['AuthenticationResult']['AccessToken']

try:
    one=account();two=account()
    req('/api/support/business',expected=401);checks.append('anonymous business access denied')
    b=req('/api/support/business','PUT',{'name':'Synthetic integration test','website':BASE,'domains':[BASE],'greeting':'Welcome to the synthetic test.'},jwt=one)
    checks.append('Cognito owner workspace and trial created')
    source=req('/api/support/sources','POST',{'title':'Synthetic return policy','content':'Unused items may be returned within 30 days of delivery. Contact the support team before shipping any return.','approved':True},jwt=one,expected=201)
    assert len(req('/api/support/sources',jwt=one))==1
    checks.append('approved knowledge persisted')
    r=req('/public/support/sites/'+b['siteId']+'/conversations','POST',{'name':'Synthetic customer','category':'returns','consent':True},expected=201)
    c=r['conversation'];t=r['token'];public='/public/support/conversations/'+c['id'];private='/api/support/conversations/'+c['id']
    req(private,jwt=two,expected=404);req(public,token='wrong',expected=404);checks.append('cross-tenant and wrong-token access denied')
    c=req(public+'/messages','POST',{'content':'What is the return policy for unused items?','requestId':'question-1'},token=t)
    ai='available' if c['messages'][-1].get('sources') else 'unavailable-fallback'
    checks.append('customer message saved; model outcome: '+ai)
    assert req('/api/support/usage',jwt=one)['aiStatus']==('available' if ai=='available' else 'unavailable')
    checks.append('workspace model-readiness status reflects the actual attempt')
    seq=c['seq'];again=req(public+'/messages','POST',{'content':'What is the return policy for unused items?','requestId':'question-1'},token=t);assert again['seq']==seq
    checks.append('message retry did not duplicate the record')
    assert req(public+'/handoff','POST',{'requestId':'handoff'},token=t)['mode']=='waiting'
    assert req(private+'/takeover','POST',{'requestId':'takeover'},jwt=one)['mode']=='human'
    req(private+'/reply','POST',{'requestId':'human-reply','content':'This is a synthetic human reply for deployment verification.'},jwt=one)
    assert req(public,token=t)['messages'][-1]['role']=='agent';checks.append('customer-to-human handoff and reply visible to customer')
    closed=req(private+'/close','POST',{'requestId':'close'},jwt=one);assert closed['archive']['versionId']
    check=req(private+'/verify',jwt=one);assert check['valid'] and check['archiveValid'];checks.append('closed transcript and protected S3 version match')
    transcript=req(public+'/export',token=t);assert transcript['status']=='closed' and any(m['role']=='agent' for m in transcript['messages']);checks.append('customer exported complete transcript')
    req(public+'/messages','POST',{'requestId':'late','content':'Cannot change closed transcript'},token=t,expected=409)
    assert req('/api/support/select-plan','POST',{'plan':'growth'},jwt=one)['billingEnabled'] is False
    assert req('/api/support/business',jwt=one)['plan']=='trial';checks.append('plan preference cannot activate paid access')
    result={'testedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'url':BASE,'checks':checks,'bedrock':ai,'syntheticConversationId':c['id'],'note':'Synthetic test records retained according to the archive lifecycle. Temporary test login accounts removed.'}
    Path('docs/evidence/live-support-smoke.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:
    for email in created:auth.admin_delete_user(UserPoolId=POOL,Username=email)
