from pathlib import Path

root = Path(".")
java = root / "app/src/main/java/com/zeroscript/studio/MainActivity.java"
s = java.read_text(encoding="utf-8")
s = s.replace("import android.widget.HorizontalScrollView;\n", "")
old = """        LinearLayout top = new LinearLayout(this);
        top.setOrientation(LinearLayout.HORIZONTAL);
        HorizontalScrollView scroll = new HorizontalScrollView(this);
        LinearLayout chips = new LinearLayout(this);
        chips.setOrientation(LinearLayout.HORIZONTAL);
        for (final Provider p : PROVIDERS) {
            Button btn = new Button(this);
            btn.setText(p.label);
            btn.setAllCaps(false);
            btn.setOnClickListener(v -> show(p));
            chips.addView(btn);
        }
        scroll.addView(chips);
        top.addView(scroll, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        Button menu = new Button(this);
        menu.setText("⋮");
        menu.setOnClickListener(this::openMenu);
        top.addView(menu);
        root.addView(top);

        statusView = new TextView(this);
        statusView.setPadding(24, 8, 24, 8);
        statusView.setGravity(Gravity.CENTER_VERTICAL);
        statusView.setTextSize(13);
        root.addView(statusView);

        container = new FrameLayout(this);
"""
new = """        // Compact app bar: AI selection lives in the overflow menu, not a wide chip strip.
        LinearLayout top = new LinearLayout(this);
        top.setOrientation(LinearLayout.HORIZONTAL);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setPadding(dp(12), dp(2), dp(6), dp(2));
        TextView title = new TextView(this);
        title.setText("ZeroScript Studio");
        title.setTextSize(18);
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        title.setGravity(Gravity.CENTER_VERTICAL);
        top.addView(title, new LinearLayout.LayoutParams(0, dp(48), 1f));
        Button menu = new Button(this);
        menu.setText("⋮");
        menu.setTextSize(22);
        menu.setMinWidth(dp(48));
        menu.setOnClickListener(this::openMenu);
        top.addView(menu, new LinearLayout.LayoutParams(dp(48), dp(48)));
        root.addView(top, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        statusView = new TextView(this);
        statusView.setPadding(dp(16), dp(4), dp(16), dp(4));
        statusView.setGravity(Gravity.CENTER_VERTICAL);
        statusView.setTextSize(12);
        root.addView(statusView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        // Hide secondary status text in compact pop-up windows; the web page gets the space.
        root.addOnLayoutChangeListener((v, left, topEdge, right, bottom, oldLeft, oldTop, oldRight, oldBottom) -> {
            int heightDp = (bottom - topEdge) / Math.max(1, getResources().getDisplayMetrics().densityDpi / 160);
            statusView.setVisibility(heightDp < 430 ? View.GONE : View.VISIBLE);
        });

        container = new FrameLayout(this);
"""
if old not in s:
    raise SystemExit("Expected AI switcher block was not found; refusing to patch.")
s = s.replace(old, new, 1)
old = """        PopupMenu m = new PopupMenu(this, anchor);
        m.getMenu().add(0, 5, 0, "Conectar Mobile Studio (codigo)");
        m.getMenu().add(0, 4, 0, "Enviar plugin a Mobile Studio (1 toque)");
        m.getMenu().add(0, 1, 1, "Guardar plugin en Descargas");
        m.getMenu().add(0, 2, 2, "Abrir Mobile Studio");
        m.getMenu().add(0, 3, 3, "Recargar pagina");
        m.setOnMenuItemClickListener(it -> {
            switch (it.getItemId()) {
"""
new = """        PopupMenu m = new PopupMenu(this, anchor);
        android.view.SubMenu aiMenu = m.getMenu().addSubMenu("Cambiar IA" +
                (current == null ? "" : " (" + current.label + ")"));
        for (int i = 0; i < PROVIDERS.length; i++) {
            Provider p = PROVIDERS[i];
            aiMenu.add(0, 100 + i, i, (current != null && current.id.equals(p.id) ? "✓ " : "") + p.label);
        }
        m.getMenu().add(0, 5, 1, "Conectar Mobile Studio (codigo)");
        m.getMenu().add(0, 4, 2, "Enviar plugin a Mobile Studio (1 toque)");
        m.getMenu().add(0, 1, 3, "Guardar plugin en Descargas");
        m.getMenu().add(0, 2, 4, "Abrir Mobile Studio");
        m.getMenu().add(0, 3, 5, "Recargar pagina");
        m.setOnMenuItemClickListener(it -> {
            int itemId = it.getItemId();
            if (itemId >= 100 && itemId < 100 + PROVIDERS.length) {
                show(PROVIDERS[itemId - 100]);
                return true;
            }
            switch (itemId) {
"""
if old not in s:
    raise SystemExit("Expected menu block was not found; refusing to patch.")
s = s.replace(old, new, 1)
needle = "    private void askCode() {\n"
if needle not in s:
    raise SystemExit("Could not find insertion point for dp helper.")
s = s.replace(needle, """    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

""" + needle, 1)
java.write_text(s, encoding="utf-8")

