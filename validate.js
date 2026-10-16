/* Validação estática da base versionada. Rodar: node validate.js */
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync('data.json','utf8'));
const screen=JSON.parse(fs.readFileSync('triagem.json','utf8'));
const extra=JSON.parse(fs.readFileSync('candidatos-catalogo.json','utf8'));
assert.equal(data.universities.length,66);
assert.equal(data.courses.length,4);
assert.equal(data.courses.reduce((x,c)=>x+c.rows.length,0),221);
assert.equal(screen.pairs.length,data.courses.reduce((a,c)=>a+c.rows.length*data.universities.filter(u=>u.courses?.[c.id]).length,0));
const indexed=new Set();data.foreignCourses.forEach(f=>{const key=f.universityId+'|'+f.code;assert(!indexed.has(key),'foreign key duplicated: '+key);indexed.add(key);assert(/^https?:\/\//.test(f.source||''),'no source: '+key)});
data.matches.forEach(m=>{assert(indexed.has(m.universityId+'|'+m.foreignCode),'unresolved match');const course=data.courses.find(c=>c.id===m.courseId);assert(course&&course.rows.some(s=>s.id? s.id===m.mackCode:s.name.toLowerCase()===m.mackName.toLowerCase()),'unresolved Mackenzie course')});
const seen=new Set();screen.pairs.forEach(p=>{const course=data.courses.find(c=>c.id===p[0]);const u=data.universities[p[2]];assert(course&&course.rows[p[1]]&&u?.courses?.[p[0]],'invalid triage pair');const key=p.slice(0,3).join('|');assert(!seen.has(key),'duplicate triage pair');seen.add(key);if(p[4])assert(indexed.has(u.id+'|'+p[4][0]),'invalid triage foreign course')});
extra.pairs.forEach(p=>{const u=data.universities[p[2]],course=data.courses.find(c=>c.id===p[0]);assert(u&&course?.rows[p[1]],'invalid extra pair');p[3].forEach(x=>assert(indexed.has(u.id+'|'+x[0]),'invalid additional candidate'))});
console.log('OK: 66 universidades, 221 disciplinas Mackenzie, '+data.foreignCourses.length+' cursos estrangeiros, '+data.matches.length+' registros, '+screen.pairs.length+' pares triados.');
