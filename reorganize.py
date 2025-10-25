import os, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()

def log(msg): print(msg)
def safe_write(p, c):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(c.rstrip()+"\n")
    log(f"[WRITE] {p.relative_to(ROOT)}")

def nuke(p):
    if not p.exists(): return
    if p.is_file(): p.unlink(missing_ok=True)
    else: shutil.rmtree(p, ignore_errors=True)
    log(f"[DEL] {p.relative_to(ROOT)}")

def cleanup():
    keep_dirs = {"src","test","outbound",".venv",".git"}
    keep_files = {".env","reorganize.py","requirements.txt","pytest.ini","README.md","print_structure.py"}
    for x in ROOT.iterdir():
        if x.is_dir() and x.name not in keep_dirs: nuke(x)
        elif x.is_file() and x.name not in keep_files: nuke(x)
    for bad in ["src/test_lab","test/test_lab"]:
        nuke(ROOT/bad)
    for c in ROOT.rglob("__pycache__"): nuke(c)

def mkdirs():
    for d in [
        "src/analytics","src/coverage_engine","src/postman_export",
        "test/analytics","test/coverage_engine","test/postman_export","outbound"
    ]: Path(d).mkdir(parents=True, exist_ok=True)

# ---------------- root files ----------------
REQS = """pytest
python-dotenv
networkx
matplotlib
pydantic
openai
"""
PYTEST = "[pytest]\naddopts=-q\ntestpaths=test\npythonpath=src\n"
README = "# API Param Coverage\n\nRun:\npytest\npython -m src.coverage_engine.runner\npython src/postman_export/csv_to_postman_collection.py\npython src/analytics/coverage_graph.py\n"
PRINT = """import os
from datetime import datetime
def tree(p='.',ind='',f=None):
    for e in sorted(os.listdir(p)):
        if e in {'.venv','.git','__pycache__'}:continue
        path=os.path.join(p,e)
        line=ind+'├── '+e
        print(line);f.write(line+'\\n')
        if os.path.isdir(path):tree(path,ind+'│   ',f)
if __name__=='__main__':
    os.makedirs('outbound',exist_ok=True)
    ts=datetime.now().strftime('%Y%m%d_%H%M%S')
    o=f'outbound/project_structure_{ts}.txt'
    with open(o,'w',encoding='utf-8') as f:tree('.',f=f)
    print('Saved to',o)
"""

# ---------------- src ----------------
COVERAGE_CALC = """import itertools
def greedy_min_cover(space):
    if not space:return []
    keys=list(space)
    combos=[dict(zip(keys,v)) for v in itertools.product(*space.values())]
    allpairs={(k,v) for k,vs in space.items() for v in vs}
    cov=set();chosen=[]
    while cov!=allpairs:
        best=max(combos,key=lambda c:len(set(c.items())-cov))
        chosen.append(best);cov|=set(best.items())
    return chosen
"""
LLM = """def generate_bdd_for_endpoint(meta,scenarios,api_key=None):
    out=[]
    for i,s in enumerate(scenarios,1):
        txt=f"Given {s}\\nWhen {meta['method']} {meta['path']}\\nThen 200"
        out.append({'scenario_id':f"{meta['endpointName']}_scn_{i}",'gherkin_and_curl':txt})
    return out
"""
MODELS = "from dataclasses import dataclass\nfrom typing import Dict,List\n@dataclass\nclass ParamSpace: headers:Dict[str,List[str]];query:Dict[str,List[str]];body:Dict[str,List[str]]\n@dataclass\nclass Endpoint: apiName:str;endpointName:str;method:str;path:str;param_space:ParamSpace\n"
UTILS = """import json
from .models import ParamSpace,Endpoint
def load_collection(p):
    with open(p) as f:d=json.load(f)
    eps=[]
    for a in d.get('apis',[]):
        for e in a['endpoints']:
            ps=e.get('param_space',{})
            eps.append(Endpoint(a['apiName'],e['name'],e['method'],e['path'],ParamSpace(ps.get('headers',{}),ps.get('query',{}),ps.get('body',{}))))
    return eps
def flatten(ep):
    r={}
    for pre,g in [('header',ep.param_space.headers),('query',ep.param_space.query),('body',ep.param_space.body)]:
        for k,v in g.items():r[f"{pre}.{k}"]=v or ['<default>']
    return r
"""
RUNNER = """import os,csv,argparse
from . import utils,coverage_calculator,llm_bdd_generator
OUT_DIR='src/coverage_engine/outbound';CSV=OUT_DIR+'/bdd_scenarios.csv'
def gen(col):
    os.makedirs(OUT_DIR,exist_ok=True)
    eps=utils.load_collection(col);rows=[]
    for e in eps:
        space=utils.flatten(e)
        scs=coverage_calculator.greedy_min_cover(space)
        meta={'apiName':e.apiName,'endpointName':e.endpointName,'method':e.method,'path':e.path}
        for b in llm_bdd_generator.generate_bdd_for_endpoint(meta,scs):
            rows.append({**meta,**b})
    if not rows:return CSV
    with open(CSV,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    print('Wrote',CSV);return CSV
def main():
    a=argparse.ArgumentParser();a.add_argument('--collection',default='src/coverage_engine/outbound/sample.json')
    c=a.parse_args();gen(c.collection)
if __name__=='__main__':main()
"""
POSTMAN = """import csv,json,os
from datetime import datetime
CSV='src/coverage_engine/outbound/bdd_scenarios.csv';OUT='src/postman_export/outbound'
def main():
    if not os.path.exists(CSV):return print('no csv')
    with open(CSV) as f:r=csv.DictReader(f);items=[]
    for row in r:
        sc=[f"// {l}" for l in row['gherkin_and_curl'].split('\\\\n')]
        items.append({'name':row['endpointName'],'request':{'method':row['method'],'url':{'raw':row['path']}},'event':[{'listen':'test','script':{'type':'text/javascript','exec':sc}}]})
    os.makedirs(OUT,exist_ok=True)
    o=f"{OUT}/postman_{int(datetime.now().timestamp())}.json"
    json.dump({'info':{'name':'Coll'},'item':items},open(o,'w'),indent=2);print('Saved',o)
if __name__=='__main__':main()
"""
GRAPH = """import csv,os,networkx as nx,matplotlib.pyplot as plt
CSV='src/coverage_engine/outbound/bdd_scenarios.csv';OUT='src/analytics/outbound/graph.png'
def draw():
    G=nx.DiGraph()
    if not os.path.exists(CSV):return
    with open(CSV) as f:
        for r in csv.DictReader(f):G.add_edge(r['apiName'],r['endpointName'])
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    nx.draw(G,with_labels=True,node_color='lightblue');plt.savefig(OUT);plt.close();print('Saved',OUT)
if __name__=='__main__':draw()
"""

