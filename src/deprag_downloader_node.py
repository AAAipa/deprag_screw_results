#!/usr/bin/env python
import rospy
from deprag_downloader.srv import download_request
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
import requests as requester
import os
from deprag_downloader.msg import screwing
import csv
import shutil
import time

downloadDirectory = "/home/adm-awi/Downloads/TestFolder"

depragIP = "172.10.25.100" #ip address of the deprag screwdriver

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def callback_download(data): #if data is -1 publishe curve to topic
    #copy past download part with data.iTarget as Index
    #set up headles browse
    global downloadDirectory
    backupDownload = downloadDirectory
    pub = False
    if(data.iTarget < 0):
        pub = True
        data.iTarget = 1 
        downloadDirectory = "/tmp/deprag_downloaderERmabs4k23lknad33"
        os.mkdir(downloadDirectory)
    

    opts = Options()
    opts.set_headless()
    fxProfile = FirefoxProfile()
    
    fxProfile.set_preference("browser.download.folderList",2)
    fxProfile.set_preference("browser.download.manager.showWhenStarting",False)
    fxProfile.set_preference("browser.download.dir",downloadDirectory)
    fxProfile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv/ast")
    browser = Firefox(options=opts,firefox_profile=fxProfile)

    #interact with duck duck
    browser.get("http://" + depragIP + "/cgi-bin/cgiread?site=-&request=curves&args=&mode=-1-")
    
    
    dropdown = browser.find_element_by_class_name("dd-selected")
    dropdown.click()
    choice = browser.find_elements_by_class_name("dd-option")
    choice[1].click()
    downloads = browser.find_elements_by_class_name("download")
    downloads[data.iTarget].click()
    
    browser.close()

    if(pub):
        _kurve_name = os.listdir(downloadDirectory)[0]
        print(_kurve_name)
        subDir = "/sub" #sub directory to determine what program was used
        os.mkdir(downloadDirectory + subDir) 


        opts = Options()
        opts.set_headless()
        fxProfile = FirefoxProfile()
    
        fxProfile.set_preference("browser.download.folderList",2)
        fxProfile.set_preference("browser.download.manager.showWhenStarting",False)
        fxProfile.set_preference("browser.download.dir",downloadDirectory + subDir)
        fxProfile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv/ast")
        browser = Firefox(options=opts,firefox_profile=fxProfile)

        #interact with duck duck
        browser.get("http://" + depragIP + "/cgi-bin/cgiread?site=-&request=fvalues&args=&mode=-1-")
        
        
        
        downloads = browser.find_elements_by_class_name("download")
        downloads[ len(downloads) - 2].click()
        
        browser.close()

        info = open(downloadDirectory + subDir + "/actual.csv","r")
        _info = info.read()
        info.close()
        _info = _info[20:]
        c = _info.find(",")
        _info = _info[:c]
        
        _prgrmNumber = int(_info)
        print(_prgrmNumber)

        #get programm info
        _str = "http://"+ depragIP +"/cgi-bin/cgiread?site=getprg&program=" + str(_prgrmNumber)
        r = requester.get(_str)
        prgmInfo = r.text
        print(prgmInfo)  #for debuging can be disabled

        msg = screwing()
        msg.prgrmInfo = prgmInfo
        os.rename(downloadDirectory + "/" + _kurve_name,downloadDirectory + "/data.txt")

        _csv = open(downloadDirectory + "/data.txt","r")
        _csv_str =  _csv.read()
        c = _csv_str.find("Temperatur")
        c = c+15
        _csv_str = _csv_str[c:]
        msg.csv = _csv_str
        _csv.close()
        publer.publish(msg)

        filepath = backupDownload + "/" + str(time.time()) +".json"
        _f = open(filepath, "w")
        jsonInfo = prgmInfo.replace("\n",",\n\"")
        jsonInfo = jsonInfo.replace("=","\":")
        jsonInfo = "\"" + jsonInfo
        c = find_nth(jsonInfo,":",2) + 1
        jsonInfo = jsonInfo[:c] + "\"" + jsonInfo[c:]
        c = find_nth(jsonInfo,",",2)
        jsonInfo = jsonInfo[:c] + "\"" + jsonInfo[c:]
        _f.write("{ \n")
        _f.write(jsonInfo)


        zeit = "["
        Dmess1 = "["
        Wmess1 = "["
        Dmotor = "["
        Wmotor = "["
        DZ = "["
        Schritt = "["
        Strom = "["
        Temp = "["
        lines = _csv_str.count("\n") + 1 #anzahl Zeilen
        for i in range(0,lines):
            #Zeit
            c = _csv_str.find(",")
            zeit = zeit + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #Mess1 Dreh
            c = _csv_str.find(",")
            Dmess1 = Dmess1 + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #W mess1
            c = _csv_str.find(",")
            Wmess1 = Wmess1 + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #D motor
            c = _csv_str.find(",")
            Dmotor = Dmotor + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #W Motor
            c = _csv_str.find(",")
            Wmotor = Wmotor + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #Drehzahl
            c = _csv_str.find(",")
            DZ = DZ + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #Schritt
            c = _csv_str.find(",")
            Schritt = Schritt + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #Strom
            c = _csv_str.find(",")
            Strom = Strom + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]
            #temp
            c = _csv_str.find("\n")
            Temp = Temp + _csv_str[:c] + ","
            _csv_str = _csv_str[c+1:]

        zeit = zeit.replace("\n","")

        zeit = zeit[:(len(zeit) - 2)] + "],"
        Dmess1 = Dmess1[:(len(zeit) - 2)] + "],"
        Wmess1 = Wmess1[:(len(zeit) - 2)] + "],"
        Dmotor = Dmotor[:(len(zeit) - 2)] + "],"
        Wmotor = Wmotor[:(len(zeit) - 2)] + "],"
        DZ = DZ[:(len(zeit) - 2)] + "],"
        Schritt = Schritt[:(len(zeit) - 2)] + "],"
        Strom = Strom[:(len(zeit) - 2)] + "],"
        Temp = Temp[:(len(zeit) - 2)] + "]"

        _f.write("csv\" : { \n")
        t = "   \"Zeit(0.001 ms)\":" + zeit
        t.replace("\n","")
        _f.write(t + "\n")
        _f.write("  \"Drehmoment Messsystem 1 (Nm)\":" + Dmess1 + "\n")
        _f.write("  \"Winkel Messsystem 1\":" + Wmess1 + "\n")
        _f.write("  \"Drehmoment Motor (Nm)\":" + Dmotor + "\n")
        _f.write("  \"Winkel Motor\":" + Wmotor + "\n")
        _f.write("  \"Drehzahl (U/min)\":" + DZ + "\n")
        _f.write("  \"Schritt\":" + Schritt + "\n")
        _f.write("  \"Stromstaerke (A)\":" + Strom + "\n")
        _f.write("  \"Temperatur (C)\":" + Temp + "\n")
        

    

        _f.write("}\n")
        _f.write("  }")
        _f.close()

        shutil.rmtree(downloadDirectory, ignore_errors=True)

        
    
    


    downloadDirectory = backupDownload
    return []

publer = 0

def downloader():
    global publer
    rospy.init_node("deprag_downloader",anonymous=True)
    service_download = rospy.Service('deprag_download', download_request, callback_download)
    publer = rospy.Publisher('deprag/curves', screwing, queue_size=10)
   
    

    rospy.spin()


if __name__ == '__main__':  #apparetly good practise in python
    try:
        downloader()
    except rospy.ROSInterruptException: pass 