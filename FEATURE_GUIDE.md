# Feature Development Guide

Quick reference for creating and working with feature modules in Video Wizard.

## Creating a New Feature

### 1. Create Feature Structure

```bash
mkdir -p features/my-feature/{components,hooks,types,lib}
touch features/my-feature/{index.ts,README.md}
touch features/my-feature/components/index.ts
touch features/my-feature/types/index.ts
touch features/my-feature/lib/utils.ts
```

### 2. Define Types First

```typescript
// features/my-feature/types/index.ts
export type ProcessingStep = 'idle' | 'processing' | 'complete' | 'error';

export interface MyFeatureState {
  currentStep: ProcessingStep;
  result: MyResult | null;
  error: string;
}

export interface MyResult {
  id: string;
  value: string;
}
```

### 3. Create Utility Functions

```typescript
// features/my-feature/lib/utils.ts

/**
 * Validates feature input
 */
export function validateInput(input: string): string | null {
  if (!input) return 'Input required';
  if (input.length < 10) return 'Too short';
  return null;
}

/**
 * Formats result for display
 */
export function formatResult(result: MyResult): string {
  return `${result.id}: ${result.value}`;
}
```

### 4. Build Presentational Components

```typescript
// features/my-feature/components/my-component.tsx
'use client';

import { Card } from '@/components/ui/card';
import type { MyResult } from '../types';

interface MyComponentProps {
  result: MyResult;
  onAction: (id: string) => void;
}

/**
 * My Component
 * 
 * Displays feature result
 */
export function MyComponent({ result, onAction }: MyComponentProps) {
  return (
    <Card className="p-6">
      <h3>{result.value}</h3>
      <button onClick={() => onAction(result.id)}>
        Action
      </button>
    </Card>
  );
}
```

### 5. Create Feature Hook

```typescript
// features/my-feature/hooks/use-my-feature.ts
'use client';

import { useState, useCallback } from 'react';
import type { MyFeatureState } from '../types';
import { validateInput } from '../lib/utils';

interface UseMyFeatureOptions {
  onComplete?: (data: unknown) => void;
  onError?: (error: Error) => void;
}

export function useMyFeature(options: UseMyFeatureOptions = {}) {
  const [state, setState] = useState<MyFeatureState>({
    currentStep: 'idle',
    result: null,
    error: '',
  });

  const process = useCallback(async (input: string) => {
    const error = validateInput(input);
    if (error) {
      setState(prev => ({ ...prev, error }));
      return;
    }

    try {
      setState(prev => ({ ...prev, currentStep: 'processing' }));
      
      const response = await fetch('/api/my-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      });

      const data = await response.json();
      
      setState(prev => ({
        ...prev,
        currentStep: 'complete',
        result: data.result,
      }));
      
      options.onComplete?.(data.result);
    } catch (err) {
      setState(prev => ({
        ...prev,
        currentStep: 'error',
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
      options.onError?.(err instanceof Error ? err : new Error('Unknown error'));
    }
  }, [options]);

  const reset = useCallback(() => {
    setState({ currentStep: 'idle', result: null, error: '' });
  }, []);

  return { ...state, process, reset };
}
```

### 6. Export Components

```typescript
// features/my-feature/components/index.ts
export { MyComponent } from './my-component';
export { MyForm } from './my-form';
export { MyResults } from './my-results';
```

### 7. Main Feature Export

```typescript
// features/my-feature/index.ts

// Components
export * from './components';

// Hooks
export { useMyFeature } from './hooks/use-my-feature';

// Types
export type * from './types';

// Utils
export * from './lib/utils';
```

### 8. Use in Page

```typescript
// app/my-feature/page.tsx
'use client';

import {
  MyComponent,
  MyForm,
  MyResults,
  useMyFeature,
} from '@/features/my-feature';

export default function MyFeaturePage() {
  const { result, process, reset } = useMyFeature({
    onComplete: (data) => console.log('Done!', data),
  });

  return (
    <div className="container">
      <MyForm onSubmit={process} onReset={reset} />
      {result && <MyResults result={result} />}
    </div>
  );
}
```

### 9. Write Documentation

```markdown
<!-- features/my-feature/README.md -->
# My Feature

Description of what this feature does.

## Components

- **MyComponent**: Does X
- **MyForm**: Handles input
- **MyResults**: Shows output

## Hooks

- **useMyFeature**: Main feature hook

## Usage

[Examples here]
```

## Checklist for New Features

