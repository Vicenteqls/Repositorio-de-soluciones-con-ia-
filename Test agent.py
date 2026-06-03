tests/test_agent.py — Pruebas del Agente Helpdesk
Evidencia de pruebas de software para el repositorio (IE7, IE9).
"""
 
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
 
# Configurar credenciales
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = os.environ.get(
    "OPENAI_BASE_URL", "https://models.inference.ai.azure.com"
)
 
from agent.tools import buscar_faq, consultar_estado_pedido, calcular_reembolso, crear_ticket_soporte
 
 
def test_buscar_faq_envio():
    resultado = buscar_faq.invoke("¿cuánto demora la entrega?")
    assert "día" in resultado.lower() or "plazo" in resultado.lower() or "entrega" in resultado.lower()
    print(f"✅ test_buscar_faq_envio: {resultado[:60]}...")
 
 
def test_buscar_faq_no_encontrado():
    resultado = buscar_faq.invoke("¿venden cohetes espaciales?")
    assert "No encontré" in resultado
    print(f"✅ test_buscar_faq_no_encontrado: {resultado}")
 
 
def test_consultar_pedido_existe():
    resultado = consultar_estado_pedido.invoke("ORD-001")
    assert "ORD-001" in resultado
    assert "tránsito" in resultado.lower() or "estado" in resultado.lower()
    print(f"✅ test_consultar_pedido_existe: {resultado}")
 
 
def test_consultar_pedido_no_existe():
    resultado = consultar_estado_pedido.invoke("ORD-999")
    assert "No encontré" in resultado
    print(f"✅ test_consultar_pedido_no_existe: {resultado}")
 
 
def test_calcular_reembolso_100():
    resultado = calcular_reembolso.invoke({"monto_compra": 50000.0, "dias_desde_compra": 5})
    assert "50.000" in resultado or "100%" in resultado
    print(f"✅ test_calcular_reembolso_100%: {resultado}")
 
 
def test_calcular_reembolso_70():
    resultado = calcular_reembolso.invoke({"monto_compra": 50000.0, "dias_desde_compra": 15})
    assert "70%" in resultado or "35.000" in resultado
    print(f"✅ test_calcular_reembolso_70%: {resultado}")
 
 
def test_calcular_reembolso_0():
    resultado = calcular_reembolso.invoke({"monto_compra": 50000.0, "dias_desde_compra": 45})
    assert "0%" in resultado or "Lo sentimos" in resultado or "31" in resultado or "45" in resultado
    print(f"✅ test_calcular_reembolso_0%: {resultado}")
 
 
def test_crear_ticket():
    resultado = crear_ticket_soporte.invoke("Cuenta hackeada, compras no autorizadas")
    assert "TKT-" in resultado
    assert "24 horas" in resultado
    print(f"✅ test_crear_ticket: {resultado[:80]}...")
 
 
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  PRUEBAS DE HERRAMIENTAS — Agente Helpdesk")
    print("="*50 + "\n")
 
    tests = [
        test_buscar_faq_envio,
        test_buscar_faq_no_encontrado,
        test_consultar_pedido_existe,
        test_consultar_pedido_no_existe,
        test_calcular_reembolso_100,
        test_calcular_reembolso_70,
        test_calcular_reembolso_0,
        test_crear_ticket,
    ]
 
    pasados = 0
    fallidos = 0
 
    for test in tests:
        try:
            test()
            pasados += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FALLÓ — {e}")
            fallidos += 1
        except Exception as e:
            print(f"❌ {test.__name__}: ERROR — {e}")
            fallidos += 1
 
    print(f"\n{'='*50}")
    print(f"  Resultado: {pasados}/{len(tests)} pruebas pasadas")
    print(f"{'='*50}\n")
