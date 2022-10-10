import os
import qrcode

def print_label(id):
    img = qrcode.make(id)

    qr_file_name = "/Users/leonardokokot/dev/pilana_proj/web/some_file_{}.jpg".format(id)
    img.save(qr_file_name)

    #send image to printer
    os.system("lpr -P YOUR_PRINTER {}".format(qr_file_name))

    #delete image
    # os.remove(qr_file_name)