# Fluxo Contínuo — pesquisa independente de mobilidade 2027.2

> **Projeto acadêmico independente e não oficial.** Pesquisa de possíveis aproveitamentos curriculares para o campus Mackenzie Alphaville, não homologações institucionais.

**Site principal:** https://fluxo-continuo.vercel.app  
**Página de idiomas:** https://fluxo-continuo.vercel.app/idiomas.html

## Estado auditado da base — 16/10/2026

Os valores a seguir foram contados na base versionada em `data.json`, `triagem.json` e `candidatos-catalogo.json`. A cobertura documental não implica validação curricular.

| Indicador | Quantidade |
| --- | ---: |
| Cursos brasileiros | 4 (Ciência da Computação, Sistemas de Informação, Administração, Direito) |
| Componentes Mackenzie | 221 (CC 47, SI 46, Administração 47, Direito 81) |
| Universidades listadas pela COI | 66 |
| Universidades com ao menos um título estrangeiro indexado | **44** |
| Disciplinas estrangeiras com título/catálogo indexado | **1.838** |
| Correspondências e indícios registrados | **553** |
| Pares da triagem adicional com alguma sugestão de título | **438** |
| Cruzamentos disciplina × universidade elegível triados | **6.856** |
| Aproveitamentos homologados | **0** |

As 553 correspondências e as sugestões adicionais podem coincidir: nunca somá-las como equivalências distintas. Há **22 universidades sem disciplinas indexadas**; parte dessas 22 não tem marcação Sim para nenhum dos quatro cursos. O projeto **não concluiu** o cotejo integral das ementas nem a verificação de todas as ofertas em 2027.2.

A rodada de 16/10 também indexou o catálogo departamental oficial da [Soongsil](https://sec.ssu.ac.kr/page/subject_contents.php), com 31 títulos e resumos temáticos sem comprovação de disponibilidade para intercambistas. Um placeholder não verificado da Universidad Evangélica Boliviana foi removido.

A rodada de 16/10 agregou **155 títulos oficiais** de Ferrara (13), Roma Tor Vergata (70) e Salerno (72), provenientes de catálogos institucionais 2026/27. Em Direito italiano, nomes semelhantes envolvem sistemas jurídicos diferentes. Foram removidas seis associações ambíguas e corrigidos códigos internos repetidos.

Veja [cobertura por universidade e curso](./cobertura.html) para separar elegibilidade, indexação e pendências.

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
- Em caso de dúvida, siga a planilha atual da COI e a coordenação do Mackenzie. Não existe aproveitamento aprovado na base.

Para validar o banco localmente, execute `node validate.js`.
