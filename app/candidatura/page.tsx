import type { Metadata } from "next";
import Link from "next/link";
import { Checklist } from "./checklist";
import styles from "./preview.module.css";

export const metadata: Metadata = {
  title: "Como se candidatar",
};
const official = "https://www.mackenzie.br/universidade/coi/editais-abertos";
const documents = "https://www.mackenzie.br/universidade/fluxo-continuo";
const pdf =
  "https://www.mackenzie.br/fileadmin/ARQUIVOS/Public/1-mackenzie/universidade/coi/2026/Fluxo_Cont%C3%ADnuo/IN_RE_110_2026_Edital_PROGRAMA_FLUXO_CONT%C3%8DNUO_1S_2027_COI_Assinada.pdf";
const dates = [
  [
    "13 out — 14 dez 2026",
    "Inscrição",
    "Separe os documentos e envie o Forms.",
  ],
  [
    "13 nov 2026",
    "Lista definitiva de universidades",
    "Confira as vagas antes de concluir suas escolhas.",
  ],
  [
    "15 dez 2026 / 11 jan 2027",
    "Recebidas / deferidas",
    "Acompanhe as listas da COI.",
  ],
  [
    "12 — 18 jan 2027",
    "Reconsideração",
    "Exclusiva para indeferimento por certificado de idioma (item 3.1).",
  ],
  [
    "20 — 27 jan 2027",
    "Vagas remanescentes",
    "Pré-seleção em 20/01; desistência até 28/01; resultado das remanescentes em 29/01.",
  ],
  [
    "Até 05 fev 2027",
    "Resultado final",
    "Vagas residuais: 08/02 a 10/03, com edital e cronograma próprios.",
  ],
  [
    "15 / 16 — 25 mar 2027",
    "Reunião / nomeação",
    "Reunião obrigatória em 15/03. Treinamento intercultural a partir de 03/05.",
  ],
];
export default function ApplicationGuide() {
  return (
    <div className={styles.page}>
      <Link href="/" className={styles.back}>
        ← Início
      </Link>
      <header className={styles.hero}>
        <div>
          <p className={styles.kicker}>Guia de candidatura / Fluxo Contínuo</p>
          <h1>
            Seu intercâmbio
            <br />
            começa <em>aqui.</em>
          </h1>
          <p className={styles.intro}>
            Do primeiro documento ao envio da inscrição. Um passo de cada vez.
          </p>
          <a
            className={styles.button}
            href="https://forms.cloud.microsoft/r/VMKaSyTrJz"
            target="_blank"
            rel="noreferrer"
          >
            Abrir inscrição oficial <span aria-hidden="true">↗</span>
          </a>
          <p className={styles.caption}>
            Acesse com seu e-mail Mackenzista. O envio acontece no Microsoft
            Forms.
          </p>
        </div>
        <aside className={styles.edition}>
          <span className={styles.kicker}>IN-RE 110/2026</span>
          <strong>
            2º semestre
            <br />
            de 2027
          </strong>
          <p>
            Quando você vai.
            <br />
            Processo seletivo: 1S/2027.
          </p>
          <a href={pdf}>Consultar edital assinado ↗</a>
        </aside>
      </header>
      <div className={styles.notice}>
        <strong>Atenção ao prazo.</strong> O PDF assinado encerra as inscrições
        em <b>14/12/2026</b>; a <a href={official}>página da COI</a> informa{" "}
        <b>14/12/2027</b>. Há divergência nas fontes: confirme com a COI antes
        de depender da data mais longa.
      </div>
      <nav className={styles.nav} aria-label="Neste guia">
        <a href="#requisitos">01 / Posso participar?</a>
        <a href="#documentos">02 / Preparar documentos</a>
        <a href="#cronograma">03 / Acompanhar prazos</a>
      </nav>
      <section id="requisitos" className={styles.section}>
        <div className={styles.sectionHeading}>
          <p className={styles.kicker}>01 / Antes de escolher</p>
          <h2>Confira seu ponto de partida.</h2>
          <a href={`${pdf}#page=1`}>Requisitos no edital, pp. 1–2 ↗</a>
        </div>
        <div className={styles.requirements}>
          <article>
            <strong>20%–90%</strong>
            <p>
              de integralização da matriz na candidatura — não é um filtro por
              etapa.
            </p>
          </article>
          <article>
            <strong>Média ≥ 7</strong>
            <p>
              Matrícula regular, sem punição disciplinar e com componentes a
              cursar na UPM ao retornar.
            </p>
          </article>
          <article>
            <strong>Até 2 destinos</strong>
            <p>
              Primeira e segunda opções. Vagas e elegibilidade devem ser
              conferidas na planilha da edição.
            </p>
          </article>
        </div>
        <details className={styles.detail}>
          <summary>Idioma, passaporte e exceções</summary>
          <p>
            Idioma: B2 ou exigência superior do destino; comprove cada idioma
            das disciplinas. O termo do Apêndice IV só substitui o certificado
            quando o destino não o exige, acompanhado de prova oficial da
            isenção. Passaporte válido por toda a mobilidade. Para Duke/Direito,
            integralização de 70%–90%.
          </p>
          <a href={`${pdf}#page=4`}>Conferir regras de idioma ↗</a>
        </details>
      </section>
      <section id="documentos" className={styles.section}>
        <div className={styles.sectionHeading}>
          <p className={styles.kicker}>02 / Prepare com calma</p>
          <h2>Sua pasta de candidatura.</h2>
          <p>
            Marque o que você já preparou. A lista reinicia ao sair; nenhum
            documento é enviado aqui.
          </p>
          <a href={`${pdf}#page=3`}>Documentação obrigatória, item 3.1 ↗</a>
        </div>
        <Checklist />
        <details className={styles.detail}>
          <summary>Como montar o plano de estudos?</summary>
          <p>
            Prepare um plano preliminar por universidade: 4–5 disciplinas por
            semestre, idealmente 30 ECTS na Europa. Na inscrição, basta sua
            assinatura; aprovações vêm depois da seleção. O catálogo atual pode
            apoiar o planejamento quando o próximo ainda não foi publicado.
          </p>
          <a href={`${pdf}#page=15`}>Instruções completas, Apêndice II.b ↗</a>
          <p>
            <Link href="/plano">Abrir o planejador de disciplinas →</Link>
          </p>
        </details>
        <details className={styles.detail}>
          <summary>Certificados opcionais e classificação</summary>
          <p>
            Pesquisa, extensão, monitoria e programas COI podem acrescentar
            pontos conforme os critérios do item 3.2. Não substituem documentos
            obrigatórios. Confira assinaturas, traduções e validade antes do
            envio.
          </p>
          <a href={`${pdf}#page=4`}>Critérios e pontuação ↗</a>
        </details>
      </section>
      <section id="cronograma" className={styles.section}>
        <div className={styles.sectionHeading}>
          <p className={styles.kicker}>03 / Próximos passos</p>
          <h2>Uma coisa de cada vez.</h2>
          <a href={`${pdf}#page=10`}>Cronograma completo, item 7 ↗</a>
        </div>
        <ol className={styles.timeline}>
          {dates.map(([date, title, description]) => (
            <li key={title}>
              <span>{date}</span>
              <div>
                <h3>{title}</h3>
                <p>{description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <footer className={styles.footer}>
        <div>
          <h2>Pronto para dar o próximo passo?</h2>
          <p>
            Seleção UPM, nomeação e aceitação no destino são etapas distintas.
          </p>
          <a
            className={styles.button}
            href="https://forms.cloud.microsoft/r/VMKaSyTrJz"
            target="_blank"
            rel="noreferrer"
          >
            Ir para o Forms oficial ↗
          </a>
        </div>
        <div>
          <p className={styles.kicker}>
            Fontes oficiais · consultadas em 19/10/2026
          </p>
          <a href={official}>Editais e resultados da COI ↗</a>
          <a href={documents}>Planilha, modelos e formulários ↗</a>
          <a href={pdf}>Edital IN-RE 110/2026 completo ↗</a>
          <p className={styles.caption}>
            Guia explicativo independente. Consulte o edital e suas atualizações
            para a candidatura.
          </p>
        </div>
      </footer>
    </div>
  );
}
