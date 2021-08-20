import os
import yaml
import requests
import json
import oss2
import time
from ImageProcess2 import ImageProcess2
from fileCopy import fileCopy
import shutil


def get_token(config):
    loginUrl = config['loginUrl']
    usermsgs = {'username': config['username'],
                 'password': config['password']}
    loginheaders ={}

    try:
        loginmsgs = requests.request("POST",loginUrl,headers=loginheaders,data = usermsgs)
    except requests.exceptions.ConnectionError:
        print('ConnectionError -- please wait 3 seconds')
        time.sleep(3)
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError -- please wait 3 seconds')
        time.sleep(3)
    except:
        print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        time.sleep(3)

    #loginmsgs = requests.request("POST",loginUrl,headers=loginheaders,data = usermsgs)
    token = json.loads(loginmsgs.text).get('data').get('token')
    headers = {
        'token': token
    }
    return headers

def get_image(pagesize,pagenum):
    downloadUrl = config['dowloadUrl'] + "?pageSize=" + str(pagesize) + "&pageNum=" + str(pagenum)
    payload = {}
    try:
        downloadMsgs = requests.request("GET", downloadUrl, headers=headers, data=payload)
    except requests.exceptions.ConnectionError:
        print('ConnectionError -- please wait 3 seconds')
        time.sleep(3)
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError -- please wait 3 seconds')
        time.sleep(3)
    except:
        print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
        time.sleep(3)
    itemdata = json.loads(downloadMsgs.text)
    totaliteam = int(itemdata.get('data').get('totalItems'))
    return itemdata,totaliteam

def oss2_getobject(id,imagename,name,bucketName,config):
    key_id = config['key_id']
    key_secret = config['key_secret']
    end_point = config['end_point']
    localfile = config['localfile']

    print("start download : " + imagename)
    time_start = time.time()
    auth = oss2.Auth(key_id, key_secret)
    bucket = oss2.Bucket(auth, end_point, bucketName)
    try:
        result = bucket.get_object_to_file(imagename, localfile + name + '.jpg')
        print(result.status)
    except oss2.exceptions.ServerError as e:
        print('status={0}, request_id={1}'.format(e.status, e.request_id))
        print("server error")
    except oss2.exceptions.ClientError as e:
        print('status={0}, request_id={1}'.format(e.status, e.request_id))
        print("client error")
    except oss2.exceptions.RequestError as e:
        print('status={0}, request_id={1}'.format(e.status, e.request_id))
        print("request error")
    #bucket.get_object_to_file(imagename,localfile+name+'.jpg')
    time_end = time.time()
    print('download image time cost', time_end - time_start, 's')
    print("image download success")

    imagefile = localfile+name+'.jpg'
    return id,imagefile


def oss2_putobject(data,bucketName,config):
    #data  20210604
    key_id = config['key_id']
    key_secret = config['key_secret']
    end_point = config['end_point']
    localfile = config['localmereyfile']

    objectfile = config['objectfile']

    print("start upload.....")
    print(data)
    time_start = time.time()
    auth = oss2.Auth(key_id, key_secret)
    bucket = oss2.Bucket(auth, end_point, bucketName)

    if (os.path.isdir(localfile)):
        firfileName = os.listdir(localfile)
        for firfile in firfileName:
            localsecfile = localfile + '/' + firfile
            if (os.path.isdir(localsecfile)):
                secfileName = os.listdir(localsecfile)
                for secfile in secfileName:
                    localthifile = localsecfile + '/' + secfile
                    if (os.path.isdir(localthifile)):
                        imagefileName = os.listdir(localthifile)
                        for image in imagefileName:
                            objectimagepath = objectfile + data +'/'+ firfile + '/' + secfile + '/' + image
                            localimagepath = localthifile + '/' + image
                            try:
                                result = bucket.put_object_from_file(objectimagepath, localimagepath)
                                #print(result.status)
                            except oss2.exceptions.ServerError as e:
                                print('status={0}, request_id={1}'.format(e.status, e.request_id))
                                print("server error")
                            except oss2.exceptions.ClientError as e:
                                print('status={0}, request_id={1}'.format(e.status, e.request_id))
                                print("client error")
                            except oss2.exceptions.RequestError as e:
                                print('status={0}, request_id={1}'.format(e.status, e.request_id))
                                print("request error")

    time_end = time.time()
    print('upload merey dir time cost', time_end - time_start, 's')
    print("image upload success")


