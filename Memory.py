
memory.py — Gestión de Memoria del Agente Helpdesk
Implementa tres estrategias de memoria (IE3, IE4):
  - Buffer completo: guarda todo el historial
  - Ventana (window): solo las últimas k interacciones
  - Resumen (summary): resume el historial para flujos prolongados
"""
 
from langchain_core.messages import HumanMessage, AIMessage
 
 
class MemoriaBuffer:
    """
    Memoria de buffer completo.
    Guarda cada mensaje de la conversación íntegramente.
    Ideal para conversaciones cortas donde el contexto completo importa.
    """
 
    def __init__(self):
        self.historial = []
 
    def agregar(self, pregunta: str, respuesta: str):
        self.historial.append(HumanMessage(content=pregunta))
        self.historial.append(AIMessage(content=respuesta))
 
    def obtener(self) -> list:
        return self.historial.copy()
 
    def limpiar(self):
        self.historial = []
 
    def resumen_estado(self) -> str:
        turnos = len(self.historial) // 2
        return f"[MemoriaBuffer] {turnos} turno(s) almacenado(s)"
 
 
class MemoriaVentana:
    """
    Memoria de ventana deslizante.
    Solo conserva las últimas k interacciones (cada interacción = 1 par usuario/asistente).
    Útil para flujos prolongados donde solo el contexto reciente importa.
    """
 
    def __init__(self, k: int = 3):
        self.k = k
        self.historial = []
 
    def agregar(self, pregunta: str, respuesta: str):
        self.historial.append(HumanMessage(content=pregunta))
        self.historial.append(AIMessage(content=respuesta))
        # Mantener solo las últimas k interacciones (k*2 mensajes)
        if len(self.historial) > self.k * 2:
            self.historial = self.historial[-(self.k * 2):]
 
    def obtener(self) -> list:
        return self.historial.copy()
 
    def limpiar(self):
        self.historial = []
 
    def resumen_estado(self) -> str:
        turnos = len(self.historial) // 2
        return f"[MemoriaVentana k={self.k}] {turnos}/{self.k} turno(s) en ventana"
 
 
class MemoriaResumen:
    """
    Memoria basada en resumen semántico.
    Usa el LLM para comprimir el historial en un resumen conciso.
    Permite mantener contexto en conversaciones muy largas sin exceder el límite de tokens.
    Implementa recuperación de contexto semántico (IE4).
    """
 
    def __init__(self, llm):
        self.llm = llm
        self.resumen = ""
        self.mensajes_recientes = []
 
    def agregar(self, pregunta: str, respuesta: str):
        self.mensajes_recientes.append(HumanMessage(content=pregunta))
        self.mensajes_recientes.append(AIMessage(content=respuesta))
        # Actualizar resumen cada 4 mensajes (2 turnos)
        if len(self.mensajes_recientes) >= 4:
            self._actualizar_resumen()
 
    def _actualizar_resumen(self):
        """Comprime el historial reciente en un resumen usando el LLM."""
        historial_texto = "\n".join([
            f"{'Usuario' if isinstance(m, HumanMessage) else 'Asistente'}: {m.content}"
            for m in self.mensajes_recientes
        ])
 
        prompt = f"""Resume esta conversación de soporte al cliente en 2-3 oraciones, 
conservando los datos clave (números de pedido, montos, problemas mencionados).
 
Resumen anterior: {self.resumen if self.resumen else 'Ninguno'}
 
Nueva conversación:
{historial_texto}
 
Resumen actualizado:"""
 
        respuesta = self.llm.invoke(prompt)
        self.resumen = respuesta.content
        self.mensajes_recientes = []
 
    def obtener(self) -> list:
        mensajes = []
        if self.resumen:
            mensajes.append(HumanMessage(
                content=f"[Contexto previo de la conversación]: {self.resumen}"
            ))
        mensajes.extend(self.mensajes_recientes)
        return mensajes
 
    def limpiar(self):
        self.resumen = ""
        self.mensajes_recientes = []
 
    def resumen_estado(self) -> str:
        tiene_resumen = "con resumen" if self.resumen else "sin resumen"
        recientes = len(self.mensajes_recientes) // 2
        return f"[MemoriaResumen] {tiene_resumen}, {recientes} mensaje(s) reciente(s)"
