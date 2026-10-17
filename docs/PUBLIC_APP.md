# Public research application

## Scope

Next.js App Router + React Server Components + strict TypeScript. Public, read-only browsing. No database, admin area, authentication, external API, or new credentials. The approved decision to defer Neon keeps publishing and review in Git.

The visual system follows the local MackJr reference: warm ink `#15110e`, paper `#f1ece3`, signal red `#e63322`, phosphor `#c8fa3d`; genuine Space Grotesk, DM Serif Display, and JetBrains Mono fonts are bundled locally via Fontsource. Tailwind v4 is configured; shared component styling and responsive rules live in `app/globals.css`. Fonts do not call Google at runtime or build time.

## Data flow

`lib/data.ts` is the typed, Zod-validated access boundary. It statically imports only:

- `data.json`: degrees, curriculum rows, universities, foreign course catalogue, candidate relations.
- `syllabi/programas.json`: Brazilian programme text, provenance, hashes, currency.
- `syllabi/records.json`: foreign document classifications and hashes.
- `syllabi/pareceres-index.json`: published review content and exact topic evidence.
- `syllabi/pendencias-documentais.json`: pending Brazilian/foreign documents and COI questions.

No arbitrary filesystem reads, cache directories, downloaded documents, or internal repository files are served. Malformed consumed fields fail validation visibly. React escapes text; source hyperlinks allow only HTTP/HTTPS. Empty curriculum IDs fall back to discipline names, scoped by degree. Review routes use reversible base64url identifiers for exact lookup, not inferred equivalences.

Counts are calculated from the consumed records. A count of individual foreign syllabi uses `records.foreign[].status === ementa_individual`; priority missing syllabi and blocked crossings use the pending inventory. These have different denominators. Zero homologations is computed from review institutional statuses.

Search forms use GET, preserving state in shareable URLs. Accents are normalized in the main searches. Catalogue and syllabus lists paginate at 36 items. Missing detail records return 404; read errors present a retry state. All browsing works without client-side JavaScript. Next.js enhances internal navigation when JavaScript is enabled.

## Publish an update

1. Update the versioned datasets using the existing research workflow.
2. Review documentary evidence, curriculum linkage, current year, and contact-hour basis. Do not derive contact hours from ECTS.
3. Run `npm test`, `npm run lint`, `npm run build`, `python -X utf8 -m pytest -q tests`, and `node validate.js`.
4. Commit the research changes and deploy the Next.js application. Static pages rebuild alongside server bundles; all imported data changes require a new build/deploy.

Historic HTML files are retained as sources, but Next.js redirects their public URLs to current routes. Hosting must detect Next.js; a static HTML deployment will still serve the historical application. No deploy was performed in this implementation.

## Remaining research work

The public `/pendencias` route reports current counts and details. Reliable comparisons require:

- Complete official programmes on both sides, with topical evidence and document identity.
- Confirmation of Brazilian curriculum, campus, and currency; historical Direito and undated Administração documents need particular attention.
- Foreign contact hours, hour duration, semester basis, academic year, and course level. ECTS stays separate.
- Actual 2027.2 offering, teaching language, prerequisites, and exchange-student enrolment access.
- Independent second reviews where flagged and institutional decisions by coordination/COI.

This release displays existing reviewed comparisons. It does not create new academic judgments or accept public submissions. Candidate title matches remain preliminary; missing analysis does not imply incompatibility. A future Neon adapter can replace this repository boundary when collaborative editing or frequent publication makes database persistence useful.

## Validation and dependency audit

Seven contract tests cover derived counts, degree-scoped identities (including empty source IDs), all candidate links, accent-insensitive searches, safely decoded route names, exact comparison evidence/hour uncertainty, invalid schema rejection, and unsafe source protocols. Existing Python and Node validation remains intact. Tests were first committed red in `db680a3`; the encoded-route regression was committed red in `8364632` and fixed in `b0d41b5`. Independent HTTP checks verified actual rendered discipline headings, comparison evidence, filters, redirects, empty results, and not-found states. Automated visual browser review was unavailable in this session.

`npm audit --omit=dev` reports zero vulnerabilities at implementation time. The full audit reports five high findings along the development-only `eslint-config-next → fast-glob → micromatch → braces` chain (GHSA-vfj7-8cjw-p6xm). npm suggests an incompatible Next ESLint downgrade rather than a supported patched dependency; no forced downgrade was applied. Recheck the advisory and upgrade when supported fixes ship. This chain is not included in the production dependency installation.
