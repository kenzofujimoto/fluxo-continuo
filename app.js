/* MobiMatch Alpha — public, read-only, dependency-free academic matrix. */
'use strict';
const $ = selector => document.querySelector(selector);
const els = {
  tabs: $('#courseTabs'), search: $('#search'), semester: $('#semester'),
  university: $('#university'), status: $('#status'), only: $('#onlyMatched'), all: $('#allUniversities'),
  head: $('#matrixHead'), body: $('#matrixBody'), overlay: $('#overlay'),
  detail: $('#detailBody'), detailTitle: $('#detailTitle')
};
let database;
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
function matchFor(subject, universityId) {
  const normalized = subject.name.toLocaleLowerCase('pt-BR');
  return database.matches.find(item => item.courseId === currentCourse && item.universityId === universityId &&
    ((subject.id && subject.id === item.mackCode) || (!subject.id && normalized === item.mackName.toLocaleLowerCase('pt-BR'))));
}
function foreignFor(item) {
  return item ? database.foreignCourses.find(course => course.universityId === item.universityId && course.code === item.foreignCode) : null;
}
function matchingRows() {
  const term = state.search.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const universities = visibleUniversities();
  return current().rows.filter(row => {
    if (term && ![row.name, row.id, row.abstract].some(value => String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(term))) return false;
    if (state.semester !== 'all' && String(row.semester) !== state.semester) return false;
    const related = universities.map(u => matchFor(row,u.id)).filter(Boolean);
    if (state.status === 'candidata_forte' && !related.some(m => m.status === 'candidata_forte')) return false;
    if (state.status === 'em_analise' && !related.some(m => m.status === 'em_analise')) return false;
    if (state.status === 'indicio_titulo' && !related.some(m=>m.status==='indicio_titulo')) return false;
    if (state.status === 'sem_dados' && related.length) return false;
    if (state.only && !related.length) return false;
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
    const m=matchFor(row,u.id);const f=foreignFor(m);
    if(m) return `<td class="foreign-cell"><button class="cell-button ${m.status==='indicio_titulo'?'suggested':m.status==='candidata_forte'?'strong':'pending'}" type="button" data-r="${r}" data-u="${i}" aria-label="Abrir proposta ${esc(f?.name||m.foreignCode)} para ${esc(row.name)} em ${esc(u.name)}"><span class="match-code">${esc(f?.officialCodeKnown===false?'Catálogo ↗':m.foreignCode+' ↗')}</span><span class="cell-tag">${esc(f?.name||'Candidata em análise')}</span></button></td>`;
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
  const other= m && f ? `<section class="detail-section"><div class="detail-label">DISCIPLINA DA UNIVERSIDADE ESTRANGEIRA</div><div class="detail-course">${esc(f.name)}</div><span class="detail-code">${esc(f.officialCodeKnown===false?'Referência do catálogo (não é código oficial): '+f.code:f.code)}</span><div class="detail-meta">${f.contactHours!=null?`<span>${esc(f.contactHours)}h de contato</span>`:''}${f.credits?`<span>${esc(f.credits)} créditos</span>`:''}<span>${esc(f.period||'Semestre a verificar')}</span><span>${esc(f.degree||'Nível pendente')}</span></div>${link('Abrir programa / ementa estrangeira',f.source)}</section><section class="detail-section"><h3>Comparação documental</h3><div class="callout ${m.status==='candidata_forte'?'pink':''}"><b>${m.status==='indicio_titulo'?'Indício por título em catálogo oficial — NÃO É EQUIVALÊNCIA':m.status==='candidata_forte'?'Forte candidata — não homologada':'Em análise — não homologada'}</b><br/>${esc(m.evidence)}</div>${f.topics?`<p><b>Conteúdo estrangeiro:</b> ${esc(f.topics)}</p>`:''}${f.overlap?`<p><b>Sobreposição identificada:</b> ${esc(f.overlap)}</p>`:''}${f.novel?`<p><b>Conteúdo novo:</b> ${esc(f.novel)}</p>`:''}${f.limitations?`<p><b>Limitações:</b> ${esc(f.limitations)}</p>`:''}${f.assessment?`<p><b>Parecer técnico:</b> ${esc(f.assessment)}</p>`:''}${f.constraints?`<p><b>Oferta e matrícula:</b> ${esc(f.constraints)}</p>`:''}</section>` : `<section class="detail-section"><h3>Nenhuma equivalência documentada</h3><div class="callout">Não há comparação de ementas registrada para este cruzamento. Isso <b>não significa incompatibilidade</b>; significa ausência de evidência verificada.</div><p>Para cadastrar uma correspondência, precisamos de código, syllabus oficial, horas presenciais, semestre de oferta, idioma, pré-requisitos e análise com a disciplina brasileira.</p></section>`;
  const further=database.matches.filter(a=>a.courseId===currentCourse&&a.universityId===uni.id&&a!==m&&((subject.id&&a.mackCode===subject.id)||(!subject.id&&a.mackName.toLocaleLowerCase('pt-BR')===subject.name.toLocaleLowerCase('pt-BR'))));
  const more=further.length?'<section class="detail-section"><h3>Outras disciplinas a considerar nesta universidade</h3>'+further.map(x=>{const fx=foreignFor(x);return '<div class="callout"><b>'+esc(fx?.name||x.foreignCode)+'</b><p>'+esc(x.status==='indicio_titulo'?'Similaridade de título, ainda sem análise de conteúdo.':x.evidence)+'</p>'+link('Ver fonte oficial',fx?.source||x.source)+'</div>';}).join('')+'</section>':'';
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
  const a=document.createElement('a');a.href=url;a.download=`mobimatch_${currentCourse}_${database.meta.semester.replace('.','-')}.csv`;a.click();
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
    if(!database?.courses?.length||!database?.universities?.length)throw new Error('Inconsistent database');
    renderTabs();renderFilters();attach();renderMatrix();
  } catch(e) {
    $('#matrixBody').innerHTML=`<tr><td class="loading">Não foi possível carregar a base local. Execute o app em um servidor HTTP (ex.: python -m http.server 8000). ${esc(e.message)}</td></tr>`;
  }
}
bootstrap();


