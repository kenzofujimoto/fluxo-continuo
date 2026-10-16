# Fluxo Contínuo — pesquisa independente de mobilidade 2027.2

> **Projeto acadêmico independente e não oficial.** Pesquisa de possíveis aproveitamentos curriculares para o campus Mackenzie Alphaville, não homologações institucionais.

**Site principal:** https://fluxo-continuo.vercel.app  
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
| Pares com sugestões lexicais da rodada anterior | **438** |
| Cruzamentos elegíveis na triagem inicial | **6.856** |
| Aproveitamentos formalmente homologados | **0** |

**A indexação das 22 universidades pendentes foi concluída no nível mínimo de título e fonte acadêmica. Isso NÃO equivale a comparar integralmente todas as ementas.** Os 725 registros e 438 sugestões têm sobreposição, não devem ser somados e não são aprovações institucionais. As 11 universidades sem marcação COI Sim em nenhum dos quatro cursos têm registros documentais, mas não são destinos elegíveis para essas matrizes.

### Última expansão

- **Universidad Evangélica Boliviana:** 59 disciplinas de Engenharia de Sistemas e 57 de Administração Geral, com códigos institucionais, semestres, créditos locais CR e pré-requisitos em PDFs vinculados pela universidade; ano de vigência a confirmar.
- **Universidad Alfa y Omega (México):** 42 disciplinas de Administração, 42 de Direito e 48 de Informática Administrativa em PDFs oficiais com códigos e semestre. A instituição não consta como elegível nos quatro cursos.
- **Universidade Lusíada Lisboa:** 84 disciplinas de Gestão e Direito da matriz de 2025/26.
- **Outras 19 universidades:** matrizes e páginas acadêmicas catalogadas, incluindo IPCB, UPAL, Konkuk, Florence University of the Arts, Nevşehir, BML Munjal, ISG, Viaa e instituições sem elegibilidade COI.

A triagem adicional tem **3.920 pares com estado I (indexação posterior: comparação individual pendente)**. Não houve nova análise automática de conteúdo destes pares. As fontes por instituição podem ser abertas na [cobertura](./cobertura.html) e em `data.json`.

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
- Foram extraídos 41 de 46 textos de ementas de SI e 63 de 81 de Direito; o ementário de Administração para a matriz correta permanece pendente.
- Fontes institucionais agregadas: [Ferrara](https://corsi.unife.it/it/lm-giurisprudenza/studiare/didattica/progr/programma-del-corso-e-dei-curricula-n-o), [Tor Vergata](https://cdl.giurisprudenza.uniroma2.it/a-a-2025-2026/) e [Salerno](https://corsi.unisa.it/giurisprudenza/didattica/insegnamenti).
- Códigos internos `CAT-*` não são códigos oficiais. O exame individual de cada ementa, carga horária e semestre permanece obrigatório.
- O estado **I** sinaliza disciplina indexada posteriormente e pendência de nova análise por par; não é incompatibilidade.
- Em caso de dúvida, siga a planilha atual da COI e a coordenação do Mackenzie. Não existe aproveitamento aprovado na base.

Para validar o banco localmente, execute `node validate.js`.
