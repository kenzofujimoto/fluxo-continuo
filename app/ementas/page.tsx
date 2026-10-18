import Link from "next/link";
import {
  disciplinePath,
  getRepository,
  label,
  normalize,
  searchDisciplines,
} from "../../lib/data";
import {
  CourseSelect,
  Heading,
  Pagination,
  Search,
  Source,
  pageNumber,
  queryValue,
  type Query,
} from "../ui";
export const metadata = { title: "Biblioteca de ementas" };
export default async function Syllabi({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const repository = getRepository();
  const foreign = queryValue(query, "origem") === "exterior";
  const brazil = searchDisciplines(
    queryValue(query, "q"),
    queryValue(query, "curso"),
  );
  const abroad = repository.foreignCourses.filter((item) => {
    const document = repository.records.find(
      (record) =>
        record.universityId === item.universityId &&
        record.foreignCode === item.code,
    );
    return (
      (!queryValue(query, "universidade") ||
        item.universityId === queryValue(query, "universidade")) &&
      (!queryValue(query, "status") ||
        document?.status === queryValue(query, "status")) &&
      normalize(
        `${item.name} ${item.code} ${repository.universities.find((university) => university.id === item.universityId)?.name}`,
      ).includes(normalize(queryValue(query, "q")))
    );
  });
  const total = foreign ? abroad.length : brazil.length;
  const page = pageNumber(query, total);
  return (
    <div className="page-shell">
      <Heading
        eyebrow="04 / Biblioteca documental"
        title="Conhecimento com fonte."
      >
        Documentos brasileiros e registros estrangeiros, com procedência e
        limites explícitos. Título de catálogo não é ementa integral.
      </Heading>
      <div className="tabs">
        <Link aria-current={!foreign ? "page" : undefined} href="/ementas">
          Mackenzie · {repository.stats.disciplines}
        </Link>
        <Link
          aria-current={foreign ? "page" : undefined}
          href="/ementas?origem=exterior"
        >
          Exterior · {repository.stats.foreignCourses}
        </Link>
      </div>
      <form className="filters wrap">
        <input
          type="hidden"
          name="origem"
          value={foreign ? "exterior" : "brasil"}
        />
        <Search query={queryValue(query, "q")} />
        {!foreign && <CourseSelect value={queryValue(query, "curso")} />}
        {foreign && (
          <>
            <label>
              Universidade
              <select
                name="universidade"
                defaultValue={queryValue(query, "universidade")}
              >
                <option value="">Todas as instituições</option>
                {repository.universities.map((university) => (
                  <option key={university.id} value={university.id}>
                    {university.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Documentação
              <select name="status" defaultValue={queryValue(query, "status")}>
                <option value="">Todos os estados</option>
                {[
                  "ementa_individual",
                  "pagina_com_conteudo",
                  "catalogo_ou_matriz",
                  "indisponivel",
                ].map((status) => (
                  <option key={status} value={status}>
                    {label(status)}
                  </option>
                ))}
              </select>
            </label>
          </>
        )}
        <button className="button dark">Consultar →</button>
      </form>
      <p className="result-count">{total} registros encontrados</p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Disciplina</th>
              <th>Documentação</th>
              <th>Fonte e identificação</th>
            </tr>
          </thead>
          <tbody>
            {foreign
              ? abroad.slice((page - 1) * 36, page * 36).map((item) => {
                  const record = repository.records.find(
                    (record) =>
                      record.universityId === item.universityId &&
                      record.foreignCode === item.code,
                  );
                  return (
                    <tr key={`${item.universityId}|${item.code}`}>
                      <td>
                        <strong>{item.name}</strong>
                        <p className="muted">
                          {item.code} ·{" "}
                          <Link href={`/universidades/${item.universityId}`}>
                            {
                              repository.universities.find(
                                (university) =>
                                  university.id === item.universityId,
                              )?.name
                            }
                          </Link>
                        </p>
                      </td>
                      <td>
                        {label(record?.status ?? "nao_verificado")}
                        <p className="muted">{record?.reason}</p>
                        {item.sourceEligibility === "outside_agreement" && (
                          <p>Fora do escopo do acordo</p>
                        )}
                        {item.limitations && <p className="muted">{item.limitations}</p>}
                      </td>
                      <td>
                        <Source url={record?.source ?? item.source} />
                        <p className="hash mono">
                          SHA-256: {record?.sha256 ?? "não registrado"}
                        </p>
                      </td>
                    </tr>
                  );
                })
              : brazil
                  .slice((page - 1) * 36, page * 36)
                  .map(({ course, row }) => {
                    const key = row.id || row.name;
                    const program = repository.programs[`${course.id}|${key}`];
                    const pending = repository.pending.brazil[
                      course.id
                    ]?.rows.find((item) => item.code === key);
                    return (
                      <tr key={`${course.id}|${key}`}>
                        <td>
                          <Link href={disciplinePath(course.id, row)}>
                            <strong>{row.name}</strong>
                          </Link>
                          <p className="muted">
                            {course.name} · {row.id || "Código não informado"}
                          </p>
                        </td>
                        <td>
                          {pending?.label ?? "Documentação a verificar"}
                          <p className="muted">{program?.currencyNote}</p>
                        </td>
                        <td>
                          <Source
                            url={
                              program?.source ??
                              row.syllabusUrl ??
                              course.source
                            }
                          />
                          <p className="hash mono">
                            SHA-256: {program?.sha256 ?? "não registrado"}
                          </p>
                        </td>
                      </tr>
                    );
                  })}
          </tbody>
        </table>
        {!total && (
          <p className="empty">Nenhum documento corresponde aos filtros.</p>
        )}
      </div>
      <Pagination total={total} page={page} query={query} base="/ementas" />
    </div>
  );
}
