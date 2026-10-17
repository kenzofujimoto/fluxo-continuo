import { z } from "zod";
import locations from "../data/university-locations.json";
import { normalize, type University } from "./data";

const locationSchema = z.object({
  lat: z.number().min(-90).max(90),
  lng: z.number().min(-180).max(180),
  city: z.string().min(1),
  precision: z.enum(["city", "campus"]),
  source: z.url().refine((value) => /^https?:\/\//.test(value)),
  verifiedAt: z.iso.date(),
  locationNote: z.string().optional(),
});
const locationsSchema = z
  .object({
    origin: locationSchema.extend({ name: z.string() }),
    universities: z.array(locationSchema.extend({ universityId: z.string() })),
  })
  .refine(
    (value) =>
      new Set(value.universities.map((item) => item.universityId)).size ===
      value.universities.length,
    "Duplicate university location",
  );
export const parseLocations = (value: unknown) => locationsSchema.parse(value);
export const universityLocations = parseLocations(locations);
export type Location = z.infer<typeof locationSchema>;
export type Destination = {
  id: string;
  name: string;
  country: string;
  flag: string;
  courses: Record<string, boolean>;
  catalogCount: number;
  location?: Location;
};

export function filterDestinations<
  T extends Pick<University, "name" | "country" | "courses">,
>(
  universities: T[],
  filters: { q?: string; course?: string; eligible?: boolean },
) {
  return universities.filter(
    (university) =>
      normalize(`${university.name} ${university.country}`).includes(
        normalize(filters.q ?? ""),
      ) &&
      (!filters.eligible ||
        (filters.course
          ? university.courses[filters.course]
          : Object.values(university.courses).some(Boolean))),
  );
}
