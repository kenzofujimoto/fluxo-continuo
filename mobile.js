/* MobiMatch Alpha — exploração móvel independente da tabela desktop. */
'use strict';
(function () {
  const root = document.getElementById('mobileExplorer');
  const results = document.getElementById('mobileResults');
  const head = document.getElementById('matrixHead');
  if (!root || !results || !head) return;

  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const flags = {RO:'🇷🇴',ES:'🇪🇸',GB:'🇬🇧',AT:'🇦🇹',PT:'🇵🇹',KR:'🇰🇷',IE:'🇮🇪',US:'🇺🇸',AR:'🇦🇷',UY:'🇺🇾',BO:'🇧🇴',CO:'🇨🇴',FR:'🇫🇷',DE:'🇩🇪',BE:'🇧🇪',CL:'🇨🇱',MX:'🇲🇽',IT:'🇮🇹'};
  const states = {P:'Indício por nome',T:'Período a verificar',S:'Triagem parcial',C:'Catálogo pendente',F:'Documentos pendentes'};
  let catalog, registry, foreign, expanded = null, revealAll = false;
  const selected = () => document.querySelector('.course-tab[aria-selected="true"]')?.dataset.course || 'cc';

  function entries(courseId, subject, subjectIndex) {
    const filter = document.getElementById('university').value;
    const showAll = document.getElementById('allUniversities').checked;
    return catalog.universities.map((uni,ui) => {
      if ((!showAll && !uni.courses?.[courseId]) || (filter !== 'all' && filter !== uni.id)) return null;
      const m = catalog.matches.find(item => item.courseId === courseId && item.universityId === uni.id &&
        ((subject.id && item.mackCode === subject.id) || (!subject.id && normalize(item.mackName) === normalize(subject.name))));
      const triage = registry.get(courseId+'|'+subjectIndex+'|'+ui);
      const candidate = triage?.[4] && foreign.get(uni.id+'|'+triage[4][0]);
      const doc = m && foreign.get(uni.id+'|'+m.foreignCode);
      const rank = m ? (m.status === 'indicio_titulo' ? 2 : m.status === 'candidata_forte' ? 0 : 1) : (candidate ? 2 : 3);
      return {uni,ui,m,triage,candidate,doc,rank};
    }).filter(Boolean).sort((a,b) => a.rank-b.rank || a.uni.name.localeCompare(b.uni.name,'pt-BR'));
  }
  function universityCard(e,subjectIndex,courseId) {
    const title = e.doc?.name || e.candidate?.name || '';
    const code = e.doc?.officialCodeKnown===false ? 'Ref. catálogo' : e.m?.foreignCode || e.candidate?.code || '';
    const state = e.m ? (e.m.status === 'indicio_titulo' ? 'Afinidade no catálogo · falta comparar ementas' : e.rank===0 ? 'Candidata forte, não homologada' : 'Em análise documental') : (states[e.triage?.[3]] || 'Sem candidata documentada');
    const color = e.rank===0?'strong':e.rank===1?'pending':e.rank===2?'potential':'unknown';
    return '<button type="button" class="mobile-university '+color+'" data-mobile-university="'+e.ui+'" data-mobile-subject="'+subjectIndex+'" data-mobile-course="'+esc(courseId)+'" aria-label="Abrir '+esc(e.uni.name)+'">'+
      '<span class="mobile-university-main"><span class="mobile-flag">'+(flags[e.uni.flag]||'🌐')+'</span><span class="mobile-university-text"><strong>'+esc(e.uni.name)+'</strong><small>'+esc(e.uni.country)+' · '+esc(state)+'</small></span><span class="mobile-arrow" aria-hidden="true">›</span></span>'+
      (title ? '<span class="mobile-foreign-course"><b>'+esc(code)+'</b> '+esc(title)+'</span>' : '<span class="mobile-undocumented">Sem correspondência documental cadastrada</span>')+'</button>';
  }
  function content(courseId,subjectIndex,es) {
    const useful=es.filter(e=>e.rank<3),remaining=es.filter(e=>e.rank===3);
    const showing=revealAll ? useful.concat(remaining) : useful;
    let html='<div class="mobile-entry-panel"><div class="mobile-entry-summary"><b>'+es.length+'</b> universidades elegíveis · <b>'+es.filter(e=>e.m&&e.m.status!=='indicio_titulo').length+'</b> pré-análises documentais · <b>'+es.filter(e=>e.rank===2).length+'</b> indícios em catálogos</div>';
    html+=showing.length ? showing.map(e=>universityCard(e,subjectIndex,courseId)).join('') : '<p class="mobile-no-matches">Nenhuma candidata identificada nos catálogos pesquisados. Isso não significa incompatibilidade.</p>';
    if(remaining.length) html+='<button type="button" class="mobile-show-more" data-mobile-more="true">'+(revealAll?'Ocultar universidades sem candidata ↑':'Ver outras '+remaining.length+' universidades sem candidata verificada ↓')+'</button>';
    return html+'<p class="mobile-disclaimer">Indícios automáticos não são equivalências. A homologação depende de ementas, carga horária, oferta e coordenação.</p></div>';
  }
  function render() {
    if(!catalog || !registry || !head.querySelector('th')) return;
    const courseId=selected(),course=catalog.courses.find(c=>c.id===courseId);
    if(!course) return;
    const search=normalize(document.getElementById('search').value.trim());
    const stage=document.getElementById('semester').value;
    const status=document.getElementById('status').value;
    const only=document.getElementById('onlyMatched').checked;
    const rows=course.rows.map((s,i)=>({s,i,es:entries(courseId,s,i)})).filter(({s,es})=>{
      if(stage!=='all' && String(s.semester)!==stage) return false;
      if(search && ![s.name,s.id,s.abstract].some(v=>normalize(v).includes(search))) return false;
      const matches=es.filter(e=>e.m&&e.m.status!=='indicio_titulo');
      if(only && !matches.length) return false;
      if(status==='candidata_forte' && !matches.some(e=>e.m.status==='candidata_forte')) return false;
      if(status==='em_analise' && !matches.some(e=>e.m.status==='em_analise')) return false;
      if(status==='indicio_titulo' && !es.some(e=>e.rank===2)) return false;
      if(status==='sem_dados' && matches.length===es.length) return false;
      return true;
    });
    if(rows.length===1 && !expanded) expanded=courseId+'|'+rows[0].i;
    results.innerHTML='<div class="mobile-results-count"><span>'+rows.length+' de '+course.rows.length+' disciplinas</span><span>Toque para expandir ↓</span></div>'+
      (rows.length ? rows.map(({s,i,es})=>{
        const opened=expanded===courseId+'|'+i,docs=es.filter(e=>e.m&&e.m.status!=='indicio_titulo').length,lex=es.filter(e=>e.rank===2).length;
        return '<article class="mobile-subject '+(opened?'is-open':'')+'"><button type="button" class="mobile-subject-trigger" data-mobile-toggle="'+i+'" aria-expanded="'+opened+'" aria-controls="mobile-panel-'+courseId+'-'+i+'">'+
          '<span class="mobile-subject-top"><span>'+esc(s.semester)+'ª etapa</span><span>'+esc(s.id||'Código a conferir')+'</span></span>'+
          '<span class="mobile-subject-title">'+esc(s.name)+'</span><span class="mobile-subject-footer"><span class="mobile-status-count '+(docs?'has-doc':'')+'">'+(docs?docs+' pré-análises':'Documento pendente')+'</span>'+(lex?'<span class="mobile-status-count has-doc">'+lex+' possibilidades</span>':'')+
          '<span class="mobile-subject-chevron" aria-hidden="true">'+(opened?'⌃':'⌄')+'</span></span></button><div id="mobile-panel-'+courseId+'-'+i+'" '+(opened?'':'hidden')+'>'+(opened?content(courseId,i,es):'')+'</div></article>';
      }).join(''):'<div class="mobile-empty-state"><strong>Nenhuma disciplina encontrada.</strong><p>Experimente outra etapa, universidade ou palavra-chave.</p></div>');
  }
  function openDetails(subjectIndex,ui,courseId) {
    const s=catalog.courses.find(c=>c.id===courseId)?.rows[subjectIndex], uni=catalog.universities[ui];
    if(!s||!uni)return;
    const col=[...document.querySelectorAll('#matrixHead th.foreign-cell')].findIndex(h=>h.querySelector('.uni-name')?.textContent.trim()===uni.name);
    const row=[...document.querySelectorAll('#matrixBody tr')].find(tr =>
      tr.querySelector('.subj-title')?.textContent.trim()===s.name &&
      (s.id ? tr.querySelector('.subj-code')?.textContent.trim()===s.id : tr.querySelector('.term')?.textContent.trim()===s.semester+'ª'));
    const button=col>=0&&row?.querySelectorAll('button.cell-button')[col];
    if(button){button.click();return;}
    document.getElementById('detailTitle').textContent=uni.name;
    document.getElementById('detailBody').textContent='Não foi possível abrir esta combinação. Ajuste os filtros e tente novamente.';
    document.getElementById('overlay').hidden=false;document.body.style.overflow='hidden';
  }
  results.addEventListener('click',event=>{
    const uni=event.target.closest('[data-mobile-university]');
    if(uni){openDetails(+uni.dataset.mobileSubject,+uni.dataset.mobileUniversity,uni.dataset.mobileCourse);return;}
    if(event.target.closest('[data-mobile-more]')){revealAll=!revealAll;render();return;}
    const trigger=event.target.closest('[data-mobile-toggle]');
    if(trigger){const key=selected()+'|'+(+trigger.dataset.mobileToggle);expanded=expanded===key?null:key;revealAll=false;render();}
  });
  root.querySelectorAll('[data-mobile-mode]').forEach(button=>button.addEventListener('click',()=>{
    document.body.classList.toggle('mobile-table-mode',button.dataset.mobileMode==='table');
    root.querySelectorAll('[data-mobile-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  }));
  new MutationObserver(render).observe(head,{childList:true});
  Promise.all([fetch('./data.json'),fetch('./triagem.json')]).then(async ([d,t])=>{
    if(!d.ok||!t.ok) throw new Error('Base indisponível');
    catalog=await d.json();const screening=await t.json();
    registry=new Map(screening.pairs.map(p=>[p[0]+'|'+p[1]+'|'+p[2],p]));
    foreign=new Map(catalog.foreignCourses.map(f=>[f.universityId+'|'+f.code,f]));
    render();
  }).catch(e=>{results.innerHTML='<p class="mobile-no-matches">Não foi possível carregar os dados. Atualize a página.</p>';console.error(e);});
})();
