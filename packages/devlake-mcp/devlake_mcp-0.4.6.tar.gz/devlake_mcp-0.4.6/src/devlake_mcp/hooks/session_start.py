#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话启动时记录会话信息（SessionStart Hook）

功能：
1. 调用 session_manager.start_new_session() 强制开始新会话
   - SessionStart 语义：明确的"新会话开始"信号
   - 无论如何都会结束旧会话并创建新会话（即使 session_id 相同）
2. 同步执行，确保会话创建成功后才继续
3. 失败时输出错误到 stderr 并返回 exit code 2

注意：
- 使用 start_new_session 而非 check_and_switch_session
- SessionStart = 强制新建，UserPromptSubmit = 智能判断
- 即使 SessionStart 未触发，UserPromptSubmit 也会创建 session（容错）
- 错误时会向用户显示提示信息（通过 stderr 和 exit 2）

@author wangzhong
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# 导入公共工具（使用包导入）
from devlake_mcp.enums import IDEType
from devlake_mcp.session_manager import start_new_session
from devlake_mcp.generation_manager import cleanup_old_generation_files
from devlake_mcp.logging_config import configure_logging, get_log_dir
from devlake_mcp.hooks.transcript_utils import safe_parse_hook_input
from devlake_mcp.constants import HOOK_LOG_DIR
from devlake_mcp.client import (
    DevLakeAPIError,
    DevLakeConnectionError,
    DevLakeTimeoutError,
    DevLakeAuthError
)
from devlake_mcp.retry_queue import save_failed_upload
from devlake_mcp.error_reporter import report_error

# 配置日志（启动时调用一次）
configure_logging(log_dir=get_log_dir(HOOK_LOG_DIR), log_file='session_start.log')
logger = logging.getLogger(__name__)


def main():
    """
    SessionStart Hook 主逻辑（同步执行）

    错误处理策略：
    - 解析错误、配置错误、认证错误：输出 stderr + exit 2（阻止会话启动）
    - 网络临时错误：保存到队列，记录日志但继续（不影响用户使用）
    - API 错误：保存到队列，输出 stderr + exit 2
    """
    session_id = None  # 用于错误日志和队列
    cwd = None  # 用于队列

    try:
        # 1. 清理超过 7 天的历史 generation 状态文件（防止文件堆积）
        try:
            cleanup_old_generation_files(max_age_days=7)
        except Exception as e:
            # 清理失败不影响会话启动
            logger.warning(f'清理历史文件失败: {e}')

        # 2. 从 stdin 读取 hook 输入（使用安全解析函数）
        input_data = safe_parse_hook_input(logger)
        if not input_data:
            # 解析失败 - 这是严重错误
            sys.stderr.write('⚠️  DevLake SessionStart 错误: 无法解析 hook 输入\n')
            sys.stderr.write('   详细日志: ~/.devlake/logs/session_start.log\n')
            sys.stderr.flush()
            logger.error('无法解析 hook 输入数据')
            sys.exit(2)

        session_id = input_data.get('session_id')
        if not session_id:
            sys.stderr.write('⚠️  DevLake SessionStart 错误: 缺少 session_id\n')
            sys.stderr.flush()
            logger.warning('缺少 session_id')
            sys.exit(2)

        # 打印完整的 input_data 用于调试
        logger.info(f'SessionStart Hook 触发 - session: {session_id}')
        logger.debug(f'收到的 input_data: {json.dumps(input_data, ensure_ascii=False, indent=2)}')

        # 3. 获取项目信息
        # 注意：如果 cwd 是空字符串，也应该使用 os.getcwd()
        raw_cwd = input_data.get('cwd')
        logger.debug(f'input_data 中的 cwd 原始值: {repr(raw_cwd)}')

        cwd = raw_cwd or os.getcwd()
        logger.debug(f'最终使用的 cwd: {cwd}')

        # 4. 强制开始新会话（SessionStart 语义 = 新会话开始）
        start_new_session(
            session_id=session_id,
            cwd=cwd,
            ide_type=IDEType.CLAUDE_CODE
        )
        logger.info(f'SessionStart 完成 - session: {session_id}')

    except DevLakeAuthError as e:
        # 认证错误 - 阻止会话启动
        error_msg = f'DevLake 认证失败: {e}'
        sys.stderr.write(f'⚠️  {error_msg}\n')
        sys.stderr.write(f'   检查配置: ~/.devlake/config.json\n')
        sys.stderr.write(f'   详细日志: ~/.devlake/logs/session_start.log\n')
        sys.stderr.flush()
        logger.error(error_msg, exc_info=True)
        # 上报错误到服务端
        report_error(
            error=e,
            hook_name='session_start',
            api_endpoint='/api/ai-coding/sessions',
            http_method='POST',
            ide_type='claude_code'
        )
        sys.exit(2)

    except (DevLakeConnectionError, DevLakeTimeoutError) as e:
        # 网络错误 - 提示用户，保存到队列，但不阻止启动
        error_msg = f'DevLake 网络错误（会话数据将延迟上传）: {e}'
        sys.stderr.write(f'⚠️  {error_msg}\n')
        sys.stderr.write(f'   详细日志: ~/.devlake/logs/session_start.log\n')
        sys.stderr.flush()
        logger.warning(error_msg)

        # 上报错误到服务端
        report_error(
            error=e,
            hook_name='session_start',
            api_endpoint='/api/ai-coding/sessions',
            http_method='POST',
            ide_type='claude_code'
        )

        # 保存失败的 session 创建请求到队列
        if session_id and cwd:
            save_failed_upload(
                queue_type='session',
                data={
                    'session_id': session_id,
                    'cwd': cwd,
                    'ide_type': 'claude_code'
                },
                error=str(e)
            )
        sys.exit(2)

    except DevLakeAPIError as e:
        # 其他 API 错误 - 保存到队列，但阻止会话启动
        error_msg = f'DevLake API 错误: {e}'
        sys.stderr.write(f'⚠️  {error_msg}\n')
        sys.stderr.write(f'   详细日志: ~/.devlake/logs/session_start.log\n')
        sys.stderr.flush()
        logger.error(error_msg, exc_info=True)

        # 上报错误到服务端
        report_error(
            error=e,
            hook_name='session_start',
            api_endpoint='/api/ai-coding/sessions',
            http_method='POST',
            ide_type='claude_code'
        )

        # 保存到队列供后续重试
        if session_id and cwd:
            save_failed_upload(
                queue_type='session',
                data={
                    'session_id': session_id,
                    'cwd': cwd,
                    'ide_type': 'claude_code'
                },
                error=str(e)
            )

        sys.exit(2)

    except Exception as e:
        # 未知错误 - 阻止会话启动
        error_msg = f'SessionStart Hook 执行失败: {e}'
        sys.stderr.write(f'⚠️  {error_msg}\n')
        sys.stderr.write(f'   详细日志: ~/.devlake/logs/session_start.log\n')
        sys.stderr.flush()
        logger.error(error_msg, exc_info=True)
        # 上报错误到服务端
        report_error(
            error=e,
            hook_name='session_start',
            ide_type='claude_code'
        )
        sys.exit(2)


if __name__ == '__main__':
    main()
    # 失败的请求已保存到队列，由其他异步 hook（PostToolUse 等）自动重试
    sys.exit(0)  # 唯一的 exit 点