# Disable DOM-driven automation of consumer AI websites. This is a protective
# stop-gap: the browser tabs remain usable manually, but ZeroScript must not
# inject hidden prompts, replay turns, scrape replies, or execute tool calls
# through personal web sessions. Re-enable only after official API adapters exist.
main_js = root / "app/src/main/assets/zs/main.js"
js = main_js.read_text(encoding="utf-8")
anchor = "  const P = ZSProvider;\n"
if anchor not in js:
    raise SystemExit("Could not find provider bootstrap in main.js; refusing safety patch.")
guard = """  const P = ZSProvider;
  const WEB_AUTOMATION_DISABLED = true;
  let webAutomationNoticeShown = false;
  function notifyWebAutomationDisabled() {
    if (webAutomationNoticeShown) return;
    webAutomationNoticeShown = true;
    ui.banner("warn", "Automatización web desactivada",
      "Para proteger tus cuentas, ZeroScript no automatiza sesiones personales de ChatGPT, DeepSeek u otras IAs. Puedes usar esta página manualmente. La integración automática volverá mediante API oficiales.");
  }
"""
if "const WEB_AUTOMATION_DISABLED = true;" not in js:
    js = js.replace(anchor, guard, 1)
for signature, statement in [
    ("  async function submitAndGetBase(text, images) {\n",
     "    if (WEB_AUTOMATION_DISABLED) { notifyWebAutomationDisabled(); return P.assistantCount(); }\n"),
    ("  async function agentLoop(base) {\n",
     "    if (WEB_AUTOMATION_DISABLED) { notifyWebAutomationDisabled(); return; }\n"),
    ("  async function startSession() {\n",
     "    if (WEB_AUTOMATION_DISABLED) { notifyWebAutomationDisabled(); return; }\n"),
]:
    if signature not in js:
        raise SystemExit("Could not find expected function " + signature.strip() + "; refusing safety patch.")
    if statement.strip() not in js:
        js = js.replace(signature, signature + statement, 1)
main_js.write_text(js, encoding="utf-8")

# Do not disguise Android WebView as a regular browser. Let providers receive
# the genuine WebView user-agent instead of stripping the "; wv" marker.
activity = root / "app/src/main/java/com/zeroscript/studio/MainActivity.java"
activity_source = activity.read_text(encoding="utf-8")
activity_source = activity_source.replace(
    '        s.setUserAgentString(s.getUserAgentString().replace("; wv", ""));\\n',
    ''
)
activity.write_text(activity_source, encoding="utf-8")

manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")
m = m.replace('android:label="ZeroScript Studio"', 'android:label="ZeroScript Studio"\n        android:icon="@mipmap/ic_launcher"\n        android:roundIcon="@mipmap/ic_launcher_round"', 1)
manifest.write_text(m, encoding="utf-8")

res = root / "app/src/main/res"
(res / "drawable").mkdir(parents=True, exist_ok=True)
(res / "mipmap").mkdir(parents=True, exist_ok=True)
(res / "mipmap-anydpi-v26").mkdir(parents=True, exist_ok=True)
(res / "drawable/ic_launcher_background.xml").write_text(
    '<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#101827" /></shape>\n',
    encoding="utf-8")
foreground = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#1DD6B4" android:pathData="M54,10 C78.3,10 98,29.7 98,54 C98,78.3 78.3,98 54,98 C29.7,98 10,78.3 10,54 C10,29.7 29.7,10 54,10 Z" />
    <path android:fillColor="#101827" android:pathData="M32,31 L76,31 L76,42 L48,42 L76,67 L76,78 L32,78 L32,67 L60,67 L32,42 Z" />
    <path android:fillColor="#FFFFFF" android:pathData="M78,22 C82.4,22 86,25.6 86,30 C86,34.4 82.4,38 78,38 C73.6,38 70,34.4 70,30 C70,25.6 73.6,22 78,22 Z" />
    <path android:fillColor="#FFFFFF" android:pathData="M30,70 C34.4,70 38,73.6 38,78 C38,82.4 34.4,86 30,86 C25.6,86 22,82.4 22,78 C22,73.6 25.6,70 30,70 Z" />
    <path android:fillColor="#FFFFFF" android:pathData="M78,70 C82.4,70 86,73.6 86,78 C86,82.4 82.4,86 78,86 C73.6,86 70,82.4 70,78 C70,73.6 73.6,70 78,70 Z" />
</vector>
"""
(res / "drawable/ic_launcher_foreground.xml").write_text(foreground, encoding="utf-8")
adaptive = """<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
"""
(res / "mipmap-anydpi-v26/ic_launcher.xml").write_text(adaptive, encoding="utf-8")
(res / "mipmap-anydpi-v26/ic_launcher_round.xml").write_text(adaptive, encoding="utf-8")
legacy = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#101827" android:pathData="M0,0h108v108h-108z" />
    <path android:fillColor="#1DD6B4" android:pathData="M54,10 C78.3,10 98,29.7 98,54 C98,78.3 78.3,98 54,98 C29.7,98 10,78.3 10,54 C10,29.7 29.7,10 54,10 Z" />
    <path android:fillColor="#101827" android:pathData="M32,31 L76,31 L76,42 L48,42 L76,67 L76,78 L32,78 L32,67 L60,67 L32,42 Z" />
</vector>
"""
(res / "mipmap/ic_launcher.xml").write_text(legacy, encoding="utf-8")
