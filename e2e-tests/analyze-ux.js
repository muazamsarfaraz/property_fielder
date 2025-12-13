/**
 * Analyze dispatch view screenshots using Gemini 3 Pro Preview
 */

const fs = require('fs');
const path = require('path');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const MODEL = 'gemini-3-pro-preview';

async function analyzeScreenshots() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY environment variable is required');
    process.exit(1);
  }

  const screenshots = [
    'test-results/dispatch-view.png',
    'test-results/dispatch-dropdown-open.png',
    'test-results/dispatch-after-load.png',
    'test-results/dispatch-jobs-loaded.png'
  ];

  // Read and encode images as base64
  const imageParts = [];
  for (const screenshot of screenshots) {
    const filePath = path.join(__dirname, screenshot);
    if (fs.existsSync(filePath)) {
      const imageData = fs.readFileSync(filePath);
      const base64 = imageData.toString('base64');
      imageParts.push({
        inline_data: {
          mime_type: 'image/png',
          data: base64
        }
      });
      console.log(`Loaded: ${screenshot}`);
    } else {
      console.warn(`Warning: ${screenshot} not found`);
    }
  }

  if (imageParts.length === 0) {
    console.error('No screenshots found to analyze');
    process.exit(1);
  }

  const prompt = `You are a UX/UI expert. Analyze these screenshots of a Field Service Dispatch view in an Odoo-based property management application.

The screenshots show:
1. The dispatch view with a map, jobs panel, inspectors panel, and routes panel
2. A "Test Data" dropdown menu that was added for loading/deleting test data
3. The view after loading test data (jobs appearing on the map)

Please provide:
1. **Overall UX Assessment**: Rate the current UI design (1-10) and explain why
2. **Specific Issues**: List any UX problems you see (layout, colors, readability, navigation)
3. **Test Data Button Feedback**: Is the "Test Data" dropdown well-placed? Is it intuitive? Should it be styled differently?
4. **Map Integration**: How well is the map integrated with the job list?
5. **Recommendations**: Provide 5-10 specific, actionable improvements

Focus on practical improvements that would enhance the user experience for field service dispatchers.`;

  const requestBody = {
    contents: [{
      parts: [
        { text: prompt },
        ...imageParts
      ]
    }]
  };

  console.log('\nSending to Gemini 3 Pro Preview for analysis...\n');

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error: ${response.status} - ${errorText}`);
      process.exit(1);
    }

    const data = await response.json();
    
    if (data.candidates && data.candidates[0]?.content?.parts) {
      const text = data.candidates[0].content.parts
        .filter(p => p.text)
        .map(p => p.text)
        .join('\n');
      
      console.log('='.repeat(80));
      console.log('GEMINI UX ANALYSIS');
      console.log('='.repeat(80));
      console.log(text);
      console.log('='.repeat(80));
    } else {
      console.log('Unexpected response format:', JSON.stringify(data, null, 2));
    }
  } catch (error) {
    console.error('Error calling Gemini API:', error.message);
    process.exit(1);
  }
}

analyzeScreenshots();

