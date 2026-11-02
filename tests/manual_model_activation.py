"""第二階段：模型停用／啟用／Chat 驗證（必須手動指定檔案執行）。

檔案刻意命名為 manual_ 開頭，讓一般 `pytest -v` 不會收集。
預設只執行不改變服務狀態的 preflight；寫入測試需要明確環境變數。
MODEL_TEST_ALLOW_RETRY=YES 可在啟用回退或逾時後，確認狀態並最多重試一次。
首次異常保留在 reports/model_activation/enable_attempts.log。
MODEL_TEST_CHAT_SEND=YES 才會送出一則測試訊息，並驗證回覆與歷史紀錄。
"""
from __future__ import annotations

import os
import json
import time
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pytest
from playwright.sync_api import Page

from pages.platform_manager_page import PlatformManagerPage
from pages.user_home_page import UserHomePage


TARGET_MODEL = "Llama3.1-FFM-8B"  # 本次限定的 LLM；不批次操作其他模型
MODEL_ENABLE_TIMEOUT_SECONDS = 600
MODEL_DISABLED_GRACE_SECONDS = 20
MODEL_DISABLE_TIMEOUT_SECONDS = 90
MODEL_RETRY_CONFIRM_SECONDS = 10


class ModelEnableFallback(AssertionError):
    """啟用後持續顯示未啟用；允許明確授權的一次重試。"""


class ModelEnableTimeout(AssertionError):
    """啟用等待到期，必須再次確認狀態才可重試。"""


def _record_activation_event(event: str, state: str) -> None:
    folder = Path("reports/model_activation")
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    with (folder / "enable_attempts.log").open("a", encoding="utf-8") as stream:
        stream.write(f"{now}\t{TARGET_MODEL}\t{event}\tstate={state}\n")
    print(f"模型啟用嘗試紀錄：{event}，狀態={state}")


def _record_failure(page: Page) -> None:
    """失敗時留截圖與有限的頁面狀態；URL 不含查詢參數或身分資訊。"""
    try:
        parsed = urlsplit(page.url)
        host = parsed.hostname or ""
        if ":" in host:
            host = f"[{host}]"  # IPv6
        authority = host + (f":{parsed.port}" if parsed.port is not None else "")
        safe_url = urlunsplit((parsed.scheme, authority, parsed.path, "", ""))
        print(f"\n失敗頁面 URL（已移除查詢參數與片段）：{safe_url}")
        if "/protocol/openid-connect/auth" in parsed.path:
            print("失敗頁面位於登入授權路徑，請檢查驗證導向與登入狀態。")
    except Exception as exc:
        print(f"\n無法取得失敗頁面 URL：{type(exc).__name__}")

    try:
        info = page.locator("html").evaluate(
            "(element) => ({ title: document.title, readyState: document.readyState })",
            timeout=3_000,
        )
        print(f"失敗頁面標題：{info['title']!r}")
        print(f"失敗頁面載入狀態：{info['readyState']}")
    except Exception as exc:
        print(f"無法取得頁面標題／載入狀態：{type(exc).__name__}")

    path = Path("reports/model_activation")
    path.mkdir(parents=True, exist_ok=True)
    filename = path / "model_activation_failure.png"
    try:
        page.screenshot(path=str(filename), full_page=True, timeout=10000)
        print(f"\n已保存失敗截圖：{filename}")
    except Exception as exc:
        print(f"\n截圖失敗（不覆蓋原測試錯誤）：{type(exc).__name__}")


def _wait_for_downloaded_state(manager: PlatformManagerPage) -> None:
    deadline = time.monotonic() + MODEL_DISABLE_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        state = manager.model_state(TARGET_MODEL)
        if state == "downloaded_disabled":
            return
        if state == "not_downloaded":
            raise AssertionError("停用後模型變成未下載，停止測試")
        time.sleep(0.6)
    raise AssertionError("等待模型停用逾時，未回到『已下載，未啟用』")


