import asyncio
import json
import os
from pathlib import Path

async def create_and_upload_archive(output_dir: Path, timestamp: str, gofile_api_key: str = None) -> str:
    """Creates a RAR archive and uploads to gofile.io using the new API."""
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
        
        # Upload to gofile using new API
        if not gofile_api_key:
            print(f"[!] No gofile API key provided. Archive saved locally: {archive_name}")
            print(f"    Upload manually: curl -X POST 'https://upload.gofile.io/uploadfile' -H 'Authorization: Bearer YOUR_KEY' -F 'file=@{archive_name}'")
            return None
        
        print(f"[+] Uploading to gofile.io...")
        upload_result = await asyncio.create_subprocess_exec(
            'curl', '-s', '-X', 'POST',
            'https://upload.gofile.io/uploadfile',
            '-H', f'Authorization: Bearer {gofile_api_key}',
            '-F', f'file=@{archive_name}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await upload_result.communicate()
        
        if upload_result.returncode == 0:
            try:
                result_json = json.loads(stdout.decode())
                if result_json.get('status') == 'ok':
                    download_link = result_json['data'].get('downloadPage') or result_json['data'].get('link')
                    file_id = result_json['data'].get('fileId', '')
                    print(f"[+] Upload successful!")
                    print(f"    Download: {download_link}")
                    if file_id:
                        print(f"    File ID: {file_id}")
                    
                    # Delete temporary archive
                    try:
                        os.remove(archive_name)
                        print(f"[+] Temporary archive deleted: {archive_name}")
                    except Exception as e:
                        print(f"[!] Failed to delete temp archive: {e}")
                    
                    return download_link
                else:
                    error_msg = result_json.get('message', 'Unknown error')
                    print(f"[!] Upload failed: {error_msg}")
            except json.JSONDecodeError:
                print(f"[!] Failed to parse upload response: {stdout.decode()[:200]}")
        else:
            print(f"[!] curl failed with code {upload_result.returncode}")
            if stderr:
                print(f"    Error: {stderr.decode()[:200]}")
        
        return None
        
    except FileNotFoundError:
        print("[!] 'rar' or 'curl' command not found. Skipping archive creation.")
        return None
    except Exception as e:
        print(f"[!] Archive/upload error: {e}")
        return None


async def upload_file_to_gofile(file_path: str, gofile_api_key: str) -> str:
    """Upload a single file to gofile.io."""
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return None
    
    if not gofile_api_key:
        print(f"[!] No gofile API key provided.")
        return None
    
    print(f"[+] Uploading {file_path} to gofile.io...")
    
    try:
        upload_result = await asyncio.create_subprocess_exec(
            'curl', '-s', '-X', 'POST',
            'https://upload.gofile.io/uploadfile',
            '-H', f'Authorization: Bearer {gofile_api_key}',
            '-F', f'file=@{file_path}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await upload_result.communicate()
        
        if upload_result.returncode == 0:
            result_json = json.loads(stdout.decode())
            if result_json.get('status') == 'ok':
                download_link = result_json['data'].get('downloadPage') or result_json['data'].get('link')
                print(f"[+] Upload successful: {download_link}")
                return download_link
        
        return None
    except Exception as e:
        print(f"[!] Upload error: {e}")
        return None
