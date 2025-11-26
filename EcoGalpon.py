# ==============================
# PROYECTO GALPÓN AUTOMÁTICO V2
# Control PID de temperatura
# ==============================

from machine import Pin, I2C, PWM
import dht
import ssd1306
import time
from hx711 import HX711

# ---------- CONFIGURACIÓN OLED ----------
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# ---------- SENSORES ----------
sensor_interior = dht.DHT22(Pin(15))
sensor_exterior = dht.DHT22(Pin(16))
nivel_agua = Pin(2, Pin.IN, Pin.PULL_DOWN)

# ---------- ACTUADORES ----------
bomba = Pin(22, Pin.OUT)
buzzer = Pin(18, Pin.OUT)
servo = PWM(Pin(19))
servo.freq(50)
ventilador = PWM(Pin(20))
ventilador.freq(25000) 

# ---------- SENSOR DE PESO ----------
hx711 = HX711(Pin(4, Pin.OUT), Pin(3, Pin.IN))
hx711.tare()
hx711.set_scale(197.0267)

# ---------- PARÁMETROS ----------
setpoint_gallina = 29.0
setpoint_pato = 25.0
setpoint = setpoint_gallina  # Por defecto gallinas
peso_limite = 450  # gramos
Kp, Ki, Kd = 3000, 50, 1200  # PID inicial
pid_integral = 0
pid_last_error = 0

# ---------- FUNCIONES ----------
def pid_control(temp_actual, setpoint):
    global pid_integral, pid_last_error
    error = setpoint - temp_actual
    pid_integral += error
    derivative = error - pid_last_error
    output = (Kp * error) + (Ki * pid_integral) + (Kd * derivative)
    pid_last_error = error
    output = max(0, min(65535, int(abs(output))))
    return output

def servo_abrir():
    servo.duty_u16(6553)  # ~50 grados
    time.sleep(0.4)
    servo.duty_u16(0)

def mostrar_datos(temp, hum, temp_out, peso, agua, pwm_val):
    oled.fill(0)
    oled.text(f"T_in:{temp:.1f}C", 0, 0)
    oled.text(f"T_out:{temp_out:.1f}C", 0, 12)
    oled.text(f"H:{hum:.1f}%", 0, 24)
    oled.text(f"Peso:{peso:.0f}g", 0, 36)
    oled.text(f"Agua:{'OK' if agua==0 else 'BAJA'}", 0, 48)
    oled.text(f"Vent:{int(pwm_val/655)}%", 64, 48)
    oled.show()

def alarma(condicion):
    if condicion:
        buzzer.value(1)
        time.sleep(0.2)
        buzzer.value(0)
        time.sleep(0.2)

# ---------- BUCLE PRINCIPAL ----------
while True:
    try:
        # Lecturas
        sensor_interior.measure()
        temp_in = sensor_interior.temperature()
        hum_in = sensor_interior.humidity()
        sensor_exterior.measure()
        temp_out = sensor_exterior.temperature()
        agua = nivel_agua.value()
        peso = hx711.get_units()

        # ----- PID: control del ventilador -----
        pwm_value = pid_control(temp_in, setpoint)
        ventilador.duty_u16(pwm_value)

        # ----- Control de agua -----
        if agua == 1:
            bomba.value(1)
            alarma(True)
        else:
            bomba.value(0)

        # ----- Control del comedero -----
        if peso < peso_limite:
            servo_abrir()

        # ----- Alarmas -----
        if agua == 1 or peso < peso_limite:
            alarma(True)
        else:
            buzzer.value(0)

        # ----- Mostrar en pantalla -----
        mostrar_datos(temp_in, hum_in, temp_out, peso, agua, pwm_value)

        time.sleep(3)  # Ciclo de control (3 s)

    except OSError:
        oled.fill(0)
        oled.text("Error sensor!", 0, 0)
        oled.show()
        time.sleep(2)