def _wait_for_model_enabled(manager: PlatformManagerPage) -> None:
    """只點一次啟用：區分成功、回復未啟用及一直卡在啟用中。"""
    deadline = time.monotonic() + MODEL_ENABLE_TIMEOUT_SECONDS
    seen_enabling = False
    disabled_since = None
    last_state = None
    seen_snackbar = set()
    last_progress = time.monotonic()

    while time.monotonic() < deadline:
        state = manager.model_state(TARGET_MODEL)
        if state != last_state:
            print(f"模型狀態：{state}")
            last_state = state
        for message in manager.visible_snackbar_messages():
            if message not in seen_snackbar:
                print(f"Snackbar／提示訊息：{message}")
                seen_snackbar.add(message)

        now = time.monotonic()
        if now - last_progress >= 10:
            remaining = max(0, deadline - now)
            print(f"仍在等待模型啟用：目前 {state}，最多再等 {remaining:.0f} 秒")
            last_progress = now
        if state == "enabling":
            seen_enabling = True
            disabled_since = None
        elif state == "enabled":
            return
        elif state == "downloaded_disabled":
            if disabled_since is None:
                disabled_since = time.monotonic()
            # 允許頁面短暫顯示未啟用，避免單次狀態閃爍導致誤判。
            # 若持續未啟用，代表部署並未進入成功狀態，提早報錯。
            if time.monotonic() - disabled_since >= MODEL_DISABLED_GRACE_SECONDS:
                if seen_enabling:
                    raise ModelEnableFallback(
                        "模型曾進入啟用中，但連續 20 秒顯示『已下載，未啟用』；"
                        "可能部署失敗，請查操作紀錄／後端日誌"
                    )
                raise ModelEnableFallback("點擊啟用後連續 20 秒未觀察到進度或成功狀態")
        elif state == "not_downloaded":
            raise AssertionError("啟用過程中模型變成『未下載』")
        elif state in {"disabling", "downloading"}:
            disabled_since = None
        else:
            raise AssertionError(f"啟用過程中出現未預期狀態：{state}")

        time.sleep(0.6)

    raise ModelEnableTimeout(
        f"模型啟用等待超過 {MODEL_ENABLE_TIMEOUT_SECONDS} 秒；"
        "請查看 Hub 服務狀態與錯誤紀錄"
    )


def _wait_enabled_with_optional_retry(manager: PlatformManagerPage) -> None:
    """首次回退保留紀錄；MODEL_TEST_ALLOW_RETRY=YES 才最多再點一次。"""
    print("模型重試：" + (
        f"已開啟；未啟用持續 {MODEL_DISABLED_GRACE_SECONDS} 秒後檢查，最多重試一次。"
        if os.getenv("MODEL_TEST_ALLOW_RETRY") == "YES"
        else "未開啟；第一輪異常後不會第二次點擊啟用。"
    ))
    try:
        _wait_for_model_enabled(manager)
        return
    except (ModelEnableFallback, ModelEnableTimeout) as exc:
        state = manager.model_state(TARGET_MODEL)
        event = "attempt_1_fallback" if isinstance(exc, ModelEnableFallback) else "attempt_1_timeout"
        _record_activation_event(event, state)
        print(f"第一輪啟用異常：{exc}；即使重試成功，此紀錄仍保留。")
        if os.getenv("MODEL_TEST_ALLOW_RETRY") != "YES":
            print("未開啟 MODEL_TEST_ALLOW_RETRY=YES，不會再次點擊啟用。")
            raise

    if state == "enabled":
        _record_activation_event("enabled_before_retry", state)
        return
    if state != "downloaded_disabled":
        raise AssertionError(f"拒絕重試：模型狀態為 {state}，不是已下載未啟用")
    print(f"已授權一次重試；等待 {MODEL_RETRY_CONFIRM_SECONDS} 秒確認狀態。")
    confirmation_deadline = time.monotonic() + MODEL_RETRY_CONFIRM_SECONDS
    while True:
        state = manager.model_state(TARGET_MODEL)
        if state == "enabled":
            _record_activation_event("enabled_during_retry_confirmation", state)
            return
        if state != "downloaded_disabled":
            raise AssertionError(f"拒絕重試：確認期間模型狀態變為 {state}")
        if time.monotonic() >= confirmation_deadline:
            break
        time.sleep(0.6)
    if manager.other_running_models(TARGET_MODEL):
        raise AssertionError("拒絕重試：目前有其他已啟用或操作中的模型")
    # 再次核對寫入授權與狀態；不重試未知錯誤或仍在啟用中的服務。
    if os.getenv("MODEL_TEST_WRITE") != "I_UNDERSTAND":
        raise AssertionError("拒絕重試：模型寫入授權已失效")
    state = manager.model_state(TARGET_MODEL)
    if state != "downloaded_disabled":
        raise AssertionError(f"拒絕重試：點擊前模型狀態變為 {state}")
    manager.click_model_action(TARGET_MODEL, "啟用")
    _record_activation_event("attempt_2_clicked", state)
    try:
        _wait_for_model_enabled(manager)
    except (ModelEnableFallback, ModelEnableTimeout):
        _record_activation_event("attempt_2_failed", manager.model_state(TARGET_MODEL))
        raise
    _record_activation_event("attempt_2_enabled", "enabled")


