# -*- coding: utf-8 -*-
'''
Create on '2019/4/23 0023 9:43'
@author yys

'''
#本脚本做以下几件事：
#1.得到jpg的名称，然后找bmp
#2.对bmp图做二值化，外接矩形-680*300宽高
#3.对xml的位置及逆行变换
#4.对以上图做flip操作。
#处理：
    # 1_scratch_127pcs
    # 2_incomplete1_310pcs
    # 3_stains_222pcs
    # 4_unknown

import glob
import cv2
import sys
import numpy as np
import xml.etree.ElementTree as ET

#划痕的文件夹进行操作
handle="3_stains"
path1=r"C:\Users\Administrator\Desktop\apple_cut\*.jpg"
jpg_folder_path=glob.glob(path1)
print(len(jpg_folder_path))
print(jpg_folder_path[0])
#D:\class7_CurrentlyWorking\20190423\augment\20190422\jpg\1_scratch\143114.776.jpg
#D:\class7_CurrentlyWorking
# \20190423\augment\Magnet_Images\1_scratch_127pcs

#jpg folder
raw_folder="3_stains"

#bmp folder
replace_folder="3_stains_222pcs"


for i in range(len(jpg_folder_path)):

    pic_name=jpg_folder_path[i].split("\\")[-1]

    bmp_path=jpg_folder_path[i]
    print('bmp_path1',pic_name)

    #bmp_path=jpg_folder_path[i].replace("20190422","Magnet_Images").replace("jpg","",1).replace(raw_folder,replace_folder).replace("jpg","bmp")

    #read rgb
    # 改成自己的jpg 格式文件
    bmp_img=cv2.imread(bmp_path,1)
    # print(bmp_img)
    #change to gray
    gray_bmp=cv2.cvtColor(bmp_img,cv2.COLOR_RGB2GRAY)

    #threshold processing
    ret, thresh = cv2.threshold(gray_bmp, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # cv2.imshow("thresh",thresh)
    # cv2.waitKey(0)

    # noise removal
    kernel = np.ones((2, 2), np.uint8)  #(1, 1)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # cv2.imshow("opening", opening)
    # cv2.waitKey(0)

    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    #
    # cv2.imshow("sure_bg", sure_bg)
    # cv2.waitKey(0)

    #find contours
    contours_1, hierarchy_1 = cv2.findContours(sure_bg, cv2.RETR_TREE,
                                                       cv2.CHAIN_APPROX_SIMPLE)
    con_num=0
    con_list=[]

    for K in range(len(contours_1)):
        #找外接矩形
        apple_x, apple_y, apple_w, apple_h = cv2.boundingRect(contours_1[K])
        print(apple_x, apple_y, apple_w, apple_h)
        if (300<apple_w < 700 and 100<apple_h < 400) or (100<apple_w < 400 and 300<apple_h < 700):
            con_num+=1
            con_list.append((apple_x, apple_y, apple_w, apple_h))


            print(con_list)#[(354, 489, 628, 283)]
    if con_num==1:
        #将bmp格式的图片进行切图后保存成jpg格式。
        x0,y0,w0, h0=con_list[0]
        print(con_list[0])
        if w0<=680 and h0<=300:
            x1= x0-int(340-w0/2)
            y1 = y0 - int(150 - h0 / 2)
            crop_bmp = bmp_img[y1:y1+300,x1:x1+680]
            # print("debug,crop_bmp.shape",crop_bmp.shape)#(300, 680, 3)

            #save jpg
            print(bmp_path)#D:\class7_CurrentlyWorking\20190423\augment\Magnet_Images\\1_scratch_127pcs\143114.776.bmp
            saveJpgPath=bmp_path.replace("Magnet_Images","save").replace("bmp","jpg")
            print("saveJpgPath",saveJpgPath)
            cv2.imwrite(saveJpgPath, crop_bmp, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            # cv2.imshow("crop_bmp",crop_bmp)
            # cv2.waitKey(0)

            #suit xml
            # 更改xml
            print("xml")#D:\class7_CurrentlyWorking\20190423\augment\20190422\jpg\1_scratch\143114.776.jpg
            print(jpg_folder_path[i])
            read_xml_path=jpg_folder_path[i].rstrip("jpg")+"xml"
            print( read_xml_path)
            updateTree = ET.parse(read_xml_path)
            root = updateTree.getroot()

            #modify folder contend
            root.find("folder").text=r"/home/ts006/objdetect/TF_OD/tf_od_mag/data_set/train_set/"
            root.find("filename").text=str(pic_name)
            root.find("size/height").text= str(crop_bmp.shape[0])
            root.find("size/width").text = str(crop_bmp.shape[1])
            root.find("size/depth").text = str(crop_bmp.shape[2])

            eles_Paramter = root.findall("object")  # 获得所有树节点
            print(len(eles_Paramter))

            for node in eles_Paramter:
                xmin = node.find("bndbox/xmin")
                xmin.text = str(int(xmin.text) - x1)

                xmax = node.find("bndbox/xmax")
                xmax.text = str(int(xmax.text) - x1)

                ymin = node.find("bndbox/ymin")
                ymin.text = str(int(ymin.text) - y1)

                ymax = node.find("bndbox/ymax")
                ymax.text = str(int(ymax.text) - y1)

            save_xml_path=saveJpgPath.rstrip("jpg")+"xml"
            updateTree.write(save_xml_path)

            #查看保存的xml的标注框在裁剪的jpg图中的情况
            # from new xml path get bndbox
            rectangle_img = crop_bmp.copy()
            detectTree = ET.parse(save_xml_path)
            root2 = detectTree.getroot()

            eles_Paramter2 = root2.findall("object")  # 获得所有树节点
            for node2 in eles_Paramter2:
                xmin_text = int(node2.find("bndbox/xmin").text)
                ymin_text = int(node2.find("bndbox/ymin").text)

                xmax_text = int(node2.find("bndbox/xmax").text)
                ymax_text = int(node2.find("bndbox/ymax").text)

                cv2.rectangle(rectangle_img, (xmin_text, ymin_text), (xmax_text, ymax_text), (0, 0, 255), 2)

            # cv2.imshow("rectangle_img", rectangle_img)
            # cv2.waitKey(0)

        else:
            print("裁剪的大小不符合w680_h300")
            # 记下对应的图片
            with open("readme_20190423.txt", 'a') as f:
                f.write("\n以下路径的图片裁剪的大小不符合w680_h300!\n")
                f.write("%s\n\n" % bmp_path)
    else:
        print("边界框数量%s"%(con_num))
        #记下对应的图片

        with open("readme_20190423.txt",'a') as f:
            f.write("\n以下路径的图片边界框数量有问题\n")
            f.write("%s\n\n"%bmp_path)

    # sys.exit()











