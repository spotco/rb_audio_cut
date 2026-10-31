import numpy as np
from scipy import ndimage
D=np.load('/mnt/data/song_features.npz');C,M,t=[D[s] for s in ['C','M','times']]
feats=np.vstack([C*.75,M*.5]);feat=ndimage.gaussian_filter1d(feats,1,axis=1)
# assess sustained best matches for jump time from x to y : x[k-N..k] similar to y[k-N..k], and continue? For loop repeats, align before+after sample at point across song separated by delta. 

def score(a,b,w=2):
 i=int(a*4);j=int(b*4);n=int(w*4)
 if i<n or j<n:return 9
 # match chroma/spectral at the cut boundary, compare windows of spectrogram around both
 ca=C[:,i-n:i+n];cb=C[:,j-n:j+n]
 ma=M[:,i-n:i+n];mb=M[:,j-n:j+n]
 if ca.shape!=cb.shape:return 9
 cdist=np.mean(np.sum((ca-cb)**2,axis=0))
 mdist=np.mean(np.sum((ma-mb)**2,axis=0))
 return .6*cdist+.4*mdist
for src,dst in [((80,85),(170,176)),((223,239),(246,265)),((225,250),(250,267)),((52,55),(97,114)),((52,55),(170,176)),((135,143),(170,176)),((134,141),(189,196)),((81,85),(170,176)),((80,85),(91,100)),((28,35),(170,177))]:
 scores=[]
 for a in np.arange(src[0],src[1]+.01,.25):
  for b in np.arange(dst[0],dst[1]+.01,.25):
   scores.append((score(a,b),a,b))
 print(src,'->',dst,'top',[(round(float(sc),3),a,b) for sc,a,b in sorted(scores)[:8]])
# best 8bar repeat ending
for lag in [9.7,19.4,29.1,38.8]:
 vals=[]
 for a in np.arange(225,270-lag,.25):
  vals.append((score(a,a+lag,1),a,a+lag))
 print('lag',lag,'best',[(round(float(s),3),round(a,2),round(b,2)) for s,a,b in sorted(vals)[:6]])
