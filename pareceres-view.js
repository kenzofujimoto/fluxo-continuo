/* Fluxo Contínuo — shared, dependency-free rendering of individual curricular opinions (pareceres).
 * Every string from data is escaped; links pass through safeUrl (https/http only).
 * Four independent dimensions are never merged: candidate colour (matrix), evidence stage,
 * documentary opinion (this module) and homologation (always "none" unless a formal decision exists). */
'use strict';
(function (global) {
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const safeUrl = v => { try { const u = new URL(v); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch { return ''; } };
  const fmt = (n, d = 2) => n == null || Number.isNaN(Number(n)) ? '—' : Number(n).toLocaleString('pt-BR', {maximumFractionDigits: d});

  const CLASS = {
    alta_afinidade: {label: 'Alta afinidade documental', short: 'Alta', css: 'v-alta',
      plain: 'Os programas oficiais cobrem a maior parte dos tópicos da ementa Mackenzie e as horas de contato declaradas são analisáveis. Ainda depende da decisão da coordenação.'},
    afinidade_parcial: {label: 'Afinidade parcial', short: 'Parcial', css: 'v-parcial',
      plain: 'Há sobreposição relevante, mas faltam tópicos, as horas não são comparáveis ou a ementa brasileira não está confirmada como vigente.'},
    baixa_afinidade: {label: 'Baixa afinidade documental', short: 'Baixa', css: 'v-baixa',
      plain: 'Os programas mostram diferenças importantes de conteúdo ou de carga. A semelhança do título não se sustenta no conteúdo.'},
    evidencia_insuficiente: {label: 'Evidência insuficiente', short: 'Insuf.', css: 'v-insuf',
      plain: 'Faltam documentos ou informações essenciais para comparar. Isso não é uma reprovação.'},
  };
  const TOPIC = {coberto: ['Coberto', 't-ok'], parcial: ['Parcial', 't-part'], nao_encontrado: ['Não encontrado', 't-miss'], nao_verificavel: ['Não verificável', 't-unk']};
  const RANK = {alta_afinidade: 3, afinidade_parcial: 2, baixa_afinidade: 1, evidencia_insuficiente: 0};
  const CONF = {alta: 'Confiança alta', moderada: 'Confiança moderada', baixa: 'Confiança baixa'};

  function classPill(p) {
    const c = CLASS[p.conclusionClass] || CLASS.evidencia_insuficiente;
    return '<span class="verdict-pill ' + c.css + '" title="' + esc(c.plain) + '">Parecer: ' + esc(c.label) + '</span>';
  }
  function link(label, url) {
    const u = safeUrl(url);
    return u ? '<a class="detail-link" href="' + esc(u) + '" target="_blank" rel="noopener noreferrer"><span>' + esc(label) + '</span><span aria-hidden="true">↗</span></a>' : '';
  }
  function hoursHtml(p) {
    const h = p.hoursComparison || {};
    const b = p.brazil.hours || {};
    const fs = p.foreign.map(f => {
      const x = f.hours || {};
      const parts = [];
      if (x.contactTotal != null) parts.push(fmt(x.contactTotal) + ' h de contato/semestre' + (x.contactLecture != null ? ' (' + fmt(x.contactLecture) + ' aula + ' + fmt(x.contactSeminarLab) + ' sem./lab.)' : ''));
      if (x.selfStudy != null) parts.push(fmt(x.selfStudy) + ' h estudo autônomo');
      if (x.totalWorkload != null) parts.push(fmt(x.totalWorkload) + ' h de trabalho total');
      if (x.ects != null) parts.push(fmt(x.ects) + ' ECTS');
      return '<li><b>' + esc(f.code) + ':</b> ' + esc(parts.join(' · ') || 'Horas não declaradas no documento') + '</li>';
    }).join('');
    const brTxt = b.value == null ? 'Não comprovadas' : fmt(b.value) + (b.unit === 'hora_relogio' ? ' h (horas-relógio, semestre)' : ' h-a por ' + (b.basis === 'semana' ? 'semana' : 'período'));
    let cmp;
    if (h.state === 'comparavel') cmp = 'Comparável: ' + fmt(h.foreignClockHours) + ' h × ' + fmt(h.brClockHours) + ' h → diferença ' + fmt(h.diffAbs) + ' h (' + fmt(h.diffPct, 1) + '%). ' + esc(h.basis);
    else if (h.state === 'comparavel_condicional') cmp = 'Comparação condicional: ' + fmt(h.foreignDeclaredHours) + ' h declaradas × ' + fmt(h.brClockHours) + ' h Mackenzie → ' + (h.diffAbs >= 0 ? '+' : '') + fmt(h.diffAbs) + ' h (' + fmt(h.diffPct, 1) + '%); razão ' + fmt(h.ratio, 2) + ' (ou ' + fmt(h.ratioIf50min, 2) + ' se a hora estrangeira tiver 50 min). A duração da hora estrangeira não é informada.';
    else cmp = 'Não comparável: ' + (h.reason || 'bases diferentes') + ' ECTS não são convertidos em horas.';
    return '<div class="pv-block"><h4>Carga horária</h4><p><b>Mackenzie:</b> ' + esc(brTxt) + '</p><ul class="pv-list">' + fs + '</ul><p class="pv-note">' + esc(cmp) + '</p></div>';
  }
  function topicsHtml(p) {
    const rows = p.topics.map(t => {
      const s = TOPIC[t.status] || TOPIC.nao_verificavel;
      const ev = t.status === 'nao_encontrado' ? 'Não encontrado em: ' + (t.scopeExamined || '') : (t.foreignEvidence || '—');
      return '<li class="pv-topic ' + s[1] + '"><div class="pv-topic-head"><span class="pv-tag">' + esc(s[0]) + '</span>' + (t.essential === false ? '<span class="pv-tag pv-muted">não essencial</span>' : '') +
        '</div><p class="pv-br"><b>Mackenzie:</b> ' + esc(t.brTopic) + '</p><p class="pv-fr"><b>Estrangeira:</b> ' + esc(ev) + '</p>' +
        (t.foreignLocation ? '<p class="pv-loc">' + esc(t.foreignLocation) + '</p>' : '') + (t.note ? '<p class="pv-loc">' + esc(t.note) + '</p>' : '') + '</li>';
    }).join('');
    const c = p.coverage || {};
    return '<div class="pv-block"><h4>Conteúdos tópico a tópico</h4><p class="pv-note">' + esc(c.coberto) + ' coberto(s), ' + esc(c.parcial) + ' parcial(is), ' + esc(c.nao_encontrado) + ' não encontrado(s) e ' + esc(c.nao_verificavel) + ' não verificável(is), de ' + esc(c.essential) + ' tópicos essenciais. A contagem não é percentual oficial de equivalência.</p><ul class="pv-topics">' + rows + '</ul></div>';
  }
  function listBlock(title, items) {
    const arr = (items || []).map(x => typeof x === 'string' ? x : (x.topic ? x.topic + (x.location ? ' — ' + x.location : '') : JSON.stringify(x)));
    return arr.length ? '<div class="pv-block"><h4>' + esc(title) + '</h4><ul class="pv-list">' + arr.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div>' : '';
  }
  function render(p, opts = {}) {
    const c = CLASS[p.conclusionClass] || CLASS.evidencia_insuficiente;
    const f0 = p.foreign[0] || {};
    const sources = '<div class="pv-block"><h4>Documentos de referência</h4>' +
      '<p><b>Mackenzie</b> · ' + esc(p.brazil.documentTitle || 'Ementário') + ' · ano ' + esc(p.brazil.documentYear ?? 'não impresso') + (p.brazilDocumentCurrent ? '' : ' · <b>vigência não confirmada</b>') + '<br><span class="pv-loc">' + esc(p.brazil.location || '') + '</span></p>' + link('Ementa Mackenzie', p.brazil.source) +
      p.foreign.map(f => '<p><b>' + esc(f.university || '') + ' · ' + esc(f.code) + '</b> · ano letivo ' + esc(f.academicYear || 'não informado') + '<br><span class="pv-loc">' + esc(f.location || '') + '</span></p>' + link('Programa oficial ' + f.code, f.source)).join('') + '</div>';
    const practical = p.practical || {};
    const prac = '<div class="pv-block"><h4>Restrições práticas</h4><ul class="pv-list">' +
      ['period', 'language', 'enrolment', 'prerequisites'].filter(k => practical[k]).map(k => '<li><b>' + ({period: 'Período', language: 'Idioma', enrolment: 'Matrícula', prerequisites: 'Pré-requisitos'}[k]) + ':</b> ' + esc(practical[k]) + '</li>').join('') +
      '<li><b>Oferta 2027.2:</b> não confirmada</li></ul></div>';
    const comp = p.competencies ? listBlock('Competências convergentes', p.competencies.convergences) + listBlock('Diferenças de competências', p.competencies.differences) : '';
    const depth = p.depth ? '<div class="pv-block"><h4>Nível e profundidade</h4><p>' + esc([p.depth.level, p.depth.theoryPractice].filter(Boolean).join(' · ')) + '</p></div>' : '';
    return '<article class="pv-card" id="' + esc('p-' + p.id.replace(/[^A-Za-z0-9]+/g, '-')) + '">' +
      '<div class="pv-head">' + classPill(p) + '<span class="verdict-pill v-conf">' + esc(CONF[p.confidence] || p.confidence) + '</span><span class="verdict-pill v-homolog">Homologação: nenhuma decisão formal</span>' +
      (p.secondReview && p.secondReview.required ? '<span class="verdict-pill v-second" title="' + esc(p.secondReview.reason || '') + '">Segunda revisão recomendada</span>' : '') + '</div>' +
      (opts.withTitle ? '<h3 class="pv-title">' + esc(p.brazil.name) + ' × ' + esc(f0.name) + '</h3><p class="pv-sub">' + esc(p.brazil.courseName || p.brazil.courseId) + ' · ' + esc(f0.university || f0.universityId) + ' · ' + esc(f0.code) + '</p>' : '') +
      '<p class="pv-plain"><b>Em linguagem simples:</b> ' + esc(c.plain) + '</p>' +
      '<p><b>Síntese:</b> ' + esc(p.synthesis) + '</p><p><b>Fundamentação:</b> ' + esc(p.justification) + '</p>' +
      (p.downgradeReason ? '<p><b>Por que a classe é mais conservadora que a regra:</b> ' + esc(p.downgradeReason) + '</p>' : '') +
      '<details class="pv-details"' + (opts.open ? ' open' : '') + '><summary>Ver análise completa</summary>' +
      topicsHtml(p) + listBlock('Conteúdos adicionais da disciplina estrangeira', p.additionalForeignTopics) + hoursHtml(p) + comp + depth + prac +
      listBlock('Limitações e informações não confirmadas', p.limitations) + listBlock('Perguntas para a coordenação', p.openQuestions) +
      listBlock('Alternativas na mesma universidade', (p.alternatives || []).map(a => a.code + ' — ' + a.name + (a.relation ? ': ' + a.relation : ''))) +
      '<div class="pv-block"><h4>Confiança</h4><p>' + esc(p.confidenceRationale) + '</p></div>' + sources +
      '<p class="pv-loc">Método: ' + esc(p.method || '') + ' · revisado em ' + esc(p.reviewedAt || '') + '. Parecer preliminar independente; não é homologação.</p></details></article>';
  }
  async function load() {
    try { const r = await fetch('./syllabi/pareceres-index.json', {cache: 'no-store'}); if (!r.ok) return []; return (await r.json()).pareceres || []; }
    catch (e) { console.warn('Pareceres indisponíveis', e); return []; }
  }
  global.Pareceres = {render, load, classPill, CLASS, RANK, esc, safeUrl};
})(window);
