// Login oficial da Steam (OpenID) e leitura do perfil e da biblioteca.
// A senha fica só na Steam. A chave STEAM_KEY fica nos segredos do Supabase.

const SITE = "https://dmacwolf.github.io/joga-junto/";
const OPENID = "https://steamcommunity.com/openid/login";
const NS = "http://specs.openid.net/auth/2.0";
const IDENTIFICADOR = `${NS}/identifier_select`;
const API = "https://api.steampowered.com";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const BASE = `${SUPABASE_URL}/functions/v1/steam`;

function irPara(destino: string): Response {
  return new Response(null, { status: 302, headers: { Location: destino } });
}

function voltar(tipo: string, dados: Record<string, string>): Response {
  return irPara(`${SITE}steam-volta.html#${new URLSearchParams({ a: tipo, ...dados })}`);
}

function hex(bytes: Uint8Array): string {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

async function verificarLogin(q: URLSearchParams): Promise<boolean> {
  const corpo = new URLSearchParams();
  for (const [chave, valor] of q) {
    if (chave.startsWith("openid.")) corpo.set(chave, valor);
  }
  corpo.set("openid.mode", "check_authentication");
  const resposta = await fetch(OPENID, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: corpo,
  });
  return /is_valid\s*:\s*true/.test(await resposta.text());
}

async function jsonDaSteam(caminho: string, chave: string, extra: Record<string, string>) {
  const params = new URLSearchParams({ key: chave, format: "json", ...extra });
  const resposta = await fetch(`${API}/${caminho}?${params}`);
  if (!resposta.ok) throw new Error(`steam ${resposta.status}`);
  return await resposta.json();
}

async function concluir(steamid: string, chave: string): Promise<string> {
  const resumo = await jsonDaSteam("ISteamUser/GetPlayerSummaries/v2/", chave, { steamids: steamid });
  const jogador = resumo?.response?.players?.[0] ?? {};
  const biblioteca = await jsonDaSteam("IPlayerService/GetOwnedGames/v1/", chave, {
    steamid,
    include_appinfo: "1",
    include_played_free_games: "1",
  });
  const lista: { appid: number; name?: string; playtime_forever?: number }[] = biblioteca?.response?.games ?? [];
  const totalMinutos = lista.reduce((soma, j) => soma + (j.playtime_forever ?? 0), 0);
  const jogos = [...lista]
    .sort((a, b) => (b.playtime_forever ?? 0) - (a.playtime_forever ?? 0))
    .slice(0, 500)
    .map((j) => ({ a: j.appid, n: j.name ?? "", h: Math.round((j.playtime_forever ?? 0) / 60) }));

  const token = hex(crypto.getRandomValues(new Uint8Array(32)));
  const hash = hex(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token))));
  const servico = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  const salvo = await fetch(`${SUPABASE_URL}/rest/v1/rpc/jj_steam_salvar`, {
    method: "POST",
    headers: { apikey: servico, Authorization: `Bearer ${servico}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      p_hash: hash,
      p_steamid: steamid,
      p_nome: jogador.personaname ?? "",
      p_avatar: jogador.avatarfull ?? "",
      p_perfil: jogador.profileurl ?? "",
      p_privado: lista.length === 0,
      p_total_jogos: lista.length,
      p_total_horas: Math.round(totalMinutos / 60),
      p_jogos: jogos,
    }),
  });
  if (!salvo.ok) throw new Error(`banco ${salvo.status}`);
  return token;
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const q = url.searchParams;
  const acao = q.get("acao");
  const tipo = q.get("volta") === "app" ? "app" : "site";
  const chave = Deno.env.get("STEAM_KEY") ?? "";

  if (acao === "status") {
    return new Response(JSON.stringify({ ativa: chave.length > 0 }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }

  if (acao === "login") {
    const params = new URLSearchParams({
      "openid.ns": NS,
      "openid.mode": "checkid_setup",
      "openid.return_to": `${BASE}?acao=retorno&volta=${tipo}`,
      "openid.realm": `${new URL(BASE).origin}/`,
      "openid.identity": IDENTIFICADOR,
      "openid.claimed_id": IDENTIFICADOR,
    });
    return irPara(`${OPENID}?${params}`);
  }

  if (acao === "retorno") {
    if (q.get("openid.mode") !== "id_res") return voltar(tipo, { erro: "cancelado" });
    if (!chave) return voltar(tipo, { erro: "inativa" });
    const steamid = (q.get("openid.claimed_id") ?? "").match(/^https:\/\/steamcommunity\.com\/openid\/id\/(\d{17})$/)?.[1];
    const voltaCerta = (q.get("openid.return_to") ?? "").startsWith(`${BASE}?acao=retorno`);
    if (!steamid || !voltaCerta || q.get("openid.op_endpoint") !== OPENID) return voltar(tipo, { erro: "falha" });
    try {
      if (!(await verificarLogin(q))) return voltar(tipo, { erro: "falha" });
      return voltar(tipo, { t: await concluir(steamid, chave) });
    } catch (erro) {
      console.error(erro);
      return voltar(tipo, { erro: "falha" });
    }
  }

  return new Response("Não encontrado", { status: 404 });
});
