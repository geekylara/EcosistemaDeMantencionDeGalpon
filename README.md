# Sistema Automático para Galpón de Gallinas Ponedoras

## Descripción del Proyecto

Este proyecto es un sistema automatizado para el mantenimiento de un galpón de gallinas ponedoras de la línea genética **Super Nick**. Utiliza una Raspberry Pi Pico para controlar y monitorear diversos aspectos del galpón, incluyendo la temperatura, humedad, nivel de agua y nivel de alimento. El sistema incluye las siguientes características:

- **Monitoreo de Temperatura y Humedad**: Utiliza un sensor DHT22 para medir la temperatura y la humedad dentro del galpón y muestra los valores en una pantalla OLED.
- **Control Automático de Ventilación**: Activa un ventilador cuando la temperatura excede un umbral específico para mantener un ambiente óptimo para las gallinas.
- **Monitoreo y Relleno del Nivel de Agua**: Utiliza un sensor MH-RD para detectar el nivel de agua y activa una bomba de agua cuando el nivel es bajo.
- **Autollenado del Comedero**: Utiliza un sensor de peso HX711 para medir el nivel de alimento en el comedero y activa un mecanismo de relleno cuando el peso es insuficiente.
- **Interfaz Visual**: Muestra la temperatura, humedad, estado del ventilador, nivel de agua y peso del comedero en una pantalla OLED de 128x32.

## Componentes Utilizados

- **Raspberry Pi Pico**: Unidad de procesamiento principal.
- **Sensor DHT22**: Sensor de temperatura y humedad.
- **Sensor de Nivel de Agua MH-RD**: Sensor para detectar el nivel de agua.
- **Sensor de Peso HX711**: Sensor para medir el peso del comedero.
- **Pantalla OLED 128x32**: Pantalla para mostrar datos en tiempo real.
- **Relés**: Para controlar el ventilador y el mecanismo de relleno de agua y alimento.
- **Ventilador**: Para la ventilación del galpón.
- **Bomba de Agua**: Para rellenar el bebedero automáticamente.
- **Mecanismo de Relleno del Comedero**: Controlado por un relé y activado basado en el peso.

## Conexiones de Hardware

### Conexiones de Sensores y Actuadores

| Componente                | Conexión en Raspberry Pi Pico |
|---------------------------|------------------------------|
| **Sensor DHT22**          | VCC: 3.3V, GND: GND, DATA: GP15 |
| **Sensor de Nivel de Agua MH-RD** | VCC: 3.3V, GND: GND, D0: GP2 |
| **Sensor de Peso HX711**  | VCC: 3.3V, GND: GND, DT: GP3, SCK: GP4 |
| **Pantalla OLED 128x32**  | VCC: 3.3V, GND: GND, SDA: GP0, SCL: GP1 |
| **Relé Ventilador**       | GP16 |
| **Relé Relleno de Agua**  | GP17 |
| **Relé Relleno de Comedero** | GP18 |

## Instalación y Configuración

1. **Descargar el Repositorio**:
   ```bash
   git clone https://github.com/geekylara/EcosistemaDeMantencionDeGalpon.git
   cd EcosistemaDeMantencionDeGalpo
   ```

2. **Copiar Librerías Necesarias**:
   - Copia `hx711.py` al directorio `/lib` de tu Raspberry Pi Pico. <a rel="noreferrer" target="_new" href="https://github.com/robert-hh/hx711">Repositorio Del sensor HX711</a>
   - Asegúrate de tener las librerías `dht`, `ssd1306`, y `machine` instaladas.

3. **Cargar el Código en la Raspberry Pi Pico**:
   - Utiliza un editor compatible con MicroPython para cargar el código `EcoGalpon.py` en tu Raspberry Pi Pico.

## Uso del Proyecto

1. **Encender el Sistema**:
   - Conecta todos los componentes según las conexiones de hardware.
   - Alimenta la Raspberry Pi Pico.

2. **Visualización de Datos**:
   - La pantalla OLED mostrará la temperatura, humedad, estado del ventilador, nivel de agua y peso del comedero en tiempo real.

3. **Automatización**:
   - El ventilador se activará automáticamente si la temperatura supera los 30°C.
   - La bomba de agua se activará si el sensor MH-RD detecta un nivel bajo de agua.
   - El mecanismo de relleno del comedero se activará si el peso del alimento es menor a 450 gramos.

## Modificaciones del Proyecto

### Parámetros Ajustables

Los siguientes parámetros están ajustados según los requerimientos de la línea genética de gallinas **Super Nick**. Puedes modificar estos valores en el código según tus propias necesidades:

- **Umbral de Temperatura para Ventilación**: Línea 43 en `EcoGalpon.py`
  ```python
  if temp > 30:  # Ajusta este valor según sea necesario
  ```

- **Umbral de Peso para Relleno del Comedero**: Línea 49 en `EcoGalpon.py`
  ```python
  if weight < 450:  # Ajusta este valor según sea necesario
  ```

- **Factor de Escala del Sensor de Peso**: Línea 29 en `EcoGalpon.py`
  ```python
  scale_factor = 214.0267  # Ajusta este valor según la calibración de tu sensor
  ```

## Ejemplo de Código

```python
# El código completo del proyecto se encuentra en el archivo EcoGalpon.py.
# Aquí se muestra una sección del código para ilustrar la estructura general.
from machine import Pin, I2C
import time
import dht
import ssd1306
from hx711 import HX711

# Configuración del I2C y la pantalla OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# Configuración del sensor DHT22
sensor = dht.DHT22(Pin(15))

# Configuración del sensor de peso HX711
hx711 = HX711(Pin(4, Pin.OUT), Pin(3, Pin.IN))
hx711.tare()
hx711.set_scale(214.0267)

# Bucle principal del programa
while True:
    # Código para leer los sensores y controlar los relés
    ...
    time.sleep(2)
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o un pull request en GitHub.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más detalles.

---
