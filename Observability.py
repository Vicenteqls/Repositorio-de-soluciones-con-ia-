import time
import json
import logging
import hashlib
import statistics
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("observabilidad")

json_logger = logging.getLogger("metricas_json")
json_logger.setLevel(logging.DEBUG)
json_handler = logging.FileHandler(
    os.path.join(LOG_DIR, "agent_execution.jsonl"), encoding="utf-8"
)
json_handler.setFormatter(logging.Formatter("%(message)s"))
json_logger.addHandler(json_handler)
json_logger.propagate = False

@dataclass
class MetricaEjecucion:
    timestamp: str
    query_id: str
    consulta: str
    respuesta: str
    latencia_segundos: float
    tokens_estimados: int
    herramientas_usadas: int
    exitoso: bool
    mensaje_error: Optional[str]
    hash_respuesta: str
    score_precision: float

class RecolectorMetricas:

    def __init__(self):
        self.metricas: list[MetricaEjecucion] = []
        self._cache_consistencia: dict[str, list[str]] = {}

    def registrar(self, metrica: MetricaEjecucion):
        self.metricas.append(metrica)

        json_logger.info(json.dumps(asdict(metrica), ensure_ascii=False))

        logger.info(
            f"[{metrica.query_id}] latencia={metrica.latencia_segundos*1000:.1f}ms | "
            f"tokens={metrica.tokens_estimados} | "
            f"herramientas={metrica.herramientas_usadas} | "
            f"precisión={metrica.score_precision:.2f} | "
            f"ok={metrica.exitoso}"
        )

        clave = hashlib.md5(metrica.consulta.lower().strip().encode()).hexdigest()[:8]
        self._cache_consistencia.setdefault(clave, []).append(metrica.hash_respuesta)

    def calcular_resumen(self) -> dict:
        if not self.metricas:
            return {}

        latencias   = [m.latencia_segundos for m in self.metricas]
        precisiones = [m.score_precision    for m in self.metricas]
        tokens      = [m.tokens_estimados   for m in self.metricas]
        errores     = [m for m in self.metricas if not m.exitoso]

        scores_consistencia = []
        for hashes in self._cache_consistencia.values():
            if len(hashes) > 1:
                unicos = len(set(hashes))
                scores_consistencia.append(1.0 if unicos == 1 else 1.0 / unicos)
        consistencia = (
            statistics.mean(scores_consistencia) if scores_consistencia else 1.0
        )

        latencias_sorted = sorted(latencias)
        p95_idx = int(len(latencias_sorted) * 0.95)

        return {
            "total_consultas"     : len(self.metricas),
            "tasa_errores"        : len(errores) / len(self.metricas),
            "latencia_promedio_s" : statistics.mean(latencias),
            "latencia_p95_s"      : latencias_sorted[p95_idx],
            "latencia_min_s"      : min(latencias),
            "latencia_max_s"      : max(latencias),
            "precision_promedio"  : statistics.mean(precisiones),
            "tokens_promedio"     : statistics.mean(tokens),
            "tokens_total"        : sum(tokens),
            "consistencia"        : consistencia,
            "herramientas_promedio": statistics.mean(
                [m.herramientas_usadas for m in self.metricas]
            ),
        }

def evaluar_precision(consulta: str, respuesta: str) -> float:

    q = consulta.lower()
    r = respuesta.lower()
    score = 0.5

    if len(respuesta.strip()) > 30:
        score += 0.1

    keywords_dominio = [
        "pedido", "estado", "envío", "reembolso", "garantía",
        "ticket", "ord-", "tkt-", "política", "techstore",
        "días", "pago", "compra", "devolución", "soporte",
    ]
    hits = sum(1 for kw in keywords_dominio if kw in r)
    score += min(0.2, hits * 0.04)

    if any(w in q for w in ["pedido", "ord-", "estado", "entrega"]):
        if "" in respuesta or "estado" in r or "ord-" in r:
            score += 0.15
        else:
            score -= 0.1

    if any(w in q for w in ["reembolso", "devolver", "devolución", "dinero"]):
        if "" in respuesta or "$" in respuesta or "%" in respuesta:
            score += 0.15
        else:
            score -= 0.1

    frases_error = ["no puedo", "no tengo información", "lo siento, no"]
    if any(f in r for f in frases_error):
        score -= 0.1

    if "ticket" in q or "problema" in q:
        if "" in respuesta or "tkt-" in r:
            score += 0.1

    return max(0.0, min(1.0, score))

