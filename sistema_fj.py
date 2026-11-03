import abc
import datetime

# =====================================================================
# 1. EXCEPCIONES PERSONALIZADAS
# =====================================================================
class ErrorSoftwareFJ(Exception):
    """El papa de todos los errores del sistema."""
    pass

class ErrorDatosInvalidos(ErrorSoftwareFJ):
    """Para cuando meten un correo feo o un ID vacio."""
    pass

class ErrorServicioNoDisponible(ErrorSoftwareFJ):
    """Para cuando se acaben los equipos en stock."""
    pass

class ErrorReservaInvalida(ErrorSoftwareFJ):
    """Para cuando intenten cancelar dos veces o reservar 0 horas."""
    pass

# =====================================================================
# 2. SISTEMA DE REGISTRO DE EVENTOS
# =====================================================================
def registrar_log(nivel: str, mensaje: str):
    """Guarda los eventos en un bloc de notas llamado software_fj.log."""
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
# 3. ABSTRACCIÓN BASE DEL SISTEMA
# =====================================================================
class EntidadSistema(abc.ABC):
    """Un molde puro. Obliga a implementar el metodo obtener_detalles."""
    @abc.abstractmethod
    def obtener_detalles(self) -> str:
        pass

# =====================================================================
# 4. CLASE CLIENTE CON ENCAPSULAMIENTO ESTRICTO
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
            raise ErrorDatosInvalidos("El ID del cliente debe tener minimo 5 caracteres.")
        self._id_cliente = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or valor.strip() == "":
            raise ErrorDatosInvalidos("El nombre del cliente no puede estar vacio.")
        self._nombre = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor: str):
        if "@" not in valor or "." not in valor:
            raise ErrorDatosInvalidos(f"El correo electronico {valor} no tiene un formato valido.")
        self._email = valor

    def obtener_detalles(self) -> str:
        return f"Cliente: {self._nombre} | ID: {self._id_cliente} | Correo: {self._email}"

# =====================================================================
# 5. CLASE ABSTRACTA SERVICIO
# =====================================================================
class Servicio(EntidadSistema, abc.ABC):
    """Clase abstracta que define la estructura y contrato para todos los servicios."""
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float):
        self.id_servicio = id_servicio
        self.nombre_servicio = nombre_servicio
        if tarifa_base < 0:
            raise ErrorDatosInvalidos("La tarifa base no puede ser un valor negativo.")
        self.tarifa_base = tarifa_base

    @abc.abstractmethod
    def calcular_costo(self, tiempo: int, *args, **kwargs) -> float:
        """Metodo polinomico para calcular los costos especificos de cada servicio."""
        pass

    def obtener_detalles(self) -> str:
        return f"Servicio [{self.id_servicio}]: {self.nombre_servicio} | Tarifa Base: ${self.tarifa_base:.2f}"

# =====================================================================
# 6. SUBCLASES ESPECIALIZADAS (Polimorfismo y Sobrecarga)
# =====================================================================
class ReservaSala(Servicio):
    """Servicio especializado en la reserva de salas fisicas o de co-working."""
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, capacidad: int):
        super().__init__(id_servicio, nombre_servicio, tarifa_base)
        if capacidad <= 0:
            raise ErrorDatosInvalidos("La capacidad de la sala debe ser mayor a cero.")
        self.capacidad = capacidad

    def calcular_costo(self, horas: int, *args, **kwargs) -> float:
        if horas <= 0:
            raise ErrorDatosInvalidos("Las horas de reserva de la sala deben ser mayores a cero.")
        costo_total = self.tarifa_base * horas
        if kwargs.get("tecnologia_avanzada", False):
            costo_total += 50.0
        if kwargs.get("catering", False):
            costo_total += 20.0 * horas
        return costo_total

class AlquilerEquipo(Servicio):
    """Servicio especializado en el prestamo o alquiler de hardware."""
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, stock_disponible: int):
        super().__init__(id_servicio, nombre_servicio, tarifa_base)
        self.stock_disponible = stock_disponible

    def calcular_costo(self, dias: int, *args, **kwargs) -> float:
        if self.stock_disponible <= 0:
            raise ErrorServicioNoDisponible(f"No hay stock disponible para el equipo: {self.nombre_servicio}")
        if dias <= 0:
            raise ErrorDatosInvalidos("Los dias de alquiler deben ser mayores a cero.")
        costo_total = self.tarifa_base * dias
        if args:
            descuento = args[0]
            if isinstance(descuento, (int, float)) and 0 <= descuento <= 1:
                costo_total -= (costo_total * descuento)
        return costo_total

