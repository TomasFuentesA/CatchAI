# CatchAI

**CatchAI** es una aplicación web desarrollada con Streamlit que permite buscar información relevante en archivos PDF usando inteligencia artificial. El sistema utiliza procesamiento de lenguaje natural, embeddings y modelos LLM para responder consultas sobre el contenido de los documentos cargados.

---

## Características principales

- **Carga de PDFs:** Permite subir hasta 5 archivos PDF por sesión.
- **Extracción y limpieza de texto:** El texto de los PDFs se extrae y limpia automáticamente.
- **División en chunks:** El texto se divide en fragmentos para facilitar la búsqueda semántica.
- **Base vectorial:** Los chunks se indexan usando embeddings y ChromaDB para búsquedas eficientes.
- **Consulta inteligente:** Puedes realizar preguntas sobre los PDFs y el sistema responde usando solo la información relevante.
- **Historial de consultas:** Guarda y muestra todas las consultas y respuestas generadas en la sesión.
- **Gestión de memoria:** Incluye botones para limpiar la base de datos y la memoria del modelo.
- **Dockerizado:** Listo para desplegarse en cualquier entorno usando Docker y Docker Compose.

---

## Requisitos

- Docker y Docker Compose instalados
- Token de HuggingFace (para modelos gated)
- Recursos recomendados: 4 CPUs, 8GB RAM

---

## Instalación y despliegue

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd CatchAI
   ```

2. **Configura tu token de HuggingFace:**
   - Añade tu TOKEN en el archivo config.py:
     ```
     HF_TOKEN=tu_token_aqui
     ```

3. **Construye y levanta el servicio:**
   ```bash
   docker-compose up --build
   ```

4. **Accede a la aplicación:**
   - Abre [http://localhost:8501](http://localhost:8501) en tu navegador.

---

## Estructura del proyecto

```
CatchAI/
│
├── app/
│   ├── app.py
│   ├── pdf_utils.py
│   ├── vector_utils.py
│   ├── llm_utils.py
│   ├── config.py
│   └── __init__.py
├── pdf/
├── chroma_db/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
```

---

## Uso

1. **Carga PDFs:**  
   Sube hasta 5 archivos PDF usando el botón correspondiente.

2. **Realiza consultas:**  
   Escribe tu pregunta en el campo "Escribe tu consulta" y presiona Enter.

3. **Revisa el historial:**  
   Todas las consultas y respuestas se muestran en la parte inferior de la app.

4. **Gestión avanzada:**  
   Usa los botones para limpiar la base de datos o la memoria del modelo si lo necesitas.

---

## Personalización

- Puedes cambiar el modelo LLM en `llm_utils.py` (por ejemplo, usar `google/gemma-2b-it` o `google/flan-t5-base`).
- Ajusta el tamaño de los chunks en `vector_utils.py` para mejorar la precisión de las búsquedas.
- Modifica el prompt en `llm_utils.py` para adaptar el estilo de las respuestas.

---

## Troubleshooting

- **Error de memoria:** Usa el botón "Limpiar memoria del modelo" o aumenta los recursos del contenedor.
- **Conflicto de dependencias:** Revisa y simplifica `requirements.txt` si Docker falla al construir.
- **Respuestas vacías o irrelevantes:** Verifica que el PDF tenga texto extraíble y que el modelo seleccionado sea adecuado.

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

---

## Autor

Desarrollado por [Tu Nombre o Equipo].

---

¿Preguntas o sugerencias? ¡Abre un issue o
