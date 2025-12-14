"""
Enhanced TTS Webhook Service - Flask Version
Compatible with deployment system
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import datetime
import os
import logging
import hashlib
import json
from pathlib import Path
from enum import Enum

# TTS Engine imports
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
AUDIO_DIR = Path("audio_files")
CACHE_DIR = Path("cache")
AUDIO_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Global state
app_state = {
    "start_time": datetime.datetime.now(),
    "request_count": 0,
    "cache": {}
}

# TTS Engine Classes
class GTTSEngine:
    def __init__(self):
        self.name = "gtts"
    
    def generate_audio(self, text, options):
        if not GTTS_AVAILABLE:
            raise Exception("gTTS engine not available")
        
        try:
            lang = options.get('language', 'en')
            slow = options.get('speed', 1.0) < 0.8
            
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            filename = f"{options['agent']}_{options['timestamp'].isoformat().replace(':', '-')}.mp3"
            filepath = AUDIO_DIR / filename
            
            tts.save(str(filepath))
            
            logger.info(f"Generated audio with gTTS: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            raise Exception(f"gTTS generation failed: {str(e)}")

class OpenAITTSEngine:
    def __init__(self):
        self.name = "openai"
        self.client = None
        if OPENAI_AVAILABLE:
            try:
                self.client = openai.OpenAI()
            except Exception as e:
                logger.warning(f"OpenAI TTS client initialization failed: {e}")
    
    def generate_audio(self, text, options):
        if not self.client:
            raise Exception("OpenAI TTS engine not available")
        
        try:
            voice_map = {
                "male": "onyx",
                "female": "nova",
                "neutral": "alloy"
            }
            
            voice = voice_map.get(options.get('voice_type', 'neutral'), "alloy")
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3",
                speed=options.get('speed', 1.0)
            )
            
            filename = f"{options['agent']}_{options['timestamp'].isoformat().replace(':', '-')}.mp3"
            filepath = AUDIO_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Generated audio with OpenAI TTS: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"OpenAI TTS generation failed: {e}")
            raise Exception(f"OpenAI TTS generation failed: {str(e)}")

class SystemTTSEngine:
    def __init__(self):
        self.name = "system"
    
    def generate_audio(self, text, options):
        try:
            filename = f"{options['agent']}_{options['timestamp'].isoformat().replace(':', '-')}.wav"
            filepath = AUDIO_DIR / filename
            
            import subprocess
            cmd = [
                "espeak", 
                "-s", str(int(150 * options.get('speed', 1.0))),
                "-w", str(filepath),
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Generated audio with system TTS: {filepath}")
                return str(filepath)
            else:
                raise Exception(f"espeak failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"System TTS generation failed: {e}")
            filename = f"{options['agent']}_{options['timestamp'].isoformat().replace(':', '-')}_silent.wav"
            filepath = AUDIO_DIR / filename
            
            import wave
            with wave.open(str(filepath), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                wav_file.writeframes(b'\x00' * 44100)
            
            logger.info(f"Generated silent audio fallback: {filepath}")
            return str(filepath)

# Initialize TTS engines
tts_engines = {
    "gtts": GTTSEngine(),
    "openai": OpenAITTSEngine(),
    "system": SystemTTSEngine()
}

def generate_cache_key(text, options):
    """Generate a cache key for the given text and options"""
    cache_data = {
        'text': text,
        'engine': options.get('engine'),
        'voice_type': options.get('voice_type'),
        'language': options.get('language'),
        'speed': options.get('speed')
    }
    return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

# API Endpoints
@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint with system status"""
    uptime = datetime.datetime.now() - app_state["start_time"]
    
    engines_status = {
        "gtts": GTTS_AVAILABLE,
        "openai": OPENAI_AVAILABLE and tts_engines["openai"].client is not None,
        "system": True
    }
    
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "engines_available": engines_status,
        "uptime": str(uptime),
        "total_requests": app_state["request_count"],
        "cache_size": len(app_state["cache"])
    })

