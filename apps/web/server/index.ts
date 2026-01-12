/**
 * Server Module - Content Analysis
 * 
 * Central module to export services, types, and configurations
 * related to video content analysis.
 */

// Services
export { ContentAnalysisService, contentAnalysisService } from './services/content-analysis-service';

// Types
export type {
    AnalyzeContentErrorResponse, AnalyzeContentRequest,
    AnalyzeContentResponse, ContentAnalysis, ViralClip
} from './types/content-analysis';

export {
    ContentAnalysisSchema, ViralClipSchema
} from './types/content-analysis';

// Config
export { AI_MODELS, getOpenAIConfig, validateAIConfig } from './config/ai';

// Prompts
export {
    VIRAL_EDITOR_SYSTEM_PROMPT,
    buildAnalysisPrompt
} from './prompts/viral-editor';

// Lib (utilities)
export {
    ConfigurationError,
    ServiceError, ValidationError, getEnv, logger, requireEnv, safeAsync, validateString
} from './lib/utils';

