"""
HeyGen Integration Module for Avatar Binding
Integrates with HeyGen API for visual avatar generation
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class HeyGenAvatarService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('HEYGEN_API_KEY')
        self.base_url = "https://api.heygen.com"
        self.client = httpx.AsyncClient(
            headers={
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            } if self.api_key else {}
        )
    
    async def create_avatar_video(self, 
                                text: str, 
                                avatar_id: str,
                                voice_id: Optional[str] = None,
                                background: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an avatar video using HeyGen API
        
        Args:
            text: The text to be spoken by the avatar
            avatar_id: HeyGen avatar ID
            voice_id: Optional voice ID for the avatar
            background: Optional background setting
            
        Returns:
            Dict containing video generation response
        """
        if not self.api_key:
            raise ValueError("HeyGen API key not provided")
        
        try:
            payload = {
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": text,
                        "voice_id": voice_id or "default"
                    },
                    "background": {
                        "type": "color",
                        "value": background or "#ffffff"
                    }
                }],
                "dimension": {
                    "width": 1280,
                    "height": 720
                },
                "aspect_ratio": "16:9"
            }
            
            response = await self.client.post(
                f"{self.base_url}/v2/video/generate",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"HeyGen video generation initiated: {result.get('video_id')}")
                return result
            else:
                logger.error(f"HeyGen API error: {response.status_code} - {response.text}")
                return {"error": f"HeyGen API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HeyGen avatar video creation failed: {e}")
            return {"error": str(e)}
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation
        
        Args:
            video_id: The video ID returned from create_avatar_video
            
        Returns:
            Dict containing video status information
        """
        if not self.api_key:
            raise ValueError("HeyGen API key not provided")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/video_status.get",
                params={"video_id": video_id},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HeyGen status check error: {response.status_code}")
                return {"error": f"Status check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HeyGen status check failed: {e}")
            return {"error": str(e)}
    
    async def list_avatars(self) -> Dict[str, Any]:
        """
        List available avatars
        
        Returns:
            Dict containing available avatars
        """
        if not self.api_key:
            return {"error": "HeyGen API key not provided"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/avatar.list",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HeyGen avatar list error: {response.status_code}")
                return {"error": f"Avatar list failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HeyGen avatar list failed: {e}")
            return {"error": str(e)}
    
    async def list_voices(self) -> Dict[str, Any]:
        """
        List available voices
        
        Returns:
            Dict containing available voices
        """
        if not self.api_key:
            return {"error": "HeyGen API key not provided"}
        
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/voice.list",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HeyGen voice list error: {response.status_code}")
                return {"error": f"Voice list failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"HeyGen voice list failed: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Integration with main TTS service
async def bind_avatar_to_utterance(utterance_data: Dict[str, Any], 
                                 audio_file_path: str,
                                 heygen_service: HeyGenAvatarService) -> Dict[str, Any]:
    """
    Bind an avatar to a generated utterance
    
    Args:
        utterance_data: The original utterance payload
        audio_file_path: Path to the generated audio file
        heygen_service: HeyGen service instance
        
    Returns:
        Dict containing avatar binding result
    """
    try:
        avatar_id = utterance_data.get('avatar_id')
        if not avatar_id:
            return {"status": "skipped", "message": "No avatar ID provided"}
        
        # Create avatar video with the utterance text
        result = await heygen_service.create_avatar_video(
            text=utterance_data['utterance'],
            avatar_id=avatar_id,
            voice_id=utterance_data.get('voice_id'),
            background=utterance_data.get('background')
        )
        
        if 'error' in result:
            return {"status": "error", "message": result['error']}
        
        return {
            "status": "success",
            "video_id": result.get('video_id'),
            "message": "Avatar video generation initiated"
        }
        
    except Exception as e:
        logger.error(f"Avatar binding failed: {e}")
        return {"status": "error", "message": str(e)}
