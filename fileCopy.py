import os
import shutil
import cv2



def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print
        "---  new folder...  ---"
        print
        "---  OK  ---"

    else:
        print
        "---  There is this folder!  ---"

class fileCopy:
    def __init__(self,sourcepath,despath):
        self.sourcepath = sourcepath
        self.despath = despath

    def copyandmerey(self):
        dirname = self.despath
        secfile = self.sourcepath
        if (os.path.isdir(secfile)):
            secfileName = os.listdir(secfile)
            for file2 in secfileName:
                thrfile = (secfile + "/" + file2)
                if (os.path.isdir(thrfile)):
                    # print(file2)
                    thrfileName = os.listdir(thrfile)
                    mkdirpath = (dirname + "/" + file2)
                    mkdir(mkdirpath)
                    for file3 in thrfileName:
                        forfile = (thrfile + "/" + file3)
                        if (os.path.isdir(forfile)):
                            mkdirpath1 = (mkdirpath + "/" + file3)
                            mkdir(mkdirpath1)
                            # print(file3)
                            forfileName = os.listdir(forfile)
                            for imagefile in forfileName:
                                sourimageName = (forfile + "/" + imagefile)
                                imageName = (mkdirpath1 + "/" + imagefile)
                                if (not os.path.exists(imageName)):

                                    #print(sourimageName)
                                    #print(imageName)
                                    #print(os.path.exists(imageName))
                                    shutil.copy(sourimageName, mkdirpath1)
                                else:
                                    img1 = cv2.imread(imageName, cv2.IMREAD_UNCHANGED)
                                    img2 = cv2.imread(sourimageName, cv2.IMREAD_UNCHANGED)
                                    if (int(file2) < 17):
                                        img_merge = cv2.addWeighted(img1, 1, img2, 0.8, 0)
                                        cv2.imwrite(imageName, img_merge)
                                    elif (int(file2) >= 17 and int(file2) < 19):
                                        img_merge = cv2.addWeighted(img1, 1, img2, 0.75, 0)
                                        cv2.imwrite(imageName, img_merge)
                                    else:
                                        count1 = 0
                                        count2 = 0
                                        L = 255
                                        H = 255
                                        for h in range(H):
                                            for l in range(L):
                                                if (not img1[l, h][3]):
                                                    count1 += 1
                                                if (not img2[l, h][3]):
                                                    count2 += 1
                                        if (count1 > count2):
                                            shutil.copy(sourimageName, mkdirpath1)
