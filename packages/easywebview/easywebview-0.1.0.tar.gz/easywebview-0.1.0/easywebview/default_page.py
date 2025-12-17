from __future__ import annotations

import json
from typing import Any


DEFAULT_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>EasyWebView</title>
  <style>
    :root {
      --bg-color: #f4f7f6;
      --card-bg: #ffffff;
      --accent: #6c5ce7;
      --accent-2: #00b894;
      --danger: #d63031;
      --text-main: #2d3436;
      --text-sub: #636e72;
      --code-bg: #f1f2f6;
      --border: #e6e6e6;
      --shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-main);
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .container {
      background: var(--card-bg);
      width: 100%;
      max-width: 680px;
      padding: 40px;
      border-radius: 24px;
      box-shadow: var(--shadow);
      text-align: center;
      margin: 20px;
      animation: floatUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    @keyframes floatUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .icon {
      font-size: 64px;
      margin-bottom: 12px;
      display: inline-block;
      user-select: none;
    }

    h1 {
      font-size: 28px;
      font-weight: 800;
      margin: 0 0 10px;
      color: var(--text-main);
      letter-spacing: -0.2px;
    }

    p {
      color: var(--text-sub);
      line-height: 1.6;
      margin: 0 0 22px;
      font-size: 16px;
    }

    .divider {
      height: 1px;
      background: var(--border);
      margin: 22px 0;
      border: 0;
    }

    .code-box {
      background: var(--code-bg);
      padding: 16px 16px;
      border-radius: 14px;
      text-align: left;
      border: 1px solid var(--border);
      position: relative;
      user-select: text;
      -webkit-user-select: text;
    }

    .label {
      font-size: 12px;
      color: var(--accent);
      font-weight: 800;
      margin-bottom: 10px;
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }

    .snippet-row {
      display: flex;
      gap: 12px;
      align-items: stretch;
    }

    .usage {
      margin: 0;
      flex: 1;
      padding: 12px 12px;
      border-radius: 12px;
      background: #fff;
      border: 1px solid var(--border);
      font-family: "JetBrains Mono", Consolas, monospace;
      font-size: 13.5px;
      color: #2d3436;
      line-height: 1.35;
      cursor: grab;
      white-space: nowrap;
      overflow: auto;
      user-select: text;
      -webkit-user-select: text;
    }

    .usage:active {
      cursor: grabbing;
    }

    .btn {
      border: 0;
      border-radius: 12px;
      padding: 10px 12px;
      font-weight: 800;
      cursor: pointer;
      transition: transform 0.08s ease, filter 0.12s ease;
      user-select: none;
      -webkit-user-select: none;
      white-space: nowrap;
    }
    .btn:active {
      transform: translateY(1px);
      filter: brightness(0.98);
    }

    .btn-copy {
      background: var(--accent);
      color: #fff;
      min-width: 92px;
    }

    .input-area {
      text-align: left;
      margin-top: 8px;
    }

    .input-title {
      font-size: 12px;
      color: var(--accent-2);
      font-weight: 800;
      margin: 0 0 10px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }

    .input-row {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .url-input {
      flex: 1;
      border: 1px solid var(--border);
      background: #fff;
      padding: 12px 12px;
      border-radius: 12px;
      font-size: 14px;
      outline: none;
    }

    .url-input:focus {
      border-color: rgba(108, 92, 231, 0.6);
      box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.12);
    }

    .btn-go {
      background: var(--accent-2);
      color: #fff;
      min-width: 92px;
    }

    .hint {
      margin: 10px 0 0;
      font-size: 13px;
      color: var(--text-sub);
    }

    code {
      color: var(--danger);
      background: rgba(214, 48, 49, 0.10);
      padding: 2px 6px;
      border-radius: 6px;
    }

    .footer {
      margin-top: 26px;
      font-size: 13px;
      color: #b2bec3;
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 22px;
      transform: translateX(-50%);
      background: rgba(45, 52, 54, 0.92);
      color: #fff;
      padding: 10px 14px;
      border-radius: 999px;
      font-size: 13px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease, transform 0.2s ease;
      box-shadow: var(--shadow);
    }

    .toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(-2px);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">🪐</div>
    <h1>EasyWebView</h1>
    <p id="welcomeText">
      Welcome! You started EasyWebView without a URL.<br>
      Drag or <code>copy</code> the example below and paste it into your terminal.
    </p>

    <div class="code-box">
      <span id="usageLabel" class="label">Usage Example (Drag / Copy)</span>

      <div class="snippet-row">
        <pre id="usageText" class="usage" draggable="true">easywebview --persist --url https://www.google.com</pre>
        <button id="copyBtn" class="btn btn-copy" type="button">Copy</button>
      </div>
    </div>

    <hr class="divider" />

    <div class="input-area">
      <div id="inputTitle" class="input-title">Open URL Manually</div>

      <div class="input-row">
        <input
          id="urlInput"
          class="url-input"
          type="text"
          inputmode="url"
          autocomplete="off"
          spellcheck="false"
          placeholder="e.g. https://example.com or example.com"
        />
        <button id="goBtn" class="btn btn-go" type="button">Open</button>
      </div>

      <p id="hintText" class="hint">
        If there's no scheme, <code>https://</code> is added automatically.
        (Supports <code>http://</code>, <code>https://</code>, <code>file://</code>)
      </p>
    </div>

    <div class="footer">
      Simple Standalone Browser powered by <strong>pywebview</strong>
    </div>
  </div>

  <div id="toast" class="toast" aria-live="polite"></div>

  <script>
    const CONFIG = __EASYWEBVIEW_CONFIG__;

    const I18N = {
      en: {
        welcome:
          "Welcome! You started EasyWebView without a URL.<br>" +
          "Drag or <code>copy</code> the example below and paste it into your terminal.",
        usageLabel: "Usage Example (Drag / Copy)",
        copy: "Copy",
        inputTitle: "Open URL Manually",
        placeholder: "e.g. https://example.com or example.com",
        open: "Open",
        hint:
          "If there's no scheme, <code>https://</code> is added automatically. " +
          "(Supports <code>http://</code>, <code>https://</code>, <code>file://</code>)",
        toastCopied: "Copied to clipboard.",
        toastCopyFailed: "Copy failed. Please select the text and copy manually.",
        toastEnterUrl: "Please enter a URL.",
      },
      ko: {
        welcome:
          "환영합니다! 현재 URL 인자 없이 실행되었습니다.<br>" +
          "아래 예시를 <code>드래그</code>하거나 <code>복사</code>하여 터미널에 붙여넣을 수 있습니다.",
        usageLabel: "사용 예시 (드래그 / 복사)",
        copy: "복사",
        inputTitle: "URL 수동 입력",
        placeholder: "예: https://example.com 또는 example.com",
        open: "열기",
        hint:
          "스킴이 없으면 자동으로 <code>https://</code>를 붙입니다. " +
          "(<code>http://</code>, <code>https://</code>, <code>file://</code> 지원)",
        toastCopied: "클립보드에 복사되었습니다.",
        toastCopyFailed: "복사에 실패했습니다. 텍스트를 직접 선택하여 복사해 주세요.",
        toastEnterUrl: "URL을 입력해 주세요.",
      },
    };

    function detectLang() {
      const raw = (navigator.language || "").toLowerCase();
      return raw.startsWith("ko") ? "ko" : "en";
    }

    function normalizeLang(value) {
      const s = (value || "").toLowerCase();
      if (s === "ko" || s === "en") return s;
      return "";
    }

    const forcedLang = normalizeLang(CONFIG.lang);
    let currentLang = forcedLang || detectLang();

    function t(key) {
      const table = I18N[currentLang] || I18N.en;
      return table[key] || I18N.en[key] || key;
    }

    function applyI18n() {
      document.documentElement.lang = currentLang;
      document.getElementById("welcomeText").innerHTML = t("welcome");
      document.getElementById("usageLabel").textContent = t("usageLabel");
      document.getElementById("copyBtn").textContent = t("copy");
      document.getElementById("inputTitle").textContent = t("inputTitle");
      document.getElementById("urlInput").placeholder = t("placeholder");
      document.getElementById("goBtn").textContent = t("open");
      document.getElementById("hintText").innerHTML = t("hint");
    }

    function showToast(message) {
      const toast = document.getElementById("toast");
      toast.textContent = message;
      toast.classList.add("show");
      window.clearTimeout(showToast._t);
      showToast._t = window.setTimeout(() => {
        toast.classList.remove("show");
      }, 1400);
    }

    function normalizeUrl(raw) {
      const s = (raw || "").trim();
      if (!s) return "";
      const lower = s.toLowerCase();
      if (lower.startsWith("http://") || lower.startsWith("https://") || lower.startsWith("file://")) {
        return s;
      }
      return "https://" + s;
    }

    async function copyToClipboard(text) {
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return true;
        }
      } catch (e) {
        // 무시하고 폴백으로 진행한다.
      }

      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        ta.style.top = "-9999px";
        document.body.appendChild(ta);

        ta.focus();
        ta.select();

        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        return ok;
      } catch (e) {
        return false;
      }
    }

    function selectAllInElement(el) {
      const range = document.createRange();
      range.selectNodeContents(el);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }

    const usageEl = document.getElementById("usageText");
    const copyBtn = document.getElementById("copyBtn");
    const urlInput = document.getElementById("urlInput");
    const goBtn = document.getElementById("goBtn");

    const injectedUsage = (typeof CONFIG.usageExample === "string" && CONFIG.usageExample.trim())
      ? CONFIG.usageExample.trim()
      : "";
    if (injectedUsage) {
      usageEl.textContent = injectedUsage;
    }

    applyI18n();

    usageEl.addEventListener("dragstart", (ev) => {
      try {
        ev.dataTransfer.setData("text/plain", usageEl.textContent);
        ev.dataTransfer.effectAllowed = "copy";
      } catch (e) {
        // 일부 환경에서는 dataTransfer 접근이 제한될 수 있다.
      }
    });

    usageEl.addEventListener("click", () => {
      selectAllInElement(usageEl);
    });

    copyBtn.addEventListener("click", async () => {
      const text = usageEl.textContent || "";
      const ok = await copyToClipboard(text);

      if (ok) {
        showToast(t("toastCopied"));
      } else {
        showToast(t("toastCopyFailed"));
        selectAllInElement(usageEl);
      }
    });

    goBtn.addEventListener("click", () => {
      const raw = urlInput.value;
      const url = normalizeUrl(raw);

      if (!url) {
        showToast(t("toastEnterUrl"));
        urlInput.focus();
        return;
      }

      window.location.href = url;
    });

    urlInput.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        goBtn.click();
      }
    });
  </script>
</body>
</html>
"""


def _json_for_html(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/")


def render_default_html(*, usage_example: str, lang: str = "auto") -> str:
    lang_norm = (lang or "auto").lower()
    if lang_norm not in ("auto", "ko", "en"):
        lang_norm = "auto"

    config_json = _json_for_html(
        {
            "lang": lang_norm,
            "usageExample": usage_example,
        }
    )
    return DEFAULT_HTML_TEMPLATE.replace("__EASYWEBVIEW_CONFIG__", config_json)


DEFAULT_HTML = render_default_html(
    usage_example="easywebview --persist --url https://www.google.com",
    lang="auto",
)
