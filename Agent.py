
"""
agent.py — Agente Principal de Helpdesk TechStore
Integra LLM, herramientas, memoria y planificación (IE1, IE2, IE3, IE4, IE5, IE6).
 
Arquitectura:
  Usuario → AgenteHelpdesk → [planificador] → herramientas → respuesta
                                    ↑
                               memoria activa
"""
 
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
 
from agent.tools import TOOLS
from agent.memory import MemoriaBuffer, MemoriaVentana, MemoriaResumen
 
# ─────────────────────────────────────────────
# SYSTEM PROMPT — Define el comportamiento y planificación del agente
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un agente de soporte al cliente de TechStore, una tienda de tecnología.
Tu objetivo es resolver las consultas de los clientes de forma eficiente y empática.
 
HERRAMIENTAS DISPONIBLES:
- buscar_faq: para preguntas sobre políticas, envíos, pagos, garantías
- consultar_estado_pedido: cuando el cliente menciona un número de pedido (formato ORD-XXX)
- calcular_reembolso: cuando el cliente quiere saber el monto de una devolución
- crear_ticket_soporte: solo cuando no puedes resolver el problema con las otras herramientas
 
ESTRATEGIA DE PLANIFICACIÓN (ejecuta en este orden):
1. ANALIZA la consulta del cliente
2. IDENTIFICA si necesitas una o más herramientas
3. EJECUTA las herramientas necesarias en orden lógico
4. SINTETIZA la información y responde de forma clara y amable
 
REGLAS:
- Siempre saluda al inicio de la conversación
- Si el cliente menciona un número de pedido, SIEMPRE consulta su estado
- Si el cliente quiere devolver algo, SIEMPRE calcula el reembolso si te dan el monto
- Crea un ticket solo si el problema es complejo o no tienes solución
- Responde siempre en español
- Sé breve, claro y empático
"""
 
 
class AgenteHelpdesk:
    """
    Agente de soporte al cliente con memoria configurable y planificación adaptativa.
    """
 
    def __init__(self, tipo_memoria: str = "ventana"):
        """
        Args:
            tipo_memoria: 'buffer' | 'ventana' | 'resumen'
        """
        # Configurar LLM (igual que el notebook del curso)
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            openai_api_base=os.environ.get("OPENAI_BASE_URL"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            temperature=0
        )
 
        # Crear agente con herramientas (IE1, IE2)
        self.agente = create_agent(
            model=self.llm,
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT
        )
 
        # Configurar memoria según tipo (IE3, IE4)
        self.tipo_memoria = tipo_memoria
        if tipo_memoria == "buffer":
            self.memoria = MemoriaBuffer()
        elif tipo_memoria == "resumen":
            self.memoria = MemoriaResumen(llm=self.llm)
        else:
            self.memoria = MemoriaVentana(k=3)
 
        print(f"✅ Agente Helpdesk TechStore iniciado")
        print(f"   Memoria: {tipo_memoria}")
        print(f"   Herramientas: {[t.name for t in TOOLS]}")
 
    def chat(self, mensaje_usuario: str) -> str:
        """
        Procesa un mensaje del usuario y retorna la respuesta del agente.
        Implementa el ciclo completo: memoria → agente → herramientas → respuesta
        """
        # Recuperar historial de memoria (IE3, IE4)
        historial = self.memoria.obtener()
 
        # Construir lista de mensajes con historial + nuevo mensaje
        mensajes = historial + [{"role": "user", "content": mensaje_usuario}]
 
        # Invocar al agente (IE5, IE6 — el agente decide qué herramientas usar)
        respuesta = self.agente.invoke({"messages": mensajes})
        texto_respuesta = respuesta["messages"][-1].content
 
        # Guardar en memoria
        self.memoria.agregar(mensaje_usuario, texto_respuesta)
 
        return texto_respuesta
 
    def estado_memoria(self) -> str:
        return self.memoria.resumen_estado()
 
    def reiniciar(self):
        self.memoria.limpiar()
        print("🔄 Memoria reiniciada.")
