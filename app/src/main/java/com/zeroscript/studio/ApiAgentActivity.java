package com.zeroscript.studio;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Official-API agent path. No browser cookies, DOM injection, or simulated UI events. */
public final class ApiAgentActivity extends Activity {
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private Spinner provider;
    private EditText key, model, prompt;
    private CheckBox allowTools;
    private TextView output;
    private Button run;
    private static final String SYSTEM = "You are ZeroScript, an assistant connected to the user's Roblox Studio through MCP. " +
            "Use the supplied tools when useful. Inspect the place before editing. Never claim an action succeeded unless its tool result confirms it. " +
            "For Luau use the execute_luau tool and valid Roblox Luau. Keep tool arguments faithful to their schemas.";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setPadding(18,14,18,14);
        TextView heading = new TextView(this); heading.setText("ZeroScript · API oficial"); heading.setTextSize(21); heading.setPadding(0,0,0,8); root.addView(heading);
        TextView note = new TextView(this); note.setText("Conecta mediante la API del proveedor. No usa tu sesión web ni automatiza la página de la IA. La clave solo se mantiene en memoria durante esta pantalla."); note.setTextSize(13); root.addView(note);
        provider = new Spinner(this);
        String[] providers = {"DeepSeek API", "OpenAI API", "Qwen API", "GLM API", "Moonshot API", "Endpoint compatible personalizado"};
        provider.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, providers)); root.addView(provider);
        key = field("API key (no se guarda)", true); root.addView(key);
        model = field("Modelo (ej. deepseek-chat)", false); model.setText("deepseek-chat"); root.addView(model);
        allowTools = new CheckBox(this); allowTools.setText("Permitir que la IA ejecute herramientas MCP y modifique Roblox Studio"); allowTools.setChecked(false); root.addView(allowTools);
        prompt = field("¿Qué quieres hacer en Roblox Studio?", false); prompt.setMinLines(3); prompt.setGravity(48); root.addView(prompt);
        run = new Button(this); run.setText("Iniciar agente"); root.addView(run);
        ScrollView scroll = new ScrollView(this); output = new TextView(this); output.setTextIsSelectable(true); output.setTextSize(14); output.setPadding(4,12,4,12); scroll.addView(output); root.addView(scroll, new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
        provider.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            public void onNothingSelected(android.widget.AdapterView<?> a) {}
            public void onItemSelected(android.widget.AdapterView<?> a, View v, int pos, long id) {
                String[] defaults = {"deepseek-chat", "gpt-4.1-mini", "qwen-plus", "glm-4.5", "kimi-k2.5", "model-name"}; model.setText(defaults[pos]);
            }
        });
        run.setOnClickListener(v -> startAgent());
    }
    private EditText field(String hint, boolean secret) {
        EditText e = new EditText(this); e.setSingleLine(!secret); e.setHint(hint);
        if (secret) e.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        else e.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        return e;
    }
    private String baseUrl() {
        switch (provider.getSelectedItemPosition()) {
            case 0: return "https://api.deepseek.com";
            case 1: return "https://api.openai.com";
            case 2: return "https://dashscope.aliyuncs.com/compatible-mode";
            case 3: return "https://open.bigmodel.cn/api/paas/v4";
            case 4: return "https://api.moonshot.ai/v1";
            default: return "";
        }
    }
    private void startAgent() {
        final String secret = key.getText().toString().trim(), modelName = model.getText().toString().trim(), userText = prompt.getText().toString().trim();
        if (secret.isEmpty() || modelName.isEmpty() || userText.isEmpty()) { Toast.makeText(this,"Completa API key, modelo y petición.",Toast.LENGTH_LONG).show(); return; }
        String base = baseUrl();
        if (base.isEmpty()) { new AlertDialog.Builder(this).setTitle("Endpoint compatible").setMessage("El endpoint personalizado estará disponible en una próxima actualización. Selecciona DeepSeek, OpenAI, Qwen, GLM o Moonshot.").setPositiveButton("OK",null).show(); return; }
        final boolean toolsAllowed = allowTools.isChecked();
        run.setEnabled(false); output.setText("Conectando con la API oficial…\n");
        worker.execute(() -> {
            try { String result = agent(base, secret, modelName, userText, toolsAllowed); runOnUiThread(() -> output.append("\n" + result)); }
            catch (Exception ex) { runOnUiThread(() -> output.append("\nERROR: " + ex.getMessage())); }
            runOnUiThread(() -> run.setEnabled(true));
        });
    }
    private String agent(String base, String apiKey, String modelName, String userText, boolean toolsAllowed) throws Exception {
        JSONArray messages = new JSONArray();
        messages.put(new JSONObject().put("role","system").put("content",SYSTEM));
        messages.put(new JSONObject().put("role","user").put("content",userText));
        JSONArray tools = toolSpecs();
        for (int turn=0; turn<8; turn++) {
            JSONObject req = new JSONObject().put("model",modelName).put("messages",messages).put("temperature",0.2);
            if (tools.length()>0) req.put("tools",tools).put("tool_choice","auto");
            JSONObject response = post(base + "/chat/completions", apiKey, req);
            JSONObject choice = response.getJSONArray("choices").getJSONObject(0);
            JSONObject message = choice.getJSONObject("message");
            messages.put(message);
            String content = message.optString("content","");
            JSONArray calls = message.optJSONArray("tool_calls");
            if (calls == null || calls.length()==0) return content.isEmpty()?"La API no devolvió texto.":content;
            if (!toolsAllowed) {
                StringBuilder pending = new StringBuilder("La IA propuso herramientas, pero la ejecución MCP está desactivada. Revisa la propuesta y activa la casilla solo si autorizas cambios:\n");
                for (int i=0;i<calls.length();i++) { JSONObject fn=calls.getJSONObject(i).getJSONObject("function"); pending.append("\n• ").append(fn.optString("name")).append(" ").append(fn.optString("arguments")); }
                return pending.toString();
            }
            for (int i=0;i<calls.length();i++) {
                JSONObject call=calls.getJSONObject(i), fn=call.getJSONObject("function");
                String name=fn.getString("name"); JSONObject args=new JSONObject(fn.optString("arguments","{}"));
                JSONObject result=Hub.handle(new JSONObject().put("type","call_tool").put("name",name).put("arguments",args).put("timeout",120000));
                String text=result.optBoolean("ok")?result.optString("text"):"ERROR: "+result.optString("error","fallo MCP");
                messages.put(new JSONObject().put("role","tool").put("tool_call_id",call.getString("id")).put("content",text));
                final String line="\n[MCP] "+name+": "+text;
                runOnUiThread(() -> output.append(line.length()>5000?line.substring(0,5000)+"…":line));
            }
        }
        return "Se alcanzó el límite de 8 turnos de herramientas. Continúa con una nueva petición si hace falta.";
    }
    private JSONArray toolSpecs() throws Exception {
        JSONObject list=Hub.handle(new JSONObject().put("type","list_tools")); JSONArray src=list.optJSONArray("tools"), out=new JSONArray();
        if(src==null)return out;
        for(int i=0;i<src.length();i++) {
            JSONObject t=src.getJSONObject(i);
            JSONObject schema=t.optJSONObject("inputSchema");
            if(schema==null) schema=new JSONObject().put("type","object").put("properties",new JSONObject());
            JSONObject fn=new JSONObject().put("name",t.getString("name")).put("description",t.optString("description","")).put("parameters",schema);
            out.put(new JSONObject().put("type","function").put("function",fn));
        }
        return out;
    }
    private JSONObject post(String url, String apiKey, JSONObject body) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL(url).openConnection(); c.setRequestMethod("POST"); c.setConnectTimeout(20000); c.setReadTimeout(120000); c.setDoOutput(true);
        c.setRequestProperty("Authorization","Bearer "+apiKey); c.setRequestProperty("Content-Type","application/json"); c.setRequestProperty("Accept","application/json");
        try(OutputStream os=c.getOutputStream()){os.write(body.toString().getBytes(StandardCharsets.UTF_8));}
        int code=c.getResponseCode(); InputStream in=code>=200&&code<300?c.getInputStream():c.getErrorStream(); ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] buf=new byte[8192]; int n; while((n=in.read(buf))!=-1)b.write(buf,0,n); String text=b.toString("UTF-8"); c.disconnect();
        if(code<200||code>=300) throw new Exception("API HTTP "+code+": "+(text.length()>1500?text.substring(0,1500):text));
        return new JSONObject(text);
    }
    @Override protected void onDestroy(){super.onDestroy();worker.shutdownNow();}
}