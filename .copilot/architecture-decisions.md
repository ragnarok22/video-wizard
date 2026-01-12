# Architecture Decision Records (ADRs)

## ADR-001: Server-Side Code Organization

**Date**: 2026-01-11  
**Status**: Accepted

### Context

The original API routes contained business logic, AI prompts, and type definitions mixed together, making the code hard to maintain, test, and scale.

### Decision

Create a dedicated `server/` folder with clear separation of concerns:

- `server/services/` - Business logic
- `server/types/` - Zod schemas and TypeScript types
- `server/config/` - Configuration and environment variables
- `server/prompts/` - AI prompts
- `server/lib/` - Shared utilities

### Consequences

**Positive:**
- Better testability (services can be tested independently)
- Improved maintainability (clear responsibility for each module)
- Type safety (centralized types prevent drift)
- Scalability (easy to add new services)
- Reusability (services can be used from multiple routes)

**Negative:**
- More files to navigate
- Slightly more boilerplate

### Alternatives Considered

1. Keep everything in API routes (rejected - not maintainable)
2. Use a traditional `src/` folder (rejected - conflicts with Next.js conventions)

---

## ADR-002: TypeScript Over JavaScript

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need to ensure type safety and prevent runtime errors in a growing codebase.

### Decision

Use TypeScript with strict mode enabled for all code. Use Zod for runtime validation.

### Consequences

**Positive:**
- Catch errors at compile time
- Better IDE support and autocomplete
- Self-documenting code
- Easier refactoring

**Negative:**
- Learning curve for team members unfamiliar with TypeScript
- Some additional development time for type definitions

---

## ADR-003: Zod for Schema Validation

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need both runtime validation and TypeScript types for API payloads and AI responses.

### Decision

Use Zod schemas as the single source of truth. Infer TypeScript types from Zod schemas.

### Consequences

**Positive:**
- Single source of truth for types
- Runtime validation prevents bad data
- Better error messages
- Works seamlessly with Vercel AI SDK

**Negative:**
- Learning curve for Zod syntax
- Schemas can become verbose

---

## ADR-004: Vercel AI SDK for AI Integration

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need to integrate OpenAI's GPT-4 for content analysis with structured output.

### Decision

Use Vercel AI SDK with `Output.object()` for structured responses validated by Zod schemas.

### Consequences

**Positive:**
- Type-safe AI responses
- Built-in streaming support
- Works well with Next.js
- Structured output reduces parsing errors

**Negative:**
- Couples code to Vercel ecosystem
- Less flexibility than raw OpenAI API

---

## ADR-005: Custom Error Classes

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need to differentiate between validation errors, configuration errors, and service errors.

### Decision

Create custom error classes:
- `ValidationError` - Input validation failures
- `ConfigurationError` - Environment/config issues
- `ServiceError` - Business logic failures

### Consequences

**Positive:**
- Clear error types
- Better error handling in API routes
- Easier to provide user-friendly messages

**Negative:**
- More classes to maintain

---

## ADR-006: Singleton Pattern for Services

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Services are stateless and should be reused across requests.

### Decision

Export singleton instances of services:

```typescript
export const myService = new MyService();
```

### Consequences

**Positive:**
- Prevents unnecessary instantiation
- Simpler imports
- Consistent instance across app

**Negative:**
- Harder to mock in tests (need to use module mocking)
- No per-request state (must use dependency injection)

---

## ADR-007: Structured Logging

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need to track operations and debug issues in production.

### Decision

Use a structured logger that outputs JSON:

```typescript
logger.info('Operation', { context });
logger.error('Error', error, { context });
```

### Consequences

**Positive:**
- Easier to parse logs in production
- Better integration with log aggregation tools
- Consistent format

**Negative:**
- Less human-readable in development
- Requires log viewer for best experience

---

## ADR-008: English-Only Codebase

**Date**: 2026-01-11  
**Status**: Accepted

### Context

International team, GitHub Copilot works better with English, industry standard.

### Decision

All code, comments, documentation, and commit messages MUST be in English.

### Consequences

