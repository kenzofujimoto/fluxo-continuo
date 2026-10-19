# Simplified home preview — 2026-10-19

- Approved separate local mock: http://127.0.0.1:3002/teste-inicio . Existing home and global layout/styles remain unchanged.
- Short headline, one sentence, two primary paths, interactive globe and accessible destination selector. Removed metrics/cards/research detail from this preview only.
- Desktop visual verified: globe loads, changing destination updates institution link. Screenshot: .cache/simple-home-preview.jpg. Do not apply this design to home or publish it until user chooses.
- Original flags were pushed to fix/flag-preview; draft PR #3: https://github.com/kenzofujimoto/fluxo-continuo/pull/3 . Simplified-home mock remains local.
# Local flag comparison mock — 2026-10-19

- Branch: fix/flag-preview. Local preview: http://127.0.0.1:3002/teste-bandeiras (server session 52327).
- User requested original colors alongside MackJr palette before applying changes. Compare 21 countries in light headers, dark cards and a complete contact sheet. Production CountryFlag and original SVG assets remain unchanged. No push or deployment.
- Commits: 5909258 (failing regression), 75b1b06 (implementation). Full 96 tests, lint and build passed. Browser verified 50 loaded images and no CSS filters; visual snapshot: .cache/flag-preview.jpg.
- Await user preference before integrating either option into the main site. Preserve existing untracked directories.
# Published checkpoint — 2026-10-19

- PR #2 was created as draft, checks passed, marked ready and merged: https://github.com/kenzofujimoto/fluxo-continuo/pull/2 . Merge commit9dd145a67987c4445fd82249d753bfe7ea00851a; origin/main then auto-generated a coverage timestamp-only commitd1db2bc. Local branch fast-forwarded to that state before this documentation checkpoint.
- Production is live at https://fluxo-continuo.vercel.app/ . Verified ready deploymentdpl_9XYuBDfWdHx6PEqbrj36UxANi3wS (fluxo-continuo-8facn5p69-kenzofujimotos-projects.vercel.app), with public domain alias. Git integration performed production deployment; no extra manual deployment or promotion was necessary.
- HTTP200 and content verified on home,/cobertura (1633syllabi/585reviews/0approvals),/ementas ENCOM300 and DER9829,/universidades/po-57-universidadeno (outside-agreement warning),/comparacoes?curso=dir (new Anthropology review),/pendencias. Evidence snapshot.cache/public-release-http-checks.json. GitHub validation and Vercel checks passed; local85Python+10TS tests,lint/types/build/audit passed.
- Final research statistics and limitations are in docs/release-2026-10-18.md. No institutional messages sent. No universal public-source exhaustion claim;1084candidate pairs still await detailed analysis and1455foreign records lack confirmed individual programme. This was publication of the expanded audited source round, not completion of all curricular comparisons.
- Preserve untracked.claude/,.playwright-mcp/ and ignored.cache/. They are excluded from deployment. No agent mutations pending. This post-publication documentation checkpoint is local; published application content is the merged PR #2.

# Release candidate — 2026-10-18 (latest authoritative checkpoint)

- Public-source round validated:3088 foreign catalogue records,1633 with individual syllabus,1455 without,1098 individual missing contact totals.188/221 Brazilian actual syllabus texts linked;33 absent(7 ordinary,16freeelective,8TCC,2internship). Historical scope is explicit; no universal exhaustion claim and no contacts.
-585reviews,174uniqueBRsubjects,47unreviewed. Classes5high/357partial/198low/25insufficient; high covers4uniqueBR.0homologations,0drift.1084additional ready pairs remain for detailed review; automatic candidates are not conclusions.47unscoped shared-document profiles intentionally do not use global body.
- Permanent TDD fixes:clippedPDFfields,scopedcompendiumretrieval,missing-onlyBRsupplements/contextualyear,scopewarnings,andcurrentcoveragecounts.85Python+10TS passed,lint/types/build/nodevalidate/documentaryaudit passed.
- Source imports finalized:65+26FEN,8UDP,officialFENcrosswalkcommunication correction,+2historicalBRtext. Current FEN May2026PDF resolves the two October2025 code differences; both versions preserved in syllabi/auditoria-planos-fen.json. ENGIN460 catalogue MachineLearning label conflict remains explicit; source is BusinessIntelligence.1GDPidentity/21brokenFENlinks/18physicalelectives/13inactiveversions documented. Code absence alone uses clearly internalCAT identifiers, never guessed academic codes.
- New release notes docs/release-2026-10-18.md. Institutional inventory refreshed66/66. No further agent mutations pending.
- Publishing authorized. Target verified via `vercel project inspect --non-interactive`:kenzofujimotos-projects/fluxo-continuo,prj_BqriF3HyVaMLm1w8VCOHDZSoCvhg. vercel.json explicitly overrides project framework Other to nextjs. .vercelignore excludes .claude/.cache/.playwright-mcp/.env. No secrets printed.
- Next operational steps:commit dataset/docs; merge origin/main(only extra cf67fdd coverage data, may conflict and should be regenerated); draftPR,push,attach,ready/merge per authorized publishing; deployprodskipdomain,verifyHTTP/cobertura585 and1633,thenpromote. Do not claim further1084pairs complete. Keep ignored evidence caches for continuation.

