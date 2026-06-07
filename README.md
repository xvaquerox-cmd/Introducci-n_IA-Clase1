# Asistente de Voz - Proyecto de Introduccion a la IA

Este repositorio es mi version trabajada del proyecto **Asistente_Voz** que el profesor compartio desde:

[https://github.com/Heeber24/Asistente_Voz](https://github.com/Heeber24/Asistente_Voz)

Yo lo importe a mi cuenta de GitHub para poder trabajarlo sin modificar directo el repositorio original:

[https://github.com/xvaquerox-cmd/Introducci-n_IA-Clase1/tree/mi-version-asistente](https://github.com/xvaquerox-cmd/Introducci-n_IA-Clase1/tree/mi-version-asistente)

La idea de la tarea era entender como funcionaba el asistente de voz y agregar **3 comandos nuevos**. En mi caso tambien tuve que adaptarlo para que funcionara en una **Mac mini**, porque el proyecto original estaba mas orientado a Windows.

---

## Resumen de lo que se hizo

Primero tuve que entender GitHub, clonar/importar el proyecto, crear mi rama de trabajo y despues correr el asistente en mi computadora. Al intentar ejecutarlo tal como venia, me di cuenta de que algunas partes no funcionaban igual en macOS, sobre todo la voz y la apertura de aplicaciones.

Despues de varios dias revisando el proyecto, fui entendiendo que el asistente trabaja asi:

```text
yo hablo
el microfono escucha
Google convierte la voz a texto
la gramatica valida la frase
agente.py decide que hacer
acciones.py ejecuta la accion
voz_tts.py responde hablando
```

Al final quedaron agregados estos comandos:

1. Consultar el tipo de cambio de Banxico.
2. Consultar mi IP publica.
3. Decir en que ciudad estoy y complementar con el clima.

Tambien se adaptaron algunas partes para macOS, como abrir aplicaciones con `open` y usar el comando nativo `say` para la voz.

---

## Como funciona el proyecto

El asistente sigue una idea simple:

**percibir -> interpretar -> actuar**

1. **Percibir:** escucha la voz con el microfono.
2. **Interpretar:** convierte la voz a texto y valida que la frase tenga sentido con la gramatica.
3. **Actuar:** ejecuta una funcion dependiendo del comando.

Por ejemplo, si digo:

```text
jarvis dame el tipo de cambio
```

El programa detecta:

```text
palabra de activacion: jarvis
verbo: dame
consulta: el tipo de cambio
```

Y entonces llama la funcion que consulta Banxico.

---

## Archivos principales

| Archivo | Para que sirve |
|---|---|
| `Asistente_Voz_IA.py` | Es el archivo principal. Arranca el asistente. |
| `asistente_voz/agente.py` | Es como el cerebro del asistente. Recibe el texto, identifica el verbo y decide que funcion ejecutar. |
| `asistente_voz/config.py` | Tiene configuracion general: palabras de activacion, verbos, microfono y rutas de aplicaciones. |
| `asistente_voz/gramatica.py` | Valida que la frase tenga una estructura correcta usando una gramatica. |
| `asistente_voz/acciones.py` | Aqui estan las funciones que hacen el trabajo real: abrir apps, consultar APIs, buscar en web, etc. |
| `asistente_voz/voz_stt.py` | Es el oido del asistente. Captura audio y lo manda a Google para convertirlo a texto. |
| `asistente_voz/voz_tts.py` | Es la boca del asistente. Convierte texto a voz para que la computadora conteste hablando. |
| `tipo-cambio/` | API se usa para la consulta a Banxico. |
| `Notas_Cesar_Torres.txt/` | Bitacora personal del proceso. |

---

## Adaptacion a macOS

El proyecto original venia mas pensado para Windows. Al correrlo en mi Mac mini tuve que revisar varios errores.

### Voz del asistente

El proyecto usaba `pyttsx3` para hablar. En Windows funciona bien porque se conecta al motor de voz de Windows, pero en mi Mac se quedaba mudo o no terminaba algunas frases.

Antes se usaba algo como:

```python
self._pyttsx3.say(texto)
self._pyttsx3.runAndWait()
```

En macOS lo cambie para usar el comando nativo de la Mac:

```python
subprocess.run(["say", texto], check=True)
```

Esto se hizo en `asistente_voz/voz_tts.py`, detectando si el sistema es Mac:

```python
if sys.platform == "darwin":
```

`darwin` es como Python identifica a macOS.

### Apertura de aplicaciones

Tambien adapte la parte de abrir aplicaciones. En Windows se hablaba de `notepad`, pero en Mac no existe. Entonces lo adapte para abrir Notas, Chrome y Terminal.

En Mac se usa `open`, por eso en `acciones.py` se usa:

```python
subprocess.Popen(["open", str(ruta)], shell=False)
```

---

## Microfono

El microfono se configura en:

```text
asistente_voz/config.py
```

La variable importante es:

```python
MIC_DEVICE_INDEX_OVERRIDE
```

En mi caso use el indice `3`, porque era el microfono USB de mi webcam.

Para listar microfonos se puede usar:

```bash
python -c "import speech_recognition as sr; [print(i, '-', n) for i, n in enumerate(sr.Microphone.list_microphone_names())]"
```

---

## Palabras de activacion y verbos

Agregue `jarvis` y `jarviz` como palabras de activacion, porque a veces Google transcribe diferente lo que uno dice.

Tambien agregue los verbos:

```text
dime
dame
donde
```

Estos verbos se agregan en:

```text
asistente_voz/config.py
asistente_voz/gramatica.py
```

Y despues se conectan en:

```text
asistente_voz/agente.py
```

---

## Comandos agregados

### 1. Tipo de cambio de Banxico

Comandos:

```text
jarvis dime el tipo de cambio
jarvis dame el tipo de cambio
```

Para este comando use una API de Banxico, porque ya habia trabajado algo parecido en un ERP que estoy haciendo.

API usada:

```text
https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718,SF343410/datos/oportuno
```

Esta consulta trae:

- Tipo de cambio FIX.
- Tipo de cambio de cierre.

La funcion se agrego en:

```text
asistente_voz/acciones.py
```

Y se conecta desde:

```text
asistente_voz/agente.py
```

El agente revisa si la consulta contiene palabras como:

```text
tipo de cambio
dolar
cambio
```

Si encuentra esas palabras, llama la funcion que consulta Banxico.

---

### 2. IP publica

Comandos:

```text
jarvis dame mi ip publica
jarvis dime mi ip publica
```

API usada:

```text
https://api.ipify.org
```

Esta API devuelve directamente la IP publica de la conexion.

En `acciones.py` se lee la respuesta y luego se cambia el punto por la palabra `punto`, para que el asistente la pueda decir mas claro.

Ejemplo:

```text
189.203.44.12
```

Se lee como:

```text
189 punto 203 punto 44 punto 12
```

---

### 3. Ciudad y clima

Comandos:

```text
jarvis donde estoy
jarvis dime el clima
jarvis dame el clima
jarvis dame la temperatura
```

Aqui se usan dos servicios:

#### API para detectar ciudad

```text
http://ip-api.com/json/
```

Esta API detecta la ubicacion aproximada usando la IP publica. Devuelve datos como pais, region y ciudad.

#### API para consultar clima

```text
http://wttr.in/
```

Primero se consulta la ciudad. Luego esa ciudad se usa para armar la URL del clima.

Ejemplo:

```text
http://wttr.in/Mexicali?lang=es&format=%C+con+temperatura+de+%t
```

Donde:

- `lang=es` hace que responda en español.
- `%C` trae la condicion del clima, por ejemplo `Soleado`.
- `%t` trae la temperatura.

Me paso que usando `https` me daba un error en mi Mac, entonces para esta consulta publica lo deje con `http` y funciono bien.

Tambien deje `Mexicali` como valor de respaldo por si no se detecta la ciudad durante la demostracion.

---

## Ejemplos de uso

Con el entorno virtual activado:

```bash
python Asistente_Voz_IA.py
```

Ejemplos de comandos por voz:

```text
jarvis dame el tipo de cambio
jarvis dime mi ip publica
jarvis donde estoy
jarvis dame el clima
jarvis abre notas
jarvis abre terminal
jarvis busca inteligencia artificial
jarvis reproduce Soda Stereo
```

---

## Instalacion basica

Crear entorno virtual:

```bash
python3 -m venv .venv
```

Activarlo en Mac:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar:

```bash
python Asistente_Voz_IA.py
```

---

## Modo texto para probar sin microfono

Tambien se puede probar por texto, que sirve mucho para depurar sin estar hablando todo el tiempo.

En Mac:

```bash
ASISTENTE_TEXTO=1 python Asistente_Voz_IA.py
```

---

## Flujo para agregar un comando nuevo

Lo que entendi es que normalmente se cambian estos archivos:

1. `config.py`  
   Se agrega el verbo a `VERBOS`.

2. `gramatica.py`  
   Se agrega el verbo a la gramatica y, si acepta texto libre despues, tambien a `VERBOS_CON_OBJETO_ABIERTO`.

3. `acciones.py`  
   Se programa la funcion que hace el trabajo.

4. `agente.py`  
   Se conecta el comando con la funcion.

Este fue el aprendizaje mas importante para mi, porque ahi entendi como una frase hablada termina convirtiendose en una accion real.

---

## GitHub

Para respaldar cambios use este flujo:

```bash
git status
git add .
git commit -m "mensaje del cambio"
git push origin mi-version-asistente
```

Tambien aprendi que no se debe subir la carpeta `.venv`, porque contiene el entorno virtual y son muchos archivos que no forman parte del codigo fuente.

---

## Problemas que se fueron corrigiendo

- El proyecto estaba mas orientado a Windows y yo lo cambié a Mac.
- La voz con `pyttsx3` no funcionaba bien en macOS, por eso se cambio a `say`.
- Hubo que seleccionar correctamente el microfono.
- Se adapto la apertura de apps usando `open`, ya que OSX mira los programas com si fuera carpeta y no como ve windows un ".exe" .
- Se agregaron `jarvis` y `jarviz` como palabras de activacion.
- Se agregaron los verbos `dime`, `dame` y `donde`.
- Se agregaron las consultas a Banxico, IP publica, ciudad y clima.
- Se corrigio el bloque de `agente.py` para que `abre`, `dime`, `dame` y `donde` quedaran separados correctamente.

---

## Conclusion

Al inicio pense que solo era agregar tres comandos, pero realmente tuve que entender el proyecto completo: GitHub, entorno virtual, microfono, voz, gramatica, acciones y APIs.

Lo que mas me quedo claro fue como se conecta todo:

```text
voz_stt.py escucha
Google regresa texto
gramatica.py valida
agente.py decide
acciones.py ejecuta
voz_tts.py responde
```

Con eso quedo terminada mi version del asistente de voz y respaldada en GitHub.
