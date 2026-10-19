import { filteredPageMetadata } from "../../lib/page-metadata";
import Link from "next/link";
import { getRepository, normalize } from "../../lib/data";
import {
  Badge,
  CourseSelect,
  Heading,
  Search,
  Source,
  queryValue,
  type Query,
} from "../ui";
export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  return filteredPageMetadata("Idiomas e requisitos", await searchParams);
}
export default async function Languages({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const repository = getRepository();
  const universities = repository.universities.filter(
    (item) =>
      (!queryValue(query, "curso") ||
        item.courses[queryValue(query, "curso")]) &&
      normalize(
        `${item.name} ${item.country} ${item.language.required} ${item.language.acceptedTests}`,
      ).includes(normalize(queryValue(query, "q"))),
  );
  return (
    <div className="page-shell">
      <Heading
        eyebrow="05 / Prepare sua chegada"
        title="Encontre a sua língua."
      >
        Requisitos de proficiência por instituição. Confirme o teste, a nota e a
        validade com a universidade e a COI antes da candidatura.
      </Heading>
      <form className="filters">
        <Search
          query={queryValue(query, "q")}
          placeholder="País, idioma, teste ou instituição"
        />
        <CourseSelect value={queryValue(query, "curso")} />
        <button className="button dark">Buscar →</button>
      </form>
      <div className="notice">
        <strong>Atenção às inconsistências da planilha</strong>
        <p>
          Campos que repetem nomes de instituições não comprovam idioma aceito.
          Uma indicação de MLC também não substitui confirmação do requisito
          atual ou do idioma das disciplinas.
        </p>
      </div>
      <p className="result-count">{universities.length} instituições</p>
      <div className="university-grid">
        {universities.map((item) => (
          <article className="panel" key={item.id}>
            <p className="eyebrow">{item.country}</p>
            <h2>
              <Link href={`/universidades/${item.id}`}>{item.name}</Link>
            </h2>
            {item.language.dataIssue && (
              <Badge>Fonte inconsistente · confirmar</Badge>
            )}
            <dl className="facts">
              <div>
                <dt>Exigência registrada</dt>
                <dd>{item.language.required || "Não informada"}</dd>
              </div>
              <div>
                <dt>Testes</dt>
                <dd>{item.language.acceptedTests || "Não informados"}</dd>
              </div>
              <div>
                <dt>Nota / nível mínimo</dt>
                <dd>{item.language.minimumScore || "Não informado"}</dd>
              </div>
              <div>
                <dt>MLC</dt>
                <dd>
                  {item.language.mlcAccepted == null
                    ? "Não confirmado"
                    : item.language.mlcAccepted
                      ? "Aceitação indicada na base; confirmar"
                      : "Não indicado como aceito"}
                </dd>
              </div>
            </dl>
            <p>{item.language.notes}</p>
            <Source url={item.language.source} />
          </article>
        ))}
      </div>
      {!universities.length && (
        <p className="empty">Nenhum requisito encontrado com esses filtros.</p>
      )}
    </div>
  );
}
