"""YouTube, Google y programas (lo que hace el agente en el equipo)."""

from __future__ import annotations

# Cada función recibe la cola del comando (texto tras el verbo) y un callback hablar(msg) que usa el TTS.
# pywhatkit intenta abrir el navegador; si falla, se usa webbrowser como respaldo.
# Para nuevas apps en "abre", amplía resolver_ruta_aplicacion y ALIAS_ETIQUETA en config.py, y detectar_alias_app_en_tokens aquí.

import subprocess
import threading
import time
import webbrowser
import json
import urllib.request
from urllib.parse import quote_plus, quote

import pywhatkit

from asistente_voz.config import ALIAS_ETIQUETA, resolver_ruta_aplicacion


def _youtube_url(q: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"


def _google_url(q: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(q)}"


def _play_youtube_hilo(q: str) -> None:
    try:
        pywhatkit.playonyt(q)
    except Exception as e:
        print(f"[YouTube] {e} — abriendo búsqueda en el navegador.")
        webbrowser.open(_youtube_url(q))


def _buscar_google_hilo(q: str) -> None:
    try:
        pywhatkit.search(q)
    except Exception as e:
        print(f"[Google] pywhatkit: {e}")
        webbrowser.open(_google_url(q))


def ejecutar_reproducir_youtube(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres reproducir en YouTube.")
        return
    msg = f"Reproduciendo {q} en YouTube."
    print(msg)
    hablar(msg)
    time.sleep(0.7)
    threading.Thread(target=_play_youtube_hilo, args=(q,), daemon=True, name="yt").start()


def ejecutar_busqueda_google(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres buscar en Google.")
        return
    msg = f"Buscando {q} en Google."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    threading.Thread(target=_buscar_google_hilo, args=(q,), daemon=True, name="gg").start()


def ejecutar_abrir_aplicacion(alias: str, hablar) -> None:
    alias = alias.lower()
    ruta = resolver_ruta_aplicacion(alias)
    etiqueta = ALIAS_ETIQUETA.get(alias, alias)
    if ruta is None:
        hablar(f"No encontré instalada la aplicación {etiqueta}. Revisa config.py.")
        print(f"No hay ruta para: {alias}")
        return
    msg = f"Abriendo {etiqueta}."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    try:
        subprocess.Popen(["open",str(ruta)], shell=False)
    except OSError as e:
        hablar("No pude lanzar la aplicación.")
        print(e)


def detectar_alias_app_en_tokens(tokens: list[str]) -> str | None:
    # Primera coincidencia con la lista; debe alinearse con lo que entiende resolver_ruta_aplicacion.
    apps = ("notas", "word", "chrome", "documento", "terminal")
    found: str | None = None
    for t in tokens:
        if t in apps:
            found = t
    return found
    
def ejecutar_consulta_tipo_cambio(consulta: str, hablar) -> None:
    # Le avisamos al usuario que estamos buscando la información
    hablar("Consultando el tipo de cambio en el Banco de México.")
    
    url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718,SF343410/datos/oportuno"
    token = "6f56d2412aa2a3f530dc89983d7155349245ad9491464b9411766d6c65e5ee3c" #token de ERP SOLTEC 
    
    # Preparamos la petición HTTP con los encabezados (headers) requeridos por Banxico
    req = urllib.request.Request(
        url,
        headers={
            "Bmx-Token": token,
            "Accept": "application/json"
        }
    )
    
    try:
        # Hacemos la consulta física a la API (máximo 5 segundos de espera)
        with urllib.request.urlopen(req, timeout=5) as response:
            datos = json.loads(response.read().decode("utf-8"))
            series = datos["bmx"]["series"]
            
            # Buscamos las series FIX (SF43718) y de Cierre (SF343410) en la respuesta
            fix_serie = next((s for s in series if s["idSerie"] == "SF43718"), None)
            cierre_serie = next((s for s in series if s["idSerie"] == "SF343410"), None)
            
            fix_dato = fix_serie["datos"][0]["dato"] if fix_serie and "datos" in fix_serie and fix_serie["datos"] else None
            cierre_dato = cierre_serie["datos"][0]["dato"] if cierre_serie and "datos" in cierre_serie and cierre_serie["datos"] else None
            
            # Construimos la frase que dirá el asistente de voz
            if fix_dato:
                msg = f"El tipo de cambio FIX reportado hoy es de {fix_dato} pesos por dólar."
                if cierre_dato:
                    msg += f" Y el tipo de cambio de cierre es de {cierre_dato} pesos por dólar."
            else:
                msg = "No encontré datos de tipo de cambio disponibles en este momento."
            
            # Imprimimos en consola y mandamos la respuesta a la síntesis de voz (TTS)
            print(f"[Banxico] {msg}")
            hablar(msg)
            
    except Exception as e:
        print(f"[Banxico Error] {e}")
        hablar("Lo siento, tuve un problema de conexión al consultar el Banco de México.")

def ejecutar_consulta_ip_publica(hablar) -> None:
    hablar("Consultando tu dirección IP pública en internet.")
    
    try:
        # consultamos pagina para leer ip
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            ip = response.read().decode("utf-8").strip()
            
            # reemplazamos "." por palabra "punto"
            ip_leible = ip.replace(".", " punto ")
            msg = f"Tu dirección IP pública es {ip_leible}."
            
            print(f"[IP Pública] {ip}")
            hablar(msg)
            
    except Exception as e:
        print(f"[IP Error] {e}")
        hablar("Lo siento, no pude obtener tu dirección IP pública.")
        
def ejecutar_consulta_clima_local(hablar) -> None:
    
    hablar("Buscando tu ubicación en el mapa.")
    
    try:
        
        url_geolocalizacion = "http://ip-api.com/json/" # 1 localizamos 
        respuesta_geo = urllib.request.urlopen(url_geolocalizacion, timeout=5)
        datos_geo_texto = respuesta_geo.read().decode("utf-8")
        
        
        datos_geo_diccionario = json.loads(datos_geo_texto) # 2 respuesta en JSON 
        ciudad = datos_geo_diccionario.get("city", "Mexicali") # 3 del JSON sacamos la ciudad y si no hay decimos que es Mexicali... 
        ciudad_para_url = quote(ciudad) # 4 guardamos ciudad en variable para url 
        url_clima = f"http://wttr.in/{ciudad_para_url}?lang=es&format=%C+con+temperatura+de+%t" # 5 generamos url de consulta 
        respuesta_clima = urllib.request.urlopen(url_clima, timeout=5)
        clima_texto = respuesta_clima.read().decode("utf-8").strip() # 6 la respuesta la guardamos en variable 
              
        mensaje_final = f"Según tu dirección de internet, estás en la ciudad de {ciudad}. El clima actual es {clima_texto}." # 7  generamos el mensaje de aviso
        
        
        print(f"[Clima Local] {mensaje_final}") # 8 mostramos mensaje de la respuesta
        hablar(mensaje_final) #decimo mensaje
        
    except Exception as e:
        print(f"[Error Clima] {e}")
        hablar("Lo siento, no pude determinar tu ubicación o el clima de tu ciudad.")