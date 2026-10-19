import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { comparisonId, disciplineKey, getRepository } from "../lib/data";
const require = createRequire(import.meta.url);
require.extensions[".css"] = (module) => {
  module.exports = {};
};

test("filtered page metadata names valid courses and ignores invalid filters", async () => {
  const modules = [
    [await import("../app/disciplinas/page"), "Disciplinas"],
    [await import("../app/ementas/page"), "Biblioteca de ementas"],
    [await import("../app/comparacoes/page"), "Comparar ementas"],
    [await import("../app/idiomas/page"), "Idiomas e requisitos"],
    [await import("../app/universidades/page"), "Explore destinos"],
  ] as const;
  const course = getRepository().courses[0];
  for (const [page, title] of modules) {
    assert.equal(
      (
        await page.generateMetadata({
          searchParams: Promise.resolve({ curso: course.id }),
        })
      ).title,
      `${title} · ${course.name}`,
    );
    for (const curso of [
      "invalid",
      "%E0%A4%A",
      [course.id, "invalid"],
      undefined,
    ]) {
      assert.equal(
        (
          await page.generateMetadata({
            searchParams: Promise.resolve({ curso }),
          })
        ).title,
        title,
      );
    }
  }
});

test("planner metadata matches its default and selected course", async () => {
  const { generateMetadata } = await import("../app/plano/page");
  const courses = getRepository().courses;
  for (const curso of [courses[1].id, "invalid", undefined, [courses[1].id]]) {
    const course = courses.find((item) => item.id === curso) ?? courses[0];
    assert.equal(
      (await generateMetadata({ searchParams: Promise.resolve({ curso }) }))
        .title,
      `Meu plano de estudos · ${course.name}`,
    );
  }
});

test("detail metadata uses the resolved entity and safely rejects unknown routes", async () => {
  const universityPage = await import("../app/universidades/[id]/page");
  const disciplinePage =
    await import("../app/disciplinas/[course]/[code]/page");
  const comparisonPage = await import("../app/comparacoes/[id]/page");
  const repository = getRepository();
  const university = repository.universities[0];
  assert.equal(
    (
      await universityPage.generateMetadata({
        params: Promise.resolve({ id: university.id }),
      })
    ).title,
    university.name,
  );
  const course = repository.courses[0];
  const row = course.rows.find((item) => !item.id) ?? course.rows[0];
  for (const code of [
    disciplineKey(row),
    encodeURIComponent(disciplineKey(row)),
  ]) {
    assert.equal(
      (
        await disciplinePage.generateMetadata({
          params: Promise.resolve({ course: course.id, code }),
        })
      ).title,
      `${row.name} · ${course.name}`,
    );
  }
  const review = repository.reviews[0];
  assert.equal(
    (
      await comparisonPage.generateMetadata({
        params: Promise.resolve({ id: comparisonId(review.id) }),
      })
    ).title,
    `${review.brazil.name} · ${review.foreign[0].university}`,
  );
  for (const id of ["invalid", "%E0%A4%A"]) {
    await assert.rejects(
      universityPage.generateMetadata({ params: Promise.resolve({ id }) }),
      /NEXT_HTTP_ERROR_FALLBACK;404/,
    );
    await assert.rejects(
      comparisonPage.generateMetadata({ params: Promise.resolve({ id }) }),
      /NEXT_HTTP_ERROR_FALLBACK;404/,
    );
    await assert.rejects(
      disciplinePage.generateMetadata({
        params: Promise.resolve({ course: course.id, code: id }),
      }),
      /NEXT_HTTP_ERROR_FALLBACK;404/,
    );
  }
});
