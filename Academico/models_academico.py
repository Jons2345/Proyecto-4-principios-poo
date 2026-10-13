"""Modelos del negocio académico. Persona, ModeloBase y las reglas ya existen:
se reutilizan tal cual desde models.py."""

from models import ModeloBase, Persona


# =====================================================================
# HERENCIA: dos personas distintas, misma base
# =====================================================================
class Estudiante(Persona):
    CAMPOS = Persona.CAMPOS + ("carnet",)
    OBLIGATORIOS = Persona.OBLIGATORIOS + ("carnet",)

    def __init__(self, id_registro, nombre, apellido, email, carnet):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet

    @property
    def carnet(self):
        return self.__carnet

    @carnet.setter
    def carnet(self, valor):
        valor = Estudiante.limpiar(valor).upper()
        if len(valor) < 4:
            raise ValueError("El carnet debe tener al menos 4 caracteres")
        self.__carnet = valor

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.__carnet
        return datos

    def etiqueta(self):
        return f"{self.nombre_completo} · carnet {self.__carnet}"


class Docente(Persona):
    CAMPOS = Persona.CAMPOS + ("titulo", "especialidad")
    OBLIGATORIOS = Persona.OBLIGATORIOS

    def __init__(self, id_registro, nombre, apellido, email, titulo="", especialidad=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.titulo = titulo
        self.especialidad = especialidad

    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, valor):
        self.__titulo = Docente.limpiar(valor)

    @property
    def especialidad(self):
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor):
        self.__especialidad = Docente.limpiar(valor).title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["titulo"] = self.__titulo
        datos["especialidad"] = self.__especialidad
        return datos

    def etiqueta(self):
        prefijo = f"{self.__titulo} " if self.__titulo else ""
        return f"{prefijo}{self.nombre_completo} · {self.__especialidad or 'sin especialidad'}"


# =====================================================================
# AGREGACIÓN: la materia apunta a un docente por su id.
# Si se borra la materia, el docente sigue existiendo.
# =====================================================================
class Materia(ModeloBase):
    CAMPOS = ("nombre", "codigo", "creditos", "docente_id")
    OBLIGATORIOS = ("nombre", "codigo")

    def __init__(self, id_registro, nombre, codigo, creditos=0, docente_id=None):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos
        self.docente_id = docente_id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Materia.limpiar(valor)
        if not valor:
            raise ValueError("El nombre de la materia es obligatorio")
        self.__nombre = valor.title()

    @property
    def codigo(self):
        return self.__codigo

    @codigo.setter
    def codigo(self, valor):
        valor = Materia.limpiar(valor).upper()
        if len(valor) < 3:
            raise ValueError("El código debe tener al menos 3 caracteres")
        self.__codigo = valor

    @property
    def creditos(self):
        return self.__creditos

    @creditos.setter
    def creditos(self, valor):
        try:
            valor = int(valor or 0)
        except (TypeError, ValueError):
            raise ValueError(f"Los créditos deben ser un número: '{valor}'")
        if not 0 <= valor <= 10:
            raise ValueError("Los créditos deben estar entre 0 y 10")
        self.__creditos = valor

    @property
    def docente_id(self):
        return self.__docente_id

    @docente_id.setter
    def docente_id(self, valor):
        if valor in (None, "", "0"):
            self.__docente_id = None
            return
        try:
            self.__docente_id = int(valor)
        except (TypeError, ValueError):
            raise ValueError(f"docente_id inválido: '{valor}'")

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "codigo": self.__codigo,
            "creditos": self.__creditos,
            "docente_id": self.__docente_id,
        }

    def etiqueta(self):
        docente = f"docente {self.__docente_id}" if self.__docente_id else "sin docente"
        return f"{self.__codigo} · {self.__nombre} · {self.__creditos} créditos · {docente}"


# =====================================================================
# COMPOSICIÓN: la Nota vive dentro de la Matrícula, igual que
# DetalleVenta vive dentro de la Venta.
# =====================================================================
class Nota:
    TIPOS = ("deber", "lección", "examen")
    MINIMA = 0
    MAXIMA = 20

    def __init__(self, tipo, valor, peso=1):
        self.tipo = tipo
        self.valor = valor
        self.peso = peso

    @staticmethod
    def es_valida(valor):
        return isinstance(valor, (int, float)) and Nota.MINIMA <= valor <= Nota.MAXIMA

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        valor = str(valor).strip().lower()
        if valor not in Nota.TIPOS:
            raise ValueError(f"Tipo inválido. Use uno de: {', '.join(Nota.TIPOS)}")
        self.__tipo = valor

    @property
    def valor(self):
        return self.__valor

    @valor.setter
    def valor(self, valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"La nota debe ser un número: '{valor}'")
        if not Nota.es_valida(valor):
            raise ValueError(f"La nota debe estar entre {Nota.MINIMA} y {Nota.MAXIMA}")
        self.__valor = round(valor, 2)

    @property
    def peso(self):
        return self.__peso

    @peso.setter
    def peso(self, valor):
        valor = float(valor or 1)
        if valor <= 0:
            raise ValueError("El peso debe ser mayor a 0")
        self.__peso = valor

    def a_diccionario(self):
        return {"tipo": self.__tipo, "valor": self.__valor, "peso": self.__peso}

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["tipo"], datos["valor"], datos.get("peso", 1))

    def __str__(self):
        return f"{self.__tipo}: {self.__valor}"


