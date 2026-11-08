package app.jogajunto;

import android.app.Application;
import android.os.Build;
import android.util.Log;

import org.json.JSONObject;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/** Quando o app fecha por erro, envia o motivo para o projeto antes de encerrar. */
public class JogaJuntoApp extends Application {

    private static final String ENDERECO =
            "https://mlfxwdfuadcactwwbjyl.supabase.co/rest/v1/rpc/jj_relato_app";
    private static final String CHAVE_PUBLICA = "sb_publishable_4sRyRGc6bADRWtuD-Js-QQ_BLgQx162";

    @Override
    public void onCreate() {
        super.onCreate();
        final Thread.UncaughtExceptionHandler anterior = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((linha, erro) -> {
            relatar("FECHOU: " + Log.getStackTraceString(erro), true);
            if (anterior != null) {
                anterior.uncaughtException(linha, erro);
            }
        });
    }

    static void relatar(String texto, boolean esperar) {
        Thread envio = new Thread(() -> {
            try {
                enviar(texto);
            } catch (Exception ignorado) {
                // Sem internet: não há o que fazer.
            }
        });
        envio.start();
        if (esperar) {
            try {
                envio.join(4000);
            } catch (InterruptedException ignorado) {
                // Segue o encerramento.
            }
        }
    }

    private static void enviar(String texto) throws Exception {
        JSONObject corpo = new JSONObject();
        corpo.put("versao", BuildConfig.VERSION_NAME);
        corpo.put("aparelho", Build.MANUFACTURER + " " + Build.MODEL + " Android " + Build.VERSION.RELEASE);
        corpo.put("texto", texto);

        HttpURLConnection conexao = (HttpURLConnection) new URL(ENDERECO).openConnection();
        conexao.setRequestMethod("POST");
        conexao.setConnectTimeout(3500);
        conexao.setReadTimeout(3500);
        conexao.setDoOutput(true);
        conexao.setRequestProperty("apikey", CHAVE_PUBLICA);
        conexao.setRequestProperty("Content-Type", "application/json");
        try (OutputStream saida = conexao.getOutputStream()) {
            saida.write(corpo.toString().getBytes(StandardCharsets.UTF_8));
        }
        conexao.getResponseCode();
        conexao.disconnect();
    }
}
