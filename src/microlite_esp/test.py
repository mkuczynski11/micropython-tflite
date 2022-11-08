import jpglib

buf, _, _ = jpglib.decompress_jpg('ja.jpg')

buf = jpglib.resize_img(buf, 96, 96, 240, 240)
f = open('resized.jpg', 'wb')
f.write(buf)
f.close()