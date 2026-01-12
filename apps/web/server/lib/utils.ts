/**
 * Server utilities for validation and error handling
 */

/**
 * Custom errors for the server
 */

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

export class ServiceError extends Error {
  constructor(message: string, public originalError?: unknown) {
    super(message);
    this.name = 'ServiceError';
  }
}

/**
 * Helper to validate required environment variables
 */
export function requireEnv(key: string): string {
  const value = process.env[key];
  
  if (!value) {
    throw new ConfigurationError(
      `Environment variable ${key} is required but not set`
    );
  }
  
  return value;
}

/**
 * Helper to get an environment variable with a default value
 */
export function getEnv(key: string, defaultValue: string): string {
  return process.env[key] ?? defaultValue;
}

/**
 * Validates that a string is not empty and meets minimum length requirements
 */
export function validateString(
  value: string,
  fieldName: string,
  options?: {
    minLength?: number;
    maxLength?: number;
  }
): void {
  if (!value || value.trim().length === 0) {
    throw new ValidationError(`${fieldName} cannot be empty`);
  }

  if (options?.minLength && value.trim().length < options.minLength) {
    throw new ValidationError(
      `${fieldName} must be at least ${options.minLength} characters long`
    );
  }

  if (options?.maxLength && value.trim().length > options.maxLength) {
    throw new ValidationError(
      `${fieldName} must be at most ${options.maxLength} characters long`
    );
  }
}

/**
 * Safe wrapper for async operations with improved error handling
 */
export async function safeAsync<T>(
  operation: () => Promise<T>,
  errorMessage: string
): Promise<T> {
  try {
    return await operation();
  } catch (error) {
    console.error(`${errorMessage}:`, error);
    throw new ServiceError(
      errorMessage,
      error
    );
  }
}

/**
 * Structured logs for the server
 */
export const logger = {
  info: (message: string, meta?: Record<string, unknown>) => {
    console.log(JSON.stringify({ level: 'info', message, ...meta, timestamp: new Date().toISOString() }));
  },
  warn: (message: string, meta?: Record<string, unknown>) => {
    console.warn(JSON.stringify({ level: 'warn', message, ...meta, timestamp: new Date().toISOString() }));
  },
  error: (message: string, error?: unknown, meta?: Record<string, unknown>) => {
    console.error(JSON.stringify({
      level: 'error',
      message,
      error: error instanceof Error ? { name: error.name, message: error.message, stack: error.stack } : error,
      ...meta,
      timestamp: new Date().toISOString()
    }));
  },
};
