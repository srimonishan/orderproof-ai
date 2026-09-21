import sys
from pathlib import Path
import json
import time
from unittest.mock import Mock
import socket
import boto3
from moto import mock_aws
import pytest
from botocore.exceptions import ClientError
sys.path.insert(0, str(Path(__file__).parents[1] / 'backend'))
import app
import support as s

@pytest.fixture(autouse=True)
def db(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID','testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY','testing')
    with mock_aws():
        s._c.clear(); app._clients.clear()
        d=boto3.resource('dynamodb',region_name='us-east-1')
        for name in (app.TABLE,s.SUPPORT_TABLE,s.EVENTS_TABLE):
            d.create_table(TableName=name,KeySchema=[{'AttributeName':'pk','KeyType':'HASH'},{'AttributeName':'sk','KeyType':'RANGE'}],AttributeDefinitions=[{'AttributeName':'pk','AttributeType':'S'},{'AttributeName':'sk','AttributeType':'S'}],BillingMode='PAY_PER_REQUEST')
        monkeypatch.setattr(s,'ARCHIVE_BUCKET','test-transcript-archive')
        s.archive_client().create_bucket(Bucket=s.ARCHIVE_BUCKET,ObjectLockEnabledForBucket=True)
        s.archive_client().put_object_lock_configuration(Bucket=s.ARCHIVE_BUCKET,ObjectLockConfiguration={'ObjectLockEnabled':'Enabled','Rule':{'DefaultRetention':{'Mode':'GOVERNANCE','Days':30}}})
        yield
        s._c.clear();app._clients.clear()

def biz(owner='alice'):
    return s.save_business(owner,{'name':'Test Company','website':'https://example.com','domains':['https://example.com']})

def chat():
    b=biz();r=s.start_chat(b['siteId'],{'name':'Maya','consent':True,'category':'returns'},'192.0.2.1');return r['conversation'],r['token']

def event(path,method='GET',data=None,owner='alice',token=None):
    return {'rawPath':path,'headers':{'x-conversation-token':token or ''},'body':json.dumps(data or {}),'requestContext':{'http':{'method':method,'sourceIp':'192.0.2.1'},'authorizer':{'jwt':{'claims':{'sub':owner,'token_use':'access'}}} if owner else {}}}

def call(path,method='GET',data=None,owner='alice',token=None):
    r=app.handler(event(path,method,data,owner,token),None)
    return r['statusCode'],json.loads(r['body'])

def test_start_auth_and_ownership():
    c,t=chat();assert len(c['messages'])==2
    assert call('/public/support/conversations/'+c['id'],owner=None,token=t)[0]==200
    assert call('/public/support/conversations/'+c['id'],owner=None,token='wrong')[0]==404
    assert call('/api/support/conversations/'+c['id'],owner='mallory')[0]==404
    assert call('/api/support/conversations',owner=None)[0]==401
    assert 'tokenHash' not in c and 'owner' not in c

def test_append_idempotency_and_concurrency():
    c,t=chat();old=s.get_conversation(c['id']);new=s.append(old,'customer','Original message','one')
    retry=s.append(old,'customer','Original message','one');assert retry['seq']==new['seq']
    with pytest.raises(app.Problem) as e:s.append(old,'customer','Concurrent message','two')
    assert e.value.status==409
    assert s.verify(new)['valid']
    assert len(s.messages(c['id']))==3

def test_human_handoff_full_record_and_archive():
    c,t=chat();base='/api/support/conversations/'+c['id'];public='/public/support/conversations/'+c['id']
    assert call(public+'/handoff','POST',{'requestId':'handoff'},owner=None,token=t)[1]['mode']=='waiting'
    assert call(base+'/reply','POST',{'requestId':'early','content':'Hi'})[0]==409
    assert call(base+'/takeover','POST',{'requestId':'join'})[1]['mode']=='human'
    assert call(base+'/reply','POST',{'requestId':'reply','content':'I can help with this return.'})[0]==200
    closed_result=s.route(event(base+'/close','POST',{'requestId':'close'}));closed=json.loads(closed_result['body'])
    assert closed['status']=='closed' and closed['archive']['versionId']
    assert call(base+'/verify')[1]['archiveValid'] is True
    assert call(public+'/messages','POST',{'requestId':'late','content':'Edit it'},owner=None,token=t)[0]==409
    assert call(base+'/export')[1]['messages'][-1]['role']=='system'
    b=s.business('alice');s.save_business('alice',{**s.clean(b),'name':'Renamed business','version':int(b['version'])})
    assert call(base+'/verify')[1]['archiveValid'] is True
    stored=s.archive_client().head_object(Bucket=s.ARCHIVE_BUCKET,Key=closed['archive']['key'],VersionId=closed['archive']['versionId'])
    assert stored['ObjectLockMode']=='GOVERNANCE'

def test_tampering_is_detected():
    c,t=chat();item=s.events_table().get_item(Key=s.key('CHAT#'+c['id'],'EVENT#000002'))['Item'];item['content']='Tampered';s.events_table().put_item(Item=item)
    assert s.verify(s.get_conversation(c['id']))['valid'] is False

def test_retrieval_requires_approval_and_tenant_match():
    biz();biz('bob')
    s.save_source('alice',{'title':'Returns','content':'Unused products can be returned within 30 days of purchase.','approved':False})
    s.save_source('bob',{'title':'Returns','content':'Bob secret returns information only his customers may see.','approved':True})
    assert s.retrieve('alice','returns products')==[]
    doc=s.save_source('alice',{'title':'Shipping','content':'Shipping takes five working days for all standard deliveries.','approved':True})
    results=s.retrieve('alice','shipping days');assert results[0]['sourceId']==doc['id'];assert 'Bob' not in json.dumps(results)

def test_grounded_answer_and_unavailable_fallback(monkeypatch):
    c,t=chat();s.save_source('alice',{'title':'Returns','content':'Returns are accepted within 30 days for unused products.','approved':True})
    model=Mock();model.converse.return_value={'output':{'message':{'content':[{'text':json.dumps({'answer':'Unused products can be returned within 30 days.','sourceIds':['1'],'handoff':False})}]}}}
    monkeypatch.setattr(app,'bedrock',lambda:model)
    path='/public/support/conversations/'+c['id']+'/messages'
    code,result=call(path,'POST',{'requestId':'q1','content':'What is the returns policy?'},owner=None,token=t)
    assert code==200,result
    assert result['messages'][-1]['sources'][0]['title']=='Returns'
    model.converse.side_effect=ClientError({'Error':{'Code':'ThrottlingException','Message':'quota'}},'Converse')
    code,result=call(path,'POST',{'requestId':'q2','content':'Can I make returns?'},owner=None,token=t)
    assert code==200 and 'temporarily unavailable' in result['messages'][-1]['content']
    assert any(m['content']=='Can I make returns?' for m in result['messages'])

def test_late_ai_cannot_interrupt_human(monkeypatch):
    c,t=chat();s.save_source('alice',{'title':'Returns','content':'Returns are accepted within 30 days for unused products.','approved':True})
    def response(**kwargs):
        current=s.get_conversation(c['id']);s.append(current,'system','Human joined','human',{'mode':'human','status':'active'})
        return {'output':{'message':{'content':[{'text':'{"answer":"30 days","sourceIds":["1"]}'}]}}}
    model=Mock();model.converse.side_effect=response;monkeypatch.setattr(app,'bedrock',lambda:model)
    updated=s.answer(s.get_conversation(c['id']),'returns','query')
    assert updated['mode']=='human' and s.messages(c['id'])[-1]['content']=='Human joined'

def test_trial_and_plan_preference_do_not_grant_paid_access():
    c,t=chat();b=s.business('alice');b['trialEnds']=int(time.time())-1;s.store().put_item(Item=b)
    assert call('/api/support/select-plan','POST',{'plan':'scale'})[0]==200
    assert s.business('alice')['plan']=='trial'
    assert call('/public/support/conversations/'+c['id']+'/messages','POST',{'requestId':'expired','content':'hello'},owner=None,token=t)[0]==402
    assert call('/api/support/conversations/'+c['id']+'/export')[0]==200
    with pytest.raises(app.Problem):s.start_chat(b['siteId'],{'name':'M','consent':True},'192.0.2.2')

def test_ssrf_and_domain_limit(monkeypatch):
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',('127.0.0.1',443))])
    with pytest.raises(app.Problem):s.validate_url('https://example.com/private',['https://example.com'])
    with pytest.raises(app.Problem):s.validate_url('https://evil.example',['https://example.com'])
    with pytest.raises(app.Problem):s.save_business('a',{'name':'A','website':'https://a.example','domains':['https://b.example','https://c.example','https://d.example']})

def test_widget_embedding_is_restricted_to_registered_origins():
    b=biz();r=app.handler(event('/widget/'+b['siteId'],owner=None),None)
    assert r['statusCode']==200
    assert "frame-ancestors 'self' https://example.com" in r['headers']['Content-Security-Policy']
    assert 'X-Frame-Options' not in r['headers']


def test_customer_cannot_reuse_system_id_or_change_retry_content():
    c,t=chat();path='/public/support/conversations/'+c['id']+'/messages'
    code,result=call(path,'POST',{'requestId':'welcome','content':'Customer question'},owner=None,token=t)
    assert code==200 and any(m['role']=='customer' and m['content']=='Customer question' for m in result['messages'])
    assert call(path,'POST',{'requestId':'welcome','content':'Different question'},owner=None,token=t)[0]==409

def test_message_limit_reserves_closing_event():
    c,t=chat();current=s.get_conversation(c['id']);current['seq']=249
    s.store().put_item(Item=current)
    with pytest.raises(app.Problem):s.append(current,'customer','Too late','late')
    final=s.append(current,'system','Closed','close',{'status':'closed'})
    assert final['seq']==250 and final['status']=='closed'


def test_reviewer_grant_cannot_be_self_issued_or_extended():
    b=biz()
    assert not b['reviewAccessUntil']
    changed=s.save_business('alice',{**b,'reviewAccessUntil':int(time.time())+9000000})
    assert changed['reviewAccessUntil']==0
    grant=int(time.time())+3600
    s.store().update_item(Key=s.key('BIZ#alice','PROFILE'),UpdateExpression='SET reviewAccessUntil = :t, trialEnds = :e',ExpressionAttributeValues={':t':grant,':e':1})
    b=s.business('alice');s.ensure_active(b)
    changed=s.save_business('alice',{**s.clean(b),'version':int(b['version']),'reviewAccessUntil':grant+9000000})
    assert changed['reviewAccessUntil']==grant
    assert s.entitlements(changed)['ai']==100


def test_expired_reviewer_grant_does_not_bypass_trial():
    b=biz()
    b.update(trialEnds=1,reviewAccessUntil=2)
    with pytest.raises(app.Problem) as error:s.ensure_active(b)
    assert error.value.status==402
    b['trialEnds']=int(time.time())+3600
    s.ensure_active(b)


def test_saved_citation_survives_policy_removal_and_verifies_offline(monkeypatch):
    import importlib.util
    spec=importlib.util.spec_from_file_location('offline',Path(__file__).parents[1]/'scripts/verify_transcript.py')
    offline=importlib.util.module_from_spec(spec);spec.loader.exec_module(offline)
    c,t=chat()
    source=s.save_source('alice',{'title':'Returns','content':'Returns are accepted within 30 days for unused products.','approved':True})
    model=Mock();model.converse.return_value={'output':{'message':{'content':[{'text':json.dumps({'answer':'Unused products can be returned within 30 days.','sourceIds':['1'],'handoff':False})}]}}}
    monkeypatch.setattr(app,'bedrock',lambda:model)
    code,result=call('/public/support/conversations/'+c['id']+'/messages','POST',{'requestId':'q','content':'What is the returns policy?'},owner=None,token=t)
    assert code==200
    s.store().delete_item(Key=s.key('BIZ#alice','SOURCE#'+source['id']))
    saved=s.get_conversation(c['id']);export=s.transcript(saved)
    # Round-trip exactly as the JSON API does, converting DynamoDB numbers.
    export=json.loads(s.canon(export))
    assert '30 days' in export['messages'][-1]['sources'][0]['excerpt']
    assert s.retrieve('alice','returns policy')==[]
    assert offline.verify(export,export['lastDigest'])['chainConsistent']


def test_feedback_is_optional_isolated_and_does_not_change_archive():
    c, token = chat()
    private = '/api/support/conversations/' + c['id']
    public = '/public/support/conversations/' + c['id']
    payload = {'resolution': 'partly', 'rating': 3, 'comment': 'Clear record; needed a person.'}
    assert call(public+'/feedback', 'POST', payload, owner=None, token=token)[0] == 409
    assert call(private+'/close', 'POST', {'requestId': 'feedback-close'})[0] == 200
    before = call(private+'/export')[1]
    assert call(public+'/feedback', 'POST', payload, owner=None, token='wrong')[0] == 404
    first = call(public+'/feedback', 'POST', payload, owner=None, token=token)
    assert first[0] == 200
    assert call(public+'/feedback', 'POST', payload, owner=None, token=token) == first
    assert call(public+'/feedback', 'POST', {**payload, 'rating': 5}, owner=None, token=token)[0] == 409
    assert call(private, owner='mallory')[0] == 404
    assert call(private)[1]['feedback']['rating'] == 3
    assert call(public, owner=None, token=token)[1]['feedback']['resolution'] == 'partly'
    assert call(private+'/export')[1] == before
    assert call(private+'/verify')[1]['archiveValid'] is True


@pytest.mark.parametrize('change', [{'rating': True}, {'rating': 0}, {'rating': 6}, {'rating': '5'}, {'resolution': 'maybe'}, {'comment': ['bad']}, {'comment': 'x'*1001}])
def test_feedback_rejects_invalid_values(change):
    c, token = chat()
    assert call('/api/support/conversations/'+c['id']+'/close', 'POST', {'requestId':'close'})[0] == 200
    assert call('/public/support/conversations/'+c['id']+'/feedback', 'POST', {'resolution':'yes','rating':5, **change}, owner=None, token=token)[0] == 400
