"""Illustrative low-traffic monthly estimate; excludes unrelated account resources and tax."""
import json
from pathlib import Path
# Nova Lite Oregon rates verified by AWS Pricing GetProducts on 2026-09-19.
assumptions={'ai_calls':500,'input_tokens_per_call':9000,'output_tokens_per_call':1800,'http_requests':100000,'lambda_non_ai_requests':99500,'lambda_non_ai_seconds':0.15,'lambda_ai_seconds':29,'memory_gb':0.25,'database_write_units':1000000,'database_read_units':2000000,'database_gb':0.5,'logs_gb':0.2,'data_transfer_gb':3,'active_sellers':50}
a=assumptions
costs={'bedrock':a['ai_calls']*(a['input_tokens_per_call']*0.06+a['output_tokens_per_call']*0.24)/1000000,'http_api':a['http_requests']/1000000,'lambda_requests':a['http_requests']*0.2/1000000,'lambda_compute':(a['ai_calls']*a['lambda_ai_seconds']+a['lambda_non_ai_requests']*a['lambda_non_ai_seconds'])*a['memory_gb']*0.0000133334,'dynamodb_writes':a['database_write_units']*0.625/1000000,'dynamodb_reads':a['database_read_units']*0.125/1000000,'dynamodb_storage':a['database_gb']*0.25,'logs':a['logs_gb']*0.53,'data_transfer_allowance':a['data_transfer_gb']*0.09,'cognito_allowance':a['active_sellers']*0.0055,'artifact_storage_allowance':0.05,'s3_archive_storage_and_requests_allowance':0.10,'transactional_email_allowance':0.05}
result={'assumptions':a,'estimated_usd':{k:round(v,4) for k,v in costs.items()},'total_usd':round(sum(costs.values()),2),'planning_allowance_usd':5,'budget_usd':10,'note':'Estimates are not a hard spending cap. Includes conservative paid allowances rather than assuming free-tier eligibility. Model global monthly limit is enforced server-side; public traffic, AWS pricing, tax, and unrelated account spend can vary.'}
print(json.dumps(result,indent=2))
Path('docs/evidence/cost-estimate.json').write_text(json.dumps(result,indent=2))