@pytest.mark.auth
def test_model_activation_preflight(authenticated_page: Page) -> None:
    """安全的唯讀檢查：先確認模型存在、狀態與其他正在啟用的模型。"""
    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_model_management()

    state = manager.model_state(TARGET_MODEL)
    other_models = manager.other_running_models(TARGET_MODEL)
    print(f"\n模型：{TARGET_MODEL}")
    print(f"目前狀態：{state}")
    print(f"其他已啟用或操作中模型：{other_models or '無'}")
    print("此測試沒有點擊啟用或停用，也沒有下載模型。")


@pytest.mark.auth
def test_model_activation_and_chat(authenticated_page: Page) -> None:
    """操作指定模型與 Chat UI；MODEL_TEST_CHAT_SEND=YES 時另送出一則訊息。"""
    if os.getenv("MODEL_TEST_WRITE") != "I_UNDERSTAND":
        pytest.skip("操作測試預設關閉，需設定 MODEL_TEST_WRITE=I_UNDERSTAND")

    manager = PlatformManagerPage(authenticated_page)
    manager.goto()
    manager.open_model_management()

    state = manager.model_state(TARGET_MODEL)
    other_models = manager.other_running_models(TARGET_MODEL)
    if other_models:
        pytest.skip(f"有其他已啟用／操作中的模型，不干擾現有服務：{other_models}")

    if state == "not_downloaded":
        pytest.skip("目標模型尚未下載；本測試不自動下載大型檔案")
    if state in {"downloading", "enabling", "disabling"}:
        pytest.skip(f"模型正在處理中（{state}），不重複操作")
    if state not in {"enabled", "downloaded_disabled"}:
        pytest.fail(f"無法從這個模型狀態安全地啟用：{state}")

    try:
        if state == "enabled" and os.getenv("MODEL_TEST_ALLOW_DISABLE") != "YES":
            print("模型已啟用，未授權停用；直接驗證 Chat UI。")
        else:
            if state == "enabled":
                print(f"\n準備停用指定模型：{TARGET_MODEL}")
                manager.click_model_action(TARGET_MODEL, "停用")
                _wait_for_downloaded_state(manager)

            # 啟用前再次檢查狀態，防止等待期間被其他使用者改動。
            assert manager.model_state(TARGET_MODEL) == "downloaded_disabled", (
                "啟用前模型不是『已下載，未啟用』，停止操作"
            )
            assert not manager.other_running_models(TARGET_MODEL), (
                "目前存在其他已啟用模型，停止操作"
            )
            print(f"\n準備啟用指定模型：{TARGET_MODEL}")
            manager.click_model_action(TARGET_MODEL, "啟用")
            _wait_enabled_with_optional_retry(manager)

        assert manager.model_state(TARGET_MODEL) == "enabled", (
            "Chat 驗證前模型已非啟用狀態，停止操作"
        )

        home = UserHomePage(authenticated_page)
        home.goto()
        home.expect_loaded(timeout_ms=100_000)
        home.select_chat_model(TARGET_MODEL)
        home.expect_chat_text_can_be_entered()
        print("模型已啟用，Chat 模型可選取且可輸入文字（未送出訊息）。")
        if os.getenv("MODEL_TEST_CHAT_SEND") == "YES":
            token = uuid4().hex[:8]
            prompt = f"自動化測試 {token}，請只回覆 OK。"
            evidence = home.send_chat_and_expect_reply(prompt)
            evidence.update(model=TARGET_MODEL, prompt=prompt,
                            verified_at=datetime.now().astimezone().isoformat(timespec="seconds"))
            folder = Path("reports/model_chat")
            folder.mkdir(parents=True, exist_ok=True)
            artifact = folder / f"chat_{token}.json"
            artifact.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            print(f"Chat 送出與歷史紀錄驗證通過；證據：{artifact}")
        else:
            print("未要求 MODEL_TEST_CHAT_SEND=YES，本輪只驗證輸入，不送出對話。")
    except Exception:
        _record_failure(authenticated_page)
        raise
