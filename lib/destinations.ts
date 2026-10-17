import { getRepository } from "./data";
import { universityLocations, type Destination } from "./locations";
export function getDestinations(): Destination[] {
  const repository = getRepository();
  return repository.universities.map((university) => ({
    id: university.id,
    name: university.name,
    country: university.country,
    flag: university.flag,
    courses: university.courses,
    catalogCount: repository.foreignCourses.filter(
      (course) => course.universityId === university.id,
    ).length,
    location: universityLocations.universities.find(
      (location) => location.universityId === university.id,
    ),
  }));
}
