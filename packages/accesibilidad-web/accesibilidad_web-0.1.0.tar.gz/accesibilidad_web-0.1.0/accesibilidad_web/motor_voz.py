# motor_voz.py
import speech_recognition as sr

class MotorVoz:

    def __init__(self, idioma='es-ES'):
        self.recognizer = sr.Recognizer()
        self.idioma = idioma
        self.comandos = {}  # {"ir al menu": "MENU"}

    def registrar_comando(self, frase, accion):
        """
        Permite al programador registrar comandos personalizados
        """
        self.comandos[frase.lower()] = accion

    def escuchar(self, timeout=10, phrase_time_limit=10):
        with sr.Microphone() as mic:
            self.recognizer.adjust_for_ambient_noise(mic, duration=1)
            print("🎤 Puedes hablar...")

            try:
                audio = self.recognizer.listen(
                    mic,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                texto = self.recognizer.recognize_google(audio, language=self.idioma)
                texto = texto.lower()
                print("🗣️ Dijiste:", texto)

                for frase, accion in self.comandos.items():
                    if frase in texto:
                        print("Comando reconocido:", frase)
                        return accion

                return "CMD_NO_RECONOCIDO"

            except sr.WaitTimeoutError:
                return "CMD_TIMEOUT"
            except sr.UnknownValueError:
                return "CMD_ININTELIGIBLE"
            except Exception as e:
                print("❌ Error:", e)
                return "CMD_ERROR"
