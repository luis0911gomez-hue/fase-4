import abc
import datetime

# =====================================================================
# 1. EXCEPCIONES PERSONALIZADAS (Estudiante 1)
# =====================================================================
class ErrorSoftwareFJ(Exception):
    """El papá de todos los errores del sistema."""
    pass

class ErrorDatosInvalidos(ErrorSoftwareFJ):
    """Para cuando meten un correo feo o un ID vacío."""
    pass

class ErrorServicioNoDisponible(ErrorSoftwareFJ):
    """Para cuando se acaben los equipos en stock."""
    pass

class ErrorReservaInvalida(ErrorSoftwareFJ):
    """Para cuando intenten cancelar dos veces o reservar 0 horas."""
    pass


# =====================================================================
# 2. SISTEMA DE REGISTRO DE EVENTOS (Estudiante 1)
# =====================================================================
def registrar_log(nivel: str, mensaje: str):
    """Guarda los eventos en un bloc de notas llamado 'software_fj.log'."""
    archivo = None
    try:
        archivo = open("software_fj.log", "a", encoding="utf-8")
        hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        archivo.write(f"[{hora_actual}] [{nivel.upper()}] {mensaje}\n")
    except IOError as e:
        print(f"Error guardando el log en el disco: {e}")
    finally:
        if archivo:
            archivo.close()


# =====================================================================
# 3. ABSTRACCIÓN BASE DEL SISTEMA (Estudiante 2)
# =====================================================================
class EntidadSistema(abc.ABC):
    """Un molde puro. Obliga a implementar el método obtener_detalles."""
    @abc.abstractmethod
    def obtener_detalles(self) -> str:
        pass


# =====================================================================
# 4. CLASE CLIENTE CON ENCAPSULAMIENTO ESTRICTO (Estudiante 2)
# =====================================================================
class Cliente(EntidadSistema):
    """Representa un Cliente con validaciones en tiempo real para sus datos."""
    def __init__(self, id_cliente: str, nombre: str, email: str):
        self.id_cliente = id_cliente  
        self.nombre = nombre          
        self.email = email            

    @property
    def id_cliente(self): 
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: str):
        if not valor or len(valor) < 5:
            raise ErrorDatosInvalidos("El ID del cliente debe tener mínimo 5 caracteres.")
        self._id_cliente = valor

    @property
    def nombre(self): 
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or valor.strip() == "":
            raise ErrorDatosInvalidos("El nombre del cliente no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def email(self): 
        return self._email

    @email.setter
    def email(self, valor: str):
        if "@" not in valor or "." not in valor:
            raise ErrorDatosInvalidos(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self._email = valor

    def obtener_detalles(self) -> str:
        return f"Cliente: {self._nombre} | ID: {self._id_cliente} | Correo: {self._email}"
