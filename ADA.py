#! /usr/bin/env python
import os
import sys
import csv
import cv
import cv2
import glob
import numpy as np
from matplotlib import pyplot as plt


if __name__ == "__main__":
    
    cv2.namedWindow('Lane Markers')
    imgs = glob.glob("images/*.png")  #Path to list of images

    intercepts = []
    x = 0
    for fname in imgs:
        # Load image and prepare output image
        img = cv2.imread(fname)
        x = x+1
        (height, width) = img.shape[:2]
        
        #Image Preparation
        tri_image = img[height/2:height,:,:]
        orig_image = img[height/2:height,:,:]
        mono_image = img[height/2:height,:,1]
        #black_image = np.zeros((height/2,2*width),np.uint8)
        mono_image_left = mono_image[:,0:width/2]
        mono_image_right = mono_image[:,width/2:width]
        half_image = mono_image
        
        # Preprocessing - left half
        kernel_open = np.ones((2,2),np.uint8)
        mono_image_left = cv2.GaussianBlur(mono_image_left,(3,3),0)
        mono_image_left = cv2.Canny(mono_image_left,30,50,3)
        
        # Preprocessing - Right half
        mono_image_right = cv2.GaussianBlur(mono_image_right,(3,3),0)
        mono_image_right = cv2.adaptiveThreshold(mono_image_right,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
        #mono_image_right = cv2.morphologyEx(mono_image_right, cv2.MORPH_OPEN, kernel_open)
        mono_image_right = cv2.Canny(mono_image_right,30,50,3)
        
        #Left Half
        lines = cv2.HoughLines(mono_image_left,1,np.pi/180,190)

        if lines == None :
            print('Lines is none for left')
            continue

        #Variable declaration
        i = 0
        j = 0
        m = 0
        n = 0
        total_x1 = 0
        total_x2 = 0
        total_y1 = 0
        total_y2 = 0
        x1_left = 0
        y1_left = 0
        x2_left = 0
        y2_left = 0

        for rho,theta in lines[0]:
            
            a = np.cos(theta)                                                       #Finding points on line segment
            b = np.sin(theta)
            slope = -a/b

            intercept = (lines[0][i][1])
            i = i+1
            if abs(slope) < 0.1 or intercept > 1 or intercept < 0.79:               #Threhold for slope and intercepts
                j = j+1
                continue
            
            
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            
            total_x1 = total_x1+x1                                                   #Combining multiple lines to give out single line
            total_x2 = total_x2+x2
            total_y1 = total_y1+y1
            total_y2 = total_y2+y2
            
        if i == j:                                                               #If no lines are found within the first threshold, expand search
            m = 0
            n = 0
            for rho,theta in lines[0]:
        
                a = np.cos(theta)
                b = np.sin(theta)
                slope = -a/b
                intercept = (lines[0][m][1])
                m = m+1
                if (abs(slope) < 0.05 or intercept > 1.3 or intercept < 0.45):
                    n = n+1
                    continue
            
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
            
                total_x1 = total_x1+x1
                total_x2 = total_x2+x2
                total_y1 = total_y1+y1
                total_y2 = total_y2+y2
            
            if m == n:
                left_x = 'none'
            else:
                x1_left = total_x1/(m-n)
                x2_left = total_x2/(m-n)
                y1_left = total_y1/(m-n)
                y2_left = total_y2/(m-n)
                cv2.line(orig_image,(x1_left,y1_left),(x2_left,y2_left),(0,0,255),2)

        else:
            x1_left = total_x1/(i-j)
            x2_left = total_x2/(i-j)
            y1_left = total_y1/(i-j)
            y2_left = total_y2/(i-j)
    
            cv2.line(orig_image,(x1_left,y1_left),(x2_left,y2_left),(0,255,255),2)


        x2_left = 800-x2_left
        x1_left = 800-x1_left
        
        


        if (((x2_left - x1_left) != 0) and ((y2_left - y1_left) !=0)):
            Final_Slope_Left= float(y2_left - y1_left)/(x2_left - x1_left)
            Y_Intercept = y2_left - (Final_Slope_Left*x2_left)
            left_x = -(Y_Intercept/Final_Slope_Left)
        else:
            left_x = 'none'


        #Right Half
        lines = cv2.HoughLines(mono_image_right,1,np.pi/180,190)                                    #Similar techniques as before
        if lines == None:
            print('Lines is none for right')
            continue

        k = 0
        l = 0
        total_x1_right = 0
        total_x2_right = 0
        total_y1_right = 0
        total_y2_right = 0
        x1_right = 0
        y1_right = 0
        x2_right = 0
        y2_right = 0
        for rho,theta in lines[0]:

            a = np.cos(theta)
            b = np.sin(theta)
            slope = -a/b
            intercept = (lines[0][k][1])
            k = k+1
            if abs(slope) < 0.1 or intercept < 2.15 or intercept > 2.3:
                l = l+1
                continue

            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            total_x1_right = total_x1_right+x1
            total_x2_right = total_x2_right+x2
            total_y1_right = total_y1_right+y1
            total_y2_right = total_y2_right+y2

        if k == l:
                
            y = 0
            z = 0
            for rho,theta in lines[0]:
                
                a = np.cos(theta)
                b = np.sin(theta)
                slope = -a/b
                intercept = (lines[0][y][1])
                y = y+1
                if (abs(slope) < 0.1 or intercept > 2.4 or intercept < 1.9):
                    z = z+1
                    continue
                
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                
                total_x1_right = total_x1_right+x1
                total_x2_right = total_x2_right+x2
                total_y1_right = total_y1_right+y1
                total_y2_right = total_y2_right+y2
            
            if y == z:
                right_x = 'none'
            else:
                x1_right = total_x1_right/(y-z)
                x2_right = total_x2_right/(y-z)
                y1_right = total_y1_right/(y-z)
                y2_right = total_y2_right/(y-z)
                cv2.line(orig_image,(x1_right+width/2,y1_right),(x2_right+width/2,y2_right),(0,0,255),2)

        else:
            x1_right = total_x1_right/(k-l)
            x2_right = total_x2_right/(k-l)
            y1_right = total_y1_right/(k-l)
            y2_right = total_y2_right/(k-l)
            
            cv2.line(orig_image,(x1_right+width/2,y1_right),(x2_right+width/2,y2_right),(0,255,255),2)



        x2_right = 1600-x2_right
        x1_right = 1600-x1_right


        if (((x2_right - x1_right) != 0) and ((y2_right - y1_right) !=0)):
            Final_Slope_Right = -(float(y2_right - y1_right))/(x2_right - x1_right)
            Y_Intercept = y2_right - (Final_Slope_Right*x2_right)
            right_x = -(Y_Intercept/Final_Slope_Right) + width/2
        else :
            right_x = 'none'

        cv2.imshow('Lane Markers', orig_image)
        
        # Sample intercepts
        # intercepts.append((os.path.basename(fname), left_x, right_x))
        
        # Show image
        # cv2.imshow('Lane Markers', half_image)
        key = cv2.waitKey(50)
        if key == 27:
            sys.exit(0)




