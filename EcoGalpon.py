import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_ds1307
import adafruit_dht
from adafruit_st7735r import ST7735R  # Asegúrate de tener la librería correcta
from hx711 import HX711
from adafruit_display_text import label
import displayio
import terminalio

# Configuración de pines para HX711
DT_PIN = board.GP2
SCK_PIN = board.GP3

# Inicializar I2C
i2c = busio.I2C(board.GP1, board.GP0)

# Inicializar DS1307
rtc = adafruit_ds1307.DS1307(i2c)

# Inicializar DHT22
dht_device = adafruit_dht.DHT22(board.GP4)

# Configurar pantalla ST7735
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
tft_cs = DigitalInOut(board.GP13)
tft_dc = DigitalInOut(board.GP14)
tft_rst = DigitalInOut(board.GP15)
tft = ST7735R(spi, cs=tft_cs, dc=tft_dc, rst=tft_rst)

# Configurar LED para el sistema de calefacción
led_calefaccion = DigitalInOut(board.GP16)
led_calefaccion.direction = Direction.OUTPUT

# Inicializar HX711
hx = HX711(dout_pin=DT_PIN, pd_sck_pin=SCK_PIN)
hx.set_scale_ratio(2280)  # Calibrar según tu celda de carga

# Configurar LED para el auto llenado del comedero
led_auto_llenado = DigitalInOut(board.GP17)
led_auto_llenado.direction = Direction.OUTPUT

# Umbrales
TEMPERATURE_THRESHOLD = 20.0
WEIGHT_THRESHOLD = 100

def get_weight():
    return hx.get_weight_mean(5)

def show_info():
    group = displayio.Group()
    t = rtc.datetime
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
    except RuntimeError as error:
        # Errores comunes al leer el sensor DHT22
        print(error)
        temperature = None
        humidity = None

    time_text = "{:02}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec)
    time_label = label.Label(terminalio.FONT, text=time_text, color=0xFFFFFF, x=10, y=10)
    group.append(time_label)

    if temperature is not None:
        temp_text = "Temp: {:.1f}C".format(temperature)
        temp_label = label.Label(terminalio.FONT, text=temp_text, color=0xFFFFFF, x=10, y=30)
        group.append(temp_label)

    if humidity is not None:
        hum_text = "Hum: {:.1f}%".format(humidity)
        hum_label = label.Label(terminalio.FONT, text=hum_text, color=0xFFFFFF, x=10, y=50)
        group.append(hum_label)

    tft.show(group)

def control_temperature():
    try:
        temperature = dht_device.temperature
    except RuntimeError as error:
        print(error)
        temperature = None

    if temperature is not None:
        led_calefaccion.value = temperature < TEMPERATURE_THRESHOLD

def control_auto_llenado(weight):
    led_auto_llenado.value = weight < WEIGHT_THRESHOLD

while True:
    weight = get_weight()
    show_info()
    control_temperature()
    control_auto_llenado(weight)
    print(f'Peso: {weight} gramos')
    time.sleep(1)
