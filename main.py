"""
Version: 0a
Tecnocoli - @07/2020
Author: Jeferson Coli - jcoli@tecnocoli.com.br
SPEED SENSOR SIMULATOR - camshafts and crankshafts - Arduino Uno/Nano
Main
"""

import sys
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTableView, QMessageBox
from PyQt5.QtCore import QFile, QTimer, QTime, Qt
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import pyqtgraph
from pyqtgraph import PlotWidget
from pathlib import Path
from forms.MainWindow import Ui_MainWindow
import numpy


# import sqlite3
import hashlib
import serial
from datetime import datetime
import time
from time import sleep
from functions.conn_serial import scan_serial, serial_list_ports, serial_read_events
from functions.basic_controls import btn_connect, btn_send, send_patern, send_patern1
from functions.db_controls import tableWheel_clicked_db, btnw_insert, btnw_edit, btnw_update\
    , btnw_cancel, btnw_delete, tableChoose_clicked_db, btnw_new, cp_pattern, teeth_changed\
    , export_data, import_data, btnw_save
from functions.gen_pattern import btn_next, btn_prior, btn_gen_pattern, \
    line_gen_edges_changed_pat, start_pat, clean_pat, cb000_t_clicked
import functions.btn_controls
from functions.plot_graph import plotgraph, plotgraph_pattern, plotgraph_gen_pattern, plotgraph_data
from functions.get_css.get_qtcss import get_style, available_styles


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




# conn = sqlite3.connect('venv/database/injetor.db')
# cur = conn.cursor()
#ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2);    #/dev/ttyACM0

