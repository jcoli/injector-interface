"""
Version: 0a
Tecnocoli - @07/2020
Author: Jeferson Coli - jcoli@tecnocoli.com.br
SPEED SENSOR SIMULATOR - camshafts and crankshafts - Arduino Uno/Nano
Main
"""

from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTableView, QMessageBox
from PyQt5.QtCore import QFile, QTimer, QTime, Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import pyqtgraph
from pyqtgraph import PlotWidget
from functions.gen_pattern import btn_next, btn_prior


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
text_date = datetime.now().strftime('%d-%m-%Y')
scanner_file = 'injector-' + text_date+'.log'
handler = logging.FileHandler(scanner_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def plotgraph(input):
    if input.debug:
        logger.info("plotGraph")
    Y1 = [0, 0, 1, 1, 0, 0, 1, 1, 1, 1]
    Y2 = [3, 3, 3, 3, 4, 4, 4, 4, 3, 3]
    Y3 = [6, 6, 5, 5, 6, 6, 5, 5, 6, 6]
    Y4 = [2, 2, 2, 2, 2, 2, 3, 3, 3, 3]
    X = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    pen1 = pyqtgraph.mkPen(color=(255, 85, 0))
    pen2 = pyqtgraph.mkPen(color=(0, 85, 255))
    pen3 = pyqtgraph.mkPen(color=(8, 255, 144))
    pen4 = pyqtgraph.mkPen(color=(255, 0, 0))
    input.graphicsView.plot(X, Y1, pen=pen1)
    input.graphicsView.plot(X, Y2, pen=pen2)
    input.graphicsView.plot(X, Y3, pen=pen3)
    input.graphicsView.plot(X, Y4, pen=pen4)


def plotgraph_pattern(input, teeth, pattern):
    if input.debug:
        logger.info("plotGraph Pattern")
    input.tab_bar.setTabEnabled(3, True)
    input.tab_bar.setCurrentIndex(3)
    # input.btn_graph_pat.setEnabled(False)
    pen1 = pyqtgraph.mkPen(color=(255, 85, 0))
    pen2 = pyqtgraph.mkPen(color=(0, 85, 255))
    pen3 = pyqtgraph.mkPen(color=(8, 255, 144))
    pen4 = pyqtgraph.mkPen(color=(255, 0, 0))
    if teeth > 0:
        input.edges = teeth
        dim_x = (teeth * 4)
        line_x = []
        pat_y1 = []
        pat_y2 = []
        pat_y3 = []
        pat_y4 = []
        pat_y1.append(0)
        pat_y2.append(3)
        pat_y3.append(6)
        pat_y4.append(9)
        for i in range(0, dim_x+2):
            line_x.append(int(i)+1)
        for z in range(0, dim_x):
            i = int(z/2)
            y1 = (2 ** 0) & int(pattern[i])
            y2 = (2 ** 1) & int(pattern[i])
            y3 = (2 ** 2) & int(pattern[i])
            y4 = (2 ** 3) & int(pattern[i])
            if y1 > 0:
                pat_y1.append(2)
            else:
                pat_y1.append(0)
            if y2 > 0:
                pat_y2.append(5)
            else:
                pat_y2.append(3)
            if y3 > 0:
                pat_y3.append(8)
            else:
                pat_y3.append(6)
            if y4 > 0:
                pat_y4.append(11)
            else:
                pat_y4.append(9)
        pat_y1.append(0)
        pat_y2.append(3)
        pat_y3.append(6)
        pat_y4.append(9)
        input.graphicsView.clear()
        input.graphicsView.showGrid(True, False, 0.7)
        input.graphicsView.showAxis('left', False)
        # input.graphicsView.showAxis('bottom', False)
        input.graphicsView.plot(line_x, pat_y1, pen=pen1)
        input.graphicsView.plot(line_x, pat_y2, pen=pen2)
        input.graphicsView.plot(line_x, pat_y3, pen=pen3)
        input.graphicsView.plot(line_x, pat_y4, pen=pen4)


def plotgraph_gen_pattern(input):
    if input.debug:
        logger.info("plotGraph Gen Pattern")
    btn_prior(input)
    pattern = input.textEdit_gen_pattern.toPlainText()
    teeth = int(input.line_gen_edges.text())
    pattern_temp1 = (pattern.split(","))
    pattern2 = []
    # logger.info("PatternTemp " + str(pattern_temp1))
    for i in range(0, len(pattern_temp1) - 1):
        pattern2.append(int(pattern_temp1[i]))
    # logger.info("Pattern2 " + str(pattern2))
    plotgraph_pattern(input, teeth, pattern2)

def plotgraph_data(input):
    if input.debug:
        logger.info("plotGraph data")
    pattern = input.textEdit_pattern.toPlainText()
    teeth = int(input.lineEdit_dentes.text())
    pattern_temp1 = (pattern.split(","))
    pattern2 = []
    # logger.info("PatternTemp " + str(pattern_temp1))
    for i in range(0, len(pattern_temp1) - 1):
        pattern2.append(int(pattern_temp1[i]))
    # logger.info("Pattern 2 " + str(pattern2))
    plotgraph_pattern(input, teeth, pattern2)
