/* Protocolos piloto do Copeiro Performance.
 *
 * Este arquivo e a unica fonte de conteudo dos intervalos inteligentes. A
 * interface apenas filtra e apresenta estes dados, o que permite substituir
 * o conteudo depois da revisao profissional sem mexer no motor do app.
 */
(function () {
  'use strict';

  window.COPEIRO_AVISO_PROTOCOLO =
    'Protocolo piloto — pendente de revisão pelo profissional de Educação Física.';

  window.COPEIRO_PROTOCOLOS = [
    {
      id: 'reinicio-sentado-2',
      nome: 'Reinício sentado',
      objetivo: 'Mudar a posição do corpo antes do próximo bloco.',
      duracao: 2,
      intensidade: 'Muito leve',
      ambientes: ['casa', 'biblioteca', 'faculdade'],
      filtros: ['silencioso', 'sem-suar', 'pouco-espaco', 'sentado', 'antes-treino', 'depois-treino'],
      instrucoes: [
        { segundos: 40, texto: 'Apoie os pés e ajuste a posição no assento, sem forçar.' },
        { segundos: 40, texto: 'Movimente tornozelos e mãos devagar, no seu ritmo.' },
        { segundos: 40, texto: 'Relaxe os ombros e faça uma respiração confortável.' }
      ]
    },
    {
      id: 'levanta-leve-2',
      nome: 'Levanta leve',
      objetivo: 'Sair da posição sentada por alguns instantes.',
      duracao: 2,
      intensidade: 'Leve',
      ambientes: ['casa', 'faculdade'],
      filtros: ['silencioso', 'sem-suar', 'pouco-espaco', 'antes-treino', 'depois-treino'],
      instrucoes: [
        { segundos: 40, texto: 'Levante com calma e encontre uma posição confortável.' },
        { segundos: 40, texto: 'Transfira o peso de um pé para o outro, sem pressa.' },
        { segundos: 40, texto: 'Caminhe poucos passos e prepare a volta ao estudo.' }
      ]
    },
    {
      id: 'mobilidade-silenciosa-5',
      nome: 'Mobilidade silenciosa',
      objetivo: 'Variar movimentos sem fazer barulho nem elevar o ritmo.',
      duracao: 5,
      intensidade: 'Leve',
      ambientes: ['casa', 'biblioteca', 'faculdade'],
      filtros: ['silencioso', 'sem-suar', 'pouco-espaco', 'antes-treino', 'depois-treino'],
      instrucoes: [
        { segundos: 60, texto: 'Levante, se puder, e encontre uma postura confortável.' },
        { segundos: 60, texto: 'Movimente os ombros e os braços com amplitude confortável.' },
        { segundos: 60, texto: 'Alterne o apoio dos pés de forma lenta e silenciosa.' },
        { segundos: 60, texto: 'Caminhe poucos passos ou continue alternando os apoios.' },
        { segundos: 60, texto: 'Reduza o movimento e organize o próximo bloco.' }
      ]
    },
    {
      id: 'caminhada-curta-5',
      nome: 'Caminhada curta',
      objetivo: 'Trocar de ambiente e recuperar a disposição.',
      duracao: 5,
      intensidade: 'Leve',
      ambientes: ['casa', 'faculdade'],
      filtros: ['sem-suar', 'posso-caminhar', 'antes-treino', 'depois-treino'],
      instrucoes: [
        { segundos: 60, texto: 'Comece a caminhar em ritmo confortável.' },
        { segundos: 180, texto: 'Continue pelo espaço disponível, sem buscar velocidade.' },
        { segundos: 60, texto: 'Volte ao local de estudo e diminua o ritmo.' }
      ]
    },
    {
      id: 'volta-ao-quarteirao-10',
      nome: 'Caminhada de dez',
      objetivo: 'Fazer uma pausa mais longa fora da posição sentada.',
      duracao: 10,
      intensidade: 'Leve',
      ambientes: ['casa', 'faculdade'],
      filtros: ['posso-caminhar', 'antes-treino', 'depois-treino'],
      instrucoes: [
        { segundos: 120, texto: 'Comece a caminhar em ritmo confortável.' },
        { segundos: 360, texto: 'Mantenha uma caminhada tranquila pelo espaço disponível.' },
        { segundos: 120, texto: 'Retorne com calma e prepare água e material de estudo.' }
      ]
    },
    {
      id: 'recuperacao-tranquila-10',
      nome: 'Recuperação tranquila',
      objetivo: 'Variar posições com baixa intensidade antes de retomar.',
      duracao: 10,
      intensidade: 'Muito leve',
      ambientes: ['casa', 'biblioteca', 'faculdade'],
      filtros: ['silencioso', 'sem-suar', 'pouco-espaco', 'sentado', 'depois-treino'],
      instrucoes: [
        { segundos: 120, texto: 'Ajuste a posição e movimente mãos e tornozelos devagar.' },
        { segundos: 180, texto: 'Se puder, levante e alterne os apoios com conforto.' },
        { segundos: 180, texto: 'Caminhe poucos passos ou permaneça em movimento leve.' },
        { segundos: 120, texto: 'Diminua o movimento e organize a volta ao foco.' }
      ]
    }
  ];
})();
