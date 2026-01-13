import { REMOTION_CONFIG } from '@/remotion/config';
import { logger } from '@/server/lib/utils';
import type {
    RenderRequest,
    RenderResponse,
    SubtitleSegment
} from '@/server/types/video-render';
import { randomUUID } from 'crypto';
import { join } from 'path';

/**
 * Video Rendering Service (Phase T)
 * 
 * Server-side video rendering using Remotion
 * Creates final MP4 with synchronized subtitles
 * 
 * NOTE: We use serveUrl instead of bundle() to avoid bundling at runtime
 * For production, pre-build the Remotion bundle and serve it statically
 */
export class VideoRenderService {
  private readonly outputDir: string;
  private readonly serveUrl: string;

  constructor() {
    // Use output directory or temp directory
    this.outputDir = join(process.cwd(), 'public', 'rendered');
    
    // For local development: use the Next.js dev server
    // For production: pre-bundle and deploy to static hosting
    this.serveUrl = process.env.REMOTION_SERVE_URL || 'http://localhost:3000/remotion';
  }

  /**
   * Render video with subtitles
   * 
   * NOTE: Server-side rendering disabled to avoid bundling issues
   * Use Python FFmpeg backend for exports instead
   * 
   * See: /docs/VIDEO_EXPORT_STRATEGY.md
   */
  async renderVideo(request: RenderRequest): Promise<RenderResponse> {
    logger.info('Render request received', { template: request.template });

    // Server-side rendering not implemented
    return {
      success: false,
      error: 'Server-side rendering not configured. Use Python FFmpeg backend for exports.',
    };
  }

  /**
   * Legacy method - kept for reference
   * Server-side rendering removed to avoid @remotion/bundler conflicts
   */
  private async _renderVideoLegacy(request: RenderRequest): Promise<RenderResponse> {
    try {
      logger.info('Starting video render', { template: request.template });

      // Generate unique output filename
      const outputId = randomUUID();
      const outputFileName = `video_${outputId}.${request.outputFormat}`;
      const outputPath = join(this.outputDir, outputFileName);

      // Calculate duration from subtitles
      const durationInFrames = this.calculateDuration(request.subtitles);

      // This would require @remotion/renderer which causes bundling issues
      throw new Error('Remotion server-side rendering not available');

      // Get file stats
      const stats = await this.getFileStats(outputPath);

      logger.info('Video render complete', {
        outputPath,
        fileSize: stats.size,
      });

      return {
        success: true,
        outputUrl: `/rendered/${outputFileName}`,
        outputPath,
        fileSize: stats.size,
        duration: durationInFrames / REMOTION_CONFIG.DEFAULT_FPS,
      };
    } catch (error) {
      logger.error('Video render failed', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Render failed',
      };
    }
  }

  /**
   * Calculate duration in frames from subtitles
   */
  private calculateDuration(subtitles: SubtitleSegment[]): number {
    if (subtitles.length === 0) return 300; // Default 10 seconds

    const lastSegment = subtitles[subtitles.length - 1];
    return Math.ceil(lastSegment.end * REMOTION_CONFIG.DEFAULT_FPS);
  }

  /**
   * Get file statistics
   */
  private async getFileStats(filePath: string): Promise<{ size: number }> {
    try {
      const fs = await import('fs/promises');
      const stats = await fs.stat(filePath);
      return { size: stats.size };
    } catch {
      return { size: 0 };
    }
  }
}

// Singleton instance
export const videoRenderService = new VideoRenderService();
