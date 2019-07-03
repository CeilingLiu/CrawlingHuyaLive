import requests
import re
from queue import Queue
from lxml import etree
import json,time,os
import threading
import time,shutil

RoomNum="saonan"      #房间号
WebUrl="https://www.huya.com/"



DownLoadList=[] #ts视频下载队列
islive=True
SaveDirName=""
LogFileName=""


def printlog(logdata):
    strtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    writelog=strtime+" "+str(logdata)
    f = open(LogFileName, "a")
    f.writelines(writelog)
    f.write("\n")

def GetStreamConfigInfo():
    global islive
    #获取流信息,返回对象
    url=WebUrl+str(RoomNum)
    try:
        html = requests.get(url)
    except:
        printlog("connect fail,try again")
        islive=None
    # print(html)
    html = etree.HTML(html.text)  # 初始化生成一个XPath解析对象
    items = html.xpath('//script[contains(@data-fixed,"true")]')
    strItem=items[0].text
    ConfigStr=strItem[strItem.find("hyPlayerConfig")+16:strItem.find("window.TT_LIVE_TIMING = {};")-10].strip(" ")
    try:
        mm=json.loads(ConfigStr)
    except:
        printlog("room error")
    return mm

def DownM3U8():
    global DownLoadList
    global islive
    global SaveDirName
    lasturl=""
    while True:
        time.sleep(0.1)
        ConfigDic = GetStreamConfigInfo()
        # print(ConfigDic)
        if ConfigDic['stream'] == None:
            printlog("未开播")
            time.sleep(10)
            islive=None
        else:
            printlog("直播中....")
            gameLiveInfoDic = ConfigDic["stream"]["data"][0]
            gameStreamInfoList = gameLiveInfoDic["gameStreamInfoList"]
            gameLiveInfo=gameLiveInfoDic["gameLiveInfo"]
            gameStreamInfoDic = gameStreamInfoList[0]
            HttpUrl = gameStreamInfoDic["sFlvUrl"].replace("\\", "")
            sStreamName = gameStreamInfoDic["sStreamName"]
            sHlsUrl = gameStreamInfoDic["sHlsUrl"].replace("\\", "")
            sHlsUrlSuffix = gameStreamInfoDic["sHlsUrlSuffix"]
            #时间戳转换格式
            timeStamp=gameLiveInfo["startTime"]
            timeArray = time.localtime(int(timeStamp))
            otherStyleTime = time.strftime("%Y-%m-%d_%H-%M-%S", timeArray)
            SaveDirName= gameLiveInfo["nick"]+"_"+  gameLiveInfo["profileRoom"]+ "_"+otherStyleTime    #视频流保存目录（主播名_房间号_开始时间）
            #判断目录是否存在，不存在则创建
            if os.path.exists(SaveDirName):
                pass
            else:
                os.mkdir(SaveDirName)
            m3u8Url = sHlsUrl + "/" + sStreamName + "." + sHlsUrlSuffix
            re = requests.get(m3u8Url)
            strre = str(re.text)
            # print(strre)
            url = sHlsUrl + "/" + strre[strre.rfind(",") + 2:].strip(" ")
            # print(url)
            if url == lasturl:
                pass
            else:
                DownLoadList.append(url)
            lasturl = url
            islive = True

#debug
def DownTs():
    i = 0
    while True:
        if islive==None and len(DownLoadList) == 0:
            if os.path.exists(SaveDirName+"/filelist.txt"):
                try:
                    kk = os.listdir(SaveDirName)
                    list = []
                    for i in kk:
                        if i == "filelist.txt":
                            pass
                        else:
                            list.append(int(i[:-3]))
                    obj = sorted(list)
                    w = open(SaveDirName+"/filelist.txt", "w")
                    for o in obj:
                        w.writelines("file \'%s.ts\'" % (str(o)))
                        w.write("\n")
                    w.close()
                    # obj=sorted(list)
                    # for o in obj:
                    # return 0

                    cmd = "ffmpeg -f concat -i \"%s/filelist.txt\" -codec copy %s" % (SaveDirName, SaveDirName + ".ts")
                    # print(cmd)
                    # return 0
                    res=os.system(cmd)
                    if res==0:
                        shutil.rmtree(SaveDirName)
                        printlog("finish")
                    else:
                        continue


                except:
                    printlog("Error:merge video fail,try again")
                    continue

            else:
                pass
            time.sleep(10)
            continue
        else:
            time.sleep(0.3)
            printlog("下载队列：%s"%( len(DownLoadList)))
            if len(DownLoadList) == 0:
                continue
            else:
                i = i + 1
                DownTsUrl = DownLoadList[0]
                name = DownTsUrl[DownTsUrl.rfind("/") + 1:DownTsUrl.rfind("?")]
                # print(DownTsUrl)
                # print(name)
                name = str(i) + ".ts"
                # SortedTsList.append(name + "\n")
                # printlog(SortedTsList)

                try:
                    r = requests.get(DownTsUrl)
                    TsSaveUrl = SaveDirName + "/" + str(i) + ".ts"
                    with open(TsSaveUrl, "ab") as code:
                        code.write(r.content)
                    DownLoadList.remove(DownTsUrl)
                    f = open(SaveDirName + "/" + "filelist.txt", "w")
                    f.write("测试文件")
                    f.close()
                except:
                    printlog("Error:Download error!!!")
                    continue


def ClearInit():
    #初始化log文件名
    global LogFileName
    strtime = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    LogFileName="log_"+strtime+".txt"
    #删除文件夹
    print("Start...")

if __name__ == '__main__':
    ClearInit()
    #获取url线程
    m = threading.Thread(target=DownM3U8)
    m.start()
    #下载ts视频线程
    n = threading.Thread(target=DownTs)
    n.start()
    # Cmd="ls"
    # m=os.system(Cmd)
    # if m ==0:
    #     print("ok")
    # else:
    #     print("eoor")
    # DownTs()