# Live research notes — 2026-10-18 (latest)

- Latest data checkpoint committed645579d at1,533/2,989 foreign individual syllabi,88tests+lint+build+audit passed. Added scope correction commits58031bc/dfb1366. Production still unchanged.
- IMPORTANT NEW BUG: TorVergataPDF get_text clips overflowing AcroForm programme fields. Root read full field values and appended complete curricular form fields to56cached texts; raw sourceSHAunchanged. Manifest documents haveextractionSupplement; journalpdfFormCompletenessAudit records56. No existing572reviews use these56sources, so no old reviews affected. Never infer absent topics from the clipped text appearance. AgentAsia must implement permanent TDDPDFformextraction after its12reviews.
- Root wrote validated newreview dir|DIREITO DA INOVAÇÃO TECNOLÓGICA|it-47-universitadegl|8022971 (low:2covered,4partial,15notfound/21; reviewedfullform including AI). Covers one previously unreviewed BRsubject. Not yet indexed/committed. AgentAsia owns12frozenIDs in .cache/worklist-r-asia.json, includingAntropologiaJuridicaNOVA27139 and11CC/SSU; do not duplicate.
- IMPORTANT NEW TRIAGE BUG: semantic_triage reads full shared pages/compendia for each course; SSU31descriptions sharepage, so concepts can leak across courses.1,078readyworklist is provisional/inflated until scoped retrieval fix. AgentAsia notified to implement TDDboundedSSU text profiles and prevent crosscourse contamination after12reviews. Root is not treating whole shared page as per-course evidence.
- Root independently validated65newFENPDFs (hashes, titles+codesfirstpage, substantivecontent) in .cache/public-research/fen-expanded-parent-audit.json; no duplicateexistingtitles/codes. AgentAmericas authorized to integrate65data+sources+records+cache+journal; EXCLUSIVE sharedfileownership during import.13alternativeversions not imported now.
- AuthoritativeFEN2026catalogue independently freshly downloaded to .cache/public-research/fen-2026-parent-verified.pdf,74pages,SHA27cb8ae640f5eab08222ea21c2fa52918b0dd9d8519d1ca981685cf6f295b54f. p48POSTGRADUATEopenonlygraduates; p67OTHERSopenundergrad+postgrad. Old.cache/public-research/fen-catalogue.pdf66pages is DIFFERENT historicalversion, do not use to audit2026page scope.
- FEN178classification now78undergraduate(65new+13alternatives),55masters,21sports/cultural,24ambiguous. Agent asked to reconsider code-absent exact-title/official-linked programmes using clearly internalCATidentifiers (never invent officialcode); realidentityconflicts remain rejected. UDP9newprogrammeproposals may be eligible similarly, pending verification. No contacts.
- AgentEurope final audit attempt failed usage limit; do not assume its newFENaudit exists. Root independently completed binary+identity65audit instead.

# Current checkpoint — 2026-10-18 (supersedes historical sections)

