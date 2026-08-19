/* =========================================================================
   Service worker do Copeiro — estratégia offline-first.

   Tudo que o app precisa cabe em quatro arquivos, então o cache é feito
   inteiro na instalação. Depois disso o app abre sem rede nenhuma: a rede
   só é consultada quando o arquivo não está no cache.

   Para publicar uma versão nova, basta trocar o número em VERSAO: o
   service worker novo instala, limpa os caches antigos e assume o controle.
   ========================================================================= */

const VERSAO = 'copeiro-v9';

/* Caminhos relativos: assim funciona igual em https://usuario.github.io/repo/copeiro/
   e em qualquer outra pasta, sem precisar ajustar nada. */
const ARQUIVOS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icone-192.png',
  './icone-512.png'
];

/* ---- Instalação: baixa e guarda tudo ---- */
self.addEventListener('install', (evento) => {
  evento.waitUntil(
    caches.open(VERSAO)
      .then((cache) => cache.addAll(ARQUIVOS))
      // Se um arquivo falhar (offline na primeira visita, por exemplo),
      // a instalação não é abortada: o que der certo já fica guardado.
      .catch((erro) => console.warn('[copeiro] cache parcial na instalação:', erro))
      .then(() => self.skipWaiting())
  );
});

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
