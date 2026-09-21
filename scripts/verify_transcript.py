"""Verify an exported OrderProof transcript offline using Python's standard library.
A trusted final digest must be obtained separately to detect a wholly rewritten chain.
This does not verify identity, factual accuracy, timestamps, or S3 retention.
"""
import argparse
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',', ':'),ensure_ascii=False)


def verify(record,expected_digest=None):
    if not isinstance(record,dict) or record.get('format')!='orderproof-transcript-v1':
        raise ValueError('Unsupported transcript format; fictional demo exports are not verifiable records.')
    messages=record.get('messages')
    if not isinstance(messages,list) or not messages:raise ValueError('Missing conversation events.')
    previous='0'*64
    for index,event in enumerate(messages,1):
        if not isinstance(event,dict) or event.get('sequence')!=index or event.get('previousDigest')!=previous:
            raise ValueError('Broken event sequence or previous digest at event '+str(index))
        payload={k:v for k,v in event.items() if k not in ('pk','sk','digest','expires')}
        digest=hashlib.sha256(canonical(payload).encode()).hexdigest()
        if event.get('digest')!=digest:raise ValueError('Event content or citation changed at event '+str(index))
        previous=digest
    if record.get('lastDigest')!=previous:raise ValueError('Final digest does not match.')
    if expected_digest is not None and expected_digest!=previous:raise ValueError('Transcript differs from the separately trusted digest.')
    return {'chainConsistent':True,'messageCount':len(messages),'lastDigest':previous,'trustedDigestMatched':True if expected_digest is not None else None,'scope':'Event contents and saved citations only. Top-level metadata, identity, factual accuracy, and archive retention are not authenticated. Without a separately trusted digest, a rewritten chain is not detectable.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transcript',type=Path)
    parser.add_argument('--expected-digest',help='Final SHA-256 digest obtained independently from a trusted record')
    args=parser.parse_args()
    try:
        if args.transcript.stat().st_size>10*1024*1024:raise ValueError('Limit transcript input to 10 MB.')
        result=verify(json.loads(args.transcript.read_text()),args.expected_digest)
    except (ValueError,OSError) as error:parser.exit(1,'Verification failed: '+str(error)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
