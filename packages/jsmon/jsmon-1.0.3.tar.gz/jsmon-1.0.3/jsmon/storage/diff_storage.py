import os
import time
import zlib
import redis.asyncio as redis
from jsmon.utils.hashing import calculate_content_hash
from jsmon.utils.diff import create_beautified_diff
from jsmon.config.constants import CONTENT_HASH_KEY_TPL

class HybridDiffStorage:
    """
    Hybrid storage:
    - Redis: hashes and metadata (fast access)
    - Disk: compressed content (cheap storage)
    """
    def __init__(self, redis_client: redis.Redis, storage_dir: str = "js_storage"):
        self.r = redis_client
        self.storage_dir = storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    async def get_and_compare(self, url: str, new_content: str) -> tuple:
        """
        Returns: (has_changes: bool, diff: str, old_hash: str)
        """
        new_hash = calculate_content_hash(new_content)
        redis_key = CONTENT_HASH_KEY_TPL.format(hash=new_hash)
        
        # 1. Check if this hash is already known (global deduplication)
        if await self.r.exists(redis_key):
            # Update the last access time
            await self.r.expire(redis_key, 86400 * 30)
            return False, "", new_hash

        # 2. If the hash is new, check the previous hash for this URL
        url_key = f"url_hash:{url}"
        old_hash = await self.r.get(url_key)
        
        if old_hash:
            old_hash = old_hash.decode()
            if old_hash == new_hash:
                return False, "", new_hash
            
            # 3. If hashes differ, load old content from disk
            old_content = await self._load_content_from_disk(old_hash)
            if old_content:
                diff = create_beautified_diff(old_content, new_content, os.path.basename(url))
                await self._save_content_to_disk(new_hash, new_content)
                await self.r.set(url_key, new_hash)
                await self.r.set(redis_key, "1", ex=86400 * 30)
                return True, diff, old_hash
        
        # 4. If it's a new URL
        await self._save_content_to_disk(new_hash, new_content)
        await self.r.set(url_key, new_hash)
        await self.r.set(redis_key, "1", ex=86400 * 30)
        
        return False, "", None

    async def _save_content_to_disk(self, content_hash: str, content: str):
        """Saves compressed content to disk."""
        file_path = os.path.join(self.storage_dir, content_hash[:2], content_hash)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        compressed = zlib.compress(content.encode('utf-8'))
        
        # Blocking I/O in executor
        import asyncio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._write_file, file_path, compressed)

    def _write_file(self, path, data):
        with open(path, 'wb') as f:
            f.write(data)

    async def _load_content_from_disk(self, content_hash: str) -> str:
        """Loads and decompresses content from disk."""
        file_path = os.path.join(self.storage_dir, content_hash[:2], content_hash)
        if not os.path.exists(file_path):
            return ""
        
        import asyncio
        loop = asyncio.get_running_loop()
        try:
            compressed = await loop.run_in_executor(None, self._read_file, file_path)
            return zlib.decompress(compressed).decode('utf-8')
        except Exception as e:
            print(f"[!] Read error {content_hash}: {e}")
            return ""

    def _read_file(self, path):
        with open(path, 'rb') as f:
            return f.read()

    async def get_storage_stats(self) -> dict:
        """Returns storage usage statistics."""
        info = await self.r.info(section='memory')
        keys = await self.r.dbsize()
        
        # Disk stats
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(self.storage_dir):
            for f in files:
                fp = os.path.join(root, f)
                total_size += os.path.getsize(fp)
                file_count += 1
        
        return {
            'redis_memory': info.get('used_memory_human'),
            'redis_peak': info.get('used_memory_peak_human'),
            'redis_keys': keys,
            'disk_files': file_count,
            'disk_size_mb': round(total_size / (1024 * 1024), 2),
            'fragmentation': info.get('mem_fragmentation_ratio')
        }
