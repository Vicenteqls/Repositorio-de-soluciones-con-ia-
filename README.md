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
