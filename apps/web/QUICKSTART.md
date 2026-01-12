# Content Intelligence Module - Quick Start Guide

Get the AI-powered viral clip detector running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- pnpm installed (`npm install -g pnpm`)

## Step 1: Configure API Key (30 seconds)

Create `.env.local` in the `apps/web` directory:

```bash
cd apps/web
echo "OPENAI_API_KEY=your_api_key_here" > .env.local
```

Replace `your_api_key_here` with your actual OpenAI API key.

## Step 2: Install Dependencies (if not already installed)

Dependencies are already installed! If you need to reinstall:

```bash
cd apps/web
pnpm install
```

## Step 3: Start the Server (10 seconds)

```bash
cd apps/web
pnpm dev
```

## Step 4: Access the Demo (now!)

Open your browser and navigate to:
```
http://localhost:3000/content-intelligence
```

## Step 5: Try It Out! (2 minutes)

1. Click **"Load Sample"** to load a sample transcript
2. Click **"Analyze Content"** 
3. Wait 3-5 seconds for AI analysis
4. View the viral clips with scores!

## What You'll See

### Input Section
- Textarea with a sample YouTube video transcript
- Analyze button to trigger AI analysis

### Results Section
- List of identified viral clips
- Each clip shows:
  - ⏱️ Timestamps (start - end)
  - 📊 Viral score (0-100)
  - 📝 Summary of why it's engaging
  - 🎣 Hook (attention grabber)
  - ✅ Conclusion (how it ends)

### Color-Coded Scores
- 🟢 Green (90-100): Extremely Viral
- 🔵 Blue (70-89): High Potential  
- 🟡 Yellow (50-69): Good Potential
- 🟠 Orange (30-49): Moderate
- 🔴 Red (0-29): Low Potential

## API Usage (For Developers)

### Basic Example
```typescript
const response = await fetch('/api/analyze-content', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    transcript: '[00:00 - 00:30] Your transcript here...' 
  }),
});

const data = await response.json();
console.log(data.data.clips); // Array of viral clips
```

### Using the React Hook
```typescript
import { useContentAnalysis } from '@/lib/hooks/useContentAnalysis';

function MyComponent() {
  const { analyzeContent, isAnalyzing, analysis } = useContentAnalysis();

  const handleClick = async () => {
    await analyzeContent(transcript);
  };

  return (
    <button onClick={handleClick} disabled={isAnalyzing}>
      {isAnalyzing ? 'Analyzing...' : 'Analyze'}
    </button>
  );
}
```

## Sample Transcript Format

For best results, format transcripts with timestamps:

```
[00:00 - 00:15] Opening statement with a hook
[00:15 - 00:45] Main content with value
[00:45 - 01:20] Detailed explanation
[01:20 - 01:45] Conclusion with call to action
```

## Troubleshooting

### "OpenAI API key not configured"
- Check that `.env.local` exists in `apps/web/`
- Verify the API key starts with `sk-`
- Restart the dev server after adding the key

### Analysis takes too long
- Normal: 3-8 seconds
- Long transcript? May take up to 15 seconds
- Check your internet connection

### No clips found
- Ensure transcript has enough content (100+ words)
- Include timestamps for better results
- Try the sample transcript first

### API Error
- Check OpenAI API status: https://status.openai.com
- Verify you have API credits available
- Check console for detailed error messages

## Next Steps

### Integration with Python Engine
See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for connecting with the transcription service.

### Customization
Edit [app/api/analyze-content/route.ts](app/api/analyze-content/route.ts) to:
- Modify viral criteria
- Adjust clip length requirements
- Change scoring thresholds
- Switch GPT models

### Full Documentation
See [CONTENT_INTELLIGENCE.md](CONTENT_INTELLIGENCE.md) for complete API reference and advanced features.

## Cost Estimation

Typical costs per analysis with GPT-4o:
- Short video (5 min): ~$0.01-0.02
- Medium video (15 min): ~$0.03-0.05
- Long video (30 min): ~$0.05-0.10

💡 **Tip**: Use `gpt-4o-mini` during development for 60% cost reduction!

```typescript
// In route.ts
model: openai('gpt-4o-mini')  // Instead of 'gpt-4o'
```

## Features at a Glance

✅ AI-powered content analysis with GPT-4o  
✅ Strict JSON validation with Zod  
✅ Type-safe TypeScript throughout  
✅ Beautiful UI with color-coded scores  
✅ React hook for easy integration  
✅ Comprehensive documentation  
✅ Sample transcript included  
✅ Error handling built-in  
✅ Ready for production  

## Questions?

1. **How accurate is the AI?** - Very accurate! GPT-4o has been trained on vast amounts of viral content and understands engagement patterns.

2. **Can I customize the criteria?** - Yes! Edit the `VIRAL_EDITOR_PROMPT` in the API route.

3. **Does it work with other languages?** - Yes! OpenAI models support 50+ languages.

4. **Can I use a different AI model?** - Yes! Just change the model parameter in the API route.

5. **Is it production-ready?** - Yes! Add rate limiting and caching for production use.

## Support

- 📖 [Full Documentation](CONTENT_INTELLIGENCE.md)
- 🔗 [Integration Guide](INTEGRATION_GUIDE.md)
- 📊 [Implementation Status](IMPLEMENTATION_STATUS.md)
- 🧪 [Test Suite](lib/__tests__/content-intelligence.test.ts)

---

**You're all set! 🎉**

Start analyzing transcripts and finding viral clips in seconds!
