'use client';

import {
  AnalysisResults,
  ProcessingProgress,
  TranscriptionResults,
  useVideoProcessing,
  VideoHeader,
  VideoHowItWorks,
  VideoUploader,
} from '@/features/video';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

/**
 * Video Container Component
 * 
 * Central hub for all video processing logic:
 * 1. Upload video to processing-engine
 * 2. Extract subtitles (transcription)
 * 3. Analyze content to find viral moments (time_from, time_to)
 * 4. Create clips for each viral moment
 * 5. Navigate to editor for subtitle overlay with Remotion
 */
export function VideoContainer() {
  const router = useRouter();
  const [processingClips, setProcessingClips] = useState(false);
  const [clipsProgress, setClipsProgress] = useState<{
    current: number;
    total: number;
    status: string;
  } | null>(null);

  const {
    file,
    currentStep,
    transcription,
    analysis,
    error,
    progress,
    uploadedPath,
    setFile,
    processVideo,
    resetState,
  } = useVideoProcessing({
    onComplete: (data) => {
      console.log('Analysis completed:', data);
      console.log('Found viral moments:', data.clips);
    },
    onError: (err) => {
      console.error('Processing error:', err);
    },
  });

  /**
   * Create a clip from a viral moment and navigate to editor
   */
  const handleClipSelect = async (clip: {
    start_time: number;
    end_time: number;
    viral_score: number;
    summary: string;
  }) => {
    if (!uploadedPath) {
      console.error('No video path available');
      return;
    }

    try {
      setProcessingClips(true);
      setClipsProgress({
        current: 1,
        total: 1,
        status: 'Creating clip...',
      });

      // Step 1: Create the vertical clip using Python /render-clip
      const clipResponse = await fetch('/api/create-clip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_path: uploadedPath,
          start_time: clip.start_time,
          end_time: clip.end_time,
          crop_mode: 'dynamic', // Use face tracking
        }),
      });

      if (!clipResponse.ok) {
        throw new Error('Failed to create clip');
      }

      const clipResult = await clipResponse.json();

      if (!clipResult.success) {
        throw new Error(clipResult.message || 'Clip creation failed');
      }

      setClipsProgress((prev) =>
        prev ? { ...prev, status: 'Getting subtitles...' } : null
      );

      // Step 2: Get subtitles for this specific clip
      const transcribeResponse = await fetch('/api/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_path: clipResult.data.output_path,
        }),
      });

      if (!transcribeResponse.ok) {
        throw new Error('Failed to transcribe clip');
      }

      const transcribeResult = await transcribeResponse.json();

      if (!transcribeResult.success) {
        throw new Error(transcribeResult.message || 'Transcription failed');
      }

      // Step 3: Navigate to editor with clip URL and subtitles
      const params = new URLSearchParams({
        videoUrl: clipResult.data.output_url,
        clipPath: clipResult.data.output_path,
        viralScore: clip.viral_score.toString(),
        summary: clip.summary,
      });

      router.push(`/editor/new?${params.toString()}`);
    } catch (err) {
      console.error('Error creating clip:', err);
      alert(err instanceof Error ? err.message : 'Failed to create clip');
    } finally {
      setProcessingClips(false);
      setClipsProgress(null);
    }
  };

  /**
   * Create ALL viral clips at once (batch processing)
   */
  const handleCreateAllClips = async () => {
    if (!analysis || !uploadedPath) return;

    try {
      setProcessingClips(true);

      const clips = analysis.clips;
      const createdClips = [];

      for (let i = 0; i < clips.length; i++) {
        const clip = clips[i];

        setClipsProgress({
          current: i + 1,
          total: clips.length,
          status: `Creating clip ${i + 1}/${clips.length}: ${clip.summary.substring(0, 50)}...`,
        });

        // Create clip
        const clipResponse = await fetch('/api/create-clip', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_path: uploadedPath,
            start_time: clip.start_time,
            end_time: clip.end_time,
            crop_mode: 'dynamic',
          }),
        });

        if (clipResponse.ok) {
          const clipResult = await clipResponse.json();
          if (clipResult.success) {
            createdClips.push({
              ...clip,
              clipUrl: clipResult.data.output_url,
              clipPath: clipResult.data.output_path,
            });
          }
        }
      }

      // Navigate to clips gallery (you can create this page)
      console.log('All clips created:', createdClips);
      alert(`Successfully created ${createdClips.length} clips!`);
    } catch (err) {
      console.error('Error creating clips:', err);
      alert('Failed to create some clips');
    } finally {
      setProcessingClips(false);
      setClipsProgress(null);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <VideoHeader />

      <VideoUploader
        file={file}
        currentStep={currentStep}
        onFileSelect={setFile}
        onProcess={processVideo}
        onReset={resetState}
        error={error}
      />

      <ProcessingProgress
        currentStep={currentStep}
        progress={progress}
        error={error}
      />

      {/* Show clip creation progress */}
      {processingClips && clipsProgress && (
        <div className="my-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-blue-900">Creating Clips</h3>
            <span className="text-sm text-blue-700">
              {clipsProgress.current} / {clipsProgress.total}
            </span>
          </div>
          <p className="text-sm text-blue-600 mb-2">{clipsProgress.status}</p>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(clipsProgress.current / clipsProgress.total) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      {transcription && currentStep !== 'idle' && (
        <TranscriptionResults transcription={transcription} />
      )}

      {analysis && currentStep === 'complete' && (
        <div className="space-y-4">
          {/* Batch action button */}
          <div className="flex justify-end">
            <button
              onClick={handleCreateAllClips}
              disabled={processingClips}
              className="px-6 py-3 bg-linear-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
            >
              {processingClips ? 'Creating Clips...' : 'Create All Clips'}
            </button>
          </div>

          <AnalysisResults
            analysis={analysis}
            onClipSelect={handleClipSelect}
          />
        </div>
      )}

      {currentStep === 'idle' && <VideoHowItWorks />}
    </div>
  );
}
