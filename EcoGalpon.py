# Librerías
from machine import Pin, I2C, PWM
import dht
import ssd1306
import time
from hx711 import HX711

# Configuración del I2C y OLED con SCL en GP1 y SDA en GP0
i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # Inicializa el bus I2C en los pines 1 (SCL) y 0 (SDA)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # Inicializa la pantalla OLED de 128x32 píxeles

# Mostrar el nombre del proyecto al iniciar
oled.fill(0)  # Limpia la pantalla OLED
oled.text('Proyecto', 0, 0)  # Muestra "Proyecto" en la pantalla OLED
oled.text('Galpon Autom.', 0, 15)  # Muestra "Galpon Autom." en la pantalla OLED
oled.show()  # Actualiza la pantalla OLED
time.sleep(3)  # Pausa de 3 segundos para que el usuario vea el mensaje

# Configuración de los sensores y actuadores
sensor_interior_id = "Sensor Interior"
sensor_interior = dht.DHT22(Pin(15))  # Configura el sensor DHT22 en el pin 15 para leer temperatura y humedad interior
ventilation_relay = Pin(17, Pin.OUT)  # Configura el pin 17 como salida para el relé de ventilación
water_level_sensor_id = "Sensor Nivel Agua"
water_level_sensor = Pin(2, Pin.IN, Pin.PULL_DOWN)  # Configura el pin 2 como entrada para el sensor de nivel de agua
water_refill_relay = Pin(18, Pin.OUT)  # Configura el pin 18 como salida para el relé de la bomba de agua

# Configuración del sensor de peso HX711
hx711_id = "Sensor Peso"
clock = Pin(4, Pin.OUT)  # Configura el pin 4 como salida para el reloj del HX711
data = Pin(3, Pin.IN)  # Configura el pin 3 como entrada para los datos del HX711
hx711 = HX711(clock, data)  # Inicializa el sensor de peso HX711
hx711.tare()  # Tarea el sensor de peso (establece el punto cero)
scale_factor = 214.0267  # Define el factor de escala ajustado para el HX711
hx711.set_scale(scale_factor)  # Aplica el factor de escala al HX711

# Configuración del servomotor para el autollenado del comedero
servo = PWM(Pin(19))  # Configura el pin 19 para controlar el servomotor
servo.freq(50)  # Frecuencia de 50 Hz para el servomotor

# Configuración del buzzer para las alarmas
buzzer = Pin(20, Pin.OUT)  # Configura el pin 20 como salida para el buzzer de alarma

# Variables para la selección del animal
animal = 'Gallinas'  # Variable para almacenar el animal seleccionado
temp_setpoint = 30  # Setpoint de temperatura para gallinas
weight_setpoint = 450  # Setpoint de peso para gallinas

# Funciones
# Función para mostrar errores en la pantalla OLED y pausar el sistema
def display_error(sensor_id):
    reboot = Pin(12, Pin.IN, Pin.PULL_UP)  # Configura el pin 12 para el botón de reinicio
    error_displayed = False
    
    while True:
        oled.fill(0)  # Limpia la pantalla OLED
        if error_displayed:
            oled.text('Presione tercer', 0, 0)
            oled.text('boton para reiniciar', 0, 15)
        else:
            oled.text('Error al leer:', 0, 0)  # Muestra el mensaje de error
            oled.text(sensor_id, 0, 15)  # Muestra el ID del sensor con error
        oled.show()  # Actualiza la pantalla OLED
        
        if not reboot.value():  # Si el botón de reinicio es presionado
            break
        
        error_displayed = not error_displayed
        time.sleep(0.5)  # Pausa de 2 segundos para alternar el mensaje

# Función para leer un sensor con manejo de errores
def read_sensor(sensor, sensor_id, measure_func, read_func):
    try:
        measure_func()
        return read_func()
    except OSError:
        print(f'Error al leer el {sensor_id}')  # Imprime el error si falla la lectura del sensor
        display_error(sensor_id)  # Muestra el error en la pantalla OLED
        return None

# Función para mostrar texto en la pantalla OLED
def display_text(temp_interior, hum_interior, water_present, weight, alarm_message=""):
    oled.fill(0)  # Limpia la pantalla OLED
    oled.text('Temp In: {} C'.format(temp_interior), 0, 0)  # Muestra la temperatura interior
    oled.text('Water: {}'.format('Bajo' if water_present else 'lleno'), 0, 15)  # Muestra el estado del agua
    oled.text('Weight: {} g'.format(weight), 0, 25)  # Muestra el peso del comedero
    if alarm_message:
        oled.text(alarm_message, 0, 35)  # Muestra el mensaje de alarma
    oled.show()  # Actualiza la pantalla OLED

