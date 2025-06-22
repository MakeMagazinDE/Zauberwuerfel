# SR Apr25
# Setup matrix display, following https://max7219.readthedocs.io/

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
#from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
from luma.core.render import canvas

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=12, block_orientation=90, rotate=0, blocks_arranged_in_reverse_order=True, persist=True)

def showMessage(msg="Welcome!"):
    print("["+msg+"]")
    with canvas(device) as draw:
        text(draw, (0,0), msg, fill="white")

