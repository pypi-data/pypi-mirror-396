import time
import threading
import httpx
import logging
import json
import os
import fcntl
from . import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self):
        self.token = None
        self.token_expiry = 0
        self.lock = threading.Lock()
        # Token validity duration in seconds (12 hours)
        self.TOKEN_LIFETIME = 12 * 60 * 60
        # File path for token persistence
        # Using /tmp ensures write permissions in most serverless/container environments
        self.TOKEN_FILE = "/tmp/zhongzhi_token_cache.json"

    def _load_from_file(self):
        """Loads token from file if valid."""
        if not os.path.exists(self.TOKEN_FILE):
            return None, 0
        
        try:
            with open(self.TOKEN_FILE, 'r') as f:
                # Shared lock for reading
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return data.get("token"), data.get("expiry", 0)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logger.warning(f"Failed to load token from file: {e}")
            return None, 0

    def _save_to_file(self, token, expiry):
        """Saves token to file."""
        try:
            with open(self.TOKEN_FILE, 'w') as f:
                # Exclusive lock for writing
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump({"token": token, "expiry": expiry}, f)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logger.warning(f"Failed to save token to file: {e}")

    def login(self):
        """Performs login and updates the token."""
        url = f"{config.BASE_URL}{config.LOGIN_ENDPOINT}"
        data = {
            "userName": config.USERNAME,
            "password": config.PASSWORD
        }
        
        try:
            logger.info(f"Attempting login to {url}...")
            response = httpx.post(url, data=data, timeout=10.0, verify=False)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                new_token = result.get("token")
                expiry = time.time() + self.TOKEN_LIFETIME
                
                # Update memory
                with self.lock:
                    self.token = new_token
                    self.token_expiry = expiry
                
                # Update file
                self._save_to_file(new_token, expiry)
                
                logger.info("Login successful. Token updated and saved to file.")
                return True
            else:
                logger.error(f"Login failed: {result.get('msg')}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def get_token(self):
        """
        Returns the current valid token. 
        Checks memory -> file -> login.
        """
        current_time = time.time()
        
        # 1. Check Memory
        with self.lock:
            if self.token and current_time < self.token_expiry:
                return self.token

        # 2. Check File (in case another process updated it)
        file_token, file_expiry = self._load_from_file()
        if file_token and current_time < file_expiry:
            with self.lock:
                self.token = file_token
                self.token_expiry = file_expiry
            return self.token

        # 3. Login (if both memory and file are expired)
        # Use a file lock to ensure only one process performs login
        # We open the file (or create it) just for locking purposes
        lock_file = self.TOKEN_FILE + ".lock"
        with open(lock_file, 'w') as f_lock:
            try:
                # Try to acquire exclusive lock. 
                # If blocked, it means another process is logging in.
                fcntl.flock(f_lock, fcntl.LOCK_EX)
                
                # Double check file after acquiring lock
                file_token, file_expiry = self._load_from_file()
                if file_token and current_time < file_expiry:
                    with self.lock:
                        self.token = file_token
                        self.token_expiry = file_expiry
                    return self.token
                
                # Still expired? Perform login
                if not self.login():
                    raise Exception("Failed to obtain token")
                    
            finally:
                fcntl.flock(f_lock, fcntl.LOCK_UN)
        
        return self.token

    def start_scheduler(self):
        """Deprecated."""
        pass

    def stop_scheduler(self):
        """Deprecated."""
        pass