class AsesoriaEspecializada(Servicio):
    """Servicio de consultoria tecnica o arquitectonica de software."""
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, consultor_asignado: str):
        super().__init__(id_servicio, nombre_servicio, tarifa_base)
        if not consultor_asignado:
            raise ErrorDatosInvalidos("Toda asesoria debe tener un consultor asignado.")
        self.consultor_asignado = consultor_asignado

    def calcular_costo(self, horas: int, *args, **kwargs) -> float:
        if horas <= 0:
            raise ErrorDatosInvalidos("Las horas de asesoria deben ser superiores a cero.")
        costo_total = self.tarifa_base * horas
        if kwargs.get("es_extranjero", False):
            costo_total *= 1.19
        return costo_total

# =====================================================================
# 7. CLASE RESERVA CON MANEJO AVANZADO DE EXCEPCIONES
# =====================================================================
class Reserva(EntidadSistema):
    """Clase transaccional que integra Cliente, Servicio y controla el flujo."""
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int, **opciones_costo):
        if not id_reserva:
            raise ErrorReservaInvalida("El ID de la reserva no puede estar vacio.")
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.opciones_costo = opciones_costo
        self.costo_calculado = 0.0

    def procesar_reserva(self):
        try:
            registrar_log("INFO", f"Iniciando procesamiento de Reserva {self.id_reserva}")
            self.costo_calculado = self.servicio.calcular_costo(self.duracion, **self.opciones_costo)
        except ErrorSoftwareFJ as e:
            self.estado = "FALLIDA"
            raise ErrorReservaInvalida(f"No se pudo procesar la reserva {self.id_reserva} por error de negocio.") from e
        except Exception as e:
            self.estado = "ERRONEA"
            raise ErrorReservaInvalida(f"Fallo critico inesperado en la Reserva {self.id_reserva}") from e
        else:
            self.estado = "CONFIRMADA"
            registrar_log("SUCCESS", f"Reserva {self.id_reserva} procesada con exito por ${self.costo_calculado:.2f}")
        finally:
            registrar_log("INFO", f"Finalizo evaluacion de la Reserva {self.id_reserva}. Estado actual: {self.estado}")

    def cancelar_reserva(self):
        if self.estado == "CANCELADA":
            raise ErrorReservaInvalida(f"La reserva {self.id_reserva} ya se encuentra cancelada.")
        self.estado = "CANCELADA"
        registrar_log("INFO", f"Reserva {self.id_reserva} ha sido cancelada por el cliente.")

    def obtener_detalles(self) -> str:
        return (f"Reserva: {self.id_reserva} | Estado: {self.estado} | Costo: ${self.costo_calculado:.2f}\n"
                f"\t-> {self.cliente.obtener_detalles()}\n"
                f"\t-> {self.servicio.obtener_detalles()}")

# =====================================================================
# 8. BANCO DE PRUEBAS AUTOMATIZADO - EJECUCIÓN DIRECTA Y LINEAL
# =====================================================================
# =====================================================================
# 8. BANCO DE PRUEBAS AUTOMATIZADO (CONFORME A LA GUÍA UNAD)
# =====================================================================

