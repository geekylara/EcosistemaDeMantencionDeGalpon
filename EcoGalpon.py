import machine
import dht
import ssd1306
import time

# Configuración del I2C y OLED con SCL en GP1 y SDA en GP0
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Configuración del sensor DHT22 y del relé
sensor = dht.DHT22(machine.Pin(15))
relay = machine.Pin(16, machine.Pin.OUT)

def control_ventilation(temp):
    if temp > 30:  # Umbral de temperatura para activar el ventilador
        relay.value(1)  # Activa el relé (y el ventilador)
    else:
        relay.value(0)  # Desactiva el relé (y el ventilador)

def display_text(temp, hum):
    oled.fill(0)
    oled.text('Temp: {} C'.format(temp), 0, 0)
    oled.text('Hum: {} %'.format(hum), 0, 10)
    oled.text('Vent: {}'.format('ON' if relay.value() else 'OFF'), 0, 20)
    oled.show()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        control_ventilation(temp)
        display_text(temp, hum)
    except OSError as e:
        print('Error reading sensor:', e)
    time.sleep(2)
