#!/usr/bin/env python3
"""Concept-based (not title-based) screening of every eligible Mackenzie course x university crossing.

A controlled multilingual thesaurus (pt, en, es, ca, it, fr, ro) maps official ementa text, foreign course
titles, catalogue notes and cached individual syllabi to concepts. Shared concepts, weighted by how rare
each concept is in the foreign catalogue (IDF), produce an *indicator* of thematic overlap. The indicator
is a retrieval aid: it is never a percentage of equivalence and never a reason to call a pair incompatible.

Every crossing receives exactly one research state (STATES) with a data-specific note, so that no
crossing remains untriaged and absence of words never becomes a negative conclusion.

Run: python scripts/semantic_triage.py   ->  syllabi/triagem-semantica.json
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import math
import re
import unicodedata
from itertools import combinations
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "syllabi" / "triagem-semantica.json"

STATES = (
    "parecer_concluido",            # at least one individual parecer exists for the cell
    "candidata_registrada",          # registered candidate(s) awaiting a parecer (missing documents listed)
    "candidata_semantica",           # new concept-based candidate(s) found in the indexed catalogue
    "regra_especifica",              # TCC / estágio / optativa livre: governed by specific rules
    "sem_candidata_no_catalogo_indexado",  # indexed area catalogue examined; no shared concepts (NOT a verdict)
    "catalogo_insuficiente",         # too few indexed courses in the area to conclude anything
)

# concept -> (domain, regex fragments). Fragments are matched on accent-folded lowercase text.
THESAURUS: dict[str, tuple[str, list[str]]] = {
    # ---- computing
    "algoritmos": ("cc", [r"algorit", r"algorithm"]),
    # 'programação linear/inteira' is operations research, not programming
    "programacao": ("cc", [r"programa[cç](?:[aã]o|[oõ]es)(?! linear| inteira| matem| din[aâ]mica)", r"programaci[oó]n(?! lineal| entera| matem| din[aá]mica)",
                           r"programmazione(?! lineare)", r"(?<!linear )(?<!integer )(?<!dynamic )programming", r"programare(?! liniar)", r"programaci[oó](?! lineal)", r"\bcoding\b"]),
    "estruturas_dados": ("cc", [r"estrutura\w* de dados", r"data structur", r"estructuras? de datos", r"strutture dati", r"structuri de date", r"estructures de dades", r"\blistas?\b.*\bpilhas?\b", r"\bheap\b"]),
    "complexidade": ("cc", [r"complexit", r"complejidad", r"complessita", r"complexidade", r"assint", r"asymptot", r"big[- ]o\b"]),
    "poo": ("cc", [r"orient\w* a objet", r"object[- ]oriented", r"orientad\w* a objetos", r"orientat\w* agli oggetti", r"orientat\w* pe obiect", r"\bpoo\b", r"\boop\b"]),
    "paradigmas": ("cc", [r"paradigm", r"functional programming", r"programa[cç][aã]o funcional", r"programacion funcional", r"lambda", r"haskell", r"prolog", r"logic programming"]),
    "linguagens_formais": ("cc", [r"linguagens formais", r"formal languages", r"lenguajes formales", r"linguaggi formali", r"automat", r"automat[ao]s?\b", r"autom[aá]tos", r"gram[aá]tic", r"grammar", r"turing"]),
    "compiladores": ("cc", [r"compil", r"\bparser", r"lexical analy", r"an[aá]lise l[eé]xica", r"analisis lexico"]),
    "arquitetura_comp": ("cc", [r"computer architecture", r"arquitetura de computadores", r"arquitectura de computadores", r"architettura degli elaboratori", r"arhitectura sistemelor de calcul", r"organiza[cç][aã]o de computadores", r"\bassembl", r"processador", r"processor", r"memoria cache", r"cache memor"]),
    "circuitos_digitais": ("cc", [r"circuitos? (?:l[oó]gicos|digita)", r"digital (?:logic|circuit|system)", r"logic circuit", r"portas l[oó]gicas", r"flip[- ]flop", r"[aá]lgebra booleana", r"boolean algebra", r"karnaugh"]),
    "eletronica": ("cc", [r"eletr[oô]nic", r"electr[oó]nic", r"circuitos el[eé]tricos", r"electric circuit", r"arduino"]),
    "sistemas_operacionais": ("cc", [r"operating system", r"sistemas? operaciona", r"sistemas? operativ", r"sistemi operativ", r"sisteme de operare", r"escalonamento", r"scheduling", r"memoria virtual", r"virtual memory"]),
    "concorrencia": ("cc", [r"concurren", r"concorr[eê]n", r"concurrent", r"synchroni", r"sincroniza", r"semaphore", r"sem[aá]foro", r"deadlock", r"\bthreads?\b", r"concurrenc", r"programacion concurrente", r"programaci[oó]n concurrente"]),
    "paralelismo": ("cc", [r"parallel", r"paralel", r"parallel", r"openmp", r"\bmpi\b", r"\bcuda\b", r"\bgpu", r"multicore", r"manycore"]),
    "distribuidos": ("cc", [r"distributed system", r"sistemas distribu[ií]d", r"sistemi distribuiti", r"sisteme distribuite", r"middleware", r"\brpc\b", r"consensus", r"replica[cç]", r"replication", r"computa[cç][aã]o distribu"]),
    "redes": ("cc", [r"computer networks?", r"redes de computador", r"redes de (?:computadoras|datos|comunicac)", r"reti di calcolatori", r"\bretele\b", r"retele de calculatoare", r"tcp/ip", r"\bosi\b", r"network protocol", r"protocolos de rede", r"xarxes", r"\bnetworking\b", r"redes de dados"]),
    "seguranca": ("cc", [r"security", r"seguran[cç]a", r"seguridad(?! social)", r"sicurezza", r"securitate", r"seguretat(?! social)", r"cryptograph", r"criptogra", r"cybersecur", r"ciberseg"]),
    "banco_dados": ("cc", [r"database", r"banco[s]? de dados", r"base[s]? de datos", r"basi di dati", r"baze de date", r"bases de dades", r"\bsql\b", r"modelo relacional", r"relational model", r"sgbd", r"dbms"]),
    "engenharia_software": ("cc", [r"software engineering", r"engenharia de software", r"ingenier[ií]a del? software", r"ingegneria del software", r"ingineria program", r"enginyeria del programari", r"requisitos de software", r"requirements engineering", r"\buml\b", r"\bscrum\b", r"agile", r"metodologias? [aá]geis"]),
    "teste_software": ("cc", [r"software testing", r"testes? de software", r"pruebas de software", r"test[- ]driven", r"\btdd\b", r"quality assurance", r"qualidade de software", r"verifica[cç][aã]o e valida"]),
    "web": ("cc", [r"\bweb\b", r"\bhtml", r"\bcss\b", r"javascript", r"\bhttp\b", r"front[- ]?end", r"back[- ]?end", r"\brest(?:ful)?\b", r"\bapis?\b"]),
    "mobile": ("cc", [r"\bmobile\b", r"dispositivos m[oó]veis", r"dispositivos m[oó]viles", r"android", r"\bios\b"]),
    "ihc": ("cc", [r"human[- ]computer interaction", r"intera[cç][aã]o humano", r"interacci[oó]n persona", r"interaccion humano", r"usabilit", r"usabilid", r"user experience", r"\bux\b", r"interface[s]? (?:gr[aá]fic|de usu|do usu)", r"user interface"]),
    "ia": ("cc", [r"artificial intelligence", r"intelig[eê]ncia artificial", r"inteligencia artificial", r"intelligenza artificiale", r"inteligenta artificiala", r"intel\.ligencia artificial", r"agentes inteligentes", r"busca heur", r"heuristic search"]),
    "aprendizado_maquina": ("cc", [r"machine learning", r"aprendizado de m[aá]quina", r"aprendizaje autom[aá]tico", r"apprendimento automatico", r"deep learning", r"neural network", r"redes neura", r"redes neuronales", r"learning algorithms"]),
    "ciencia_dados": ("cc", [r"data science", r"ci[eê]ncia de dados", r"ciencia de datos", r"data mining", r"minera[cç][aã]o de dados", r"miner[ií]a de datos", r"big data", r"\banalytics\b", r"data analysis"]),
    "computacao_grafica": ("cc", [r"computer graphics", r"computa[cç][aã]o gr[aá]fica", r"inform[aá]tica gr[aá]fica", r"rendering", r"opengl", r"grafica computerizzata"]),
    "visao_imagem": ("cc", [r"computer vision", r"vis[aã]o computacional", r"visi[oó]n por computador", r"image processing", r"processamento de imagens", r"procesamiento de im[aá]genes"]),
    "nuvem": ("cc", [r"\bcloud\b", r"\bnuvem\b", r"\bnube\b", r"virtualiz", r"container", r"docker", r"kubernetes", r"devops"]),
    "teoria_computacao": ("cc", [r"computabil", r"teoria da computa", r"theory of computation", r"decidab", r"np[- ]complet"]),
    "sistemas_informacao": ("si", [r"information systems?", r"sistemas de informa[cç]", r"sistemas de informaci", r"sistemi informativi", r"sisteme informatice", r"\berp\b", r"business intelligence", r"gest[aã]o da informa", r"information management"]),
    "governanca_ti": ("si", [r"it governance", r"governan[cç]a de ti", r"governan[cç]a", r"cobit", r"\bitil\b", r"compliance"]),
    # ---- mathematics / methods (shared by all courses)
    "matematica_discreta": ("mat", [r"discrete math", r"matem[aá]tica discreta", r"teoria dos grafos", r"graph theory", r"teor[ií]a de grafos", r"combinat[oó]r", r"teoria dos conjuntos", r"set theory", r"indu[cç][aã]o matem"]),
    "logica": ("mat", [r"\blogic", r"\bl[oó]gica\b", r"\blogica\b", r"proposicional", r"propositional", r"predicate", r"predicados"]),
    "calculo": ("mat", [r"calculus", r"\bc[aá]lculo\b", r"\bcalcul\b", r"derivad", r"\bintegra(?:l|is|les)\b",r"an[aá]lisis matem[aá]tico", r"analisi matematica"]),
    "algebra_linear": ("mat", [r"linear algebra", r"[aá]lgebra linear", r"[aá]lgebra lineal", r"algebra lineare", r"algebra liniara", r"\bmatri(?:z|zes|ces|x|ces)\b", r"espa[cç]os vetoriais", r"vector spaces?"]),
    "estatistica": ("mat", [r"statistic", r"estat[ií]stic", r"estad[ií]stic", r"statistica", r"probabil", r"infer[eê]ncia", r"inferencia", r"regress", r"hypothesis test", r"testes? de hip[oó]tese", r"contraste de hip"]),
    "metodos_numericos": ("mat", [r"numerical (?:methods|analysis)", r"m[eé]todos num[eé]ricos", r"c[aá]lculo num[eé]rico", r"an[aá]lisis num[eé]rico"]),
    "pesquisa_operacional": ("mat", [r"operations research", r"pesquisa operacional", r"investigaci[oó]n operativa", r"ricerca operativa", r"programa[cç][aã]o linear", r"linear programming", r"programaci[oó]n lineal",
                                    # plain "optimisation" also names code/compiler optimisation: require a mathematical qualifier
                                    r"otimiza[cç][aã]o (?:linear|combinat|matem|inteira)", r"(?:mathematical|linear|combinatorial|integer) optimi[sz]ation",
                                    r"optimi[sz]ation (?:models?|methods|problems|techniques|theory)", r"optimizaci[oó]n (?:lineal|matem|combinat|entera)", r"simplex", r"m[eé]todos quantitativos", r"quantitative methods"]),
    "matematica_basica": ("mat", [r"matem[aá]tica b[aá]sica", r"elementos de matem", r"fundamentos de matem", r"matem[aá]ticas? (?:para|aplicad)", r"mathematics for", r"funciones? de", r"fun[cç][oõ]es do 1"]),
    "metodologia_pesquisa": ("gen", [r"research method", r"metodologia (?:da|de) pesquisa", r"metodolog[ií]a de (?:la )?investigaci", r"metodologia cient[ií]fica", r"scientific method", r"m[eè]tode cient", r"projeto de pesquisa", r"research project", r"trabalho cient"]),
    "comunicacao": ("gen", [r"communication skills", r"comunica[cç][aã]o e express", r"expresi[oó]n oral", r"escrita acad", r"academic writing", r"reda[cç][aã]o", r"comunicaci[oó]n oral y escrita", r"oratoria", r"public speaking", r"comunica[cç][aã]o empresarial"]),
    "etica": ("gen", [r"\bethic", r"\b[eé]tica\b", r"\betica\b", r"deontolog", r"\bmoral\b"]),
    "cts": ("gen", [r"ci[eê]ncia,? tecnologia e sociedade", r"science,? technology and society", r"ciencia,? tecnolog[ií]a y sociedad", r"epistemolog", r"filosofia da ci[eê]ncia", r"philosophy of science"]),
    "cosmovisao": ("gen", [r"cosmovis", r"worldview", r"reformad", r"reformed", r"teolog", r"theolog", r"cristianismo", r"christian", r"religi"]),
    # ---- business / economics
    "administracao_geral": ("adm", [r"teorias? da administra", r"teor[ií]as? de la administraci", r"management theor", r"fundamentals of management", r"introdu[cç][aã]o [aà] administra", r"introducci[oó]n a la administraci", r"principles of management", r"organiza[cç][aã]o e gest", r"fun[cç][oõ]es administrativas", r"\bpodc\b", r"gest[aã]o de empresas", r"business administration", r"administraci[oó]n de empresas", r"direcci[oó]n de empresas", r"organitzaci[oó] d'empreses", r"economia aziendale"]),
    "comportamento_org": ("adm", [r"organi[sz]ational behavio", r"comportamento organizacional", r"comportamiento organizacional", r"comportamento organizzativo", r"lideran[cç]a", r"leadership", r"liderazgo", r"motiva[cç][aã]o", r"motivation", r"cultura organizacional", r"organizational culture"]),
    "gestao_pessoas": ("adm", [r"human resource", r"gest[aã]o de pessoas", r"recursos humanos", r"gesti[oó]n de personas", r"risorse umane", r"\bhrm\b", r"talent"]),
    "marketing": ("adm", [r"marketing", r"mercadotecnia", r"m[aà]rqueting", r"consumer behavio", r"comportamento do consumidor", r"comportamiento del consumidor", r"branding", r"gest[aã]o de marcas", r"\bmarcas\b", r"publicidad", r"advertising"]),
    "estrategia": ("adm", [r"strateg", r"estrat[eé]gi", r"vantagem competitiva", r"ventaja competitiva", r"competitive advantage", r"\bporter\b"]),
    "sustentabilidade": ("adm", [r"sustainab", r"sustentab", r"sostenib", r"\besg\b", r"responsabilidade social", r"responsabilidad social", r"corporate social responsibility", r"\bcsr\b"]),
    "contabilidade": ("adm", [r"accounting", r"contabil", r"contabilidad", r"contabilitat", r"contabilit[aà]", r"balan[cç]o patrimonial", r"balance sheet", r"financial statements", r"demonstra[cç][oõ]es (?:financeiras|cont[aá]beis)", r"estados financieros"]),
    "custos": ("adm", [r"cost accounting", r"contabilidade de custos", r"contabilidad de costes", r"contabilidad de costos", r"gest[aã]o de custos", r"\bcusteio\b", r"costing", r"\bcostes\b", r"\bcustos\b"]),
    "financas": ("adm", [r"corporate finance", r"finan[cç]as", r"finanzas", r"finanza", r"finances", r"financial management", r"gest[aã]o financeira", r"capital budgeting", r"valuation", r"avalia[cç][aã]o de empresas", r"custo de capital", r"cost of capital", r"capital de giro", r"working capital", r"viabilidade financeira"]),
    "investimentos": ("adm", [r"investment", r"investiment", r"inversiones", r"inversions", r"portfolio", r"carteira", r"mercado de capitais", r"capital markets", r"mercados financieros", r"financial markets", r"derivativ", r"derivados"]),
    "matematica_financeira": ("adm", [r"financial mathematics", r"matem[aá]tica financeira", r"matem[aá]ticas financieras", r"matem[aà]tica financera", r"\bjuros\b", r"interest rates?", r"amortiza", r"capitaliza"]),
    "microeconomia": ("adm", [r"microecon"]),
    "macroeconomia": ("adm", [r"macroecon", r"pol[ií]tica monet", r"monetary policy", r"infla[cç][aã]o", r"inflation", r"inflaci"]),
    "economia": ("adm", [r"\beconom"]),
    "operacoes": ("adm", [r"operations management", r"gest[aã]o de opera[cç]", r"direcci[oó]n de operaciones", r"gesti[oó]n de operaciones", r"production management", r"gest[aã]o da produ[cç]", r"\blean\b", r"just[- ]in[- ]time", r"administra[cç][aã]o da produ"]),
    "logistica": ("adm", [r"logistic", r"log[ií]stic", r"supply chain", r"cadeia de suprimento", r"cadena de suministro", r"cadena de abastecimiento"]),
    "qualidade": ("adm", [r"quality management", r"gest[aã]o da qualidade", r"gesti[oó]n de la calidad", r"\biso 9001", r"six sigma", r"\btqm\b"]),
    "inovacao": ("adm", [r"innova", r"inova[cç]", r"innovaci"]),
    "empreendedorismo": ("adm", [r"entrepreneur", r"empreend", r"emprend", r"imprenditor", r"startup", r"business plan", r"plano de neg[oó]cio", r"plan de negocio", r"modelo de neg[oó]cio", r"business model", r"criação de empresas", r"cria[cç][aã]o de empresas"]),
    "gestao_projetos": ("adm", [r"project management", r"gest[aã]o de projetos", r"gesti[oó]n de proyectos", r"ger[eê]ncia de projetos", r"gerenciamento de projetos", r"\bpmbok\b", r"gestione dei progetti"]),
    "negocios_internacionais": ("adm", [r"international business", r"neg[oó]cios internacionais", r"negocios internacionales", r"com[eé]rcio internacional", r"international trade", r"comercio exterior", r"globaliza"]),
    "processos_org": ("adm", [r"processos organizacionais", r"business process", r"gest[aã]o (?:por|de) processos", r"gesti[oó]n por procesos", r"\bbpm\b", r"estrutura organizacional", r"organizational (?:design|structure)"]),
    "sociologia": ("gen", [r"sociolog", r"ci[eê]ncias sociais", r"social sciences", r"ciencias sociales", r"antropolog", r"anthropolog"]),
    # ---- law
    "teoria_direito": ("dir", [r"teoria geral do direito", r"teor[ií]a general del derecho", r"teoria del diritto", r"teoria del dret", r"theory of law", r"legal theory", r"introdu[cç][aã]o ao (?:estudo do )?direito", r"introducci[oó]n al derecho", r"introducci[oó] al dret", r"fontes do direito", r"norma jur[ií]dica"]),
    "filosofia_direito": ("dir", [r"filosofia do direito", r"filosof[ií]a del derecho", r"filosofia del diritto", r"filosofia del dret", r"philosophy of law", r"jusnatural", r"positivismo jur", r"justi[cç]a"]),
    "historia_direito": ("dir", [r"hist[oó]ria do direito", r"historia del derecho", r"storia del diritto", r"hist[oò]ria del dret", r"legal history", r"direito romano", r"derecho romano", r"dret rom[aà]", r"roman law", r"diritto romano"]),
    "ciencia_politica": ("dir", [r"ci[eê]ncia pol[ií]tica", r"ciencia pol[ií]tica", r"ci[eè]ncia pol[ií]tica", r"political science", r"scienza politica", r"teoria do estado", r"teor[ií]a del estado", r"state theory"]),
    "constitucional": ("dir", [r"constitucional", r"constitutional", r"costituzional", r"direitos fundamentais", r"fundamental rights", r"derechos fundamentales", r"drets fonamentals", r"controle de constitucionalidade", r"separa[cç][aã]o de poderes", r"organiza[cç][aã]o do estado"]),
    "administrativo": ("dir", [r"direito administrativo", r"derecho administrativo", r"dret administratiu", r"diritto amministrativo", r"administrative law", r"ato administrativo", r"acto administrativo", r"administra[cç][aã]o p[uú]blica", r"administraci[oó]n p[uú]blica"]),
    "civil_geral": ("dir", [r"direito civil", r"derecho civil", r"dret civil", r"diritto civile", r"civil law", r"pessoas e bens", r"neg[oó]cio jur[ií]dico", r"parte geral", r"personalidade jur", r"capacidade civil"]),
    "obrigacoes_contratos": ("dir", [r"obriga[cç]", r"obligacion", r"obligacions", r"obbligazion", r"obligations", r"contrat", r"contract", r"responsabilidade civil", r"responsabilidad civil", r"responsabilitat civil", r"\btort"]),
    "reais": ("dir", [r"direito das coisas", r"direitos reais", r"derechos reales", r"drets reals", r"diritti reali", r"property law", r"\bposse\b", r"propriedade", r"propiedad\b"]),
    "familia_sucessoes": ("dir", [r"fam[ií]lia", r"family law", r"fam[ií]lia", r"diritto di famiglia", r"sucess", r"sucesion", r"successi", r"succession", r"heran[cç]a", r"inheritance"]),
    "empresarial": ("dir", [r"direito empresarial", r"direito comercial", r"derecho mercantil", r"dret mercantil", r"diritto commerciale", r"company law", r"corporate law", r"commercial law", r"societ[aá]ri", r"direito de empresa", r"derecho de sociedades", r"fus[oõ]es e aquisi", r"mergers"]),
    "propriedade_intelectual": ("dir", [r"propriedade intelectual", r"propiedad intelectual", r"intellectual property", r"propriet[aà] intellettuale", r"patente", r"patent", r"copyright", r"direitos autorais", r"propriedade industrial"]),
    "penal": ("dir", [r"direito penal", r"derecho penal", r"dret penal", r"diritto penale", r"criminal law", r"teoria do crime", r"teor[ií]a del delito", r"\bcrimes?\b", r"\bdelitos?\b"]),
    "processo_penal": ("dir", [r"processo penal", r"proceso penal", r"proc[eé]s penal", r"procedura penale", r"criminal procedure", r"medidas cautelares penais"]),
    "processo_civil": ("dir", [r"processo civil", r"proceso civil", r"proc[eé]s civil", r"procedura civile", r"civil procedure", r"direito processual", r"derecho procesal", r"dret processal", r"jurisdi[cç][aã]o", r"jurisdicci", r"coisa julgada", r"cosa juzgada", r"recursos c[ií]veis", r"execu[cç][aã]o"]),
    "trabalho": ("dir", [r"direito do trabalho", r"derecho del trabajo", r"dret del treball", r"diritto del lavoro", r"labou?r law", r"employment law", r"trabalhist", r"laboral", r"sindica", r"rela[cç][aã]o de emprego", r"contrato de trabalho", r"contrato de trabajo"]),
    "seguridade": ("dir", [r"seguridade social", r"seguridad social", r"seguretat social", r"social security", r"previd[eê]nci", r"pensiones", r"pension"]),
    "tributario": ("dir", [r"tribut[aá]ri", r"derecho tributario", r"dret tributari", r"diritto tributario", r"tax law", r"direito fiscal", r"derecho financiero y tributario", r"\bimpostos\b", r"\btributos\b", r"fiscalidad", r"taxation"]),
    "financeiro_economico": ("dir", [r"direito financeiro", r"derecho financiero", r"direito econ[oô]mico", r"derecho econ[oó]mico", r"concorrencial", r"direito da concorr[eê]ncia", r"derecho de la competencia", r"competition law", r"antitrust", r"project finance"]),
    "internacional_publico": ("dir", [r"direito internacional p[uú]blico", r"derecho internacional p[uú]blico", r"dret internacional p[uú]blic", r"diritto internazionale", r"public international law", r"\btratados\b", r"treaties"]),
    "internacional_privado": ("dir", [r"direito internacional privado", r"derecho internacional privado", r"dret internacional privat", r"private international law", r"conflict of laws", r"conflitos de leis"]),
    "direitos_humanos": ("dir", [r"direitos humanos", r"derechos humanos", r"drets humans", r"diritti umani", r"human rights"]),
    "ambiental": ("dir", [r"direito ambiental", r"derecho ambiental", r"dret ambiental", r"environmental law", r"diritto dell'ambiente"]),
    "consumidor": ("dir", [r"direito do consumidor", r"derecho del consum", r"dret del consum", r"consumer law", r"consumer protection", r"rela[cç][oõ]es de consumo"]),
    "direito_digital": ("dir", [r"direito digital", r"law and technology", r"cyber ?law", r"cybercrim", r"data protection", r"prote[cç][aã]o de dados", r"\blgpd\b", r"\bgdpr\b", r"protecci[oó]n de datos", r"privacidade", r"privacy"]),
    "mediacao": ("dir", [r"media[cç][aã]o", r"mediaci", r"mediation", r"arbitra", r"concilia[cç]", r"resolu[cç][aã]o de conflitos", r"resoluci[oó]n de conflictos", r"dispute resolution", r"m[eé]todos consensuais"]),
    "etica_profissional": ("dir", [r"[eé]tica profissional", r"legal ethics", r"deontologia profissional", r"deontolog[ií]a profesional", r"professional responsibility", r"estatuto da advocacia"]),
    "hermeneutica": ("dir", [r"hermen[eê]utica", r"interpreta[cç][aã]o jur", r"argumenta[cç][aã]o jur", r"argumentaci[oó]n jur", r"legal reasoning", r"metodologia jur[ií]dica", r"metodolog[ií]a jur[ií]dica", r"legal method", r"linguagem jur[ií]dica", r"legal writing", r"legal language"]),
    "eleitoral": ("dir", [r"direito eleitoral", r"derecho electoral", r"electoral law"]),
    "criminologia": ("dir", [r"criminolog"]),
    "pratica_juridica": ("dir", [r"pr[aá]tica jur[ií]dica", r"pr[aá]ctica jur[ií]dica", r"legal clinic", r"cl[ií]nica jur[ií]dica", r"cl[ií]nica legal", r"pr[aà]ctiques jur", r"advocacia", r"abogac"]),
}



def fold(text: str) -> str:
    t = unicodedata.normalize("NFD", str(text or "").lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", t)


def concepts(text: str, min_hits: int = 1) -> set[str]:
    """Concepts whose patterns occur at least ``min_hits`` times in the (accent-folded) text."""
    t = fold(text)
    # Patterns contain accented alternatives; matching the folded text also requires folded patterns.
    out = set()
    for c, rx in _FOLDED.items():
        n = len(rx.findall(t))
        if n >= min_hits:
            out.add(c)
    return out


_FOLDED = {c: re.compile("|".join(f"(?:{fold(p)})" for p in pats)) for c, (_, pats) in THESAURUS.items()}


def domain(c: str) -> str:
    return THESAURUS[c][0]


def coverage_score(br: set[str], foreign: set[str], idf: dict[str, float]) -> dict:
    """IDF-weighted share of the Brazilian concepts present in the foreign course. Indicator only."""
    shared = sorted(br & foreign)
    total = sum(idf.get(c, 1.0) for c in br)
    got = sum(idf.get(c, 1.0) for c in shared)
    return {"shared": shared, "score": (got / total) if total else 0.0, "kind": "indicador_conceitual"}


# Broad concepts that may support but never establish thematic identity on their own.
GENERIC = {"economia", "programacao", "etica", "web", "inovacao", "estrategia"}


def is_candidate(br_title: set[str], br_all: set[str], f_title: set[str], f_all: set[str], idf: dict[str, float],
                 threshold: float = 0.4) -> bool:
    """Concept candidate rule: identity concepts must meet on both sides, plus the weighted indicator.

    * the foreign course (title, notes or syllabus) must contain a concept of the Brazilian TITLE;
    * the foreign TITLE must contain a concept of the Brazilian ementa;
    * the IDF-weighted indicator must reach ``threshold``.
    A shared generic concept alone (e.g. 'programação') never makes a candidate.
    """
    core = br_title or br_all
    specific_core = core - GENERIC
    # Identity: a specific concept must be shared, unless the Brazilian side itself is only generic.
    if specific_core:
        if not (specific_core & f_all):
            return False
    elif not (core & f_all):
        return False
    title_overlap = f_title & br_all
    if not (title_overlap - GENERIC or (title_overlap and not (br_all - GENERIC))):
        return False
    return coverage_score(br_all, f_all, idf)["score"] >= threshold


_TCC = re.compile(r"\b(?:tcc|trabalho de conclus|trabalho de gradua)", re.I)
_EST = re.compile(r"\best[aá]gio", re.I)
_OPT = re.compile(r"^\s*optativa\s+[ivxlc\d]+\s*$", re.I)


def row_kind(name: str) -> str:
    if _TCC.search(fold(name)):
        return "tcc"
    if _EST.search(fold(name)):
        return "estagio"
    if _OPT.match(fold(name)):
        return "optativa_livre"
    return "disciplina"


RULE_NOTES = {
    "tcc": "Trabalho de conclusão segue regulamento próprio do curso; aproveitamento por disciplina estrangeira não é a via usual e depende da coordenação.",
    "estagio": "Estágio segue regra própria: o Manual do Intercâmbio 2024 (§6.5) prevê requerimento de aproveitamento de horas de estágio no exterior, decidido pela coordenação e pelo RINT.",
    "optativa_livre": "Optativa de livre escolha: qualquer disciplina da macroárea do curso pode ser proposta no Plano de Estudos (Manual 2024 §3.3), sujeita à coordenação.",
}
MIN_AREA_COURSES = 8


def crossing_state(kind: str, pareceres: list, registered: list, semantic: list, area_courses: int) -> dict:
    if pareceres:
        best = max(pareceres, key=lambda p: ["evidencia_insuficiente", "baixa_afinidade", "afinidade_parcial", "alta_afinidade"].index(p["conclusionClass"]))
        return {"state": "parecer_concluido", "note": f"{len(pareceres)} parecer(es) individual(is); melhor classe documental: {best['conclusionClass']}."}
    if registered:
        return {"state": "candidata_registrada", "note": f"{len(registered)} candidata(s) já cadastrada(s) aguardando documentos ou parecer."}
    if kind in RULE_NOTES:
        return {"state": "regra_especifica", "note": RULE_NOTES[kind]}
    if semantic:
        return {"state": "candidata_semantica", "note": f"{len(semantic)} disciplina(s) do catálogo indexado compartilham conceitos da ementa; requer leitura das ementas."}
    if area_courses < MIN_AREA_COURSES:
        return {"state": "catalogo_insuficiente", "note": f"Somente {area_courses} disciplina(s) da área indexada(s) nesta universidade: não é possível concluir; ampliar a coleta do catálogo."}
    return {"state": "sem_candidata_no_catalogo_indexado",
            "note": f"{area_courses} disciplinas da área foram examinadas por conceitos sem sobreposição suficiente. Isso não demonstra incompatibilidade: o catálogo indexado pode ser parcial e títulos podem omitir conteúdos."}


# ------------------------------------------------------------------ build

def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def _cached_text(url: str) -> str:
    p = ROOT / ".cache" / "text" / (hashlib.sha256(str(url).encode()).hexdigest()[:24] + ".txt")
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _evidence_headings(source: dict) -> list[str]:
    headings = [source.get("headingExact"), source.get("evidenceHeading")]
    headings.extend(p.get("exactHeading") for p in source.get("evidencePointers", []) if isinstance(p, dict))
    if source.get("officialCode") and source.get("officialTitle"):
        headings.append(f"{source['officialCode']} {source['officialTitle']}")
    headings.extend(source.get("sourceCourseTitles", []))
    return list(dict.fromkeys(h for h in headings if h))


def cached_course_text(url: str, source: dict, peers: list[dict]) -> str:
    """Retrieve an audited course section, never unrelated courses in a shared source."""
    if len(source.get("sourceCourseTitles", [])) > 1:
        return ""  # Alternative units cannot be pooled into one course profile.
    text = _cached_text(url)
    if not text:
        return ""
    shared = len({p.get("code") for p in peers}) > 1
    compendium = "compendium" in str(source.get("sourceType", "")) + str(source.get("documentType", ""))
    if not shared and not compendium:
        return text[:40000]
    headings = _evidence_headings(source)
    normalize = lambda value: re.sub(r"\s+", " ", value).strip().casefold()
    # HTML heading elements delimit even unregistered neighbours, unlike a title-only search.
    sha = str(source.get("sha256") or "")
    if re.fullmatch(r"[a-fA-F0-9]{64}", sha):
        for directory in ("audited-public-http", "docs"):
            raw = ROOT / ".cache" / directory / (sha + ".html")
            if not raw.exists():
                continue
            raw_bytes = raw.read_bytes()
            if hashlib.sha256(raw_bytes).hexdigest() != sha:
                continue
            soup = BeautifulSoup(raw_bytes, "html.parser")
            found = [h for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "dt"])
                     if normalize(h.get_text(" ", strip=True)) in {normalize(h) for h in headings}]
            if len(found) != 1:
                return ""
            chunks = []
            for node in found[0].next_elements:
                if isinstance(node, Tag) and node.name in ("h1", "h2", "h3", "h4", "h5", "h6", "dt"):
                    break
                if isinstance(node, NavigableString) and node.parent.name not in ("script", "style") and node.strip():
                    chunks.append(str(node).strip())
            return "\n".join(chunks)[:40000]
    pages = list(source.get("evidencePages") or [])
    for pointer in source.get("evidencePointers", []):
        if isinstance(pointer, dict):
            pages += pointer.get("pages") or []
    if pages:
        document_pages = text.split("\f")
        if any(not isinstance(n, int) or n < 1 or n > len(document_pages) for n in pages):
            return ""
        text = "\n".join(document_pages[n - 1] for n in sorted(set(pages)))
    elif not source.get("headingExact"):
        return ""  # Missing shared-source boundaries are not permission to use the entire page.
    # Text-cache fallback: exact audited heading, then stop at the next known course heading.
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if normalize(line) in {normalize(h) for h in headings}]
    if not starts:
        return ""
    start = starts[0]
    other_headings = {normalize(h) for peer in peers if peer.get("code") != source.get("code") for h in _evidence_headings(peer)}
    end = next((i for i in range(start + 1, len(lines)) if normalize(lines[i]) in other_headings), len(lines))
    if not pages:
        # Brief HTML descriptions are a single adjacent paragraph in this fallback.
        paragraph = next((line for line in lines[start + 1:end] if line.strip()), "")
        return "\n".join([lines[start], paragraph])[:40000]
    return "\n".join(lines[start:end])[:40000]


def main() -> int:
    data = _load("data.json")
    programs = _load("syllabi/programas.json") if (ROOT / "syllabi/programas.json").exists() else {"brazil": {}, "foreign": {}}
    records = {(r["universityId"], r["foreignCode"]): r for r in _load("syllabi/records.json")["foreign"]}
    verified = {}
    source_peers = collections.defaultdict(list)
    # Programmes verified later by resolve_syllabi.py count as individual syllabi too.
    if (ROOT / "syllabi/fontes-verificadas.json").exists():
        for v in _load("syllabi/fontes-verificadas.json").get("foreign", []):
            if v.get("individualSyllabus"):
                verified[(v["universityId"], v["code"])] = v
                source_peers[v["source"]].append(v)
                records[(v["universityId"], v["code"])] = {"status": "ementa_individual", "document": v["source"]}
    for key, record in records.items():
        url = record.get("document")
        if url and not any(peer.get("code") == key[1] for peer in source_peers[url]):
            source_peers[url].append({"code": key[1], "source": url})
    pidx = _load("syllabi/pareceres-index.json")["pareceres"] if (ROOT / "syllabi/pareceres-index.json").exists() else []
    triage = _load("triagem.json")["pairs"]
    unis = data["universities"]

    # Foreign concept profiles: title counts twice as strong evidence; document text needs 2 hits (bibliography noise).
    fprof = {}
    unscoped_documents = []
    for f in data["foreignCourses"]:
        key = (f["universityId"], f["code"])
        rec = records.get(key, {})
        title = concepts(f.get("name", ""))
        notes = concepts(" ".join(str(f.get(k) or "") for k in ("topics", "role")))
        url = rec.get("document")
        document_text = cached_course_text(url, verified.get(key, {}), source_peers.get(url, [])) if rec.get("status") == "ementa_individual" else ""
        if rec.get("status") == "ementa_individual" and not document_text:
            unscoped_documents.append(list(key))
        doc = concepts(document_text, min_hits=2)
        fprof[key] = {"title": title, "all": title | notes | doc, "docState": "ementa_individual" if rec.get("status") == "ementa_individual" else (rec.get("status") or "sem_registro")}
    n = len(fprof)
    df = collections.Counter(c for v in fprof.values() for c in v["all"])
    idf = {c: math.log((n + 1) / (df.get(c, 0) + 1)) + 1 for c in THESAURUS}

    by_uni = collections.defaultdict(list)
    for f in data["foreignCourses"]:
        if f.get("sourceEligibility") != "outside_agreement":
            by_uni[f["universityId"]].append(f)
    # Registered candidates keyed by matrix row index: Direito/Administração records use mackName with empty mackCode.
    registered = collections.defaultdict(list)
    rows_by_course = {c["id"]: c["rows"] for c in data["courses"]}
    for m in data["matches"]:
        rows = rows_by_course[m["courseId"]]
        idx = next((i for i, x in enumerate(rows) if m.get("mackCode") and (x.get("id") or x["name"]) == m["mackCode"]), None)
        if idx is None:
            idx = next((i for i, x in enumerate(rows) if x["name"].casefold() == str(m.get("mackName", "")).casefold()), None)
        if idx is not None:
            registered[(m["courseId"], idx, m["universityId"])].append(m["foreignCode"])
    par = collections.defaultdict(list)
    for p in pidx:
        par[tuple(p["cell"])].append({"id": p["id"], "conclusionClass": p["conclusionClass"]})

    # Brazilian concept profiles: official ementa/content when available, else matrix title + abstract.
    bprof = {}
    for c in data["courses"]:
        for i, r in enumerate(c["rows"]):
            code = r.get("id") or r["name"]
            bp = programs["brazil"].get(f"{c['id']}|{code}", {})
            official = bp.get("status") == "lido"
            text = " ".join([r["name"], bp.get("ementa", ""), " ".join(bp.get("programContent") or [])]) if official else " ".join([r["name"], r.get("abstract", "")])
            bprof[(c["id"], i)] = {"code": code, "name": r["name"], "concepts": concepts(text), "title": concepts(r["name"]),
                                   "official": official, "kind": row_kind(r["name"])}

    out_rows, combos = [], []
    states = collections.Counter()
    new_candidates = 0
    for cid, ri, ui, *_ in triage:
        b = bprof[(cid, ri)]
        u = unis[ui]
        bc = b["concepts"]
        doms = collections.Counter(domain(x) for x in bc)
        main_dom = doms.most_common(1)[0][0] if doms else None
        foreign = by_uni.get(u["id"], [])
        area = [f for f in foreign if main_dom and any(domain(x) == main_dom for x in fprof[(u["id"], f["code"])]["all"])]
        reg = registered.get((cid, ri, u["id"]), [])
        sem = []
        if bc and b["kind"] == "disciplina":
            for f in foreign:
                prof = fprof[(u["id"], f["code"])]
                if f["code"] not in reg and is_candidate(b["title"], bc, prof["title"], prof["all"], idf):
                    s = coverage_score(bc, prof["all"], idf)
                    sem.append([f["code"], round(s["score"], 3), s["shared"], prof["docState"]])
            sem.sort(key=lambda x: (-x[1], x[0]))
            sem = sem[:5]
            # Combined coverage: two foreign courses that together reach what neither reaches alone.
            # Each member must itself be thematically anchored (its title shares a concept with the ementa).
            anchored = {f["code"] for f in foreign if fprof[(u["id"], f["code"])]["title"] & bc}
            singles = {f["code"]: fprof[(u["id"], f["code"])]["all"] & bc for f in foreign}
            best_single = max((coverage_score(bc, v, idf)["score"] for v in singles.values()), default=0)
            if len(bc) >= 3 and best_single < 0.6:
                cand = [k for k, v in singles.items() if v and k in anchored]
                best = None
                for a, z in combinations(cand[:60], 2):
                    sc = coverage_score(bc, singles[a] | singles[z], idf)["score"]
                    if sc >= 0.75 and sc - best_single >= 0.25 and (best is None or sc > best[2]):
                        best = (a, z, sc)
                if best:
                    combos.append({"cell": [cid, ri, ui], "foreign": [best[0], best[1]], "indicator": round(best[2], 3),
                                   "bestSingle": round(best_single, 3),
                                   "caveat": "Combinação depende de autorização específica; a mesma carga horária estrangeira não pode ser contada para dois requisitos."})
        st = crossing_state(b["kind"], par.get((cid, ri, ui), []), reg, sem, len(area))
        if st["state"] == "candidata_semantica":
            new_candidates += len(sem)
        if not b["official"] and st["state"] in ("candidata_semantica", "sem_candidata_no_catalogo_indexado"):
            st["note"] += " Conceitos brasileiros lidos apenas do título/resumo da matriz (ementa oficial não vinculada)."
        states[st["state"]] += 1
        out_rows.append([cid, ri, ui, st["state"], sem, st["note"]])

    meta = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "crossings": len(out_rows), "states": dict(states), "newSemanticCandidates": new_candidates,
        "combinedSuggestions": len(combos), "concepts": len(THESAURUS),
        "unscopedDocumentProfiles": unscoped_documents,
        "documentScopePolicy": "Compêndios usam somente rubrica individual ou páginas auditadas; sem delimitação segura, recuperação usa apenas título/notas próprios. Documento não delimitado não significa ementa inexistente.",
        "method": "Tesauro multilíngue controlado (pt/en/es/ca/it/fr/ro); conceitos da ementa oficial brasileira x título, notas de catálogo e ementa individual estrangeira (≥2 ocorrências); peso IDF; limiar 0,4 com ≥2 conceitos. Indicador de recuperação, não percentual de equivalência.",
        "statesLegend": {s: s for s in STATES},
        "neverMeans": "Nenhum estado significa incompatibilidade ou aprovação.",
    }
    OUT.write_text(json.dumps({"meta": meta, "conceptDomains": {c: v[0] for c, v in THESAURUS.items()},
                               "crossings": out_rows, "combined": combos}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("semantic triage:", meta["states"], "new candidates:", new_candidates, "combined:", len(combos))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