@app.route("/webhook", methods=["POST"])
def receive_utterance():
    """Enhanced webhook endpoint for TTS generation"""
    start_time = datetime.datetime.now()
    app_state["request_count"] += 1
    
    try:
        payload = request.get_json()
        
        # Extract and validate payload
        agent = payload.get('agent', 'unknown')
        utterance = payload.get('utterance', '')
        importance = payload.get('importance', 1.0)
        timestamp = payload.get('timestamp', datetime.datetime.now().isoformat())
        
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        engine_name = payload.get('engine', 'gtts')
        voice_type = payload.get('voice_type', 'neutral')
        language = payload.get('language', 'en')
        speed = payload.get('speed', 1.0)
        
        if not utterance or not utterance.strip():
            return jsonify({
                "status": "error",
                "message": "Utterance cannot be empty"
            }), 400
        
        logger.info(f"[{timestamp}] Agent: {agent}, Engine: {engine_name}, Utterance: '{utterance[:50]}...'")
        
        # Generate cache key
        options = {
            'agent': agent,
            'timestamp': timestamp,
            'engine': engine_name,
            'voice_type': voice_type,
            'language': language,
            'speed': speed
        }
        
        cache_key = generate_cache_key(utterance, options)
        cache_hit = False
        
        # Check cache
        if cache_key in app_state["cache"]:
            cached_file = app_state["cache"][cache_key]
            if Path(cached_file).exists():
                audio_filepath = cached_file
                cache_hit = True
                logger.info(f"Cache hit for utterance: {cache_key}")
            else:
                del app_state["cache"][cache_key]
        
        if not cache_hit:
            # Select TTS engine with fallback
            engine = tts_engines.get(engine_name)
            if not engine:
                engine = tts_engines["system"]
            
            # Generate audio
            try:
                audio_filepath = engine.generate_audio(utterance, options)
                app_state["cache"][cache_key] = audio_filepath
            except Exception as e:
                if engine_name != "system":
                    logger.warning(f"Primary engine failed, trying system fallback: {e}")
                    engine = tts_engines["system"]
                    audio_filepath = engine.generate_audio(utterance, options)
                    app_state["cache"][cache_key] = audio_filepath
                else:
                    raise e
        
        # Get file info
        file_path = Path(audio_filepath)
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # Generate public URL for the audio file
        audio_url = f"/audio/{file_path.name}"
        
        # Calculate processing time
        processing_time = (datetime.datetime.now() - start_time).total_seconds()
        
        # Simulate avatar binding dispatch
        avatar_id = payload.get('avatar_id')
        if avatar_id:
            logger.info(f"Dispatching to Avatar binding for agent {agent} with avatar {avatar_id}")
        
        return jsonify({
            "status": "success",
            "message": "Utterance processed successfully",
            "audio_file": audio_filepath,
            "audio_url": audio_url,
            "agent": agent,
            "engine_used": engine.name,
            "processing_time": processing_time,
            "file_size": file_size,
            "cache_hit": cache_hit
        })
        
    except Exception as e:
        logger.error(f"TTS processing failed: {e}")
        processing_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return jsonify({
            "status": "error",
            "message": f"TTS processing failed: {str(e)}",
            "agent": payload.get('agent', 'unknown') if payload else 'unknown',
            "engine_used": "none",
            "processing_time": processing_time
        }), 500

@app.route("/audio/<filename>", methods=["GET"])
def serve_audio(filename):
    """Serve generated audio files"""
    file_path = AUDIO_DIR / filename
    
    if not file_path.exists():
        return jsonify({"error": "Audio file not found"}), 404
    
    return send_file(
        str(file_path),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name=filename
    )

@app.route("/engines", methods=["GET"])
def list_engines():
    """List available TTS engines and their status"""
    engines_info = {}
    
    for engine_name, engine in tts_engines.items():
        if engine_name == "gtts":
            available = GTTS_AVAILABLE
        elif engine_name == "openai":
            available = OPENAI_AVAILABLE and engine.client is not None
        else:
            available = True
            
        engines_info[engine_name] = {
            "name": engine.name,
            "available": available,
            "description": f"{engine_name.title()} Text-to-Speech Engine"
        }
    
    return jsonify(engines_info)

@app.route("/cache", methods=["DELETE"])
def clear_cache():
    """Clear the TTS cache"""
    app_state["cache"].clear()
    return jsonify({"status": "success", "message": "Cache cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
