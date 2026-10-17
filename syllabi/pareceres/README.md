# Pareceres curriculares individuais (esquema v2)

Cada arquivo `syllabi/pareceres/<curso>/<CODIGO_BR>__<universidade>__<CODIGO_ESTR>.json` registra **um** cotejo
documental entre uma disciplina Mackenzie e uma (ou, em `type: "combinada"`, mais de uma) disciplina estrangeira.
O padrão mínimo de profundidade é `cc/ENEC61020__ro-babes__MLE5077.json`. Ele é referência de **profundidade**, não
de conclusão: cada parecer deve chegar à sua própria conclusão a partir dos documentos.

Nenhum parecer é homologação. `institutionalStatus` permanece `aguardando_validacao_institucional` até existir
documento formal de decisão do Mackenzie (`decisionDocument.url`).

Quando o documento oficial possui o campo Ementa vazio, `brazil.topics` permanece vazio. O cotejo
registra somente um marcador explícito de pendência documental com estado `nao_verificavel`,
identificado na nota como marcador e não como tópico curricular. Bibliografia não substitui ementa;
esses casos permanecem `evidencia_insuficiente` até a obtenção do plano de ensino completo.

## Como produzir

1. `python scripts/fetch_documents.py` (cache incremental; documentos ficam em `.cache/`, fora do Git).
2. `python scripts/make_dossier.py <curso> <codigo_br> <universidade> <codigo_estr>` gera `.cache/dossiers/*.md`
   com os dois textos oficiais e os campos extraídos.
3. Ler **integralmente** os dois textos. Escrever o JSON.
4. `python scripts/build_pareceres.py` valida e publica `syllabi/pareceres-index.json`.

## Campos obrigatórios e regras

| Campo | Regra |
|---|---|
| `brazil.topics` | Reproduz exatamente os tópicos oficiais de `programas.json` (`brazil.<curso>|<codigo>.topics`). |
| `topics[]` | Um item para **cada** tópico oficial brasileiro, com `brTopic` idêntico. `status`: `coberto`, `parcial`, `nao_encontrado`, `nao_verificavel`. |
| `topics[].foreignEvidence` + `foreignLocation` | Obrigatórios para `coberto`/`parcial`: unidade/item e secção do documento estrangeiro. Citação curta (≤ 25 palavras) ou paráfrase. |
| `topics[].scopeExamined` | Obrigatório para `nao_encontrado`: quais secções foram lidas. |
| `topics[].essential` | `true` por padrão. Use `false` apenas para itens não curriculares (ex.: "Práticas de Extensão"), explicando em `note`. |
| `foreign[].hours` | Copiar valores explícitos: `contactTotal`, `contactLecture`, `contactSeminarLab`, `selfStudy`, `totalWorkload`, `ects`, `basis` (`semestre`/`semana`/null), `hourLengthMinutes` (só se o documento declarar). **Nunca** derivar horas de ECTS. |
| `brazil.hours` | `{value, unit: "hora_relogio", basis: "semestre"}` do ementário 2025. Direito 2022 informa horas-aula semanais → `basis: "semana"`. |
| `conclusionClass` | Não pode ser mais favorável que a classe derivada pelas regras (ver abaixo). Classe mais conservadora exige `downgradeReason`. |
| `confidence` | `alta`/`moderada`/`baixa`, conforme completude dos documentos (não conforme a segurança do texto). |
| `synthesis`/`justification` | Específicos do par: nomear unidades, números e divergências. Textos quase idênticos entre pareceres são rejeitados. |
| `limitations` | Sempre listar oferta 2027/28 não confirmada e demais incertezas. |

### Regra interna de classificação (não é fórmula oficial)

Parâmetro de referência: 75% de compatibilidade de carga horária e conteúdo (Manual do Intercâmbio 2024, vigência
e interpretação a confirmar com a COI).

- `evidencia_insuficiente`: algum documento individual oficial ausente, ou mais de 1/3 dos tópicos essenciais `nao_verificavel`.
- `alta_afinidade`: ≥ 75% dos tópicos essenciais `coberto`, nenhum `nao_encontrado`, horas de contato semestrais
  analisáveis com razão ≥ 0,75 e ementa brasileira vigente.
- `afinidade_parcial`: `coberto` + `parcial` ≥ 50% dos tópicos essenciais.
- `baixa_afinidade`: demais casos.

### Carga horária

- `comparavel`: ambos semestrais e duração da hora estrangeira declarada.
- `comparavel_condicional`: ambos semestrais, duração da hora estrangeira não declarada (calcula-se também o cenário de 50 min).
- `nao_comparavel`: apenas ECTS, horas semanais ou dados ausentes. A diferença numérica não é calculada.

## Proibições

Não declarar equivalência por título; não inventar conteúdo; não converter ECTS em horas; não confundir hora-aula
com hora-relógio; não usar documento antigo como vigente; não tratar ausência de dados como reprovação; não usar
"homologada"/"aprovada" sem decisão formal; não repetir texto genérico.
