import assert from 'node:assert/strict';
import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const worker = fs.readFileSync(new URL('../service-worker.js', import.meta.url), 'utf8');

const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
assert.ok(scripts.length, 'index.html precisa conter o script principal');
const principal = scripts[scripts.length - 1][1];
new Function(principal);
new Function(worker);

function fonteDaFuncao(nome) {
  const inicio = principal.indexOf('function ' + nome + '(');
  assert.ok(inicio >= 0, 'função ausente: ' + nome);
  const abre = principal.indexOf('{', inicio);
  let nivel = 0;
  for (let i = abre; i < principal.length; i += 1) {
    if (principal[i] === '{') nivel += 1;
    if (principal[i] === '}') nivel -= 1;
    if (nivel === 0) return principal.slice(inicio, i + 1);
  }
  throw new Error('função não fechada: ' + nome);
}

const migracao = new Function(
  fonteDaFuncao('performanceNovo') + '\n' + fonteDaFuncao('normalizaPerformance') +
  '\nreturn { performanceNovo, normalizaPerformance };'
)();
const legado = migracao.normalizaPerformance(undefined);
assert.equal(legado.ativo, false);
assert.deepEqual(legado.atividades, []);
const parcial = migracao.normalizaPerformance({ ativo: true, contexto: { ambiente: 'casa' } });
assert.equal(parcial.ativo, true);
assert.equal(parcial.contexto.ambiente, 'casa');
assert.deepEqual(parcial.contexto.preferidas, []);
assert.deepEqual(parcial.contexto.diasTreino, []);

const estadoTeste = { performance: { atividades: [{ id: 'a1' }, { id: 'a2' }] } };
const chamadas = [];
const exclusao = new Function('estado', 'registraEventoPerformance', 'salvaEstado', 'desenhaPerformance',
  'let ultimoRegistroDeAtividade = "a1";\n' + fonteDaFuncao('removeAtividadePerformance') +
  '\nremoveAtividadePerformance("a1"); return { estado, ultimoRegistroDeAtividade };'
)(estadoTeste, (tipo) => chamadas.push(tipo), () => chamadas.push('salvou'), () => chamadas.push('desenhou'));
assert.deepEqual(exclusao.estado.performance.atividades.map((a) => a.id), ['a2']);
assert.equal(exclusao.ultimoRegistroDeAtividade, null);
assert.deepEqual(chamadas, ['activity_deleted', 'salvou', 'desenhou']);

const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
const duplicados = ids.filter((id, i) => ids.indexOf(id) !== i);
// modalEntrada já era repetido no HTML de referência; esta entrega não amplia
// o problema nem o usa no módulo novo.
assert.deepEqual(duplicados.filter((id) => id !== 'modalEntrada'), [], 'IDs novos precisam ser únicos');

for (const id of [
  'tela-performance', 'performanceConvite', 'performancePainel', 'perfDuracoes',
  'perfSugestao', 'perfAtivo', 'perfListaAtividades', 'perfMarcos'
]) {
  assert.ok(ids.includes(id), 'elemento obrigatório ausente: ' + id);
}

const estilos = [...html.matchAll(/<style(?:\s[^>]*)?>([\s\S]*?)<\/style>/gi)].map((m) => m[1]).join('\n');
let nivel = 0;
let comentario = false;
for (let i = 0; i < estilos.length; i += 1) {
  if (!comentario && estilos.slice(i, i + 2) === '/*') { comentario = true; i += 1; continue; }
  if (comentario && estilos.slice(i, i + 2) === '*/') { comentario = false; i += 1; continue; }
  if (comentario) continue;
  if (estilos[i] === '{') nivel += 1;
  if (estilos[i] === '}') nivel -= 1;
  assert.ok(nivel >= 0, 'CSS contém fechamento de bloco excedente');
}
assert.equal(nivel, 0, 'CSS contém bloco não fechado');

assert.match(html, /<script src="\.\/performance-protocols\.js"><\/script>/);
assert.match(worker, /copeiro-v20/);
assert.match(html, /const DURACOES = \[5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60\]/);
assert.match(worker, /performance-protocols\.js/);

console.log('validate-app: sintaxe, migração e exclusão válidas; ' + ids.length + ' IDs inspecionados');
