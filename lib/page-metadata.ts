import type { Metadata } from "next";
import { getRepository } from "./data";

type PageQuery = Record<string, string | string[] | undefined>;

export function filteredPageMetadata(
  title: string,
  query: PageQuery,
): Metadata {
  const course = getRepository().courses.find(
    (item) => item.id === query.curso,
  );
  return { title: course ? `${title} · ${course.name}` : title };
}
