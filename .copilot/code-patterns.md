# Code Patterns and Examples

This file contains common code patterns used in the Video Wizard project. Use these as references when implementing new features.

## API Route Pattern

```typescript
// app/api/my-feature/route.ts
import { myService } from '@/server/services/my-service';
import type {
  MyRequest,
  MyResponse,
  MyErrorResponse,
} from '@/server/types/my-types';
import { NextRequest, NextResponse } from 'next/server';

/**
 * API Route Handler for my feature
 * 
 * POST /api/my-feature
 * Description of what this endpoint does
 */
export async function POST(
  request: NextRequest
): Promise<NextResponse<MyResponse | MyErrorResponse>> {
  try {
    // Parse request body
    const body = (await request.json()) as MyRequest;
    const { input } = body;

    // Validate input
    try {
      myService.validateInput(input);
    } catch (validationError) {
      return NextResponse.json(
        {
          success: false,
          error: validationError instanceof Error 
            ? validationError.message 
            : 'Invalid input',
        },
        { status: 400 }
      );
    }

    // Execute business logic
    const data = await myService.processInput(input);

    return NextResponse.json({
      success: true,
      data,
    });
  } catch (error) {
    console.error('API error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Operation failed',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
```

## Service Pattern

```typescript
// server/services/my-service.ts
import { AI_MODELS, validateAIConfig } from '../config/ai';
import { logger, safeAsync, validateString } from '../lib/utils';
import { MY_PROMPT, buildMyPrompt } from '../prompts/my-prompt';
import {
  MyResult,
  MyResultSchema,
} from '../types/my-types';
import { generateText, Output } from 'ai';

/**
 * Service for my feature
 * 
 * Provides functionality to process data and interact with AI.
 */
export class MyService {
  /**
   * Processes input data
   * 
   * @param input - The input data to process
   * @returns Processed result
   * @throws Error if validation fails or processing fails
   */
  async processInput(input: string): Promise<MyResult> {
    // Validate configuration
    validateAIConfig();
    
    // Validate input
    this.validateInput(input);

    logger.info('Starting processing', {
      inputLength: input.length,
    });

    return safeAsync(async () => {
      const { output } = await generateText({
        model: AI_MODELS.contentAnalysis,
        output: Output.object({
          schema: MyResultSchema,
        }),
        system: MY_PROMPT,
        prompt: buildMyPrompt(input),
      });

      logger.info('Processing completed', {
        resultSize: output.items.length,
      });

      return output;
    }, 'Processing failed');
  }

  /**
   * Validates input data
   * 
   * @param input - The input to validate
   * @returns true if valid
   * @throws ValidationError if invalid
   */
  validateInput(input: string): boolean {
    validateString(input, 'Input', {
      minLength: 10,
      maxLength: 10000,
    });

    return true;
  }
}

/**
 * Singleton instance of the service
 */
export const myService = new MyService();
```

## Types Pattern

```typescript
// server/types/my-types.ts
import { z } from 'zod';

/**
 * Zod schema for my item
 */
export const MyItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  score: z.number().min(0).max(100),
  metadata: z.object({
    created: z.string().datetime(),
    tags: z.array(z.string()),
  }),
});

/**
 * Schema for the complete result
 */
export const MyResultSchema = z.object({
  items: z.array(MyItemSchema),
  total: z.number(),
  summary: z.string(),
});

/**
 * TypeScript types inferred from schemas
 */
export type MyItem = z.infer<typeof MyItemSchema>;
export type MyResult = z.infer<typeof MyResultSchema>;

/**
 * Request payload
 */
export interface MyRequest {
  input: string;
  options?: {
    maxResults?: number;
    includeMetadata?: boolean;
  };
}

/**
 * Success response payload
 */
export interface MyResponse {
  success: true;
  data: MyResult;
}

/**
 * Error response payload
 */
export interface MyErrorResponse {
  success: false;
  error: string;
  details?: string;
}
```

## AI Prompt Pattern

```typescript
// server/prompts/my-prompt.ts

/**
 * System prompt for my AI feature
 * 
 * This prompt guides the AI model to perform a specific task.
 */
export const MY_PROMPT = `You are an expert in [domain].

