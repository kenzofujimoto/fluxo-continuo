import type { Metadata } from "next";
import { getRepository } from "../../lib/data";
import { CourseEntry } from "./course-entry";

export const metadata: Metadata = {
  title: "Seu curso, seu próximo destino",
  robots: { index: false, follow: false },
};

export default function HomePreview() {
  return (
    <CourseEntry
      courses={getRepository().courses.map(({ id, name, rows }) => ({
        id,
        name,
        stages: [
          ...new Set(
            rows.flatMap((row) => (row.semester ? [row.semester] : [])),
          ),
        ].sort((a, b) => a - b),
      }))}
    />
  );
}
