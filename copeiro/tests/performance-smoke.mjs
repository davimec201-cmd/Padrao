import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const fonte = fs.readFileSync(new URL('../performance-protocols.js', import.meta.url), 'utf8');
const contexto = { window: {} };
vm.createContext(contexto);
vm.runInContext(fonte, contexto);

const protocolos = contexto.window.COPEIRO_PROTOCOLOS;
const aviso = contexto.window.COPEIRO_AVISO_PROTOCOLO;

assert.ok(Array.isArray(protocolos) && protocolos.length >= 6, 'deve haver protocolos piloto');
assert.deepEqual([...new Set(protocolos.map((p) => p.duracao))].sort((a, b) => a - b), [2, 5, 10]);
assert.match(aviso, /Protocolo piloto/);
assert.match(aviso, /pendente de revisão/);

for (const protocolo of protocolos) {
  assert.ok(protocolo.id && protocolo.nome && protocolo.objetivo);
  assert.ok(['Muito leve', 'Leve'].includes(protocolo.intensidade));
  assert.ok(Array.isArray(protocolo.ambientes) && protocolo.ambientes.length);
  assert.ok(Array.isArray(protocolo.filtros));
  assert.ok(Array.isArray(protocolo.instrucoes) && protocolo.instrucoes.length);
  assert.equal(
    protocolo.instrucoes.reduce((soma, passo) => soma + passo.segundos, 0),
    protocolo.duracao * 60,
    protocolo.id + ' precisa preencher a duração declarada'
  );
}

console.log('performance-smoke: ok (' + protocolos.length + ' protocolos)');