Your task is to [describe the task].

CRITERIA:
1. **First Criterion** - Description
2. **Second Criterion** - Description
3. **Third Criterion** - Description

GUIDELINES:
- Guideline 1
- Guideline 2
- Guideline 3

Focus on quality and accuracy.`;

/**
 * Builds the user prompt for processing
 * 
 * @param input - The input data
 * @param options - Optional processing options
 * @returns Formatted prompt string
 */
export function buildMyPrompt(
  input: string,
  options?: { style?: string }
): string {
  const styleNote = options?.style 
    ? `\nStyle preference: ${options.style}` 
    : '';

  return `Process the following input:

${input}${styleNote}

Remember to:
- Apply all criteria
- Provide clear reasoning
- Be thorough and accurate`;
}
```

## Custom Hook Pattern

```typescript
// lib/hooks/useMyFeature.ts
'use client';

import type {
  MyRequest,
  MyResponse,
  MyErrorResponse,
  MyResult,
} from '@/lib/types/my-types';
import { useState } from 'react';

interface UseMyFeatureOptions {
  onSuccess?: (data: MyResult) => void;
  onError?: (error: string) => void;
}

export function useMyFeature(options?: UseMyFeatureOptions) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<MyResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const process = async (input: string) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch('/api/my-feature', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input } satisfies MyRequest),
      });

      const data: MyResponse | MyErrorResponse = await response.json();

      if (!response.ok || !data.success) {
        const errorData = data as MyErrorResponse;
        const errorMessage = errorData.error || 'Operation failed';
        setError(errorMessage);
        options?.onError?.(errorMessage);
        return null;
      }

      const successData = data as MyResponse;
      setResult(successData.data);
      options?.onSuccess?.(successData.data);
      return successData.data;
    } catch (err) {
      const errorMessage = 
        err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      options?.onError?.(errorMessage);
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setIsProcessing(false);
  };

  return {
    process,
    isProcessing,
    result,
    error,
    reset,
  };
}
```

## React Component Pattern

```typescript
// components/my-component.tsx
'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useMyFeature } from '@/lib/hooks/useMyFeature';
import { useState } from 'react';

interface MyComponentProps {
  title: string;
  onComplete?: (result: string) => void;
}

export function MyComponent({ title, onComplete }: MyComponentProps) {
  const [input, setInput] = useState('');
  const { process, isProcessing, result, error } = useMyFeature({
    onSuccess: (data) => {
      console.log('Success:', data);
      onComplete?.(data.summary);
    },
    onError: (err) => {
      console.error('Error:', err);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await process(input);
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter input..."
          className="w-full px-4 py-2 border rounded"
          disabled={isProcessing}
        />
        
        <Button type="submit" disabled={isProcessing}>
          {isProcessing ? 'Processing...' : 'Submit'}
        </Button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-600 rounded">
          Error: {error}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-green-50 rounded">
          <h3 className="font-semibold mb-2">Result:</h3>
          <p>{result.summary}</p>
        </div>
      )}
    </Card>
  );
}
```

## Configuration Pattern

```typescript
// server/config/my-config.ts
import { requireEnv, getEnv } from '../lib/utils';

/**
 * Configuration for my feature
 */
export const MY_CONFIG = {
  apiKey: requireEnv('MY_API_KEY'),
  apiUrl: getEnv('MY_API_URL', 'https://api.example.com'),
  timeout: parseInt(getEnv('MY_TIMEOUT', '30000')),
  maxRetries: parseInt(getEnv('MY_MAX_RETRIES', '3')),
} as const;

/**
 * Validates that the configuration is valid
 */
export function validateMyConfig(): void {
  if (!MY_CONFIG.apiKey.startsWith('sk-')) {
    throw new Error('Invalid API key format');
  }
  
  if (MY_CONFIG.timeout < 1000) {
    throw new Error('Timeout must be at least 1000ms');
  }
}
```

## Utility Function Pattern

