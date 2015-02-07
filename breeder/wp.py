from PIL import Image

a = Image.open('000001.png').convert('L').load()
mat=[];wid=379;hei=192
for l in xrange(wid): mat.append([False]*hei)
for y in xrange(hei):
 for x in xrange(wid):
  mat[x][y] = a[x, y] < 40
def num(x,y):
 options=[]
 options.append(mat[(x+1)%wid][(y  )%hei])
 options.append(mat[(x+1)%wid][(y+1)%hei])
 options.append(mat[(x  )%wid][(y+1)%hei])
 options.append(mat[(x-1)%wid][(y+1)%hei])
 options.append(mat[(x-1)%wid][(y  )%hei])
 options.append(mat[(x-1)%wid][(y-1)%hei])
 options.append(mat[(x  )%wid][(y-1)%hei])
 options.append(mat[(x+1)%wid][(y-1)%hei])
 return options.count(True)
def newgen():
 newmat=[]
 for l in range(wid): newmat.append([False]*hei)
 for y in range(hei):
  for x in range(wid):
   numnum=num(x,y)
   if not mat[x][y] and numnum==3: newmat[x][y]=True
   elif mat[x][y] and (numnum==2 or numnum==3): newmat[x][y]=True
 return newmat
 
for l in xrange(2, 499):
 b = Image.new('L', (wid, hei), 255)
 mat=newgen()
 for y in xrange(hei):
  for x in xrange(wid):
   if mat[x][y]:
    b.putpixel((x, y), 0)
 b.save(str(l).zfill(6)+'.png')
 print chr(8)*30+str(l).zfill(6)+'.png finished.',
