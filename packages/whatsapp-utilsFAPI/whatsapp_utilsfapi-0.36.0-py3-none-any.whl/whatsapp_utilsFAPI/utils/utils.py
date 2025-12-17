"""
Utility functions for WhatsApp audio message handling.
"""

import glob
import json
import logging
import os
import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import Response
import requests
import nltk
from nltk.tokenize import sent_tokenize
import time

#from pydub import AudioSegment



logger = logging.getLogger(__name__)

class WhatsAppError(Exception):
    """Custom exception for WhatsApp API errors."""
    pass


class AudioConversionError(Exception):
    """Custom exception for audio conversion errors."""
    pass

def webhook_check(challenge,token,VERIFY_TOKEN):
    print(f"{challenge},{token},{VERIFY_TOKEN}")
    print(token == VERIFY_TOKEN)
    if token == VERIFY_TOKEN:
        print(f"{challenge},{token},{VERIFY_TOKEN}")
        logger.info("Webhook verified successfully")
        return Response(content=challenge, status_code=status.HTTP_200_OK)
    else:
        logger.warning("Webhook verification failed: invalid token or missing challenge")
        return Response(content="Verification failed", status_code=status.HTTP_403_FORBIDDEN)

def verfy_token(sys_conf: dict,timeout: int = 5):
    url = "https://graph.facebook.com/v20.0/me"
    headers = {
        "Authorization": f"Bearer {sys_conf['whatapp_token']}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        status_code = response.status_code

        if status_code == 200:
            return {
                "status": True,
                "status_code": status_code,
                "message": "Token is valid and active",
                "data": response.json()
            }

        else:
            error = response.json().get("error", {})
            return {
                "status": False,
                "status_code": status_code,
                "message": error.get("message", "Invalid token"),
                "data": error
            }

    except requests.exceptions.Timeout:
        return {
            "status": False,
            "status_code": 408,
            "message": "Request timed out",
            "data": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": False,
            "status_code": 500,
            "message": str(e),
            "data": None
        }
def get_message(data):
    try:
        logger.info("Incoming webhook payload: %s", json.dumps(data, indent=2, ensure_ascii=False))
        print(f"""####   Data 
              
              {data}
              
              """)
        entry = data.get("entry", [])[0].get("changes", [])[0].get("value", {})
        messages = entry.get("messages", [])

        if not messages:
            logger.info("No messages found in webhook payload")
            return {"status":True,"msg":""}

        msg = messages[0]
        return {"status":True,
                "msg":msg}

    except Exception as e:
        logger.error("Error in delete_files_by_mask: %s", str(e))
        return {"status":False}


def delete_files_by_mask(directory: str, pattern: str) -> int:
    """
    Delete files in a directory matching a given pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern (e.g., '*.mp3', 'temp_*')
        
    Returns:
        Number of files deleted
    """
    try:
        files = glob.glob(os.path.join(directory, pattern))
        deleted_count = 0

        for file_path in files:
            try:
                os.remove(file_path)
                deleted_count += 1
                logger.info("Deleted file: %s", file_path)
            except Exception as e:
                logger.warning("Failed to delete %s: %s", file_path, str(e))

        logger.info("Total files deleted: %d", deleted_count)
        return deleted_count
        
    except Exception as e:
        logger.error("Error in delete_files_by_mask: %s", str(e))
        return 0



def send_whatsapp_text_message(to: str, message: str, sys_conf: dict) -> Dict[str, Any]:
    """
    Send WhatsApp text message via Meta Graph API.
    
    Args:
        to: Recipient phone number
        message: Text message to send
        sys_conf: System configuration dictionary
        
    Returns:
        API response
        
    Raises:
        WhatsAppError: If message sending fails
    """
    try:
        url = f"https://graph.facebook.com/v22.0/{sys_conf['whatsapp_phone_id']}/messages"
        headers = {
            "Authorization": f"Bearer {sys_conf['whatapp_token']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        print(f"""result 
              
              {result}
              
              """)
        print(response.raise_for_status())
        
        
        logger.info("Text message sent successfully to %s", to)
        return {"status":True,"data":result,"comment":200}
        
    except requests.exceptions.RequestException as e:
        print("Failed to send WhatsApp text message: %s", str(e))
        return {"status":True,"data":result,"comment":f"Failed to send WhatsApp text message: {str(e)}"}


def whatsapp_upload_media(file_path: str, sys_conf: dict) -> Optional[str]:
    """
    Upload media file to WhatsApp and return media ID.
    
    Args:
        file_path: Path to media file
        sys_conf: System configuration dictionary
        
    Returns:
        Media ID if successful, None otherwise
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Media file not found: {file_path}")

        url = f"https://graph.facebook.com/v20.0/{sys_conf['whatsapp_phone_id']}/media"
        headers = {"Authorization": f"Bearer {sys_conf['whatapp_token']}"}

        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file, "audio/mpeg")}
            data = {"messaging_product": "whatsapp"}
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()

        result = response.json()
        logger.info("Media uploaded successfully: %s", result.get("id"))
        return result.get("id")
        
    except Exception as e:
        logger.error("Failed to upload media to WhatsApp: %s", str(e))
        return None


