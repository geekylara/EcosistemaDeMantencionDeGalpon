# **Ecosistema Automático para el Mantenimiento de un Galpón**

Este proyecto implementa un sistema automático para el mantenimiento ambiental y sanitario de un galpón destinado a gallinas o patos. Mediante sensores, actuadores y un controlador PID para la temperatura, el sistema mantiene condiciones óptimas y reduce la necesidad de intervención humana.

---

# 🚀 **Estado Actual del Proyecto**

La versión actual incorpora mejoras significativas:

* **Nuevo control PID** para la temperatura interior, con regulación suave mediante PWM sobre un ventilador DC.
* **Eliminación de las máquinas de estado (FSM)** para simplificar el procesamiento y mejorar la estabilidad.
* **Retiro del sistema automático de alimentación**, ya que no aportaba beneficios significativos al ser un proceso lento y sin variaciones rápidas.
* **Lógica de agua simplificada**: activación directa de bomba según el sensor MH-RD.
* **Monitorización completa del entorno** (temperatura, humedad, agua, alimento) con visualización en tiempo real.
* **Pantalla OLED mejorada** con nuevos indicadores (como velocidad del ventilador en porcentaje).

---

# 🎯 **Objetivo del Proyecto**

Automatizar las tareas esenciales del mantenimiento de un galpón avícola, priorizando la precisión del control térmico, la disponibilidad continua de agua y la supervisión básica del alimento, incrementando la eficiencia y reduciendo la intervención manual.

---

# 🧩 **Descripción General del Sistema**

El sistema, basado en una **Raspberry Pi Pico**, gestiona las siguientes funciones:

* **Control PID de temperatura** mediante ventilador DC regulado por PWM.
* **Monitoreo de temperatura y humedad interior/exterior** con sensores DHT22.
* **Gestión automática del nivel de agua** mediante sensor MH-RD y una bomba.
* **Monitoreo del nivel de alimento** mediante el módulo HX711.
* **Alarmas sonoras** mediante buzzer.
* **Interfaz visual** mediante una pantalla OLED I2C.
* **Selección inicial del tipo de animal (gallinas/patos)** para ajustar el setpoint de temperatura.

---

# 🛠️ **Componentes del Sistema**

## **Hardware**

* **Microcontrolador:** Raspberry Pi Pico (RP2040).
* **Pantalla OLED:** 128×64 px (I2C).
* **Sensores:**

  * DHT22 ×2 (interior y exterior).
  * MH-RD (nivel de agua).
  * HX711 + celda de carga (peso del alimento).
* **Actuadores:**

  * Ventilador DC 12V (control PWM).
  * Bomba de agua (controlada por relé).
  * Buzzer para alarmas.
* **Botones** para selección del tipo de animal.

## **Software**

* **Lenguaje:** CircuitPython
* **Librerías utilizadas:**

  * `ssd1306.py`
  * `dht.py`
  * `hx711.py`

---

# 🔌 **Conexiones de Hardware**

| Componente           | Pin Pico | Descripción                            |
| -------------------- | -------- | -------------------------------------- |
| OLED (SCL, SDA)      | GP1, GP0 | Interfaz I2C para pantalla OLED        |
| DHT22 (interior)     | GP15     | Sensor de temperatura/humedad interior |
| DHT22 (exterior)     | GP16     | Sensor de temperatura/humedad exterior |
| Ventilador PWM       | GP20     | Control de velocidad vía PWM           |
| Bomba de agua (relé) | GP22     | Control ON/OFF                         |
| Sensor MH-RD         | GP2      | Detección del nivel de agua            |
| HX711 (DT, SCK)      | GP3, GP4 | Sensor de peso                         |
| Servo MG90           | GP19     | *Ya no se usa para alimentación*       |
| Buzzer               | GP18     | Alarma sonora                          |
| Botón gallinas       | GP10     | Selección inicial del animal           |
| Botón patos          | GP11     | Selección inicial del animal           |

---

# ⚙️ **Funcionalidades Principales**

### ✅ **1. Control PID de Temperatura**

* El sistema ajusta la velocidad del ventilador mediante PWM.
* Usa un PID para mantener estable la temperatura del galpón.
* Setpoints distintos según el animal:

  * Gallinas: 29 °C
  * Patos: 25 °C

### ✅ **2. Gestión Automática del Agua**

* Si el MH-RD detecta nivel bajo → activa la bomba.
* Cuando se restablece el nivel → apaga la bomba.

### ✅ **3. Monitoreo del Alimento**

* Se mide el peso del comedero con HX711.
* Ya **no se activa** el servo para rellenar de forma automática.
* Esto reduce desgaste y complejidad innecesaria.

### ✅ **4. Alarmas**

* Falta de agua.
* Peso de alimento bajo.

### ✅ **5. Pantalla OLED**

* Muestra:

  * Temperatura interior/exterior.
  * Humedad interior.
  * Nivel de agua.
  * Peso del comedero.
  * Velocidad del ventilador (% PWM).
  * Estado del sistema.

### ✅ **6. Selección del Animal**

* En el arranque, se elige gallinas o patos mediante botones.

---

# 🔧 **Instalación y Puesta en Marcha**

1. Instalar CircuitPython en la Raspberry Pi Pico.
2. Copiar las librerías necesarias en `/lib`.
3. Colocar el archivo principal (`EcoGalpon.py` o similar) en la raíz del dispositivo.
4. Reiniciar la Pico.
5. Seleccionar el animal con los botones físicos.

---

# 📏 **Calibración**

### HX711 (Peso)

* Colocar un peso conocido.
* Ajustar el factor de escala en el código hasta que el valor coincida.

### PID

* Ajustar `Kp`, `Ki`, `Kd` según el comportamiento del ventilador.
* Comenzar con control proporcional (solo Kp).

---

# 🧹 **Cambios Relevantes respecto a la Versión Anterior**

* 🔥 Se eliminó el autollenado del comedero por ser innecesario.
* 🔥 Se quitó el uso de máquinas de estado (FSM).
* 🔥 Se incorporó control PID de temperatura.
* 🔥 Lógica general optimizada y menos dependiente de temporizadores.
* 🔥 Pantalla actualizada con nuevos indicadores.
* 🔥 Código reorganizado, más limpio y estable.

---

# 🤝 **Contribuciones**

¡Las contribuciones son bienvenidas!
Puedes abrir un **Issue** o enviar un **Pull Request**.

---

# 📄 **Licencia**

Este proyecto está bajo la licencia MIT.
Consulta el archivo `LICENSE` para más detalles.