- Approved public-source research continues on `feature/public-syllabus-sweep`; no contacts and no claim of universal exhaustion. Production still serves the previous403-review release; this round is not pushed or deployed.
- Integrated base:2,989 foreign catalogue records;1,533 individual syllabi;1,456 without individual syllabus;998 individual syllabi without verified total contact hours. Brazilian linked actual syllabi186/221 (35 absent),81 flagged current. Historical official-document status metrics use a narrower separate definition; do not confuse75 current matched FCI records with186 actual linked syllabus texts.
- Frozen review round complete:572 reviews (5 high,347 partial,195 low,25 insufficient),172/221 Brazilian subjects reviewed;49 without review; zero drift and zero institutional approvals. A newly regenerated worklist has1,078 further documentary pairs: this is pending analysis, not equivalence.
- Follow-up imports complete: Europe136, Asia58, Europe extra97 (18Bauhaus+22IPCB+57NOVA Law), Americas42 (40new+2versions), plus prior manual sources. All source caches and literal-hour provenance retained. NOVA56SBE records explicitly outside agreement;57 eligible Law records added without modifying COI flags. FEN TallerPolitica has2026 cover with2022 internal headers; warning retained.
- Attempt ledger merged:2,324 historical attempts, preserving prior histories and mistaken identifiers. Institutional inventory versioned at `syllabi/inventario-pesquisa-instituicoes.json` with66 institutions and explicit unresolved frontiers.
- TDD scope fix:58031bc red,dfb1366 green. New semantic suggestions/worklist exclude only explicit outside_agreement records; UI displays limitations.78 Python+10 TS passed; lint/typecheck and build passed. Node validation and documentary audit passed after1,533-source integration.
- Pending concrete FEN expansion: `.cache/public-research/fen-expanded-audited.json` classifies178remaining PDFs:78 undergraduate ADM programmes (65new+13alternative versions),55masters,21sport/culture,24ambiguous. Not yet imported. Parent independent audit in progress; verify printed codes/titles, substantive content and official catalogue scope before adding65records. Preserve ignored caches. An attempted Europe audit agent hit usage limit; no result produced.
- Root integrated Americas via `.cache/public-research/import-americas-followup.py --apply`; previous sources and hashes preserved. Another frontier rejected: ebs.istanbul.edu.tr is Istanbul University, not the partner Istanbul Aydin; do not import that homonym.
- Agent verify_asia_followup assigned up to12new reviews prioritizing49subjects without any review; selection will be frozen in `.cache/worklist-r-asia.json`. Agent finish_americas_search finishing FEN proposals. Re-run derived scripts after any further import/reviews; incremental fetch only, never blindly refresh15Konkuk browser captures (HTTP requests can return WAF pages).
- Next: audit/integrate FEN65, finish new high-priority reviews, update inventory/coverage and run validation; commit logical units and publish only validated release. Preserve `.claude/`,`.playwright-mcp/` and `.cache/`.

# Active public source sweep — 2026-10-18

- User repeatedly authorized continuation; the research plan is approved. No institutional contacts. Do not claim global public-source exhaustion: several concrete institutional frontiers remain active.
- Branch `feature/public-syllabus-sweep`, latest research checkpoint `94fe96a`. The complete frozen q1–q12 round is finished: 572 reviews (5 high, 347 partial, 195 low, 25 insufficient), covering 172/221 Brazilian disciplines; 49 have no review. All six source drifts were re-reviewed: zero remaining drift and zero institutional approvals.
- Cádiz incorrect catalogue code21719027 was migrated to actual Proyectos Informáticos21714018 in data, matches, records, programme keys and four review filenames/IDs. Previous identifiers and decisions are retained in history. Two USAL101114 reviews now use the correct source.
- Authoritative individual foreign sources currently1,202/2,932 (1,730 missing; 756 without contact hours). This includes436 Claude imports,39 independently checked manual compendium/section sources and9 additional FEN/Duke/Rosario sources. The last9 and their fetched document metadata are not committed yet; regenerate derived reports before committing.
- `76` Python tests and9 application tests passed after fixing the missing `brTopic` label in an empty-syllabus diagnostic. The empty FCI block flag regression is fixed byTDD (`d216491`,`4338350`). No new public deployment yet; production remains the previous release.
- Active agents: verify_europe_followup (136 audited discoveries, plus Bauhaus17 and NOVA Law catalogue expansion), verify_asia_followup (15 Konkuk browser captures plus31 Soongsil descriptions), finish_americas_search (FEN2026:216 public PDFs cached from237 links; matching existing82course records conservatively).
- Ready integration artifacts: `.cache/public-research/europe-followup-audited.json` (136 compact verified sources); `.cache/public-research/asia-followup-audited.json` (now46 sources). A root import attempt for Konkuk failed on a newly added Soongsil entry lacking`audit`; it failed during pre-validation BEFORE any mutation. Filter `captureMethod == public_browser_dom` when importing the15Konkuk entries. Preserve sourceDOM hash vs cacheArtifact hash and reconstruct Windows newline expansion exactly as specified in audit metadata. Seed document manifest/text cache from audited snapshots so requests firewall pages do not replace them.
- Important eligibility issue: NOVA agreement marks onlyLaw, while old56catalogued courses are NOVASBEManagement. The29public SBE guides must carry sourceEligibilityWarning; agent is collecting the correctly eligible Law programme9078 and proposed new catalogue records. BMUCSE is similarly outside the existingLaw-only eligibility and must not be added as an eligible alternative.
- All evidence caches are under `.cache/public-research/`; preserve them. The isolated all-missing sweep finished with2,324 distinct attempt records at `.cache/public-sweep/syllabi/tentativas-coleta.json`; these still need merging into the authoritative attempt ledger with historical wrong identifiers retained explicitly.
- Next: integrate independently audited follow-up sources and browser cache, finish institutional search frontiers, update programme caches/research states/coverage, validate tests/lint/build and document exact unresolved obstacles. Older sections below describe historical checkpoints and are superseded by this one.

