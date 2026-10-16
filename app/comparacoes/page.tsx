import Link from "next/link";
import { getRepository, normalize } from "../../lib/data";
import {
  CourseSelect,
  Empty,
  Heading,
  Pagination,
  ReviewCard,
  Search,
  pageNumber,
  queryValue,
  type Query,
} from "../ui";
export const metadata = { title: "Comparar ementas" };
export default async function Comparisons({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const repository = getRepository();
  const reviews = repository.reviews.filter(
    (review) =>
      (!queryValue(query, "curso") ||
        review.brazil.courseId === queryValue(query, "curso")) &&
      (!queryValue(query, "universidade") ||
        review.foreign.some(
          (item) => item.universityId === queryValue(query, "universidade"),
        )) &&
      (!queryValue(query, "classe") ||
        review.conclusionClass === queryValue(query, "classe")) &&
      normalize(
        [
          review.brazil.name,
          ...review.foreign.map((item) => `${item.name} ${item.university}`),
        ].join(" "),
      ).includes(normalize(queryValue(query, "q"))),
  );
  const page = pageNumber(query, reviews.length);
  return (
    <div className="page-shell">
      <Heading
        eyebrow="03 / Comparar com evidências"
        title="Muito além do título."
      >
        Pareceres com tópicos lado a lado, fontes, lacunas e análise de horas.
        Toda conclusão é preliminar e depende da coordenação.
      </Heading>
      <form className="filters wrap">
        <Search
          query={queryValue(query, "q")}
          placeholder="Disciplina ou instituição"
        />
        <CourseSelect value={queryValue(query, "curso")} />
        <label>
          Universidade
          <select
            name="universidade"
            defaultValue={queryValue(query, "universidade")}
          >
            <option value="">Todas as universidades</option>
            {repository.universities
              .filter((university) =>
                repository.reviews.some((review) =>
                  review.foreign.some(
                    (item) => item.universityId === university.id,
                  ),
                ),
              )
              .map((university) => (
                <option key={university.id} value={university.id}>
                  {university.name}
                </option>
              ))}
          </select>
        </label>
        <button className="button dark">Comparar →</button>
        <Link href="/comparacoes">Limpar</Link>
      </form>
      <p className="result-count">
        {reviews.length} pareceres documentados · {repository.stats.homologated}{" "}
        homologações registradas
      </p>
      <div className="review-grid">
        {reviews.slice((page - 1) * 36, page * 36).map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
      {!reviews.length && (
        <Empty>
          Ainda não há parecer com esses filtros. Consulte a disciplina para ver
          candidatas preliminares e documentação disponível.
        </Empty>
      )}
      <Pagination
        total={reviews.length}
        page={page}
        query={query}
        base="/comparacoes"
      />
      <div className="notice">
        <strong>Como interpretar</strong>
        <p>
          “Não encontrado” descreve o conteúdo nos documentos examinados. Não
          significa que o tópico não seja ensinado. Tópicos parciais não são
          contados como cobertura integral; créditos ECTS não são convertidos em
          horas de contato.
        </p>
      </div>
    </div>
  );
}