class Matricula(ModeloBase):
    """Une a un Estudiante con una Materia y guarda sus notas.
    Es el equivalente académico de la Venta con sus detalles."""

    CAMPOS = ("estudiante_id", "materia_id", "periodo")
    OBLIGATORIOS = ("estudiante_id", "materia_id")
    NOTA_APROBACION = 14

    def __init__(self, id_registro, estudiante_id, materia_id, periodo="", notas=None):
        super().__init__(id_registro)
        self.estudiante_id = estudiante_id
        self.materia_id = materia_id
        self.periodo = periodo
        self.__notas = list(notas) if notas else []

    @property
    def estudiante_id(self):
        return self.__estudiante_id

    @estudiante_id.setter
    def estudiante_id(self, valor):
        self.__estudiante_id = int(valor)

    @property
    def materia_id(self):
        return self.__materia_id

    @materia_id.setter
    def materia_id(self, valor):
        self.__materia_id = int(valor)

    @property
    def periodo(self):
        return self.__periodo

    @periodo.setter
    def periodo(self, valor):
        self.__periodo = Matricula.limpiar(valor) or "2026-1"

    @property
    def notas(self):
        return tuple(self.__notas)           # copia de solo lectura

    @property
    def promedio(self):
        if not self.__notas:
            return 0
        puntos = sum(nota.valor * nota.peso for nota in self.__notas)
        pesos = sum(nota.peso for nota in self.__notas)
        return round(puntos / pesos, 2)

    @property
    def estado(self):
        if not self.__notas:
            return "Sin notas"
        return "Aprobado" if self.promedio >= Matricula.NOTA_APROBACION else "Reprobado"

    def agregar_nota(self, tipo, valor, peso=1):
        nota = Nota(tipo, valor, peso)      # la Matrícula crea sus propias notas
        self.__notas.append(nota)
        return nota

    def notas_por_tipo(self, tipo):
        tipo = str(tipo).lower()
        return [nota for nota in self.__notas if nota.tipo == tipo]

    def a_diccionario(self):
        return {
            "id": self.id,
            "estudiante_id": self.__estudiante_id,
            "materia_id": self.__materia_id,
            "periodo": self.__periodo,
            "promedio": self.promedio,
            "estado": self.estado,
            "notas": [nota.a_diccionario() for nota in self.__notas],
        }

    @classmethod
    def desde_diccionario(cls, datos):
        notas = [Nota.desde_diccionario(n) for n in datos.get("notas", [])]
        return cls(datos["id"], datos["estudiante_id"], datos["materia_id"],
                   datos.get("periodo", ""), notas)

    def etiqueta(self):
        return (f"Estudiante {self.__estudiante_id} · materia {self.__materia_id} · "
                f"{self.__periodo} · promedio {self.promedio} ({self.estado})")
    """Une a un Estudiante con una Materia y guarda sus notas.
    Es el equivalente académico de la Venta con sus detalles."""

    CAMPOS = ("estudiante_id", "materia_id", "periodo")
    OBLIGATORIOS = ("estudiante_id", "materia_id")
    NOTA_APROBACION = 14

    def __init__(self, id_registro, estudiante_id, materia_id, periodo="", notas=None):
        super().__init__(id_registro)
        self.estudiante_id = estudiante_id
        self.materia_id = materia_id
        self.periodo = periodo
        self.__notas = list(notas) if notas else []

    @property
    def estudiante_id(self):
        return self.__estudiante_id

    @estudiante_id.setter
    def estudiante_id(self, valor):
        self.__estudiante_id = int(valor)

    @property
    def materia_id(self):
        return self.__materia_id

    @materia_id.setter
    def materia_id(self, valor):
        self.__materia_id = int(valor)

    @property
    def periodo(self):
        return self.__periodo

    @periodo.setter
    def periodo(self, valor):
        self.__periodo = Matricula.limpiar(valor) or "2026-1"

    @property
    def notas(self):
        return tuple(self.__notas)          # copia de solo lectura

    @property
    def promedio(self):
        if not self.__notas:
            return 0
        puntos = sum(nota.valor * nota.peso for nota in self.__notas)
        pesos = sum(nota.peso for nota in self.__notas)
        return round(puntos / pesos, 2)

    @property
    def estado(self):
        if not self.__notas:
            return "Sin notas"
        return "Aprobado" if self.promedio >= Matricula.NOTA_APROBACION else "Reprobado"

    def agregar_nota(self, tipo, valor, peso=1):
        nota = Nota(tipo, valor, peso)      # la Matrícula crea sus propias notas
        self.__notas.append(nota)
        return nota

    def notas_por_tipo(self, tipo):
        tipo = str(tipo).lower()
        return [nota for nota in self.__notas if nota.tipo == tipo]

    def a_diccionario(self):
        return {
            "id": self.id,
            "estudiante_id": self.__estudiante_id,
            "materia_id": self.__materia_id,
            "periodo": self.__periodo,
            "promedio": self.promedio,
            "estado": self.estado,
            "notas": [nota.a_diccionario() for nota in self.__notas],
        }

    @classmethod
    def desde_diccionario(cls, datos):
        notas = [Nota.desde_diccionario(n) for n in datos.get("notas", [])]
        return cls(datos["id"], datos["estudiante_id"], datos["materia_id"],
                   datos.get("periodo", ""), notas)

    def etiqueta(self):
        return (f"Estudiante {self.__estudiante_id} · materia {self.__materia_id} · "
                f"{self.__periodo} · promedio {self.promedio} ({self.estado})")