#mil_lamp = True


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    bit_alive = False
    thread_bit = False
    mil_lamp = True
    conected = False
    simu_conn = False
    livebit_tmp = 0
    prog_id = []
    hash_id = hashlib.md5()
    inTx = False
    inRx = False
    stopGo = False
    value_serial = ""
    rpm_min = 0
    rpm_max = 7500
    next_rpm = 0
    edges = 0
    max_pages = 25
    edges_last_page = 10
    page_pattern = 1
    pattern_p = ""
    pattern_pt = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    thread_flag = None
    debug = True
    conn_timeout = 15
    flag_new = False
    flag_import = False
    pattern = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ser = serial.Serial();

        self.setupUi(self)
        self.tab_bar.setCurrentIndex(0)
        if not self.debug:
            self.tab_bar.removeTab(4)
        self.tab_bar.setTabEnabled(2, False)
        self.tab_bar.setTabEnabled(3, False)
        self.t1 = threading.Thread(target=self.task1)
        self.onlyInt = QIntValidator(0, 120, self)
        #self.tabDebug.setVisible(False)
        self.btnConnect.clicked.connect(self.btn_connect_clicked)
        self.btnStopGo.clicked.connect(self.btn_stop_go)
        self.btnw_edit.clicked.connect(self.btnw_edit_clicked)
        self.btnw_update.clicked.connect(self.btnw_update_clicked)
        self.btnw_cancel.clicked.connect(self.btnw_cancel_clicked)
        self.btnw_export.clicked.connect(self.btnw_export_clicked)
        self.btnw_import.clicked.connect(self.btnw_import_clicked)
        self.btnw_delete.clicked.connect(self.btnw_delete_clicked)
        self.btn_nw_send.clicked.connect(self.btn_nw_send_clicked)
        self.btnw_new.clicked.connect(self.btnw_new_clicked)
        self.btnw_cancel.setEnabled(False)
        self.btnw_update.setEnabled(False)
        self.btnw_delete.setEnabled(False)
        self.btn_nw_send.setEnabled(False)
        if not self.debug:
            self.rb_1rev.hide()
            self.rb_2rev.hide()
            self.lineEdit_edges.hide()
            self.label_24.hide()
            self.label_4.hide()
            self.label_5.hide()
            self.textEdit_pattern.hide()
            self.textEdit_gen_pattern.hide()
            self.lineEdit_scaler.hide()

        self.btn_prior_pat.clicked.connect(self.btn_prior_pat_clicked)
        self.btn_next_pat.clicked.connect(self.btn_next_pat_clicked)
        self.btn_gen_pat.clicked.connect(self.btn_gen_pat_clicked)
        self.btn_clear_pat.clicked.connect(self.btn_clear_pat_clicked)
        self.line_gen_edges.setValidator(self.onlyInt)
        self.cb001_t.clicked.connect(self.cb001_t_clicked)
        self.cb002_t.clicked.connect(self.cb002_t_clicked)
        self.cb003_t.clicked.connect(self.cb003_t_clicked)
        self.cb004_t.clicked.connect(self.cb004_t_clicked)
        self.cb011_t.clicked.connect(self.cb011_t_clicked)
        self.cb012_t.clicked.connect(self.cb012_t_clicked)
        self.cb013_t.clicked.connect(self.cb013_t_clicked)
        self.cb014_t.clicked.connect(self.cb014_t_clicked)
        self.btn_graph_pat.clicked.connect(self.plot_pat_graph_clicked)
        self.btn_graph_data.clicked.connect(self.plot_data_graph_clicked)

        self.btnStopGo.setText("Acionar")
        self.btnStopGo.setEnabled(False)
        self.label_led_stop.hide()
        self.btn_cp_pattern.clicked.connect(self.btn_cp_pattern_clicked)
        self.lineEdit_dentes.setValidator(QIntValidator(16, 60))
        self.status_bar.setStyleSheet("background-color: rgb(244, 255, 16);color: rgb(0, 0, 0);")
        self.status_bar.showMessage('Injetor Desconectado')
        self.label_led_connected_2.hide()
        self.tableWheel.clicked.connect(self.tableWheel_clicked)
        self.tableChoose.clicked.connect(self.tableChoose_clicked)
        self.btn_new_rpm.clicked.connect(self.btn_new_rpm_clicked)
        self.btn_new_rpm.setEnabled(False)
        self.line_new_rpm.setText("50")

        # self.showMaximized()
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.modelWheel = QSqlQueryModel()
        self.modelChoose = QSqlQueryModel()
        self.db.setDatabaseName("database/injector.db")
        # self.model = QSqlTableModel(self, self.db)
        if not self.db.open():
            logger.info("db error")


        self.initializedModelWheel()
        self.initializedModelChoose()
        timer: object = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)
        # self.t1.start()

    def test(self):
        logger.info("teeth changed")

    def lineEdit_TeethChanged(self):
        if self.debug:
            logger.info("teeth changed")
        teeth_changed(window)

    def btnw_import_clicked(self):
        if self.debug:
            logger.info("Import")
        import_data(window)

    def btnw_export_clicked(self):
        if self.debug:
            logger.info("Export")
        export_data(window)

    def plot_pat_graph_clicked(self):
        # if self.debug:
        #     logger.info("plot graph")
        plotgraph_gen_pattern(window)

    def plot_data_graph_clicked(self):
        if self.debug:
            logger.info("plot graph")
        plotgraph_data(window)


    def closeEvent(self, event):

        box = QtWidgets.QMessageBox()
        box.setIcon(QtWidgets.QMessageBox.Question)
        box.setWindowTitle('Fechar Aplicativo')
        box.setText('Tem certeza que deseja fechar o aplicativo?')
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        box.setDefaultButton(QtWidgets.QMessageBox.No)
        buttonY = box.button(QtWidgets.QMessageBox.Yes)
        buttonY.setText('Sim')
        buttonN = box.button(QtWidgets.QMessageBox.No)
        buttonN.setText('Não')
        box.exec_()

        if box.clickedButton() == buttonY:
            btn_send(window, self.ser, "descon")
            time.sleep(0.2)
            event.accept()
            self.thread_flag = "stop"
            time.sleep(0.7)
            if self.debug:
                logger.info("Closed")
        else:
            event.ignore()

    def btn_nw_send_clicked(self):
        if self.debug:
            logger.info("new nw")
        if self.conected:
            self.conn_timeout = 75
            self.btn_new_rpm.setEnabled(False)
            # time.sleep(20)
            send_txt = 'nw'
            # self.next_rpm = 80;
            # send_rpm = "rpm00" + str(self.next_rpm) + "#"
            self.lcdRpm.display(str(self.next_rpm))
            send_patern1(window, self.ser, send_txt)
            time.sleep(10)
            self.btn_new_rpm.setEnabled(True)
            self.btn_nw_send.setEnabled(False)
            self.stopGo = False
            self.btnStopGo.setText("Acionar")
            self.label_led_stop.hide()
            self.append_text_ptd_datetime("receive stop: ")
            self.lbl_to_send.setText("...........")
            if self.debug:
                logger.info("new nw finished")

    def show_time(self):
        # self.mil_lamp = not self.mil_lamp
        time = QTime.currentTime()
        text = time.toString('hh:mm:ss')
        if (time.second() % 2) == 0:
            text = text[:2] + ' ' + text[3:]
        self.lcdTime.display(text)
        if self.conected:
            btn_send(window, self.ser, "live")
            if not self.bit_alive:
                self.livebit_tmp = self.livebit_tmp+1
            if self.bit_alive:
                self.bit_alive = False
                self.livebit_tmp = 0
                self.conn_timeout = 15
                self.btnStopGo.setEnabled(True)
            if self.livebit_tmp == self.conn_timeout:
                if self.debug:
                    logger.info("live timeout")
                self.thread_flag = 'paused'
                self.append_text_ptd_datetime("not alive")
                self.conected = False
                self.append_text_ptd_datetime("not ok livebit")
                self.btnStopGo.setEnabled(False)
                self.label_led_connected_2.hide()
                self.status_bar.setStyleSheet("background-color: rgb(246, 11, 11);")
                self.status_bar.showMessage('Connection Error')
                self.btnConnect.setEnabled(True)
                self.append_text_ptd_datetime("serial timeout")
                self.btnConnect.setText("Desconectar")

    def task1(self):
        # if self.debug:
        #     self.append_text_ptd_datetime("new rpm: " + str(self.next_rpm))
        #     self.append_text_ptd_datetime("Inside Thread 1")

        try:
            if self.ser.isOpen():
                while True:
                    try:
                        # if self.debug:
                        #     self.append_text_ptd_datetime("Thread 1 waiting for permission to read")
                               # logger.info("waiting ")
                        while self.thread_flag != 'go':
                            time.sleep(0.1)
                            # self.append_text_ptd_datetime("Paused")
                            # if self.debug:
                            #     logger.info("Paused")
                        if self.debug:
                            logger.info("Thread 1 is waiting 1 " + self.thread_flag)

                        while self.thread_flag == 'go':
                            if self.debug:
                                logger.info("Thread 1 is reading")
                            self.value_serial = self.ser.readline().strip()
                            if len(self.value_serial) > 0:
                                serial_read_events(window, self.value_serial)
                            time.sleep(0.1)
                        if self.thread_flag == 'stop':
                            break
                        else:
                            self.thread_flag = 'paused'  # signals that the inner loop is done
                            if self.debug:
                                logger.info(str("Paused"))

                    except Exception as e:
                        logger.info("Error serial reading :" + str(e))
            else:
                if self.debug:
                    logger.info("serial closed")

        except Exception as e:
            if self.debug:
                logger.info("Error serial reading :" + str(e))
                # self.append_text_ptd_datetime("Connection Error " + str(e))
                # self.status_bar.setStyleSheet("background-color: rgb(246, 11, 11);")
                # self.status_bar.showMessage('Connection Error Thread')
                #self.append_text_ptd_datetime("Thread 1 complete")

    def btn_stop_go(self):
        if self.stopGo:
            send_txt = 'pa,stop'
        else:
            send_txt = 'pa,go'

        btn_send(window, self.ser, send_txt)

    def btn_connect_clicked(self):
        if self.debug:
            logger.info('btn connected')
        try:
            if not self.conected:
                port = scan_serial(window)
                if self.debug:
                    logger.info("Connecting 1 ")
                if port is not None:
                    if self.debug:
                        logger.info("Connecting ")
                    time.sleep(0.5)

                    ret_txt = btn_connect(window, port, self.ser, self.prog_id)
                    if ("ok" in ret_txt):
                        if self.debug:
                            logger.info("Connecting ok ")
                            self.append_text_ptd_datetime("ok")
                        self.btnStopGo.setEnabled(True)
                        self.lcdRpm.display(str(self.next_rpm))
                        time.sleep(0.5)
                        self.append_text_ptd_datetime("ok 2")
                        if not self.thread_bit:
                            self.t1.start()
                            self.thread_bit = True
                        time.sleep(0.5)
                        self.thread_flag = 'go'
                        self.bit_alive = True
                        # self.btnConnect.setEnabled(False)
                        self.btnConnect.setText("Desconectar")
                    else:
                        if self.debug:
                            logger.info("Connecting not ok connecting")
                        self.label_led_connected_2.hide()
                        self.status_bar.setStyleSheet("background-color: rgb(246, 11, 11); color: rgb(0, 0, 0);")
                        self.status_bar.showMessage('Connection Error')

                else:
                    self.status_bar.setStyleSheet("background-color: rgb(255, 107, 58);color: rgb(0, 0, 0);")
                    self.status_bar.showMessage('Connection Error: Não foi encontrado nenhum dispositivo compatível')
                    if self.debug:
                        logger.info("Connecting 2 ")
                        logger.info('Não foi encontrado nenhum dispositivo compatível')
            else:
                self.conected = False
                self.thread_flag = 'paused'
                self.bit_alive = False
                self.btnConnect.setText("Conectar")
                btn_send(window, self.ser, "descon")
                if self.debug:
                    logger.info("Disconnecting")
                self.status_bar.setStyleSheet("background-color: rgb(244, 255, 16);color: rgb(0, 0, 0);")
                self.status_bar.showMessage('Injetor Desconectado')
                self.label_led_connected_2.hide()
                self.btnStopGo.setEnabled(False)
                self.btn_new_rpm.setEnabled(False)
                self.stopGo = False
                self.btnStopGo.setText("Acionar")
                self.label_led_stop.hide()

        except Exception as e:
            if self.debug:
                logger.info("Error connecting btn_connect_clicked" + str(e))
            self.status_bar.setStyleSheet("background-color: rgb(246, 11, 11);color: rgb(0, 0, 0);")
            self.status_bar.showMessage('Connection Error')

    def btn_next_pat_clicked(self):
        btn_next(window)

    def btn_prior_pat_clicked(self):
        btn_prior(window)

    def btn_gen_pat_clicked(self):
        btn_gen_pattern(window)

    def btn_clear_pat_clicked(self):
        clean_pat(window)

    def initializedModelWheel(self):
        try:
            # self.model.setTable("WheelPattern")
            # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
            # self.model.select()
            #self.modelWheel.setQuery("SELECT * FROM WheelPattern")
            self.modelWheel.setQuery(
                "SELECT  id, name, pattern, teeth, rpmscaler, short_desc, long_desc, edges, "
                "revolution FROM WheelPattern")
            self.tableWheel.setModel(self.modelWheel)
            # self.tableWheel.horizontalHeader().setStretchLastSection(True)
            self.modelWheel.setHeaderData(0, Qt.Horizontal, "id")
            self.modelWheel.setHeaderData(1, Qt.Horizontal, "Nome")
            self.modelWheel.setHeaderData(2, Qt.Horizontal, "Padrão")
            self.modelWheel.setHeaderData(3, Qt.Horizontal, "Dentes")
            self.modelWheel.setHeaderData(4, Qt.Horizontal, "Escala")
            self.modelWheel.setHeaderData(5, Qt.Horizontal, "Desc. Curta")
            self.modelWheel.setHeaderData(6, Qt.Horizontal, "Desc. Longa")
            self.modelWheel.setHeaderData(7, Qt.Horizontal, "Edges")
            self.modelWheel.setHeaderData(8, Qt.Horizontal, "Voltas")
            self.tableWheel.hideColumn(0)
            self.tableWheel.hideColumn(2)
            self.tableWheel.hideColumn(4)
            self.tableWheel.hideColumn(7)
            self.tableWheel.hideColumn(8)
            self.tableWheel.setColumnWidth(0, 10)
            self.tableWheel.setColumnWidth(1, 160)
            self.tableWheel.setColumnWidth(2, 80)
            self.tableWheel.setColumnWidth(3, 15)
            self.tableWheel.setColumnWidth(4, 15)
            self.tableWheel.setColumnWidth(5, 160)
            self.tableWheel.setColumnWidth(6, 450)
            self.tableWheel.setColumnWidth(7, 40)
            self.tableWheel.setColumnWidth(8, 40)
            record = self.modelWheel.record(0)
            self.lineEdit_name.setText(record.value("name"))
            self.lineEdit_scaler.setText(str(record.value("rpmScaler")))
            self.lineEdit_dentes.setText(str(record.value("teeth")))
            self.textEdit_pattern.setText(record.value("pattern"))
            if record.value("revolution") == 1:
                self.rb_1rev.setChecked(True)
            else:
                self.rb_2rev.setChecked(True)
            self.lineEdit_desc_curta.setText(record.value("short_desc"))
            self.lineEdit_desc_longa.setText(record.value("long_desc"))
            self.lineEdit_edges.setText(str(record.value("edges")))
        except Exception as e:
            if self.debug:
                logger.info("Error initializedModelWheel " + str(e))
            # logger.info("Connected " + str(dig))

    def initializedModelChoose(self):
        # self.model.setTable("WheelPattern")
        # self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        # self.model.select()
        self.modelChoose.setQuery("SELECT  * FROM WheelPattern ")
        self.tableChoose.setModel(self.modelChoose)
        # self.tableWheel.horizontalHeader().setStretchLastSection(True)
        self.modelChoose.setHeaderData(0, Qt.Horizontal, "id")
        self.modelChoose.setHeaderData(1, Qt.Horizontal, "Nome")
        self.modelChoose.setHeaderData(2, Qt.Horizontal, "Padrão")
        self.modelChoose.setHeaderData(3, Qt.Horizontal, "Dentes")
        self.modelChoose.setHeaderData(4, Qt.Horizontal, "Escala")
        self.modelChoose.setHeaderData(5, Qt.Horizontal, "Desc. Curta")
        self.modelChoose.setHeaderData(6, Qt.Horizontal, "Desc. Longa")
        self.modelChoose.setHeaderData(7, Qt.Horizontal, "teeth")
        self.modelChoose.setHeaderData(8, Qt.Horizontal, "revolution")
        self.tableChoose.hideColumn(0)
        self.tableChoose.hideColumn(2)
        self.tableChoose.hideColumn(3)
        self.tableChoose.hideColumn(4)
        self.tableChoose.hideColumn(6)
        self.tableChoose.hideColumn(7)
        self.tableChoose.hideColumn(8)
        self.tableChoose.setColumnWidth(0, 10)
        self.tableChoose.setColumnWidth(1, 400)
        self.tableChoose.setColumnWidth(2, 1)
        self.tableChoose.setColumnWidth(3, 1)
        self.tableChoose.setColumnWidth(4, 1)
        self.tableChoose.setColumnWidth(5, 400)
        self.tableChoose.setColumnWidth(6, 1)
        self.tableChoose.setColumnWidth(7, 1)
        self.tableChoose.setColumnWidth(8, 1)

    def tableWheel_clicked(self):
        tableWheel_clicked_db(window)

    def tableChoose_clicked(self):
        if self.conected:
            tableChoose_clicked_db(window)
            record = self.modelChoose.record(self.tableChoose.currentIndex().row())
            name_pattern = record.value("name")
            self.lbl_to_send.setText(name_pattern)
            self.btn_nw_send.setEnabled(True)

    def btnw_edit_clicked(self):
        # self.line_gen_edges.textChanged.connect(self.line_gen_edges_changed)
        btnw_edit(window)

    def btnw_update_clicked(self):
        btnw_save(window)

    def btnw_cancel_clicked(self):
        btnw_cancel(window)

    def btnw_new_clicked(self):
        btnw_new(window)

    def btn_cp_pattern_clicked(self):
        cp_pattern(window)

    def btnw_delete_clicked(self):
        btnw_delete(window)

    def btn_new_rpm_clicked(self):
        # self.send_txt = 'nw'
        self.next_rpm = int(self.line_new_rpm.text());
        if (self.next_rpm < 1000):
            send_rpm = "rpm00" + str(self.next_rpm) + "#"
        elif (self.next_rpm >= 1000) and (self.next_rpm < 10000):
            send_rpm = "rpm0" + str(self.next_rpm) + "#"
        else:
            send_rpm = "rpm" + str(self.next_rpm) + "#"
        self.append_text_ptd_datetime("new rpm: " + send_rpm)
        self.lcdRpm.display(str(self.next_rpm));
        btn_send(window, self.ser, send_rpm)
        # self.append_text_ptd_datetime("new rpm 2: " + ret_txt)

    # def btn_nw(self):
    #     send_txt = 'nw'
    #     self.next_rpm = 80;
    #     send_rpm = "rpm00" + str(self.next_rpm) + "#"
    #     self.lcdRpm.display(str(self.next_rpm));
    #     send_patern(window, self.ser, send_txt)




    # def btn_nw1(self):
    #     send_txt = 'nw'
    #     self.next_rpm = 150;
    #     self.lcdRpm.display(str(self.next_rpm));
    #     ret_txt = send_patern1(window, self.ser, send_txt)

    def btn_send_clicked(self):
        if self.debug:
            logger.info('btn send')
        try:
            send_txt = self.lineEdit.text()
            btn_send(window, self.ser, send_txt)

        except Exception as e:
            if self.debug:
                logger.info("Error connecting ")
                logger.info(str(e))
            self.append_text_ptd_datetime("Sending Error")
            self.append_text_ptd_datetime(str(e))



    def list_ports(self):
        serial_list_ports(window)

    def show_file_dialog(self):
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            f = open(fname[0], 'rb')
            self.lbl_file.setText(fname[0])
            with f:
                data = f.read()
                self.plainTextEdit.clear()
                gen = dump_gen(data)
                for line in gen:
                    #print(line)
                    self.plainTextEdit.appendPlainText(line)





    def cb001_t_clicked(self):
        cb000_t_clicked(window, 0, 1)

    def cb002_t_clicked(self):
        cb000_t_clicked(window, 0, 2)

    def cb003_t_clicked(self):
        cb000_t_clicked(window, 0, 3)

    def cb004_t_clicked(self):
        cb000_t_clicked(window, 0, 4)



    def cb011_t_clicked(self):
        cb000_t_clicked(window, 1, 1)

    def cb012_t_clicked(self):
        cb000_t_clicked(window, 1, 2)

    def cb013_t_clicked(self):
        cb000_t_clicked(window, 1, 3)

    def cb014_t_clicked(self):
        cb000_t_clicked(window, 1, 4)



    def append_text_ptd_datetime(self, pText):
        self.plainTextEdit_debug.appendPlainText(
            datetime.now().strftime('%d-%m-%Y %H:%M:%S') + " --> " + pText)

# def time_thread(self):
#     timer: object = QTimer()
#     timer.timeout.connect(MainWindow.show_time)
#     timer.start(1000)
#     MainWindow.show_time(self)


app = QtWidgets.QApplication(sys.argv)
# available_styles()
style_string = get_style("dark_blue")
app.setStyleSheet(style_string)
window = MainWindow()
window.show()
app.exec()


