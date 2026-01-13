import { logger } from '@/server/lib/utils';
import { clipIntegrationService } from '@/server/services/clip-integration-service';
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const TranscribeRequestSchema = z.object({
  video_path: z.string(),
  language: z.string().optional(),
});

/**
 * POST /api/transcribe
 * 
 * Proxy endpoint to Python backend /transcribe
 * Extracts audio and generates timestamped transcription
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { video_path, language } = TranscribeRequestSchema.parse(body);

    logger.info('Transcribe request received', { video_path });

    // Call Python service to transcribe
    const result = await clipIntegrationService.transcribeVideo(
      video_path,
      language
    );

    logger.info('Transcription completed', {
      segment_count: result.segment_count,
    });

    return NextResponse.json({
      success: true,
      data: result,
    });
  } catch (error) {
    logger.error('Transcribe endpoint error', error);

    if (error instanceof Error && error.name === 'ZodError') {
      return NextResponse.json(
        {
          success: false,
          message: 'Invalid request data',
          errors: error,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        message: error instanceof Error ? error.message : 'Internal server error',
      },
      { status: 500 }
    );
  }
}
