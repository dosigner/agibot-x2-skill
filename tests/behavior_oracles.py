"""Independent checks for code produced by the opt-in skill behavior probes.

Run against an isolated generated workspace, never the robot project.
"""
import argparse
from pathlib import Path
import subprocess
import sys

CHECKS = {
    'sensors': """import geometry as m, math
c=dict(fx=500.,fy=500.,cx=320.,cy=240.,scale_m_per_raw=.001,depth_kind='optical_z',rectified=True)
p=m.deproject(2500,420,290,c)
assert all(abs(a-b)<1e-9 for a,b in zip(p,(.5,.25,2.5))), p
assert m.deproject(0,420,290,c) is None
for patch in [dict(fx=0),dict(scale_m_per_raw=0),dict(scale_m_per_raw=float('nan')),dict(rectified=False),dict(depth_kind='unknown')]:
 try: m.deproject(2500,420,290,dict(c,**patch))
 except ValueError: pass
 else: raise AssertionError(('accepted invalid calibration',patch))
for args in [(float('nan'),420,290),(2500,float('inf'),290),(-1,420,290)]:
 try:m.deproject(*args,c)
 except ValueError:pass
 else:raise AssertionError(('accepted invalid input',args))
try:p=m.deproject(2500,420,290,dict(c,depth_kind='range'))
except ValueError:pass
else:
 expected=[v*2.5/math.sqrt(1.05) for v in (.2,.1,1)]
 assert all(abs(a-b)<1e-9 for a,b in zip(p,expected)),p
print('independent sensor oracle passed')
""",
    'slam': """import pose as m, copy
I=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
A=copy.deepcopy(I);A[0][3]=10
B=[[0,-1,0,0],[1,0,0,2],[0,0,1,0],[0,0,0,1]]
C=copy.deepcopy(I);C[0][3]=1
expected=[[0,-1,0,10],[1,0,0,1],[0,0,1,0],[0,0,0,1]]
actual=m.base_in_nav(I,A,B,C)
assert max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-9,actual
bad=[]
for i,j,val in [(0,0,-1),(0,0,2),(3,0,1),(0,3,float('nan'))]:
 x=copy.deepcopy(I);x[i][j]=val;bad.append(x)
bad.append([[1]])
for x in bad:
 for k in range(4):
  args=[I,I,I,I];args[k]=x
  try:m.base_in_nav(*args)
  except ValueError:pass
  else:raise AssertionError(('invalid transform accepted',k,x))
print('independent rigid transform oracle passed')
""",
    'control': """import ledger as m
base=dict(sent=False,response_accepted=False,observed_running=False,observed_finished=False,cleanup_confirmed=False)
for patch,expected in [({},'not_sent'),({'sent':True},'unknown'),({'sent':True,'response_accepted':True},'accepted'),({'sent':True,'response_accepted':True,'observed_running':True},'running'),({'sent':True,'response_accepted':True,'observed_running':True,'observed_finished':True},'unknown'),({'sent':True,'response_accepted':True,'observed_running':True,'observed_finished':True,'cleanup_confirmed':True},'finished')]:
 r=dict(base,**patch);assert m.classify(r)==expected,(r,m.classify(r),expected)
 assert m.can_retry_motion(r)==(not r['sent'])
for key in base:
 for value in [0,1,None,'false']:
  r=dict(base);r[key]=value
  for fn in [m.classify,m.can_retry_motion]:
   try:fn(r)
   except ValueError:pass
   else:raise AssertionError(('non-bool accepted',key,value,fn.__name__))
print('independent ledger oracle passed')
""",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=sorted(CHECKS))
    parser.add_argument('workspace', type=Path)
    args = parser.parse_args()
    result = subprocess.run([sys.executable, '-c', CHECKS[args.case]],
                            cwd=args.workspace.resolve(), timeout=20)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
