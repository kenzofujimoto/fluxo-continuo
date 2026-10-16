/* Fluxo Contínuo — exploração móvel independente da tabela desktop. */
'use strict';
(function () {
  const root = document.getElementById('mobileExplorer');
  const results = document.getElementById('mobileResults');
  const head = document.getElementById('matrixHead');
  if (!root || !results || !head) return;

  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const flags = {RO:'🇷🇴',ES:'🇪🇸',GB:'🇬🇧',AT:'🇦🇹',PT:'🇵🇹',KR:'🇰🇷',IE:'🇮🇪',US:'🇺🇸',AR:'🇦🇷',UY:'🇺🇾',BO:'🇧🇴',CO:'🇨🇴',FR:'🇫🇷',DE:'🇩🇪',BE:'🇧🇪',CL:'🇨🇱',MX:'🇲🇽',IT:'🇮🇹'};
  const states = {P:'Indício por nome',T:'Período a verificar',S:'Triagem parcial',C:'Catálogo pendente',F:'Documentos pendentes',I:'Catálogo indexado · analisar par'};
  let catalog, registry, foreign, expanded = null, revealAll = false, suggestionIndex = new Map();
  let syllabi = new Map();
  const selected = () => document.querySelector('.course-tab[aria-selected="true"]')?.dataset.course || 'cc';

  function entries(courseId, subject, subjectIndex) {
    const filter = document.getElementById('university').value;
    const showAll = document.getElementById('allUniversities').checked;
    return catalog.universities.map((uni,ui) => {
      if ((!showAll && !uni.courses?.[courseId]) || (filter !== 'all' && filter !== uni.id)) return null;
      const matches = catalog.matches.filter(item => item.courseId === courseId && item.universityId === uni.id &&
        ((subject.id && item.mackCode === subject.id) || (!subject.id && normalize(item.mackName) === normalize(subject.name))));
      matches.sort((a,b) => (a.status==='candidata_forte'?0:a.status==='em_analise'?1:2) - (b.status==='candidata_forte'?0:b.status==='em_analise'?1:2));
      const m = matches[0];
      const triage = registry.get(courseId+'|'+subjectIndex+'|'+ui);
      const candidate = triage?.[4] && foreign.get(uni.id+'|'+triage[4][0]);
      const doc = m && foreign.get(uni.id+'|'+m.foreignCode);
      const extraSuggestions = (suggestionIndex.get(courseId+'|'+subjectIndex+'|'+ui) || []).map(pair => ({f:foreign.get(uni.id+'|'+pair[0]),lexical:pair[1]})).filter(x => x.f && !matches.some(m => m.foreignCode === x.f.code));
      const rank = m ? (m.status === 'indicio_titulo' ? 2 : m.status === 'candidata_forte' ? 0 : 1) : (candidate || extraSuggestions.length ? 2 : 3);
      return {uni,ui,m,matches,triage,candidate,doc,rank,extraSuggestions};
    }).filter(Boolean).sort((a,b) => a.rank-b.rank || a.uni.name.localeCompare(b.uni.name,'pt-BR'));
  }
  function universityCard(e,subjectIndex,courseId) {
    const displayMatches = e.matches.map(m => ({m,f:foreign.get(e.uni.id+'|'+m.foreignCode)})).filter(x=>x.f);
    const titles = displayMatches.map(({m,f})=>'<span class="mobile-foreign-course"><b>'+esc(f.originalCode || (f.officialCodeKnown===false?'Ref. catálogo':f.code))+'</b> '+esc(f.name)+' <small>· '+esc(m.status==='candidata_forte'?'candidata forte':m.status==='em_analise'?'pré-análise':'indício por título')+'</small></span>').join('');
    const extra = e.extraSuggestions.map(x=>'<span class="mobile-foreign-course">'+esc(x.f.name)+' <small>· indício de nome</small></span>').join('');
    const candidate = (!displayMatches.length && e.candidate) ? '<span class="mobile-foreign-course">'+esc(e.candidate.name)+' · <small>triagem lexical</small></span>' : '';
    const count=displayMatches.length + e.extraSuggestions.length;
    const label = count ? count+' possibilidade'+(count===1?'':'s') : (e.candidate?'Triagem lexical':'Pesquisa pendente');
    const color = e.rank===0?'strong':e.rank===1?'pending':e.rank===2?'potential':'unknown';
    return '<button type="button" class="mobile-university '+color+'" data-mobile-university="'+e.ui+'" data-mobile-subject="'+subjectIndex+'" data-mobile-course="'+esc(courseId)+'" aria-label="Abrir '+esc(e.uni.name)+': '+label+'">'+
      '<span class="mobile-university-main"><span class="mobile-flag">'+(flags[e.uni.flag]||'🌐')+'</span><span class="mobile-university-text"><strong>'+esc(e.uni.name)+'</strong><small>'+esc(e.uni.country)+' · '+esc(label)+'</small></span><span class="mobile-arrow" aria-hidden="true">›</span></span>'+
      (titles + extra || candidate || '<span class="mobile-undocumented">Sem candidata localizada nos catálogos indexados</span>')+'</button>';
  }
  function content(courseId,subjectIndex,es) {
    const useful=es.filter(e=>e.rank<3),remaining=es.filter(e=>e.rank===3);
    const showing=revealAll ? useful.concat(remaining) : useful;
    let html='<div class="mobile-entry-panel"><div class="mobile-entry-summary"><b>'+es.length+'</b> universidades elegíveis · <b>'+es.reduce((n,e)=>n+e.matches.filter(m=>m.status!=='indicio_titulo').length,0)+'</b> pré-análises documentais · <b>'+es.reduce((n,e)=>n+e.matches.filter(m=>m.status==='indicio_titulo').length+e.extraSuggestions.length+(e.m?0:e.candidate?1:0),0)+'</b> indícios em catálogos</div>';
    html+=showing.length ? showing.map(e=>universityCard(e,subjectIndex,courseId)).join('') : '<p class="mobile-no-matches">Não há candidata localizada nas fontes cadastradas. Muitos catálogos estrangeiros ainda não foram indexados integralmente; isso não demonstra incompatibilidade.</p>';
    if(remaining.length) html+='<button type="button" class="mobile-show-more" data-mobile-more="true">'+(revealAll?'Ocultar universidades sem candidata ↑':'Ver outras '+remaining.length+' universidades com pesquisa pendente ↓')+'</button>';
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
      const matches=es.flatMap(e=>e.matches).filter(m=>m.status!=='indicio_titulo');
      if(only && !es.some(e=>e.rank<3)) return false;
      if(status==='candidata_forte' && !matches.some(e=>e.status==='candidata_forte')) return false;
      if(status==='em_analise' && !matches.some(e=>e.status==='em_analise')) return false;
      if(status==='indicio_titulo' && !es.some(e=>e.matches.some(m=>m.status==='indicio_titulo') || e.rank===2)) return false;
      if(status==='sem_dados' && es.some(e=>e.rank<3)) return false;
      return true;
    });
    if(rows.length===1 && !expanded) expanded=courseId+'|'+rows[0].i;
    results.innerHTML='<div class="mobile-results-count"><span>'+rows.length+' de '+course.rows.length+' disciplinas</span><span>Toque para expandir ↓</span></div>'+
      (rows.length ? rows.map(({s,i,es})=>{
        const opened=expanded===courseId+'|'+i,docs=es.reduce((n,e)=>n+e.matches.filter(m=>m.status!=='indicio_titulo').length,0),lex=es.reduce((n,e)=>n+e.matches.filter(m=>m.status==='indicio_titulo').length+e.extraSuggestions.length+(e.matches.length?0:e.candidate?1:0),0);
        return '<article class="mobile-subject '+(opened?'is-open':'')+'"><button type="button" class="mobile-subject-trigger" data-mobile-toggle="'+i+'" aria-expanded="'+opened+'" aria-controls="mobile-panel-'+courseId+'-'+i+'">'+
          '<span class="mobile-subject-top"><span>'+esc(s.semester)+'ª etapa</span><span>'+esc(s.id||'Código a conferir')+'</span></span>'+
          '<span class="mobile-subject-title">'+esc(s.name)+'</span><span class="mobile-subject-footer"><span class="mobile-status-count '+(docs?'has-doc':'')+'">'+(docs?docs+' pré-análises':'Documento pendente')+'</span>'+(lex?'<span class="mobile-status-count has-doc">'+lex+' possibilidades</span>':'')+
          '<span class="mobile-subject-chevron" aria-hidden="true">'+(opened?'⌃':'⌄')+'</span></span></button><div id="mobile-panel-'+courseId+'-'+i+'" '+(opened?'':'hidden')+'>'+(opened?content(courseId,i,es):'')+'</div></article>';
      }).join(''):'<div class="mobile-empty-state"><strong>Nenhuma disciplina encontrada.</strong><p>Experimente outra etapa, universidade ou palavra-chave.</p></div>');
  }
  function openDetails(subjectIndex,ui,courseId) {
    const course=catalog.courses.find(c=>c.id===courseId);
    const s=course?.rows[subjectIndex],uni=catalog.universities[ui];
    if(!s||!uni)return;
    const matches=catalog.matches.filter(m=>m.courseId===courseId&&m.universityId===uni.id&&
      ((s.id&&m.mackCode===s.id)||(!s.id&&normalize(m.mackName)===normalize(s.name))));
    const getSafeLink=(label,url)=>{
      try {const u=new URL(url);return ['https:','http:'].includes(u.protocol)?'<a href="'+esc(u.href)+'" target="_blank" rel="noopener noreferrer" class="detail-link">'+esc(label)+' ↗</a>':'';}
      catch{return '';}
    };
    let html='<section class="detail-section"><div class="detail-label">DISCIPLINA MACKENZIE</div><div class="detail-course">'+esc(s.name)+'</div><p>'+esc(s.semester)+'ª etapa · '+esc(course.name)+'</p>'+getSafeLink('Ementário Mackenzie',s.syllabusUrl||course.source)+'</section>';
    if(matches.length) {
      html+='<section class="detail-section"><h3>'+matches.length+' possibilidade'+(matches.length===1?'':'s')+' encontrada'+(matches.length===1?'':'s')+'</h3><p>Correspondências documentais e afinidades por catálogo, sem homologação institucional.</p></section>';
      matches.forEach((m,i)=>{
        const f=foreign.get(uni.id+'|'+m.foreignCode);
        if(!f)return;
        const status=m.status==='candidata_forte'?'Candidata forte':m.status==='em_analise'?'Pré-análise documental':'Afinidade de nome — ementa não comparada';
        const proof=syllabi.get(uni.id+'|'+m.foreignCode);
        const evidenceHtml=proof?.status==='ementa_individual'
          ? '<div class="callout"><b>Ementa individual localizada.</b> '+esc(proof.contactHours!=null?proof.contactHours+' horas de contato na fonte':'Carga de contato a confirmar')+'; equivalência ainda não analisada integralmente.</div>'+getSafeLink('Abrir ementa auditada',proof.document)
          : '<p><b>Auditoria:</b> '+esc(proof?.status==='nao_tentada'?'Fonte aguarda coleta':proof?.status==='pagina_com_conteudo'?'Página com programa; verificação documental pendente':'Ementa individual não comprovada')+'</p>';
        html+='<section class="detail-section"><div class="detail-label">'+(i+1)+' · '+esc(status)+'</div><div class="detail-course">'+esc(f.name)+'</div>'+
        '<p><b>Código:</b> '+esc(f.originalCode || (f.officialCodeKnown===false?'Referência do catálogo (não código oficial)':f.code))+
        ' · <b>Oferta:</b> '+esc(f.period||'A confirmar')+' · <b>Créditos:</b> '+esc(f.credits ? f.credits+' '+(f.creditUnit||'créditos') : 'A confirmar')+'</p>'+
        '<div class="callout">'+esc(m.evidence||'É necessário conferir a ementa individual e a carga horária.')+'</div>'+
        getSafeLink('Consultar fonte oficial',f.source||m.source)+evidenceHtml+'</section>';
      });
    } else {
      const pair=registry.get(courseId+'|'+subjectIndex+'|'+ui);
      const possible=pair?.[4]&&foreign.get(uni.id+'|'+pair[4][0]);
      html+='<section class="detail-section"><h3>'+esc(states[pair?.[3]]||'Pesquisa pendente')+'</h3><p>Não há candidata curricular documentada neste cruzamento; isso não prova incompatibilidade.</p>'+
        (possible?'<p>Indício lexical: '+esc(possible.name)+'. Pontuação não é percentual de equivalência.</p>'+getSafeLink('Consultar catálogo',possible.source):'')+'</section>';
    }
    const extraSuggestions=(suggestionIndex.get(courseId+'|'+subjectIndex+'|'+ui)||[]).map(x=>({f:foreign.get(uni.id+'|'+x[0]),score:x[1]})).filter(x=>x.f&&!matches.some(m=>m.foreignCode===x.f.code));
    if(extraSuggestions.length){
      html+='<section class="detail-section"><h3>Outras disciplinas com nome semelhante</h3><p>Pesquisa automática de títulos em catálogos oficiais. <b>Não corresponde à equivalência curricular</b>, e a pontuação não é percentual de compatibilidade.</p>';
      extraSuggestions.forEach(x=>{html+='<p><b>'+esc(x.f.name)+'</b> · '+esc(x.f.officialCodeKnown===false?'Código não confirmado':x.f.code)+' · similaridade lexical '+esc(x.score)+'/100</p>'+getSafeLink('Fonte oficial',x.f.source);});
      html+='</section>';
    }
    html+='<section class="detail-section"><h3>Limitações</h3><p>Exigências de idioma, matrícula, horas e oferta de 2027.2 ainda precisam de confirmação. A coordenação decide qualquer aproveitamento.</p>'+
       getSafeLink('Site da universidade',uni.website)+getSafeLink('Catálogo',uni.catalogUrl)+'</section>';
    document.getElementById('detailTitle').textContent=uni.name;
    document.getElementById('detailBody').innerHTML=html;
    document.getElementById('overlay').hidden=false;document.body.style.overflow='hidden';
    document.getElementById('closeDetail').focus();
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
  Promise.all([fetch('./data.json'),fetch('./triagem.json'),fetch('./candidatos-catalogo.json')]).then(async ([d,t,candidates])=>{
    if(!d.ok||!t.ok) throw new Error('Base indisponível');
    catalog=await d.json();const screening=await t.json();const suggestions=candidates.ok?await candidates.json():{pairs:[]};
    suggestionIndex=new Map(suggestions.pairs.map(p=>[p[0]+'|'+p[1]+'|'+p[2],p[3]]));
    registry=new Map(screening.pairs.map(p=>[p[0]+'|'+p[1]+'|'+p[2],p]));
    foreign=new Map(catalog.foreignCourses.map(f=>[f.universityId+'|'+f.code,f]));
    try {const resp=await fetch('./syllabi/records.json',{cache:'no-store'});if(resp.ok){const doc=await resp.json();syllabi=new Map((doc.foreign||[]).map(r=>[r.universityId+'|'+r.foreignCode,r]));}}
    catch(error){console.warn('Ementários documentados indisponíveis',error);}
    render();
  }).catch(e=>{results.innerHTML='<p class="mobile-no-matches">Não foi possível carregar os dados. Atualize a página.</p>';console.error(e);});
})();
