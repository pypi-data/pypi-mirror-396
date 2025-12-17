# accesibilidad.py
from .motor_voz import MotorVoz
from .motor_imagen import MotorImagen

class Accesibilidad:

    def __init__(self):
        self.motor_voz = MotorVoz()
        self.motor_imagen = MotorImagen()

    # -------- REGISTRO DE COMANDOS --------

    def registrar_comando_voz(self, frase, accion):
        """
        Registra un comando por voz
        """
        self.motor_voz.registrar_comando(frase, accion)

    def registrar_comando_gesto(self, dedos, accion):
        """
        Registra un comando por gesto (cantidad de dedos)
        """
        self.motor_imagen.registrar_comando(dedos, accion)

    # -------- ESCUCHA --------

    def escuchar_voz(self):
        """
        Escucha por micrófono y devuelve una acción
        """
        return self.motor_voz.escuchar()

    def escuchar_gesto(self):
        """
        Escucha por cámara y devuelve una acción
        """
        return self.motor_imagen.detectar()
