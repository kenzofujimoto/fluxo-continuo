import { test } from 'node:test';
import assert from 'node:assert/strict';
import { choosePlan, type PlanningOption } from '../lib/planning';
const option = (key:string, foreign:string[], level:'high'|'partial'='partial'):PlanningOption => ({key, universityId:'u', foreign, level, reviewId:key, href:'/comparacoes/'+key, name:key, foreignNames:foreign, hours:'Não confirmadas', limitations:[]});
test('bundles reserve all foreign courses and never count a Brazilian discipline twice',()=>{
 const result=choosePlan([option('a',['x','y']),option('b',['y']),option('a',['z']),option('c',['w'])],['a','b','c']);
 assert.equal(new Set(result.map(x=>x.key)).size,result.length);
 assert.equal(new Set(result.flatMap(x=>x.foreign)).size,result.flatMap(x=>x.foreign).length);
 assert.equal(result.length,3);
});
test('selection excludes stale disciplines and prioritizes high affinity',()=>{
 const result=choosePlan([option('a',['x']),option('b',['x'],'high'),option('c',['y'])],['a','b']);
 assert.deepEqual(result.map(x=>x.key),['b']);
 assert.deepEqual(choosePlan([option('a',['x'])],[]),[]);
});
