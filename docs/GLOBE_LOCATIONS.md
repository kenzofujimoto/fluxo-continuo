# Globe location provenance

Verified on 2026-10-16. Coordinates are public geographic reference points, not confirmation of exchange campus, course availability, enrollment eligibility, or curricular equivalence.

## Method

- 57 of 66 institutions have sourced points. Unmapped institutions remain available in the university list.
- Institutional points use Wikidata P625 after resolving the institution identity (including country). Coordinate precision of 0.01 degrees or coarser is labeled `city`.
- `campus` denotes a sourced institutional reference point. It does not identify every campus of a multicampus university. The UI should call it an institutional point.
- When no institutional coordinate exists, a city point is used only when Wikidata P131 links the institution to that city. Its source is the city entity; locationNote links the institutional entity.
- The origin uses camera GPS metadata from a public photograph explicitly depicting Mackenzie Alphaville. This is approximate and does not claim a surveyed entrance coordinate. Its institutional address is corroborated by the official Mackenzie page linked in locationNote.
- Wikidata structured data is CC0. The photograph is not copied or distributed by this feature. Only its public GPS metadata is referenced.
- No online geocoding runs in the client; coordinates are versioned locally.

## Pending coordinates

These institutions have no point in this version. A source identifying the relevant campus and coordinate is still needed; no point was inferred from country or institution name.

- `co-16-corporaciontec`: Corporación Tecnológica de Bogotá
- `fr-38-lecolededesign`: L'Ecole de Design Nantes Atlantique
- `fr-37-ecoledarchitec`: École d'architecture de Paris Val-de-Seine
- `ho-40-viaachristianu`: Viaa - Christian University of Applied Sciences
- `it-44-florenceuniver`: Florence University of Arts
- `me-52-universidadalf`: Universidad Alfa y Omega
- `pt-iade`: IADE
- `pt-estg`: P.PORTO / ESTG
- `uy-udelar`: Universidad de la República

## Retrieved institution entity revisions

Institution identities and P625/P131 claims were inspected through Wikidata Special:EntityData JSON. Official sites listed below are the P856 values recorded by Wikidata, not an independent verification of the campus offering.