# Función para manejar el buzzer de alarma
def sound_alarm(water_alarm, food_alarm):
    if water_alarm and food_alarm:
        # Pitido largo intermitente si ambos (agua y comida) están bajos
        buzzer.value(1)
        time.sleep(1)
        buzzer.value(0)
        time.sleep(1)
        return "Niveles bajos"
    elif water_alarm:
        # Pitido intermitente para el nivel de agua bajo
        buzzer.value(1)
        time.sleep(0.1)
        buzzer.value(0)
        time.sleep(0.3)
        return "Nivel agua bajo"
    elif food_alarm:
        # Dos pitidos intermitentes para el nivel de comida bajo
        for _ in range(2):
            buzzer.value(1)
            time.sleep(0.2)
            buzzer.value(0)
            time.sleep(0.2)
        time.sleep(0.8)
        return "Nivel comida bajo"
    return ""

# Clase para la FSM del comedero
class ComederoFSM:
    def __init__(self):
        self.state = 'PESO_OK'  # Estado inicial del peso del comedero
        self.previous_weight = hx711.get_units()  # Almacena el peso anterior del comedero

    def transition(self, event):
        if self.state == 'PESO_OK' and event == 'PESO_BAJO':
            self.abrir_comedero()  # Transición a abrir el comedero
        elif self.state == 'RELLENO_ENCENDIDO' and event == 'PESO_OK':
            self.cerrar_comedero()  # Transición a cerrar el comedero
        elif self.state == 'RELLENO_ENCENDIDO' and event == 'PESO_SIGUE_BAJO':
            self.activar_alarma()  # Transición a activar la alarma
        elif self.state == 'ALARMA_COMEDERO' and event == 'PESO_OK':
            self.state = 'RELLENO_ENCENDIDO'  # Cambia el estado a relleno encendido

    def abrir_comedero(self):
        self.state = 'RELLENO_ENCENDIDO'  # Cambia el estado a relleno encendido
        servo.duty_u16(8200)  # Mueve el servomotor a 90 grados
        print("Comedero abierto")
        time.sleep(2)  # Mantiene el comedero abierto por 2 segundos

    def cerrar_comedero(self):
        if hx711.get_units() > weight_setpoint + 50:  # Umbral adicional para desactivar la alarma
            self.state = 'PESO_OK'  # Cambia el estado a peso OK
            servo.duty_u16(4100)  # Mueve el servomotor a 0 grados
            print("Comedero cerrado")

    def activar_alarma(self):
        self.state = 'ALARMA_COMEDERO'  # Cambia el estado a alarma del comedero
        print("Alarma del comedero activada")

# Inicialización de la máquina de estado finito del comedero
comedero_fsm = ComederoFSM()  # Inicializa la FSM del comedero

# Bucle principal
while True:
    temp_interior = read_sensor(sensor_interior, sensor_interior_id, sensor_interior.measure, sensor_interior.temperature)
    hum_interior = read_sensor(sensor_interior, sensor_interior_id, sensor_interior.measure, sensor_interior.humidity)
    water_present = read_sensor(water_level_sensor, water_level_sensor_id, lambda: None, water_level_sensor.value)
    weight = read_sensor(hx711, hx711_id, lambda: None, hx711.get_units)
    
    if None in [temp_interior, hum_interior, water_present, weight]:
        continue  # Si alguno de los sensores falla, omite el ciclo actual y vuelve a intentar

    if weight < weight_setpoint:
        comedero_fsm.transition('PESO_BAJO')  # Transición a peso bajo del comedero
    else:
        comedero_fsm.transition('PESO_OK')  # Transición a peso OK del comedero
    
    if comedero_fsm.state == 'RELLENO_ENCENDIDO' and weight <= comedero_fsm.previous_weight:
        comedero_fsm.transition('PESO_SIGUE_BAJO')  # Transición a activar alarma del comedero
    
    # Manejo del buzzer de alarma
    water_alarm = water_present
    food_alarm = comedero_fsm.state == 'ALARMA_COMEDERO'
    alarm_message = sound_alarm(water_alarm, food_alarm)
    
    display_text(temp_interior, hum_interior, water_present, weight, alarm_message)  # Muestra los datos en la pantalla OLED
    
    comedero_fsm.previous_weight = weight  # Actualiza el peso anterior del comedero
    
    time.sleep(1)  # Pausa de 1 segundo entre lecturas para evitar sobrecarga del procesador
