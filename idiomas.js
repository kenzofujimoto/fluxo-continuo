'use strict';
const $=s=>document.querySelector(s);
let db;
const state={course:'cc',mlc:'all',group:'all',search:''};
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function safeUrl(x){try{const u=new URL(x);return ['https:','http:'].includes(u.protocol)?u.href:'';}catch{return '';}}
function anchor(text,url){const href=safeUrl(url);return href?`<a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>`:'';}
function flag(code){const map={DE:'🇩🇪',AR:'🇦🇷',AT:'🇦🇹',BE:'🇧🇪',BO:'🇧🇴',CL:'🇨🇱',CO:'🇨🇴',KR:'🇰🇷',ES:'🇪🇸',US:'🇺🇸',FR:'🇫🇷',NL:'🇳🇱',IN:'🇮🇳',GB:'🇬🇧',IE:'🇮🇪',IT:'🇮🇹',MX:'🇲🇽',PT:'🇵🇹',RO:'🇷🇴',TR:'🇹🇷',UY:'🇺🇾'};return map[code]||'🌐';}
function matches(u){if(!u.courses?.[state.course])return false;const l=u.language||{};if(state.mlc==='yes'&&l.mlcAccepted!==true)return false;if(state.mlc==='no'&&l.mlcAccepted!==false)return false;if(state.mlc==='unknown'&&l.mlcAccepted!==null)return false;if(state.group!=='all'&&!String(l.required||'').toLocaleUpperCase('pt-BR').includes(state.group))return false;const q=state.search.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();const full=[u.name,u.coiName,u.country].join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();return !q||full.includes(q);}
function render(){const results=db.universities.filter(matches);$('#langCount').textContent=`${results.length} instituições marcadas “Sim” para ${db.courses.find(c=>c.id===state.course).name}`;$('#langResults').innerHTML=results.length?results.map(u=>{
 const l=u.language||{};const cls=l.mlcAccepted===true?'accepted':l.mlcAccepted===false?'rejected':'unknown';
 const mlc=l.mlcAccepted===true?'Aceita MLC: Sim':l.mlcAccepted===false?'Aceita MLC: Não':'MLC: não informado';
 const lang=l.dataIssue?'Requisito de idioma inválido no XLSX':l.required||'Requisito não informado';
 const req=l.dataIssue?'Conferir diretamente na universidade':(l.minimumScore||'Nota mínima não informada');
 return `<article class="lang-university" id="uni-${esc(u.id)}"><div class="lang-uni-main"><div class="lang-uni-flag">${flag(u.flag)}</div><div><div class="lang-country">${esc(u.country)}</div><h3>${esc(u.name)}</h3><p>${esc(lang)}</p></div></div><div class="lang-uni-info"><div><span>EXAMES ACEITOS (SEGUNDO COI)</span><strong>${esc(l.dataIssue?'Informação inválida':l.acceptedTests||'Não informado')}</strong></div><div><span>NOTA MÍNIMA</span><strong>${esc(req)}</strong></div><div class="lang-uni-meta"><b class="mlc-status ${cls}">${mlc}</b><small>Curso ${esc(state.course.toUpperCase())}: COI Sim</small></div></div><div class="lang-uni-links">${anchor('Exigências oficiais',l.source)}${anchor('Catálogo da instituição',u.catalogUrl)}${anchor('Site da instituição',u.website)}</div>${l.notes?`<p class="uni-note">${esc(l.notes)}</p>`:''}</article>`}).join(''):'<div class="no-lang">Nenhuma instituição encontrada. Ajuste os filtros.</div>';
}
async function bootstrap(){try{db=JSON.parse(document.getElementById('catalog-data').textContent);for(const [id,key] of [['langCourse','course'],['langAcceptance','mlc'],['langGroup','group']]){$('#'+id).addEventListener('change',e=>{state[key]=e.target.value;render();});}$('#langSearch').addEventListener('input',e=>{state.search=e.target.value;render();});const params=new URLSearchParams(location.search);const uni=db.universities.find(u=>u.id===params.get('universidade'));if(uni){state.course=Object.entries(uni.courses||{}).find(([c,yes])=>yes)?.[0]||'cc';$('#langCourse').value=state.course;}render();if(uni){const item=document.getElementById('uni-'+uni.id);if(item)item.scrollIntoView({behavior:'smooth',block:'center'});}}catch(e){$('#langResults').textContent='Não foi possível carregar os requisitos: '+e.message;}}
bootstrap();


