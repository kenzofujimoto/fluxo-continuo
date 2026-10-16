/* Fluxo Contínuo — public, read-only, dependency-free academic matrix. */
'use strict';
const $ = selector => document.querySelector(selector);
const els = {
  tabs: $('#courseTabs'), search: $('#search'), semester: $('#semester'),
  university: $('#university'), status: $('#status'), only: $('#onlyMatched'), all: $('#allUniversities'),
  head: $('#matrixHead'), body: $('#matrixBody'), overlay: $('#overlay'),
  detail: $('#detailBody'), detailTitle: $('#detailTitle')
};
let database;
let titleSuggestionIndex = new Map();
let foreignIndex = new Map();
let currentCourse = 'cc';
let activeElementBeforeDrawer = null;
const state = { search: '', semester: 'all', university: 'all', status: 'all', only: false, all: false };
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function safeUrl(value) {
  try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) ? url.href : ''; } catch {return '';}
}
function current() { return database.courses.find(course => course.id === currentCourse); }
function matchesFor(subject, universityId) {
  const normalized = subject.name.toLocaleLowerCase('pt-BR');
  const rank={candidata_forte:0,em_analise:1,indicio_titulo:2};
  return database.matches.filter(item=>item.courseId===currentCourse&&item.universityId===universityId&&
    ((subject.id && subject.id===item.mackCode)||(!subject.id&&normalized===String(item.mackName||'').toLocaleLowerCase('pt-BR'))))
    .sort((a,b)=>(rank[a.status]??9)-(rank[b.status]??9));
}
function matchFor(subject,universityId){return matchesFor(subject,universityId)[0]||null;}
function foreignFor(item) {
  return item ? database.foreignCourses.find(course => course.universityId === item.universityId && course.code === item.foreignCode) : null;
}
function extraFor(subject, universityId) {
  const rowIndex = current().rows.indexOf(subject);
  const uniIndex = database.universities.findIndex(u => u.id === universityId);
  if (rowIndex < 0 || uniIndex < 0) return [];
  return (titleSuggestionIndex.get(currentCourse+'|'+rowIndex+'|'+uniIndex) || []).map(([code,score])=>({foreign:foreignIndex.get(universityId+'|'+code),score})).filter(item=>item.foreign);
}
function matchingRows() {
  const term = state.search.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const universities = visibleUniversities();
  return current().rows.filter(row => {
    if (term && ![row.name, row.id, row.abstract].some(value => String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(term))) return false;
    if (state.semester !== 'all' && String(row.semester) !== state.semester) return false;
    const related = universities.flatMap(u => matchesFor(row,u.id));
    if (state.status === 'candidata_forte' && !related.some(m => m.status === 'candidata_forte')) return false;
    if (state.status === 'em_analise' && !related.some(m => m.status === 'em_analise')) return false;
    if (state.status === 'indicio_titulo' && !related.some(m=>m.status==='indicio_titulo') && !universities.some(u=>extraFor(row,u.id).length)) return false;
    if (state.status === 'sem_dados' && related.length) return false;
    if (state.only && !related.length && !universities.some(u=>extraFor(row,u.id).length)) return false;
    return true;
  });
}
function eligibleUniversities() {return database.universities.filter(u => u.courses?.[currentCourse] === true);}
function visibleUniversities() {return database.universities.filter(item => (state.all || item.courses?.[currentCourse] === true) && (state.university === 'all' || state.university === item.id));}
function renderTabs() {
  els.tabs.innerHTML = database.courses.map(course => `<button class="course-tab" role="tab" type="button" data-course="${esc(course.id)}" aria-selected="${course.id===currentCourse}">${esc(course.name)}</button>`).join('');
  els.tabs.querySelectorAll('[data-course]').forEach(button => button.addEventListener('click', () => {
    currentCourse = button.dataset.course; state.search=''; state.semester='all'; state.university='all'; state.status='all'; state.only=false;
    els.search.value=''; els.only.checked=false; els.status.value='all';
    renderTabs(); renderFilters(); renderMatrix();
  }));
}
function renderFilters() {
  const c = current();
  const semesters = [...new Set(c.rows.map(r=>r.semester))].sort((a,b)=>a-b);
  els.semester.innerHTML = `<option value="all">Todas as etapas</option>${semesters.map(s=>`<option value="${s}">${s}ª etapa</option>`).join('')}`;
  const eligible = state.all ? database.universities : eligibleUniversities();
  els.university.innerHTML = `<option value="all">Todas as universidades (${eligible.length})</option>${eligible.map(u=>`<option value="${esc(u.id)}">${esc(u.name)} (${esc(u.country)})</option>`).join('')}`;
  els.semester.value = state.semester; els.university.value = state.university;
  $('#sourceSheet').href = safeUrl(database.meta.availabilitySource);
}
function renderMatrix() {
  const c = current(); const unis=visibleUniversities(); const rows=matchingRows();
  $('#matrixTitle').textContent=c.name;
  $('#matrixDescription').textContent=`${c.matrix} · ${c.rows.length} disciplinas catalogadas · instituições marcadas Sim para ${c.name} pela COI`; 
  $('#countSubjects').textContent=String(c.rows.length);
  $('#countUniversities').textContent=String(unis.length);
  const available = database.matches.filter(m=>m.courseId===currentCourse && unis.some(u=>u.id===m.universityId));
  $('#countMatches').textContent=String(available.filter(m=>m.status!=='indicio_titulo').length);
  $('#countEvidence').textContent=String(available.filter(m=>m.status==='indicio_titulo').length);
  $('#rowCount').textContent=`Exibindo ${rows.length} de ${c.rows.length} disciplinas`;
  els.head.innerHTML=`<tr><th class="fixedcol"><div class="fixed-content">COMPONENTE CURRICULAR MACKENZIE</div></th><th class="semester-cell">ETAPA</th>${unis.map(u=>`<th class="foreign-cell" scope="col"><span class="uni-flag">${flag(u.flag)}</span><span class="uni-name">${esc(u.name)}</span><div class="uni-country">${esc(u.country)} · ${u.courses?.[currentCourse] ? 'COI: Sim' : 'COI: não consta Sim'}</div></th>`).join('')}</tr>`;
  els.body.innerHTML=rows.length ? rows.map((row,r)=> `<tr><td class="fixedcol"><div class="fixed-content"><span class="subj-title">${esc(row.name)}</span><span class="subj-code">${esc(row.id || 'Código não cadastrado')}</span></div></td><td class="semester-cell"><span class="term">${row.semester}ª</span></td>${unis.map((u,i)=>{
    const options=matchesFor(row,u.id);const m=options[0];const f=foreignFor(m);
    if(m) return `<td class="foreign-cell"><button class="cell-button ${m.status==='indicio_titulo'?'suggested':m.status==='candidata_forte'?'strong':'pending'}" type="button" data-r="${r}" data-u="${i}" aria-label="Abrir proposta ${esc(f?.name||m.foreignCode)} para ${esc(row.name)} em ${esc(u.name)}"><span class="match-code">${esc(f?.originalCode?f.originalCode+' ↗':f?.officialCodeKnown===false?'Catálogo ↗':m.foreignCode+' ↗')}</span><span class="cell-tag">${esc(f?.name||'Candidata em análise')}${options.length>1?' · +'+(options.length-1)+' alternativa(s)':''}</span></button></td>`;
    return `<td class="foreign-cell"><button class="cell-button empty" type="button" data-r="${r}" data-u="${i}" aria-label="Não verificada: ${esc(row.name)} e ${esc(u.name)}" title="Sem comparação documental cadastrada">—</button></td>`;
  }).join('')}</tr>`).join('') : `<tr><td class="loading" colspan="${unis.length+2}">Nenhuma disciplina corresponde aos filtros. Ajuste a etapa ou a busca.</td></tr>`;
  els.body.querySelectorAll('[data-r][data-u]').forEach(b=>b.addEventListener('click',()=>openDetail(rows[Number(b.dataset.r)],unis[Number(b.dataset.u)])));
}
function flag(code) {const map={RO:'🇷🇴',ES:'🇪🇸',GB:'🇬🇧',AT:'🇦🇹',PT:'🇵🇹',KR:'🇰🇷',IE:'🇮🇪',US:'🇺🇸',AR:'🇦🇷',UY:'🇺🇾',BO:'🇧🇴',CO:'🇨🇴'};return map[code]||'🌐';}
function link(label,url){let safe=safeUrl(url);return safe?`<a class="detail-link" href="${esc(safe)}" target="_blank" rel="noopener noreferrer"><span>${esc(label)}</span><span aria-hidden="true">↗</span></a>`:'';}
function openDetail(subject,uni) {
  activeElementBeforeDrawer = document.activeElement;
  const m=matchFor(subject,uni.id); const f=foreignFor(m);
  els.detailTitle.textContent=uni.name;
  const base=`<section class="detail-section"><div class="detail-label">DISCIPLINA DO MACKENZIE</div><div class="detail-course">${esc(subject.name)}</div><span class="detail-code">${esc(subject.id||'Sem código cadastrado')}</span><div class="detail-meta"><span>${subject.semester}ª etapa</span>${subject.hours?`<span>${Number(subject.hours).toLocaleString('pt-BR',{maximumFractionDigits:2})} horas</span>`:''}<span>${esc(current().name)}</span></div>${subject.abstract?`<p>${esc(subject.abstract)}</p>`:''}${link('Ementário Mackenzie',subject.syllabusUrl||current().source)}</section>`;
  const allOptions=matchesFor(subject,uni.id);
  const other=allOptions.length
    ? '<section class="detail-section"><h3>'+allOptions.length+' possibilidade'+(allOptions.length>1?'s':'')+' nesta universidade</h3><p>Correspondências e afinidades preliminares. Nenhuma está homologada.</p></section>'+
      allOptions.map((candidate,i)=>{
        const foreign=foreignFor(candidate);
        if(!foreign)return '';
        const state=candidate.status==='candidata_forte'?'Candidata forte':candidate.status==='em_analise'?'Em análise documental':'Afinidade por título (sem cotejo de ementas)';
        return '<section class="detail-section"><div class="detail-label">'+(i+1)+' · '+esc(state)+'</div>'+
         '<div class="detail-course">'+esc(foreign.name)+'</div>'+
         '<span class="detail-code">'+esc(foreign.originalCode?'Código no plano: '+foreign.originalCode+' · registro interno: '+foreign.code:foreign.officialCodeKnown===false?'Referência de catálogo (não código oficial): '+foreign.code:foreign.code)+'</span>'+
         '<div class="detail-meta">'+(foreign.contactHours!=null?'<span>'+esc(foreign.contactHours)+'h de contato</span>':'<span>Horas não comprovadas</span>')+
         (foreign.credits?'<span>'+esc(foreign.credits)+' '+esc(foreign.creditUnit||'créditos')+'</span>':'')+'<span>'+esc(foreign.period||'Oferta a confirmar')+'</span></div>'+
         link('Abrir disciplina / ementa oficial',foreign.source||candidate.source)+
         '<div class="callout"><b>'+esc(state)+' — não homologada</b><p>'+esc(candidate.evidence||'Comparação curricular pendente')+'</p></div>'+
         (foreign.topics?'<p><b>Conteúdo estrangeiro:</b> '+esc(foreign.topics)+'</p>':'')+
         (foreign.limitations?'<p><b>Limitações:</b> '+esc(foreign.limitations)+'</p>':'')+
         (foreign.assessment?'<p><b>Observações:</b> '+esc(foreign.assessment)+'</p>':'')+
         (foreign.prerequisites?'<p><b>Pré-requisitos:</b> '+esc(foreign.prerequisites)+'</p>':'')+
         '</section>';
      }).join('')
    : '<section class="detail-section"><h3>Nenhuma candidata catalogada</h3><div class="callout">O catálogo pode estar incompleto. A ausência de correspondência não demonstra incompatibilidade.</div></section>';
  const registeredCodes = new Set(allOptions.map(item=>item.foreignCode));
  const candidates = extraFor(subject,uni.id).filter(item=>!registeredCodes.has(item.foreign.code));
  const more = candidates.length ? '<section class="detail-section"><h3>'+candidates.length+' indício(s) adicionais de catálogo</h3><p>Somente semelhança lexical de títulos. Pontuação NÃO é percentual de equivalência.</p>'+
    candidates.map(item=>'<p><b>'+esc(item.foreign.name)+'</b> · '+esc(item.foreign.officialCodeKnown===false?'Código de referência (não oficial)':item.foreign.code)+' · afinidade lexical '+esc(item.score)+'/100</p>'+link('Fonte institucional',item.foreign.source)).join('')+'</section>' : '';
  const eligible=uni.courses?.[currentCourse]===true;
  const requirement=uni.language?.required||'Não informado ou campo inválido no XLSX';
  const eligibility=`<section class="detail-section"><h3>Elegibilidade & idioma</h3><div class="callout"><b>${eligible?'COI: curso assinalado Sim':'COI: curso sem marcação Sim'}</b><br/>A disponibilidade de matéria, vaga individual, idioma e período deve ser confirmada pela instituição.</div><p><b>Idioma informado:</b> ${esc(requirement)}</p><p><b>Certificado MLC:</b> ${uni.language?.mlcAccepted===true?'COI assinala Sim':uni.language?.mlcAccepted===false?'COI assinala Não':'Não informado'}</p>${link('Página de idiomas desta universidade',`./idiomas.html?universidade=${encodeURIComponent(uni.id)}`)}${link('Fonte da planilha COI',database.meta.availabilitySource)}${link('Site da universidade',uni.website)}${link('Catálogo estrangeiro',uni.catalogUrl)}<p>O estudo é preliminar. A coordenação do curso decide se o aproveitamento curricular será aceito.</p></section>`;
  els.detail.innerHTML=base+other+more+eligibility;
  els.overlay.hidden=false;
  document.body.style.overflow='hidden';
  $('#closeDetail').focus();
}
function closeDetail(){els.overlay.hidden=true;document.body.style.overflow='';if(activeElementBeforeDrawer?.focus)activeElementBeforeDrawer.focus();}
function safeCsv(value) {let s=String(value??''); if(/^[\s]*[=+@-]/.test(s))s="'"+s; return '"'+s.replace(/"/g,'""')+'"';}
function exportCsv() {
  const unis=visibleUniversities();
  const out=[['Etapa','Código Mackenzie','Disciplina Mackenzie',...unis.map(u=>u.name)]];
  matchingRows().forEach(row=>out.push([row.semester,row.id,row.name,...unis.map(u=>{
    const m=matchFor(row,u.id);const f=foreignFor(m);
    return m?`${m.foreignCode} — ${f?.name||''} — ${m.status} — ${f?.source||''}`:'NÃO VERIFICADO';
  })]));
  const csv='\ufeff'+out.map(row=>row.map(safeCsv).join(';')).join('\r\n');
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download=`fluxo-continuo_${currentCourse}_${database.meta.semester.replace('.','-')}.csv`;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function attach() {
  els.search.addEventListener('input',e=>{state.search=e.target.value;renderMatrix();});
  els.semester.addEventListener('change',e=>{state.semester=e.target.value;renderMatrix();});
  els.university.addEventListener('change',e=>{state.university=e.target.value;renderMatrix();});
  els.all.addEventListener('change',e=>{state.all=e.target.checked;state.university='all';renderFilters();renderMatrix();});
  els.status.addEventListener('change',e=>{state.status=e.target.value;renderMatrix();});
  els.only.addEventListener('change',e=>{state.only=e.target.checked;renderMatrix();});
  $('#resetFilters').addEventListener('click',()=>{state.search='';state.semester='all';state.university='all';state.status='all';state.only=false;state.all=false;els.search.value='';els.only.checked=false;els.all.checked=false;els.status.value='all';renderFilters();renderMatrix();});
  $('#exportCsv').addEventListener('click',exportCsv);
  $('#closeDetail').addEventListener('click',closeDetail);
  $('#backdrop').addEventListener('click',closeDetail);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!els.overlay.hidden)closeDetail();});
}
async function bootstrap() {
  try {
    const response = await fetch('./data.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('Erro ao carregar data.json: HTTP ' + response.status);
    database = await response.json();
    foreignIndex = new Map(database.foreignCourses.map(f=>[f.universityId+'|'+f.code,f]));
    try { const source = await fetch('./candidatos-catalogo.json'); if (source.ok) { const suggestions=await source.json(); titleSuggestionIndex=new Map(suggestions.pairs.map(p=>[p[0]+'|'+p[1]+'|'+p[2],p[3]])); } } catch(error) { console.warn('Índice complementar indisponível',error); }
    const covered = new Set(database.foreignCourses.filter(f=>f.universityId).map(f=>f.universityId)).size;
    const titleCandidates = database.matches.filter(m=>m.status==='indicio_titulo').length;
    document.getElementById('researchCoverage').textContent = covered + ' de ' + database.universities.length + ' universidades com pelo menos uma disciplina catalogada · ' + database.foreignCourses.length + ' disciplinas estrangeiras indexadas · ' + titleCandidates + ' indícios por título';

    if(!database?.courses?.length||!database?.universities?.length)throw new Error('Inconsistent database');
    renderTabs();renderFilters();attach();renderMatrix();
  } catch(e) {
    $('#matrixBody').innerHTML=`<tr><td class="loading">Não foi possível carregar a base local. Execute o app em um servidor HTTP (ex.: python -m http.server 8000). ${esc(e.message)}</td></tr>`;
  }
}
bootstrap();


