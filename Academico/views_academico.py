from models_academico import Estudiante, Docente, Materia, Matricula
from views import CrudBase


class EstudianteController(CrudBase):
    """LISTO como ejemplo: cópialo y guíate con él para los demás."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    NOMBRE = "estudiante"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            faltantes = [c for c in self.MODELO.OBLIGATORIOS
                         if not str(datos.get(c, "")).strip()]
            if faltantes:
                return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        if "carnet" in datos and str(datos["carnet"]).strip():
            carnet = str(datos["carnet"]).strip().upper()
            usados = {r["carnet"].upper() for r in self.registros()
                      if r["id"] != id_actual}
            if carnet in usados:
                return f"El carnet {carnet} ya está registrado"
        return None


class DocenteController(CrudBase):
    MODELO = Docente
    ARCHIVO = "data/docentes.json"
    NOMBRE = "docente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "especialidad")

    def validar(self, datos, id_actual=None):
        # TODO: obligatorios + email único (mírate el ClienteController de la parte 3)
        return None


class MateriaController(CrudBase):
    MODELO = Materia
    ARCHIVO = "data/materias.json"
    NOMBRE = "materia"
    CAMPOS_BUSCABLES = ("nombre", "codigo")

    def __init__(self, docentes=None):
        super().__init__()
        self.docentes = docentes or DocenteController()

    def validar(self, datos, id_actual=None):
        # TODO 1: obligatorios cuando id_actual is None
        # TODO 2: el código debe ser único
        # TODO 3: si viene docente_id y no es vacío, ese docente debe existir
        #         (usa self.docentes.existe(int(datos["docente_id"])))
        return None

    def asignar_docente(self, materia_id, docente_id):
        # TODO: verificar que ambos existan y luego
        # return self.actualizar(materia_id, {"docente_id": docente_id})
        pass

    def materias_de_docente(self, docente_id):
        return [m for m in self.listar() if m.docente_id == docente_id]


class MatriculaController(CrudBase):
    """El equivalente académico del VentaController."""

    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matrícula"
    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None):
        super().__init__()
        self.estudiantes = estudiantes or EstudianteController()
        self.materias = materias or MateriaController()

    def validar(self, datos, id_actual=None):
        # TODO 1: el estudiante debe existir
        # TODO 2: la materia debe existir
        # TODO 3: no se puede matricular dos veces al mismo estudiante
        #         en la misma materia y el mismo periodo
        return None

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        # TODO: obtener la matrícula, llamar a matricula.agregar_nota(...),
        # atrapar ValueError y volver a guardar el registro completo.
        pass

    def boletin(self, estudiante_id):
        # TODO: devolver el texto con todas las materias del estudiante,
        # su promedio por materia y el promedio general.
        # Guíate con VentaController.factura().
        pass
    """El equivalente académico del VentaController."""

    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matrícula"
    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None):
        super().__init__()
        self.estudiantes = estudiantes or EstudianteController()
        self.materias = materias or MateriaController()

    def validar(self, datos, id_actual=None):
        # TODO 1: el estudiante debe existir
        # TODO 2: la materia debe existir
        # TODO 3: no se puede matricular dos veces al mismo estudiante
        #         en la misma materia y el mismo periodo
        return None

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        # TODO: obtener la matrícula, llamar a matricula.agregar_nota(...),
        # atrapar ValueError y volver a guardar el registro completo.
        pass

    def boletin(self, estudiante_id):
        # TODO: devolver el texto con todas las materias del estudiante,
        # su promedio por materia y el promedio general.
        # Guíate con VentaController.factura().
        pass