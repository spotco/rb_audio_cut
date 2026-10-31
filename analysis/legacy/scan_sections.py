import numpy as np
from scipy import ndimage
D=np.load('/mnt/data/song_features.npz')
C,M,times,rms,onset,beats=[D[x] for x in ['C','M','times','rms','onset','beats']]
# change points via before/after window avg features
for wins in [2,4,8]:
 n=int(wins/0.25)
 features=np.vstack([C*.7,M*.3]); feat=ndimage.gaussian_filter1d(features,1,axis=1)
 arr=[]
 for i in range(n,len(times)-n):
  v1=np.mean(feat[:,i-n:i],axis=1);v2=np.mean(feat[:,i:i+n],axis=1)
  d=np.linalg.norm(v1-v2)
  arr.append(d)
 p= np.array(arr)
 from scipy.signal import find_peaks
 peaks,_=find_peaks(p,distance=5/.25,prominence=.02)
 top=sorted([(round(float(p[j]),3),round(float(times[j+n]),1)) for j in peaks], reverse=True)[:28]
 print('change',wins,top)
print('rms 5s',[(i,round(np.mean(rms[int(i*11025/512):int((i+5)*11025/512)]),2)) for i in range(0,270,5)])
# tempos
print('beats @ important:')
for t in [50,53,85,88,100,103,111,139,140,157,173,175,190,193,223,225,230,240,250,260,268,271]:
 i=np.argmin(np.abs(beats-t));print(t,'=>',round(float(beats[i]),2),end='; ')
print()
