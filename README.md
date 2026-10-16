# MobiMatch Alpha — Fluxo Contínuo 2027.2

> **Projeto acadêmico independente e não oficial.** Pesquisa de possíveis aproveitamentos curriculares para o campus Mackenzie Alphaville, não homologações institucionais.

**Site principal:** https://fluxo-continuo.vercel.app  
**Página de idiomas:** https://fluxo-continuo.vercel.app/idiomas.html

## Estado da pesquisa — 15/10/2026

Os números abaixo foram verificados na base `data.json` publicada na Vercel:

| Indicador | Quantidade |
| --- | ---: |
| Cursos brasileiros | 4 (Ciência da Computação, Sistemas de Informação, Administração e Direito) |
| Disciplinas brasileiras listadas | 221 (CC 47, SI 46, ADM 47, Direito 81) |
| Instituições elegíveis da planilha COI | 66 |
| Instituições com disciplinas estrangeiras indexadas | 39 |
| Disciplinas estrangeiras indexadas | 1.596 |
| Registros de possíveis correspondências | 505 |
| Indícios *somente pelo título* | 447 |
| Correspondências em análise | 55 |
| Candidatas fortes | 3 |
| Equivalências formalmente homologadas | **0** |

As quantidades podem mudar a cada atualização. Os números de cada aba são recortes por curso/universidades elegíveis.

**A pesquisa não está completa.** Ainda há 27 instituições sem disciplinas estrangeiras indexadas; mesmo onde há catálogo, várias ementas individuais, cargas horárias, pré-requisitos e ofertas em 2027/28 não foram verificados. Ter executado a triagem dos 6.856 cruzamentos possíveis não é o mesmo que ter comparado integralmente as ementas de todas essas combinações. O método de título é apenas um filtro inicial.

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

**O MobiMatch Alpha não é afiliado nem endossado pelo Mackenzie e não emite pareceres acadêmicos.**

## Cobertura verificável (16/10/2026)

- **6.856** cruzamentos de disciplina Mackenzie x instituição elegível classificados; isso é triagem, **não** 6.856 equivalências verificadas.
- **1.653** disciplinas estrangeiras com títulos indexados de catálogos/páginas oficiais de **41** universidades; **25** instituições da planilha ainda sem disciplinas indexadas.
- **505** correspondências anteriormente cadastradas (incluem fortes candidatas, pré-análises e indícios de título), **439** pares com candidatos na passagem multilíngue adicional; conjuntos parcialmente sobrepostos.
- Ementários brasileiros: **CC 47/47 com resumos**; **SI 41/46 com texto do ementário oficial de 2025**; **Direito 63/81 com texto do ementário oficial de 2022**; Administração ainda requer verificação de ementário próprio do campus e da matriz curricular de ingresso.
- Fontes por registro estão expostas no site. Nenhuma correspondência está homologada pela coordenação; confirmar horas, conteúdo, idioma, pré-requisitos e oferta em **2027.2**.
- Finis Terrae: malla oficial de Direito usada somente para títulos; Bologna: fichas individuais 2026/27. Códigos `CAT-*` e sufixos internos não são códigos acadêmicos oficiais.
- **Próxima etapa indispensável**: indexar e ler ementas individuais das universidades ausentes e revisar par a par o conteúdo, carga e semestre. Não usar ausência de resultado como prova de incompatibilidade.
