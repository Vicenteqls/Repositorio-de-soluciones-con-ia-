Esto se probo con linux en windows no se si funciona 


# Repositorio-de-soluciones-con-ia-

Evaluación Parcial N°2 — ISY0101 Ingeniería de Soluciones con IA
Agente inteligente de soporte al cliente construido con LangChain y GitHub Models API, capaz de integrar herramientas de consulta, escritura y razonamiento en un flujo de trabajo organizacional automatizado.

┌─────────────────────────────────────────────────────────┐
│                    USUARIO / CLIENTE                     │
└────────────────────────┬────────────────────────────────┘
                         │ mensaje
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  AgenteHelpdesk                          │
│                                                          │
│   ┌─────────────┐    ┌──────────────────────────────┐   │
│   │  MEMORIA    │    │     PLANIFICADOR (LLM)        │   │
│   │             │    │   Ciclo ReAct:                │   │
│   │ • Buffer    │◄──►│   1. Razona la consulta       │   │
│   │ • Ventana   │    │   2. Selecciona herramienta   │   │
│   │ • Resumen   │    │   3. Ejecuta                  │   │
│   └─────────────┘    │   4. Observa resultado        │   │
│                      │   5. Genera respuesta final   │   │
│                      └──────────────┬───────────────┘   │
│                                     │                    │
│              ┌──────────────────────┼──────────────┐    │
│              ▼              ▼       ▼       ▼       │    │
│         buscar_faq  consultar  calcular  crear      │    │
│                     _pedido   _reembolso _ticket    │    │
│              │              │       │       │       │    │
│              └──────────────┴───────┴───────┘       │    │
│                         data/faq.json               │    │
└─────────────────────────────────────────────────────┘

agente-helpdesk/
├── agent/
│   ├── __init__.py
│   ├── agent.py        # Agente principal (LangChain + planificación)
│   ├── tools.py        # 4 herramientas personalizadas
│   └── memory.py       # 3 estrategias de memoria
├── data/
│   └── faq.json        # Base de conocimiento + datos de pedidos
├── tests/
│   └── test_agent.py   # Pruebas de herramientas
├── docs/
│   └── architecture.md # Documentación técnica
├── main.py             # Punto de entrada (demo + chat interactivo)
├── requirements.txt
├── .env.example
└── .gitignore

--La instalacion y configuracion--
1. Clonar el repositorio
git clone https://github.com/tu-usuario/agente-helpdesk.git
cd agente-helpdesk

2. Crear entorno virtual
python -m venv venv
source venv/bin/activate.fish
source venv/bin/activate

3. Instalar dependencias
pip install -r requirements.txt

4. Configurar credenciales
cp .env.example .env

--Ejecución--
Demo automático (6 escenarios de prueba)
-python main.py
Chat interactivo
-python main.py --chat
Pruebas de herramientas
-python tests/test_agent.py


--Herramientas del Agente--
Herramienta               Tipo          Descripción
-buscar_faq               Consulta      Busca en la base de preguntas frecuentes
-consultar_estado_pedido  Consulta API  Retorna el estado de un pedido por número
-calcular_reembolso       Razonamiento  Calcula el monto de devolución según política
-crear_ticket_soporte     Escritura     Genera un ticket cuando no hay solución directa

--Estrategias de Memoria--
tipo       clase            Comportamiento
-Buffer    MemoriaBuffer    Guarda todo el historial completo
-ventana   MemoriaVentana   Solo conserva las últimas k interacciones
-resumen   MemoriaResumen   Comprime el historial con el LLM

--Flujo de Planificación--
El agente sigue este esquema de prioridades (IE5)
Consulta recibida
      │
      ├─ ¿Contiene número ORD-XXX? ──► consultar_estado_pedido
      │
      ├─ ¿Menciona devolución + monto? ──► calcular_reembolso
      │
      ├─ ¿Es pregunta sobre política? ──► buscar_faq
      │
      └─ ¿Problema complejo/sin solución? ──► crear_ticket_soporte

Stack Tecnológico

LangChain 1.x — Framework de agentes
langchain-openai — Integración con API compatible OpenAI
GitHub Models API — Backend LLM (gpt-4.1)
Python 3.14 — Lenguaje base

Evaluación Parcial N°3 — Implementacion de Observabilidad

Extiende el agente TechStore con un sistema completo de observabilidad, trazabilidad, seguridad y propuestas de mejora basadas en datos recolectados.

Archivos nuevos EP3

observability.py     IL3.1 - Metricas de precision, latencia, consistencia y tokens
traceability.py      IL3.2 - Analisis de logs y deteccion de patrones y anomalias
security.py          IL3.3 - Protocolos de seguridad y uso responsable
improvements.py      IL3.4 - Propuestas de mejora y escalabilidad
dashboard.py         Dashboard interactivo con Streamlit y Plotly
logs/
  agent_execution.jsonl    Logs de ejecucion (generado automaticamente)
  metrics_summary.json     Resumen estadistico de metricas
  trace_report.json        Reporte de patrones y anomalias
  security_audit.log       Registro de eventos de seguridad

Dependencias adicionales EP3

bashpip install streamlit plotly pandas

Ejecucion EP3

Ejecutar en orden:

bashpython observability.py

Corre 15 consultas de prueba sobre el agente, mide precision, latencia, consistencia, tokens y herramientas usadas. Genera los archivos en la carpeta logs/.

bashpython traceability.py

Lee los logs generados, identifica consultas sin herramienta activa, consultas con baja precision, outliers de latencia y analiza consistencia entre respuestas repetidas.

bashpython security.py

Ejecuta una demo de todos los protocolos de seguridad: rate limiting, deteccion de prompt injection, filtro de contenido inapropiado y anonimizacion de datos sensibles.

bashpython improvements.py

Muestra propuestas de mejora fundamentadas en los datos: demo del cache de respuestas, clasificador de intencion mejorado, analisis de costo operacional y arquitectura escalable propuesta.

bashstreamlit run dashboard.py

Lanza el dashboard interactivo en http://localhost:8501. Requiere haber ejecutado observability.py primero.

Metricas implementadas EP3

MetricaDescripcionIndicadorPrecisionScore heuristico 0.0 a 1.0 por consultaIE1LatenciaTiempo de respuesta en ms, promedio y P95IE2ConsistenciaPorcentaje de respuestas identicas ante queries repetidasIE1Frecuencia de erroresTasa de fallos durante la ejecucionIE1Tokens estimadosConsumo de recursos por consultaIE2Herramientas usadasNumero de tool calls por consultaIE2

Protocolos de seguridad EP3

ProtocoloDescripcionRate limiting10 solicitudes por minuto por usuarioDeteccion de injection9 patrones de prompt injectionFiltro de contenidoBloqueo de consultas inapropiadasAnonimizacionRUT, email, telefono y tarjeta redactados en logsAuditoriaRegistro completo de eventos en security_audit.log

Nota de compatibilidad

Los scripts de EP3 incluyen un agente mock que replica el comportamiento del AgenteHelpdesk sin necesidad de la API. Para usar el agente real con la API activa, reemplazar en observability.py:

pythonfrom Agent import AgenteHelpdesk
agente_base = AgenteHelpdesk(tipo_memoria="ventana")

Stack tecnologico


LangChain 1.x
langchain-openai
GitHub Models API (gpt-4.1)
Streamlit
Plotly
Python 3.10+
