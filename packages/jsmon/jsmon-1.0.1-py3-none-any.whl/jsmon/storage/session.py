import time
import json
import os
import redis.asyncio as redis
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class DomainSession:
    """A structure for storing a domain session."""
    domain: str
    cookies: List[Dict[str, str]]
    created_at: float
    expires_at: float
    last_validated: float
    auto_refresh_token: Optional[str] = None
    bearer_token: Optional[str] = None
    localstorage: Optional[Dict[str, str]] = None
    status: str = "active"

class SessionManager:
    """Manager for working with authenticated sessions."""
    
    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client
        self.encryption_key = os.getenv("SESSION_ENCRYPTION_KEY")
        if self.encryption_key:
            from cryptography.fernet import Fernet
            self.cipher = Fernet(self.encryption_key.encode())
        else:
            self.cipher = None
            # print("[⚠️] SESSION_ENCRYPTION_KEY not set! Cookies will be stored unencrypted.")
        
        self.health_config = self._load_health_config()
    
    def _load_health_config(self) -> dict:
        """Loads the configuration for health checks."""
        try:
            with open('health_check_config.json', 'r') as f:
                config = json.load(f)
                return config['health_checks']
        except FileNotFoundError:
            return {
                "_default": {
                    "url": "/api/users/me", "expected_status": 200,
                    "auth_indicators": ["id", "email", "username"],
                    "failure_indicators": ["unauthorized", "unauthenticated", "login"]
                }
            }
        except Exception as e:
            print(f"[❌] Failed to load or parse health_check_config.json: {e}")
            return {"_default": {}}

    async def save_session(self, domain: str, cookies: List[Dict], 
                           expires_in_days: int = 30,
                           refresh_token: str = None,
                           bearer_token: str = None,
                           localstorage: dict = None):
        """Saves a session in Redis."""
        session_data = {
            'cookies': cookies, 'created_at': time.time(),
            'expires_at': time.time() + (expires_in_days * 86400),
            'last_validated': time.time(), 'auto_refresh_token': refresh_token,
            'bearer_token': bearer_token,
            'localstorage': localstorage,
            'status': 'active'
        }
        if self.cipher:
            encrypted = self.cipher.encrypt(json.dumps(session_data).encode())
            await self.r.set(f"session:{domain}", encrypted, ex=expires_in_days * 86400)
        else:
            await self.r.set(f"session:{domain}", json.dumps(session_data), ex=expires_in_days * 86400)

    async def update_session(self, session: DomainSession):
        """Updates session data but retains the original TTL."""
        session_data = {
            'cookies': session.cookies,
            'created_at': session.created_at,
            'expires_at': session.expires_at,
            'last_validated': time.time(),
            'auto_refresh_token': session.auto_refresh_token,
            'bearer_token': session.bearer_token,
            'localstorage': session.localstorage,
            'status': 'active'
        }
        if self.cipher:
            encrypted = self.cipher.encrypt(json.dumps(session_data).encode())
            await self.r.set(f"session:{session.domain}", encrypted, keepttl=True)
        else:
            await self.r.set(f"session:{session.domain}", json.dumps(session_data), keepttl=True)
    
    async def get_session(self, domain: str) -> Optional[DomainSession]:
        """Gets the session from Redis with fallback to root domain."""
        session = await self._get_session_by_key(f"session:{domain}")
        if session:
            return session

        parts = domain.split('.')
        if len(parts) > 2:
            if len(parts[-2]) <= 3 and len(parts[-1]) <= 2 and len(parts) > 2:
                root_domain = '.'.join(parts[-3:])
            else:
                root_domain = '.'.join(parts[-2:])
            
            if root_domain != domain:
                session = await self._get_session_by_key(f"session:{root_domain}")
                if session:
                    return session
        return None

    async def _get_session_by_key(self, session_key: str) -> Optional[DomainSession]:
        """Internal helper method for retrieving and decrypting a session by key."""
        encrypted_data = await self.r.get(session_key)
        if not encrypted_data:
            return None
        
        domain_from_key = session_key.split(':', 1)[1]
        
        try:
            if self.cipher:
                decrypted_data = self.cipher.decrypt(encrypted_data)
                session_data = json.loads(decrypted_data.decode())
            else:
                session_data = json.loads(encrypted_data.decode() if isinstance(encrypted_data, bytes) else encrypted_data)
            
            return DomainSession(
                domain=domain_from_key,
                cookies=session_data['cookies'],
                created_at=session_data['created_at'],
                expires_at=session_data['expires_at'],
                last_validated=session_data['last_validated'],
                auto_refresh_token=session_data.get('auto_refresh_token'),
                bearer_token=session_data.get('bearer_token'),
                localstorage=session_data.get('localstorage'),
                status=session_data.get('status', 'active')
            )
        except Exception as e:
            print(f"[❌] Failed to process session for key {session_key}: {e}")
            return None

    async def list_all_sessions(self) -> List[str]:
        """Returns a list of all domains with saved sessions."""
        pattern = "session:*"
        try:
            keys = [key.decode().replace('session:', '') async for key in self.r.scan_iter(pattern)]
            return keys
        except Exception as e:
            print(f"[❌] Failed to list sessions from Redis: {e}")
            return []
    
    async def mark_expired(self, domain_to_check: str):
        """Marks the session as expired."""
        session = await self.get_session(domain_to_check)
        if session:
            actual_domain = session.domain 
            session_data = {
                'cookies': session.cookies,
                'created_at': session.created_at,
                'expires_at': session.expires_at,
                'last_validated': time.time(),
                'auto_refresh_token': session.auto_refresh_token,
                'localstorage': session.localstorage, 
                'status': 'active'
            }
            if self.cipher:
                encrypted = self.cipher.encrypt(json.dumps(session_data).encode())
                await self.r.set(f"session:{actual_domain}", encrypted, keepttl=True)
            else:
                await self.r.set(f"session:{actual_domain}", json.dumps(session_data), keepttl=True)
