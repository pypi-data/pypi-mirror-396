import random
from typing import Dict, Optional
from bosha.server.utils import info, warning, error
from bosha.server.config import settings

class ResourceManager:
    """资源管理器，管理channel和uid等资源"""
    
    def __init__(self):
        """初始化资源管理器"""
        self.channels = {}  # 存储通道信息
        self.client_resources = {}  # 存储客户端资源映射
        self.available_channels = []  # 可用通道列表
        
        # 初始化通道
        self.init_channels()
    
    def init_channels(self):
        """初始化通道列表"""
        try:
            for i in range(settings.MAX_CHANNELS):
                channel_name = f"{settings.AGORA_CHANNEL_PREFIX}{i+1}"
                self.channels[channel_name] = {
                    "name": channel_name,
                    "uids": [],
                    "max_uids": settings.MAX_UIDS_PER_CHANNEL
                }
                self.available_channels.append(channel_name)
            
            info(f"初始化完成 {settings.MAX_CHANNELS} 个通道")
            
        except Exception as e:
            error(f"初始化通道失败: {e}")
    
    def allocate_resource(self, client_id: str) -> Optional[Dict]:
        """
        为客户端分配资源
        
        Args:
            client_id: 客户端ID
            
        Returns:
            Optional[Dict]: 分配的资源信息，包括channel、uid等
        """
        try:
            # 检查客户端是否已经分配了资源
            if client_id in self.client_resources:
                warning(f"客户端 {client_id} 已经分配了资源")
                return self.client_resources[client_id]
            
            # 查找可用的通道
            available_channels = [
                channel for channel in self.channels.values()
                if len(channel["uids"]) < channel["max_uids"]
            ]
            
            if not available_channels:
                warning("没有可用的通道资源")
                return None
            
            # 随机选择一个可用通道
            selected_channel = random.choice(available_channels)
            
            # 分配UID
            uid = self._allocate_uid(selected_channel["name"])
            if uid is None:
                warning(f"通道 {selected_channel['name']} 没有可用的UID")
                return None
            
            # 生成Token（示例：实际应使用声网SDK生成）
            token = self._generate_agora_token(selected_channel["name"], uid)
            
            # 记录资源分配
            resource = {
                "channel": selected_channel["name"],
                "uid": uid,
                "token": token,
                "client_id": client_id
            }
            
            # 更新资源映射
            self.client_resources[client_id] = resource
            selected_channel["uids"].append(uid)
            
            info(f"已为客户端 {client_id} 分配资源: channel={selected_channel['name']}, uid={uid}")
            return resource
            
        except Exception as e:
            error(f"分配资源失败: {e}")
            return None
    
    def release_resource(self, client_id: str):
        """
        释放客户端资源
        
        Args:
            client_id: 客户端ID
        """
        try:
            # 检查客户端是否分配了资源
            if client_id not in self.client_resources:
                warning(f"客户端 {client_id} 没有分配资源")
                return
            
            # 获取客户端资源
            resource = self.client_resources[client_id]
            channel_name = resource["channel"]
            uid = resource["uid"]
            
            # 从通道中移除UID
            if channel_name in self.channels:
                if uid in self.channels[channel_name]["uids"]:
                    self.channels[channel_name]["uids"].remove(uid)
                    info(f"从通道 {channel_name} 中移除UID {uid}")
            
            # 移除客户端资源映射
            del self.client_resources[client_id]
            info(f"已释放客户端 {client_id} 的资源")
            
        except Exception as e:
            error(f"释放资源失败: {e}")
    
    def _allocate_uid(self, channel_name: str) -> Optional[int]:
        """
        为通道分配UID
        
        Args:
            channel_name: 通道名称
            
        Returns:
            Optional[int]: 分配的UID，None表示没有可用UID
        """
        try:
            if channel_name not in self.channels:
                return None
            
            channel = self.channels[channel_name]
            used_uids = channel["uids"]
            
            # 查找可用的UID
            for uid in range(1, channel["max_uids"] + 1):
                if uid not in used_uids:
                    return uid
            
            return None
            
        except Exception as e:
            error(f"分配UID失败: {e}")
            return None
    
    def _generate_agora_token(self, channel_name: str, uid: int) -> str:
        """
        生成声网Token
        
        Args:
            channel_name: 通道名称
            uid: 用户ID
            
        Returns:
            str: 声网Token
        """
        try:
            # 示例：实际应使用声网SDK生成Token
            # 例如使用声网的RtcTokenBuilder
            # from agora_token_builder import RtcTokenBuilder
            # token = RtcTokenBuilder.build_token_with_uid(
            #     settings.AGORA_APP_ID,
            #     settings.AGORA_APP_CERT,
            #     channel_name,
            #     uid,
            #     settings.AGORA_ROLE_PUBLISHER,
            #     settings.AGORA_TOKEN_EXPIRY
            # )
            
            # 这里使用示例Token
            token = f"example_token_{channel_name}_{uid}"
            return token
            
        except Exception as e:
            error(f"生成声网Token失败: {e}")
            return ""
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict]:
        """
        获取通道信息
        
        Args:
            channel_name: 通道名称
            
        Returns:
            Optional[Dict]: 通道信息
        """
        return self.channels.get(channel_name)
    
    def get_client_resource(self, client_id: str) -> Optional[Dict]:
        """
        获取客户端资源
        
        Args:
            client_id: 客户端ID
            
        Returns:
            Optional[Dict]: 客户端资源信息
        """
        return self.client_resources.get(client_id)
    
    @property
    def available_resources(self) -> Dict:
        """
        获取可用资源信息
        
        Returns:
            Dict: 可用资源信息
        """
        total_channels = len(self.channels)
        used_channels = len([
            channel for channel in self.channels.values()
            if len(channel["uids"]) > 0
        ])
        available_channels = total_channels - used_channels
        
        total_uids = sum(channel["max_uids"] for channel in self.channels.values())
        used_uids = sum(len(channel["uids"]) for channel in self.channels.values())
        available_uids = total_uids - used_uids
        
        return {
            "total_channels": total_channels,
            "used_channels": used_channels,
            "available_channels": available_channels,
            "total_uids": total_uids,
            "used_uids": used_uids,
            "available_uids": available_uids
        }
    
    def get_stats(self) -> Dict:
        """
        获取资源统计信息
        
        Returns:
            Dict: 资源统计信息
        """
        stats = {
            "available_resources": self.available_resources,
            "client_count": len(self.client_resources),
            "channels": {}
        }
        
        for channel_name, channel_info in self.channels.items():
            stats["channels"][channel_name] = {
                "uids": channel_info["uids"],
                "max_uids": channel_info["max_uids"],
                "used_uids": len(channel_info["uids"]),
                "available_uids": channel_info["max_uids"] - len(channel_info["uids"])
            }
        
        return stats
