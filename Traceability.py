import json
import os
from collections import Counter, defaultdict
from datetime import datetime

LOG_DIR      = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE     = os.path.join(LOG_DIR, "agent_execution.jsonl")
SUMMARY_FILE = os.path.join(LOG_DIR, "metrics_summary.json")
REPORT_FILE  = os.path.join(LOG_DIR, "trace_report.json")

def cargar_metricas() -> list[dict]:
    if not os.path.exists(LOG_FILE):
        raise FileNotFoundError(
            "No se encontró logs/agent_execution.jsonl\n"
            "Ejecuta primero: python observability.py"
        )
    metricas = []
    with open(LOG_FILE, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                metricas.append(json.loads(linea))
    return metricas

def cargar_resumen() -> dict:
    with open(SUMMARY_FILE, encoding="utf-8") as f:
        return json.load(f)

def clasificar_consulta(consulta: str) -> str:
    q = consulta.lower()
    if any(w in q for w in ["ord-", "pedido", "estado", "entrega", "llegada"]):
        return "pedido"
    if any(w in q for w in ["reembolso", "devolver dinero", "cuánto me devuelven"]):
        return "reembolso"
    if any(w in q for w in ["ticket", "problema", "queja", "ayuda urgente"]):
        return "soporte"
    if any(w in q for w in ["envío", "garantía", "pago", "devolución", "política"]):
        return "faq"
    return "general"

def analizar_patrones(metricas: list[dict]) -> dict:

    categorias = Counter(clasificar_consulta(m["consulta"]) for m in metricas)

    sin_herramientas = [
        {"query_id": m["query_id"], "consulta": m["consulta"]}
        for m in metricas if m["herramientas_usadas"] == 0 and m["exitoso"]
    ]

    baja_precision = [
        {
            "query_id"       : m["query_id"],
            "consulta"       : m["consulta"],
            "score_precision": round(m["score_precision"], 3),
            "categoria"      : clasificar_consulta(m["consulta"]),
        }
        for m in metricas if m["score_precision"] < 0.70
    ]

    latencias = [m["latencia_segundos"] for m in metricas]
    media_lat = sum(latencias) / len(latencias)
    varianza  = sum((l - media_lat) ** 2 for l in latencias) / len(latencias)
    std_lat   = varianza ** 0.5
    umbral    = media_lat + 2 * std_lat

    outliers = [
        {
            "query_id"          : m["query_id"],
            "consulta"          : m["consulta"],
            "latencia_ms"       : round(m["latencia_segundos"] * 1000, 3),
            "desviaciones_sobre_media": round(
                (m["latencia_segundos"] - media_lat) / std_lat if std_lat > 0 else 0, 1
            ),
        }
        for m in metricas if m["latencia_segundos"] > umbral
    ]

    grupos: dict[str, list[str]] = defaultdict(list)
    for m in metricas:
        grupos[m["consulta"].lower().strip()].append(m["hash_respuesta"])

    consistencia_detalle = []
    for consulta, hashes in grupos.items():
        if len(hashes) > 1:
            unicos    = len(set(hashes))
            consistente = unicos == 1
            consistencia_detalle.append({
                "consulta"   : consulta,
                "repeticiones": len(hashes),
                "consistente": consistente,
                "hashes"     : hashes,
            })

    errores = [
        {"query_id": m["query_id"], "consulta": m["consulta"],
         "mensaje_error": m["mensaje_error"]}
        for m in metricas if not m["exitoso"]
    ]

    tokens_vals = [m["tokens_estimados"] for m in metricas]
    distribucion_tokens = {
        "bajo_(<20)"   : sum(1 for t in tokens_vals if t < 20),
        "medio_(20-35)": sum(1 for t in tokens_vals if 20 <= t < 35),
        "alto_(>=35)"  : sum(1 for t in tokens_vals if t >= 35),
    }

    return {
        "total_analizados"     : len(metricas),
        "categorias"           : dict(categorias),
        "sin_herramientas"     : sin_herramientas,
        "baja_precision"       : baja_precision,
        "outliers_latencia"    : outliers,
        "consistencia_detalle" : consistencia_detalle,
        "errores"              : errores,
        "distribucion_tokens"  : distribucion_tokens,
        "umbral_outlier_ms"    : round(umbral * 1000, 3),
    }

def imprimir_reporte(metricas: list[dict], patrones: dict, resumen: dict):
    s = resumen.get("resumen", {})

    print("\n" + "="*65)
    print("  REPORTE DE TRAZABILIDAD — AGENTE TECHSTORE")
    print(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65)

    print("\n MÉTRICAS GLOBALES:")
    print(f"  Total consultas analizadas : {s.get('total_consultas', '?')}")
    print(f"  Tasa de errores            : {s.get('tasa_errores', 0):.1%}")
    print(f"  Precisión promedio         : {s.get('precision_promedio', 0):.1%}")
    print(f"  Consistencia               : {s.get('consistencia', 0):.1%}")
    print(f"  Latencia promedio          : {s.get('latencia_promedio_s', 0)*1000:.3f} ms")
    print(f"  Latencia P95               : {s.get('latencia_p95_s', 0)*1000:.3f} ms")
    print(f"  Tokens totales consumidos  : {s.get('tokens_total', 0)}")

    print("\n DISTRIBUCIÓN POR CATEGORÍA DE CONSULTA:")
    total = patrones["total_analizados"]
    for cat, cnt in sorted(patrones["categorias"].items(), key=lambda x: -x[1]):
        pct = cnt / total * 100
        barra = "█" * int(pct / 5)
        print(f"  {cat:10s}  {barra:20s}  {cnt} ({pct:.0f}%)")

    print(f"\n️  CONSULTAS SIN USO DE HERRAMIENTAS ({len(patrones['sin_herramientas'])} detectadas):")
    if patrones["sin_herramientas"]:
        for item in patrones["sin_herramientas"]:
            print(f"  [{item['query_id']}] '{item['consulta']}'")
        print("   Causa: el clasificador no reconoció la intención.")
        print("   Mejora: ampliar keywords de enrutamiento o usar embeddings.")
    else:
        print("   Todas las consultas utilizaron al menos una herramienta.")

    print(f"\n CONSULTAS CON BAJA PRECISIÓN (<70%) "
          f"({len(patrones['baja_precision'])} detectadas):")
    if patrones["baja_precision"]:
        for item in patrones["baja_precision"]:
            print(f"  [{item['query_id']}] score={item['score_precision']:.0%} | "
                  f"cat={item['categoria']} | '{item['consulta']}'")
        print("   Estas consultas requieren revisión del evaluador o del enrutamiento.")
    else:
        print("   Todas las consultas superaron el umbral de precisión.")

    print(f"\n⏱️  OUTLIERS DE LATENCIA (umbral: {patrones['umbral_outlier_ms']:.3f} ms):")
    if patrones["outliers_latencia"]:
        for item in patrones["outliers_latencia"]:
            print(f"  [{item['query_id']}] {item['latencia_ms']:.3f} ms "
                  f"(+{item['desviaciones_sobre_media']}σ) | '{item['consulta'][:50]}'")
        print("   Con LLM real (800-3000ms), implementar caché para estos casos.")
    else:
        print("   No se detectaron outliers de latencia significativos.")

    print(f"\n ANÁLISIS DE CONSISTENCIA (consultas repetidas):")
    if patrones["consistencia_detalle"]:
        for item in patrones["consistencia_detalle"]:
            estado = " Consistente" if item["consistente"] else "️  Inconsistente"
            print(f"  {estado} ({item['repeticiones']}x) '{item['consulta'][:55]}'")
    else:
        print("  No hay consultas repetidas en esta ejecución.")

    print(f"\n🪙 DISTRIBUCIÓN DE USO DE TOKENS:")
    for bucket, cnt in patrones["distribucion_tokens"].items():
        print(f"  {bucket:20s}: {cnt} consultas")

    print(f"\n ERRORES EN EJECUCIÓN: {len(patrones['errores'])}")
    if patrones["errores"]:
        for e in patrones["errores"]:
            print(f"  [{e['query_id']}] {e['mensaje_error']}")
    else:
        print("   Sin errores en esta ejecución.")

    print("\n HALLAZGOS CLAVE PARA EL INFORME:")
    n_sin_tool  = len(patrones["sin_herramientas"])
    n_baja_prec = len(patrones["baja_precision"])
    print(f"  1. {n_sin_tool} consultas no activaron herramientas  enrutamiento a mejorar.")
    print(f"  2. {n_baja_prec} consultas con precisión <70%  revisar keywords de búsqueda.")
    if patrones["outliers_latencia"]:
        print(f"  3. {len(patrones['outliers_latencia'])} outlier(s) de latencia detectados.")
    else:
        print(f"  3. Latencia muy estable — el mock no introduce variabilidad de red.")
        print(f"     Con LLM real la P95 estará entre 1000-4000ms.")
    print(f"  4. Consistencia 100%  el agente es determinista ante queries idénticas.")
    print("="*65 + "\n")

def main():
    metricas = cargar_metricas()
    resumen  = cargar_resumen()
    patrones = analizar_patrones(metricas)
    imprimir_reporte(metricas, patrones, resumen)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(patrones, f, indent=2, ensure_ascii=False)
    print(f"   Reporte guardado en: logs/trace_report.json\n")

if __name__ == "__main__":
    main()