### Setup
- [ ] Create feature folder structure
- [ ] Add types in `types/index.ts`
- [ ] Add utilities in `lib/utils.ts`
- [ ] Create `README.md`

### Components
- [ ] Build presentational components
- [ ] Use 'use client' directive appropriately
- [ ] Add TypeScript interfaces for props
- [ ] Add JSDoc comments
- [ ] Export via `components/index.ts`

### Logic
- [ ] Create custom hook in `hooks/`
- [ ] Implement state management
- [ ] Add error handling
- [ ] Add lifecycle callbacks (onComplete, onError)

### Integration
- [ ] Create main export in `index.ts`
- [ ] Update page to use feature
- [ ] Test workflow end-to-end

### Documentation
- [ ] Write feature README
- [ ] Document all components
- [ ] Add usage examples
- [ ] List props and types

### Quality
- [ ] Run TypeScript check: `pnpm type-check`
- [ ] Run build: `pnpm build`
- [ ] Test in browser
- [ ] Check for console errors

## Best Practices

### Component Design

✅ **DO:**
```typescript
// Atomic, single responsibility
export function VideoUploader({ file, onFileSelect }: Props) {
  return <input type="file" onChange={onFileSelect} />;
}
```

❌ **DON'T:**
```typescript
// Multiple responsibilities
export function VideoProcessor() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  // Upload logic
  // Process logic
  // Display logic
  return <div>...</div>;
}
```

### State Management

✅ **DO:**
```typescript
// Centralized in hook
const { state, actions } = useFeature();
```

❌ **DON'T:**
```typescript
// Scattered useState in components
const [state1, setState1] = useState();
const [state2, setState2] = useState();
```

### Error Handling

✅ **DO:**
```typescript
// Provide callbacks
useFeature({
  onError: (err) => console.error(err),
  onComplete: (data) => console.log(data),
});
```

❌ **DON'T:**
```typescript
// Silent failures
try {
  await process();
} catch (err) {
  // Nothing
}
```

### Type Safety

✅ **DO:**
```typescript
// Explicit types
interface Props {
  value: string;
  onChange: (value: string) => void;
}
```

❌ **DON'T:**
```typescript
// Any types
interface Props {
  value: any;
  onChange: any;
}
```

## Common Patterns

### Conditional Rendering

```typescript
export default function Page() {
  const { currentStep, result, error } = useFeature();

  return (
    <>
      {currentStep === 'idle' && <WelcomeMessage />}
      {currentStep === 'processing' && <LoadingSpinner />}
      {currentStep === 'complete' && result && <Results data={result} />}
      {error && <ErrorMessage error={error} />}
    </>
  );
}
```

### Loading States

```typescript
export function MyButton({ onClick, isLoading }: Props) {
  return (
    <Button onClick={onClick} disabled={isLoading}>
      {isLoading ? 'Processing...' : 'Submit'}
    </Button>
  );
}
```

### Error Display

```typescript
export function ErrorDisplay({ error }: { error?: string }) {
  if (!error) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded p-4">
      <p className="text-sm text-red-700">{error}</p>
    </div>
  );
}
```

### Progress Tracking

```typescript
const steps: ProcessingStep[] = ['upload', 'transcribe', 'analyze'];

export function ProgressBar({ currentStep }: Props) {
  return (
    <div className="flex gap-2">
      {steps.map(step => (
        <div
          key={step}
          className={cn(
            'flex-1 h-2 rounded',
            currentStep === step ? 'bg-blue-500' : 'bg-gray-300'
          )}
        />
      ))}
    </div>
  );
}
```

## Troubleshooting

### Build Errors

**Error:** `Cannot find module '@/features/my-feature'`
- Ensure `index.ts` exists and exports correctly
- Check tsconfig.json path aliases
- Restart TypeScript server

**Error:** `'use client' must be at top of file`
- Move 'use client' to very first line
- Remove any comments above it

### Type Errors

**Error:** `Type 'X' is not assignable to type 'Y'`
- Check prop types match interfaces
- Ensure null/undefined handled correctly
- Use type guards: `if (value) { ... }`

### Runtime Errors

**Error:** `Cannot read property of undefined`
- Add null checks: `data?.property`
- Use optional chaining
- Provide default values

## Examples

See existing features:
- `features/video/` - Complete video processing feature
- `features/video/README.md` - Detailed documentation

## References

- [Project Instructions](../.copilot/project-instructions.md)
- [Code Patterns](../.copilot/code-patterns.md)
- [Architecture Decisions](../.copilot/architecture-decisions.md)
- [Architecture Overview](../ARCHITECTURE.md)
