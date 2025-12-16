import asyncio
import json
import os
from pathlib import Path

async def create_and_upload_archive(output_dir: Path, timestamp: str) -> str:
    """Creates a RAR archive and uploads to gofile.io."""
    archive_name = f"js_analyzer_report_{timestamp}.rar"
    print(f"[+] Creating RAR archive: {archive_name}")
    
    try:
        # Create RAR archive
        result = await asyncio.create_subprocess_exec(
            'rar', 'a', '-r', '-ep1', archive_name, str(output_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await result.communicate()
        
        if result.returncode != 0:
            print(f"[!] RAR creation failed with code {result.returncode}")
            return None
        
        print(f"[+] Archive created successfully: {archive_name}")
        
        # Upload to gofile
        print(f"[+] Uploading to gofile.io...")
        upload_result = await asyncio.create_subprocess_exec(
            'curl', '-s', '-F', f'file=@{archive_name}', 
            'https://store1.gofile.io/uploadFile',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await upload_result.communicate()
        
        if upload_result.returncode == 0:
            try:
                result_json = json.loads(stdout.decode())
                if result_json.get('status') == 'ok':
                    download_link = result_json['data']['downloadPage']
                    print(f"[+] Upload successful: {download_link}")
                    
                    # Delete temporary archive
                    try:
                        os.remove(archive_name)
                        print(f"[+] Temporary archive deleted: {archive_name}")
                    except Exception as e:
                        print(f"[!] Failed to delete temp archive: {e}")
                    
                    return download_link
            except json.JSONDecodeError:
                print(f"[!] Failed to parse upload response")
        
        return None
        
    except FileNotFoundError:
        print("[!] 'rar' or 'curl' command not found. Skipping archive creation.")
        return None
    except Exception as e:
        print(f"[!] Archive/upload error: {e}")
        return None
