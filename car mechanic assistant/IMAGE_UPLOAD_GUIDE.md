> Historical prototype snapshot. The October 2026 rebuild changes behaviour and commands; see [BUILD_STATUS.md](BUILD_STATUS.md) and [QUICKSTART.md](QUICKSTART.md) for the current verified state.

# Image Upload Feature - User Guide

## Overview

The Car Mechanic Assistant now supports **multimodal queries** - you can upload images along with your questions to get AI-powered visual analysis combined with knowledge base expertise.

## How It Works

1. **Upload an Image** - Click the upload area or drag & drop
2. **Add Your Question** - Ask about the image (or leave blank for general analysis)
3. **Get AI Analysis** - Gemini Vision analyzes the image + retrieves relevant knowledge base documents

## Example Use Cases

### 🔧 **Part Identification**
- **Upload**: Photo of engine component
- **Ask**: "What part is this? Should I replace it?"
- **Result**: Part identification, function, replacement guidance

### 💥 **Damage Assessment**
- **Upload**: Photo of dented bumper
- **Ask**: "How much to repair this?"
- **Result**: Damage assessment, repair options, cost estimates

### 🎨 **Paint Matching**
- **Upload**: Photo of car panel
- **Ask**: "What paint code is this?"
- **Result**: Color analysis, paint code suggestions, matching tips

### 📋 **VIN/Part Number Reading**
- **Upload**: Photo of VIN plate or part label
- **Ask**: "What's the VIN number?"
- **Result**: OCR extraction of VIN/part numbers

### 🔍 **Diagnosis Support**
- **Upload**: Photo of check engine light screen
- **Ask**: "What does this code mean?"
- **Result**: Code interpretation + diagnostic guidance

### ⚙️ **Installation Verification**
- **Upload**: Photo of installed part
- **Ask**: "Is this installed correctly?"
- **Result**: Visual inspection, installation check, corrections

## Supported Image Types

- **Format**: JPG, PNG, HEIC, WebP
- **Size**: Up to 10MB recommended
- **Quality**: Higher resolution = better analysis

## Tips for Best Results

### ✅ **Good Photos**
- Well-lit, clear focus
- Close enough to see details
- Multiple angles if needed
- Include context (surrounding parts)

### ❌ **Avoid**
- Blurry or dark photos
- Too far away (can't see details)
- Obstructed views
- Extreme angles

## Example Queries

### Part Identification
```
Image: Close-up of cylindrical component
Query: "Is this the HPFP? Should I replace it?"
```

### Damage Assessment
```
Image: Dented rear bumper
Query: "How much will this cost to fix? Can I drive with it?"
```

### Paint Code
```
Image: Car door panel
Query: "I need to match this paint. What color/code is this?"
```

### Leak Diagnosis
```
Image: Wet spot under engine
Query: "What's leaking? How urgent is this?"
```

### Wear Assessment
```
Image: Brake pad close-up
Query: "Do I need to replace these brake pads?"
```

## How It Combines Image + Knowledge Base

1. **Image Analysis**: Gemini Vision processes the image
   - Identifies parts, damage, colors, text
   - Assesses condition and severity

2. **Knowledge Base Retrieval**: RAG system finds relevant docs
   - Based on your query text
   - Pulls repair procedures, pricing, specs

3. **Combined Response**: Best of both worlds
   - Visual observations from the image
   - Expert knowledge from the database
   - Practical recommendations

## Privacy & Data

- Images are sent to Google Gemini API for processing
- Not stored permanently on server
- Processed in memory only
- See Google Gemini privacy policy

## Technical Details

- **Model**: Uses your configured Gemini model (gemini-3-pro-preview)
- **API**: Google Gemini Multimodal API
- **Processing**: Server-side (Flask backend)
- **Response Time**: 3-8 seconds depending on image size

## Troubleshooting

### "Image too large" error
- Resize image to < 10MB
- Use JPG instead of PNG for smaller size

### "Cannot process image" error
- Check file format (JPG, PNG, HEIC, WebP)
- Ensure image isn't corrupted
- Try a different image

### Slow response
- Large images take longer to process
- Resize to 1920x1080 or smaller
- Check internet connection

### Inaccurate analysis
- Ensure good lighting and focus
- Take photo from better angle
- Add more specific query text
- Try multiple photos from different angles

## Examples Gallery

### Before/After Comparison
You can upload multiple images in sequence to compare:
```
1st Query: "What's wrong with this engine bay?" (before photo)
2nd Query: "Did I fix it correctly?" (after photo)
```

### Progressive Diagnosis
```
Upload 1: "What's this part called?"
Upload 2: "How do I remove it?"
Upload 3: "Is this the correct replacement?"
```

## Limitations

- Cannot identify very rare/custom parts
- Paint color matching is approximate (lighting affects it)
- Cannot see internal damage (only visible)
- Text (VIN/codes) must be readable in photo
- Multiple small parts in one photo may be hard to isolate

## Best Practices

1. **Be Specific**: Ask targeted questions
2. **Quality Photos**: Good lighting, sharp focus
3. **Context**: Include surrounding components
4. **Zoom**: Get close for part details
5. **Multiple Angles**: Take several photos if complex
6. **Combine Info**: Add vehicle make/model/year to query

---

**Need Help?** Start with these example queries:
- "What part is this?"
- "Is this damage serious?"
- "What paint code?"
- "How do I fix this?"
