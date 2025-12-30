/**
 * Analyze production screenshots using Gemini 2.5 Pro Preview
 */

const fs = require('fs');
const path = require('path');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const MODEL = 'gemini-2.0-flash';

async function analyzeProductionScreenshots() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY environment variable is required');
    process.exit(1);
  }

  const screenshots = [
    'test-results/production-ux-dispatch-view.png',
    'test-results/production-ux-property-list.png',
    'test-results/production-ux-property-detail.png'
  ];

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
      console.log('Loaded: ' + screenshot);
    } else {
      console.warn('Warning: ' + screenshot + ' not found');
    }
  }

  if (imageParts.length === 0) {
    console.error('No screenshots found to analyze');
    process.exit(1);
  }

  const prompt = `You are a UX/UI expert. Analyze these screenshots of a Property Management application built on Odoo 19 for UK property managers and landlords.

The screenshots show:
1. Dispatch View - A field service dispatch interface with jobs list, map, and status filters
2. Property List - A kanban view of properties with compliance status badges
3. Property Detail - A property form showing details, FLAGE+ compliance status, and certifications

Please provide a comprehensive UX analysis:

1. **Overall UX Score** (1-10): Rate the overall user experience and explain why

2. **Dispatch View Analysis**:
   - Job card design and information density
   - Map integration and usability
   - Filter pills and workflow steps
   - Any issues with visual hierarchy

3. **Property List Analysis**:
   - Card design and scanability
   - Compliance status visibility
   - Navigation and filtering options

4. **Property Detail Form Analysis**:
   - Form layout and organization
   - FLAGE+ compliance section visibility
   - Tab organization
   - Data entry experience

5. **Top 10 Specific Recommendations**: 
   Provide actionable improvements ranked by impact

6. **Quick Wins** (changes that can be made easily):
   List 3-5 small changes that would immediately improve UX

Focus on practical improvements for property managers who need to quickly assess compliance status and schedule inspections.`;

  const requestBody = {
    contents: [{
      parts: [
        { text: prompt },
        ...imageParts
      ]
    }],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 4096
    }
  };

  console.log('\nSending to Gemini for production UX analysis...\n');

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
      console.log('PRODUCTION UX ANALYSIS - Railway Deployment');
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

analyzeProductionScreenshots();

