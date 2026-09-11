# Agentes de IA — DataMentor AR (Gem de Gemini)

Un agente conversacional especializado, construido con **Gems de Gemini**, diseñado para asistir en tres tareas puntuales del trabajo diario de un analista de datos: revisar consultas SQL, recomendar el tipo de visualización correcto, y explicar conceptos técnicos en español simple.

Este proyecto conecta con el resto del portfolio: el agente está pensado como un "copiloto" para el mismo tipo de trabajo que se muestra en las carpetas `01` a `04` — revisión de SQL (como en el proyecto de BigQuery), selección de gráficos (como en el dashboard de clima), y modelado de datos (como en el proyecto de analytics engineering).

## 🎯 Por qué este diseño

Un agente genérico ("ayudame con datos") da respuestas vagas. Este Gem tiene **tres modos de uso explícitos y acotados**, cada uno con criterios claros de cuándo aplica y qué formato de respuesta debe dar. El detalle completo del prompt y la justificación de cada decisión de diseño está en [`instrucciones_gem.md`](./instrucciones_gem.md).

| Modo | Qué hace | Ejemplo de uso |
|---|---|---|
| Revisor de SQL | Detecta columnas innecesarias, oportunidades de particionado/clustering, problemas de legibilidad | Pegar una consulta y pedir revisión |
| Selector de visualización | Recomienda el gráfico correcto para una pregunta de negocio | "Tengo ventas por mes, ¿qué gráfico uso?" |
| Explicador de conceptos | Explica términos técnicos en español simple, con analogía y ejemplo | "¿Qué es clustering en BigQuery?" |

## 🛠️ Cómo se creó

1. Se definieron las instrucciones completas (ver `instrucciones_gem.md`) siguiendo principios de prompt engineering: rol claro, alcance acotado, formato de salida especificado, y reglas explícitas contra alucinación de resultados.
2. Se creó el Gem en [gemini.google.com/gems](https://gemini.google.com/gems), pegando esas instrucciones.
3. Se probó con casos reales tomados de los otros proyectos del portfolio (una consulta SQL del proyecto de BigQuery, una pregunta de visualización del proyecto de clima) para validar que las respuestas fueran útiles y consistentes.

## 💬 Ejemplos de conversación

Ver [`ejemplos_conversacion.md`](./ejemplos_conversacion.md) para capturas/transcripciones probando los 3 modos.

## 🛠️ Herramientas

Gemini (Gems), prompt engineering

## 📌 Nota

Los Gems son personales y no tienen un link público para compartir fuera de la cuenta de Google que los creó — por eso este proyecto documenta el diseño y el resultado (capturas + transcripciones) en vez de un link en vivo, a diferencia de los dashboards de las otras carpetas.
