"""Makes the two-tone backpack of S10.4.9 from the all-yellow backpack photo of S10.4.8: the front panel stays fluorescent
yellow and every other yellow part is recolored navy.  Usage: python3 twotone.py <yellow photo> <output photo>"""
import cv2,numpy as np,sys
a=cv2.imread(sys.argv[1])   # the all-yellow backpack photo of S10.4.8
H,W=a.shape[:2]
hsv=cv2.cvtColor(a,cv2.COLOR_BGR2HSV).astype(np.float32)
h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
yel=(h>=22)&(h<=48)&(s>55)&(v>45)
mesh=np.zeros((H,W),bool); mesh[630:955,480:672]=True
yel=yel|(mesh&(h>=5)&(h<=55)&(s>35)&(v>28))                 # every yellow-tinted pixel, incl. dark ones seen through the mesh
dark=(v<75)|((s<60)&(v<140))                         # black zippers, pulls, trim
barrier=cv2.dilate(dark.astype(np.uint8),np.ones((3,3),np.uint8))
# yellow-on-yellow seams of the front pocket: right edge below the zipper end, then the bottom piping
seam=np.array([(438, 655), (432, 672), (421, 690), (421, 800), (420, 900), (413, 926), (400, 937), (370, 940), (300, 937), (220, 932), (150, 924), (95, 911), (62, 892), (48, 868), (40, 850), (20, 845)],np.int32)
cv2.polylines(barrier,[seam],False,1,3)
free=((yel)&(barrier==0)).astype(np.uint8)
ff=free.copy(); mask=np.zeros((H+2,W+2),np.uint8)
cv2.floodFill(ff,mask,(250,520),2)
keep=(ff==2).astype(np.uint8)
keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))     # stitches, piping, the seam line itself
keep=cv2.dilate(keep,np.ones((3,3),np.uint8))
keepf=cv2.GaussianBlur(keep.astype(np.float32),(5,5),1.2)
navy=yel.astype(np.float32)*(1-keepf)
navy=cv2.GaussianBlur(navy,(3,3),0.7)
out=hsv.copy()
vn=np.clip(74*np.power(np.clip(v/221.0,0,1.3),1.3),0,255)
out2=np.dstack([np.full_like(h,114),np.clip(s/219.0*170,0,255),vn])
bgr_navy=cv2.cvtColor(out2.astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)
res=a.astype(np.float32)*(1-navy[...,None])+bgr_navy*navy[...,None]
cv2.imwrite(sys.argv[2],np.clip(res,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,93])
print('yellow kept px',int((yel&(keep>0)).sum()),'recolored px',int((navy>0.5).sum()))
