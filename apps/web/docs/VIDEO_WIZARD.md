# Video Wizard - Procesamiento Automático Completo

Flujo automatizado end-to-end: sube un video → transcripción → análisis de IA → clips virales.

## 🎯 Características

- **Upload de Video**: Interfaz drag & drop para subir videos (máx. 500MB)
- **Transcripción Automática**: Extracción de audio y generación de subtítulos con timestamps
- **Análisis con IA**: GPT-4o identifica automáticamente los clips más virales
- **UI Interactiva**: Indicadores de progreso en tiempo real con 3 pasos
- **Resultados Visuales**: Lista de clips con puntuaciones y análisis detallado

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Crea `.env.local` en `apps/web/`:

```env
# OpenAI API Key (para análisis de IA)
OPENAI_API_KEY=sk-...

# URL del Python Processing Engine
NEXT_PUBLIC_PYTHON_ENGINE_URL=http://localhost:8000
```

### 2. Iniciar el Processing Engine (Python)

```bash
# Terminal 1: Python Backend
cd apps/processing-engine
docker-compose -f docker-compose.dev.yml up

# O sin Docker:
python main.py
```

El servidor debería estar corriendo en `http://localhost:8000`

### 3. Iniciar Next.js

```bash
# Terminal 2: Next.js Frontend
cd apps/web
pnpm dev
```

### 4. Acceder a la Aplicación

Abre tu navegador en:
```
http://localhost:3000/video-wizard
```

## 📋 Flujo de Trabajo

### Paso 1: Seleccionar Video
- Haz clic en "Selecciona tu video"
- Elige un archivo de video (MP4, MOV, AVI, etc.)
- Máximo 500MB

### Paso 2: Procesamiento Automático (3 etapas)

#### Etapa 1: Upload del Video 📤
```
POST http://localhost:8000/upload
```
- Sube el video al servidor Python
- Valida el tipo de archivo
- Retorna la ruta del archivo en el servidor

#### Etapa 2: Transcripción 🎙️
```
POST http://localhost:8000/transcribe
```
- Extrae el audio del video
- Genera transcripción con Whisper AI
- Retorna segmentos con timestamps precisos

#### Etapa 3: Análisis de IA 🤖
```
POST http://localhost:3000/api/analyze-content
```
- Formatea la transcripción con timestamps
- GPT-4o analiza el contenido
- Identifica clips virales (30-90 segundos)

### Paso 3: Resultados
- Transcripción completa con timestamps
- Lista de clips virales ordenados por puntuación
- Análisis detallado de cada clip:
  - Tiempo de inicio y fin
  - Puntuación viral (0-100)
  - Resumen del contenido
  - Hook identificado
  - Conclusión

## 🎨 Componentes de UI

### Indicadores de Progreso

La página muestra 3 pasos con indicadores visuales:

```
1. 🔵 Subir video → ✅ Completado
2. 🔵 Extraer audio y subtítulos → ⏳ En progreso
3. ⚪ Análisis de contenido con IA → ⏸️ Pendiente
```

### Estados de Proceso

- **idle**: Esperando archivo
- **uploading**: Subiendo video
- **transcribing**: Generando subtítulos
- **analyzing**: Analizando con IA
- **complete**: Proceso completo
- **error**: Error en algún paso

## 📊 Formato de Datos

### Respuesta del Python Engine (Transcripción)

```typescript
{
  "video_path": "uploads/my-video.mp4",
  "audio_path": "temp/audio.wav",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 4.5,
      "text": "Welcome to this tutorial"
    }
  ],
  "full_text": "Complete transcription...",
  "segment_count": 42
}
```

### Formato para Análisis de IA

Los segmentos se convierten a:

```
[00:00 - 00:04] Welcome to this tutorial
[00:04 - 00:15] Today we're going to learn...
```

### Respuesta del Análisis de IA

```typescript
{
  "clips": [
    {
      "start_time": 0,
      "end_time": 45,
      "viral_score": 85,
      "summary": "Strong opening hook...",
      "hook": "Welcome message with clear value",
      "conclusion": "Sets up tutorial expectations"
    }
  ],
  "total_clips": 5,
  "analysis_summary": "Found 5 high-potential clips..."
}
```

## 🛠️ Personalización

### Cambiar el Tamaño Máximo de Archivo

En `page.tsx`:

```typescript
const maxSize = 500 * 1024 * 1024; // Cambiar a tu límite deseado
```

### Ajustar el Idioma de Transcripción

```typescript
body: JSON.stringify({
  video_path: uploadData.path,
  language: 'es', // Especificar idioma: 'es', 'en', 'fr', etc.
  cleanup: true,
})
```

### Modificar Criterios de Análisis

Los criterios de análisis están en:
```
apps/web/app/api/analyze-content/route.ts
```

