import { getRepository } from "../../lib/data";
import Link from "next/link";
import { getDestinations } from "../../lib/destinations";
import { filterDestinations, universityLocations } from "../../lib/locations";
import { DestinationGlobe } from "../destination-globe";
import { queryValue, type Query } from "../ui";
export const metadata = { title: "Explore destinos" };
export default async function Universities({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const query = await searchParams;
  const course = queryValue(query, "curso");
  const eligible = queryValue(query, "elegiveis") === "1";
  const results = filterDestinations(getDestinations(), {
    q: queryValue(query, "q"),
    course,
    eligible,
  });
  return (
    <div className="destinations-page">
      <header className="destination-heading">
        <p className="eyebrow">02 / Novas coordenadas</p>
        <h1>
          Encontre seu próximo <em>destino.</em>
        </h1>
        <p>
          Explore universidades pelo mundo e encontre novas formas de aprender.
        </p>
      </header>
      <div className="destination-layout">
        <aside className="destination-sidebar">
          <form className="destination-filters">
            <label>
              Seu curso
              <select name="curso" defaultValue={course}>
                <option value="">Todos os cursos</option>
                {getRepository().courses.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              País ou universidade
              <input
                name="q"
                defaultValue={queryValue(query, "q")}
                placeholder="Qual é sua próxima parada?"
                type="search"
              />
            </label>
            <label className="eligibility-toggle">
              <input
                type="checkbox"
                name="elegiveis"
                value="1"
                defaultChecked={eligible}
              />
              <span>
                Somente elegíveis
                {course ? " para meu curso" : " em algum curso"}
              </span>
            </label>
            <button className="button dark">Explorar destinos ↗</button>
            <Link className="text-link" href="/universidades">
              Limpar filtros
            </Link>
          </form>
          <p className="sidebar-note">
            A elegibilidade vem da planilha COI. Vagas, matrícula e oferta de
            disciplinas precisam de confirmação.
          </p>
          <p className="sidebar-note">
            Os pontos indicam campi ou cidades de referência. Confira a precisão
            e a fonte ao selecionar um destino.
          </p>
        </aside>
        <DestinationGlobe
          destinations={results}
          origin={universityLocations.origin}
        />
      </div>
    </div>
  );
}
