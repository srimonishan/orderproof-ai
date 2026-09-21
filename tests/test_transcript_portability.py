import copy
import hashlib
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('verifier',Path(__file__).parents[1]/'scripts/verify_transcript.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def sample():
    events=[];previous='0'*64
    for i,role in enumerate(['customer','assistant','agent'],1):
        e={'sequence':i,'previousDigest':previous,'role':role,'content':'Message '+str(i),'sources':[{'excerpt':'Returns within 30 days.','sourceDigest':'historical-source'}] if role=='assistant' else []}
        e['digest']=hashlib.sha256(v.canonical(e).encode()).hexdigest();previous=e['digest'];events.append(e)
    return {'format':'orderproof-transcript-v1','messages':events,'lastDigest':previous}

def test_valid_export_with_trusted_digest():
    r=sample();assert v.verify(r,r['lastDigest'])['trustedDigestMatched'] is True

@pytest.mark.parametrize('kind',['content','citation','missing','reorder','tail'])
def test_mutations_rejected(kind):
    r=sample()
    if kind=='content':r['messages'][0]['content']='Changed'
    if kind=='citation':r['messages'][1]['sources'][0]['excerpt']='Returns within 999 days.'
    if kind=='missing':r['messages'].pop(1)
    if kind=='reorder':r['messages'].reverse()
    if kind=='tail':r['lastDigest']='f'*64
    with pytest.raises(ValueError):v.verify(r)

def test_rehashed_forgery_requires_independent_anchor():
    r=sample();trusted=r['lastDigest'];r['messages'][0]['content']='Rewritten'
    previous='0'*64
    for e in r['messages']:
        e['previousDigest']=previous
        e['digest']=hashlib.sha256(v.canonical({k:x for k,x in e.items() if k!='digest'}).encode()).hexdigest();previous=e['digest']
    r['lastDigest']=previous
    assert v.verify(r)['trustedDigestMatched'] is None
    with pytest.raises(ValueError,match='trusted'):v.verify(r,trusted)

def test_demo_export_rejected():
    with pytest.raises(ValueError):v.verify({'demo':True,'messages':[]})