| Institution ID | Entity / revision | Official URL recorded in P856 |
| --- | --- | --- |
| al-3-bauhausunivers | [Q573975](https://www.wikidata.org/w/index.php?title=Q573975&oldid=2556966957) | http://www.uni-weimar.de/ |
| al-4-leibnizunivers | [Q678982](https://www.wikidata.org/w/index.php?title=Q678982&oldid=2556927719) | https://www.uni-hannover.de/, https://www.uni-hannover.de/en/ |
| ar-6-universidadcat | [Q1736398](https://www.wikidata.org/w/index.php?title=Q1736398&oldid=2537174246) | http://www.uccor.edu.ar/ |
| ar-7-universidaddec | [Q6156753](https://www.wikidata.org/w/index.php?title=Q6156753&oldid=2511576262) | http://www.ucongreso.edu.ar/ |
| ar-cordoba | [Q1570489](https://www.wikidata.org/w/index.php?title=Q1570489&oldid=2537178157) | https://www.unc.edu.ar/ |
| bo-ueb | [Q30294038](https://www.wikidata.org/w/index.php?title=Q30294038&oldid=2474479301) |  |
| bo-12-universidadpri | [Q30293988](https://www.wikidata.org/w/index.php?title=Q30293988&oldid=2511437252) |  |
| be-9-hasseltunivers | [Q1781858](https://www.wikidata.org/w/index.php?title=Q1781858&oldid=2553175521) | http://www.uhasselt.be/ |
| be-10-kuleuven | [Q833670](https://www.wikidata.org/w/index.php?title=Q833670&oldid=2554942347) | https://www.kuleuven.be/, https://www.kuleuven.be/english/ |
| co-23-konkukuniversi | [Q41765](https://www.wikidata.org/w/index.php?title=Q41765&oldid=2550000305) | https://konkuk.ac.kr |
| co-22-kyungpooknatio | [Q487841](https://www.wikidata.org/w/index.php?title=Q487841&oldid=2519264777) | http://www.knu.ac.kr/ |
| co-24-solbridgeinter | [Q16979171](https://www.wikidata.org/w/index.php?title=Q16979171&oldid=2539969643) | http://www.solbridge.ac.kr |
| co-25-soongsiluniver | [Q489331](https://www.wikidata.org/w/index.php?title=Q489331&oldid=2516574771) | https://ssu.ac.kr/, https://ssu.ac.kr/ssu-service/#ssu_foreigner |
| es-cadiz | [Q2000065](https://www.wikidata.org/w/index.php?title=Q2000065&oldid=2536551371) | https://www.uca.es, https://www.uca.es/?lang=en |
| es-26-universidaddej | [Q573144](https://www.wikidata.org/w/index.php?title=Q573144&oldid=2535215483) | https://www.ujaen.es |
| es-salamanca | [Q308963](https://www.wikidata.org/w/index.php?title=Q308963&oldid=2538098161) | https://www.usal.es/ |
| es-29-universitataut | [Q43452](https://www.wikidata.org/w/index.php?title=Q43452&oldid=2541412001) | https://www.uab.cat |
| eu-35-dukeuniversity | [Q168751](https://www.wikidata.org/w/index.php?title=Q168751&oldid=2540544623) | https://duke.edu |
| eu-31-northeasternil | [Q2000943](https://www.wikidata.org/w/index.php?title=Q2000943&oldid=2553932625) | http://www.neiu.edu/ |
| po-61-universidadeca | [Q970751](https://www.wikidata.org/w/index.php?title=Q970751&oldid=2550097133) | https://www.ucp.pt |
| pt-ubi | [Q846725](https://www.wikidata.org/w/index.php?title=Q846725&oldid=2550089712) | http://www.ubi.pt |
| pt-coimbra | [Q368643](https://www.wikidata.org/w/index.php?title=Q368643&oldid=2549611312) | https://www.uc.pt/ |
| po-56-universidadede | [Q1122926](https://www.wikidata.org/w/index.php?title=Q1122926&oldid=2522730879) | https://www.ulisboa.pt/ |
| pt-utad | [Q3309132](https://www.wikidata.org/w/index.php?title=Q3309132&oldid=2549991588) | https://www.utad.pt/, https://www.utad.pt/en/ |
| pt-porto | [Q1422903](https://www.wikidata.org/w/index.php?title=Q1422903&oldid=2534559816) | http://www.up.pt |
| po-63-universidadelu | [Q635878](https://www.wikidata.org/w/index.php?title=Q635878&oldid=2511008477) | http://www.ulusiada.pt/ |
| po-57-universidadeno | [Q1979891](https://www.wikidata.org/w/index.php?title=Q1979891&oldid=2534554545) | https://www.unl.pt/ |
| ro-babes | [Q538452](https://www.wikidata.org/w/index.php?title=Q538452&oldid=2555614519) | https://www.ubbcluj.ro/ro/ |
| ch-13-universidaddec | [Q232141](https://www.wikidata.org/w/index.php?title=Q232141&oldid=2533816923) | https://www.uchile.cl/, https://www.uchile.cl/english, https://uchile.cl/ |
| ch-15-universidaddie | [Q1316229](https://www.wikidata.org/w/index.php?title=Q1316229&oldid=2511616693) | https://www.udp.cl/ |
| ch-14-universidadfin | [Q1812621](https://www.wikidata.org/w/index.php?title=Q1812621&oldid=2557772283) | https://finis.cl/ |
| co-17-universidaddel | [Q1569421](https://www.wikidata.org/w/index.php?title=Q1569421&oldid=2533826104) | https://uniandes.edu.co/ |
| co-18-universidaddem | [Q6156785](https://www.wikidata.org/w/index.php?title=Q6156785&oldid=2516559072) | https://udemedellin.edu.co |
| co-rosario | [Q3997334](https://www.wikidata.org/w/index.php?title=Q3997334&oldid=2555574659) | http://www.urosario.edu.co/ |
| co-20-universidadlag | [Q6156504](https://www.wikidata.org/w/index.php?title=Q6156504&oldid=2511242790) | https://www.ugc.edu.co |
| kr-chung | [Q41790](https://www.wikidata.org/w/index.php?title=Q41790&oldid=2511573075) | https://www.cau.ac.kr/, https://neweng.cau.ac.kr/, https://newchn.cau.ac.kr/ |
| us-pittsburg | [Q2097334](https://www.wikidata.org/w/index.php?title=Q2097334&oldid=2549970671) | http://www.pittstate.edu |
| eu-33-theohiostateun | [Q309331](https://www.wikidata.org/w/index.php?title=Q309331&oldid=2531555681) | https://osu.edu |
| eu-32-universityofte | [Q1230739](https://www.wikidata.org/w/index.php?title=Q1230739&oldid=2540133503) | http://www.uta.edu |
| eu-34-wrightstateuni | [Q2002085](https://www.wikidata.org/w/index.php?title=Q2002085&oldid=2540584014) | http://www.wright.edu |
| fr-39-isginternation | [Q1659456](https://www.wikidata.org/w/index.php?title=Q1659456&oldid=2520548696) | http://www.isg.fr |
| fr-36-ecolenationale | [Q1050988](https://www.wikidata.org/w/index.php?title=Q1050988&oldid=2549837798) | http://www.versailles.archi.fr |
| gb-leeds | [Q503424](https://www.wikidata.org/w/index.php?title=Q503424&oldid=2526244213) | https://leeds.ac.uk/, http://www.leeds.ac.uk |
| ie-setu | [Q55670387](https://www.wikidata.org/w/index.php?title=Q55670387&oldid=2557335055) | https://www.tuse.ie, https://www.setu.ie |
| it-49-almamaterstudi | [Q131262](https://www.wikidata.org/w/index.php?title=Q131262&oldid=2557007333) | https://www.unibo.it |
| it-51-politecnicodim | [Q392904](https://www.wikidata.org/w/index.php?title=Q392904&oldid=2534562296) | https://www.polimi.it |
| it-46-universitadegl | [Q955609](https://www.wikidata.org/w/index.php?title=Q955609&oldid=2548638306) | http://www.unife.it |
| it-50-universitadegl | [Q820887](https://www.wikidata.org/w/index.php?title=Q820887&oldid=2524618812) | https://www.unifi.it/ |
| it-45-universitadegl | [Q2261128](https://www.wikidata.org/w/index.php?title=Q2261128&oldid=2522925509) | https://www.unich.it |
| it-47-universitadegl | [Q1031803](https://www.wikidata.org/w/index.php?title=Q1031803&oldid=2535532939) | https://web.uniroma2.it/it |
| it-48-universitadegl | [Q1633215](https://www.wikidata.org/w/index.php?title=Q1633215&oldid=2556174356) | https://www.unisa.it |
| po-54-institutopolit | [Q7227029](https://www.wikidata.org/w/index.php?title=Q7227029&oldid=2553491207) | https://www.ipcb.pt |
| po-55-institutopolit | [Q2103165](https://www.wikidata.org/w/index.php?title=Q2103165&oldid=2542285291) | http://internationalrelations.ipc.pt/EN/index.html |
| tu-66-istanbulaydnun | [Q6088582](https://www.wikidata.org/w/index.php?title=Q6088582&oldid=2511575238) | http://www.aydin.edu.tr |
| tu-67-nevsehirhacbek | [Q6059990](https://www.wikidata.org/w/index.php?title=Q6059990&oldid=2553846147) | http://www.nevsehir.edu.tr |
| at-graz | [Q689775](https://www.wikidata.org/w/index.php?title=Q689775&oldid=2556053012) | https://www.tugraz.at/, https://www.tugraz.at/en/home/ |
| in-41-bmlmunjalunive | [Q18355854](https://www.wikidata.org/w/index.php?title=Q18355854&oldid=2553975077) | https://www.bmu.edu.in |
