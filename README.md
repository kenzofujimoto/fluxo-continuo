# Fluxo Contínuo — pesquisa independente de mobilidade 2027.2

> **Projeto acadêmico independente e não oficial.** Pesquisa de possíveis aproveitamentos curriculares para o campus Mackenzie Alphaville, não homologações institucionais.

## Aplicação pública (Next.js)

O site agora é uma aplicação Next.js 16, React 19 e TypeScript estrito. A consulta é 100% pública, sem autenticação, administração, API de escrita ou banco. Os JSONs versionados continuam sendo a fonte de verdade; a camada `lib/data.ts` valida os campos consumidos com Zod e calcula indicadores a partir dos registros, sem depender dos resumos históricos abaixo.

```sh
npm ci
npm run dev
```

Abra `http://localhost:3000`. Para produção, execute `npm run build` e `npm start`. O deploy precisa usar o framework Next.js e não um servidor de arquivos HTML. Não é necessário configurar variáveis de ambiente ou Neon.

Rotas: `/disciplinas`, `/universidades`, `/comparacoes`, `/ementas`, `/idiomas`, `/pendencias`, `/cobertura`, `/metodologia`. Disciplinas, instituições e pareceres têm URLs próprias. Filtros, buscas e paginação permanecem na URL e funcionam sem JavaScript no navegador. URLs antigas `.html` redirecionam para a aplicação; os arquivos antigos permanecem como referência histórica no repositório.

Validação: `npm test`, `npm run lint`, `npm run build`, `python -X utf8 -m pytest -q tests` e `node validate.js`. A CI também executa esses comandos. Detalhes de arquitetura, atualização e lacunas: [docs/PUBLIC_APP.md](docs/PUBLIC_APP.md).

**Os números abaixo são um retrato histórico da coleta; os indicadores atuais da aplicação vêm dos registros e podem divergir desse retrato.**

**Site principal:** https://fluxo-continuo.vercel.app  
**Acervo de ementas e evidências:** https://fluxo-continuo.vercel.app/ementas.html  
**Pendências por disciplina e universidade:** https://fluxo-continuo.vercel.app/pendencias.html  
**Comparações curriculares:** https://fluxo-continuo.vercel.app/analises.html  
**Cobertura por universidade:** https://fluxo-continuo.vercel.app/cobertura.html  
**Página de idiomas:** https://fluxo-continuo.vercel.app/idiomas.html

## Estado auditado da base — 16/10/2026

| Indicador | Quantidade |
| --- | ---: |
| Cursos Mackenzie | 4 (CC, SI, Administração e Direito) |
| Componentes curriculares brasileiros | **221** (47 CC, 46 SI, 47 Administração, 81 Direito) |
| Universidades da planilha COI | **66** |
| Universidades com pelo menos uma disciplina individual indexada | **66/66** |
| Instituições com elegibilidade COI Sim em um dos quatro cursos | **55/66** |
| Disciplinas estrangeiras com registro e fonte | **2.608** |
| Relações preliminares e indícios cadastrados | **725** |
| Pares com sugestões lexicais (base atualizada) | **501** |
| Cruzamentos elegíveis na triagem inicial | **6.856** |
| Aproveitamentos formalmente homologados | **0** |

**A indexação das 22 universidades pendentes foi concluída no nível mínimo de título e fonte acadêmica. Isso NÃO equivale a comparar integralmente todas as ementas.** Os 725 registros e 501 sugestões têm sobreposição, não devem ser somados e não são aprovações institucionais. As 11 universidades sem marcação COI Sim em nenhum dos quatro cursos têm registros documentais, mas não são destinos elegíveis para essas matrizes.

### Última expansão

- **Universidad Evangélica Boliviana:** 59 disciplinas de Engenharia de Sistemas e 57 de Administração Geral, com códigos institucionais, semestres, créditos locais CR e pré-requisitos em PDFs vinculados pela universidade; ano de vigência a confirmar.
- **Universidad Alfa y Omega (México):** 42 disciplinas de Administração, 42 de Direito e 48 de Informática Administrativa em PDFs oficiais com códigos e semestre. A instituição não consta como elegível nos quatro cursos.
- **Universidade Lusíada Lisboa:** 84 disciplinas de Gestão e Direito da matriz de 2025/26.
- **Outras 19 universidades:** matrizes e páginas acadêmicas catalogadas, incluindo IPCB, UPAL, Konkuk, Florence University of the Arts, Nevşehir, BML Munjal, ISG, Viaa e instituições sem elegibilidade COI.

Os **3.920 pares** anteriormente marcados I receberam triagem de títulos: 140 pares apresentaram afinidades lexicais, 279 mantiveram candidatos manuais sem novo sinal, 142 mantiveram sugestões anteriores e 3359 ficaram sem indícios fortes nos catálogos parciais. Não houve cotejo de ementas ou CH.

## Pareceres curriculares individuais — estado em 16/10/2026

