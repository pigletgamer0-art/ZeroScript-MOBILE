# ZeroScript Studio — Android (Safe Mode)

ZeroScript Studio is currently built in **Safe Mode** to protect provider accounts.

## What Safe Mode does
- Opens ChatGPT, DeepSeek, Gemini, Qwen and the other configured provider pages for manual use.
- Keeps the provider selector, Android layout, Mobile Studio companion and plugin export.
- Does **not** inject JavaScript into AI pages, inspect chat DOM, hide messages, send prompts, replay turns, detect-and-retry CAPTCHA challenges, or dispatch MCP commands from a personal web session.
- Does not disguise Android WebView's user-agent. Use **⋮ → Abrir en navegador del sistema** when a provider works better in Chrome or another supported browser.

## Why automation is disabled
The previous implementation controlled consumer AI websites by injecting scripts and simulating page interactions. That can trigger anti-abuse systems and may conflict with provider terms. Safe Mode removes that automation path rather than trying to disguise it.

## Re-enabling automation
Do not re-enable website automation. Future automatic AI connections should be implemented as separate adapters for each provider's official API, with:
- user-supplied API credentials stored securely on-device;
- explicit provider selection and clear usage/cost limits;
- request timeouts, bounded retries and rate-limit handling;
- no reuse of browser cookies or personal web sessions;
- user confirmation before MCP tools perform external actions.

An official API integration reduces the risk associated with browser automation, but no software can guarantee that an account will never be restricted. Users must still follow each provider's terms and usage policies.

## Build the APK
1. Push changes to this repository or run **Build APK** from GitHub Actions.
2. Open the successful workflow run.
3. Download the **ZeroScriptStudio-apk** artifact. It contains `app-debug.apk`.

The protective build uses a separate Android application ID (`com.zeroscript.studio.safe`) so it can be installed alongside an older build without overwriting its data.
