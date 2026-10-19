import type { Discipline } from "./data";

export function parseStage(value: string): string {
  if (value === "nao-informada") return value;
  return /^(?:[1-9]|10)$/.test(value) ? value : "";
}

export function availableStages(
  rows: Pick<Discipline, "semester">[],
): number[] {
  return [
    ...new Set(rows.flatMap((row) => (row.semester ? [row.semester] : []))),
  ].sort((a, b) => a - b);
}

export function filterByStage<T extends { row: { semester?: number } }>(
  rows: T[],
  value: string,
): T[] {
  const stage = parseStage(value);
  if (!stage) return rows;
  return rows.filter(({ row }) =>
    stage === "nao-informada" ? !row.semester : row.semester === Number(stage),
  );
}
