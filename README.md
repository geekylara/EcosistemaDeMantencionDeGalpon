### README.md

# Ecosistema de Mantenimiento de Galpón Automatizado

Este proyecto implementa un sistema de mantenimiento automatizado para un galpón que alberga animales como gallinas y patos. El sistema combina sensores y actuadores para garantizar el control automático de temperatura, niveles de agua, y peso del comedero. También incluye una interfaz de usuario mediante una pantalla OLED y botones físicos.

## Objetivo

Automatizar las tareas de mantenimiento del galpón, mejorando la eficiencia y reduciendo la intervención manual.

## Descripción General

El sistema se basa en una Raspberry Pi Pico y controla las siguientes funcionalidades:
- **Monitoreo de temperatura y humedad interior/exterior.**
- **Control automático del ventilador.**
- **Gestión del nivel de agua con un sensor y una bomba.**
- **Autollenado del comedero usando un sensor de peso y un servomotor.**
- **Alarmas audibles en caso de niveles críticos de agua o comida.**

## Componentes del Sistema

### Hardware
- **Microcontrolador**: Raspberry Pi Pico.
- **Pantalla OLED**: 128x64 píxeles, interfaz I2C.
- **Sensores**:
  - DHT22 para temperatura y humedad (interior y exterior).
  - HX711 para medir el peso del comedero.
  - Sensor de nivel de agua para detectar llenado.
- **Actuadores**:
  - Relés para controlar el ventilador y la bomba de agua.
  - Servomotor para el mecanismo de llenado del comedero.
  - Buzzer para emitir alarmas.
- **Botones físicos** para la selección del tipo de animal (gallinas/patos).

### Software
- **Lenguaje**: CircuitPython/MicroPython.
- **Librerías principales**:
  - `ssd1306` para controlar la pantalla OLED.
  - `dht` para los sensores de temperatura/humedad.
  - `hx711` para el sensor de peso.

## Configuración del Hardware

### Conexiones
| Componente           | Pin de la Pico | Descripción                          |
|----------------------|----------------|--------------------------------------|
| OLED (SCL, SDA)      | GP1, GP0       | Pantalla OLED con I2C.               |
| Sensor DHT22 (Int.)  | GP15           | Sensor de temperatura interior.      |
| Sensor DHT22 (Ext.)  | GP16           | Sensor de temperatura exterior.      |
| Relé ventilación     | GP20           | Controla el ventilador.              |
| Relé bomba de agua   | GP22           | Controla la bomba de agua.           |
| Sensor nivel agua    | GP2            | Entrada del sensor de nivel de agua. |
| Sensor peso (HX711)  | GP4, GP3       | Pines de datos y reloj.              |
| Servomotor           | GP19           | PWM para control del servo.          |
| Buzzer               | GP18           | Alarma audible.                      |
| Botón gallinas       | GP10           | Selección del animal: gallinas.      |
| Botón patos          | GP11           | Selección del animal: patos.         |

### Configuración de Software
1. Instalar CircuitPython o MicroPython en la Raspberry Pi Pico.
2. Instalar las librerías necesarias en la carpeta `lib/` del dispositivo:
   - `ssd1306.py`
   - `dht.py`
   - `hx711.py`
3. Subir el archivo principal del código al dispositivo.

## Funcionalidades Principales

1. **Monitoreo y Control**:
   - Monitoreo continuo de la temperatura interior y exterior.
   - Activación del ventilador si la temperatura excede el setpoint.

2. **Gestión del Nivel de Agua**:
   - Activación de la bomba si el nivel de agua está bajo.
   - Apagado automático una vez completado el llenado.

3. **Control del Comedero**:
   - Monitoreo del peso del comedero.
   - Activación del servomotor para rellenar cuando el peso esté por debajo del setpoint.

4. **Alarmas**:
   - Alertas audibles para niveles críticos de agua o comida.
   - Indicaciones visuales en la pantalla OLED.

5. **Interfaz de Usuario**:
   - Selección de tipo de animal al inicio.
   - Visualización en tiempo real de temperatura, peso y estado del agua.

## Máquina de Estados

El sistema utiliza máquinas de estado finito (FSM) para controlar los subsistemas principales:
- **Ventilador FSM**:
  - Estados: `APAGADO`, `ENCENDIDO`.
  - Eventos: temperatura supera o desciende del setpoint.
- **Agua FSM**:
  - Estados: `NIVEL_OK`, `NIVEL_BAJO`, `BOMBA_ENCENDIDA`.
  - Eventos: detección de nivel de agua.
- **Comedero FSM**:
  - Estados: `PESO_OK`, `RELLENO_ENCENDIDO`, `ALARMA_COMEDERO`.
  - Eventos: peso cae por debajo del setpoint.

## Uso del Sistema

1. **Inicio**:
   - Al encender, selecciona el tipo de animal presionando los botones correspondientes.
   - El sistema ajusta los setpoints de temperatura y peso según la selección.

2. **Operación Automática**:
   - El sistema opera de forma autónoma para mantener las condiciones adecuadas.
   - Se muestran datos en la pantalla OLED y se emiten alarmas en caso necesario.

## Calibración

1. **Sensor de Peso (HX711)**:
   - Ajustar el factor de escala para el peso esperado.
   - Usar objetos de peso conocido para la calibración inicial.

## Contribución

Este proyecto está diseñado para mejorar las operaciones diarias de un galpón. Si deseas contribuir con mejoras, sugerencias o correcciones, ¡eres bienvenido a hacerlo!

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
