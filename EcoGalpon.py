from machine import Pin
import time
from hx711 import HX711
import dht
import ssd1306

# Configuración del I2C y OLED con SCL en GP1 y SDA en GP0
i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Configuración del sensor DHT22 y del relé para ventilación
sensor = dht.DHT22(machine.Pin(15))
ventilation_relay = machine.Pin(16, machine.Pin.OUT)
water_level_sensor = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
water_refill_relay = machine.Pin(17, machine.Pin.OUT)

# Configuración del sensor de peso HX711
clock = Pin(4, Pin.OUT)  # Pin del reloj (SCK)
data = Pin(3, Pin.IN)    # Pin de datos (DT)

hx711 = HX711(clock, data)

# Establecer la tara y calibrar el sensor HX711
hx711.tare()
scale_factor = 214.0267  # Factor de escala ajustado
hx711.set_scale(scale_factor)

# Configuración del relé para el autollenado del comedero
feeder_refill_relay = machine.Pin(18, machine.Pin.OUT)

def control_ventilation(temp):
    if temp > 33:  # Umbral de temperatura para activar el ventilador
        ventilation_relay.value(1)  # Activa el relé (y el ventilador)
    else:
        ventilation_relay.value(0)  # Desactiva el relé (y el ventilador)

def control_water_refill(water_present):
    if water_present:  # Si la señal indica que no hay agua (lógica invertida)
        water_refill_relay.value(1)  # Activa el relé para rellenar
    else:
        water_refill_relay.value(0)  # Desactiva el relé cuando hay agua

def control_feeder_refill(weight):
    if weight < 450:  # Umbral de peso para activar el relleno del comedero (ajusta según sea necesario)
        feeder_refill_relay.value(1)  # Activa el relé para rellenar el comedero
    else:
        feeder_refill_relay.value(0)  # Desactiva el relé cuando el comedero tiene suficiente comida

def display_text(temp, hum, water_present, weight):
    oled.fill(0)
    oled.text('Temp: {} C'.format(temp), 0, 0)
    oled.text('Hum: {} %'.format(hum), 0, 10)
    oled.text('Water: {}'.format('Yes' if water_present else 'No'), 0, 20)
    oled.text('Weight: {} g'.format(weight), 0, 30)
    oled.show()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        water_present = water_level_sensor.value()  # Leer el estado del agua (lógica invertida)
        
        # Obtener el peso sin promedio para mayor velocidad
        weight = hx711.get_units()  # Obtener el peso
        
        control_ventilation(temp)
        control_water_refill(water_present)
        control_feeder_refill(weight)
        display_text(temp, hum, water_present, weight)
    except OSError as e:
        print('Error al leer los sensores:', e)
    time.sleep(0.5)  # Reducir el tiempo de espera entre lecturas

