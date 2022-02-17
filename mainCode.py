
from utility import *
import time
import configparser
import os
import ftplib
import datetime
from classAI import AI
from config import *

class Main:
    def __init__(self):
        self.old_date = datetime.datetime.now().strftime('%Y_%m_%d')
        self.config_ini = self.read_ini('config.ini')
        self.ftp = ftplib.FTP(self.config_ini['FTP']['server'], self.config_ini['FTP']['username'], self.config_ini['FTP']['password'])
        if not os.path.isdir('./temp'):
            os.mkdir('./temp')

        if not os.path.isdir(overSpeedPath):
            os.mkdir(overSpeedPath)
        
        if not os.path.isdir(aggpath):
            os.mkdir(aggpath)

        self.ai = AI(self.config_ini)
        self.ai.start()

        self.loop()

    def read_ini(self,file_path):
        config_ini = {'CAMERA':{}, 'FTP':{}}
        config = configparser.ConfigParser()
        config.read(file_path)
        for section in config.sections():
            # print(section)
            if section == 'CAMERA':
                for key in config[section]:
                    config_ini['CAMERA'][key] = (config[section][key])

            if section == 'FTP':
                for key in config[section]:
                    config_ini['FTP'][key] = (config[section][key])
        return config_ini
    
    def directory_exists(self,dir):
        filelist = []
        self.ftp.retrlines('LIST', filelist.append)
        #print("File list -------------------------- ",filelist)
        for f in filelist:
             if f.split()[-1] == dir and f.split()[-2].upper().startswith('<DIR>'):
                return True
        return False

    def chdir(self, dir):
        print(dir)
        if not self.directory_exists(dir):
            listfolder = self.ftp.nlst()

            if dir not in listfolder:
                self.ftp.mkd('./' + dir)
            self.ftp.cwd('./' + dir)
            print('create folder')
        print('exist folder')

    def loop(self):
        print("ftp triggered")
        


        todate = datetime.datetime.now().strftime('%Y_%m_%d')
        if self.old_date == todate:
            pass
        else:
            if not scanlog:
                #upload csv folder
                self.ftp.cwd(f"/{self.old_date}")
                img_file = open(old_csv_file, 'rb')  # file to send
                self.ftp.storbinary('', img_file)  # send the file
                img_file.close()
                os.remove(os.path.join(ROOT_DIR, old_csv_file))
        self.chdir(todate)
        self.ftp.cwd(f"/{todate}")
        while True:
            try:
                fs = os.listdir(overSpeedPath)
                fs2 = os.listdir(aggpath)
                if fs.__len__() > 0:
                    png_files = [f for f in fs if os.path.splitext(f)[1].lower() == '.png']
                    for png in png_files:
                       
                        upload_folder_path = ''
                        self.chdir("OverSpeed")
                        self.ftp.cwd(f"/{todate}/OverSpeed")
                        upload_path = f"STOR {png}"
                        img_file = open(overSpeedPath +'/' + png, 'rb')  # file to send
                        current = self.ftp.pwd()
                        print("****************************************************** IN PATH :",current)
                        self.ftp.storbinary(upload_path, img_file)  # send the file
                        img_file.close()
                        os.remove(os.path.join(overSpeedPath, png))
                        self.ftp.cwd(f"/{todate}")
                       
                        current = self.ftp.pwd()
                        print("****************************************************** IN PATH :",current)
                if fs2.__len__() > 0:
                    png_files = [f for f in fs2 if os.path.splitext(f)[1].lower() == '.png']
                    for png in png_files:
                       
                        upload_folder_path = ''
                        self.chdir("Aggregate")
                        self.ftp.cwd(f"/{todate}/Aggregate")
                        upload_path = f"STOR {png}"
                        img_file = open(aggpath +'/' + png, 'rb')  # file to send
                        current = self.ftp.pwd()
                        print("****************************************************** IN PATH :",current)
                        self.ftp.storbinary(upload_path, img_file)  # send the file
                        img_file.close()
                        os.remove(os.path.join(aggpath, png))
                        self.ftp.cwd(f"/{todate}")

                time.sleep(0)
            except Exception as error:
                print("****** ERROR INM MAIN PROG : ", error)
                self.ai.closeProject()
                break



    pass # end of main class


if __name__ == '__main__':

    mainobj = Main()