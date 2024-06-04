import machine
import dht
import ssd1306
import time

# Configuración del I2C para la pantalla OLED
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Configuración del pin del sensor DHT22
sensor = dht.DHT22(machine.Pin(15))

def display_text(oled, temp, hum):
    oled.fill(0)  # Limpia la pantalla
    oled.text('Temp: {} C'.format(temp), 0, 0)
    oled.text('Humedad: {} %'.format(hum), 0, 10)
    oled.show()  # Actualiza la pantalla

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        display_text(oled, temp, hum)
    except OSError as e:
        print('Error al leer el sensor:', e)
    
    time.sleep(2)