class AgenteHelpdeskMock:

    PEDIDOS = {
        "ORD-001": {"estado": "En camino", "llegada": "Mañana antes de las 18:00"},
        "ORD-002": {"estado": "Entregado",  "llegada": "Entregado el 10/06/2025"},
        "ORD-003": {"estado": "En bodega",  "llegada": "2-3 días hábiles"},
    }

    FAQS = {
        "envío"      : "El envío estándar tarda 3-5 días hábiles. Envío express disponible.",
        "garantía"   : "Todos los productos tienen garantía de 1 año por defectos de fabricación.",
        "pago"       : "Aceptamos tarjetas de crédito, débito y transferencia bancaria.",
        "devolución" : "Puedes devolver productos en hasta 30 días con boleta de compra.",
        "cambio"     : "Los cambios se realizan en tienda o por despacho dentro de los 7 días.",
    }

    def __init__(self):
        self._tool_calls_last = 0

    def chat(self, consulta: str) -> str:
        self._tool_calls_last = 0
        q = consulta.lower()

        for num in ["ord-001", "ord-002", "ord-003"]:
            if num in q:
                self._tool_calls_last += 1
                info = self.PEDIDOS[num.upper()]
                return (
                    f" Pedido {num.upper()}:\n"
                    f"  Estado: {info['estado']}\n"
                    f"  Entrega estimada: {info['llegada']}"
                )

        if any(w in q for w in ["reembolso", "devolver dinero", "cuánto me devuelven"]):
            self._tool_calls_last += 1
            return (
                " Cálculo de reembolso:\n"
                "  Monto original: $50.000\n"
                "  Días desde la compra: 5\n"
                "  Porcentaje de reembolso: 100%\n"
                "  Monto a reembolsar: $50.000"
            )

        for kw, resp in self.FAQS.items():
            if kw in q:
                self._tool_calls_last += 1
                return f" Información encontrada: {resp}"

        if any(w in q for w in ["ticket", "problema", "queja", "ayuda urgente"]):
            self._tool_calls_last += 1
            return (
                " Ticket de soporte creado exitosamente:\n"
                "  ID: TKT-48291\n"
                "  Fecha: 25/06/2025 10:30\n"
                "  Un agente humano se contactará en las próximas 24 horas."
            )

        return (
            "¡Hola! Soy el asistente de TechStore. Puedo ayudarte con el estado "
            "de tu pedido, información de garantías, envíos, devoluciones o crear "
            "un ticket de soporte. ¿En qué te puedo ayudar?"
        )

    def herramientas_usadas(self) -> int:
        return self._tool_calls_last

