#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误上报模块

@author wangzhong

功能：
1. 采集 Hook 执行和 API 调用的错误
2. 脱敏处理后上报到服务端
3. 支持采样率控制和防循环保护

设计原则：
- 轻量级：不影响主流程性能
- 脱敏：不上报敏感信息（文件路径、内容等）
- 防循环：上报失败不再上报
- 快速失败：3秒超时
"""

import os
import re
import uuid
import random
import logging
import hashlib
import platform
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import requests

logger = logging.getLogger(__name__)


# ============================================================================
# 错误类型枚举
# ============================================================================

class ErrorType(str, Enum):
    """错误类型枚举"""

    # 网络层错误
    CONNECTION_ERROR = "connection_error"      # 网络不可达
    TIMEOUT_ERROR = "timeout_error"            # 请求超时
    DNS_ERROR = "dns_error"                    # DNS 解析失败
    SSL_ERROR = "ssl_error"                    # SSL/TLS 错误

    # HTTP 层错误
    AUTH_ERROR = "auth_error"                  # 401/403 认证失败
    VALIDATION_ERROR = "validation_error"      # 400 参数错误
    NOT_FOUND_ERROR = "not_found_error"        # 404 资源不存在
    SERVER_ERROR = "server_error"              # 5xx 服务器错误

    # 业务层错误
    BUSINESS_ERROR = "business_error"          # 业务逻辑错误

    # 客户端错误
    PARSE_ERROR = "parse_error"                # JSON 解析失败
    CONFIG_ERROR = "config_error"              # 配置错误
    FILE_ERROR = "file_error"                  # 文件读写错误
    HOOK_ERROR = "hook_error"                  # Hook 执行错误

    # 未知错误
    UNKNOWN_ERROR = "unknown_error"


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class ErrorLog:
    """
    错误日志数据结构（脱敏设计）

    字段说明：
    - error_id: 唯一ID，用于去重
    - error_type: 错误类型枚举值
    - error_code: HTTP状态码或业务错误码
    - error_message: 脱敏后的错误消息（限制200字符）
    - hook_name: 触发的 Hook 名称
    - api_endpoint: 调用的 API 端点
    - http_method: HTTP 方法
    - client_version: devlake-mcp 版本
    - ide_type: IDE 类型（claude_code/cursor）
    - os_type: 操作系统类型
    - python_version: Python 版本
    - user_hash: 用户邮箱的 SHA256 前8位（脱敏）
    - project_hash: 项目路径的 SHA256 前8位（脱敏）
    - occurred_at: 发生时间
    - retry_count: 重试次数
    - request_duration_ms: 请求耗时（毫秒）
    """
    error_id: str
    error_type: str
    error_code: Optional[int]
    error_message: str
    hook_name: str
    api_endpoint: str
    http_method: str
    client_version: str
    ide_type: str
    os_type: str
    python_version: str
    user_hash: str
    project_hash: str
    occurred_at: str
    retry_count: int
    request_duration_ms: Optional[int] = None


# ============================================================================
# 错误上报器
# ============================================================================

class ErrorReporter:
    """
    错误上报器

    特性：
    - 采样率控制：默认 100%，可配置
    - 防循环保护：上报失败不再上报
    - 快速失败：3秒超时
    - 静默失败：不影响主流程
    """

    # 类级别标记：防止递归上报
    _is_reporting = False

    def __init__(
        self,
        base_url: Optional[str] = None,
        sample_rate: Optional[float] = None,
        enabled: Optional[bool] = None
    ):
        """
        初始化错误上报器

        Args:
            base_url: API 基础 URL
            sample_rate: 采样率 (0.0 ~ 1.0)，默认 1.0 (100%)
            enabled: 是否启用，默认 True
        """
        from .constants import (
            get_error_report_enabled,
            get_error_sample_rate,
            get_error_report_timeout
        )

        self.base_url = base_url or os.getenv(
            'DEVLAKE_BASE_URL',
            'http://devlake.test.chinawayltd.com'
        )
        self.sample_rate = sample_rate if sample_rate is not None else get_error_sample_rate()
        self.enabled = enabled if enabled is not None else get_error_report_enabled()
        self.timeout = get_error_report_timeout()

    def report(
        self,
        error: Exception,
        hook_name: str,
        api_endpoint: str = "",
        http_method: str = "",
        ide_type: str = "claude_code",
        user_email: str = "",
        project_path: str = "",
        retry_count: int = 0,
        request_duration_ms: Optional[int] = None
    ) -> bool:
        """
        上报错误

        Args:
            error: 异常对象
            hook_name: Hook 名称（如 session_start, post_tool_use）
            api_endpoint: API 端点（如 /api/ai-coding/sessions）
            http_method: HTTP 方法（GET/POST/PATCH 等）
            ide_type: IDE 类型（claude_code/cursor）
            user_email: 用户邮箱（会脱敏为 hash）
            project_path: 项目路径（会脱敏为 hash）
            retry_count: 重试次数（0 = 首次失败）
            request_duration_ms: 请求耗时（毫秒）

        Returns:
            bool: 上报成功返回 True
        """
        # 1. 检查开关
        if not self.enabled:
            return False

        # 2. 防循环保护
        if ErrorReporter._is_reporting:
            logger.debug("跳过上报：正在上报中（防循环）")
            return False

        # 3. 采样率控制
        if random.random() > self.sample_rate:
            logger.debug(f"跳过上报：采样率 {self.sample_rate}")
            return False

        try:
            ErrorReporter._is_reporting = True

            # 4. 构造错误日志
            error_log = self._build_error_log(
                error=error,
                hook_name=hook_name,
                api_endpoint=api_endpoint,
                http_method=http_method,
                ide_type=ide_type,
                user_email=user_email,
                project_path=project_path,
                retry_count=retry_count,
                request_duration_ms=request_duration_ms
            )

            # 5. 上报
            return self._send(error_log)

        except Exception as e:
            # 上报失败静默处理，不记录日志避免死循环
            logger.debug(f"错误上报失败（静默处理）: {e}")
            return False
        finally:
            ErrorReporter._is_reporting = False

    def _build_error_log(
        self,
        error: Exception,
        hook_name: str,
        api_endpoint: str,
        http_method: str,
        ide_type: str,
        user_email: str,
        project_path: str,
        retry_count: int,
        request_duration_ms: Optional[int]
    ) -> ErrorLog:
        """构造错误日志（含脱敏）"""
        from .version_utils import get_devlake_mcp_version

        return ErrorLog(
            error_id=str(uuid.uuid4()),
            error_type=self._classify_error(error),
            error_code=self._extract_error_code(error),
            error_message=self._sanitize_message(str(error)),
            hook_name=hook_name,
            api_endpoint=api_endpoint,
            http_method=http_method,
            client_version=get_devlake_mcp_version(),
            ide_type=ide_type,
            os_type=platform.system().lower(),
            python_version=platform.python_version(),
            user_hash=self._hash_value(user_email),
            project_hash=self._hash_value(project_path),
            occurred_at=datetime.utcnow().isoformat() + 'Z',
            retry_count=retry_count,
            request_duration_ms=request_duration_ms
        )

    def _classify_error(self, error: Exception) -> str:
        """
        错误分类

        根据异常类名自动分类错误类型
        """
        error_type_name = type(error).__name__

        # 基于异常类名匹配
        mapping = {
            # DevLake 自定义异常
            'DevLakeConnectionError': ErrorType.CONNECTION_ERROR,
            'DevLakeTimeoutError': ErrorType.TIMEOUT_ERROR,
            'DevLakeAuthError': ErrorType.AUTH_ERROR,
            'DevLakeValidationError': ErrorType.VALIDATION_ERROR,
            'DevLakeNotFoundError': ErrorType.NOT_FOUND_ERROR,
            'DevLakeServerError': ErrorType.SERVER_ERROR,
            'DevLakeBusinessError': ErrorType.BUSINESS_ERROR,
            'DevLakeAPIError': ErrorType.UNKNOWN_ERROR,
            # Python 标准异常
            'ConnectionError': ErrorType.CONNECTION_ERROR,
            'Timeout': ErrorType.TIMEOUT_ERROR,
            'SSLError': ErrorType.SSL_ERROR,
            'JSONDecodeError': ErrorType.PARSE_ERROR,
            'FileNotFoundError': ErrorType.FILE_ERROR,
            'PermissionError': ErrorType.FILE_ERROR,
            'IOError': ErrorType.FILE_ERROR,
            'OSError': ErrorType.FILE_ERROR,
            'ValueError': ErrorType.VALIDATION_ERROR,
            'KeyError': ErrorType.VALIDATION_ERROR,
            'TypeError': ErrorType.VALIDATION_ERROR,
        }

        return mapping.get(error_type_name, ErrorType.UNKNOWN_ERROR).value

    def _extract_error_code(self, error: Exception) -> Optional[int]:
        """
        提取错误码

        优先从异常对象的 code 属性提取，
        其次从错误消息中提取 HTTP 状态码
        """
        # 从 DevLakeBusinessError 等提取 code 属性
        if hasattr(error, 'code') and error.code is not None:
            return error.code

        # 从错误消息中提取 HTTP 状态码（4xx/5xx）
        error_str = str(error)
        match = re.search(r'\b([45]\d{2})\b', error_str)
        if match:
            return int(match.group(1))

        return None

    def _sanitize_message(self, message: str, max_length: int = 200) -> str:
        """
        脱敏错误消息

        移除敏感信息：
        - 文件路径
        - API Token
        - 密码
        - API Key
        """
        # 移除文件路径（Unix 和 Windows）
        message = re.sub(r'/[^\s:]+', '[PATH]', message)
        message = re.sub(r'[A-Za-z]:\\[^\s:]+', '[PATH]', message)

        # 移除可能的敏感信息
        message = re.sub(r'token[=:]\s*\S+', 'token=[REDACTED]', message, flags=re.I)
        message = re.sub(r'password[=:]\s*\S+', 'password=[REDACTED]', message, flags=re.I)
        message = re.sub(r'api[_-]?key[=:]\s*\S+', 'api_key=[REDACTED]', message, flags=re.I)
        message = re.sub(r'secret[=:]\s*\S+', 'secret=[REDACTED]', message, flags=re.I)
        message = re.sub(r'bearer\s+\S+', 'Bearer [REDACTED]', message, flags=re.I)

        # 移除邮箱地址
        message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', message)

        # 限制长度
        if len(message) > max_length:
            message = message[:max_length] + '...'

        return message

    def _hash_value(self, value: str) -> str:
        """
        哈希脱敏

        将敏感值转换为 SHA256 的前8位
        """
        if not value:
            return "unknown"
        return hashlib.sha256(value.encode()).hexdigest()[:8]

    def _send(self, error_log: ErrorLog) -> bool:
        """
        发送错误日志到服务端

        使用批量上报接口，支持幂等性
        """
        try:
            url = f"{self.base_url}/api/ai-coding/error-logs"
            response = requests.post(
                url,
                json={"logs": [asdict(error_log)]},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.debug(f"错误上报成功: {error_log.error_id}")
                return True
            else:
                logger.debug(f"错误上报失败: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"错误上报请求失败: {e}")
            return False


# ============================================================================
# 全局单例和便捷函数
# ============================================================================

_reporter: Optional[ErrorReporter] = None


def get_error_reporter() -> ErrorReporter:
    """获取全局错误上报器（单例）"""
    global _reporter
    if _reporter is None:
        _reporter = ErrorReporter()
    return _reporter


def report_error(
    error: Exception,
    hook_name: str,
    api_endpoint: str = "",
    http_method: str = "",
    ide_type: str = "claude_code",
    user_email: str = "",
    project_path: str = "",
    retry_count: int = 0,
    request_duration_ms: Optional[int] = None
) -> bool:
    """
    便捷函数：上报错误

    使用全局单例上报器，适合在 Hook 中快速调用。

    示例：
        try:
            client.create_session(data)
        except Exception as e:
            report_error(
                error=e,
                hook_name='session_start',
                api_endpoint='/api/ai-coding/sessions',
                http_method='POST',
                ide_type='claude_code',
                user_email=git_email,
                project_path=git_repo_path
            )
    """
    return get_error_reporter().report(
        error=error,
        hook_name=hook_name,
        api_endpoint=api_endpoint,
        http_method=http_method,
        ide_type=ide_type,
        user_email=user_email,
        project_path=project_path,
        retry_count=retry_count,
        request_duration_ms=request_duration_ms
    )
