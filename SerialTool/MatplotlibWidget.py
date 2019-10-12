import sys
import matplotlib

matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #画布
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar#工具条
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MyMplCanvas(FigureCanvas):
    #FigureCanvas的最终父类其实是QWidget
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #设置中文显示
        plt.rcParams['font.family'] = ['SimHei'] #用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
        
        #新建一个绘图对象
        
        self.fig = Figure(figsize = (width, height), dpi=dpi)
        #新建一个子图。如果要建立复合图，可以在这里修改
        self.axes = self.fig.add_subplot(111)
        #self.axes.hold(False) #每次绘图时都不保留上一次绘图的结果
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        '''定义FigureCanvas的尺寸策略，意思是设置FigureCanvas，使之尽可能向外填充空间'''
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    
    #绘制静态图，可以在这里定义绘图逻辑    
    def start_static_plot(self):
        self.fig.suptitle('测试静态图')
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)
        self.axes.set_ylabel('静态图：Y轴')
        self.axes.set_xlabel('静态图：X轴')
        self.axes.grid(True)

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.initUi()
        
    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        #添加完整的工具栏
        self.mpl_ntb = NavigationToolbar(self.mpl, self)
        
        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    ui.mpl.start_static_plot() #测试静态图效果
    ui.show()
    sys.exit(app.exec_())
