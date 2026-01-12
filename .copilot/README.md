# Video Wizard - Copilot Knowledge Base

This directory contains documentation and guidelines for GitHub Copilot to understand the Video Wizard project better and provide more accurate suggestions.

## 📚 Documentation Files

### [project-instructions.md](project-instructions.md)
**Main project guidelines and coding standards**

Contains:
- Project overview and tech stack
- Code architecture and structure
- Coding standards and conventions
- API design patterns
- Common development patterns
- Testing approach
- Performance considerations

**Use this when**: You need to understand the project structure, coding standards, or general development guidelines.

### [code-patterns.md](code-patterns.md)
**Reusable code patterns and examples**

Contains:
- API route templates
- Service class patterns
- Type definition patterns
- AI prompt patterns
- React component patterns
- Custom hook patterns
- Utility function patterns
- Testing patterns

**Use this when**: You're implementing a new feature and need a template to follow.

### [architecture-decisions.md](architecture-decisions.md)
**Architecture Decision Records (ADRs)**

Documents important architectural decisions:
- Why we use certain technologies
- Design patterns and their rationale
- Trade-offs considered
- Alternatives explored

**Use this when**: You need to understand why the project is structured a certain way.

## 🎯 Quick Reference

### Project Structure

```
video-wizard/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/               # App Router (pages & API routes)
│   │   ├── components/        # React components
│   │   ├── lib/               # Client utilities
│   │   └── server/            # Server-side code ⭐
│   │       ├── services/      # Business logic
│   │       ├── types/         # Zod schemas & types
│   │       ├── config/        # Configuration
│   │       ├── prompts/       # AI prompts
│   │       └── lib/           # Server utilities
│   └── processing-engine/     # Python backend
└── .copilot/                  # This folder
```

### Key Principles

1. **Separation of Concerns**
   - API routes = HTTP handling only
   - Services = Business logic
   - Types = Zod schemas + TypeScript

2. **Type Safety**
   - Use TypeScript strict mode
   - Define Zod schemas first
   - Infer types from schemas

3. **Error Handling**
   - Use custom error classes
   - Log with structured logger
   - Return user-friendly messages

4. **English Only**
   - All code in English
   - All comments in English
   - All documentation in English

### Common Tasks

#### Adding a New API Endpoint

1. Define types in `server/types/my-feature.ts`
2. Create service in `server/services/my-feature-service.ts`
3. Create route in `app/api/my-feature/route.ts`
4. Export from `server/index.ts`

See [code-patterns.md](code-patterns.md) for detailed templates.

#### Adding AI Functionality

1. Create prompt in `server/prompts/my-prompt.ts`
2. Define schema in `server/types/my-types.ts`
3. Use in service with `generateText` and `Output.object()`

#### Creating a Component

1. Create in `components/my-component.tsx`
2. Use TypeScript interface for props
3. Add `'use client'` only if needed (hooks, events)
4. Use Tailwind CSS for styling

### Technology Decisions

| What | Choice | Why |
|------|--------|-----|
| Framework | Next.js 16 | App Router, Server Components, Turbopack |
| Language | TypeScript | Type safety, better DX |
| Validation | Zod | Runtime + compile-time types |
| AI SDK | Vercel AI SDK | Structured output, streaming |
| Styling | Tailwind CSS | Utility-first, fast development |
| Components | shadcn/ui | Customizable, Tailwind-native |
| Monorepo | pnpm + Turborepo | Fast, efficient, parallel builds |

### File Naming Conventions

- Components: `PascalCase.tsx` (e.g., `VideoWizard.tsx`)
- Pages: `page.tsx` (Next.js convention)
- API Routes: `route.ts` (Next.js convention)
- Utilities: `kebab-case.ts` (e.g., `content-analysis.ts`)
- Types: `kebab-case.ts` (e.g., `content-analysis.ts`)
- Config: `kebab-case.ts` (e.g., `ai.ts`)

### Import Aliases

```typescript
import { Component } from '@/components/Component';
import { myService } from '@/server/services/my-service';
import type { MyType } from '@/server/types/my-types';
import { cn } from '@/lib/utils';
```

## 🤖 For GitHub Copilot

When generating code for this project:

1. ✅ Always use TypeScript
2. ✅ Follow the separation of concerns pattern
3. ✅ Use Zod for schemas
4. ✅ Write English comments and documentation
5. ✅ Include proper error handling
6. ✅ Use the logger utility
7. ✅ Follow existing patterns in `code-patterns.md`
8. ✅ Return consistent response shapes from APIs
9. ✅ Use custom error classes
10. ✅ Add JSDoc comments for public APIs

### When Suggesting Code

- Reference patterns from `code-patterns.md`
- Consider architecture decisions in `architecture-decisions.md`
- Follow conventions from `project-instructions.md`
- Ensure all text is in English

### What NOT to Do

- ❌ Don't put business logic in API routes
- ❌ Don't use JavaScript (use TypeScript)
- ❌ Don't write comments in Spanish
- ❌ Don't use `any` type
- ❌ Don't skip error handling
- ❌ Don't hardcode configuration values

## 📖 External Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [Zod Docs](https://zod.dev/)
- [shadcn/ui Docs](https://ui.shadcn.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/)

## 🔄 Keeping This Updated

When making significant changes to the project:

1. Update relevant documentation files
2. Add new patterns to `code-patterns.md`
3. Document architectural decisions in `architecture-decisions.md`
4. Keep examples up to date with current code

## 📝 Version

Last Updated: 2026-01-11  
Project Version: 0.1.0  
Documentation Version: 1.0.0
