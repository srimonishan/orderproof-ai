"""Grant bounded reviewer access using administrator AWS credentials, never a public API.
Only the access deadline changes; AI, source, and traffic limits remain in force.
"""
import argparse
from datetime import datetime, timezone
import boto3
from botocore.config import Config


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table',required=True)
    parser.add_argument('--owner-sub',required=True,help='Cognito subject of the existing reviewer workspace owner')
    parser.add_argument('--until',default='2026-11-01T00:00:00+00:00')
    parser.add_argument('--region',default='us-east-1')
    args=parser.parse_args()
    end=datetime.fromisoformat(args.until)
    now=datetime.now(timezone.utc)
    if end.tzinfo is None or not 0 < (end-now).total_seconds() <= 60*86400:
        parser.error('Use a timezone-aware deadline within the next 60 days.')
    table=boto3.resource('dynamodb',region_name=args.region,config=Config(retries={'total_max_attempts':2})).Table(args.table)
    table.update_item(Key={'pk':'BIZ#'+args.owner_sub,'sk':'PROFILE'},
        UpdateExpression='SET reviewAccessUntil = :end, reviewGrantedAt = :now ADD #version :one',
        ConditionExpression='attribute_exists(pk)',ExpressionAttributeNames={'#version':'version'},
        ExpressionAttributeValues={':end':int(end.timestamp()),':now':now.isoformat(),':one':1})
    print('Reviewer access granted through '+end.isoformat()+'. Existing usage limits remain unchanged.')


if __name__=='__main__':main()
