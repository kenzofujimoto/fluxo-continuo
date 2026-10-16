# Triagem de cobertura — Fluxo Contínuo (16/10/2026)

6.856 pares curso/disciplina/universidade **submetidos a triagem automática de nomes e metadados**, NÃO a cotejo completo de ementas. Não existe homologação acadêmica nesta base.

- D: pré-análise documental; não homologada.
- P: afinidade lexical, sem comparação de 75% de conteúdo/horas.
- T: possível afinidade de disciplina anual ou semestre incompatível.
- S: lista estrangeira PARCIAL indexada não apresenta candidato suficientemente similar. Não indica incompatibilidade.
- C: catálogo identificado, sem coleta da lista individual.
- F: falta catálogo com disciplinas (estado histórico, sem pares atuais).
- I: catálogo já foi indexado, mas esta combinação ainda não passou por nova triagem individual.

0–100 nas células é **pontuação lexical**, jamais porcentagem de equivalência.

**Limitações:** SI possui 41/46 ementas extraídas; Direito possui 63/81 de edição 2022; Administração ainda não possui ementário validado; em todos os cursos ainda faltam horas de contato e cotejo completo estrangeiro; em Direito há ementário 2022 a atualizar para matriz 2024. Contato e semestre 2027/28 precisam confirmação. Leis espanholas não equivalem automaticamente às brasileiras. ECTS não convertem automaticamente em horas.

Fontes: planilha COI recebida; ementário Mackenzie; lista oficial UBB: https://www.cs.ubbcluj.ro/apps/fise/viewSyllabi.php?an=2026&lang=en&specializare=IE; lista UCA: https://esingenieria.uca.es/docencia/grados/gii/asignaturas/. Decisões são da coordenação e do RINT.


## Ampliação concluída da indexação institucional — 16/10/2026

A pesquisa passou a ter **66 de 66 instituições com pelo menos uma disciplina nomeada**, total de **2.608 registros estrangeiros** e **725 indícios/preanálises** (0 homologações). **55** instituições são elegíveis na planilha COI em pelo menos um dos 4 cursos; outras **11** têm disciplinas de referência, mas não são elegíveis para estas matrizes.

Foram examinados planos institucionais diversos, alguns históricos, além de cursos de tecnólogo, graduação e mestrado. Não inferir conversão de ECTS, créditos coreanos, norte-americanos, turcos, italianos, colombianos ou bolivianos em horas. Não inferir oferta 2027.2. Não presumir que um aluno pode cursar qualquer unidade da universidade.

**UEB:** 59 Engenharia de Sistemas e 57 Administração Geral, créditos locais, semestres e pré-requisitos, sem data identificável de vigência do PDF. **Alfa y Omega:** 132 unidades nas matrizes oficiais de Administração, Direito e Informática Administrativa, sem elegibilidade COI nos quatro cursos. **Lusíada Lisboa:** 84 unidades de Direito e Gestão em 2025/26, sem oferta futura garantida.

**3.920** pares históricos I reprocessados apenas por títulos: 140 afinidades lexicais, 279 cadastrados anteriormente, 142 com sugestão anterior e 3359 sem sinal lexical forte. Não implica incompatibilidade ou aprovação.

O Brasil possui ementários incompletos: SI 41/46 extraídos, Direito 63/81 de edição antiga, Administração requer ementário validado. O resultado final de equivalência depende do Mackenzie, não deste projeto.

## Rescreen conservador de nomes (16/10/2026)

O cotejo automatizado da segunda rodada usa normalização multilíngue de títulos, Dice lexical ≥ 0,70, pelo menos dois termos em comum ou um título de termo único, e evita misturar códigos de sequência I/II distintos. As faixas 0–100 são pontuações de nome, **não percentuais de equivalência**. Ausência de sugestão S significa apenas ausência de sinal de título no catálogo indexado. Nenhum programa 2027/28 foi homologado.

## Pareceres curriculares individuais (esquema v2) — 16/10/2026

A partir desta versão, a base distingue quatro dimensões que **nunca são misturadas**:

1. **Cor da candidatura** (matriz): força do indício cadastrado ou encontrado por conceitos.
2. **Estado das evidências**: sem ementa, uma ementa, duas ementas, horas verificadas.
3. **Parecer curricular**: `alta_afinidade`, `afinidade_parcial`, `baixa_afinidade` ou `evidencia_insuficiente`, sempre com status `aguardando_validacao_institucional`.
4. **Homologação**: só com documento formal de decisão do Mackenzie. Hoje: **zero**.

### Fontes e regras institucionais

- Regras da COI registradas em `docs/coi/` com página e seção (Manual do Intercâmbio 2024 §3.3, §3.4, §6.4, §6.6; Orientações 2022). O parâmetro de 75% de compatibilidade de carga horária **e** conteúdo é usado como referência interna; o Manual não define fórmula de medição, então nenhuma pontuação é apresentada como oficial. O limite de 25% da carga do curso e a dispensa de correspondência de semestre também estão registrados.
- Ementas brasileiras: CC e SI Alphaville 2025 (vigentes); Administração — fichas CCSA oficiais vinculadas à página da matriz de Alphaville, **sem ano impresso** (vigência não confirmada); Direito — ementário Alphaville **2022, histórico**. Ementa não vigente limita o parecer a, no máximo, afinidade parcial.
- Documentos estrangeiros: somente programas individuais oficiais, com SHA-256, data de coleta e localização (seção/item) de cada evidência.

### Como cada parecer é produzido e validado

1. `scripts/fetch_documents.py` baixa (de forma incremental, com ETag/Last-Modified) e lê os documentos oficiais; `syllabi/documentos.json` guarda a proveniência e `syllabi/programas.json`, os campos explícitos (horas por tipo, ECTS, ano, nível, pré-requisitos, tópicos oficiais brasileiros).
2. Leitura integral dos dois documentos (assistida por IA) e registro de **cada tópico oficial brasileiro** como coberto, parcial, não encontrado ou não verificável, com evidência e localização.
3. `scripts/build_pareceres.py` recalcula a cobertura e a comparabilidade das horas, confere hash, horas, ECTS e redação dos tópicos contra os documentos, rejeita classe mais favorável que a evidência, linguagem de homologação e textos repetitivos entre pareceres.

### Carga horária

- Mackenzie: horas-relógio semestrais (63,33 h = 4 h-a semanais de 50 min no ementário FCI). Direito 2022 e parte das fichas de Administração informam apenas horas-aula semanais: **não comparáveis**.
- Estrangeiras: só horas de contato semestrais explícitas. ECTS (25–30 h de trabalho total por crédito, Manual §3.4) **nunca** são convertidos.
- `comparavel` exige a duração da hora estrangeira; quando ela não é declarada (caso da UBB), a comparação é `comparavel_condicional` e o cenário de 50 min é mostrado ao lado.

### Triagem dos 6.856 cruzamentos

`scripts/semantic_triage.py` usa um tesauro multilíngue controlado (99 conceitos; pt, en, es, ca, it, fr, ro) ponderado por IDF. Uma candidata exige que conceitos de identidade apareçam dos dois lados (o título estrangeiro compartilha conceito com a ementa e a disciplina estrangeira contém conceito do título brasileiro). Cada cruzamento recebe um estado: parecer concluído, candidata registrada, candidata por conceitos, regra específica (TCC/estágio/optativa livre), sem candidata no catálogo indexado ou catálogo insuficiente. **Nenhum estado significa incompatibilidade.**

### Limitações conhecidas

- 3.754 cruzamentos dependem de ampliar a coleta de catálogos estrangeiros.
- 894 disciplinas estrangeiras candidatas ainda não têm programa individual obtido.
- Administração e Direito dependem de confirmação da vigência das ementas pela coordenação.
- O Regulamento RE CONSU 17/2014 é PDF digitalizado sem texto extraível; o edital específico de 2027.2 não foi localizado.
- 72 pareceres pedem segunda revisão (ano do documento divergente, hora não declarada, mesma disciplina estrangeira candidata a dois requisitos, inconsistências do próprio documento oficial).
