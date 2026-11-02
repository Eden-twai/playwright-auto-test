from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
# 自動模式用整輪執行器指定的獨立檔案；未指定時保留既有操作方式。
AUTH_STATE = Path(os.environ.get("AI_HUB_AUTH_STATE") or PROJECT_ROOT / ".auth" / "user.json")


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://202.5.254.27/").rstrip("/")


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], base_url: str
) -> dict[str, Any]:
    options = {
        **browser_context_args,
        "base_url": base_url,
        "ignore_https_errors": True,
        "locale": "zh-TW",
        "viewport": {"width": 1440, "height": 900},
    }

    if AUTH_STATE.exists():
        options["storage_state"] = str(AUTH_STATE)

    return options


@pytest.fixture
def authenticated_page(page: Page) -> Page:
    if not AUTH_STATE.exists():
        pytest.skip(
            "尚未建立登入狀態；請執行 scripts/save_login_state.py，或用 run_validation.py --auto-login"
        )
    return page
