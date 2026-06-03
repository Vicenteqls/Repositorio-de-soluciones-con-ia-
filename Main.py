
main.py — Demostración del Agente Helpdesk TechStore
Ejecuta escenarios que muestran planificación y toma de decisiones (IE5, IE6).
 
Uso:
    python main.py              # Modo demo automático
    python main.py --chat       # Modo conversación interactiva
"""
 
import os
import sys
 
# Configurar credenciales (GitHub Models API)
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = os.environ.get(
    "OPENAI_BASE_URL", "https://models.inference.ai.azure.com"
)
 
from agent.agent import AgenteHelpdesk
 
 
def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")
 
 
def demo_escenario(agente, titulo: str, mensajes: list):
    """Ejecuta un escenario de prueba mostrando el razonamiento del agente."""
    separador(titulo)
    for msg in mensajes:
        print(f"\n👤 Cliente: {msg}")
        respuesta = agente.chat(msg)
        print(f"🤖 Agente:  {respuesta}")
        print(f"   [{agente.estado_memoria()}]")
    agente.reiniciar()
 
 
def modo_demo():
    """
    Ejecuta escenarios predefinidos que demuestran:
    - IE5: Planificación de tareas (el agente decide qué herramienta usar)
    - IE6: Toma de decisiones adaptativa según el contexto
    """
 
    # ── ESCENARIO 1: Consulta simple de FAQ ──────────────────────────
    agente = AgenteHelpdesk(tipo_memoria="ventana")
    demo_escenario(agente, "ESCENARIO 1 — Consulta de política (FAQ)", [
        "Hola, ¿cuánto demora el envío?",
        "¿Y si quiero envío express?",
    ])
 
    # ── ESCENARIO 2: Seguimiento de pedido ───────────────────────────
    agente = AgenteHelpdesk(tipo_memoria="ventana")
    demo_escenario(agente, "ESCENARIO 2 — Estado de pedido", [
        "Quiero saber dónde está mi pedido ORD-001",
        "¿Y el ORD-003?",
    ])
 
    # ── ESCENARIO 3: Cálculo de reembolso ────────────────────────────
    agente = AgenteHelpdesk(tipo_memoria="ventana")
    demo_escenario(agente, "ESCENARIO 3 — Cálculo de devolución", [
        "Compré un producto hace 5 días por $45.000 y lo quiero devolver",
        "¿Y si hubieran pasado 20 días?",
    ])
 
    # ── ESCENARIO 4: Múltiples herramientas en un flujo ───────────────
    agente = AgenteHelpdesk(tipo_memoria="buffer")
    demo_escenario(agente, "ESCENARIO 4 — Flujo complejo (planificación multi-paso)", [
        "Mi pedido ORD-002 llegó dañado, lo compré hace 3 días por $89.990",
        "¿Cuánto me devuelven?",
        "Ok, ¿cómo procedo con la devolución?",
    ])
 
    # ── ESCENARIO 5: Escalamiento a ticket ───────────────────────────
    agente = AgenteHelpdesk(tipo_memoria="ventana")
    demo_escenario(agente, "ESCENARIO 5 — Escalamiento a soporte humano", [
        "Mi cuenta fue hackeada y alguien hizo compras sin mi autorización",
    ])
 
    # ── ESCENARIO 6: Memoria de resumen en flujo largo ────────────────
    agente = AgenteHelpdesk(tipo_memoria="resumen")
    demo_escenario(agente, "ESCENARIO 6 — Memoria de resumen (flujo prolongado)", [
        "Hola, tengo varias preguntas",
        "¿Cuáles son los métodos de pago?",
        "¿Tienen garantía los productos?",
        "Mi pedido es el ORD-003, ¿cuándo llega?",
        "¿Ofrecen descuentos si compro 15 unidades?",
    ])
 
 
def modo_chat():
    """Modo interactivo para conversar con el agente."""
    separador("MODO INTERACTIVO — Agente Helpdesk TechStore")
    print("Escribe 'salir' para terminar | 'reiniciar' para nueva conversación\n")
 
    agente = AgenteHelpdesk(tipo_memoria="ventana")
 
    while True:
        try:
            entrada = input("👤 Tú: ").strip()
            if not entrada:
                continue
            if entrada.lower() == "salir":
                print("¡Hasta luego!")
                break
            if entrada.lower() == "reiniciar":
                agente.reiniciar()
                continue
 
            respuesta = agente.chat(entrada)
            print(f"🤖 Agente: {respuesta}")
            print(f"   [{agente.estado_memoria()}]\n")
 
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
 
 
if __name__ == "__main__":
    if "--chat" in sys.argv:
        modo_chat()
    else:
        modo_demo()
