import jpglib

size, buf, _, _ = jpglib.decompress_jpg('sd/static/images/muschrooms/Suillus/Suillus1.jpg')

buf = jpglib.resize_img(buf, 100, 100, 240, 240)

print(len(buf))

f = open('obraz', 'wb')

f.write(buf)

f.close()
