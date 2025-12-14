# Enhanced TTS Webhook Service Documentation

## Overview

The Enhanced TTS Webhook Service is a production-ready text-to-speech API that converts agent utterances into high-quality audio files. It features multiple TTS engines, intelligent caching, fallback mechanisms, and avatar binding capabilities.

**Deployed Service URL:** https://g8h3ilcq5zq8.manus.space

**Version:** 2.0.0

## Key Features

### 1. Multiple TTS Engines
- **gTTS (Google Text-to-Speech)**: Free, open-source, supports multiple languages
- **OpenAI TTS**: High-quality voices with natural intonation (requires API key)
- **System TTS**: Fallback engine using espeak for maximum reliability

### 2. Intelligent Caching
- Automatic caching of generated audio files
- Cache key based on text content and generation parameters
- Reduces processing time and API costs for repeated utterances

### 3. Fallback Mechanisms
- Automatic fallback to system TTS if primary engine fails
- Graceful degradation ensures service availability

### 4. Avatar Binding Support
- Integration hooks for HeyGen avatar binding
- Webhook callbacks for completion notifications
- Support for visual avatar generation

### 5. Production Features
- CORS enabled for cross-origin requests
- Comprehensive error handling and logging
- Health check and monitoring endpoints
- Audio file serving with proper MIME types

## API Endpoints

