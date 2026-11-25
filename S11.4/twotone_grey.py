"""Makes the grey two-tone backpack (S11.4) from the all-yellow backpack photo used through S11.3: the front pocket panel
stays fluorescent yellow and every other yellow part is recolored grey. The boundary follows the pocket's own seam: the
seam is traced from hand-placed points, snapped to the darkest line nearby, and smoothed.
Usage: python3 twotone_grey2.py <yellow photo> <output photo>"""
import cv2,numpy as np,sys
from scipy.ndimage import gaussian_filter1d, median_filter
a=cv2.imread(sys.argv[1]); H,W=a.shape[:2]
hsv=cv2.cvtColor(a,cv2.COLOR_BGR2HSV).astype(np.float32); h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
yel=(h>=20)&(h<=50)&(s>45)&(v>40)
mesh=np.zeros((H,W),bool); mesh[630:955,480:672]=True
yel=yel|(mesh&(h>=5)&(h<=55)&(s>35)&(v>28))
dark=(v<75)|((s<60)&(v<140))
barrier=cv2.dilate(dark.astype(np.uint8),np.ones((3,3),np.uint8))
ctrl=np.array([(416,672),(416,700),(418,740),(420,780),(421,820),(422,860),(422,895),(421,912),(417,926),(408,935),(395,939),(370,940),
 (300,936),(250,932),(200,928),(150,922),(100,915),(80,904),(66,892),(57,880),(51,866),(49,850),(48,820),(48,780),(47,745),(46,718),(41,700)],np.float32)
# dense polyline
seg=np.linalg.norm(np.diff(ctrl,axis=0),axis=1); t=np.concatenate([[0],np.cumsum(seg)]); tt=np.arange(0,t[-1],1.0)
px=np.interp(tt,t,ctrl[:,0]); py=np.interp(tt,t,ctrl[:,1])
px=gaussian_filter1d(px,6,mode='nearest'); py=gaussian_filter1d(py,6,mode='nearest')
dx=np.gradient(px); dy=np.gradient(py); n=np.hypot(dx,dy); nx,ny=-dy/n,dx/n
vb=cv2.GaussianBlur(v,(0,0),1.0)
offs=np.arange(-5,6); best=np.zeros(len(tt))
for i in range(len(tt)):
    xs=np.clip(px[i]+offs*nx[i],0,W-1); ys=np.clip(py[i]+offs*ny[i],0,H-1)
    vals=vb[ys.round().astype(int),xs.round().astype(int)]+0.6*np.abs(offs)     # prefer the nearest dark line
    best[i]=offs[int(np.argmin(vals))]
best[:22]=0; best[-25:]=0                         # do not snap next to the zipper end or where the seam meets the outline
best=gaussian_filter1d(median_filter(best,21,mode='nearest'),8,mode='nearest')
sx=px+best*nx; sy=py+best*ny
seam=np.stack([sx,sy],1).round().astype(np.int32)
cv2.polylines(barrier,[seam],False,1,3)
free=((yel)&(barrier==0)).astype(np.uint8); mask=np.zeros((H+2,W+2),np.uint8)
cv2.floodFill(free,mask,(250,520),2)
keep=(free==2).astype(np.uint8)
keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
keep=cv2.dilate(keep,np.ones((3,3),np.uint8))
# never keep anything beyond the seam: cut the closed region with a half-plane mask built from the seam
keepf=cv2.GaussianBlur(keep.astype(np.float32),(0,0),0.9)
# soft yellowness, so faint yellow fringes next to black trim are recolored too
yf=np.clip((s-30)/40,0,1)*np.clip(1-np.abs(h-35)/22,0,1)*np.clip((v-30)/30,0,1)
yf=np.maximum(yf,yel.astype(np.float32)); yf=cv2.GaussianBlur(yf,(0,0),0.6)
g=yf*(1-keepf)
vn=np.clip(74*np.power(np.clip(v/221.0,0,1.3),1.3),0,255)
out2=np.dstack([np.full_like(h,110),np.clip(s/219.0*14,0,255),np.clip(vn*1.55,0,255)])
grey=cv2.cvtColor(out2.astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)
res=a.astype(np.float32)*(1-g[...,None])+grey*g[...,None]
cv2.imwrite(sys.argv[2],np.clip(res,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,95])
np.save('/tmp/seam.npy',seam); print('kept',int(keep.sum()),'snap range',best.min().round(1),best.max().round(1))
