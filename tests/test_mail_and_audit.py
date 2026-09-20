"""Regression checks for audit findings; no real mail is sent."""
import sys
from pathlib import Path
import json
from unittest.mock import Mock
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'backend'))
from mail_templates import render,KINDS
import notifications
from test_support import db, biz, chat, call
import support as s
import app

@pytest.mark.parametrize('kind',list(KINDS))
def test_email_has_text_fallback_safe_content_and_no_trackers(kind):
    message=render(kind,'https://example.com','<script>alert(1)</script>')
    assert 'role="presentation"' in message['html']
    assert '#245e4c' in message['html'] and message['text']
    assert '<script>' not in message['html'] and '<img' not in message['html']
    assert 'https://example.com/app' in message['html']
    if kind=='verification':assert '{####}' in message['html']
    else:assert '&lt;script&gt;' in message['html']

@pytest.mark.parametrize('url',['javascript:alert(1)','http://example.com','https://u:p@example.com','https://example.com/?token=private'])
def test_mail_rejects_unsafe_action_links(url):
    with pytest.raises(ValueError):render('welcome',url)

def test_notification_no_send_without_configuration_or_optin(monkeypatch):
    monkeypatch.delenv('EMAIL_FROM',raising=False)
    assert notifications.notify({'owner':'alice'},'handoff','one')=='disabled'
    monkeypatch.setenv('EMAIL_FROM','noreply@example.com');monkeypatch.setenv('APP_ORIGIN','https://example.com');monkeypatch.setenv('POOL_ID','pool')
    assert notifications.notify({'owner':'alice','emailNotifications':False},'handoff','one')=='disabled'

def test_mail_uses_verified_owner_and_deduplicates(monkeypatch):
    biz();b=s.business('alice');b['emailNotifications']=True
    monkeypatch.setenv('EMAIL_FROM','noreply@example.com');monkeypatch.setenv('APP_ORIGIN','https://example.com');monkeypatch.setenv('POOL_ID','pool')
    auth=Mock();ses=Mock();auth.admin_get_user.return_value={'Enabled':True,'UserStatus':'CONFIRMED','UserAttributes':[{'Name':'email','Value':'owner@example.com'},{'Name':'email_verified','Value':'true'}]}
    original=notifications.boto3.client
    monkeypatch.setattr(notifications.boto3,'client',lambda name,**kw: auth if name=='cognito-idp' else ses if name=='sesv2' else original(name,**kw))
    assert notifications.notify(b,'handoff','one')=='accepted'
    assert notifications.notify(b,'handoff','one')=='duplicate'
    assert ses.send_email.call_count==1
    req=ses.send_email.call_args.kwargs
    assert req['Destination']['ToAddresses']==['owner@example.com']
    assert req['Content']['Simple']['Body']['Text']['Data']
    auth.admin_get_user.return_value['UserAttributes'][1]['Value']='false'
    assert notifications.notify(b,'closed','two')=='recipient_unverified'
    assert ses.send_email.call_count==1

@pytest.mark.parametrize('question',['Can I send it back?','What about returning this product?','Are returns allowed?'])
def test_retrieval_supports_common_word_variants(question):
    biz();source=s.save_source('alice',{'title':'Return policy','content':'Unused products can be returned within 30 days in their original packaging.','approved':True})
    result=s.retrieve('alice',question)
    assert result and result[0]['sourceId']==source['id']

@pytest.mark.parametrize('output',['[]','not JSON','{"answer":"Made up answer","sourceIds":["99"]}','{"answer":"No evidence","sourceIds":[]}'])
def test_invalid_ai_output_cannot_become_a_cited_answer(monkeypatch,output):
    c,t=chat();s.save_source('alice',{'title':'Return policy','content':'Unused products can be returned within 30 days in their original packaging.','approved':True})
    model=Mock();model.converse.return_value={'output':{'message':{'content':[{'text':output}]}}};monkeypatch.setattr(app,'bedrock',lambda:model)
    status,result=call('/public/support/conversations/'+c['id']+'/messages','POST',{'requestId':'q1','content':'What is your return policy?'},owner=None,token=t)
    assert status==200 and result['messages'][-1]['sources']==[]
    assert 'temporarily unavailable' in result['messages'][-1]['content']

def test_unapproved_knowledge_never_reaches_model(monkeypatch):
    c,t=chat();s.save_source('alice',{'title':'Secret policy','content':'This unapproved internal document must not be used in customer answers.','approved':False})
    model=Mock();monkeypatch.setattr(app,'bedrock',lambda:model)
    status,result=call('/public/support/conversations/'+c['id']+'/messages','POST',{'requestId':'q1','content':'What is the secret policy?'},owner=None,token=t)
    assert status==200 and 'approved company source' in result['messages'][-1]['content']
    model.converse.assert_not_called()

def test_email_optin_rejected_until_sending_configured(monkeypatch):
    monkeypatch.delenv('EMAIL_FROM',raising=False)
    with pytest.raises(app.Problem) as e:s.save_business('alice',{'name':'Test','website':'https://example.com','emailNotifications':True})
    assert e.value.status==400

def test_model_timeout_preserves_message_and_reports_status(monkeypatch):
    from botocore.exceptions import ReadTimeoutError
    c,t=chat();s.save_source('alice',{'title':'Returns','content':'Unused items can be returned within 30 days of delivery.','approved':True})
    model=Mock();model.converse.side_effect=ReadTimeoutError(endpoint_url='https://bedrock.example.invalid');monkeypatch.setattr(app,'bedrock',lambda:model)
    code,result=call('/public/support/conversations/'+c['id']+'/messages','POST',{'requestId':'timeout','content':'Can I return an unused item?'},owner=None,token=t)
    assert code==200 and 'temporarily unavailable' in result['messages'][-1]['content']
    assert any(m['role']=='customer' and 'unused item' in m['content'] for m in result['messages'])
    assert call('/api/support/usage')[1]['aiStatus']=='unavailable'