def completed(id,headers,config):
    completedUrl = config['completedUrl']
    complesedMsgs = {'id':id}
    print(id+" is completed")
    requests.request("POST",completedUrl,headers=headers,data = complesedMsgs)
    print("upload success")

def processingImage(Imagepath,Imagename,config):
    pro_img = ImageProcess2(Imagepath,Imagename,config)
    date,process_img_path = pro_img.rotateimage()
    translate_cmd,warp_cmd,gdal2tiles_cmd,vrt1_path,vrt2_path,slice_path = pro_img.cmdtxt()
    return date,process_img_path,translate_cmd,warp_cmd,gdal2tiles_cmd,vrt1_path,vrt2_path,slice_path

def gdalProcess(translate_cmd,warp_cmd,gdal2tiles_cmd):
    os.system(translate_cmd)
    os.system(warp_cmd)
    os.system(gdal2tiles_cmd)

def sliceFileprocess(source,des):
    pro_file = fileCopy(source,des)
    pro_file.copyandmerey()

def rmTmpDir(image,process_image,vrt1,vrt2,slice_file):
    os.remove(image)
    os.remove(process_image)
    os.remove(vrt1)
    os.remove(vrt2)
    shutil.rmtree(slice_file)


if __name__ == "__main__":
    ymlfile = open("./config.yaml", 'r', encoding='utf-8')
    config = yaml.load(ymlfile, Loader=yaml.SafeLoader)

    while True:
        processed_image_flag = False
        headers = get_token(config)
        datetime = " "
        pagesize = 100
        pagenum = 1
        itemdata_tmp,totaliteam_tmp = get_image(pagesize,pagenum)
        print("The number of images currently pending: ")
        print(totaliteam_tmp)
        if(totaliteam_tmp):
            while True:
                itemdata, totaliteam = get_image(pagesize, pagenum)
                if(totaliteam):
                    for item in itemdata['data']['items']:
                        id = item['id']
                        bucketName = item['bucketName']
                        name = item['name']
                        objectlocal = item['objectName']
                        imagename = objectlocal + name + ".jpg"

                        # download image
                        complete_id, imagefile = oss2_getobject(id, imagename, name, bucketName, config)

                        # get image information; processs(ration);get gdal command and local file path
                        datetime, process_img_path, translate_cmd, warp_cmd, gdal2tiles_cmd, vrt1_path, vrt2_path, slice_path = processingImage(
                            imagefile, name, config)

                        gdalProcess(translate_cmd, warp_cmd, gdal2tiles_cmd)

                        # merey slice image
                        sliceFileprocess(slice_path, config['localmereyfile'])

                        # remove processed local file
                        rmTmpDir(imagefile, process_img_path, vrt1_path, vrt2_path, slice_path)

                        completed(complete_id, headers, config)
                    else:
                        processed_image_flag = True
                        break
        if(processed_image_flag):
            datetimefile = datetime[:4] + datetime[5:7] + datetime[8:10]
            oss2_putobject(datetimefile, bucketName, config)
            shutil.rmtree(config['localmereyfile'])
            os.mkdir(config['localmereyfile'])
            processed_image_flag = False
        print("sleeping....")
        print(time.time())
#        with open("/data/log.txt","a") as f:
#            f.write(str(time.time()))
#            f.write("  server open！")
#            f.write("\r\n")
            
        time.sleep(3600)