**Positive:**
- Better Copilot suggestions
- Easier for international contributors
- Industry standard practice
- Better documentation portability

**Negative:**
- Team members must be comfortable with English

---

## ADR-009: Monorepo with pnpm Workspaces

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Project has multiple apps (web, processing-engine) that share types and utilities.

### Decision

Use pnpm workspaces with Turborepo for monorepo management.

### Consequences

**Positive:**
- Code sharing between apps
- Faster installs with pnpm
- Parallel builds with Turborepo
- Single version control

**Negative:**
- More complex setup
- Harder to split into separate repos later

---

## ADR-010: shadcn/ui for Components

**Date**: 2026-01-11  
**Status**: Accepted

### Context

Need high-quality, customizable UI components that work with Tailwind CSS.

### Decision

Use shadcn/ui components copied into the project (not installed as dependencies).

### Consequences

**Positive:**
- Full control over component code
- Easy customization
- No version conflicts
- Works perfectly with Tailwind

**Negative:**
- Manual updates when shadcn/ui improves
- More code in repository

---

## ADR-011: Feature Module Architecture (Screaming Architecture)

**Date**: 2026-01-11  
**Status**: Accepted

### Context

As the application grows, organizing code by technical layers (components/, hooks/, lib/) makes it hard to understand what the application does. Related code is scattered across different folders.

### Decision

Organize code by feature modules using screaming architecture:

```
features/
└── video/
    ├── components/    # Presentational components
    ├── hooks/         # Feature-specific hooks
    ├── types/         # Feature-specific types
    ├── lib/           # Feature-specific utilities
    ├── index.ts       # Module export
    └── README.md      # Feature documentation
```

**Principles:**
1. **Feature-First**: Group by what the app does, not how it's built
2. **Presentational Components**: Client-side, atomic, receive data via props
3. **Self-Contained**: Each feature is independent and portable
4. **Clear Boundaries**: Features export through a single index file

### Consequences

**Positive:**
- **Discoverability**: New developers instantly understand what the app does
- **Maintainability**: All related code is in one place
- **Reusability**: Features can be extracted into libraries
- **Scalability**: Add features without affecting others
- **Testability**: Test entire features in isolation
- **Team Collaboration**: Teams can own specific features

**Negative:**
- More nested folder structure
- Some shared utilities may be duplicated
- Requires discipline to maintain boundaries

### Implementation Guidelines

**Component Rules:**
- Components are presentational (atomic)
- Receive data via props, emit events via callbacks
- No business logic or API calls
- Use `'use client'` directive when needed
- Export through `components/index.ts`

**Hook Rules:**
- Manage feature-specific state and side effects
- Handle API calls and data transformation
- Provide callbacks for lifecycle events (onComplete, onError)
- Return all state and actions needed by components

**Type Rules:**
- Define all feature-specific interfaces and types
- Use TypeScript for type safety
- Export through `types/index.ts`

**Utility Rules:**
- Pure functions for data transformation and validation
- No side effects or state
- Export through `lib/utils.ts`

### Alternatives Considered

1. **Technical Layer Organization** (rejected)
   - Pro: Simple structure
   - Con: Hard to find related code, poor discoverability

2. **Container/Presentational Pattern with Server Components** (rejected for now)
   - Pro: Better separation of data fetching
   - Con: Adds complexity, server components can't use hooks

3. **Domain-Driven Design** (too complex)
   - Pro: Very clear boundaries
   - Con: Overkill for current app size

### Migration Strategy

1. Create `features/` folder
2. Start with video feature (largest module)
3. Gradually migrate other features (content-intelligence, etc.)
4. Keep existing structure until all features migrated
5. Update imports gradually

### Examples

See:
- `features/video/` - Complete video processing feature
- `features/video/README.md` - Detailed feature documentation
- `.copilot/code-patterns.md` - Feature module pattern examples

### References

- [Screaming Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)
- [Feature-Sliced Design](https://feature-sliced.design/)
- [React Component Patterns](https://kentcdodds.com/blog/how-to-use-react-context-effectively)
