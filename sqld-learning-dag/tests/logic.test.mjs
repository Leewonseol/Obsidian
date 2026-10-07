// UI logic tests — Node's built-in test runner, no dependencies.
// Run:  node --test tests/           (from sqld-learning-dag/)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const L = require('../web/logic.js');

const ctx = { window: {} };
vm.runInNewContext(readFileSync(new URL('../web/data.js', import.meta.url), 'utf8'), ctx);
const D = ctx.window.SQLD_DATA;
const byName = new Map(D.nodes.map((n) => [n.name, n]));
const NODES = new Map(D.nodes.map((n) => [n.id, n]));
const order = (a, b) => NODES.get(a).topo_index - NODES.get(b).topo_index;
const { pred, succ } = L.adjacency(D.nodes.map((n) => n.id), D.learning_edges, order);

test('search: exact name ranks first, aliases and definitions are searchable', () => {
  const index = L.searchIndex(D.nodes, (id) => D.content[id].definition);
  assert.equal(L.rankSearch(index, 'NULL')[0].name, 'NULL');
  assert.equal(L.rankSearch(index, 'rank')[0].name, 'RANK');
  assert.equal(L.rankSearch(index, '계층형 질의')[0].name, '계층형 질의');
  assert.equal(L.rankSearch(index, 'ISNULL')[0].name, 'NVL');
  assert.deepEqual(L.rankSearch(index, '   '), []);
});

test('legacy filter: legacy-only nodes hidden unless Include Legacy', () => {
  const legacy = byName.get('실행계획');
  assert.equal(legacy.visible_by_default, false);
  const base = { clusterMode: 'all', forced: false, tier: 'core' };
  assert.equal(L.isVisible(legacy, { ...base, includeLegacy: false }), false);
  assert.equal(L.isVisible(legacy, { ...base, includeLegacy: true }), true);
  assert.equal(L.isVisible(legacy, { ...base, includeLegacy: false, forced: true }), true);
  for (const n of D.nodes.filter((x) => x.evidence_status === 'current')) assert.ok(n.visible_by_default, n.name);
});

test('expand / collapse: cluster modes and tier visibility', () => {
  assert.equal(L.nextClusterMode('core', 'toggle'), 'collapsed');
  assert.equal(L.nextClusterMode('collapsed', 'toggle'), 'core');
  assert.equal(L.nextClusterMode('core', 'expand'), 'all');
  assert.equal(L.nextClusterMode('all', 'core'), 'core');
  const detail = D.nodes.find((n) => n.visible_by_default && n.display_tier === 'detail');
  const ctxBase = { includeLegacy: false, forced: false, tier: 'detail' };
  assert.equal(L.isVisible(detail, { ...ctxBase, clusterMode: 'core' }), false);
  assert.equal(L.isVisible(detail, { ...ctxBase, clusterMode: 'all' }), true);
});

test('stage / domain filters per view', () => {
  const n = byName.get('CHECK'); // learning view moves CHECK to MG3 (Stage 7); structure keeps source SQ1 (Stage 2)
  assert.equal(L.passesFilter(n, { stage: '7', domain: '' }, 'learning'), true);
  assert.equal(L.passesFilter(n, { stage: '7', domain: '' }, 'structure'), false);
  assert.equal(L.passesFilter(n, { stage: '2', domain: 'D2' }, 'structure'), true);
  assert.equal(L.passesFilter(n, { stage: '', domain: '' }, 'learning'), true);
});

test('layered layout bridges hidden nodes and reduces transitive edges', () => {
  const vis = [{ id: 'a', topo_index: 0 }, { id: 'c', topo_index: 2 }, { id: 'd', topo_index: 3 }];
  const preds = { a: [], b: ['a'], c: ['b'], d: ['a', 'c'] };
  const lay = L.layeredLayout(vis, (id) => preds[id]);
  assert.deepEqual(lay.layers.map((r) => r.map((x) => x.id)), [['a'], ['c'], ['d']]);
  const ac = lay.allLinks.find((l) => l.s === 'a' && l.t === 'c');
  assert.equal(ac.direct, false); // through hidden b
  assert.equal(lay.links.some((l) => l.s === 'a' && l.t === 'd'), false); // implied by a→c→d
});

test('target path keeps every prerequisite branch (RANK)', () => {
  const rank = byName.get('RANK').id;
  const sub = L.prerequisiteSubgraph(pred, rank);
  const names = new Set([...sub.nodes].map((x) => NODES.get(x).name));
  for (const x of ['윈도우 함수', 'OVER 절', 'ORDER BY', '순위 함수', 'RANK']) assert.ok(names.has(x), x);
  assert.ok(!names.has('DENSE_RANK')); // comparison, not prerequisite
  const into = (name) => sub.edges.filter((e) => NODES.get(e.target).name === name).length;
  assert.ok(into('OVER 절') >= 2, 'OVER 절 has several prerequisite branches');
});

test('unmet prerequisites are reported without auto-learning children', () => {
  const where = byName.get('WHERE').id;
  const select = byName.get('SELECT').id;
  const status = (id) => (id === select ? 'learned' : 'not_started');
  assert.deepEqual(L.unmetPrereqs(pred, where, status), []);
  const child = succ.get(select)[0];
  assert.equal(status(child), 'not_started');
});

test('concept detail content is wired by Node ID', () => {
  const c = D.content[byName.get('NOT IN').id];
  assert.ok(c.definition.length > 0);
  assert.ok(c.traps.every((id) => D.rules_and_traps[id].type === 'EXAM_TRAP'));
  assert.ok(c.comparisons.includes('C019'));
  assert.ok(c.examples.some((id) => D.examples.find((e) => e.id === id).type === 'RESULT'));
  assert.ok(D.dialects.every((d) => NODES.has(d.node)));
});