```typescript
// server/lib/my-utils.ts

/**
 * Formats a timestamp into a readable date string
 */
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toISOString();
}

/**
 * Calculates percentage with precision
 */
export function calculatePercentage(
  value: number,
  total: number,
  precision: number = 2
): number {
  if (total === 0) return 0;
  return Number(((value / total) * 100).toFixed(precision));
}

/**
 * Chunks an array into smaller arrays
 */
export function chunkArray<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

/**
 * Delays execution for specified milliseconds
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retries an async operation with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');
      
      if (i < maxRetries - 1) {
        const delayMs = baseDelay * Math.pow(2, i);
        await delay(delayMs);
      }
    }
  }

  throw lastError!;
}
```

## Testing Pattern

```typescript
// __tests__/services/my-service.test.ts
import { MyService } from '@/server/services/my-service';
import { ValidationError } from '@/server/lib/utils';

describe('MyService', () => {
  let service: MyService;

  beforeEach(() => {
    service = new MyService();
  });

  describe('validateInput', () => {
    it('should accept valid input', () => {
      expect(() => service.validateInput('valid input')).not.toThrow();
    });

    it('should reject empty input', () => {
      expect(() => service.validateInput('')).toThrow(ValidationError);
    });

    it('should reject input that is too short', () => {
      expect(() => service.validateInput('short')).toThrow(ValidationError);
    });
  });

  describe('processInput', () => {
    it('should process valid input successfully', async () => {
      const result = await service.processInput('test input here');
      
      expect(result).toBeDefined();
      expect(result.items).toBeInstanceOf(Array);
      expect(result.total).toBeGreaterThan(0);
    });
  });
});
```

## Feature Module Pattern (Screaming Architecture)

Organize related functionality into feature modules with clear boundaries.

### Feature Module Structure

```
features/
└── my-feature/
    ├── components/          # Presentational components (client-side)
    │   ├── feature-header.tsx
    │   ├── feature-form.tsx
    │   ├── feature-results.tsx
    │   └── index.ts        # Component exports
    ├── hooks/              # Custom hooks
    │   └── use-feature.ts
    ├── types/              # Type definitions
    │   └── index.ts
    ├── lib/                # Utilities
    │   └── utils.ts
    ├── index.ts            # Main module export
    └── README.md           # Feature documentation
```

### Presentational Component

```typescript
// features/my-feature/components/feature-form.tsx
'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import type { ProcessingStep } from '../types';

interface FeatureFormProps {
  value: string;
  currentStep: ProcessingStep;
  onSubmit: (value: string) => void;
  onReset: () => void;
  error?: string;
}

/**
 * Feature Form Component
 * 
 * Presentational component for feature input form
 */
export function FeatureForm({
  value,
  currentStep,
  onSubmit,
  onReset,
  error,
}: FeatureFormProps) {
  const isProcessing = currentStep !== 'idle';

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Enter Data</h2>
      
      <div className="space-y-4">
        <input
          type="text"
          value={value}
          onChange={(e) => onSubmit(e.target.value)}
          disabled={isProcessing}
          className="w-full p-2 border rounded"
        />

        <div className="flex gap-2">
          <Button
            onClick={() => onSubmit(value)}
            disabled={!value || isProcessing}
            size="lg"
          >
            {isProcessing ? 'Processing...' : 'Submit'}
          </Button>
          
          {currentStep !== 'idle' && (
            <Button
              variant="outline"
              onClick={onReset}
              disabled={isProcessing}
            >
              Reset
            </Button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </div>
    </Card>
  );
}
```

### Feature Hook