def send_whatsapp_audio_by_id(to: str, media_id: str, sys_conf: dict) -> Dict[str, Any]:
    """
    Send WhatsApp audio message using media ID.
    
    Args:
        to: Recipient phone number
        media_id: WhatsApp media ID
        sys_conf: System configuration dictionary
        
    Returns:
        API response
        
    Raises:
        WhatsAppError: If audio sending fails
    """
    try:
        url = f"https://graph.facebook.com/v20.0/{sys_conf['whatsapp_phone_id']}/messages"
        headers = {
            "Authorization": f"Bearer {sys_conf['whatapp_token']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"id": media_id}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Audio message sent successfully to %s", to)
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send WhatsApp audio message: %s", str(e))
        raise WhatsAppError(f"Failed to send audio message: {str(e)}") from e


def send_whatsapp_voice(to, ogg_path,sys_conf):
    url = f"https://graph.facebook.com/v21.0/{sys_conf['whatsapp_phone_id']}/messages"
    headers = {
        "Authorization": f"Bearer {sys_conf['whatapp_token']}"
    }
    files = {
        "file": (os.path.basename(ogg_path), open(ogg_path, "rb"), "audio/ogg; codecs=opus")
    }
    data = {
        "messaging_product": "whatsapp"  # ✅ REQUIRED HERE
    }

    # Step 1: upload media
    upload_resp = requests.post(
        f"https://graph.facebook.com/v21.0/{sys_conf['whatsapp_phone_id']}/media",
        headers=headers,
        files=files,
        data=data
    ).json()
    logger.info(f"##  upload_resp  {upload_resp} " )

    media_id = upload_resp["id"]

    # Step 2: send voice message
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {
            "id": media_id
        }
    }
    resp = requests.post(url, headers=headers, json=data)
    return resp.json()


def send_custome_text_message(to,text,sys_conf,t_list=[],b_list=[]):
   

    logger.info("### WhatsAppOutput_msg - send_indus_selc ###")
    
    qt=""
    bl=[]
    
    
  
  
    time.sleep(1)
    for n,i in enumerate(b_list):
        if len(t_list) >0:
            t_list=" \n".join(t_list)

        if n<3 and len(b_list)>0:
            qt=qt+f"""\n{n+1}) {i}"""
            bl.append({"type": "reply",
                            "reply": {
                                "id": i,
                                "title": str(n+1)
                            }})
    url = f"https://graph.facebook.com/v22.0/{sys_conf['whatsapp_phone_id']}/messages"
    headers = {
        "Authorization": f"Bearer {sys_conf['whatapp_token']}", 
        "Content-Type": "application/json"
    }
    logger.info(f""" tespons 
                
            

                {t_list}

                {bl}


                """)
    if len(bl)>0:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text+qt
                },
                "action": {
                    "buttons": bl
                }
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text
                }
                
            }
        }

    
    logger.info(f"""

            {payload}

        """)
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code != 200:
            print(f"Error details: {r.json()}")
            return {"status":True,"comment":r.status_code}
        else:
            print("Message sent successfully!")
            return {"status":True,"comment":200}
            
    except Exception as e:
        print(f"Request failed: {e}")

        return {"status":False,"comment":f"Exception : {str(e)}"}
    


