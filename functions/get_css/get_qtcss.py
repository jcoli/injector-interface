import os
import traceback
import importlib
import imp

from PyQt5.QtCore import QFile, QTextStream
import logging
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
debug = True


def available_styles():

    styles = []
    package_dir = os.path.dirname(os.path.abspath(__file__))
    print(package_dir)
    for style_file in os.listdir(package_dir):
        if style_file.endswith(".py") and not style_file.startswith("__"):
            style_module = os.path.splitext(style_file)[0]
            try:
                imp.find_module(style_module, [package_dir])
                is_ok = True
            except ImportError:
                is_ok = False
            if is_ok:
                styles.append(style_module)

    return styles


def get_style(style_sheet):

    if debug:
        logger.info('css 1')
    try:
        #mod = importlib.import_module("." + style_sheet, __name__)
        #hasattr(mod, "qt_resource_name")
        f = QFile("forms/css/%s/style.qss" % style_sheet)
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
    except ImportError as e:
        logger.info("Style sheet not available. Use available_styles() to check for valid styles")
        return u""
    except Exception as e:
        logger.info("Style sheet available, but an error occured...")
        #traceback.print_exc()
        return u""

    return stylesheet