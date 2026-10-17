import { getRepository } from "../../lib/data";
import { Heading, Source } from "../ui";
export const metadata = { title: "Fontes e metodologia" };
export default function Method() {
  const { meta } = getRepository();
  return (
    <div className="page-shell prose-page">
      <Heading
        eyebrow="08 / Pesquisa verificável"
        title="Toda conclusão tem um caminho."
      >
        Projeto independente de apoio acadêmico. A decisão de aproveitamento
        cabe à coordenação do curso e à COI.
      </Heading>
      <section>
        <h2>Quatro perguntas diferentes</h2>
        <ol className="steps">
          <li>
            <strong>Conteúdo:</strong> quais tópicos do programa brasileiro
            aparecem explicitamente no estrangeiro?
          </li>
          <li>
            <strong>Horas:</strong> as duas cargas usam a mesma unidade, duração
            e período? ECTS é carga total de trabalho e não vira horas de
            contato.
          </li>
          <li>
            <strong>Matrícula:</strong> a disciplina será ofertada no semestre,
            no idioma e no nível necessários? É acessível a intercambistas?
          </li>
          <li>
            <strong>Aprovação:</strong> existe decisão institucional registrada?
            Afinidade acadêmica não constitui homologação.
          </li>
        </ol>
      </section>
      <section>
        <h2>Como interpretar os tópicos</h2>
        <p>
          “Coberto” exige evidência explícita. “Parcial” indica tratamento
          incompleto. “Não encontrado” se restringe aos documentos examinados.
          “Não verificável” indica documentação insuficiente. Contagem de
          palavras e títulos semelhantes não demonstram equivalência curricular.
        </p>
        <p>
          Pareceres indicam fontes, trechos ou localização, justificativa,
          confiança, limitações e necessidade de segunda revisão. Uma combinação
          de disciplinas exige avaliação conjunta.
        </p>
      </section>
      <section>
        <h2>Procedência e atualização</h2>
        <p>
          A base de referência é de {meta.asOf}, para planejamento de{" "}
          {meta.semester}. Documentos podem ser de anos anteriores; a vigência é
          explicitada em cada ficha.
        </p>
        <p>
          Os dados são arquivos JSON versionados no Git. URLs identificam as
          fontes e hashes SHA-256 identificam os documentos examinados. Um hash
          prova identidade de arquivo, não autenticidade, atualidade ou
          aprovação. Histórico de alterações permanece no repositório; datas de
          revisão ficam nos pareceres.
        </p>
        <p>
          Atualizações são revisadas no código e publicadas com um novo deploy.
          A consulta é pública e não exige conta.
        </p>
      </section>
      <section>
        <h2>Fontes institucionais</h2>
        <Source url="https://www.mackenzie.br/universidade/fluxo-continuo">
          Programa Fluxo Contínuo e documentos COI ↗
        </Source>
        <p>
          A planilha de vagas indica elegibilidade por curso. Não garante
          disponibilidade de uma disciplina, vaga individual ou aceitação pela
          instituição anfitriã.
        </p>
      </section>
    </div>
  );
}
