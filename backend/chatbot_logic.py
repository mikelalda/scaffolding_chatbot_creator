# --- START OF FILE chatbot_logic.py ---

import re
import random

class ChatbotLogic:
    def __init__(self, data):
        self.data = data
        self.state = "initial"
        self.step = 0
        self.error_count = 0

    def get_response(self, user_input):
        ui = user_input.lower().strip()

        # Comandos de reinicio y salida que funcionan en cualquier estado
        if re.search(r"\b(empezar|reiniciar|otra|nuevo)\b", ui):
            self.state = "initial"
            self.step = 0
            self.error_count = 0
            # --- MODIFICADO: Añadido 'practicar' a la comprobación de reinicio ---
            if re.search(r"^(practicar|pr[aá]ctica)$|(ejercicio|pr[aá]ctica)", ui):
                return self.start_solving()
            return "¡Listo para empezar de nuevo! Puedes preguntarme algo o decir 'practicar' para empezar un ejercicio."
        
        if re.search(r"\b(adi[oó]s|salir|terminar|chao)\b", ui):
            self.state = "initial"
            self.step = 0
            self.error_count = 0
            return "¡Adiós! Espero haberte ayudado. ¡Vuelve cuando quieras!"

        # Estado inicial: responder FAQs, listar preguntas, o iniciar la resolución
        if self.state == "initial":
            if re.search(r"^(qu[eé] preguntas|preguntas|listar preguntas|ayuda|dime las preguntas|qu[eé] te puedo preguntar|men[uú])$", ui):
                faqs = self.data.get("faq", [])
                if not faqs:
                    return "No tengo preguntas frecuentes predefinidas en este momento. ¡Pero puedes intentar preguntarme lo que quieras sobre el tema!"
                
                response_lines = ["¡Claro! Puedes preguntarme sobre cualquiera de estos temas:"]
                for faq in faqs:
                    response_lines.append(f"  - {faq.get('pregunta', 'Pregunta sin definir')}")
                
                return "\n".join(response_lines)

            # Buscar coincidencia en preguntas frecuentes
            for faq in self.data.get("faq", []):
                pattern = faq.get("pattern", "")
                if pattern and re.search(pattern, ui):
                    return faq.get("respuesta", "")
            
            # --- MODIFICADO: Expresión regular para iniciar la práctica ---
            # Ahora acepta 'practicar' o 'práctica' por sí solas.
            practice_pattern = r"^(practicar|pr[aá]ctica)$|(practicar|resolver|intentar|probar|ay[uú]dame|gu[ií]ame).*(ejercicio|pr[aá]ctica)"
            if re.search(practice_pattern, ui):
                return self.start_solving()

            return "No entendí. Puedes preguntarme algo sobre el tema, decir 'preguntas' para ver una lista de sugerencias, o escribir 'practicar' para empezar un ejercicio."

        # Estado de resolución paso a paso (sin cambios)
        elif self.state == "resolviendo":
            pasos = self.data.get("resolucion", [])
            if self.step < len(pasos):
                current_step_data = pasos[self.step]
                pattern = current_step_data.get("pattern", "")
                
                if pattern and re.search(pattern, ui):
                    self.error_count = 0
                    feedbacks = self.data.get("feedback_positivo", ["¡Muy bien!"])
                    resp = random.choice(feedbacks)
                    if current_step_data.get("respuesta"):
                        resp += " " + current_step_data.get("respuesta")
                    
                    self.step += 1
                    
                    if self.step < len(pasos):
                        next_instruction = pasos[self.step].get("instruccion", "")
                        if next_instruction:
                            resp += "\n" + next_instruction
                    else:
                        resp += "\n¡Felicidades, has completado todos los pasos! ¿Quieres practicar otra vez o preguntar algo más?"
                        self.state = "initial"
                        self.step = 0
                    
                    return resp
                else:
                    self.error_count += 1
                    if self.error_count > 2:
                        self.state = "initial"
                        self.step = 0
                        self.error_count = 0
                        return "Parece que te has atascado. No te preocupes, ¡es normal! Vamos a empezar de nuevo. Di 'practicar' cuando estés listo."
                    
                    pista = current_step_data.get("pista", "")
                    if not pista:
                        pista = "Intenta de nuevo. " + current_step_data.get("instruccion", "¿Cuál es el siguiente paso?")
                    
                    return f"Mmm, no es exactamente eso. Pista: {pista}"
            else:
                self.state = "initial"
                self.step = 0
                return "¡Has terminado! ¿Quieres practicar otra vez o preguntar algo más?"

        # Fallback
        return "No entendí tu mensaje."

    def start_solving(self):
        """Función auxiliar para iniciar el proceso de resolución."""
        self.state = "resolviendo"
        self.step = 0
        self.error_count = 0
        pasos = self.data.get("resolucion", [])
        if pasos and pasos[0].get("instruccion"):
            return "¡Excelente! Vamos a resolver un ejercicio juntos.\n" + pasos[0].get("instruccion")
        else:
            self.state = "initial"
            return "No hay pasos de resolución definidos. Por favor, un profesor debe agregarlos en la pestaña de 'Edición'."