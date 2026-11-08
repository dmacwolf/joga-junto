package app.jogajunto;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.TextView;

/**
 * Casca fina: abre o site publicado do Joga Junto em tela cheia.
 * O conteúdo vem sempre da internet (com cache offline no próprio site),
 * então o app se atualiza sozinho quando o site é republicado.
 */
public class MainActivity extends Activity {

    private static final String OFFLINE_PAGE = "file:///android_asset/offline.html";
    private static final String RETRY_SCHEME = "p2retry";

    private static int quedasDaPagina = 0;

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        // Transparente: enquanto a página carrega, aparece a logo da tela de abertura atrás.
        web.setBackgroundColor(0x00000000);
        setContentView(web);

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setUserAgentString(settings.getUserAgentString() + " JogaJuntoApp/2");

        final Uri home = Uri.parse(BuildConfig.APP_URL);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                String scheme = url.getScheme();

                if (RETRY_SCHEME.equals(scheme)) {
                    view.loadUrl(BuildConfig.APP_URL);
                    return true;
                }
                if ("file".equals(scheme)) {
                    return false;
                }
                String host = url.getHost();
                if (host != null && host.equals(home.getHost())) {
                    return false;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, url));
                } catch (ActivityNotFoundException ignored) {
                    // Sem app para abrir o link: ignora.
                }
                return true;
            }

            @Override
            public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detalhe) {
                aoCairPagina(view, detalhe.didCrash());
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    view.loadUrl(OFFLINE_PAGE);
                }
            }
        });

        if (!abrirRetornoSteam(getIntent())) {
            web.loadUrl(BuildConfig.APP_URL);
        }

        try {
            AvisoJob.agendar(this);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
                    && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
            }
        } catch (Throwable erro) {
            // O aviso é um extra: se falhar, o app continua abrindo.
            JogaJuntoApp.relatar("AVISO: " + Log.getStackTraceString(erro), false);
        }
    }

    /** Sem este tratamento, uma queda da parte que desenha a página derruba o app inteiro. */
    private void aoCairPagina(WebView view, boolean foiErro) {
        JogaJuntoApp.relatar("PAGINA CAIU: erro=" + foiErro + " quedas=" + quedasDaPagina, false);
        android.view.ViewGroup pai = (android.view.ViewGroup) view.getParent();
        if (pai != null) {
            pai.removeView(view);
        }
        view.destroy();
        web = null;
        if (quedasDaPagina++ < 2) {
            recreate();
            return;
        }
        TextView aviso = new TextView(this);
        aviso.setText("Não consegui abrir o Joga Junto. Feche e tente de novo.");
        aviso.setTextColor(0xFFFFFFFF);
        aviso.setGravity(Gravity.CENTER);
        aviso.setBackgroundColor(0xFF080913);
        setContentView(aviso);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        abrirRetornoSteam(intent);
    }

    /** Depois do login no navegador, a Steam volta por jogajunto://steam e o app guarda a conexão. */
    private boolean abrirRetornoSteam(Intent intent) {
        Uri dados = intent == null ? null : intent.getData();
        if (dados == null || !"jogajunto".equals(dados.getScheme())) {
            return false;
        }
        if ("login".equals(dados.getHost())) {
            String codigo = dados.getQueryParameter("code");
            boolean valido = codigo != null && codigo.matches("[0-9a-zA-Z-]{20,100}");
            web.loadUrl(BuildConfig.APP_URL + "login-volta.html" + (valido ? "?code=" + codigo : "?erro=falha"));
            return true;
        }
        if (!"steam".equals(dados.getHost())) {
            return false;
        }
        String token = dados.getQueryParameter("t");
        String erro = dados.getQueryParameter("erro");
        String fragmento = "erro=falha";
        if (token != null && token.matches("[0-9a-f]{64}")) {
            fragmento = "t=" + token;
        } else if (erro != null && erro.matches("[a-z]{1,20}")) {
            fragmento = "erro=" + erro;
        }
        web.loadUrl(BuildConfig.APP_URL + "steam-volta.html#" + fragmento);
        return true;
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onPause() {
        if (web != null) {
            web.onPause();
        }
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) {
            web.onResume();
        }
    }
}
