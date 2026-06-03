
tools.py — Herramientas del Agente de Helpdesk TechStore
Cada herramienta está decorada con @tool de LangChain para que el agente
pueda seleccionarlas y ejecutarlas de forma autónoma (IE1).
"""
 
import json
import os
from langchain.tools import tool
 
# Ruta al archivo de datos
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faq.json")
 
def _cargar_datos() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
 
 

# HERRAMIENTA 1: Consulta de FAQ (herramienta de CONSULTA)

@tool
def buscar_faq(consulta: str) -> str:
    """
    Busca en la base de preguntas frecuentes de TechStore.
    Usar cuando el cliente pregunta sobre políticas, envíos, pagos,
    garantías, devoluciones o información general de la tienda.
    """
    datos = _cargar_datos()
    consulta_lower = consulta.lower()
 
    for item in datos["faqs"]:
        palabras_clave = item["pregunta"].lower().split()
        if any(palabra in consulta_lower for palabra in palabras_clave):
            return f"📋 Información encontrada: {item['respuesta']}"
 
    return "No encontré información específica sobre eso en nuestra base de conocimiento."
 
 
# HERRAMIENTA 2: Consulta de estado de pedido (herramienta de CONSULTA API)

@tool
def consultar_estado_pedido(numero_pedido: str) -> str:
    """
    Consulta el estado actual de un pedido por su número de orden.
    El número de pedido tiene el formato ORD-XXX (ej: ORD-001).
    Usar cuando el cliente pregunta por su pedido, envío o entrega.
    """
    datos = _cargar_datos()
    numero_pedido = numero_pedido.strip().upper()
    pedidos = datos.get("pedidos", {})
 
    if numero_pedido in pedidos:
        info = pedidos[numero_pedido]
        return (
            f"📦 Pedido {numero_pedido}:\n"
            f"   Estado: {info['estado']}\n"
            f"   Entrega estimada: {info['llegada']}"
        )
    return f"No encontré el pedido {numero_pedido}. Verifica el número e intenta nuevamente."
 

# HERRAMIENTA 3: Calcular reembolso (herramienta de RAZONAMIENTO/CÁLCULO)

@tool
def calcular_reembolso(monto_compra: float, dias_desde_compra: int) -> str:
    """
    Calcula el monto de reembolso según la política de devoluciones de TechStore.
    Usar cuando el cliente quiere saber cuánto dinero recibirá de vuelta
    por una devolución. Requiere el monto de la compra y los días transcurridos.
    """
    datos = _cargar_datos()
    politica = datos["politica_reembolso"]
 
    if dias_desde_compra <= 7:
        porcentaje = politica["dentro_7_dias"]
    elif dias_desde_compra <= 30:
        porcentaje = politica["entre_8_y_30_dias"]
    else:
        porcentaje = politica["despues_30_dias"]
 
    monto_reembolso = (monto_compra * porcentaje) / 100
 
    if porcentaje == 0:
        return (
            f"❌ Lo sentimos, han pasado {dias_desde_compra} días desde la compra. "
            f"Nuestra política de devoluciones cubre hasta 30 días. No es posible procesar el reembolso."
        )
 
    return (
        f"💰 Cálculo de reembolso:\n"
        f"   Monto original: ${monto_compra:,.0f}\n"
        f"   Días desde la compra: {dias_desde_compra}\n"
        f"   Porcentaje de reembolso: {porcentaje}%\n"
        f"   Monto a reembolsar: ${monto_reembolso:,.0f}"
    )
 
 

# HERRAMIENTA 4: Crear ticket de soporte (herramienta de ESCRITURA)

@tool
def crear_ticket_soporte(descripcion_problema: str) -> str:
    """
    Crea un ticket de soporte cuando el agente no puede resolver el problema
    directamente o cuando el cliente necesita atención personalizada.
    Usar como último recurso cuando otras herramientas no resuelven la consulta.
    """
    import random
    import datetime
 
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
 
    return (
        f"✅ Ticket de soporte creado exitosamente:\n"
        f"   ID: {ticket_id}\n"
        f"   Fecha: {fecha}\n"
        f"   Problema: {descripcion_problema}\n"
        f"   Un agente humano se contactará contigo en las próximas 24 horas."
    )
 
 
# Lista de todas las herramientas disponibles para el agente
TOOLS = [
    buscar_faq,
    consultar_estado_pedido,
    calcular_reembolso,
    crear_ticket_soporte,
]
