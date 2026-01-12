# Video Wizard - Project Instructions for GitHub Copilot

## Project Overview

Video Wizard is a full-stack application for analyzing video content and identifying viral-worthy clips using AI. The project consists of:

- **Web App** (Next.js 16 + TypeScript + Tailwind CSS)
- **Processing Engine** (Python + FastAPI)

## Tech Stack

### Frontend (apps/web)
- **Framework**: Next.js 16.1.1 (App Router, Turbopack)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Base UI components)
- **AI SDK**: Vercel AI SDK (@ai-sdk/openai)
- **State Management**: React hooks
- **Package Manager**: pnpm

### Backend (apps/processing-engine)
- **Framework**: FastAPI (Python)
- **Video Processing**: FFmpeg
- **Transcription**: Whisper
- **Audio Processing**: pydub

## Code Architecture

### Web App Structure

```
apps/web/
├── app/                        # Next.js App Router
│   ├── api/                   # API Routes (HTTP handlers only)
│   ├── video-wizard/          # Main feature page
│   └── content-intelligence/  # Content analysis page
├── components/                 # React components
│   └── ui/                    # shadcn/ui components
├── lib/                       # Client-side utilities
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # Client types (re-exports from server)
│   └── utils/                 # Client utilities
└── server/                    # Server-side code (NEW)
    ├── services/              # Business logic
    ├── types/                 # Zod schemas & TypeScript types
    ├── config/                # Server configuration
    ├── prompts/               # AI prompts
    └── lib/                   # Server utilities
```

## Coding Standards

### General Rules

1. **Language**: All code, comments, and documentation MUST be in English
2. **Type Safety**: Use TypeScript strict mode, avoid `any`
3. **Naming Conventions**:
   - Files: `kebab-case.ts`
   - Classes: `PascalCase`
   - Functions/Variables: `camelCase`
   - Constants: `UPPER_SNAKE_CASE`
   - React Components: `PascalCase`

### Server-Side Code (apps/web/server)

#### Separation of Concerns

```typescript
// ❌ DON'T: Business logic in API routes
export async function POST(request: NextRequest) {
  const { transcript } = await request.json();
  const result = await generateText({ /* AI logic here */ });
  return NextResponse.json(result);
}

// ✅ DO: API routes only handle HTTP
export async function POST(request: NextRequest) {
  const { transcript } = await request.json();
  const data = await contentAnalysisService.analyzeTranscript(transcript);
  return NextResponse.json({ success: true, data });
}
```

#### Services Pattern

- **Services** contain ALL business logic
- **Services** are testable classes with clear interfaces
- **Services** use dependency injection for configuration

```typescript
// server/services/my-service.ts
export class MyService {
  async processData(input: string): Promise<Result> {
    // Business logic here
  }
}

export const myService = new MyService();
```

#### Type Safety with Zod

- Define Zod schemas in `server/types/`
- Infer TypeScript types from schemas
- Export both schemas and types

```typescript
// server/types/my-types.ts
export const MySchema = z.object({
  field: z.string(),
});

export type MyType = z.infer<typeof MySchema>;
```

#### Error Handling

```typescript
// Use custom error classes
throw new ValidationError('Invalid input');
throw new ConfigurationError('Missing API key');
throw new ServiceError('Operation failed', originalError);

// Use the logger utility
logger.info('Operation started', { context });
logger.error('Operation failed', error, { context });
```

### Client-Side Code

#### React Components

```typescript
'use client'; // Only when needed (hooks, browser APIs)

// Use TypeScript interfaces for props
interface MyComponentProps {
  title: string;
  onAction: (id: string) => void;
}

export function MyComponent({ title, onAction }: MyComponentProps) {
  // Component logic
}
```

#### Custom Hooks

```typescript
// lib/hooks/useMyHook.ts
'use client';

export function useMyHook(options?: MyHookOptions) {
  const [state, setState] = useState<MyType | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Hook logic
  
  return { state, error };
}
```

### Styling Guidelines

1. **Use Tailwind CSS** utility classes
2. **Component variants**: Use `cva` (class-variance-authority)
3. **Responsive design**: Mobile-first approach
4. **Dark mode**: Consider dark mode support

```typescript
// Using cva for variants
import { cva } from 'class-variance-authority';

const buttonVariants = cva('base-classes', {
  variants: {
    variant: {
      default: 'default-classes',
      outline: 'outline-classes',
    },
  },
});
```

## API Design

### REST API Conventions

- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return consistent response shapes:

```typescript
// Success response
{ success: true, data: T }

// Error response
{ success: false, error: string, details?: string }
```

- Use appropriate status codes:
  - 200: Success
  - 400: Bad Request (validation errors)
  - 500: Server Error

### AI Integration

- All AI prompts go in `server/prompts/`
- Document prompt purpose and structure
- Use structured output with Zod schemas

```typescript
const { output } = await generateText({
  model: AI_MODELS.contentAnalysis,
  output: Output.object({ schema: MySchema }),
  system: SYSTEM_PROMPT,
  prompt: buildPrompt(input),
});
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
NODE_ENV=development
PORT=3000
```

## Testing Approach

1. **Services**: Unit test business logic
2. **API Routes**: Integration tests with mock services
3. **Components**: Component tests with React Testing Library
4. **Types**: Validate Zod schemas

## Performance Considerations

1. **Server Components**: Use by default, add 'use client' only when needed
2. **Code Splitting**: Lazy load heavy components
3. **Caching**: Use Next.js caching strategies
4. **Optimize Images**: Use Next.js Image component

## Git Workflow

1. **Branch naming**: `feature/name`, `fix/name`, `refactor/name`
2. **Commits**: Clear, descriptive messages in English
3. **Pull Requests**: Include description and test results

## Common Patterns

### Adding a New API Endpoint

1. Define types in `server/types/my-feature.ts`
2. Create service in `server/services/my-feature-service.ts`
3. Create route in `app/api/my-feature/route.ts`
4. Export from `server/index.ts`

### Adding a New Component

1. Create component in `components/my-component.tsx`
2. Add to `components/ui/` if it's a reusable UI component
3. Use TypeScript interfaces for props
4. Document with JSDoc if complex

### Error Handling Pattern

```typescript
// In services
try {
  return await operation();
} catch (error) {
  logger.error('Operation failed', error);
  throw new ServiceError('User-friendly message', error);
}

// In API routes
try {
  const result = await service.operation();
  return NextResponse.json({ success: true, data: result });
} catch (error) {
  logger.error('API error', error);
  return NextResponse.json(
    { success: false, error: 'User-friendly message' },
    { status: 500 }
  );
}
```

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zod Documentation](https://zod.dev/)

## Project-Specific Notes

### Video Processing Flow

1. User uploads video to processing engine (Python)
2. Engine extracts audio and generates transcription
3. Web app receives transcription
4. AI analyzes transcription for viral clips
5. User views results and can export clips

### AI Prompts

- **Viral Editor**: Identifies viral-worthy clips based on engagement criteria
- Focus on hooks, emotional impact, and standalone value
- Scores clips 0-100 based on viral potential

### State Management

- Use React hooks for local state
- Consider Context API for shared state
- Avoid prop drilling with composition

## When Making Changes

1. ✅ Follow the established patterns in existing code
2. ✅ Keep API routes thin, services fat
3. ✅ Add proper TypeScript types
4. ✅ Write clear JSDoc comments
5. ✅ Use the logger utility
6. ✅ Handle errors gracefully
7. ✅ Test your changes
8. ✅ All code and comments in ENGLISH only
