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
