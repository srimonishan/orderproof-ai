"""Opt-in, verified-owner transactional notices. Disabled until SES is configured.
Never sends chat bodies or customer capability tokens. Uncertain sends are not retried
implicitly; the business can still see its durable in-app inbox and archives.
"""
import os
import time
import hashlib
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from mail_templates import render


def configured():
    return bool(os.environ.get('EMAIL_FROM') and os.environ.get('APP_ORIGIN') and os.environ.get('POOL_ID'))


def notify(business, kind, event_id):
    if not configured() or not business.get('emailNotifications', False):
        return 'disabled'
    import app as a
    import support as s
    digest = hashlib.sha256((kind + ':' + event_id).encode()).hexdigest()
    key = {'pk': 'BIZ#' + business['owner'], 'sk': 'MAIL#' + digest}
    try:
        s.store().put_item(Item={**key, 'deliveryStatus': 'processing', 'kind': kind, 'expires': int(time.time()) + 90*86400}, ConditionExpression='attribute_not_exists(pk)')
    except ClientError as e:
        if e.response['Error']['Code']=='ConditionalCheckFailedException':
            return 'duplicate'
        return 'unavailable'
    except BotoCoreError:
        return 'unavailable'
    status = 'unavailable'
    try:
        a.rate_user(business['owner'], 'email', 5)
        a.consume('MAIL#' + time.strftime('%Y-%m',time.gmtime()), 200, int(time.time())+5500000)
        cfg=Config(connect_timeout=2,read_timeout=3,retries={'total_max_attempts':1})
        user=boto3.client('cognito-idp',region_name=a.REGION,config=cfg).admin_get_user(UserPoolId=os.environ['POOL_ID'],Username=business['owner'])
        attrs={v['Name']:v['Value'] for v in user['UserAttributes']}
        if attrs.get('email_verified')!='true' or not user.get('Enabled') or user.get('UserStatus')!='CONFIRMED':
            status='recipient_unverified'
        else:
            mail=render(kind,os.environ['APP_ORIGIN'],business['name'])
            boto3.client('sesv2',region_name=a.REGION,config=cfg).send_email(
                FromEmailAddress='OrderProof <'+os.environ['EMAIL_FROM']+'>',
                Destination={'ToAddresses':[attrs['email']]},
                Content={'Simple':{'Subject':{'Data':mail['subject'],'Charset':'UTF-8'},'Body':{'Html':{'Data':mail['html'],'Charset':'UTF-8'},'Text':{'Data':mail['text'],'Charset':'UTF-8'}}}})
            status='accepted'  # SES acceptance is not proof of inbox delivery.
    except (ClientError,BotoCoreError,a.Problem,ValueError,KeyError):
        status='unavailable'
    try:
        s.store().update_item(Key=key,UpdateExpression='SET deliveryStatus = :s',ExpressionAttributeValues={':s':status})
    except ClientError:
        pass
    return status
