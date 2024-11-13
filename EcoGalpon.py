# Librerías
from machine import Pin, I2C
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
sensor_exterior_id = "Sensor Exterior"
sensor_interior = dht.DHT22(Pin(15))  # Configura el sensor DHT22 en el pin 15 para leer temperatura y humedad interior
sensor_exterior = dht.DHT22(Pin(16))  # Configura otro sensor DHT22 en el pin 16 para leer temperatura y humedad exterior
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

# Configuración del relé para el autollenado del comedero
feeder_refill_relay = Pin(19, Pin.OUT)  # Configura el pin 19 como salida para el relé del autollenado del comedero

# Configuración de los pulsadores para seleccionar el animal
button_gallinas = Pin(10, Pin.IN, Pin.PULL_UP)  # Configura el pin 10 como entrada con pull-up para el botón de gallinas
button_patos = Pin(11, Pin.IN, Pin.PULL_UP)  # Configura el pin 11 como entrada con pull-up para el botón de patos

# Configuración del buzzer para las alarmas
buzzer = Pin(20, Pin.OUT)  # Configura el pin 20 como salida para el buzzer de alarma

# Variables para la selección del animal
animal = None  # Variable para almacenar el animal seleccionado
temp_setpoint = 0  # Variable para el setpoint de temperatura
weight_setpoint = 0  # Variable para el setpoint de peso

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

# Función para seleccionar el animal
def select_animal():
    global animal, temp_setpoint, weight_setpoint
    oled.fill(0)  # Limpia la pantalla OLED
    oled.text('Seleccione Animal', 0, 0)  # Muestra el mensaje de selección de animal
    oled.text('1. Gallinas', 0, 15)  # Opción 1: Gallinas
    oled.text('2. Patos', 0, 25)  # Opción 2: Patos
    oled.show()  # Actualiza la pantalla OLED
    
    while animal is None:
        if not button_gallinas.value() and not button_patos.value():  # Si ambos botones se presionan
            continue  # Ignorar la entrada
        elif not button_gallinas.value() and button_patos.value():  # Si se presiona solo el botón de gallinas
            animal = 'Gallinas'
            temp_setpoint = 30  # Setpoint de temperatura para gallinas
            weight_setpoint = 450  # Setpoint de peso para gallinas
        elif not button_patos.value() and button_gallinas.value():  # Si se presiona solo el botón de patos
            animal = 'Patos'
            temp_setpoint = 27  # Setpoint de temperatura para patos
            weight_setpoint = 600  # Setpoint de peso para patos
        time.sleep(0.05)  # Pequeña pausa para evitar rebotes
    
    oled.fill(0)  # Limpia la pantalla OLED
    oled.text('Animal: {}'.format(animal), 0, 0)  # Muestra el animal seleccionado
    oled.show()  # Actualiza la pantalla OLED
    time.sleep(2)  # Pausa de 2 segundos para que el usuario vea la selección

# Función para mostrar texto en la pantalla OLED
def display_text(temp_interior, hum_interior, temp_exterior, water_present, weight, alarm_message=""):
    oled.fill(0)  # Limpia la pantalla OLED
    oled.text('Temp In: {} C'.format(temp_interior), 0, 0)  # Muestra la temperatura interior
    oled.text('Temp Out: {} C'.format(temp_exterior), 0, 15)  # Muestra la temperatura exterior
    oled.text('Water: {}'.format('Bajo' if water_present else 'lleno'), 0, 25)  # Muestra el estado del agua
    oled.text('Weight: {} g'.format(weight), 0, 35)  # Muestra el peso del comedero
    if alarm_message:
        oled.text(alarm_message, 0, 45)  # Muestra el mensaje de alarma
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

# Clases para las máquinas de estado finito (FSM)
# Clase para la FSM del ventilador
class VentiladorFSM:
    def __init__(self):
        self.state = 'APAGADO'  # Estado inicial del ventilador

    def transition(self, event):
        if self.state == 'APAGADO' and event == 'ENCENDER':
            self.encender()  # Transición a encender el ventilador
        elif self.state == 'ENCENDIDO' and event == 'APAGAR':
            self.apagar()  # Transición a apagar el ventilador
    
    def encender(self):
        self.state = 'ENCENDIDO'  # Cambia el estado a encendido
        ventilation_relay.value(1)  # Activa el relé (enciende el ventilador)
        print("Ventilador encendido")

    def apagar(self):
        self.state = 'APAGADO'  # Cambia el estado a apagado
        ventilation_relay.value(0)  # Desactiva el relé (apaga el ventilador)
        print("Ventilador apagado")

# Clase para la FSM del agua
class AguaFSM:
    def __init__(self):
        self.state = 'NIVEL_OK'  # Estado inicial del nivel de agua
        self.previous_water_level = water_level_sensor.value()  # Almacena el nivel de agua anterior

    def transition(self, event):
        if self.state == 'NIVEL_OK' and event == 'NIVEL_BAJO':
            self.encender_bomba()  # Transición a encender la bomba de agua
        elif self.state == 'BOMBA_ENCENDIDA' and event == 'NIVEL_OK':
            self.apagar_bomba()  # Transición a apagar la bomba de agua
        elif self.state == 'BOMBA_ENCENDIDA' and event == 'NIVEL_SIGUE_BAJO':
            time.sleep(1)  # Añade un retraso para confirmar que el nivel sigue bajo
        elif self.state == 'ALARMA_AGUA' and event == 'NIVEL_OK':
            self.state = 'NIVEL_OK'  # Cambia el estado a nivel OK

    def encender_bomba(self):
        self.state = 'BOMBA_ENCENDIDA'  # Cambia el estado a bomba encendida
        water_refill_relay.value(1)  # Activa el relé (enciende la bomba de agua)
        print("Bomba de agua encendida")

    def apagar_bomba(self):
        self.state = 'NIVEL_OK'  # Cambia el estado a nivel OK
        water_refill_relay.value(0)  # Desactiva el relé (apaga la bomba de agua)
        print("Bomba de agua apagada")