# Release checkpoint — 2026-10-17

## Integration and review round (Claude, 17/10/2026)

- Branch `feature/public-syllabus-sweep`. Regional discoveries were integrated with `scripts/integrate_research.py`: every source re-fetched and re-verified against our catalogue (`verify_programme`), 436 accepted, 51 rejected with reasons in `syllabi/integracao-pesquisa-publica.json` (commit `3bd4684`). Individual foreign syllabi 718 -> 1,154; missing 2,214 -> 1,778.
- `verify_programme` now accepts known one-course templates (USAL, Leeds, UCA, Coimbra, Nevşehir) even when prerequisites cite other courses (`INDIVIDUAL_TEMPLATES`, commit `977fece`).
- 6 existing reviews carry `documentDrift` (official document changed since review): re-review them.
- Review round 4 in progress: `.cache/worklist-q1..q12.json` (169 pairs: 66 for 31 Brazilian disciplines that had no review, 103 registered candidates). Brief: `.cache/agent-brief-batch3.md`. After each agent: `python scripts/build_pareceres.py`, commit `syllabi/pareceres*`. Remaining ready pairs: `python scripts/worklist.py`.
- Brazilian side publicly exhausted (no 2026 Alphaville ementário published); 49 Brazilian disciplines still lack any documented foreign candidate.

## Active follow-up: public source exhaustion

- User explicitly approved the new plan: inventory all 66 universities and four Brazilian courses, search public official portals/PDFs/archives, verify source identity/content/hours, update viable reviews and run tests/audit. No institutional contacts now. Do not claim the public internet is exhausted while institutional searches remain pending.
- Branch `feature/public-syllabus-sweep`. Baseline remains 403 reviews, 718 individual foreign syllabi, 2,214 missing. Production release from PR #1 is live; this follow-up is local research, not yet published.
- Collection improvements use TDD: opt-in `--scope all-missing`, resumable history, shared exact URL fetch cache, navigation-content false-positive guard, PDF signature detection fix. Full Python suite now 69 tests passed.
- The broad sweep runs in isolated `.cache/public-sweep/`; do not blindly copy its verified sources into the authoritative base. Manual identity and content checks must quarantine false positives such as ESTG curriculum page 1337 and course-code collisions.
- Regional research outputs and evidence live under `.cache/public-research/`: Europe, Americas, Asia/Brazil. SolBridge individual PDF matches are collected separately. Agents must finish their institutional ledgers and manual audits before integration. Preserve this cache; it is ignored by Git.
- Next: finish public searches, validate source discoveries, integrate accepted evidence with history, cache/read documents, recompute research states and gaps, then audit and report exact coverage and unresolved obstacles. No emails or login bypasses.

- All 270 frozen research pairs are complete; index contains 403 reviews: 5 high, 230 partial, 139 low, 29 insufficient. Covers 141/221 Brazilian disciplines. No institutional equivalence.
- Source integrity fixes and their regression tests are committed. 61 Python tests and 9 application tests passed; documentary audit passed for 403 reviews and 6,856 research states.
- Current release statistics and limitations: `docs/release-2026-10-17.md`. Foreign individual syllabi: 718/2,932; missing: 2,214; missing contact hours: 452/718; priority requests: 826.
- Branch: `feature/interactive-globe`. Target project: `fluxo-continuo`, public domain https://fluxo-continuo.vercel.app. Vercel configured for Next.js. Publishing is explicitly authorized. Final lint/build and deployment verification are the current operational steps.
- Preserve untracked `.claude/`. Older checkpoints below describe historical states.

# Globe visual refinement — 2026-10-16

- Country cards and university detail now render local SVG country flags in the red/cream palette; all 21 country codes in the current data have assets. Original flag-icons 7.6.0 SVGs and MIT license are in `public/flags/`.
- Global scrollbars match the local MackJr 6px dark styling, including horizontal destination strips. Firefox has a conditional thin fallback.
- No new automated tests were added for this reversible visual adjustment. Existing TypeScript/Python tests, lint/types and production build were rerun; browser visual verification remains unavailable.
- Preview remains http://127.0.0.1:3002, restarted after production rebuild. No push or deploy.

---
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