```typescript
// features/my-feature/hooks/use-feature.ts
'use client';

import { useState, useCallback } from 'react';
import type { FeatureState, ProcessingStep } from '../types';
import { validateInput } from '../lib/utils';

interface UseFeatureOptions {
  onComplete?: (data: unknown) => void;
  onError?: (error: Error) => void;
}

/**
 * Custom hook for feature processing workflow
 */
export function useFeature({ onComplete, onError }: UseFeatureOptions = {}) {
  const [state, setState] = useState<FeatureState>({
    input: '',
    currentStep: 'idle',
    result: null,
    error: '',
    progress: '',
  });

  const updateState = useCallback((updates: Partial<FeatureState>) => {
    setState((prev) => ({ ...prev, ...updates }));
  }, []);

  const processInput = useCallback(async () => {
    if (!state.input) return;

    try {
      // Validate
      const error = validateInput(state.input);
      if (error) {
        updateState({ error });
        return;
      }

      // Step 1: Process
      updateState({ currentStep: 'processing', progress: 'Processing...' });

      const response = await fetch('/api/my-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: state.input }),
      });

      if (!response.ok) {
        throw new Error('Processing failed');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Processing error');
      }

      updateState({
        result: data.data,
        currentStep: 'complete',
        progress: 'Complete!',
      });

      onComplete?.(data.data);
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Unknown error';
      updateState({ error, currentStep: 'error' });
      onError?.(err instanceof Error ? err : new Error(error));
    }
  }, [state.input, updateState, onComplete, onError]);

  const reset = useCallback(() => {
    setState({
      input: '',
      currentStep: 'idle',
      result: null,
      error: '',
      progress: '',
    });
  }, []);

  const setInput = useCallback(
    (input: string) => {
      updateState({ input, error: '' });
    },
    [updateState]
  );

  return {
    ...state,
    setInput,
    processInput,
    reset,
  };
}
```

### Feature Types

```typescript
// features/my-feature/types/index.ts
export type ProcessingStep = 
  | 'idle' 
  | 'processing' 
  | 'complete' 
  | 'error';

export interface FeatureResult {
  id: string;
  value: string;
  score: number;
}

export interface FeatureState {
  input: string;
  currentStep: ProcessingStep;
  result: FeatureResult | null;
  error: string;
  progress: string;
}
```

### Feature Utilities

```typescript
// features/my-feature/lib/utils.ts

/**
 * Validates feature input
 * 
 * @param input - The input to validate
 * @returns Error message or null if valid
 */
export function validateInput(input: string): string | null {
  if (!input || input.trim().length === 0) {
    return 'Input is required';
  }

  if (input.length < 10) {
    return 'Input must be at least 10 characters';
  }

  if (input.length > 1000) {
    return 'Input must be less than 1000 characters';
  }

  return null;
}

/**
 * Formats result data for display
 */
export function formatResult(result: FeatureResult): string {
  return `${result.value} (Score: ${result.score})`;
}
```

### Feature Index (Main Export)

```typescript
// features/my-feature/index.ts

// Export all components
export * from './components';

// Export hooks
export { useFeature } from './hooks/use-feature';

// Export types
export type * from './types';

// Export utilities
export * from './lib/utils';
```

### Component Index

```typescript
// features/my-feature/components/index.ts

export { FeatureHeader } from './feature-header';
export { FeatureForm } from './feature-form';
export { FeatureResults } from './feature-results';
```

### Using the Feature Module

```typescript
// app/my-feature/page.tsx
'use client';

import {
  FeatureHeader,
  FeatureForm,
  FeatureResults,
  useFeature,
} from '@/features/my-feature';

export default function MyFeaturePage() {
  const {
    input,
    currentStep,
    result,
    error,
    setInput,
    processInput,
    reset,
  } = useFeature({
    onComplete: (data) => console.log('Done!', data),
    onError: (err) => console.error('Error:', err),
  });

  return (
    <div className="container mx-auto py-8">
      <FeatureHeader />
      
      <FeatureForm
        value={input}
        currentStep={currentStep}
        onSubmit={setInput}
        onReset={reset}
        error={error}
      />

      {result && <FeatureResults result={result} />}
    </div>
  );
}
```

## Use These Patterns When

- **Creating a new API endpoint**: Use API Route + Service + Types pattern
- **Adding AI functionality**: Use Service + Prompt pattern
- **Creating interactive UI**: Use Component + Hook pattern
- **Building a complete feature**: Use Feature Module pattern (Screaming Architecture)
- **Adding configuration**: Use Configuration pattern
- **Writing utilities**: Use Utility Function pattern
- **Writing tests**: Use Testing pattern

All patterns follow:
- ✅ Type safety with TypeScript
- ✅ Separation of concerns
- ✅ Proper error handling
- ✅ Consistent naming conventions
- ✅ Clear documentation
- ✅ English-only code and comments
