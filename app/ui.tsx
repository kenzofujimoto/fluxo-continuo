import Link from "next/link";
import type { ReactNode } from "react";
import {
  comparisonPath,
  disciplinePath,
  getRepository,
  label,
  safeSource,
  type Review,
} from "../lib/data";

export function Source({
  url,
  children = "Consultar fonte oficial ↗",
}: {
  url?: string | null;
  children?: ReactNode;
}) {
  const href = safeSource(url);
  return href ? (
    <a className="source" href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ) : (
    <span className="muted">Fonte não informada</span>
  );
}
export function Badge({
  children,
  tone = "",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function conclusionTone(conclusion: string) {
  return conclusion === "alta_afinidade"
    ? "lime"
    : conclusion === "afinidade_parcial"
      ? "amber"
      : "";
}
export function Heading({
  eyebrow,
  title,
  children,
}: {
  eyebrow: ReactNode;
  title: string;
  children?: ReactNode;
}) {
  return (
    <header className="page-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      {children && <div className="lede">{children}</div>}
    </header>
  );
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty">
      <span className="eyebrow">Nenhum resultado</span>
      <p>{children}</p>
      <Link href="/disciplinas">Explorar disciplinas →</Link>
    </div>
  );
}
export function ReviewCard({ review }: { review: Review }) {
  return (
    <Link className="review-card" href={comparisonPath(review)}>
      <div className="flex flex-wrap gap-2">
        <Badge>{review.brazil.courseName}</Badge>
        <Badge tone={conclusionTone(review.conclusionClass)}>
          {label(review.conclusionClass)}
        </Badge>
      </div>
      <h3>{review.brazil.name}</h3>
      <p className="card-subtitle">
        {review.foreign.map((item) => item.name).join(" + ")}
      </p>
      <div className="card-bottom">
        <span>{review.foreign[0]?.university}</span>
        <span aria-hidden="true">↗</span>
      </div>
    </Link>
  );
}
export type Query = Record<string, string | string[] | undefined>;
export const queryValue = (query: Query, key: string) =>
  typeof query[key] === "string" ? (query[key] as string) : "";
export function CourseSelect({ value = "" }: { value?: string }) {
  return (
    <label>
      Curso
      <select name="curso" defaultValue={value}>
        <option value="">Todos os cursos</option>
        {getRepository().courses.map((course) => (
          <option key={course.id} value={course.id}>
            {course.name}
          </option>
        ))}
      </select>
    </label>
  );
}
export function Search({
  query = "",
  placeholder = "Nome ou código",
}: {
  query?: string;
  placeholder?: string;
}) {
  return (
    <label className="search-label">
      Buscar
      <input
        type="search"
        name="q"
        defaultValue={query}
        placeholder={placeholder}
      />
    </label>
  );
}
export function Pagination({
  total,
  page,
  query,
  size = 36,
  base,
}: {
  total: number;
  page: number;
  query: Query;
  size?: number;
  base: string;
}) {
  const pages = Math.ceil(total / size);
  if (pages < 2) return null;
  const href = (next: number) => {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (typeof value === "string" && value && key !== "pagina")
        params.set(key, value);
    });
    params.set("pagina", String(next));
    return `${base}?${params.toString()}`;
  };
  return (
    <nav className="pagination" aria-label="Paginação">
      {page > 1 ? <Link href={href(page - 1)}>← Anterior</Link> : <span />}
      <span>
        Página {page} de {pages} · {total} resultados
      </span>
      {page < pages ? <Link href={href(page + 1)}>Próxima →</Link> : <span />}
    </nav>
  );
}
export function pageNumber(query: Query, total: number, size = 36) {
  return Math.min(
    Math.max(1, Number.parseInt(queryValue(query, "pagina"), 10) || 1),
    Math.max(1, Math.ceil(total / size)),
  );
}
export function DisciplineLink({
  courseId,
  row,
}: {
  courseId: string;
  row: Parameters<typeof disciplinePath>[1];
}) {
  return (
    <Link href={disciplinePath(courseId, row)}>
      {row.name}
      <span className="arrow" aria-hidden="true">
        ↗
      </span>
    </Link>
  );
}
