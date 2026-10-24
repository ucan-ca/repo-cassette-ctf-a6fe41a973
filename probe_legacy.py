import os,json,urllib.request,urllib.error,uuid
base=os.environ.get('ACTIONS_RUNTIME_URL','')
token=os.environ.get('ACTIONS_RUNTIME_TOKEN','')
run=os.environ.get('GITHUB_RUN_ID','')
print('runtime_available',bool(base),'run_available',bool(run),flush=True)
if not (base and token and run):raise SystemExit()
url=base.rstrip('/')+'/_apis/pipelines/workflows/'+run+'/artifacts?api-version=6.0-preview'
body=json.dumps({'Type':'actions_storage','Name':'cassette-legacy-'+uuid.uuid4().hex[:8]}).encode()
request=urllib.request.Request(url,data=body,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
try:r=urllib.request.urlopen(request,timeout=15)
except urllib.error.HTTPError as error:r=error
print('legacy_create_status',r.status,'body',r.read(500).decode(errors='replace'),flush=True)
