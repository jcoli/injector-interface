"""
Version: 0a
Tecnocoli - @09/2021
Author: Jeferson Coli - jcoli@tecnocoli.com.br
SPEED SENSOR SIMULATOR - camshafts and crankshafts - Arduino Uno/Nano
Function up firmmare
"""

from PyQt5 import QtCore
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from functions.conn_serial import scan_serial
import serial
import serial.tools.list_ports
import logging
import string
import glob
import sys
import time
import os
import subprocess
from serial.tools.list_ports import comports
from datetime import datetime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# text_date = datetime.now().strftime('%d-%m-%Y')
text_date = datetime.now().strftime('%d-%m-%Y')
scanner_file = 'injector-' + text_date+'.log'
handler = logging.FileHandler(scanner_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def upload_firmware(window):
    if not window.conected:
        try:
            # avrdude - C avrdude.conf - v - patmega2560 - cwiring - PCOM14 - b115200 - D - Uflash: w:firmware.hex
            port = scan_serial(window)
            logger.info("Firmware " + port[0])
            upload_text = 'forms/firmware.bat '
            upload_text += port[0]
            upload_text += 'forms/firmware.hex'
            # arguments = [port[0], 'firmware.hex']
            upload_text = 'forms/avrdude -C forms/avrdude.conf -v -patmega2560 -cwiring -P'
            upload_text += port[0]
            upload_text += ' -b115200 -D -Uflash:w:forms/firmware.hex'

            logger.info("Firmware 2 " + upload_text)
            res = QtCore.QProcess.startDetached(upload_text)
            # # p = QProcess()
            # p.finished.connect(process_finished)
            # p.readyReadStandardError.connect(handle_stderr)
            # logger.info("Firmware 2a")
            # # p.startDetached("firmware.bat", arguments)
            # procStarted = p.waitForStarted(500)
            # if procStarted:
            #     finished = p.waitForFinished(10000)
            #     if finished and p.exitCode() == 0:
            #         logger.info("Firmware 2g")
            #     else:
            #         logger.info("Firmware 2h")
            # res = True
            time.sleep(15)
            logger.info("Firmware 3 " + upload_text)
            # p = subprocess.Popen([upload_text], stdout=subprocess.PIPE)
            # p.communicate()
            logger.info("Firmware 2b ")
            logger.info(res)
            if res:
                logger.info("Firmware 2 OK ")
                box = QtWidgets.QMessageBox()
                box.setIcon(QtWidgets.QMessageBox.Critical)
                box.setWindowTitle('Upload')
                box.setText('Upload de Firmware Concluido!')
                box.setStandardButtons(QtWidgets.QMessageBox.Ok)
                box.exec_()
            else:
                logger.info("Firmware 2 NOT OK ")
                box = QtWidgets.QMessageBox()
                box.setIcon(QtWidgets.QMessageBox.Critical)
                box.setWindowTitle('Upload de Firmware')
                box.setText('Upload de Firmware Não Realizado')
                box.setStandardButtons(QtWidgets.QMessageBox.Ok)
                box.exec_()
            logger.info("Firmware 2")
        except Exception as e:
            box = QtWidgets.QMessageBox()
            box.setIcon(QtWidgets.QMessageBox.Critical)
            box.setWindowTitle('Upload de Firmware')
            box.setText('Upload de Firmware Não Realizado' + str(e))
            box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            box.exec_()
            if window.debug:
                logger.info("Error Firmware " + str(e))


def process_finished(self):
    logger.info("Firmware 2 OK ")
    box = QtWidgets.QMessageBox()
    box.setIcon(QtWidgets.QMessageBox.Critical)
    box.setWindowTitle('Upload')
    box.setText('Upload de Firmware Concluido!')
    box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    box.exec_()


def handle_stderr(self):
    data = self.p.readAllStandardError()
    stderr = bytes(data).decode("utf8")
    logger.info("Error Firmware " + stderr)
    self.message(stderr)