# Clase para la FSM del comedero
class ComederoFSM:
    def __init__(self):
        self.state = 'PESO_OK'  # Estado inicial del peso del comedero
        self.previous_weight = hx711.get_units()  # Almacena el peso anterior del comedero

    def transition(self, event):
        if self.state == 'PESO_OK' and event == 'PESO_BAJO':
            self.encender_relleno()  # Transición a encender el relleno del comedero
        elif self.state == 'RELLENO_ENCENDIDO' and event == 'PESO_OK':
            self.apagar_relleno()  # Transición a apagar el relleno del comedero
        elif self.state == 'RELLENO_ENCENDIDO' and event == 'PESO_SIGUE_BAJO':
            self.activar_alarma()  # Transición a activar la alarma
        elif self.state == 'ALARMA_COMEDERO' and event == 'PESO_OK':
            self.state = 'RELLENO_ENCENDIDO'  # Cambia el estado a relleno encendido

    def encender_relleno(self):
        self.state = 'RELLENO_ENCENDIDO'  # Cambia el estado a relleno encendido
        feeder_refill_relay.value(1)  # Activa el relé (enciende el relleno del comedero)
        print("Relleno del comedero encendido")

    def apagar_relleno(self):
        if hx711.get_units() > weight_setpoint + 50:  # Umbral adicional para desactivar la alarma
            self.state = 'PESO_OK'  # Cambia el estado a peso OK
            feeder_refill_relay.value(0)  # Desactiva el relé (apaga el relleno del comedero)
            print("Relleno del comedero apagado")

    def activar_alarma(self):
        self.state = 'ALARMA_COMEDERO'  # Cambia el estado a alarma del comedero
        print("Alarma del comedero activada")

# Selección del animal al inicio
select_animal()  # Llama a la función para seleccionar el animal

# Inicialización de las máquinas de estado finito
ventilador_fsm = VentiladorFSM()  # Inicializa la FSM del ventilador
agua_fsm = AguaFSM()  # Inicializa la FSM del agua
comedero_fsm = ComederoFSM()  # Inicializa la FSM del comedero

# Bucle principal
while True:
    temp_interior = read_sensor(sensor_interior, sensor_interior_id, sensor_interior.measure, sensor_interior.temperature)
    hum_interior = read_sensor(sensor_interior, sensor_interior_id, sensor_interior.measure, sensor_interior.humidity)
    temp_exterior = read_sensor(sensor_exterior, sensor_exterior_id, sensor_exterior.measure, sensor_exterior.temperature)
    water_present = read_sensor(water_level_sensor, water_level_sensor_id, lambda: None, water_level_sensor.value)
    weight = read_sensor(hx711, hx711_id, lambda: None, hx711.get_units)
    
    if None in [temp_interior, hum_interior, temp_exterior, water_present, weight]:
        continue  # Si alguno de los sensores falla, omite el ciclo actual y vuelve a intentar

    if temp_interior > temp_setpoint + 3:
        ventilador_fsm.transition('ENCENDER')  # Transición a encender el ventilador
    elif temp_interior < temp_setpoint:
        ventilador_fsm.transition('APAGAR')  # Transición a apagar el ventilador
    
    if water_present:
        agua_fsm.transition('NIVEL_BAJO')  # Transición a nivel bajo de agua
    else:
        agua_fsm.transition('NIVEL_OK')  # Transición a nivel OK de agua
        water_refill_relay.value(0)
    
    if agua_fsm.state == 'BOMBA_ENCENDIDA' and water_present:
        agua_fsm.transition('NIVEL_SIGUE_BAJO')  # Transición a activar alarma de agua
    elif agua_fsm.state == 'BOMBA_ENCENDIDA' and not water_present:
        agua_fsm.transition('NIVEL_OK')  # Transición a desactivar bomba si el nivel de agua está OK
    
    if weight < weight_setpoint:
        comedero_fsm.transition('PESO_BAJO')  # Transición a peso bajo del comedero
    else:
        comedero_fsm.transition('PESO_OK')  # Transición a peso OK del comedero
    
    if comedero_fsm.state == 'RELLENO_ENCENDIDO' and weight <= comedero_fsm.previous_weight:
        comedero_fsm.transition('PESO_SIGUE_BAJO')  # Transición a activar alarma del comedero
    
    # Manejo del buzzer de alarma
    water_alarm = agua_fsm.state == 'BOMBA_ENCENDIDA'
    food_alarm = comedero_fsm.state == 'ALARMA_COMEDERO'
    alarm_message = sound_alarm(water_alarm, food_alarm)
    
    display_text(temp_interior, hum_interior, temp_exterior, water_present, weight, alarm_message)  # Muestra los datos en la pantalla OLED
    
    agua_fsm.previous_water_level = water_present  # Actualiza el nivel de agua anterior
    comedero_fsm.previous_weight = weight  # Actualiza el peso anterior del comedero
    
    time.sleep(1)  # Pausa de 1 segundo entre lecturas para evitar sobrecarga del procesador

