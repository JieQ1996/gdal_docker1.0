import exifread
from PIL.ExifTags import TAGS
from PIL import Image
import cv2

def get_exif_data(image):
    degree = 0
    time = ""
    try:
        img = Image.open(image)
        if hasattr(img, '_getexif'):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    #if (decoded == "XMLPacket"):
                    if (decoded == 700 or decoded == "XMLPacket"):
                        xxmp = value
                        imgAsString = str(xxmp)
                        xmp_start = imgAsString.find('<drone-dji:FlightYawDegree')
                        xmp_end = imgAsString.find('</drone-dji:FlightYawDegree')
                        if xmp_start != xmp_end:
                            xmpString = imgAsString[xmp_start + 27:xmp_end]
                            degree = float(xmpString)
                    if (decoded == "DateTime"):
                        time = value
    except IOError:
        print('IOERROR ')
    return degree, time

# ratate any angle
def rotate(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))  # 6
    return rotated

def transparent_back(img):
    img = img.convert('RGBA')
    L, H = img.size
    color_0 = (0, 0, 0, 255)
    for h in range(H):
        for l in range(L):
            dot = (l, h)
            color_1 = img.getpixel(dot)
            if color_1 == color_0 or l == 0 or h == 0:
                color_1 = color_1[:-1] + (0,)
                img.putpixel(dot, (0, 0, 0, 0))
    return img

#get GPS info
def  read(fname):
    gpsinfo = {}
    f = open(fname,'rb')
    contents = exifread.process_file(f)
    lon = contents.get('GPS GPSLongitude', '0').values
    lat = contents.get('GPS GPSLatitude', '0').values
    print(lon)
    print(lat)
    lon_last = eval(str(lon[-1]))
    new_lon = lon[0].num + lon[1].num / 60 + lon_last / 3600
    lat_last = eval(str(lat[-1]))
    new_lat = lat[0].num + lat[1].num / 60 + lat_last / 3600
    gpsinfo = [new_lon,new_lat]
    f.close()
    return gpsinfo

# image pixel and GPS info mapping
def get_info(lat, lon):
    lat_basi = 0.000347222222
    lon_basi = 0.00055555555556
    lefttoplat = str(lat + lat_basi)
    lefttoplon = str(lon - lon_basi)

    righttoplat = lefttoplat
    righttoplon = str(lon + lon_basi)

    rightdownlat = str(lat - lat_basi)
    rightdownlon = righttoplon
    info = "gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 " + lefttoplon + " " +  lefttoplat + " -gcp 4000 0 " + righttoplon + " " +  righttoplat +" -gcp 4000 3000 "  + rightdownlon + " " + rightdownlat

    return info


class ImageProcess2:
    def __init__(self,filepath,filename,config):
        self.image_name = filename.split('.')[0]
        self.image_path = filepath
        self.img = cv2.imread(filepath, 1)
        self.Img1 = Image.open(filepath)
        self.processed_image_path = config['processedimage']
        self.processed_slice_path = config['slice']



    def rotateimage(self):
        print("start rotate")
        yawdegree, timedata = get_exif_data(self.image_path)
        print(yawdegree)
        imagero = rotate(self.img, -yawdegree)
        #Add watermark to image
        text = timedata
        pos = (1200, 1500)
        font_type = 3
        font_size = 5
        color = (255, 255, 255)
        bold = 1

        # image,add text,position.text type,text size,color,text height
        cv2.putText(imagero, text, pos, font_type, font_size, color, bold)

        imgro = Image.fromarray(imagero)
        imgtran = transparent_back(imgro)
        process_img_path = self.processed_image_path + "/" + self.image_name + ".png"
        imgtran.save(process_img_path)

        return text,process_img_path

    def cmdtxt(self):
        #print("start write cmd")
        gpsinfo = read(self.image_path)
        strrr = get_info(gpsinfo[1], gpsinfo[0])

        processedImagePath = (self.processed_image_path + "/" + self.image_name)
        writeSlicePath = (self.processed_slice_path + "/" + self.image_name)

        cmd = strrr + " " + processedImagePath + ".png " + writeSlicePath + ".vrt"
        cmd1 = "gdalwarp -of VRT -t_srs EPSG:4326 " + writeSlicePath + ".vrt " + writeSlicePath + "w.vrt"
        cmd2 = "gdal2tiles.py --xyz --zoom=12-22 " + writeSlicePath + "w.vrt " + writeSlicePath

        vrt1_path = writeSlicePath + ".vrt"
        vrt2_path = writeSlicePath + "w.vrt"
        slice_path = writeSlicePath
        return cmd,cmd1,cmd2,vrt1_path,vrt2_path,slice_path