| Indicador | Quantidade |
| --- | ---: |
| Ementas Mackenzie oficiais vinculadas | **178** (75 vigentes CC/SI 2025 · 41 Administração sem ano impresso · 62 Direito 2022 histórico) |
| Programas estrangeiros individuais lidos e versionados por hash | **329** |
| Candidaturas com documentos oficiais dos dois lados | **133** |
| Pareceres individuais tópico a tópico | **133** (4 alta afinidade · 67 parcial · 55 baixa · 7 evidência insuficiente) |
| Pareceres com horas analisáveis | 41 (2 comparáveis · 39 condicionais) |
| Cruzamentos com estado de pesquisa justificado | **6.856/6.856** |
| Novas candidatas por conceitos (não por título) | 1.138 disciplinas em 572 cruzamentos · 13 combinações de duas disciplinas |
| Ementas estrangeiras a obter | 894 |
| Cruzamentos bloqueados por catálogo insuficiente | 3.754 |
| Equivalências homologadas | **0** |

- Pareceres e prioridades: [analises.html](https://fluxo-continuo.vercel.app/analises.html). O que solicitar a cada coordenação e universidade: [pendencias.html](https://fluxo-continuo.vercel.app/pendencias.html), aba "O que solicitar".
- Regras institucionais aplicadas: `docs/coi/`. Esquema e regras dos pareceres: `syllabi/pareceres/README.md`. Método: `METODOLOGIA.md`.

```bash
python -m pip install -r scripts/requirements-audit.txt pytest
python -m pytest -q tests
python scripts/fetch_documents.py            # cache incremental + campos estruturados
python scripts/build_pareceres.py            # valida pareceres e publica o índice
python scripts/semantic_triage.py            # estado de pesquisa dos 6.856 cruzamentos
python scripts/report_requests.py            # pendências documentais por instituição
python scripts/validate_audit.py && node validate.js
```

## Como usar

- No celular: explore **cartões por disciplina**, expanda para ver universidades e fontes, ou ative o modo **Tabela**.
- No desktop: use a grade disciplinas do Mackenzie (linhas) × universidades (colunas).
- Filtre curso, etapa, universidade e situação da pesquisa.
- Uma célula pode ter múltiplas candidatas estrangeiras. Confira a ficha e **a fonte oficial** antes de considerar o Plano de Estudos.
- Abra **Idiomas e provas** para requisitos da COI, testes de língua, preços de referência e benefícios anunciados; confirme vigência diretamente com os provedores.
- Exporte CSV para trabalhar e compartilhar a auditoria.

## Dados e método

- `data.json`: universidades, elegibilidade, matrizes curriculares, disciplinas estrangeiras e sugestões de correspondência.
- `triagem.json`: resultado automatizado e limitado da triagem dos **6.856 pares elegíveis**.
- `triagem-view.js`: visualização da triagem na tabela desktop.
- `mobile.js` e `mobile.css`: exploração por cartões no celular.
- `METODOLOGIA.md`: o que foi e não foi verificado.
- `cobertura.html`: mapa responsivo de 66 instituições, sem confundir ausência de catálogo com incompatibilidade.
- `validate.js`: validação cruzada dos arquivos de dados.
- `index.html`, `app.js` e `styles.css`: aplicação sem login e sem backend.

### Significado dos estados

1. **Candidata forte**: conteúdo apresenta relação significativa, mas ainda não implica aproveitamento homologado.
2. **Em análise**: proposta que exige complementação documental.
3. **Indício pelo título**: apenas nome/código de catálogo oficial, sem cotejo integral das ementas. **Não corresponde a porcentagem de equivalência.**
4. **Sem candidato encontrado na base parcial**: não significa incompatibilidade nem ausência de matérias na universidade.

É necessário verificar as ementas de ambas as instituições, a carga horária de contato, a versão curricular, a oferta no semestre, o idioma, as restrições de matrícula e as regras de aproveitamento. A decisão final pertence à coordenação do Mackenzie e aos responsáveis pela mobilidade.

## Cobertura e confiabilidade

O XLSX da COI foi importado para 2027.2. Os **66 registros e respectivos campos de elegibilidade por curso** são independentes da disponibilidade de cada disciplina. Há campos de idioma corrompidos/inconsistentes em algumas linhas de instituições portuguesas; nesses casos, a informação está marcada para verificação. Em Direito, nomes aparentemente semelhantes podem designar sistemas jurídicos nacionais diferentes.

## Execução local

Na raiz deste repositório:

```bash
python -m http.server 8000
```

Acesse http://localhost:8000. O projeto é estático, sem login nem Neon, com implantação automática na Vercel ligada à branch `main`.

## Fontes e responsabilidade

- [Comissão de Intercâmbio Internacional (COI) — Fluxo Contínuo](https://www.mackenzie.br/universidade/fluxo-continuo)
- [Mackenzie Language Center — exame de intercâmbio](https://portal.mackenzie.br/mackenzie-language-center/cursos-especificos/exame-para-intercambio-coi)
- Catálogos e ementas estrangeiras: links oficiais individualizados em `data.json`.
- As ofertas de cursos e valores de exames podem mudar sem aviso; consulte sempre a COI, a universidade anfitriã e a coordenação antes de tomar decisões.

**O projeto Fluxo Contínuo não é afiliado nem endossado pelo Mackenzie e não emite pareceres acadêmicos.**

## Limitações e fontes acrescentadas (16/10/2026)

- O índice acadêmico cobre apenas documentos coletados; 2027/28, horários, acesso externo, equivalência de horas e programas individuais ainda podem mudar.
- A auditoria oficial Alphaville 2025 conseguiu vincular 35/47 ementas de CC e 40/46 de SI. Para Direito, o PDF de 2022 disponibiliza 45 correspondências de títulos na matriz, mas **não valida a versão vigente**. Administração ainda requer o ementário oficial aplicável à matriz atual.
- Fontes institucionais agregadas: [Ferrara](https://corsi.unife.it/it/lm-giurisprudenza/studiare/didattica/progr/programma-del-corso-e-dei-curricula-n-o), [Tor Vergata](https://cdl.giurisprudenza.uniroma2.it/a-a-2025-2026/) e [Salerno](https://corsi.unisa.it/giurisprudenza/didattica/insegnamenti).
- Códigos internos `CAT-*` não são códigos oficiais. O exame individual de cada ementa, carga horária e semestre permanece obrigatório.
- Os pares I históricos foram reavaliados por título; S não significa incompatibilidade e P não significa equivalência.
- Em caso de dúvida, siga a planilha atual da COI e a coordenação do Mackenzie. Não existe aproveitamento aprovado na base.

Para validar o banco localmente, execute `node validate.js`.


## Auditoria individual de ementas (16/10/2026)

A base de catálogos e a análise curricular são conjuntos **distintos**. Consulte [o acervo de ementas](https://fluxo-continuo.vercel.app/ementas.html) para o estado documental **por disciplina**, derivado de links institucionais individuais, sem converter nomes semelhantes em equivalências.

Arquivos gerados: `syllabi/coverage-report.json` informa detalhadamente quais disciplinas ainda carecem de ementa individual ou de horas; `syllabi/direito-historico-2022.json` preserva separadamente os programas históricos; `syllabi/revisoes-ementas.json` registra as análises individuais fundamentadas. `syllabi/records.json` contém fonte, identificação do programa, ano, integridade SHA-256, status, horas de contato quando explícitas e marcadores temáticos; `syllabi/metrics.json` resume resultados; `syllabi/backlog.json` agrupa lacunas; `syllabi/comparacoes.json` cruza evidências documentais dos candidatos registrados e as 6.856 células elegíveis. `syllabi/source-inventory.json` documenta os domínios examinados.

A rotina `scripts/collect_syllabi.py` distingue documentos individuais de catálogos compartilhados, verifica a identidade da disciplina e registra somente metadados/proveniência, mantendo PDFs e programas completos nas URLs oficiais. A rotina `scripts/compare_evidence.py` procura **sinais temáticos controlados** em ementas brasileiras de fonte oficial 2025 vinculadas à matriz e em programas estrangeiros identificados. Sinais compartilhados **não são percentuais de cobertura curricular**; a carga horária do Mackenzie pode ter base distinta das horas de contato estrangeiras. Falta decisão humana fundamentada sobre todos os conteúdos, ementas brasileiras atuais e equivalência de horas.

Para repetir a coleta via GitHub Actions, execute `Coletar evidencias de ementas` em *Actions*. Localmente:

```bash
python -m pip install -r scripts/requirements-audit.txt
python scripts/collect_syllabi.py
python scripts/collect_mackenzie.py
python scripts/collect_historical_law.py
python scripts/compare_evidence.py
python scripts/report_coverage.py
node validate.js
python scripts/validate_audit.py
```

O número de documentos recuperados varia por acessibilidade dos sites; não interpretar erro HTTP, ausência de programa, URL ainda não visitada ou catálogo parcial como impossibilidade de aproveitamento. Os dados gerados **não** constituem aprovação, homologação ou atestado de oferta 2027.2.


### Legenda da matriz — cores ≠ provas documentais

- Rosa: candidatura forte já cadastrada, porém não homologada e não necessariamente revisada por ementa.
- Amarelo: candidatura em análise documental.
- Azul/lilás: indício lexical por títulos de disciplinas.
- Alaranjado: atenção ao semestre/período de oferta.
- Branco/cinza: sem candidata cadastrada ou sem sinal lexical. Não equivale a incompatibilidade.

As etiquetas **independentes da cor** dentro de cada célula discriminam: nenhuma, uma ou duas ementas individuais obtidas ou análise comparativa individual registrada (não homologada). O número de programas obtidos é atualizado em `syllabi/metrics.json` e em `syllabi/coverage-report.json`.

Nenhuma relação foi aprovada institucionalmente. Para Direito, 2022 é fonte histórica; "2 horas-aula" semanais não devem ser confundidas com carga horária semestral e não provam a vigência do componente. Para Administração, não usar o ementário de Campinas como se fosse o do campus Alphaville.
