import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('pilot_report',Path(__file__).parents[1]/'scripts/pilot_report.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def row(**changes):
    return dict(business_id='B1',task_id='T1',phase='orderproof',environment='live',owner_consent='yes',answer_origin='fallback',handling_seconds='60',resolved='yes',citation_correct='na',handoff_seconds='10',export_success='yes',owner_rating='4')|changes

def test_empty_pilot_cannot_claim_impact():
    with pytest.raises(ValueError,match='not yet measured'):p.summarize([])

def test_fallback_not_counted_as_ai_success():
    r=p.summarize([row(),row(task_id='T2',answer_origin='bedrock',citation_correct='no',resolved='no',handling_seconds='120')])['phases']['orderproof']
    assert r['answerOrigins']=={'human':0,'bedrock':1,'fallback':1}
    assert r['citations']=={'successful':0,'observed':1}
    assert r['medianHandlingSeconds']==90
    assert r['resolved']=={'successful':1,'observed':2}

@pytest.mark.parametrize('changes',[{'environment':'demo'},{'owner_consent':'no'},{'answer_origin':'fictional'},{'handling_seconds':'nan'},{'owner_rating':'6'},{'citation_correct':'yes'}])
def test_invalid_or_synthetic_evidence_rejected(changes):
    with pytest.raises(ValueError):p.summarize([row(**changes)])

def test_duplicates_rejected():
    with pytest.raises(ValueError,match='Duplicate'):p.summarize([row(),row()])


def test_business_breakdown_and_missing_measurement_denominators():
    report=p.summarize([row(business_id='B1',handling_seconds='10',handoff_seconds='',owner_rating=''),row(business_id='B2',handling_seconds='90',handoff_seconds='0',owner_rating='1')])
    assert report['businesses']==2
    assert report['phases']['orderproof']['medianHandlingSeconds']==50
    assert report['phases']['orderproof']['handoffMeasurements']==1
    assert report['phases']['orderproof']['ownerRatingMeasurements']==1
    first=report['perBusiness']['B1']['orderproof']
    assert first['medianHandlingSeconds']==10
    assert first['medianHandoffSeconds'] is None
    assert first['ownerRatingMeasurements']==0
    second=report['perBusiness']['B2']['orderproof']
    assert second['medianHandlingSeconds']==90
    assert second['medianHandoffSeconds']==0
    assert report['perBusiness']['B2']['baseline']['observations']==0
