import json
import os


class GestorJSON:
    """Lee y guarda una lista de diccionarios. Es la única parte que toca el disco."""

    def __init__(self, ruta):
        self.__ruta = ruta                       # atributo PRIVADO
        carpeta = os.path.dirname(ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    @property
    def ruta(self):
        # Solo lectura: nadie puede cambiar el archivo de un gestor ya creado
        return self.__ruta

    def leer(self):
        if not os.path.exists(self.__ruta):
            return []
        try:
            with open(self.__ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos):
        try:
            with open(self.__ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (TypeError, OSError):
            return False