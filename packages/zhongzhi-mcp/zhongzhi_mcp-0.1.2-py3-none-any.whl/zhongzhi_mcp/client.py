import httpx
import logging
from typing import Optional, Dict, Any
from . import config
from .auth import TokenManager

logger = logging.getLogger(__name__)

class ZhongzhiClient:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.client = httpx.Client(timeout=30.0)

    def _get_headers(self) -> Dict[str, str]:
        token = self.token_manager.get_token()
        return {
            "token": token,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def search_patents(self, 
                       tm_name: Optional[str] = None, 
                       reg_num: Optional[str] = None, 
                       page: int = 1, 
                       page_size: int = 10,
                       **kwargs) -> Dict[str, Any]:
        """
        Search patents using the customized query interface.
        """
        url = f"{config.BASE_URL}{config.SEARCH_ENDPOINT}"
        data = {
            "page": page,
            "pageSize": page_size
        }
        if tm_name:
            data["tmName"] = tm_name
        if reg_num:
            data["regNum"] = reg_num
        data.update(kwargs)
        data = {k: v for k, v in data.items() if v is not None}
        
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    def get_patent_detail(self, tid: str, detail_type: str = "0") -> Dict[str, Any]:
        """
        Get patent details using the customized detail interface.
        """
        url = f"{config.BASE_URL}{config.DETAIL_ENDPOINT}"
        params = {
            "tid": tid,
            "type": detail_type
        }
        try:
            response = self.client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Detail error: {e}")
            raise

    def get_pledge_info(self, reg_num: str, int_cls: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get pledge information.
        """
        url = f"{config.BASE_URL}{config.PLEDGE_ENDPOINT}"
        data = {
            "regNum": reg_num,
            "intCls": int_cls,
            "page": page,
            "pageSize": page_size
        }
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Pledge info error: {e}")
            raise

    def get_balance(self) -> Dict[str, Any]:
        """
        Get interface balance.
        """
        url = f"{config.BASE_URL}{config.BALANCE_ENDPOINT}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Balance error: {e}")
            raise

    def image_search(self, image_url: str) -> Dict[str, Any]:
        """
        Search by image.
        """
        url = f"{config.BASE_URL}{config.IMAGE_SEARCH_ENDPOINT}"
        data = {"imageUrl": image_url}
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Image search error: {e}")
            raise

    def image_search_aggregation(self, image_url: str) -> Dict[str, Any]:
        """
        Search by image (Aggregation).
        """
        url = f"{config.BASE_URL}{config.IMAGE_SEARCH_AGG_ENDPOINT}"
        data = {"imageUrl": image_url}
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Image search aggregation error: {e}")
            raise

    def check_sensitive_word(self, word: str) -> Dict[str, Any]:
        """
        Check for sensitive words.
        """
        url = f"{config.BASE_URL}{config.SENSITIVE_WORD_ENDPOINT}"
        params = {"word": word}
        try:
            response = self.client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Sensitive word check error: {e}")
            raise
