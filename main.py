import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtChart import *

import mymainwindow

if __name__ == '__main__':
    app = QApplication(sys.argv)   
    mainWindow = QMainWindow()
    ui = mymainwindow.my_ui()
    ui.setupUi(mainWindow)
    ui.serial_init()
    ui.chart_init()
    mainWindow.show()
 
    sys.exit(app.exec_())


