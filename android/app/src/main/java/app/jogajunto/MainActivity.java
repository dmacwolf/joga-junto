package app.jogajunto;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Casca fina: abre o site publicado do Joga Junto em tela cheia.
 * O conteúdo vem sempre da internet (com cache offline no próprio site),
 * então o app se atualiza sozinho quando o site é republicado.
 */
public class MainActivity extends Activity {

    private static final String OFFLINE_PAGE = "file:///android_asset/offline.html";
    private static final String RETRY_SCHEME = "p2retry";

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        web.setBackgroundColor(0xFF080913);
        setContentView(web);

        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

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
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    view.loadUrl(OFFLINE_PAGE);
                }
            }
        });

        web.loadUrl(BuildConfig.APP_URL);
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
