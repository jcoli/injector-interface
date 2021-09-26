"""
Version: 0a
Tecnocoli - @07/2020
Author: Jeferson Coli - jcoli@tecnocoli.com.br
SPEED SENSOR SIMULATOR - camshafts and crankshafts - Arduino Uno/Nano
Function conn_serial
"""

import serial
import serial.tools.list_ports
import errno
import string
import glob
import sys
import time
from datetime import datetime
import hashlib
from PyQt5.QtCore import *
from datetime import datetime
import logging
from serial.tools.list_ports import comports
from functions.basic_controls import btn_send
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


def scan_serial(input):
    """scan for available ports. return a list of serial names"""
    if input.debug:
        logger.info('Scan Serial')
    try:
        """    
        ports = list(serial.tools.list_ports.comports())
        i = 0
        for port_no, description, address in ports:
            logger.info('port_no '+port_no)
            logger.info('description ' + description)
            logger.info('address ' + address)
            if 'Arduino Due Prog' in description:
                logger.info('this is Arduino Due ' + address)
        """
        com_ports_list = list(comports())
        ard_port = None
        # For Arduino Mega
        for port in com_ports_list:
            if input.debug:
                logger.info('list ports ' + port[1] + ' - ' + port[0] + ' - ' + port[2])
            if port[1].startswith("QinHeng Electronics HL-340"):
                ard_port = port  # Success; Arduino Due found by name match.
                if input.debug:
                    logger.info('port_no 2 ' + port[1] + ' - ' + port[0])
                break  # stop searching-- we are done.
        if ard_port is None:
            for port in com_ports_list:
                if port[2].startswith("USB VID:PID=1A86:7523"):
                    if input.debug:
                        logger.info('port_no 3 ' + port[0])
                    ser = serial.Serial(port[0], 115200, timeout=2)
                    ser.write(b'id#')
                    time.sleep(0.3)
                    value_serial = ser.readline()
                    if input.debug:
                        logger.info('port_no 4 ' + str(value_serial))
                    prog_id = str(value_serial).split(",")
                    if len(value_serial) > 0:
                        if "injector" in prog_id[2]:
                            ard_port = port  # Success; Arduino Due found by VID/PID match.
                            break  # stop searching-- we are done.
        return ard_port

    except Exception as e:
        if input.debug:
            logger.info("Error scan_serial " + str(e))
        # logger.info("Connected " + str(dig))
        return ard_port



def try_port(portStr):
    """returns boolean for port availability"""
    """test if has arduino due in port"""
    try:
        s = serial.Serial(portStr)
        s.close() # explicit close 'cause of delayed GC in java
        return True

    except serial.SerialException:
        pass
    except OSError as e:
        if e.errno != errno.ENOENT: # permit "no such file or directory" errors
            raise e

    return False


def serial_list_ports(input):
    if input.debug:
        logger.info('list_ports')


def serial_read_events(input, value_serial):
    if input.debug:
        if "live" not in str(value_serial):
            logger.info(str("serial_read_events: " + str(value_serial)))
    # input.append_text_ptd_datetime(str("serial_read_events: " + str(value_serial)))
    try:
        if "live" in str(value_serial) and input.conected:
            ret_txt = str(input.value_serial).split(",")
            input.bit_alive = True
            send_txt = 'live'
            btn_send(input, input.ser, send_txt)

            # input.append_text_ptd_datetime("ALIVE")
        if "Simulator" in str(value_serial) and not input.conected:
            if input.debug:
                logger.info('serial_read Injetor')
                logger.info(input.prog_id[0])  # Nome
                logger.info(input.prog_id[1])  # versão
                logger.info(input.prog_id[2])  # tipo
                logger.info(input.prog_id[3])  # UniqueId
                logger.info("Licenciado para: " + input.prog_id[4])  # Owner
                logger.info("Licença: " + input.prog_id[5])  # License
            input.prog_id = str(input.value_serial).split(",")
            input.hash_id = hashlib.md5(input.prog_id[3].encode())  # hashMD5 UniqueId
            hex_dig = input.hash_id.hexdigest()
            # logger.infostr(hex_dig)
            dig = input.hash_id.digest()
            # logger.info(str(dig))
            input.conected = True
            # logger.info('Injetor conectado, versão ' + input.prog_id[1])
            input.status_bar.setStyleSheet("background-color: rgb(112, 159, 252); color: rgb(0, 0, 0);")
            input.status_bar.clearMessage()
            input.status_bar.showMessage('Injetor Conectado Versão: ' + input.prog_id[1] + ' - ' + input.prog_id[4])
            input.label_led_connected_2.show()
            input.ser.write(b'id#')
            if input.debug:
                logger.info("Connecting ok ")
            input.btnStopGo.setEnabled(True)
            input.lcdRpm.display(str(input.next_rpm))
            time.sleep(0.5)
            input.append_text_ptd_datetime("ok 2")
            input.thread_flag = 'go'

        if "pa" in str(value_serial):
            ret_txt = str(input.value_serial).split(",")
            if "go" in ret_txt[1]:
                input.stopGo = True
                input.btn_new_rpm.setEnabled(True)
                input.btnStopGo.setText("Parar")
                input.label_led_stop.show()
                input.append_text_ptd_datetime("receive go: ")
                input.send_rpm = "rpm00050#"
            else:
                input.stopGo = False
                input.btnStopGo.setText("Acionar")
                input.btn_new_rpm.setEnabled(False)
                input.label_led_stop.hide()
                input.append_text_ptd_datetime("receive stop: ")

        if "rpm" in str(value_serial):
            ret_txt = str(input.value_serial).split(",")
            input.append_text_ptd_datetime("rpm")
            input.next_rpm = int(ret_txt[1])
            input.lcdRpm.display(str(input.next_rpm))
            input.line_new_rpm.setText(str(input.next_rpm))
        
        if "simconn" in str(value_serial):
            if input.debug:
                logger.info("simconn aqui"+str(value_serial))
            ret_txt = str(input.value_serial).split(",")
            if input.debug:
                logger.info("simconn aqui "+str(ret_txt))
            if "1" in ret_txt[1]:
                input.conected = False
                input.simu_conn = True
                input.thread_flag = 'paused'
                input.bit_alive = False
                input.btnConnect.setText("Bloqueado")
                input.btnConnect.setEnabled(False)
                if input.debug:
                    logger.info("Desconnecting")
                input.status_bar.setStyleSheet("background-color: rgb(244, 255, 16); color: rgb(0, 0, 0);")
                input.status_bar.showMessage('Simulador Conectado')
                input.label_led_equip_2.hide()
                input.label_led_connected_2.hide()
                input.btnStopGo.setEnabled(False)
                input.btn_new_rpm.setEnabled(False)
                input.stopGo = False
                input.btnStopGo.setText("Acionar")
                input.label_led_stop.hide()
            # else:
                input.simu_conn = False
                input.btnConnect.setText("Conectar")
                input.btnConnect.setEnabled(False)


    except Exception as e:
        if input.debug:
            logger.info("Error serial_read_events " + str(e))
        # input.append_text_ptp_datetime("Connection Error " + str(e))
        # input.status_bar.setStyleSheet("background-color: rgb(246, 11, 11);")
        # input.status_bar.showMessage('Connection Error Thread')