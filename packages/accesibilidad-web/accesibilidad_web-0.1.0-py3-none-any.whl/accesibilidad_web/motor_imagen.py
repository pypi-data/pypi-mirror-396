# motor_imagen.py
import cv2
import numpy as np
import math

class MotorImagen:

    def __init__(self, camara=0):
        self.camara = camara
        self.comandos = {}  # {1: "INICIO", 2: "MENU"}

    def registrar_comando(self, dedos, accion):
        """
        dedos: int (1–10)
        accion: cualquier identificador
        """
        if 1 <= dedos <= 10:
            self.comandos[dedos] = accion

    def _contar_dedos(self, contorno):
        hull = cv2.convexHull(contorno, returnPoints=False)

        if hull is None or len(hull) < 3:
            return 0

        defects = cv2.convexityDefects(contorno, hull)
        if defects is None:
            return 0

        dedos = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contorno[s][0])
            end = tuple(contorno[e][0])
            far = tuple(contorno[f][0])

            a = math.dist(start, end)
            b = math.dist(start, far)
            c = math.dist(end, far)

            angulo = math.acos((b**2 + c**2 - a**2) / (2*b*c))

            if angulo < math.pi / 2:
                dedos += 1

        return dedos + 1  # dedos levantados

    def detectar(self, mostrar=True):
        cap = cv2.VideoCapture(self.camara)

        if not cap.isOpened():
            return "CMD_ERROR_CAMARA"

        print("📷 Muestra tu mano (presiona Q para salir)")

        accion = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Rango de piel
            bajo = np.array([0, 20, 70])
            alto = np.array([20, 255, 255])

            mask = cv2.inRange(hsv, bajo, alto)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            contornos, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if contornos:
                contorno = max(contornos, key=cv2.contourArea)

                if cv2.contourArea(contorno) > 5000:
                    dedos = self._contar_dedos(contorno)

                    cv2.putText(
                        frame,
                        f"Dedos: {dedos}",
                        (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                    if dedos in self.comandos:
                        accion = self.comandos[dedos]
                        break

            if mostrar:
                cv2.imshow("Motor Imagen - Gestos", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                accion = "CMD_CANCELADO"
                break

        cap.release()
        cv2.destroyAllWindows()
        return accion
