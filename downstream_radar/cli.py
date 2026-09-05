"""Test a release candidate against declared consumers, with a real baseline."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from pathlib import Path
import sys, tempfile, tomllib
from . import __version__
from ._runtime import child_env, command, copy_project, dump, run, sha, snapshot

def read_manifest(path):
 path=Path(path).resolve(); data=tomllib.loads(path.read_text(encoding='utf-8'))
 if data.get('version')!=1 or not isinstance(data.get('projects'),list) or not data['projects']: raise ValueError('Manifest needs version = 1 and at least one [[projects]] table.')
 names=set()
 for item in data['projects']:
  name=item.get('name')
  if not isinstance(name,str) or not name.strip() or name in names: raise ValueError('Each project needs a unique non-empty name.')
  names.add(name); item['path']=str((path.parent/item['path']).resolve()); command(item.get('test'))
  for setup in item.get('setup',[]): command(setup)
 return data
def expand(argv,package,work): return [arg.replace('{python}',sys.executable).replace('{package}',str(package)).replace('{workspace}',str(work)) for arg in command(argv)]
def phase(project,package_source,phase_name,timeout,pass_env):
 with tempfile.TemporaryDirectory(prefix=f'radar-{phase_name}-') as temporary:
  base=Path(temporary); work,package,home=base/'consumer',base/'package',base/'home'; copy_project(project['path'],work); copy_project(package_source,package); consumer_files,package_files=snapshot(work),snapshot(package)
  extra={key:os.environ[key] for key in pass_env if key in os.environ}; extra.update(RADAR_PACKAGE=str(package),RADAR_PHASE=phase_name,RADAR_WORKSPACE=str(work)); env=child_env(home,extra); steps=[]
  for argv in project.get('setup',[]):
   result=run(expand(argv,package,work),work,timeout=timeout,env=env); steps.append(result)
   if result['status']!='completed' or result['exit_code']!=0: return {'ready':False,'setup':steps,'test':None,'consumer_files':consumer_files,'package_files':package_files}
  result=run(expand(project['test'],package,work),work,timeout=timeout,env=env); return {'ready':True,'setup':steps,'test':result,'consumer_files':consumer_files,'package_files':package_files}
def classify(baseline,candidate):
 if not baseline['ready'] or baseline['test']['status']!='completed': return 'baseline-unavailable'
 if baseline['test']['exit_code']!=0: return 'baseline-failed'
 if not candidate['ready'] or candidate['test']['status']!='completed': return 'candidate-unavailable'
 return 'compatible' if candidate['test']['exit_code']==0 else 'regression'
def test_project(project,baseline,candidate,timeout,pass_env):
 results={}
 for name,source in [('baseline',baseline),('candidate',candidate)]:
  try: results[name]=phase(project,source,name,timeout,pass_env)
  except (OSError,ValueError) as exc: results[name]={'ready':False,'setup':[],'test':None,'error':str(exc)}
 return {'project':project['name'],'status':classify(results['baseline'],results['candidate']),**results}
def check(manifest,baseline,candidate,*,timeout=120,jobs=1,pass_env=()):
 if not 1<=jobs<=8 or not 0<timeout<=3600: raise ValueError('Jobs must be 1..8; timeout must be 0 < seconds <= 3600.')
 baseline,candidate=Path(baseline).resolve(),Path(candidate).resolve()
 if not baseline.is_dir() or not candidate.is_dir(): raise ValueError('Baseline and candidate must be existing local package directories.')
 spec=read_manifest(manifest)
 with ThreadPoolExecutor(max_workers=jobs) as pool: results=list(pool.map(lambda p:test_project(p,baseline,candidate,timeout,pass_env),spec['projects']))
 compatible=sum(r['status']=='compatible' for r in results); regressions=sum(r['status']=='regression' for r in results); comparable=compatible+regressions
 return {'schema':1,'tool':'downstream-radar','version':__version__,'created_at':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(Path(manifest).read_bytes()),'results':results,'compatible':compatible,'regressions':regressions,'inconclusive':len(results)-comparable,'total':len(results),'compatibility_percent':round(100*compatible/comparable,1) if comparable else None,'environment_names':list(pass_env)}
def markdown(report):
 lines=['# Downstream Radar','',f'{report["compatible"]} compatible / {report["regressions"]} regressions / {report["inconclusive"]} inconclusive.','','This describes the declared test set, not the entire package ecosystem.','','| Consumer | Result | Baseline exit | Candidate exit |','| --- | --- | ---: | ---: |']
 for row in report['results']:
  exits=[(row[p]['test'] or {}).get('exit_code','not run') for p in ('baseline','candidate')]; lines.append(f'| {row["project"]} | {row["status"]} | {exits[0]} | {exits[1]} |')
 return '\n'.join(lines)+'\n'
def main(argv=None):
 parser=argparse.ArgumentParser(description='Catch release regressions in the projects that depend on you.'); parser.add_argument('--version',action='version',version=__version__); sub=parser.add_subparsers(dest='action',required=True); p=sub.add_parser('run'); p.add_argument('manifest',type=Path); p.add_argument('--baseline',type=Path,required=True); p.add_argument('--candidate',type=Path,required=True); p.add_argument('--trust',action='store_true',required=True); p.add_argument('--timeout',type=float,default=120); p.add_argument('--jobs',type=int,default=1); p.add_argument('--pass-env',action='append',default=[]); p.add_argument('--json',type=Path,dest='report',required=True); p.add_argument('--markdown',type=Path); args=parser.parse_args(argv)
 try:
  report=check(args.manifest,args.baseline,args.candidate,timeout=args.timeout,jobs=args.jobs,pass_env=args.pass_env); dump(args.report,report)
  if args.markdown: args.markdown.parent.mkdir(parents=True,exist_ok=True); args.markdown.write_text(markdown(report),encoding='utf-8')
  for row in report['results']: print(f'{row["status"].upper():23} {row["project"]}')
  return 1 if report['regressions'] else 2 if report['inconclusive'] else 0
 except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc: print(f'downstream-radar: {exc}',file=sys.stderr); return 2
def entrypoint(): raise SystemExit(main())
