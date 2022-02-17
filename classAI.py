import cv2
import jetson.inference
import jetson.utils
import time
import threading
import os
from config import *
from utility import *
import random
import pandas as pd

import datetime


class AI(threading.Thread):
    def __init__(self, conf):
        threading.Thread.__init__(self)
        self.ROOT_DIR = ROOT_DIR
        self.net = jetson.inference.detectNet(model, model_th)
        self.video = video
        self.display = jetson.utils.videoOutput()
        self.config_ini = conf
        #camera = jetson.utils.videoSource(config_ini['CAMERA']['rtspurl'],argv=['--input-codec=h264','--input-rtsp-latency=0'])
        self.camera = jetson.utils.videoSource(self.video)
        #self.camera = jetson.utils.videoSource('rtsp://192.168.10.52:8080',argv=['--input-codec=h264','--input-rtsp-latency=0'])
        self.show_line = 0
        self.detect_line = 700
        self.dist_conf = 18 / 300  # 18 meters / 300 pixels

        self.obj_list = []
        self.frame_data = None
        self.font_size = 15.0
    
        self.is_running = True

        

        self.speed_text = 'Approx speeds :'
        pass # end of __init__ function
    
    def closeProject(self):
        self.is_running = False
        self.join()
        pass
    def run(self):
        
        #while True:
        while self.display.IsStreaming() and self.is_running:
            
            max_failed = 20
            try:
                img = self.camera.Capture()
                self.cur_failed = 0
            except:
                print("Disconnected....")
                self.cur_failed += 1
                if self.cur_failed > max_failed:
                    self.is_running = False

            if img is not None:
                try:
                    frame_data = [img, time.time()]
                    # frame_data.append([img, time.time()])
                except:
                    pass

            cuimg, dtime = frame_data.copy()
            # backup cuda-image
            cuimg_copy = jetson.utils.cudaAllocMapped(width=cuimg.width, height=cuimg.height, format=cuimg.format)

            # copy the image (dst, src)
            jetson.utils.cudaMemcpy(cuimg_copy, cuimg)

            detections = self.net.Detect(cuimg)
            is_show = False
            for detection in detections:
                self.show_line = cuimg.height-self.detect_line
                if (detection.Bottom > self.show_line):
            

                    crop_roi = (int(detection.Left), int(detection.Top), int(detection.Right), int(detection.Bottom))
                    _box = [int(detection.Left), int(detection.Top), int(detection.Right), int(detection.Bottom)]
                    imgOutput = jetson.utils.cudaAllocMapped(width=crop_roi[2] - crop_roi[0],
                                                                height=crop_roi[3] - crop_roi[1],
                                                                format=cuimg_copy.format)
                    jetson.utils.cudaCrop(cuimg_copy, imgOutput, crop_roi)
                            
                    font = jetson.utils.cudaFont(size=self.font_size)
                    font2 = jetson.utils.cudaFont(size=25)
                    cuimage = imgOutput
                    sp = int(random.randint(lowSpeed, hiSpeed))
                    font.OverlayText(cuimage, cuimage.width, cuimage.height, f"Camera ID : {self.config_ini['CAMERA']['cameraid']}", 5, 15, font.Yellow, font.Gray40)
                    font.OverlayText(cuimage, cuimage.width, cuimage.height, f"Date : {time.strftime('%m-%d-%Y')}", 5, 27, font.Yellow, font.Gray40)
                    font.OverlayText(cuimage, cuimage.width, cuimage.height, f"Time : {time.strftime('%H:%M:%S')}", 5, 40, font.Yellow, font.Gray40)
                    font.OverlayText(cuimage, cuimage.width, cuimage.height, f"Speed : {sp}", 5, 55, font.Yellow, font.Gray40)
                    font.OverlayText(cuimage, cuimage.width, cuimage.height, f"Site Name : {self.config_ini['CAMERA']['sitename']}", 5, 70, font.Yellow, font.Gray40)


                    if show_output:
                        font2.OverlayText(cuimg, cuimg.width, cuimg.height, f"Camera ID : {self.config_ini['CAMERA']['cameraid']}", int(_box[0]), int(_box[1]), font.Yellow, font.Gray40)
                        font2.OverlayText(cuimg, cuimg.width, cuimg.height, f"Date : {time.strftime('%m-%d-%Y')}", int(_box[0]),int(_box[1])+15, font.Yellow, font.Gray40)
                        font2.OverlayText(cuimg, cuimg.width, cuimg.height, f"Time : {time.strftime('%H:%M:%S')}", int(_box[0]),int(_box[1])+30, font.Yellow, font.Gray40)
                        font2.OverlayText(cuimg, cuimg.width, cuimg.height, f"Speed : {sp}", int(_box[0]),int(_box[1])+45, font.Yellow, font.Gray40)
                        font2.OverlayText(cuimg, cuimg.width, cuimg.height, f"Site Name : {self.config_ini['CAMERA']['sitename']}", int(_box[0]),int(_box[1])+60, font.Yellow, font.Gray40)
                    
                    t= str(int(time.time() * 100000))[5:]
                    name = f"{t}.png"
                    ref_name = f"{t}.csv"
                    todate = datetime.datetime.now().strftime('%Y_%m_%d')
                    try:
                        if sp >= EnforceSpeed :
                            jetson.utils.saveImage(os.path.join(overSpeedPath, name), cuimage)
                        
                            logger.info([str(datetime.datetime.now().strftime("%m_%d_%Y, %H:%M:%S")), sp, EnforceSpeed , VehicleDirection,
                            VehicleLan, GPSLati, GPSLongi, name, ref_name, '{}/OverSpeed'.foramt(todate) ])
                            
                        elif sp <= EnforceSpeed :
                            jetson.utils.saveImage(os.path.join(aggpath, name), cuimage)
                        
                            logger.info([str(datetime.datetime.now().strftime("%m_%d_%Y, %H:%M:%S")), sp, EnforceSpeed , VehicleDirection,
                            VehicleLan, GPSLati, GPSLongi, name, ref_name, '{}/Aggregate'.format(todate) ])
                    except:
                        scanlog()
                        if sp >= EnforceSpeed :
                            jetson.utils.saveImage(os.path.join(overSpeedPath, name), cuimage)
                        
                            logger.info([str(datetime.datetime.now().strftime("%m_%d_%Y, %H:%M:%S")), sp, EnforceSpeed , VehicleDirection,
                            VehicleLan, GPSLati, GPSLongi, name, ref_name, '{}/OverSpeed'.foramt(todate) ])
                            
                        elif sp <= EnforceSpeed :
                            jetson.utils.saveImage(os.path.join(aggpath, name), cuimage)
                        
                            logger.info([str(datetime.datetime.now().strftime("%m_%d_%Y, %H:%M:%S")), sp, EnforceSpeed , VehicleDirection,
                            VehicleLan, GPSLati, GPSLongi, name, ref_name, '{}/Aggregate'.format(todate) ])
                        
                       
            
            # convert to BGR, since that's what OpenCV expects
            if show_output:
                bgr_img = jetson.utils.cudaAllocMapped(width=cuimg.width,
                                                height=cuimg.height,
                                                format='bgr8')

                jetson.utils.cudaConvertColor(cuimg, bgr_img)

                # make sure the GPU is done work before we convert to cv2
                jetson.utils.cudaDeviceSynchronize()

                # convert to cv2 image (cv2 images are numpy arrays)
                cv_img = jetson.utils.cudaToNumpy(bgr_img)
                cv2.line(cv_img,(0,self.show_line),(1980,self.show_line),(0,0,255),1)
                cv2.putText(cv_img, "Processing {:.0f} FPS {}{}".format(self.net.GetNetworkFPS(), " "*50, self.speed_text), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
                cv2.imshow("window", cv_img)
                key = cv2.waitKey(1)
                if key == 27:
                    self.closeProject()
                #self.display.SetStatus("Processing {:.0f} FPS {}{}".format(self.net.GetNetworkFPS(), " "*50, self.speed_text))
                #self.display.Render(img)

        
        pass # end of run function

