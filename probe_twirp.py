import os,json,uuid,urllib.request,urllib.error,urllib.parse
import solve
run_id,job_id=solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
parsed=urllib.parse.urlsplit(os.environ['ACTIONS_RESULTS_URL'])
url=f'{parsed.scheme}://{parsed.netloc}/twirp/{solve.ARTIFACT_SERVICE}/CreateArtifact'
base={'workflow_run_backend_id':run_id,'workflow_job_run_backend_id':job_id,'name':'probe-'+uuid.uuid4().hex[:10]+'.json','version':7}
nel='\x85application/json'
cases=[
 ('snake_nel',json.dumps({**base,'mime_type':nel})),
 ('camel_nel',json.dumps({**base,'mimeType':nel})),
 ('wrapper',json.dumps({**base,'mime_type':{'value':nel}})),
 ('null',json.dumps({**base,'mime_type':None})),
 ('valid_then_bad',json.dumps({**base,'mime_type':'application/json'})[:-1]+',"mimeType":'+json.dumps(nel)+'}'),
 ('bad_then_valid',json.dumps({**base,'mime_type':nel})[:-1]+',"mimeType":"application/json"}'),
 ('dup_valid_bad',json.dumps({**base,'mime_type':'application/json'})[:-1]+',"mime_type":'+json.dumps(nel)+'}'),
 ('dup_bad_valid',json.dumps({**base,'mime_type':nel})[:-1]+',"mime_type":"application/json"}'),
 ('string_version',json.dumps({**base,'version':'7','mime_type':nel})),
]
for label,body in cases:
 try:
  req=urllib.request.Request(url,data=body.encode(),headers={'Authorization':'Bearer '+os.environ['ACTIONS_RUNTIME_TOKEN'],'Content-Type':'application/json'},method='POST')
  with urllib.request.urlopen(req,timeout=10) as r:print(label,'OK',r.read(200),flush=True)
 except urllib.error.HTTPError as e:print(label,'HTTP',e.code,e.read(250),flush=True)
 except Exception as e:print(label,'ERROR',repr(e),flush=True)
