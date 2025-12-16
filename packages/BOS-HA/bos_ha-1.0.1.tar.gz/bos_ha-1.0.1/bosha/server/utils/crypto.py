import hmac
import hashlib
import base64
import urllib.parse
from typing import Optional

class CryptoUtils:
    """加密工具类，用于处理HMAC-SHA1签名等操作"""
    
    @staticmethod
    def hmac_sha1(key: str, message: str) -> bytes:
        """
        生成HMAC-SHA1签名
        
        Args:
            key: 密钥
            message: 消息
            
        Returns:
            bytes: HMAC-SHA1签名
        """
        try:
            key_bytes = key.encode('utf-8')
            message_bytes = message.encode('utf-8')
            hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha1)
            return hmac_obj.digest()
        except Exception as e:
            print(f"生成HMAC-SHA1签名失败: {e}")
            return b''
    
    @staticmethod
    def hmac_sha1_base64(key: str, message: str) -> str:
        """
        生成Base64编码的HMAC-SHA1签名
        
        Args:
            key: 密钥
            message: 消息
            
        Returns:
            str: Base64编码的HMAC-SHA1签名
        """
        try:
            digest = CryptoUtils.hmac_sha1(key, message)
            return base64.b64encode(digest).decode('utf-8')
        except Exception as e:
            print(f"生成Base64 HMAC-SHA1签名失败: {e}")
            return ""
    
    @staticmethod
    def verify_hmac_sha1(key: str, message: str, signature: str) -> bool:
        """
        验证HMAC-SHA1签名
        
        Args:
            key: 密钥
            message: 消息
            signature: 签名（Base64编码）
            
        Returns:
            bool: 验证结果
        """
        try:
            expected_signature = CryptoUtils.hmac_sha1_base64(key, message)
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            print(f"验证HMAC-SHA1签名失败: {e}")
            return False
    
    @staticmethod
    def url_encode(data: str) -> str:
        """
        URL编码
        
        Args:
            data: 待编码的数据
            
        Returns:
            str: URL编码后的数据
        """
        try:
            return urllib.parse.quote(data, safe='~')
        except Exception as e:
            print(f"URL编码失败: {e}")
            return data
    
    @staticmethod
    def validate_client(secret: str, client_id: str, passwd: str, valid_clients: dict) -> bool:
        """
        验证客户端
        
        Args:
            secret: 客户端提供的密钥
            client_id: 客户端ID
            passwd: 客户端提供的密码（签名）
            valid_clients: 有效的客户端列表，格式为 {client_id: secret}
            
        Returns:
            bool: 验证结果
        """
        try:
            # 1. 检查客户端ID是否在有效列表中
            if client_id not in valid_clients:
                print(f"无效的客户端ID: {client_id}")
                return False
            
            # 2. 检查提供的密钥是否正确
            if secret != valid_clients[client_id]:
                print(f"客户端 {client_id} 的密钥不正确")
                return False
            
            # 3. 验证密码（签名）
            # 密码应该是使用客户端ID作为消息，密钥作为密钥生成的HMAC-SHA1签名
            expected_passwd = CryptoUtils.hmac_sha1_base64(secret, client_id)
            if not hmac.compare_digest(expected_passwd, passwd):
                print(f"客户端 {client_id} 的签名验证失败")
                return False
            
            return True
            
        except Exception as e:
            print(f"验证客户端失败: {e}")
            return False
    
    @staticmethod
    def generate_token(client_id: str, secret: str, expiry: int = 3600) -> str:
        """
        生成访问令牌
        
        Args:
            client_id: 客户端ID
            secret: 密钥
            expiry: 过期时间，单位：秒
            
        Returns:
            str: 生成的令牌
        """
        try:
            import time
            timestamp = int(time.time()) + expiry
            message = f"{client_id}:{timestamp}"
            signature = CryptoUtils.hmac_sha1_base64(secret, message)
            return f"{client_id}:{timestamp}:{signature}"
        except Exception as e:
            print(f"生成令牌失败: {e}")
            return ""
    
    @staticmethod
    def verify_token(token: str, valid_clients: dict) -> Optional[str]:
        """
        验证访问令牌
        
        Args:
            token: 令牌
            valid_clients: 有效的客户端列表
            
        Returns:
            Optional[str]: 验证成功返回客户端ID，否则返回None
        """
        try:
            import time
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            client_id, timestamp_str, signature = parts
            timestamp = int(timestamp_str)
            
            # 检查令牌是否过期
            if timestamp < int(time.time()):
                return None
            
            # 检查客户端是否有效
            if client_id not in valid_clients:
                return None
            
            # 验证签名
            secret = valid_clients[client_id]
            message = f"{client_id}:{timestamp}"
            expected_signature = CryptoUtils.hmac_sha1_base64(secret, message)
            
            if hmac.compare_digest(expected_signature, signature):
                return client_id
            
            return None
            
        except Exception as e:
            print(f"验证令牌失败: {e}")
            return None
