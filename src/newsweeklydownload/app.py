"""
新闻周刊下载器
"""
import sys
from typing import Optional
from newsweeklydownload.mainui import Ui_MainWindow
from newsweeklydownload.NwDownload import XwzkDownload

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    # Backwards compatibility - importlib.metadata was added in Python 3.8
    import importlib_metadata

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal

class DowmloadThread(QThread):
    global urls
    # 继承并重写
    # 信号用于传递视频序列
    download_index = Signal(int)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):    
        import os, requests
        Run = True
        while Run:
            # 创建临时目录
            # path = os.getcwd()
            path = "C:\\"
            if not os.path.exists("%s/xwzk_tmp"%path):
                os.makedirs("%s/xwzk_tmp"%path)
            n = 0
            for i in self.urls:
                n += 1
                # 发射信号
                self.download_index.emit(n)
                recv = requests.get(i)
                if recv.status_code == 200:
                    if n <= 9:
                        n = "0" + str(n)
                    p = path + "/xwzk_tmp/" + str(n) + ".mp4"
                    with open(p, "wb") as f:
                        f.write(recv.content)

                        n = int(n)
                else:
                    self.download_index.emit(502)
                    break
            Run = False

class ConcatThread(QThread):

    def __init__(self):
        super().__init__()
        

    def run(self):
        Run = True
        while Run:
            import os, shutil, re
            path = "C:\\"
            files = os.listdir("%s/xwzk_tmp" % path)
            files.sort()
            with open("%s/xwzk_tmp/video.txt" %path, "w+") as f:
                for i in files:
                    if re.match(r"\d+.mp4", i):
                        tmp = "file '" + i + "'\n"
                        f.write(tmp)
            os.system("cd C:\\xwzk_tmp && ffmpeg -f concat -i video.txt -c copy concat.mp4")
            if not os.path.exists("C:/Video"):
                os.makedirs("C:/Video")
            shutil.move("C:/xwzk_tmp/concat.mp4", "C:/Video/新闻周刊.mp4")
            shutil.rmtree("C:/xwzk_tmp")
            Run = False


class NewsweeklyDownload(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(NewsweeklyDownload, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        '''
        初始化
        '''
        self.setupUi(self)
        self.main()
        self.show()

    def main(self):
        # 菜单栏动作
        self.action_exit.triggered.connect(self.exit)
        self.action_author.triggered.connect(self.author)
        self.action_home.triggered.connect(self.home)
        self.actioninstall.triggered.connect(self.installff)
        self.actionopen.triggered.connect(self.open)
        # 初始化控件
        self.pushButton_2.setEnabled(False)
        self.pushButton.clicked.connect(self.flash)
        self.pushButton_2.clicked.connect(self.download)
        self.tableWidget.setColumnWidth(0,208)
        self.tableWidget.setRowCount(20)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        
        

    def exit(self):
        '''
        退出函数
        '''
        self.close()

    def open(self):
        import os
        # path = os.getcwd()
        # path2 = path + "\\Video"
        path2 = "C:\\Video"
        try:
            os.system("start explorer %s"%path2)
        except:
            self.OutputInfo("路径不存在",1000)

    def installff(self):
        import shutil, os
        if not os.path.exists("C:\\ffmpeg\\bin\\ffmpeg.exe"):
            src = r"./app/newsweeklydownload/ffmpeg/bin"
            dst = r"C:/ffmpeg"
            # 如果文件不存在，则删除C:\ffmpeg并重新创建
            try:
                shutil.rmtree(dst)
                os.makedirs("C:/ffmpeg")
            except:
                pass
            # 复制ffmpeg.exe到C:\ffmpeg\bin\内
            shutil.copytree(src, dst)
            ffmpeg_path = 'C:\\ffmpeg\\bin'
            # 拼接环境变量路径
            os.environ["PATH"] = ffmpeg_path + ";" + os.environ["PATH"]
            self.OutputInfo("ffmpeg配置成功", 3000)
        else:
            self.OutputInfo("文件已存在",3000)
            


    def author(self):
        '''
        作者
        '''
        QtWidgets.QMessageBox.information(self, "作者", "作者:letr")

    def home(self):
        '''
        项目主页
        '''
        QtWidgets.QMessageBox.information(self, "项目链接", "https://github.com/letr007/NewsweeklyDownload\n如果觉得好用就请投个star支持一下~")

    def OutputInfo(self, Info, Time):
        '''将信息输出状态栏'''
        self.statusbar.showMessage(Info, Time)

    def flash(self):
        '''刷新表格'''
        self.OutputInfo("获取视频列表...", 2000)
        self.NwDl = XwzkDownload()
        self.dict = self.NwDl.getVideoList()
        self.OutputInfo("处理数据...", 2000)
        num = 0
        dict1 = self.dict
        for i in dict1:
            item1 = QtWidgets.QTableWidgetItem(dict1[i][0])
            self.tableWidget.setItem(num, 0, item1)
            num += 1
        self.tableWidget.viewport().update()
        self.OutputInfo("刷新完成", 10000)
        self.pushButton_2.setEnabled(True)

    def download(self):
        '''下载'''
        # global urls
        self.OutputInfo("下载...", 1000)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        try:
            self.OutputInfo("获取链接...", 1000)
            num = self.spinBox.text()
        
            info = self.NwDl.getHttpVideoInfo(self.dict[int(num)][1])
            urls = self.NwDl.getDownloadUrls(info)
            self.OutputInfo("下载视频...", 1000)
        
            self.work = DowmloadThread(urls)
            self.work.download_index.connect(self.dl)
            self.work.start()
            self.work.finished.connect(self.concat)            
        except Exception as e:
            self.OutputInfo(str(e), 100000)

    def concat(self):
        '''拼接'''
        self.OutputInfo("下载完成",1000)
        self.OutputInfo("合并视频...",600000)
        self.work_2 = ConcatThread()
        self.work_2.start()
        self.work_2.finished.connect(self.finished)

    def finished(self):
        '''完成'''
        self.OutputInfo("合并完成!!!", 60000)
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
            
    def dl(self, int):
        if int != 502:
            self.OutputInfo("正在下载第%s个视频文件..." %int , 60000)
        else:
            self.OutputInfo("下载出错，请重试", 60000)









def main():
    # Linux desktop environments use app's .desktop file to integrate the app
    # to their application menus. The .desktop file of this app will include
    # StartupWMClass key, set to app's formal name, which helps associate
    # app's windows to its menu item.
    #
    # For association to work any windows of the app must have WMCLASS
    # property set to match the value set in app's desktop file. For PySide2
    # this is set with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules['__main__'].__package__
    # Retrieve the app's metadata
    metadata = importlib_metadata.metadata(app_module)

    QtWidgets.QApplication.setApplicationName(metadata['Formal-Name'])

    app = QtWidgets.QApplication(sys.argv)
    main_window = NewsweeklyDownload()
    sys.exit(app.exec())