Edita el `VIRAL_EDITOR_PROMPT` para cambiar:
- Duración de clips (actualmente 30-90s)
- Criterios de puntuación
- Enfoque de análisis

## 🐛 Troubleshooting

### "Error al subir el video"

**Problema**: El Python engine no está corriendo o no es accesible

**Solución**:
```bash
# Verificar que el Python engine esté corriendo
curl http://localhost:8000/health

# Debería retornar: {"status": "healthy"}
```

### "Error al transcribir el video"

**Problema**: Whisper no está instalado o falta ffmpeg

**Solución**:
```bash
# Dentro del container de Docker
docker exec video-processing-service pip install -r requirements.txt

# O localmente
pip install openai-whisper
brew install ffmpeg  # macOS
```

### "Error al analizar el contenido"

**Problema**: OpenAI API key no configurada o inválida

**Solución**:
```bash
# Verificar que .env.local tenga la key
cat apps/web/.env.local | grep OPENAI_API_KEY

# Reiniciar el servidor Next.js después de agregar la key
```

### CORS Error

**Problema**: El frontend no puede comunicarse con el backend

**Solución**: Verifica que el Python engine tenga CORS habilitado en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Video muy grande

**Problema**: El video excede el límite de 500MB

**Solución**: 
1. Comprime el video antes de subirlo
2. Aumenta el límite en el código (ver Personalización)
3. Configura límites en nginx/reverse proxy si usas uno

## 📈 Performance

### Tiempos Estimados

| Duración del Video | Upload | Transcripción | Análisis IA | Total |
|-------------------|--------|---------------|-------------|-------|
| 2 minutos | 5-10s | 30-45s | 3-5s | ~1 min |
| 5 minutos | 10-20s | 60-90s | 5-8s | ~2 min |
| 10 minutos | 20-40s | 120-180s | 8-12s | ~4 min |

*Los tiempos varían según la velocidad de internet y recursos del servidor*

### Optimizaciones

1. **Compresión de Video**: Usa H.264 para archivos más pequeños
2. **Procesamiento Asíncrono**: Para videos largos, considera usar jobs en background
3. **Caching**: Guarda transcripciones en base de datos para evitar reprocesamiento
4. **Rate Limiting**: Implementa límites para evitar abuso

## 🔐 Consideraciones de Seguridad

### Producción

Antes de desplegar en producción:

1. **Validación de Archivos**:
   - Verifica tipos MIME
   - Escanea por malware
   - Limita tamaños

2. **Rate Limiting**:
   - Implementa límites por IP
   - Usa colas para procesar videos

3. **Almacenamiento**:
   - Limpia archivos temporales
   - Usa storage en la nube (S3, GCS)
   - Implementa expiración automática

4. **API Keys**:
   - Nunca expongas keys en el frontend
   - Usa variables de entorno
   - Rota keys regularmente

5. **CORS**:
   - Restringe origins en producción
   - No uses wildcard (`*`)

## 🌟 Próximas Características

- [ ] Preview del video con player integrado
- [ ] Navegación a timestamps específicos
- [ ] Exportación directa de clips
- [ ] Batch processing de múltiples videos
- [ ] Historial de videos procesados
- [ ] Compartir resultados vía URL
- [ ] Integración con servicios de edición
- [ ] Análisis de sentimiento
- [ ] Detección de speakers múltiples
- [ ] Thumbnails automáticos para cada clip

## 📝 Notas Técnicas

### Arquitectura

```
Browser
  ↓ (upload)
Next.js Server (Port 3000)
  ↓ (proxy upload)
Python FastAPI (Port 8000)
  ↓ (transcribe with Whisper)
Transcription Result
  ↓ (format & analyze)
OpenAI GPT-4o
  ↓ (viral clips)
React UI
```

### Stack Completo

- **Frontend**: Next.js 16, React 19, TypeScript
- **Backend**: Python FastAPI, Whisper AI
- **AI**: OpenAI GPT-4o, Vercel AI SDK
- **Validation**: Zod schemas
- **UI**: Tailwind CSS, shadcn/ui
- **Video**: FFmpeg, OpenCV

## 🤝 Integración con Otros Módulos

Este módulo se integra con:

1. **Content Intelligence** (`/content-intelligence`): Usa el mismo análisis de IA
2. **Processing Engine** (`/processing-engine`): Usa transcripción y análisis de video
3. **Renderer**: Próximamente - exportación de clips

## 📞 Soporte

Para problemas o preguntas:

1. Revisa la sección de Troubleshooting
2. Verifica que ambos servidores estén corriendo
3. Revisa los logs del navegador (Console) y del Python engine
4. Verifica las variables de entorno

---

**¡Todo listo para procesar videos y encontrar clips virales! 🎬🔥**
