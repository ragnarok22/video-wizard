# Server Module

Estructura organizada del lado del servidor siguiendo mejores prácticas.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              API Routes (HTTP Layer)                │
│            app/api/*/route.ts                       │
│  - Request/Response handling                        │
│  - HTTP status codes                                │
│  - Input validation                                 │
└──────────────────┬──────────────────────────────────┘
                   │ imports
                   ▼
┌─────────────────────────────────────────────────────┐
│           Services (Business Logic)                 │
│          server/services/*.ts                       │
│  - Core business logic                              │
│  - Data processing                                  │
│  - External API calls                               │
└──────────────────┬──────────────────────────────────┘
                   │ uses
      ┌────────────┼────────────┐
      ▼            ▼            ▼
  ┌───────┐   ┌────────┐   ┌────────┐
  │ Types │   │ Config │   │ Prompts│
  │       │   │        │   │   AI   │
  └───────┘   └────────┘   └────────┘
      │            │            │
      └────────────┴────────────┘
                   │
                   ▼
            ┌──────────┐
            │   Lib    │
            │ (Utils)  │
            └──────────┘
```

## 📁 Estructura

```
server/
├── config/          # Configuraciones del servidor
│   └── ai.ts       # Configuración de modelos de IA
├── services/        # Lógica de negocio
│   └── content-analysis-service.ts
├── types/           # Schemas Zod y tipos TypeScript
│   └── content-analysis.ts
├── prompts/         # Prompts de IA
│   └── viral-editor.ts
├── lib/             # Funciones auxiliares (utilidades)
├── index.ts         # Exportaciones centrales
└── README.md        # Este archivo
```

## 🎯 Principios

### Separación de Responsabilidades
- **API Routes**: Solo manejan HTTP (request/response, validación de entrada, códigos de estado)
- **Services**: Contienen toda la lógica de negocio
- **Types**: Schemas Zod y tipos TypeScript centralizados
- **Config**: Configuraciones y validaciones de entorno
- **Prompts**: Prompts de IA versionados y documentados

### Ventajas

✅ **Mantenibilidad**: Cada módulo tiene una responsabilidad clara  
✅ **Testabilidad**: Servicios pueden ser probados independientemente  
✅ **Reutilización**: Servicios pueden usarse desde múltiples routes  
✅ **Type Safety**: Tipos centralizados y validación con Zod  
✅ **Escalabilidad**: Fácil agregar nuevos servicios siguiendo la estructura

## 📝 Uso

### Desde API Routes

```typescript
import { contentAnalysisService } from '@/server/services/content-analysis-service';
import type { AnalyzeContentRequest } from '@/server/types/content-analysis';

export async function POST(request: NextRequest) {
  const { transcript } = await request.json() as AnalyzeContentRequest;
  
  // Validar
  contentAnalysisService.validateTranscript(transcript);
  
  // Ejecutar lógica de negocio
  const data = await contentAnalysisService.analyzeTranscript(transcript);
  
  return NextResponse.json({ success: true, data });
}
```

### Desde Server Actions (futuro)

```typescript
'use server'

import { contentAnalysisService } from '@/server';

export async function analyzeVideo(transcript: string) {
  return await contentAnalysisService.analyzeTranscript(transcript);
}
```

## 🔧 Agregar Nuevo Servicio

1. **Definir tipos** en `types/mi-servicio.ts`
2. **Crear servicio** en `services/mi-servicio.ts`
3. **Agregar config** si necesita en `config/`
4. **Crear prompts** si usa IA en `prompts/`
5. **Exportar** desde `index.ts`
6. **Usar** en tu API route

## 🧪 Testing

Los servicios están diseñados para ser fácilmente testeables:

```typescript
import { ContentAnalysisService } from '@/server/services/content-analysis-service';

describe('ContentAnalysisService', () => {
  it('should validate transcript', () => {
    const service = new ContentAnalysisService();
    expect(() => service.validateTranscript('')).toThrow();
  });
});
```

## 📚 Convenciones

- **Nombres de archivos**: kebab-case (content-analysis-service.ts)
- **Clases**: PascalCase (ContentAnalysisService)
- **Funciones**: camelCase (analyzeTranscript)
- **Constantes**: UPPER_SNAKE_CASE (VIRAL_EDITOR_SYSTEM_PROMPT)
- **Tipos**: PascalCase (ContentAnalysis)
- **Interfaces**: PascalCase con prefijo (AnalyzeContentRequest)
