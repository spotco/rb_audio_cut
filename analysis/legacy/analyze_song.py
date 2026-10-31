import os,time
os.environ['NUMBA_NUM_THREADS']='4'
import numpy as np,librosa,soundfile as sf
from scipy import ndimage,signal
import matplotlib.pyplot as plt
f='/mnt/data/seatrus feat.愛原圭織 -終末を詠う少女.mp3'
t0=time.time()
y,sr=librosa.load(f, sr=11025, mono=True)
print('loaded',len(y)/sr,'in',time.time()-t0, flush=True)
hop=512
rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=hop)[0]
onset=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
print('onset',time.time()-t0,flush=True)
# chroma stft with smoothing
chroma=librosa.feature.chroma_stft(y=y,sr=sr,hop_length=hop,n_fft=4096,tuning=None)
print('chroma',chroma.shape,time.time()-t0,flush=True)
# MFCC spectral key
mfcc=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=14,hop_length=hop,n_fft=2048)
print('mfcc',time.time()-t0, flush=True)
# beat
_,beats=librosa.beat.beat_track(onset_envelope=onset,sr=sr,hop_length=hop,trim=False,units='time')
print('beats',np.round(beats[:25],2),len(beats),'median',np.median(np.diff(beats)),time.time()-t0,flush=True)
# aggregate on fixed-time 0.25s windows
sec=0.25
times=np.arange(0,len(y)/sr,sec)
idx=np.minimum((times*sr/hop).astype(int),chroma.shape[1]-1)
C=ndimage.gaussian_filter1d(chroma,3,axis=1)[:,idx]
M=ndimage.gaussian_filter1d(mfcc,3,axis=1)[:,idx]
C = C / (np.linalg.norm(C,axis=0,keepdims=True)+1e-8)
# normalize MFCC across time
M = (M - np.mean(M,axis=1,keepdims=True)) / (np.std(M,axis=1,keepdims=True)+1e-5)
M = M / (np.linalg.norm(M,axis=0,keepdims=True)+1e-8)
# novelty curve using compare before/after features at offsets
sim=C.T@C
sim2=M.T@M
simfeat=0.5*sim+0.5*sim2
np.fill_diagonal(sim,0)
fig,ax=plt.subplots(3,1,figsize=(17,13), gridspec_kw={'height_ratios':[1,2.5,1]})
ax[0].plot(np.arange(len(rms))*hop/sr,rms,linewidth=.8)
ax[0].set_ylabel('RMS'); ax[0].set_xlim(0,len(y)/sr)
ax[1].imshow(sim,origin='lower',extent=[0,times[-1],0,times[-1]],aspect='auto',cmap='magma',vmin=0.4,vmax=1)
ax[1].set_ylabel('Song time (s)');ax[1].set_xlabel('Song time (s)');ax[1].set_title('Harmonic similarity')
ax[2].plot(np.arange(len(onset))*hop/sr,onset,linewidth=.8)
ax[2].set_ylabel('Onset'); ax[2].set_xlim(0,len(y)/sr)
plt.savefig('/mnt/data/song_map.png',dpi=130,bbox_inches='tight')
np.savez_compressed('/mnt/data/song_features.npz', C=C,M=M,times=times,rms=rms,onset=onset,beats=beats,similarity=simfeat,sr=sr,hop=hop)
print('done',time.time()-t0)
