import os, json, subprocess, tempfile
import numpy as np, soundfile as sf
from pathlib import Path
src=Path('/mnt/data/seatrus feat.愛原圭織 -終末を詠う少女.mp3')
outdir=Path('/mnt/data')
audio,sr=sf.read(src,dtype='float32',always_2d=True)
duration=len(audio)/sr
print('Audio:',duration,sr,audio.shape,flush=True)

variants={
 'A_structure_and_outro':dict(description='Keeps the electronic break, closing verse/chorus, and original ending, shortening two repeated passages.',segments=[[0,63.25],[76.5,80.75],[171.25,234.0],[253.5,duration]],crossfades=[0.12,0.65,0.22]),
 'B_one_splice_229':dict(description='Simple edit: intro/first verse, then later verse through the complete original ending.',segments=[[0,50.0],[174.75,duration]],crossfades=[0.45]),
 'C_repeated_vocal_214':dict(description='Single early cut where first and later vocal verse material strongly matches; preserves the full final chorus and outro.',segments=[[0,34.75],[174.0,duration]],crossfades=[0.28]),
}

def render(segments, fades):
 pieces=[audio[int(round(a*sr)):int(round(b*sr))].copy() for a,b in segments]
 result=pieces[0]
 junctions=[]
 for i,piece in enumerate(pieces[1:]):
  n=int(round(fades[i]*sr));L=len(result)
  if n>0:
   t=np.linspace(0,1,n,endpoint=True,dtype='float32')[:,None]
   fade=result[-n:]*(1-t) + piece[:n]*t
   result=np.concatenate([result[:-n],fade,piece[n:]],axis=0)
  else:result=np.concatenate([result,piece],axis=0)
  junctions.append(float((L-n)/sr))
 return result,junctions

def encode(name,pcm):
 wav=outdir/(name+'.wav')
 mp3=outdir/(name+'.mp3')
 sf.write(wav,pcm,sr,subtype='PCM_24')
 p=subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-qscale:a','0',str(mp3)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr)
 wav.unlink()
 return mp3
manifest={'source_name':src.name,'source_seconds':round(duration,3),'sample_rate_hz':sr,'method':'Original stereo source PCM + short linear-overlap crossfades; each edit ends with original mastered ending. These are automated structural prototypes, not human-auditioned finals.','variants':{}}
for name,spec in variants.items():
 pcm,junctions=render(spec['segments'],spec['crossfades'])
 target=encode(name,pcm)
 entry={**spec,'output':target.name,'duration_seconds':round(len(pcm)/sr,3),'junction_output_seconds':[round(t,3) for t in junctions]}
 manifest['variants'][name]=entry
 print(name,'duration',entry['duration_seconds'],'junctions',junctions,'output',target.name, 'mb',round(target.stat().st_size/1e6,2),flush=True)
# One montage: 5 sec before and 7 sec after each junction of the most complex edit
r,j=render(variants['A_structure_and_outro']['segments'],variants['A_structure_and_outro']['crossfades'])
clips=[]
for t in j:
 start=max(0,int((t-5.0)*sr));end=min(len(r),int((t+7.0)*sr))
 clips.append(r[start:end]);clips.append(np.zeros((int(0.75*sr),2),dtype='float32'))
montage=np.concatenate(clips,axis=0)
encode('A_junctions_quick_review',montage)
(outdir/'song_edit_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
