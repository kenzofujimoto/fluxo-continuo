/* MobiMatch Alpha: camadas de triagem de TODOS os cruzamentos elegíveis.
   Afini­dade de título não constitui equivalência nem parecer acadêmico. */
'use strict';
(async function () {
  const [response, screeningResponse, candidateResponse] = await Promise.all([fetch('./data.json'), fetch('./triagem.json'), fetch('./candidatos-catalogo.json')]);
  if (!response.ok || !screeningResponse.ok) return;
  const data = await response.json();
  const screening = await screeningResponse.json();
  const registry = new Map(screening.pairs.map(function (p) {return [p[0] + '|' + p[1] + '|' + p[2], p];}));
  const extraCandidates = candidateResponse.ok ? await candidateResponse.json() : {pairs: []};
  const suggestionIndex = new Map(extraCandidates.pairs.map(function(p){return [p[0]+'|'+p[1]+'|'+p[2],p[3]];}));
  const foreignIndex = new Map(data.foreignCourses.map(function (f) {return [f.universityId + '|' + f.code, f];}));
  const uIndex = new Map(data.universities.map(function (u, i) {return [u.name, i];}));
  const labels = {P:'Afinidade lexical', T:'Verificar semestre', S:'Triagem parcial', C:'Consultar catálogo', F:'Solicitar documentos'};
  const tokens = {P:'Afinidade',T:'Período ?',S:'Sem indício',C:'Catálogo ↗',F:'Fonte ?'};
  const encode = function (s) {return String(s == null ? '' : s).replace(/[&<>"']/g, function (ch) {return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];});};
  const url = function (s) {try {const u=new URL(s);return ['https:','http:'].includes(u.protocol)?u.href:'';}catch{return '';}};
  const a = function (label, href) {const clean=url(href);return clean?'<a class="detail-link" target="_blank" rel="noopener noreferrer" href="'+encode(clean)+'">'+encode(label)+' ↗</a>':'';};
  function selectedCourse() {const tab = document.querySelector('.course-tab[aria-selected="true"]');return tab && tab.dataset.course;}
  function showDialog(record) {
    const course=data.courses.find(function (c) {return c.id===record.c;});
    const subject=course.rows[record.r],uni=data.universities[record.u];
    const entry=record.entry,st=entry[3],candidate=entry[4] && foreignIndex.get(uni.id+'|'+entry[4][0]);
    const intro='<section class="detail-section"><div class="detail-label">DISCIPLINA DO MACKENZIE</div><div class="detail-course">'+encode(subject.name)+'</div><p>'+encode(subject.semester)+'ª etapa • '+encode(course.name)+'</p>'+a('Ementário brasileiro',subject.syllabusUrl || course.source)+'</section>';
    const hints=(suggestionIndex.get(record.c+'|'+record.r+'|'+record.u)||[]).map(x=>({f:foreignIndex.get(uni.id+'|'+x[0]),score:x[1]})).filter(x=>x.f);
    const desc='<section class="detail-section"><h3>'+encode(labels[st])+'</h3><div class="callout"><b>Triagem automatizada, NÃO equivalência.</b><p>'+encode(screening.meta.statusLegend[st])+'</p><p>O algoritmo examinou nomes e metadados de disciplinas estrangeiras previamente coletadas. Não representa análise integral de todos os programas, nem reprovação de matéria sem similaridade.</p></div></section>';
    const more=hints.length?'<section class="detail-section"><h3>Possíveis disciplinas por nome (não homologadas)</h3><p>Correspondências somente lexicais de catálogos oficiais. Pontuação não corresponde a % de equivalência.</p>'+hints.map(x=>'<p><b>'+encode(x.f.name)+'</b> · '+encode(x.f.officialCodeKnown===false?'Código a confirmar':x.f.code)+' · '+x.score+'/100</p>'+a('Fonte acadêmica',x.f.source)).join('')+'</section>':'';
    const cand=candidate?'<section class="detail-section"><div class="detail-label">DISCIPLINA COM AFINIDADE LEXICAL</div><div class="detail-course">'+encode(candidate.name)+'</div><p>Código '+encode(candidate.code)+' • '+encode(candidate.academicYear || 'ano a confirmar')+'</p><p>Pontuação lexical '+entry[4][1]+'/100. <b>Não é percentual de compatibilidade.</b></p>'+a('Consultar disciplina ou catálogo oficial',candidate.source)+'</section>':'';
    const next='<section class="detail-section"><h3>O que ainda falta conferir</h3><p>Plano de ensino individual, horas de contato, cobertura tema a tema, pré-requisitos, acesso ao departamento e oferta em 2027.2.</p>'+a('Catálogo da universidade',uni.catalogUrl||uni.website)+'</section>';
    document.getElementById('detailTitle').textContent=uni.name;
    document.getElementById('detailBody').innerHTML=intro+desc+cand+more+next;
    document.getElementById('overlay').hidden=false;
    document.body.style.overflow='hidden';
    document.getElementById('closeDetail').focus();
  }
  function decorate() {
    const cid=selectedCourse();
    if(!cid)return;
    const course=data.courses.find(function (c) {return c.id===cid;});
    const headers=[...document.querySelectorAll('#matrixHead .foreign-cell .uni-name')];
    const universityIndexes=headers.map(function (x) {return uIndex.get(x.textContent.trim());});
    const rows=[...document.querySelectorAll('#matrixBody tr')];
    for (const row of rows) {
      const name=row.querySelector('.subj-title');
      if(!name)continue;
      const code=row.querySelector('.subj-code');
      const stage=row.querySelector('.term');
      let ri=course.rows.findIndex(function (x) {return x.id && x.id===(code&&code.textContent.trim()) && x.name===name.textContent.trim();});
      if(ri<0)ri=course.rows.findIndex(function (x) {return x.name===name.textContent.trim()&&String(x.semester)+'ª'===(stage&&stage.textContent.trim());});
      if(ri<0)continue;
      const buttons=[...row.querySelectorAll('button.cell-button')];
      for (let ci=0;ci<buttons.length;ci++) {
        const b=buttons[ci],ui=universityIndexes[ci];
        if(ui==null||!b.classList.contains('empty')||b.dataset.screening)continue;
        const r=registry.get(cid+'|'+ri+'|'+ui);
        if(!r)continue;
        const extras=suggestionIndex.get(cid+'|'+ri+'|'+ui)||[];
        const st=r[3];b.dataset.screening='true';b.dataset.sclass=st;b.dataset.sri=String(ri);b.dataset.sui=String(ui);b.dataset.scourse=cid;
        const first=document.createElement('span');first.className='match-code';first.textContent=extras.length?extras[0][0]:(r[4]?r[4][0]:tokens[st]);
        const second=document.createElement('span');second.className='cell-tag';second.textContent=extras.length?'Possível por título':labels[st];
        b.replaceChildren(first,second);b.title=screening.meta.statusLegend[st];
        if(st==='P'||extras.length)b.classList.add('suggested');
        if(st==='T')b.classList.add('timing');
      }
    }
  }
  const style=document.createElement('style');style.textContent='.cell-button.suggested{background:#eff1fc;color:#323a75;border-color:#c7d0eb}.cell-button.timing{background:#fff8e8;color:#825a13;border-color:#eedba7}.cell-button.screened .match-code{font-weight:700}';document.head.appendChild(style);
  document.addEventListener('click',function (event) {
    const target=event.target.closest && event.target.closest('#matrixBody button[data-screening="true"]');
    if(!target)return;
    event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();
    const key=target.dataset.scourse+'|'+target.dataset.sri+'|'+target.dataset.sui;
    const entry=registry.get(key);
    if(entry)showDialog({entry,c:target.dataset.scourse,r:+target.dataset.sri,u:+target.dataset.sui});
  },true);
  const tbody=document.getElementById('matrixBody');
  const observer=new MutationObserver(decorate);
  observer.observe(tbody,{childList:true,subtree:true});
  decorate();
  const exportButton=document.createElement('button');exportButton.type='button';exportButton.className='btn secondary';exportButton.textContent='↓ Auditoria total';
  const actions=document.querySelector('.matrix-actions');if(actions)actions.appendChild(exportButton);
  exportButton.addEventListener('click',function () {
    const output=[['Curso','Etapa','Código Mack','Disciplina Mack','Universidade','Status','Candidato lexical','Pontuação lexical','Fonte disponível','Candidatos adicionais por título','Fontes dos candidatos adicionais','Método dos candidatos adicionais']];
    for(const p of screening.pairs) {
      const c=data.courses.find(function (x) {return x.id===p[0];}),s=c.rows[p[1]],u=data.universities[p[2]];
      const f=p[4]&&foreignIndex.get(u.id+'|'+p[4][0]);
      const extras=(suggestionIndex.get(p[0]+'|'+p[1]+'|'+p[2])||[]).map(x=>({f:foreignIndex.get(u.id+'|'+x[0]),score:x[1]})).filter(x=>x.f);
      output.push([c.name,s.semester,s.id||'',s.name,u.name,screening.meta.statusLegend[p[3]],f&&f.code||'',p[4]&&p[4][1]||'',f&&f.source||u.catalogUrl||u.website||'',extras.map(x=>x.f.name+' ('+(x.f.officialCodeKnown===false?'ref.':x.f.code)+')').join(' | '),extras.map(x=>x.f.source||'').join(' | '),extras.length?'similaridade lexical, não equivalência':'']);
    }
    const csv='\ufeff'+output.map(function (r) {return r.map(function (cell) {let str=String(cell==null?'':cell);if(/^\s*[=+@-]/.test(str))str="'"+str;return '"'+str.replace(/"/g,'""')+'"';}).join(';');}).join('\r\n');
    const blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),objectUrl=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=objectUrl;a.download='mobimatch_auditoria_6856_cruzamentos.csv';a.click();setTimeout(function(){URL.revokeObjectURL(objectUrl);},1000);
  });
})().catch(function (err) {console.error('MobiMatch triagem indisponível:',err);});