def ejecutar_simulacion_completa():
    print("=" * 70)
    print(" SISTEMA INTEGRAL DE GESTIÓN SOFTWARE FJ - INICIO DE SIMULACIÓN ")
    print("=" * 70)

    # Inicialización limpia del archivo log
    with open("software_fj.log", "w", encoding="utf-8") as f:
        f.write("=== LOG DE OPERACIONES DE SOFTWARE FJ ===\n")

    clientes_registrados = []
    servicios_disponibles = []

    # -----------------------------------------------------------------
    print("\n[PRUEBA 1] Registro exitoso de clientes (Encapsulamiento)")
    # -----------------------------------------------------------------
    try:
        c1 = Cliente("CLI001", "Diana Arismendi", "diana.a@softwarefj.com")
        c2 = Cliente("CLI002", "Carlos Mendoza", "carlos.m@gmail.com")
        clientes_registrados.extend([c1, c2])
        print("-> [ÉXITO] Clientes creados correctamente.")
        print(f"   * {c1.obtener_detalles()}")
    except ErrorDatosInvalidos as e:
        print(f"-> [ERROR INESPERADO]: {e}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 2] Validación de datos: Formato de correo erróneo")
    # -----------------------------------------------------------------
    try:
        c_malo = Cliente("CLI003", "Juan Perez", "juan_perez_sin_arroba.com")
    except ErrorDatosInvalidos as e:
        registrar_log("ERROR", f"Prueba 2 - Captura correcta: {e}")
        print(f"-> [ÉXITO CONTROLADO] Excepción capturada: {e}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 3] Validación de datos: ID demasiado corto")
    # -----------------------------------------------------------------
    try:
        c_malo2 = Cliente("123", "Ana Gomez", "ana@gomez.com")
    except ErrorDatosInvalidos as e:
        registrar_log("ERROR", f"Prueba 3 - Captura correcta: {e}")
        print(f"-> [ÉXITO CONTROLADO] Excepción capturada: {e}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 4] Instanciación del catálogo mediante Polimorfismo")
    # -----------------------------------------------------------------
    try:
        s_sala = ReservaSala("SRV-SAL01", "Sala de Innovación", tarifa_base=45.0, capacidad=12)
        s_equipo = AlquilerEquipo("SRV-EQ02", "Servidor Dedicado", tarifa_base=120.0, stock_disponible=3)
        s_asesoria = AsesoriaEspecializada("SRV-ASE03", "Consultoría Cloud", tarifa_base=85.0, consultor_asignado="Ing. Andrés Restrepo")
        servicios_disponibles.extend([s_sala, s_equipo, s_asesoria])
        print("-> [ÉXITO] Servicios catalogados bajo la interfaz común 'Servicio'.")
    except ErrorDatosInvalidos as e:
        print(f"-> [ERROR INESPERADO]: {e}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 5] Validación de negocio: Tarifa base negativa")
    # -----------------------------------------------------------------
    try:
        s_malo = ReservaSala("SRV-ERR", "Sala VIP", tarifa_base=-25.0, capacidad=5)
    except ErrorDatosInvalidos as e:
        registrar_log("ERROR", f"Prueba 5 - Captura correcta: {e}")
        print(f"-> [ÉXITO CONTROLADO] Excepción capturada: {e}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 6] Flujo Transaccional Completo (try/except/else/finally)")
    # -----------------------------------------------------------------
    # Evaluamos el camino feliz: sin errores de cálculo ni de datos
    res1 = Reserva("RES-2026-001", clientes_registrados[0], servicios_disponibles[0], duracion=4, tecnologia_avanzada=True)
    res1.procesar_reserva()
    print(f"-> [ÉXITO]\n{res1.obtener_detalles()}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 7] Simulación de Sobrecarga por firma (Asesoría Extranjera)")
    # -----------------------------------------------------------------
    # Se evalúa el cálculo aplicando el recargo impositivo del 19% por kwargs
    res2 = Reserva("RES-2026-002", clientes_registrados[1], servicios_disponibles[2], duracion=10, es_extranjero=True)
    res2.procesar_reserva()
    print(f"-> [ÉXITO]\n{res2.obtener_detalles()}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 8] Encadenamiento de Excepciones ('raise ... from e')")
    # -----------------------------------------------------------------
    # Forzamos un error de negocio (duración 0) para ver cómo Reserva preserva la causa raíz
    try:
        res_error = Reserva("RES-2026-003", clientes_registrados[0], servicios_disponibles[0], duracion=0)
        res_error.procesar_reserva()
    except ErrorReservaInvalida as e:
        registrar_log("CRITICAL", f"Prueba 8 - Fallo integrado: {e}")
        print(f"-> [ÉXITO CONTROLADO] Transacción rechazada limpiamente.")
        print(f"   * Excepción principal: {e}")
        print(f"   * Causa raíz original (__cause__): {e.__cause__}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 9] Control de Estado y Bloqueo de Stock")
    # -----------------------------------------------------------------
    try:
        # Agotamos el stock a propósito
        servicios_disponibles[1].stock_disponible = 0
        res_stock = Reserva("RES-2026-004", clientes_registrados[0], servicios_disponibles[1], duracion=3)
        res_stock.procesar_reserva()
    except ErrorReservaInvalida as e:
        registrar_log("ERROR", f"Prueba 9 - Stock agotado: {e}")
        print(f"-> [ÉXITO CONTROLADO] Bloqueo exitoso. Causa: {e.__cause__}")

    # -----------------------------------------------------------------
    print("\n[PRUEBA 10] Máquina de estados: Evitar doble cancelación")
    # -----------------------------------------------------------------
    try:
        res1.cancelar_reserva() # Primera cancelación: OK
        res1.cancelar_reserva() # Segunda cancelación: Debe estallar
    except ErrorReservaInvalida as e:
        registrar_log("WARNING", f"Prueba 10 - Intento redundante: {e}")
        print(f"-> [ÉXITO CONTROLADO] Control de estado de flujo verificado: {e}")

    print("\n" + "=" * 70)
    print(" SIMULACIÓN FINALIZADA CON ÉXITO - TODOS LOS CRITERIOS EVALUADOS ")
    print(" Revise el archivo 'software_fj.log' para comprobar la auditoría. ")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_simulacion_completa()

