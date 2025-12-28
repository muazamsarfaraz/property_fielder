/**
 * UX Mockup Generator using Gemini Image Generation
 * Generates mockups for improved empty states and UI elements
 */

import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables from root .env
dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const OUTPUT_DIR = path.resolve(__dirname, '../test-results/ux-improvements/mockups');

interface MockupRequest {
  name: string;
  prompt: string;
  referenceImage?: string;
}

const mockupRequests: MockupRequest[] = [
  {
    name: 'empty-state-properties',
    prompt: `Create a clean, modern empty state illustration for a Property Management application.
The illustration should show:
- A simple house/building icon with a plus sign
- Soft, muted colors (blues and grays)
- Minimalist flat design style
- Text placeholder area below for "No properties yet"
- A call-to-action button placeholder "Add Your First Property"
Style: Modern SaaS application, professional, friendly`
  },
  {
    name: 'empty-state-jobs',
    prompt: `Create a clean, modern empty state illustration for a Field Service job scheduling application.
The illustration should show:
- A clipboard with a checkmark or calendar icon
- An inspector/worker silhouette
- Soft, professional colors (teals and grays)
- Minimalist flat design style
- Space for text "No jobs scheduled"
- A call-to-action button "Schedule First Job"
Style: Modern SaaS application, professional, friendly`
  },
  {
    name: 'empty-state-inspections',
    prompt: `Create a clean, modern empty state illustration for a Property Inspection application.
The illustration should show:
- A magnifying glass over a house
- A checklist or certificate icon
- Professional colors (greens and grays for compliance theme)
- Minimalist flat design style
- Space for "No inspections due"
- Call-to-action "Create Inspection"
Style: Modern SaaS application, professional, friendly`
  }
];

async function generateMockup(request: MockupRequest): Promise<string | null> {
  console.log(`\n🎨 Generating mockup: ${request.name}`);
  
  const requestBody = {
    contents: [{
      parts: [{ text: request.prompt }]
    }],
    generationConfig: {
      responseModalities: ['TEXT', 'IMAGE']
    }
  };

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ API Error: ${response.status} - ${errorText}`);
      return null;
    }

    const data = await response.json();
    
    // Extract image from response
    if (data.candidates?.[0]?.content?.parts) {
      for (const part of data.candidates[0].content.parts) {
        if (part.inlineData?.mimeType?.startsWith('image/')) {
          const imageData = part.inlineData.data;
          const ext = part.inlineData.mimeType.split('/')[1] || 'png';
          const filePath = path.join(OUTPUT_DIR, `${request.name}.${ext}`);
          
          fs.writeFileSync(filePath, Buffer.from(imageData, 'base64'));
          console.log(`✅ Saved: ${filePath}`);
          return filePath;
        }
      }
    }
    
    console.log('⚠️ No image in response');
    return null;
  } catch (error: any) {
    console.error(`❌ Error: ${error.message}`);
    return null;
  }
}

async function main() {
  console.log('🎨 UX Mockup Generator');
  console.log('='.repeat(50));
  
  // Create output directory
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const results: { name: string; path: string | null }[] = [];
  
  for (const request of mockupRequests) {
    const imagePath = await generateMockup(request);
    results.push({ name: request.name, path: imagePath });
  }

  console.log('\n' + '='.repeat(50));
  console.log('📊 Results:');
  results.forEach(r => {
    console.log(`  ${r.path ? '✅' : '❌'} ${r.name}: ${r.path || 'Failed'}`);
  });
}

main().catch(console.error);

