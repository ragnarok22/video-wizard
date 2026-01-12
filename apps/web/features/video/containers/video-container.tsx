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

/**
 * Video Container Component
 * 
 * Client-side container that manages video processing workflow state
 * and orchestrates presentational components
 */
export function VideoContainer() {
  const {
    file,
    currentStep,
    transcription,
    analysis,
    error,
    progress,
    setFile,
    processVideo,
    resetState,
  } = useVideoProcessing({
    onComplete: (data) => {
      console.log('Processing completed:', data);
    },
    onError: (err) => {
      console.error('Processing error:', err);
    },
  });

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

      {transcription && currentStep !== 'idle' && (
        <TranscriptionResults transcription={transcription} />
      )}

      {analysis && currentStep === 'complete' && (
        <AnalysisResults
          analysis={analysis}
          onClipSelect={(clip) => {
            console.log('Navigate to clip:', clip);
            // Could implement video player navigation here
          }}
        />
      )}

      {currentStep === 'idle' && <VideoHowItWorks />}
    </div>
  );
}
