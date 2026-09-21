"""Summarize owner-recorded real-business observations; never infer market validation.
No customer content or identifiers are needed. Keep inputs and reports private until approved.
"""
import argparse
import csv
import json
import math
import statistics
from pathlib import Path


def summarize(rows):
    groups={'baseline':[], 'orderproof':[]}
    seen=set()
    for row in rows:
        if row.get('environment')!='live' or row.get('owner_consent')!='yes':
            raise ValueError('Only consented live observations are eligible; exclude demos and synthetic tests.')
        phase=row.get('phase')
        if phase not in groups or not row.get('business_id') or not row.get('task_id'):
            raise ValueError('Provide an anonymous business/task identifier and a valid phase.')
        key=(row['business_id'],row['task_id'],phase)
        if key in seen:raise ValueError('Duplicate observation identifier.')
        seen.add(key)
        origin=row.get('answer_origin')
        if origin not in ('human','bedrock','fallback') or (phase=='baseline' and origin!='human'):
            raise ValueError('Use human baseline answers and record the actual live answer origin. Fictional answers are excluded.')
        seconds=float(row['handling_seconds'])
        if not math.isfinite(seconds) or seconds<0:raise ValueError('Handling time must be finite and nonnegative.')
        if row.get('resolved') not in ('yes','no'):raise ValueError('Resolution must be yes or no.')
        for field in ('citation_correct','export_success'):
            if row.get(field) not in ('yes','no','na'):raise ValueError(field+' must be yes, no, or na.')
        if origin!='bedrock' and row['citation_correct']!='na':raise ValueError('Only a real Bedrock answer can have a citation-quality rating.')
        handoff=float(row['handoff_seconds']) if row.get('handoff_seconds') else None
        if handoff is not None and (not math.isfinite(handoff) or handoff<0):raise ValueError('Invalid handoff duration.')
        rating=int(row['owner_rating']) if row.get('owner_rating') else None
        if rating is not None and not 1<=rating<=5:raise ValueError('Owner rating must be from 1 to 5.')
        groups[phase].append({**row,'seconds':seconds,'handoff':handoff,'rating':rating})
    if not seen:raise ValueError('No real observations supplied. Market impact is not yet measured.')
    def median(values):return round(statistics.median(values),2) if values else None
    def ratio(items,field):
        measured=[r for r in items if r[field]!='na']
        return {'successful':sum(r[field]=='yes' for r in measured),'observed':len(measured)}
    result={'status':'observations_recorded_not_independent_validation','limitations':['Owner-entered observations; consent and live provenance are declarations, not independently verified.','Small convenience samples do not establish causation, demand, revenue, or product-market fit.','Baseline and product phases may differ in task difficulty; no savings percentage is inferred.'],'businesses':len({r['business_id'] for rows in groups.values() for r in rows}),'phases':{}}
    for phase,items in groups.items():
        result['phases'][phase]={'observations':len(items),'medianHandlingSeconds':median([r['seconds'] for r in items]),'resolved':ratio(items,'resolved'),'answerOrigins':{o:sum(r['answer_origin']==o for r in items) for o in ('human','bedrock','fallback')},'citations':ratio(items,'citation_correct'),'exports':ratio(items,'export_success'),'medianHandoffSeconds':median([r['handoff'] for r in items if r['handoff'] is not None]),'medianOwnerRating':median([r['rating'] for r in items if r['rating'] is not None])}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        with args.csv_file.open(newline='') as f:report=summarize(list(csv.DictReader(f)))
    except (ValueError,KeyError) as error:parser.error(str(error))
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Report saved. Results are descriptive observations, not a production-readiness certificate.')

if __name__=='__main__':main()
