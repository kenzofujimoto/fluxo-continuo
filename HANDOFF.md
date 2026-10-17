# Interactive globe checkpoint — 2026-10-16

- Branch: `feature/interactive-globe`. Feature commit: `2680bb2`; failing tests: `a862010`; geodata: `d51b796`.
- Production preview: http://127.0.0.1:3002 (running exec session `40718`). No push or deploy.
- Home now has a dark interactive Globe.GL hero. `/universidades` has public search/course/eligibility filters, globe/list views, keyboard selection and institutional links. No login/database.
- Local Natural Earth geometry: `public/maps/countries.geojson`. Versioned coordinates: `data/university-locations.json`: 57 mapped of 66 universities; nine pending locations stay in the list. Institutional points do not certify the campus offering exchange classes; source/precision/notes are shown.
- Validation: nine TypeScript tests plus 57 Python tests (66 total), lint/types/build pass. HTTP checks pass for home, destinations, eligibility, empty searches and geography. Visual layout and actual WebGL interactions remain unverified because browser automation was unavailable.
- Operational details/manual checklist: `docs/interactive-globe.md`; coordinate sources/pending institutions: `docs/GLOBE_LOCATIONS.md`.
- Existing incoming research and untracked syllabi were preserved. Keep preview session running for user review.

---
# HANDOFF — aplicação pública (16/10/2026)

Branch atual: `feature/public-app`. Escopo aprovado: aplicação pública Next.js/TypeScript, identidade visual MackJr e comparação documental; Neon, API de escrita e administração foram adiados explicitamente pelo usuário.

- Implementado: início, disciplinas e universidades com detalhes, biblioteca de ementas, idiomas, comparações com evidências por tópico lado a lado, pendências, cobertura e metodologia. Buscas e filtros usam URLs compartilháveis; listas paginam; rotas HTML antigas redirecionam.
- Fonte de verdade: JSONs existentes no Git, validados na camada `lib/data.ts` com Zod. Fontes, vigência, hashes e revisão aparecem nas consultas. Nenhuma nova equivalência foi inventada ou homologada.
- Identidade: paleta e fontes reais do projeto MackJr local, carregadas sem chamadas externas. Layout responsivo, navegação por teclado, estados de erro/carregamento/404.
- Execução: `npm ci`, `npm run dev`; produção `npm run build` e `npm start`. Servidor de produção para revisão nesta sessão: `http://127.0.0.1:3001`. Sem deploy ou push nesta implementação.
- Validação: sete contratos TypeScript, 51 testes Python, validação Node, lint/typecheck, build de produção, 133 pareceres e auditoria documental aprovados. Testes iniciais foram registrados falhando no commit `db680a3`; a regressão de URLs com acentos foi reproduzida em `8364632` e corrigida em `b0d41b5`.
- Auditoria npm: zero vulnerabilidades de produção; cinco achados altos transitivos de desenvolvimento no encadeamento ESLint/glob, sem downgrade forçado. Detalhes em `docs/PUBLIC_APP.md`.
- Alterações anteriores em scripts de coleta, testes Python e arquivos não rastreados foram preservadas e não pertencem aos commits da aplicação.
- Próximo passo operacional: revisar visualmente e publicar como aplicação Next.js quando solicitado. Coleta adicional e segunda revisão continuam pendentes conforme `/pendencias`; não é necessário banco para a consulta pública atual.
- O navegador automatizado não ficou disponível nesta sessão; a revisão independente validou renderização HTTP, navegação por URLs, filtros, redirecionamentos, ausência de resultados e evidências do parecer. Detalhes técnicos: `docs/PUBLIC_APP.md`.

## Checkpoint anterior preservado

# HANDOFF — análise curricular profunda (checkpoint 16/10/2026)

Branch: `feature/pareceres-curriculares`. Nada foi publicado em `main`; a Vercel publica apenas `main`.

## Concluído nesta sessão

| Fase | Estado | Evidência |
|---|---|---|
| 1. Diagnóstico e infraestrutura | Concluída | `scripts/fetch_documents.py` (cache incremental, manifesto SHA-256), `scripts/program_fields.py` (UBB, FCI, fichas CCSA/Direito), `scripts/build_pareceres.py` (validação), 44 testes em `tests/` |
| 2. Ementários brasileiros | Concluída no que é público | 178/221 vinculadas: CC 35 e SI 40 vigentes; Administração 41 oficiais sem ano; Direito 62 de 2022 (histórico). Pedidos por componente em `syllabi/pendencias-documentais.json` |
| 3. Candidaturas com ementas dos dois lados | Concluída | 133/133 com parecer v2 (`syllabi/pareceres/`) |
| 4. Coleta estrangeira | **Não iniciada nesta sessão** | Backlog: 894 programas a obter, 3.754 cruzamentos com catálogo insuficiente |
| 5. Descoberta semântica | Concluída (1ª versão) | `syllabi/triagem-semantica.json`: 6.856 estados, 1.138 candidatas novas |
| 6. Pareceres | Parcial | Feitos todos os pares com documentos; as 1.138 candidatas novas e as 493 células registradas sem documentos aguardam a Fase 4 |
| 7. Auditoria final | Parcial | CI atualizado; segunda revisão pedida em 72 pareceres |
| Regras COI | Concluída | `docs/coi/` (Manual 2024 §3.3/§3.4/§6.4/§6.6) |

## Próximo lote prioritário (em ordem)

1. **Fase 4, universidades com mais candidatas e guias padronizados**: abrir `pendencias.html` → "O que solicitar" (ordenado por volume). Começar pelas instituições com catálogo de guias individuais (UAB `apps.uab.cat/guies`, Jaén, Salamanca, Cádiz, Coimbra `apps.uc.pt`, UBB `fise`) e adicionar os programas encontrados em `syllabi/fontes-verificadas.json` (`{"foreign":[{"universityId","code","source","individualSyllabus":true}]}`); depois rodar `fetch_documents.py` → `make_dossier.py` → parecer → `build_pareceres.py`.
2. Pareceres das alternativas citadas pelos agentes e não lidas: Coimbra 97282, 100127, 100137, 20923, 93362; UAB 102234, 102287; UBB MLE5011, MLE5172/5173; Cádiz 21714032 e 21714022.
3. Corrigir falsos positivos antigos de `records.json`: `ch-15-universidaddie|CAT-teoria-y-filosofia-del-derecho` (folheto, não ementa); hashes divergentes de Jaén/Salamanca (recoleta já resolvida em `documentos.json`).
4. Segunda revisão dos 72 pareceres marcados (`secondReview.required`).
5. Pedir à COI: edital 2027.2 e leitura/OCR do RE CONSU 17/2014; às coordenações: vigência das fichas de Administração e ementário vigente de Direito (contatos no relatório).

## Cuidados

- Na Bash deste ambiente, heredocs podem alterar barras invertidas: escrever código com a ferramenta de edição.
- `python -m http.server` + navegador mantêm JS em cache; recarregue sem cache ao testar.
- Nenhum parecer é homologação; não alterar `institutionalStatus` sem documento formal.
