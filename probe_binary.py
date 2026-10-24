import os,uuid,urllib.request,urllib.error,urllib.parse
import solve
run_id,job_id=solve.backend_ids(os.environ['ACTIONS_RUNTIME_TOKEN'])
def v(n):
 out=bytearray()
 while n>127:out.append((n&127)|128);n>>=7
 out.append(n);return bytes(out)
def field(num,data):return v((num<<3)|2)+v(len(data))+data
def num(num,value):return v((num<<3)|0)+v(value)
name='probe-'+uuid.uuid4().hex[:10]+'.json'
body=field(1,run_id.encode())+field(2,job_id.encode())+field(3,name.encode())+num(5,7)+field(6,field(1,solve.NEL_JSON.encode()))
p=urllib.parse.urlsplit(os.environ['ACTIONS_RESULTS_URL']);u=f'{p.scheme}://{p.netloc}/twirp/{solve.ARTIFACT_SERVICE}/CreateArtifact'
for ct in ['application/protobuf','application/octet-stream']:
 try:
  req=urllib.request.Request(u,data=body,headers={'Authorization':'Bearer '+os.environ['ACTIONS_RUNTIME_TOKEN'],'Content-Type':ct},method='POST')
  with urllib.request.urlopen(req,timeout=10) as r:print(ct,'OK',r.status,r.headers.get('Content-Type'),r.read(200),flush=True)
 except urllib.error.HTTPError as e:print(ct,'HTTP',e.code,e.read(250),flush=True)
 except Exception as e:print(ct,'ERROR',repr(e),flush=True)
