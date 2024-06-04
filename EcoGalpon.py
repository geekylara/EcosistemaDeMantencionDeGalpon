import machine
import dht
import ssd1306
import time

# Configuración del I2C y OLED con SCL en GP1 y SDA en GP0
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Configuración del sensor DHT22 y del relé para ventilación
sensor = dht.DHT22(machine.Pin(15))
ventilation_relay = machine.Pin(16, machine.Pin.OUT)

# Configuración del sensor de nivel de agua utilizando el pin D0
water_level_sensor = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Configuración del relé para el relleno de agua
water_refill_relay = machine.Pin(17, machine.Pin.OUT)  # Asumiendo que el pin GP17 está disponible para usar

def control_ventilation(temp):
    if temp > 30:  # Umbral de temperatura para activar el ventilador
        ventilation_relay.value(1)  # Activa el relé (y el ventilador)
    else:
        ventilation_relay.value(0)  # Desactiva el relé (y el ventilador)

def control_water_refill(water_present):
    if water_present:  # Si la señal indica que no hay agua (lógica invertida)
        water_refill_relay.value(1)  # Activa el relé para rellenar
    else:
        water_refill_relay.value(0)  # Desactiva el relé cuando hay agua

def display_text(temp, hum, water_present):
    oled.fill(0)
    oled.text('Temp: {} C'.format(temp), 0, 0)
    oled.text('Hum: {} %'.format(hum), 0, 10)
    oled.text('Water: {}'.format('No' if water_present else 'Yes'), 0, 20)
    oled.text('Vent: {}'.format('ON' if ventilation_relay.value() else 'OFF'), 0, 30)
    oled.show()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        water_present = water_level_sensor.value()  # Leer el estado del agua (lógica invertida)
        control_ventilation(temp)
        control_water_refill(water_present)
        display_text(temp, hum, water_present)
    except OSError as e:
        print('Error reading sensors:', e)
    time.sleep(2)