### Health Check
**GET /**

Returns service status and available engines.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "engines_available": {
    "gtts": true,
    "openai": false,
    "system": true
  },
  "uptime": "0:15:32.123456",
  "total_requests": 42,
  "cache_size": 15
}
```

### Generate TTS Audio
**POST /webhook**

Generates audio from text utterance.

**Request Body:**
```json
{
  "agent": "herald",
  "utterance": "Welcome to the enhanced TTS service!",
  "importance": 5.0,
  "timestamp": "2025-12-10T12:00:00",
  "engine": "gtts",
  "voice_type": "neutral",
  "language": "en",
  "speed": 1.0,
  "avatar_id": "optional_avatar_id",
  "callback_url": "https://your-service.com/callback"
}
```

**Parameters:**
- `agent` (required): Agent identifier (e.g., "lyra", "archimedes", "herald")
- `utterance` (required): Text to convert to speech (max 5000 characters)
- `importance` (optional): Importance level 0.0-10.0 (default: 1.0)
- `timestamp` (optional): ISO format timestamp (default: current time)
- `engine` (optional): TTS engine - "gtts", "openai", or "system" (default: "gtts")
- `voice_type` (optional): Voice type - "male", "female", or "neutral" (default: "neutral")
- `language` (optional): Language code (default: "en")
- `speed` (optional): Speech speed 0.5-2.0 (default: 1.0)
- `avatar_id` (optional): Avatar ID for binding
- `callback_url` (optional): URL for completion callback

**Response:**
```json
{
  "status": "success",
  "message": "Utterance processed successfully",
  "audio_file": "audio_files/herald_2025-12-10T12-00-00.mp3",
  "audio_url": "/audio/herald_2025-12-10T12-00-00.mp3",
  "agent": "herald",
  "engine_used": "gtts",
  "processing_time": 0.523,
  "file_size": 61824,
  "cache_hit": false
}
```

### Serve Audio File
**GET /audio/{filename}**

Serves generated audio files.

**Example:**
```
GET /audio/herald_2025-12-10T12-00-00.mp3
```

Returns the audio file with `audio/mpeg` MIME type.

### List Available Engines
**GET /engines**

Lists all TTS engines and their availability status.

**Response:**
```json
{
  "gtts": {
    "name": "gtts",
    "available": true,
    "description": "Gtts Text-to-Speech Engine"
  },
  "openai": {
    "name": "openai",
    "available": false,
    "description": "Openai Text-to-Speech Engine"
  },
  "system": {
    "name": "system",
    "available": true,
    "description": "System Text-to-Speech Engine"
  }
}
```

### Clear Cache
**DELETE /cache**

Clears the TTS cache.

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared"
}
```

## Usage Examples

### Python Example
```python
import requests

url = "https://g8h3ilcq5zq8.manus.space/webhook"

payload = {
    "agent": "lyra",
    "utterance": "Hello! This is Lyra speaking with enhanced TTS!",
    "importance": 7.0,
    "engine": "gtts",
    "voice_type": "female",
    "speed": 1.1
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Status: {result['status']}")
print(f"Audio URL: {result['audio_url']}")
print(f"Processing time: {result['processing_time']}s")

# Download the audio file
audio_url = f"https://g8h3ilcq5zq8.manus.space{result['audio_url']}"
audio_response = requests.get(audio_url)

with open("lyra_speech.mp3", "wb") as f:
    f.write(audio_response.content)
```

### cURL Example
```bash
# Generate TTS audio
curl -X POST https://g8h3ilcq5zq8.manus.space/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "archimedes",
    "utterance": "Greetings. I am Archimedes, the cyborg owl.",
    "engine": "gtts",
    "voice_type": "male",
    "speed": 0.9
  }'

# Download the audio file
curl -O https://g8h3ilcq5zq8.manus.space/audio/archimedes_2025-12-10T12-00-00.mp3
```

### JavaScript Example
```javascript
async function generateTTS(agent, text) {
  const response = await fetch('https://g8h3ilcq5zq8.manus.space/webhook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent: agent,
      utterance: text,
      engine: 'gtts',
      voice_type: 'neutral',
      speed: 1.0
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    // Play the audio
    const audio = new Audio(`https://g8h3ilcq5zq8.manus.space${result.audio_url}`);
    audio.play();
  }
  
  return result;
}

// Usage
generateTTS('herald', 'The council chamber awaits your presence.');
```

## TTS Engine Comparison

| Feature | gTTS | OpenAI TTS | System TTS |
|---------|------|------------|------------|
| **Cost** | Free | Paid | Free |
| **Quality** | Good | Excellent | Basic |
| **Languages** | 100+ | Limited | Varies |
| **Voice Options** | Limited | Multiple | Basic |
| **Speed Control** | Basic | Advanced | Basic |
| **Availability** | Always | API Key Required | Always |
| **Best For** | General use | High quality | Fallback |

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for TTS engine (optional)
- `HEYGEN_API_KEY`: HeyGen API key for avatar binding (optional)

### Audio Storage

Audio files are stored in the `audio_files` directory with automatic cleanup after 24 hours.

### Cache Management

The service maintains an in-memory cache of generated audio files. Cache keys are based on:
- Text content
- TTS engine
- Voice type
- Language
- Speed

## Integration with HeyGen Avatars

The service includes integration hooks for HeyGen avatar binding. To use this feature:

1. Set the `HEYGEN_API_KEY` environment variable
2. Include `avatar_id` in your webhook request
3. The service will automatically dispatch to HeyGen for avatar video generation

**Example with Avatar:**
```json
{
  "agent": "herald",
  "utterance": "Welcome to the council chamber.",
  "avatar_id": "your_heygen_avatar_id",
  "voice_type": "male"
}
```

## Error Handling

The service includes comprehensive error handling:

- **400 Bad Request**: Invalid input (empty utterance, invalid parameters)
- **404 Not Found**: Audio file not found
- **500 Internal Server Error**: TTS generation failed (with automatic fallback)
- **503 Service Unavailable**: TTS engine not available

All errors return JSON responses with detailed error messages.

## Performance Optimization

### Caching Strategy
- First request: Generates audio and caches result
- Subsequent identical requests: Serves from cache instantly
- Cache hit reduces processing time from ~0.5s to <0.01s

### Fallback Chain
1. Primary engine (user-selected)
2. System TTS engine
3. Silent audio file (last resort)

## Monitoring and Analytics

The service tracks:
- Total requests processed
- Cache hit rate
- Engine availability
- Processing times
- Error rates

Access metrics via the health check endpoint.

## Best Practices

1. **Use Caching**: Identical utterances are cached automatically
2. **Choose Appropriate Engine**: Use gTTS for general purposes, OpenAI for high quality
3. **Set Reasonable Speed**: Keep speed between 0.8-1.2 for natural speech
4. **Handle Errors**: Always check the response status and handle errors gracefully
5. **Cleanup**: Audio files are automatically cleaned up after 24 hours
6. **Rate Limiting**: Implement client-side rate limiting for high-volume usage

## Troubleshooting

### Issue: OpenAI TTS not available
**Solution**: Set the `OPENAI_API_KEY` environment variable with a valid API key.

### Issue: Audio file not found
**Solution**: Audio files are cleaned up after 24 hours. Re-generate if needed.

### Issue: Slow processing
**Solution**: Use caching for repeated utterances. Check if the service is under heavy load.

### Issue: Poor audio quality
**Solution**: Try using the OpenAI TTS engine for better quality, or adjust the speed parameter.

## Support and Contact

For issues, questions, or feature requests related to the TTS service, please refer to the project documentation or contact the development team.

## License

This service uses open-source components (gTTS, Flask) and is designed for integration with AI agent systems.

---

**Service Status**: ✅ Live and operational
**Deployment URL**: https://g8h3ilcq5zq8.manus.space
**Version**: 2.0.0
**Last Updated**: December 2025