class AgenteObservable:

    def __init__(self, agente, recolector: RecolectorMetricas):
        self.agente    = agente
        self.recolector = recolector
        self._contador  = 0

    def consultar(self, consulta: str) -> str:
        self._contador += 1
        query_id   = f"Q{self._contador:03d}"
        inicio     = time.perf_counter()
        exitoso    = True
        error_msg  = None
        respuesta  = ""
        tools_usados = 0

        logger.info(f"[INICIO] {query_id}  '{consulta[:60]}'")

        try:
            respuesta    = self.agente.chat(consulta)
            tools_usados = self.agente.herramientas_usadas()
        except Exception as exc:
            exitoso   = False
            error_msg = str(exc)
            respuesta = f"[ERROR] {exc}"
            logger.error(f"[ERROR] {query_id}  {exc}")

        latencia = time.perf_counter() - inicio
        tokens   = int((len(consulta.split()) + len(respuesta.split())) * 1.3)

        metrica = MetricaEjecucion(
            timestamp          = datetime.now().isoformat(),
            query_id           = query_id,
            consulta           = consulta,
            respuesta          = respuesta,
            latencia_segundos  = round(latencia, 6),
            tokens_estimados   = tokens,
            herramientas_usadas= tools_usados,
            exitoso            = exitoso,
            mensaje_error      = error_msg,
            hash_respuesta     = hashlib.md5(respuesta.encode()).hexdigest()[:12],
            score_precision    = evaluar_precision(consulta, respuesta),
        )
        self.recolector.registrar(metrica)
        return respuesta

CONSULTAS_PRUEBA = [

    "¿Cuál es el estado de mi pedido ORD-001?",
    "Necesito saber cuándo llega mi pedido ORD-002",
    "¿Dónde está mi pedido ORD-003?",

    "¿Cómo funciona el envío?",
    "¿Cuál es la política de garantía?",
    "¿Qué medios de pago aceptan?",
    "¿Puedo devolver un producto?",

    "Quiero saber cuánto me devuelven por mi compra de $50.000",
    "¿Cómo proceso una devolución de dinero?",

    "Tengo un problema con mi pedido, necesito ayuda urgente",
    "Quiero crear un ticket de soporte",

    "Hola, ¿cómo están?",
    "Necesito ayuda",

    "¿Cuál es el estado de mi pedido ORD-001?",
    "¿Cómo funciona el envío?",
]

def main():
    print("\n" + "="*60)
    print("  SUITE DE OBSERVABILIDAD — AGENTE TECHSTORE (EP3)")
    print("="*60)

    recolector = RecolectorMetricas()

    agente_base = AgenteHelpdeskMock()
    agente      = AgenteObservable(agente_base, recolector)

    print(f"\n Ejecutando {len(CONSULTAS_PRUEBA)} consultas de prueba...\n")

    for consulta in CONSULTAS_PRUEBA:
        print(f"   {consulta[:65]}")
        respuesta = agente.consultar(consulta)
        print(f"     {respuesta[:80].strip()}\n")

    resumen = recolector.calcular_resumen()

    print("\n" + "="*60)
    print("  RESUMEN DE MÉTRICAS DE OBSERVABILIDAD")
    print("="*60)
    print(f"  Total de consultas     : {resumen['total_consultas']}")
    print(f"  Tasa de errores        : {resumen['tasa_errores']:.1%}")
    print(f"  Latencia promedio      : {resumen['latencia_promedio_s']*1000:.2f} ms")
    print(f"  Latencia P95           : {resumen['latencia_p95_s']*1000:.2f} ms")
    print(f"  Latencia máxima        : {resumen['latencia_max_s']*1000:.2f} ms")
    print(f"  Precisión promedio     : {resumen['precision_promedio']:.1%}")
    print(f"  Consistencia           : {resumen['consistencia']:.1%}")
    print(f"  Tokens promedio/query  : {resumen['tokens_promedio']:.0f}")
    print(f"  Tokens totales         : {resumen['tokens_total']}")
    print(f"  Herramientas/query     : {resumen['herramientas_promedio']:.2f}")

    resumen_path = os.path.join(LOG_DIR, "metrics_summary.json")
    with open(resumen_path, "w", encoding="utf-8") as f:
        json.dump({
            "resumen": resumen,
            "metricas": [asdict(m) for m in recolector.metricas]
        }, f, indent=2, ensure_ascii=False)

    print(f"\n   Logs JSONL  : logs/agent_execution.jsonl")
    print(f"   Resumen JSON: logs/metrics_summary.json")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()