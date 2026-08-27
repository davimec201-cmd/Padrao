# Copeiro Performance — primeira entrega

O módulo conecta o fim de um bloco de foco a uma pausa de movimento opcional.
Os protocolos são pilotos e ficam centralizados em
`performance-protocols.js`, sem alegação de prescrição ou aprovação
profissional.

## Dados locais

Configuração, eventos, protocolos concluídos e atividades manuais ficam dentro
do mesmo objeto `copeiro.v1` já usado pelo aplicativo. A migração acrescenta o
novo ramo sem alterar blocos, Copas, cartas, Álbum ou preferências existentes.
O backup JSON exporta e restaura esse ramo junto com os demais dados.

Os eventos locais usam nomes estáveis para análise futura: convite visto,
aceito ou recusado; ativação e desativação; protocolo iniciado, concluído ou
pulado; feedback; atividade registrada ou excluída; retorno ao foco; e dia com
foco e movimento. A lista fica limitada aos 500 eventos mais recentes e não
inclui nome, observações nem outros identificadores pessoais. Ela já permite
calcular ativação, adesão, conclusão, retorno e uso recorrente sem simular
pagamento ou assinatura.

## Integração futura com o Álbum

A coleção bônus “Preparação Física” ficou deliberadamente fora da primeira
entrega. A implementação futura deve ser uma coleção opcional, derivada dos
marcos cumulativos do Performance, sem participar da porcentagem, dos pacotes
ou dos requisitos de conclusão do Álbum principal. Assim, quem mantiver o
Performance desligado nunca verá uma coleção obrigatória incompleta.

## Revisão profissional pendente

Antes de remover o aviso de piloto, um profissional de Educação Física deve
revisar nomes, objetivos, intensidade, adequação dos ambientes e cada instrução
de todos os protocolos. Nome, CREF ou aprovação não devem ser publicados antes
dessa revisão real.
