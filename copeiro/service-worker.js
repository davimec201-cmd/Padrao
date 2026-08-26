/* =========================================================================
   Service worker do Copeiro — estratégia offline-first.

   Tudo que o app precisa cabe em quatro arquivos, então o cache é feito
   inteiro na instalação. Depois disso o app abre sem rede nenhuma: a rede
   só é consultada quando o arquivo não está no cache.

   Para publicar uma versão nova, basta trocar o número em VERSAO: o
   service worker novo instala e guarda tudo. Assumir o controle é outra
   história — quem escolhe a hora é a página, e o porquê está em
   esperaAVezOuAssume(), mais abaixo.
   ========================================================================= */

const VERSAO = 'copeiro-v16';

/* Caminhos relativos: assim funciona igual em https://usuario.github.io/repo/copeiro/
   e em qualquer outra pasta, sem precisar ajustar nada. */
const ARQUIVOS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icone-192.png',
  './icone-512.png',
  './temas/indice.json',
  './temas/gremio.json',
  './temas/neutro.json',
  './assets/focus/focus-stadium-neutral.webp'
];

/* ---- Instalação: baixa e guarda tudo ---- */
self.addEventListener('install', (evento) => {
  evento.waitUntil(
    caches.open(VERSAO)
      .then((cache) => cache.addAll(ARQUIVOS))
      // Se um arquivo falhar (offline na primeira visita, por exemplo),
      // a instalação não é abortada: o que der certo já fica guardado.
      .catch((erro) => console.warn('[copeiro] cache parcial na instalação:', erro))
      .then(esperaAVezOuAssume)
  );
  // Sem skipWaiting de propósito. Assumir aqui apagaria o cache antigo debaixo
  // de uma tela que ainda está rodando o código velho, e daí em diante cada
  // busca traria arquivo de outra versão — frase com {nome} cru, arte que a
  // função antiga não sabe desenhar. Quem manda assumir é a página, quando
  // recarregar não custa nada. Na primeira visita não existe worker no ar, e
  // aí a ativação é imediata de qualquer jeito.
});

/* ---- Conversa com a página ---- */
let paginaCuidaDaTroca = false;
let paginaFalou;
const esperaAPagina = new Promise((avisa) => { paginaFalou = avisa; });

self.addEventListener('message', (evento) => {
  const dado = evento.data || {};
  // "Eu sei escolher a hora de trocar" — só telas desta versão em diante.
  if (dado.tipo === 'euCuido' || dado.tipo === 'assumir') {
    paginaCuidaDaTroca = true;
    paginaFalou();          // solta a espera na hora: o aviso não pode atrasar
  }
  if (dado.tipo === 'assumir') self.skipWaiting();
});

/**
 * Esperar a página pedir é o certo, mas só funciona com uma página que saiba
 * pedir. Toda tela publicada antes desta versão não sabe: o worker ficaria
 * esperando até o app fechar por inteiro, e uma aba esquecida aberta seguraria
 * a atualização por tempo indeterminado. Então são dez segundos de cortesia —
 * se ninguém se apresentou, assume do mesmo jeito.
 *
 * Sem janela nenhuma aberta não há o que combinar: a ativação já é imediata.
 */
function esperaAVezOuAssume() {
  return self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    .then((janelas) => {
      if (!janelas.length) return;
      // Corrida: quem chegar primeiro decide. Uma tela que se apresenta encerra
      // a espera no mesmo instante — senão a instalação ficaria dez segundos
      // pendurada e o aviso de versão nova só apareceria depois deles.
      return Promise.race([esperaAPagina, new Promise((pronto) => setTimeout(pronto, 10000))])
        .then(() => { if (!paginaCuidaDaTroca) return self.skipWaiting(); });
    })
    .catch(() => self.skipWaiting());
}

/* ---- Ativação: remove caches de versões anteriores ---- */
self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((chaves) => Promise.all(
        chaves.filter((chave) => chave !== VERSAO).map((chave) => caches.delete(chave))
      ))
      .then(() => self.clients.claim())
  );
});

/* ---- Toque na notificação: traz o app pra frente ---- */
self.addEventListener('notificationclick', (evento) => {
  evento.notification.close();
  evento.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((janelas) => {
      for (const janela of janelas) {
        if ('focus' in janela) return janela.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow('./index.html');
    })
  );
});

/* ---- Busca: cache primeiro, rede como reserva ---- */
self.addEventListener('fetch', (evento) => {
  const req = evento.request;

  // Só interessa GET do mesmo domínio; o resto passa direto.
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  evento.respondWith(
    caches.match(req, { ignoreSearch: true }).then((guardado) => {
      if (guardado) return guardado;

      return fetch(req)
        .then((resposta) => {
          // Guarda cópia do que veio da rede, para a próxima vez ser offline.
          if (resposta && resposta.status === 200 && resposta.type === 'basic') {
            const copia = resposta.clone();
            caches.open(VERSAO).then((cache) => cache.put(req, copia)).catch(() => {});
          }
          return resposta;
        })
        .catch(() => {
          // Sem rede: navegação cai sempre na tela do app.
          if (req.mode === 'navigate') return caches.match('./index.html');
          return new Response('', { status: 503, statusText: 'Offline' });
        });
    })
  );
});
