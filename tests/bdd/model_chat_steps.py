"""獨立執行模型啟用與對話歷史的 Gherkin 情境。"""

import os
from uuid import uuid4

import pytest
from pytest_bdd import given, scenarios, then, when

from tests.manual_model_activation import (
    activate_target_model,
    expect_target_model_enabled,
    open_model_management_for_activation,
    open_target_model_chat,
)

scenarios("model_chat.feature")


@pytest.fixture(autouse=True)
def require_model_chat_flags():
    if os.getenv("MODEL_TEST_WRITE") != "I_UNDERSTAND":
        pytest.skip("啟用模型需設定 MODEL_TEST_WRITE=I_UNDERSTAND")
    if os.getenv("MODEL_TEST_CHAT_SEND") != "YES":
        pytest.skip("送出對話需設定 MODEL_TEST_CHAT_SEND=YES")


@given("目標模型已下載且可操作", target_fixture="manager")
def check_model(auth_page):
    return open_model_management_for_activation(auth_page)


@when("我依目前狀態啟用目標模型")
def activate_model(manager):
    activate_target_model(manager)


@then("目標模型應顯示為已啟用")
def check_enabled(manager):
    expect_target_model_enabled(manager)


@when("我選取目標模型並送出一則新對話", target_fixture="sent_chat")
def send_chat(auth_page):
    home = open_target_model_chat(auth_page)
    message = f"自動化測試 {uuid4().hex[:8]}，請只回覆 OK。"
    origin_url = home.send_chat_message(message)
    return home, message, origin_url


@then("應建立新的對話並收到非空白回覆", target_fixture="chat_session_id")
def check_reply(sent_chat):
    home, message, origin_url = sent_chat
    session_id, _ = home.expect_chat_reply(message, origin_url)
    return session_id


@when("我從歷史紀錄重開這則對話")
def reopen_chat(sent_chat, chat_session_id):
    home, _, _ = sent_chat
    home.reopen_chat_history(chat_session_id)


@then("應回到同一則對話並看到原訊息與回覆")
def check_history(sent_chat, chat_session_id):
    home, message, _ = sent_chat
    home.expect_reopened_chat(message, chat_session_id)
