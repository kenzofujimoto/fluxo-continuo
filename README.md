# MobiMatch Alpha — Fluxo Contínuo 2027.2

> **Publicação em andamento:** este repositório recebeu a estrutura inicial; o pacote integral v2 (dados COI, scripts e estilos) foi produzido localmente, mas ainda não está todo commitado aqui. A URL de produção permanece na versão anterior até o novo deploy. Não usar este repositório isoladamente como catálogo oficial.

**[Abrir site publicado](https://mobimatch-alpha.vercel.app)** · [Idiomas e certificados](https://mobimatch-alpha.vercel.app/idiomas.html)

Projeto **independente e não oficial** de apoio à escolha de disciplinas e universidades estrangeiras, com foco em quatro cursos do campus Mackenzie Alphaville: Ciência da Computação, Sistemas de Informação, Direito e Administração.

## O que a versão 2 oferece

- Matriz horizontal pesquisável de disciplinas Mackenzie × instituições assinaladas **Sim** para o curso no XLSX oficial 1S/2027 (mobilidade 2027.2).
- 66 instituições da planilha inicial COI; **23 em CC, 16 em SI, 40 em Administração e 39 em Direito**. A coluna selecionada é **por curso**, não por campus ou modalidade.
- Filtro opcional para mostrar instituições sem marcação “Sim”; isso não autoriza candidatura.
- Células clicáveis com links às ementas; análise documentada em seis cruzamentos iniciais, **nenhum homologado**.
- Página exclusiva de idiomas com requisitos, nota mínima, certidão MLC, aceitação MLC e hiperlinks oficiais de cada instituição.
- Quadro de custos e descontos, com fonte e prazo: exame MLC, TOEFL ETS/GCUB, IELTS British Council, DELE/Instituto Cervantes e EF SET (diagnóstico, não substituto garantido).
- CSV da matriz filtrada; sem login, sem banco de dados e sem dados pessoais.

## Limites e qualidade da importação

- A COI publica a planilha inicial 1S/2027 e avisa que requisitos de idioma podem mudar. `Sim` indica disponibilidade **por área de estudo** no momento da planilha, não garante vaga individual nem disciplina ofertada em 2027/28.
- O campo de idioma está **inválido em 12 linhas de instituições portuguesas**: aparece repetido o texto `Universidade Lusófona`. Preservamos a universidade e a elegibilidade do curso, mas **não interpretamos esses valores como requisitos de idioma**.
- Na planilha Excel, a aba herdou um nome interno histórico (`Fluxo 2S 25 inicial`) que não corresponde ao nome/ano do XLSX. O projeto usa o nome do documento disponibilizado para 2027.2, verificando as informações sempre com a COI.
- As matrizes brasileiras são uma base preliminar já cadastrada (47 componentes CC, 46 SI, 47 ADM, 81 DIR) e não representam todas as versões/PPC por ano de ingresso. As disciplinas estrangeiras presentes vêm de auditorias anteriores de Ciência da Computação. Ampliar a cobertura exige curadoria acadêmica.
- O exame de proficiência MLC é reconhecido **somente se aceito** pela universidade da candidatura. EF SET é gratuito, mas não é aceito automaticamente por universidade ou edital.
- **Equivalências não são homologações** e nenhuma decisão de aproveitamento foi atribuída à coordenação.

## Executar localmente

```bash
python -m http.server 8000
# abra http://localhost:8000/
```

Site estático sem dependências. Hospedar os arquivos `index.html`, `app.js`, `styles.css`, `idiomas.html`, `idiomas.js`, `idiomas.css` e `data.json` na raiz do projeto. A Vercel pode servir a raiz como site estático (Framework: Other).

## Fontes oficiais

- [COI — Fluxo Contínuo, planilha inicial de universidades por curso](https://www.mackenzie.br/universidade/fluxo-continuo)
- [MLC — exame para intercâmbio COI (R$ 259, validade 6 meses)](https://portal.mackenzie.br/mackenzie-language-center/cursos-especificos/exame-para-intercambio-coi)
- [ETS — TOEFL iBT, tabela de taxas](https://www.br.ets.org/toefl/test-takers/ibt/register/fees.html)
- [GCUB — voucher TOEFL outubro/2026 de **10%**, prazo **31/10/2026**](https://www.gcub.org.br/parceiros/voucher-de-10-para-o-toefl-ibt-outubro-de-2026/)
- [GCUB/Cervantes — benefício DELE outubro/2026 de **25%**, prazo **30/10/2026**](https://www.gcub.org.br/eventos/noticias/beneficios-oferecidos-pelo-instituto-cervantes-outubro-2026/)
- [IELTS — centro SP](https://ielts.org/test-centres/british-council-sao-paulo-open-centre) / [British Council — preço de referência](https://www.britishcouncil.org.br/en/exam/ielts/which-test/academic)
- [EF SET — prova gratuita de quatro habilidades](https://www.efset.org/pt/4-skill/)

*Última checagem de fontes e dados: 15/10/2026.*

## Responsabilidade

O MobiMatch Alpha **não é afiliado, endossado ou homologado pelo Mackenzie**. A identidade cromática foi inspirada no ambiente institucional, sem uso do brasão. Exames, preços, ementas e requisitos mudam. A COI e a instituição anfitriã são as fontes definitivas, e a coordenação da graduação decide aproveitamentos curriculares.

### Resultados por par (2027.2)

`triagem.json` contém 6.856 tentativas automatizadas de correspondência de título/metadados; `triagem-view.js` mostra o motivo em cada célula e permite exportar um CSV completo. Não significa 6.856 equivalências aprovadas. Ver `METODOLOGIA.md`.
