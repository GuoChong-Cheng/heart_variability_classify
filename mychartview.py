from PyQt5.QtCore import Qt
from PyQt5.QtChart import *
 
class MYChartView(QChartView):
# view 总窗口
    def __init__(self,parent):
        super(MYChartView, self).__init__()
        self.setParent(parent)
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton):
            self.lastpoint = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
          
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton :  
            offset = event.pos()-self.lastpoint
            self.chart().scroll(-offset.x(),offset.y())
            # axisx_min = getattr(self.chart().axisX(), 'min')
            # axisx_max = getattr(self.chart().axisX(), 'max')
            # axisy_min = getattr(self.chart().axisY(), 'min')
            # axisy_max = getattr(self.chart().axisY(), 'max')
            # self.chart().axisX().setRange(axisx_min()-offset.x(),axisx_max()-offset.x())
            # self.chart().axisY().setRange(axisy_min()+offset.y(),axisy_max()+offset.y())
            #print()
            self.lastpoint = event.pos()
            

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton):
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        if(event.button() == Qt.MouseButton.RightButton):
            self.chart().zoomReset()
            self.chart().zoom(0.99999)
            
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.chart().zoomIn()
        else:
            self.chart().zoomOut()

    def keyPressEvent(self, event):
        pass
    def keyReleaseEvent(self, event):
        pass


