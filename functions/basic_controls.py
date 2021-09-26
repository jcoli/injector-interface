"""
Version: 0a
Tecnocoli - @07/2020
Author: Jeferson Coli - jcoli@tecnocoli.com.br
SPEED SENSOR SIMULATOR - camshafts and crankshafts - Arduino Uno/Nano
Function basic_controls
"""

from datetime import datetime
import serial
import time
from time import sleep
import hashlib


import logging
from serial.tools.list_ports import comports
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
text_date = datetime.now().strftime('%d-%m-%Y')
scanner_file = 'injector-' + text_date+'.log'
handler = logging.FileHandler(scanner_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def btn_send(input, ser, send_txt):
    # logger.info('btn_send')
    try:
        txt_send = str.encode(send_txt + '#')
        # if input.debug:
        #     logger.info("btn send:" + str(txt_send))
        input.ser.write(txt_send)
        time.sleep(0.2)

    except Exception as e:
        if input.debug:
            logger.info("Error connecting btn send:" + str(e))
        input.append_text_ptd_datetime("Sending Error")
        input.append_text_ptd_datetime(str(e))


def btn_connect(input, port, ser, prog_id):
    if input.debug:
        logger.info('btn_connect')
    try:
        # if input.debug:
        #     logger.info("Connecting 3")
        input.ser = serial.Serial(port[0], 115200, timeout=2)
        input.ser.write(b'id#')
        time.sleep(0.5)
        input.value_serial = input.ser.readline()
        if input.debug:
            logger.info("Connecting 3 " + str(input.value_serial))
        input.prog_id = str(input.value_serial).split(",")
        input.hash_id = hashlib.md5(input.prog_id[3].encode())  # hashMD5 UniqueId
        hex_dig = input.hash_id.hexdigest()
        dig = input.hash_id.digest()
        if input.debug:
            logger.info(str(input.value_serial))  # Nome
            logger.info(input.prog_id[0])  # Nome
            logger.info(input.prog_id[1])  # versão
            logger.info(input.prog_id[2])  # tipo
            logger.info(input.prog_id[3])  # UniqueId
            logger.info("Licenciado para: " + input.prog_id[4])  # Owner
            logger.info("Licença: " + input.prog_id[5])  # License
            logger.info("Nome: " + input.prog_id[6])  # License
            logger.info("Descrição: " + input.prog_id[7])  # License
            logger.info(str(hex_dig))
            logger.info(str(dig))
        if "injector" in input.prog_id[2]:
            if input.debug:
                logger.info("injector")
            input.hash_id = hashlib.md5(input.prog_id[3].encode())  # hashMD5 UniqueId
            hex_dig = input.hash_id.hexdigest()
            input.append_text_ptd_datetime(str(hex_dig))
            dig = input.hash_id.digest()
            input.append_text_ptd_datetime(str(dig))
            input.conected = True
            # input.status_bar.setStyleSheet("background-color: rgb(112, 159, 252); color: rgb(0, 0, 0);")
            input.status_bar.setStyleSheet("background-color: rgb(0, 150, 255); color: rgb(0, 0, 0);")
            input.status_bar.clearMessage()
            input.status_bar.showMessage('Injetor Conectado Versão: ' + input.prog_id[1] + ' - ' + input.prog_id[4])
            input.label_led_connected_2.show()
            input.lbl_onda_nome.setText(input.prog_id[6])
            input.lbl_onda_desc.setText(input.prog_id[7])
            input.ser.write(b'id#')

            return "ok"
        else:
            input.status_bar.setStyleSheet("background-color: rgb(255,69,0); color: rgb(0, 0, 0);")
            input.status_bar.clearMessage()
            input.status_bar.showMessage('Injetor não encontrado: ')
            # input.led_conn_simu_2.show()
            input.ser.write(b'id#')
            return "not ok"
    except Exception as e:
        if input.debug:
            logger.info("Error connecting btn connect: " + str(e))
        input.status_bar.setStyleSheet("background-color: rgb(246, 11, 11); color: rgb(0, 0, 0);")
        input.status_bar.showMessage('Connection Error')
        return "notok"

def send_patern(input, ser, send_txt):
    wheel_patern = ",1,0,1,0,1,0,1,0,1,0,1,0,1," \
                   "0,1,0,1,0,1,0,1,0,1,0,1,0," \
                   "1,0,1,0,1,0,1,0,1,0,1,0,1," \
                   "0,1,0,1,0,1,0,1,0,1,3,1,3,"

    send_patern = "nw053" + wheel_patern + "#"
    # input.append_text_ptd_datetime("new wheel: " + send_patern)
    btn_send(input, ser, send_patern)


def send_patern1(input, ser, send_txt):
    record = input.modelChoose.record(input.tableChoose.currentIndex().row())
    name_pattern = record.value("name")
    short_pattern = record.value("short_desc")
    wheel_patern = record.value("pattern")
    if (record.value("edges")>98):
        edges = str(record.value("edges")+1)
    else:
        edges = "0"+str(record.value("edges")+1)
    send_patern = "nw" + edges + "," + wheel_patern + "#"
    if input.debug:
        logger.info("New Pattern: "+ send_patern)
    btn_send(input, ser, send_patern)
    tdelay = record.value("edges")/32
    time.sleep(tdelay)
    pat_names = "pn,"+name_pattern+","+short_pattern+","
    input.lbl_onda_nome.setText(name_pattern)
    input.lbl_onda_desc.setText(short_pattern)
    if input.debug:
        logger.info("New Pattern: " + pat_names)
    btn_send(input, ser, pat_names)
