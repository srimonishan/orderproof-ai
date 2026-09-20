import copy
import importlib.util
import json
from pathlib import Path
import time
from unittest.mock import Mock

import boto3
from moto import mock_aws
import pytest

spec = importlib.util.spec_from_file_location('app', Path(__file__).parents[1] / 'backend' / 'app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

@pytest.fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    with mock_aws():
        db = boto3.resource('dynamodb', region_name='us-east-1')
        db.create_table(TableName=app.TABLE, KeySchema=[{'AttributeName':'pk','KeyType':'HASH'},{'AttributeName':'sk','KeyType':'RANGE'}], AttributeDefinitions=[{'AttributeName':'pk','AttributeType':'S'},{'AttributeName':'sk','AttributeType':'S'}], BillingMode='PAY_PER_REQUEST')
        app._clients.clear()
        yield
        app._clients.clear()


def order(owner='alice'):
    oid='a'*24
    fields={k:{'value':v,'quote':'','source':'seller'} for k,v in zip(app.FIELDS, ['Maya','Chocolate cake','20 servings','Blue stars','2026-09-27 16:00 pickup','LKR 8500',''])}
    item={**app.key(owner,oid),'id':oid,'fields':fields,'questions':[],'changes':[],'inquiries':[], 'conversation':'private original conversation','status':'draft','revision':1,'version':1,'history':[], 'confirmation':None,'customerRequest':'','shareHash':'','shareExpires':0,'createdAt':app.now(),'updatedAt':app.now()}
    app.table().put_item(Item=item)
    return item


def event(path, method='GET', data=None, owner='alice', token_use='access'):
    context={'http':{'method':method}}
    if owner:
        context['authorizer']={'jwt':{'claims':{'sub':owner,'token_use':token_use}}}
    return {'rawPath':path,'requestContext':context,'body':json.dumps(data or {})}


def test_auth_cannot_be_bypassed_through_default_route():
    assert app.handler(event('/api/orders',owner=None),None)['statusCode']==401
    assert app.handler(event('/api/orders',token_use='id'),None)['statusCode']==401


def test_other_seller_cannot_access_or_modify_order():
    item=order()
    for method in ['GET','PUT','DELETE']:
        assert app.handler(event('/api/orders/'+item['id'],method,{'version':1},owner='bob'),None)['statusCode']==404
    assert json.loads(app.handler(event('/api/orders',owner='bob'),None)['body'])==[]


def test_share_does_not_expose_conversation_or_source():
    item=order()
    shared=app.share_order(item,{'version':1})
    public=app.public_visible(app.public_order(shared['token']))
    assert 'conversation' not in public
    assert 'history' not in public
    assert isinstance(public['fields']['product'],str)
    assert 'shareHash' not in shared['order']


def test_confirmation_is_bound_to_revision_and_edits_revoke_link():
    item=order()
    shared=app.share_order(item,{'version':1})
    active=app.public_order(shared['token'])
    confirmed=app.public_action(active,{'version':2,'revision':1,'action':'confirm','accepted':True,'name':'Maya'})
    assert confirmed['status']=='confirmed'
    item=app.get_order('alice',item['id'])
    fields={k:v['value'] for k,v in item['fields'].items()}
    fields['fulfillment']='2026-09-28 16:00 pickup'
    edited=app.edit_order(item,{'version':3,'fields':fields,'questions':[]})
    assert edited['revision']==2 and edited['confirmation'] is None
    assert edited['history'][0]['confirmation']['revision']==1
    with pytest.raises(app.Problem) as exc:
        app.public_order(shared['token'])
    assert exc.value.status==410


def test_stale_confirmation_race_cannot_overwrite_seller_edit():
    item=order()
    shared=app.share_order(item,{'version':1})
    stale=app.public_order(shared['token'])
    fresh=app.get_order('alice',item['id'])
    fields={k:v['value'] for k,v in fresh['fields'].items()}
    fields['price']='LKR 9000'
    app.edit_order(fresh,{'version':2,'fields':fields,'questions':[]})
    with pytest.raises(app.Problem) as exc:
        app.public_action(stale,{'version':2,'revision':1,'action':'confirm','accepted':True,'name':'Maya'})
    assert exc.value.status==409
    assert app.get_order('alice',item['id'])['fields']['price']['value']=='LKR 9000'


def test_double_response_is_rejected():
    item=order(); shared=app.share_order(item,{'version':1})
    active=app.public_order(shared['token'])
    app.public_action(active,{'version':2,'revision':1,'action':'request','message':'Change the date please'})
    with pytest.raises(app.Problem):
        app.public_action(app.public_order(shared['token']),{'version':3,'revision':1,'action':'confirm','accepted':True,'name':'Maya'})


def test_unresolved_questions_block_sharing():
    item=order();item['questions']=['AM or PM?']
    with pytest.raises(app.Problem) as exc: app.share_order(item,{'version':1})
    assert exc.value.status==400


def test_noop_save_preserves_confirmation():
    item=order(); shared=app.share_order(item,{'version':1})
    app.public_action(app.public_order(shared['token']),{'version':2,'revision':1,'action':'confirm','accepted':True,'name':'Maya'})
    item=app.get_order('alice',item['id'])
    result=app.edit_order(item,{'version':3,'fields':{k:v['value'] for k,v in item['fields'].items()},'questions':[]})
    assert result['status']=='confirmed' and result['revision']==1


def test_delete_invalidates_shared_link():
    item=order(); shared=app.share_order(item,{'version':1})
    assert app.handler(event('/api/orders/'+item['id'],'DELETE',{'version':2}),None)['statusCode']==200
    with pytest.raises(app.Problem): app.public_order(shared['token'])


def test_revocation_prevents_stale_public_write():
    item=order();shared=app.share_order(item,{'version':1});stale=app.public_order(shared['token'])
    assert app.handler(event('/api/orders/'+item['id']+'/revoke','POST',{'version':2}),None)['statusCode']==200
    with pytest.raises(app.Problem) as exc:
        app.public_action(stale,{'version':2,'revision':1,'action':'confirm','accepted':True,'name':'Maya'})
    assert exc.value.status==409


def test_unverifiable_ai_fields_are_removed():
    result=app.validate_extraction({'fields':{'price':{'value':'5000','quote':'invented quote'},'product':{'value':'Chocolate','quote':'chocolate cake'}}},'Please make a chocolate cake')
    assert result['fields']['price']['value']==''
    assert result['fields']['product']['value']=='Chocolate'
    assert result['questions']


def test_usage_limit_is_enforced():
    app.consume('example',2,int(time.time())+3600)
    app.consume('example',2,int(time.time())+3600)
    with pytest.raises(app.Problem) as exc: app.consume('example',2,int(time.time())+3600)
    assert exc.value.status==429


def test_expired_link_cannot_be_used():
    item=order();shared=app.share_order(item,{'version':1})
    hashed=app.hashlib.sha256(shared['token'].encode()).hexdigest()
    app.table().update_item(Key={'pk':'SHARE#'+hashed,'sk':'META'},UpdateExpression='SET expires = :e',ExpressionAttributeValues={':e':1})
    with pytest.raises(app.Problem) as exc:app.public_order(shared['token'])
    assert exc.value.status==410


def test_malformed_and_oversized_requests_are_rejected():
    e=event('/api/orders','POST');e['body']='[]'
    assert app.handler(e,None)['statusCode']==400
    e['body']='x'*49000
    assert app.handler(e,None)['statusCode']==413


def test_client_cannot_forge_extraction():
    client=Mock()
    client.converse.return_value={'output':{'message':{'content':[{'text':json.dumps({'fields':{'product':{'value':'Cake','quote':'cake'}}})}]}}}
    app._clients['bedrock']=client
    res=app.handler(event('/api/orders','POST',{'conversation':'Please make a cake','fields':{'price':{'value':'free'}}}),None)
    assert res['statusCode']==201
    data=json.loads(res['body'])
    assert data['fields']['price']['value']==''
    assert client.converse.call_args.kwargs['inferenceConfig']['maxTokens']==1800
