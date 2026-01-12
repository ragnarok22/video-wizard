# Video Wizard - Guía de Inicio Rápido 🚀

Procesa videos completos en 3 pasos: Upload → Transcripción → Análisis de IA

## ⚡ Inicio en 2 Minutos

### 1. Configurar Environment Variables

```bash
cd apps/web
cp .env.local.example .env.local
```

Edita `.env.local`:
```env
OPENAI_API_KEY=sk-tu-api-key-aqui
NEXT_PUBLIC_PYTHON_ENGINE_URL=http://localhost:8000
```

### 2. Iniciar Servicios

**Terminal 1 - Python Backend:**
```bash
cd apps/processing-engine
docker-compose -f docker-compose.dev.yml up
```

**Terminal 2 - Next.js Frontend:**
```bash
cd apps/web
pnpm dev
```

### 3. Usar la Aplicación

1. Abre: `http://localhost:3000/video-wizard`
2. Selecciona un video (máx. 500MB)
3. Haz clic en "🚀 Procesar Video"
4. ¡Espera los resultados!

## 🎯 Lo Que Hace

1. **Sube el video** al servidor Python
2. **Extrae audio** y genera **subtítulos con timestamps**
3. **Analiza con GPT-4o** para encontrar clips virales
4. **Muestra resultados** con puntuaciones y recomendaciones

## 📊 Ejemplo de Resultado

```
✅ Video procesado: mi-video.mp4
📝 42 segmentos de transcripción
🎬 5 clips virales encontrados
⭐ Puntuación promedio: 78.5/100

Clip #1 (Score: 95/100) 🔥🔥🔥
⏱️ 00:15 - 01:02 (47s)
📝 "Opening hook con estadística impactante"
🎣 Hook: "90% de las personas no saben esto..."
```

## 🔧 Troubleshooting Rápido

### Python engine no responde
```bash
curl http://localhost:8000/health
# Debería retornar: {"status": "healthy"}
```

### Error de OpenAI
```bash
# Verifica tu API key
echo $OPENAI_API_KEY

# O revisa .env.local
cat apps/web/.env.local | grep OPENAI_API_KEY
```

### Video no se sube
- Verifica que sea un archivo de video válido
- Máximo 500MB
- Formatos soportados: MP4, MOV, AVI, MKV, etc.

## 📈 Tiempos Esperados

- Video de 2 min: ~1 minuto de procesamiento
- Video de 5 min: ~2 minutos de procesamiento
- Video de 10 min: ~4 minutos de procesamiento

## 🎨 Características de UI

- ✅ Indicadores de progreso en tiempo real
- ✅ 3 pasos visuales con estados
- ✅ Visualización de transcripción
- ✅ Lista de clips ordenados por score
- ✅ Código de colores para puntuaciones
- ✅ Diseño responsive

## 📚 Documentación Completa

Ver [VIDEO_WIZARD.md](./VIDEO_WIZARD.md) para documentación detallada.

## 🎯 Próximos Pasos

1. Procesa tu primer video
2. Revisa los clips sugeridos
3. Usa los timestamps para editar
4. ¡Crea contenido viral!

---

**¿Listo? ¡Sube un video y descubre tus mejores clips! 🎬**
