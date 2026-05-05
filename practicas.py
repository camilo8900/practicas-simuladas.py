import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod
import datetime

# ================== LOGGER ==================
class Logger:
    @staticmethod
    def log(mensaje):
        with open("logs.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} - {mensaje}\n")


# ================== EXCEPCIONES ==================
class SistemaError(Exception):
    pass

class ClienteError(SistemaError):
    pass

class ServicioError(SistemaError):
    pass

class ReservaError(SistemaError):
    pass


# ================== CLASE ABSTRACTA ==================
class Entidad(ABC):
    def __init__(self, id):
        self._id = id

    @abstractmethod
    def mostrar(self):
        pass


# ================== CLIENTE ==================
class Cliente(Entidad):
    def __init__(self, id, nombre, email):
        super().__init__(id)
        if not nombre:
            raise ClienteError("Nombre inválido")
        if "@" not in email:
            raise ClienteError("Email inválido")

        self.__nombre = nombre
        self.__email = email

    def mostrar(self):
        return f"{self.__nombre} ({self.__email})"

    def get_nombre(self):
        return self.__nombre


# ================== SERVICIO ABSTRACTO ==================
class Servicio(Entidad):
    def __init__(self, id, nombre, tarifa_base):
        super().__init__(id)

        if not nombre:
            raise ServicioError("Nombre de servicio inválido")
        if tarifa_base <= 0:
            raise ServicioError("Tarifa base inválida")

        self._nombre = nombre
        self._tarifa_base = tarifa_base

    def mostrar(self):
        return f"{self._nombre} - Tarifa: {self._tarifa_base}"

    def convertir_a_horas(self, cantidad, unidad):
        try:
            if cantidad <= 0:
                raise ServicioError("Cantidad inválida")

            unidad = unidad.lower()

            if unidad == "horas":
                return cantidad
            elif unidad == "días" or unidad == "dias":
                return cantidad * 24
            elif unidad == "semanas":
                return cantidad * 24 * 7
            else:
                raise ServicioError("Unidad de tiempo no válida")

        except Exception as e:
            Logger.log(f"Error al convertir tiempo: {str(e)}")
            raise ServicioError("Error en conversión de tiempo") from e

    @abstractmethod
    def calcular_costo(self, cantidad, unidad):
        pass


# ================== SERVICIOS ==================
class ReservaSala(Servicio):
    def __init__(self, id, tarifa):
        super().__init__(id, "Reserva de Sala", tarifa)

    def calcular_costo(self, cantidad, unidad):
        horas = self.convertir_a_horas(cantidad, unidad)
        return self._tarifa_base * horas


class AlquilerEquipo(Servicio):
    def __init__(self, id, tarifa):
        super().__init__(id, "Alquiler de Equipo", tarifa)

    def calcular_costo(self, cantidad, unidad):
        horas = self.convertir_a_horas(cantidad, unidad)
        return self._tarifa_base * horas * 0.8


class Asesoria(Servicio):
    def __init__(self, id, tarifa):
        super().__init__(id, "Asesoría Especializada", tarifa)

    def calcular_costo(self, cantidad, unidad):
        horas = self.convertir_a_horas(cantidad, unidad)
        return self._tarifa_base * horas * 1.2


# ============= RESERVAS ============
class Reserva:

    def _init_(self, cliente, servicio, cantidad, tipo_tiempo):
        if cantidad <= 0:
            raise ReservaError("Tiempo inválido")

        self._cliente = cliente
        self._servicio = servicio
        self._cantidad = cantidad
        self._tipo_tiempo = tipo_tiempo
        self._estado = "pendiente"

    def confirmar(self):
        if self._estado != "pendiente":
            raise ReservaError("Solo reservas pendientes pueden confirmarse")
        self._estado = "confirmada"

    def procesar(self):
        try:
            self.confirmar()
            costo = self._servicio.calcular_costo(self._cantidad, self._tipo_tiempo)
            self._estado = "procesada"
            return costo
        except Exception as e:
            Logger.log(f"Error al procesar: {e}")
            raise ReservaError("Error en procesamiento") from e

    def mostrar(self):
        return f"{self._cliente.mostrar()} | {self._servicio.mostrar()} | Estado: {self._estado}"


# ================== SISTEMA ==================
class Sistema:
    def _init_(self):
        self.clientes = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)

    def crear_reserva(self, reserva):
        self.reservas.append(reserva)


# ================== INTERFAZ ==================
class App:
    def __init__(self, root):
        self.sistema = Sistema()
        self.root = root
        self.root.title("Software FJ")

        # CLIENTE
        tk.Label(root, text="Nombre").grid(row=0, column=0)
        self.nombre = tk.Entry(root)
        self.nombre.grid(row=0, column=1)

        tk.Label(root, text="Email").grid(row=1, column=0)
        self.email = tk.Entry(root)
        self.email.grid(row=1, column=1)

        tk.Button(root, text="Agregar Cliente", command=self.agregar_cliente).grid(row=2, column=1)

        # SERVICIO
        tk.Label(root, text="Servicio").grid(row=3, column=0)
        self.tipo_servicio = tk.StringVar(value="Sala")

        tk.OptionMenu(root, self.tipo_servicio, "Sala", "Equipo", "Asesoria").grid(row=3, column=1)

        # TIEMPO
        tk.Label(root, text="Cantidad").grid(row=4, column=0)
        self.tiempo = tk.Entry(root)
        self.tiempo.grid(row=4, column=1)

        tk.Label(root, text="Unidad").grid(row=5, column=0)
        self.tipo_tiempo = tk.StringVar(value="horas")

        tk.OptionMenu(root, self.tipo_tiempo, "horas", "dias", "semanas").grid(row=5, column=1)

        tk.Button(root, text="Crear Reserva", command=self.crear_reserva).grid(row=6, column=1)

    def agregar_cliente(self):
        try:
            cliente = Cliente(len(self.sistema.clientes), self.nombre.get(), self.email.get())
            self.sistema.agregar_cliente(cliente)
            messagebox.showinfo("Éxito", "Cliente agregado")
        except Exception as e:
            Logger.log(str(e))
            messagebox.showerror("Error", str(e))

    def crear_reserva(self):
        try:
            if not self.sistema.clientes:
                raise ReservaError("No hay clientes")

            cliente = self.sistema.clientes[-1]

            tipo = self.tipo_servicio.get()

            if tipo == "Sala":
                servicio = ReservaSala(1, 50)
            elif tipo == "Equipo":
                servicio = AlquilerEquipo(2, 30)
            else:
                servicio = Asesoria(3, 80)

            cantidad = int(self.tiempo.get())
            tipo_tiempo = self.tipo_tiempo.get()

            reserva = Reserva(cliente, servicio, cantidad, tipo_tiempo)
            costo = reserva.procesar()

            self.sistema.crear_reserva(reserva)

            messagebox.showinfo(
                "Reserva Exitosa",
                f"Cliente: {cliente.get_nombre()}\n"
                f"Servicio: {servicio._nombre}\n"
                f"Tiempo: {cantidad} {tipo_tiempo}\n"
                f"Costo Total: ${costo}"
            )

        except Exception as e:
            Logger.log(str(e))
            messagebox.showerror("Error", str(e))


# ================== MAIN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
