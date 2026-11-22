# ZeroScript Studio Mobile

ZeroScript Studio Mobile restores the ZeroScript agent workflow inside the Android app.

## What works
- Provider-specific adapters for ChatGPT, DeepSeek, Gemini, Kimi, GLM, Qwen, Arena and Meta AI.
- ZeroScript parser and agent loop: the AI can return ZeroScript commands, the app routes them through the local Mobile Studio bridge, and the tool result is returned to the conversation.
- Mobile Studio connection, plugin export and reconnect/status UI.
- Compact provider picker in the overflow menu, responsive WebView layout for pop-up and split-screen use, and a launcher icon.

## Account and provider safety
This build keeps the normal Android WebView user-agent and does not attempt to disguise the app as Chrome. It does not add randomized "human-like" delays, CAPTCHA bypasses, cookie reuse, or other anti-detection mechanisms. The agent loop is still automation of provider websites; each provider may restrict or disallow that use, and no build can guarantee that an account will never be limited or banned. Use each provider only in ways permitted by its current terms. Stop if a provider presents a CAPTCHA, warning, or rate-limit message; do not automate around it.

Roblox/Mobile Studio tool calls can modify projects. Review commands and keep backups before running destructive edits.

## Build
Push to GitHub or manually run **Build APK** in Actions. Download the **ZeroScriptStudio-apk** artifact from the successful workflow run. The mobile package ID is `com.zeroscript.studio.mobile`, so it can coexist with older installations.
