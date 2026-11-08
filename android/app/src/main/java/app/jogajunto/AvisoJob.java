package app.jogajunto;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * De tempos em tempos o Android roda este serviço, mesmo com o app fechado.
 * Ele lê versao.json no site publicado e, se a versão mudou, avisa com uma notificação.
 */
public class AvisoJob extends JobService {

    private static final int JOB_ID = 4701;
    private static final long INTERVALO_MS = 15 * 60 * 1000L;
    private static final String CANAL = "novidades";
    private static final String PREFS = "avisos";
    private static final String CHAVE_VERSAO = "versao";

    private Thread tarefa;

    static void agendar(Context contexto) {
        JobScheduler agenda = contexto.getSystemService(JobScheduler.class);
        if (agenda == null || agenda.getPendingJob(JOB_ID) != null) {
            return;
        }
        agenda.schedule(new JobInfo.Builder(JOB_ID, new ComponentName(contexto, AvisoJob.class))
                .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
                .setPeriodic(INTERVALO_MS)
                .setPersisted(true)
                .build());
    }

    @Override
    public boolean onStartJob(JobParameters parametros) {
        tarefa = new Thread(() -> {
            try {
                verificar();
            } catch (Exception ignorado) {
                // Sem internet ou resposta inválida: tenta de novo na próxima rodada.
            }
            jobFinished(parametros, false);
        });
        tarefa.start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters parametros) {
        if (tarefa != null) {
            tarefa.interrupt();
        }
        return true;
    }

    private void verificar() throws Exception {
        JSONObject dados = new JSONObject(baixar(BuildConfig.APP_URL + "versao.json?t=" + System.currentTimeMillis()));
        String versao = dados.getString("versao");

        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String conhecida = prefs.getString(CHAVE_VERSAO, null);
        if (versao.equals(conhecida)) {
            return;
        }
        prefs.edit().putString(CHAVE_VERSAO, versao).apply();

        // Na primeira vez só guarda a versão: quem acabou de instalar não tem novidade para saber.
        if (conhecida != null) {
            notificar(dados.optString("mensagem", "O Joga Junto foi atualizado."));
        }
    }

    private String baixar(String endereco) throws Exception {
        HttpURLConnection conexao = (HttpURLConnection) new URL(endereco).openConnection();
        conexao.setUseCaches(false);
        conexao.setConnectTimeout(15000);
        conexao.setReadTimeout(15000);
        try (BufferedReader leitor = new BufferedReader(
                new InputStreamReader(conexao.getInputStream(), StandardCharsets.UTF_8))) {
            StringBuilder texto = new StringBuilder();
            String linha;
            while ((linha = leitor.readLine()) != null) {
                texto.append(linha);
            }
            return texto.toString();
        } finally {
            conexao.disconnect();
        }
    }

    private void notificar(String mensagem) {
        NotificationManager gerente = getSystemService(NotificationManager.class);
        if (gerente == null) {
            return;
        }
        NotificationChannel canal =
                new NotificationChannel(CANAL, "Novidades do app", NotificationManager.IMPORTANCE_DEFAULT);
        canal.setShowBadge(true);
        gerente.createNotificationChannel(canal);

        Intent abrir = new Intent(this, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent toque = PendingIntent.getActivity(
                this, 0, abrir, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification aviso = new Notification.Builder(this, CANAL)
                .setSmallIcon(R.drawable.ic_notif)
                .setContentTitle("Joga Junto")
                .setContentText(mensagem)
                .setStyle(new Notification.BigTextStyle().bigText(mensagem))
                .setContentIntent(toque)
                .setAutoCancel(true)
                .setNumber(1)
                .build();
        gerente.notify(1, aviso);
    }
}
