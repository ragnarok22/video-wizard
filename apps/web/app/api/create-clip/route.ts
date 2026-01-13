import { logger } from '@/server/lib/utils';
import { clipIntegrationService } from '@/server/services/clip-integration-service';
import { ClipRenderRequestSchema } from '@/server/types/clip-render';
import { NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/create-clip
 * 
 * Proxy endpoint to Python backend /render-clip
 * Creates a vertical clip from a video segment with smart cropping
 * 
 * This endpoint:
 * 1. Validates request
 * 2. Calls Python service to create clip
 * 3. Returns clip metadata with accessible URL
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = ClipRenderRequestSchema.parse(body);

    logger.info('Create clip request received', {
      start_time: validatedData.start_time,
      end_time: validatedData.end_time,
    });

    // Call Python service to create clip
    const result = await clipIntegrationService.createClip(validatedData);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          message: result.error || 'Clip creation failed',
        },
        { status: 500 }
      );
    }

    // Convert output_url to full URL if needed
    const fullUrl = result.output_url
      ? clipIntegrationService.getVideoUrl(result.output_url)
      : null;

    logger.info('Clip created successfully', {
      output_url: fullUrl,
    });

    return NextResponse.json({
      success: true,
      data: {
        ...result,
        output_url: fullUrl,
      },
    });
  } catch (error) {
    logger.error('Create clip endpoint error', error);

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