# ---------------- tests ----------------
T_CALC="from src.coverage_engine.coverage_calculator import greedy_min_cover\ndef test_cov():assert greedy_min_cover({'x':[1,2],'y':[3,4]])\n"
T_LLM="from src.coverage_engine.llm_bdd_generator import generate_bdd_for_endpoint\ndef test_llm():r=generate_bdd_for_endpoint({'endpointName':'e','method':'GET','path':'/'},[{'x':1}]);assert r\n"
T_RUN="import json,os;from src.coverage_engine.runner import gen\ndef test_run(tmp_path):d={'apis':[{'apiName':'a','endpoints':[{'name':'e','method':'GET','path':'/','param_space':{'headers':{'h':['x']},'query':{},'body':{}}}]}]};p=tmp_path/'c.json';p.write_text(json.dumps(d));gen(str(p))\n"
T_P="from src.postman_export.csv_to_postman_collection import main\ndef test_post(tmp_path,monkeypatch):f=tmp_path/'bdd.csv';f.write_text('apiName,endpointName,method,path,scenario_id,gherkin_and_curl\\na,b,GET,/,s,txt');monkeypatch.chdir(tmp_path);os.makedirs('src/postman_export/outbound',exist_ok=True);main()\n"
T_G="from src.analytics.coverage_graph import draw\ndef test_g(tmp_path,monkeypatch):monkeypatch.chdir(tmp_path);draw()\n"

def write_all():
    safe_write(ROOT/"requirements.txt",REQS)
    safe_write(ROOT/"pytest.ini",PYTEST)
    safe_write(ROOT/"README.md",README)
    safe_write(ROOT/"print_structure.py",PRINT)
    safe_write(ROOT/"src/coverage_engine/coverage_calculator.py",COVERAGE_CALC)
    safe_write(ROOT/"src/coverage_engine/llm_bdd_generator.py",LLM)
    safe_write(ROOT/"src/coverage_engine/models.py",MODELS)
    safe_write(ROOT/"src/coverage_engine/utils.py",UTILS)
    safe_write(ROOT/"src/coverage_engine/runner.py",RUNNER)
    safe_write(ROOT/"src/postman_export/csv_to_postman_collection.py",POSTMAN)
    safe_write(ROOT/"src/analytics/coverage_graph.py",GRAPH)
    safe_write(ROOT/"test/coverage_engine/test_coverage_calculator.py",T_CALC)
    safe_write(ROOT/"test/coverage_engine/test_llm_bdd_generator.py",T_LLM)
    safe_write(ROOT/"test/coverage_engine/test_runner_flow.py",T_RUN)
    safe_write(ROOT/"test/postman_export/test_csv_to_postman_collection.py",T_P)
    safe_write(ROOT/"test/analytics/test_coverage_graph.py",T_G)

if __name__=="__main__":
    log("[STEP] cleanup");cleanup()
    log("[STEP] mkdirs");mkdirs()
    log("[STEP] write files");write_all()
    log("✅ done, now run pytest")
