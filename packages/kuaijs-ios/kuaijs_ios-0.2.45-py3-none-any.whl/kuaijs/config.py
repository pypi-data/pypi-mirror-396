from typing import Any, Dict, Optional


def readConfigInt(key: str) -> int:
    """读取整数配置

    参数:
      key: 配置键
    返回:
      int: 配置值
    """
    return 0


def readConfigDouble(key: str) -> float:
    """读取浮点配置"""
    return 0.0


def readConfigString(key: str) -> Optional[str]:
    """读取字符串配置（不存在返回 None）"""
    return None


def readConfigBool(key: str) -> bool:
    """读取布尔配置"""
    return False


def getConfigJSON() -> Dict[str, Any]:
    """获取所有配置 JSON"""
    return {}


def updateConfig(key: str, value: Any) -> bool:
    """更新配置值（支持 str/int/float/bool）"""
    return True


def deleteConfig(key: str) -> bool:
    """删除配置"""
    return True
