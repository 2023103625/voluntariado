Conjunto de dados de teste — Programa de Voluntariado e Extensão Universitária

Contexto:
- Dados fictícios, mas realistas, pensados para estudantes universitários em Portugal.
- O conjunto inclui voluntários, entidades promotoras, ações, inscrições, presenças e catálogo de ODS.
- Os CSV estão normalizados por tabelas auxiliares; os JSON estão em formato mais aninhado.

Resumo:
- 60 voluntários
- 14 entidades promotoras
- 30 ações
- 650 inscrições
- 238 registos de presença

Tabelas CSV:
- ods_catalogo.csv
- voluntarios.csv
- voluntarios_competencias.csv
- voluntarios_tags.csv
- voluntarios_ods.csv
- entidades.csv
- entidades_tags.csv
- entidades_ods.csv
- acoes.csv
- acoes_competencias.csv
- acoes_ods.csv
- inscricoes.csv
- presencas.csv

Ficheiros JSON:
- ods_catalogo.json
- voluntarios.json
- entidades.json
- acoes.json
- inscricoes.json
- presencas.json
- dataset_completo.json

Notas de modelação:
- Campo 'ano' só é preenchido para voluntários com vínculo 'estudante'.
- Estados de ação: planeada, concluída, cancelada.
- Estados de inscrição: pendente, aprovada, rejeitada, lista de espera.
- 'metrica_impacto' usa 0–100; para ações futuras/canceladas foi colocado 0.
- 'horas_registadas' permite calcular estatísticas por voluntário e por ODS em ações concluídas.
