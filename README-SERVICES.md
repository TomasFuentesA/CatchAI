# CatchAI - Arquitectura de Microservicios

Este proyecto implementa un sistema de búsqueda de PDFs con IA utilizando una arquitectura de microservicios con tres servicios independientes.

## Arquitectura

### 🏗️ Servicios

1. **Streamlit Service** (Puerto 8501)
   - Interfaz de usuario web
   - Gestión de uploads de PDF
   - Coordinación entre servicios

2. **Chroma Service** (Puerto 8000)
   - Base de datos vectorial
   - API REST para operaciones vectoriales
   - Embeddings con sentence-transformers

3. **Model Service** (Puerto 8001)
   - Servicio de inferencia LLM
   - Modelo Google Gemma-2b-it
   - API REST para generación de respuestas

### 📁 Estructura de Directorios

```
/
├── services/
│   ├── streamlit/          # Servicio UI
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── app.py
│   │       ├── config.py
│   │       ├── pdf_utils.py
│   │       ├── vector_utils.py
│   │       └── llm_utils.py
│   ├── chroma/             # Servicio Base de Datos Vectorial
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       └── main.py
│   └── model/              # Servicio Modelo LLM
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
│           └── main.py
├── docker-compose-services.yml  # Orquestación de servicios
└── README-SERVICES.md
```

## 🚀 Uso

### Inicio Rápido

```bash
# Construir y ejecutar todos los servicios
docker compose -f docker-compose-services.yml up --build

# Acceder a la aplicación
open http://localhost:8501
```

### Verificar Servicios

```bash
# Chroma service
curl http://localhost:8000/health

# Model service  
curl http://localhost:8001/health

# Streamlit service
curl http://localhost:8501/_stcore/health
```

### Comandos de Desarrollo

```bash
# Ejecutar solo un servicio
docker compose -f docker-compose-services.yml up chroma

# Ver logs de un servicio
docker compose -f docker-compose-services.yml logs -f model

# Reconstruir un servicio
docker compose -f docker-compose-services.yml up --build streamlit

# Parar todos los servicios
docker compose -f docker-compose-services.yml down
```

## 🔧 APIs de Servicios

### Chroma Service (Puerto 8000)

- `GET /health` - Verificar estado
- `POST /vectorstore/create` - Crear almacén vectorial
- `POST /vectorstore/query` - Consultar similitud
- `DELETE /vectorstore/reset` - Resetear base de datos

### Model Service (Puerto 8001)

- `GET /health` - Verificar estado
- `POST /generate` - Generar respuesta LLM
- `POST /cleanup` - Limpiar memoria del modelo

## 🛠️ Configuración

### Variables de Entorno

#### Model Service
- `HF_TOKEN`: Token de HuggingFace
- `PYTORCH_CUDA_ALLOC_CONF`: Configuración de memoria PyTorch
- `TRANSFORMERS_CACHE`: Directorio de caché

#### Streamlit Service
- Configurado para comunicarse con otros servicios via docker networking

### Volúmenes Persistentes

- `chroma_data`: Datos de la base vectorial
- `model_cache`: Caché de modelos y transformers
- `./pdf`: Archivos PDF subidos (bind mount)

## 📊 Recursos del Sistema

### Requerimientos Mínimos
- **RAM**: 8GB (total para todos los servicios)
- **CPU**: 4 núcleos recomendados
- **Disco**: 10GB (para modelos y datos)

### Distribución de Recursos
- **Model Service**: 6GB RAM, 2 CPUs (más intensivo)
- **Chroma Service**: 2GB RAM, 1 CPU
- **Streamlit Service**: 1GB RAM, 1 CPU

## 🔍 Beneficios de la Arquitectura

### ✅ Ventajas

1. **Escalabilidad**: Cada servicio puede escalarse independientemente
2. **Mantenibilidad**: Separación clara de responsabilidades
3. **Desarrollo**: Equipos pueden trabajar en servicios independientes
4. **Despliegue**: Actualizaciones sin afectar otros servicios
5. **Recursos**: Mejor distribución de memoria y CPU
6. **Robustez**: Falla de un servicio no afecta los demás

### 📈 Casos de Uso

- **Producción**: Cada servicio en diferente servidor/cluster
- **Desarrollo**: Servicios individuales para testing
- **Demo**: Todo en una máquina con recursos limitados

## 🐛 Troubleshooting

### Problemas Comunes

1. **Servicios no se comunican**
   ```bash
   # Verificar que están en la misma red
   docker compose -f docker-compose-services.yml ps
   ```

2. **Memoria insuficiente**
   ```bash
   # Ajustar limits en docker-compose-services.yml
   # Reducir memory limits de ser necesario
   ```

3. **Puerto ocupado**
   ```bash
   # Cambiar puertos en docker-compose-services.yml
   ports:
     - "8502:8501"  # Cambiar puerto externo
   ```

## 🆚 Comparación con Arquitectura Anterior

| Aspecto | Monolítico | Microservicios |
|---------|------------|----------------|
| Contenedores | 1 | 3 |
| Complejidad | Baja | Media |
| Escalabilidad | Limitada | Alta |
| Recursos | 8GB en 1 contenedor | 8GB distribuidos |
| Mantenimiento | Difícil | Fácil |
| Desarrollo | Acoplado | Independiente |

La nueva arquitectura proporciona mayor flexibilidad y escalabilidad a costa de una complejidad ligeramente mayor en la configuración inicial.