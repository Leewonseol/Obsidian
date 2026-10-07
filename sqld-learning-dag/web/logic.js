/* SQLD DAG viewer — pure logic (no DOM). Loaded by index.html as window.SQLDLogic and by
 * tests/logic.test.mjs through require() / module.exports. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SQLDLogic = api;
}(typeof self !== 'undefined' ? self : this, () => {
  'use strict';

  const norm = (s) => String(s ?? '').toLowerCase().replace(/[\s·_\-()/]+/g, '');
  // exact match with spacing preserved ('ISNULL' ≠ 'IS NULL'), used to rank exact hits above normalised ones
  const rawKey = (s) => String(s ?? '').toLowerCase().trim().replace(/\s+/g, ' ');

  /** Adjacency for a directed edge list restricted to known node ids. */
  function adjacency(ids, edges, order) {
    const pred = new Map(); const succ = new Map();
    for (const id of ids) { pred.set(id, []); succ.set(id, []); }
    for (const e of edges) {
      if (!pred.has(e.target) || !succ.has(e.source)) continue;
      pred.get(e.target).push(e.source);
      succ.get(e.source).push(e.target);
    }
    if (order) {
      for (const l of pred.values()) l.sort(order);
      for (const l of succ.values()) l.sort(order);
    }
    return { pred, succ };
  }

  function closure(start, next) {
    const out = new Set(); const st = [...next(start)];
    while (st.length) {
      const x = st.pop();
      if (out.has(x)) continue;
      out.add(x);
      st.push(...next(x));
    }
    return out;
  }
  const ancestors = (pred, id) => closure(id, (x) => pred.get(x) || []);
  const descendants = (succ, id) => closure(id, (x) => succ.get(x) || []);

  /** Unlearned direct prerequisites. */
  const unmetPrereqs = (pred, id, statusOf) => (pred.get(id) || []).filter((p) => statusOf(p) !== 'learned');

  /**
   * Visibility of a node in a cluster card.
   * ctx: {includeLegacy, clusterMode: 'collapsed'|'core'|'all', forced: bool, tier: 'core'|'detail'}
   */
  function isVisible(n, ctx) {
    if (ctx.forced) return true;
    if (!n.visible_by_default && !ctx.includeLegacy) return false;
    if (ctx.clusterMode === 'all') return true;
    return ctx.tier === 'core';
  }

  /** Cluster card header toggle and "+n 세부 / 핵심만" button. */
  function nextClusterMode(mode, action) {
    if (action === 'toggle') return mode === 'collapsed' ? 'core' : 'collapsed';
    if (action === 'expand') return 'all';
    if (action === 'core') return 'core';
    return mode;
  }

  /** Stage / Domain filter. view: 'learning' | 'structure'. Empty filter value means "all". */
  function passesFilter(n, filter, view) {
    const stage = view === 'structure' ? n.source_stage : n.stage;
    const domain = view === 'structure' ? n.structure_domain : n.domain;
    if (filter.stage !== '' && filter.stage !== undefined && String(stage) !== String(filter.stage)) return false;
    if (filter.domain && domain !== filter.domain) return false;
    return true;
  }

  /**
   * Layered DAG layout of the visible nodes of one group.
   * vis: visible nodes sorted topologically; predOf(id) -> predecessors inside the group (visible or not).
   * Hidden nodes are bridged (direct=false). Returns {layers, links(transitively reduced), allLinks}.
   */
  function layeredLayout(vis, predOf) {
    const visSet = new Set(vis.map((n) => n.id));
    const links = new Map();
    for (const n of vis) {
      const seen = new Set();
      const stack = predOf(n.id).map((p) => [p, true]);
      while (stack.length) {
        const [p, direct] = stack.pop();
        if (seen.has(p)) continue;
        seen.add(p);
        if (visSet.has(p)) {
          const key = p + '>' + n.id;
          if (!links.has(key) || direct) links.set(key, { s: p, t: n.id, direct });
          continue;
        }
        for (const q of predOf(p)) stack.push([q, false]);
      }
    }
    const out = new Map(vis.map((n) => [n.id, []]));
    for (const l of links.values()) out.get(l.s).push(l.t);
    const reach = (from, to) => {
      const st = []; const seen = new Set();
      for (const y of out.get(from)) if (y !== to) st.push(y);
      while (st.length) {
        const x = st.pop();
        if (x === to) return true;
        if (seen.has(x)) continue;
        seen.add(x);
        st.push(...out.get(x));
      }
      return false;
    };
    const drawn = [...links.values()].filter((l) => !reach(l.s, l.t));
    const layer = new Map();
    const incoming = new Map(vis.map((n) => [n.id, []]));
    for (const l of links.values()) incoming.get(l.t).push(l.s);
    // vis is topologically sorted, but a bridged link may point "backwards" in that order when the
    // sort key differs; iterate until stable (graph is a DAG, so this terminates).
    let changed = true;
    for (const n of vis) layer.set(n.id, 0);
    while (changed) {
      changed = false;
      for (const n of vis) {
        let L = 0;
        for (const s of incoming.get(n.id)) L = Math.max(L, layer.get(s) + 1);
        if (L !== layer.get(n.id)) { layer.set(n.id, L); changed = true; }
      }
    }
    const layers = [];
    for (const n of vis) (layers[layer.get(n.id)] = layers[layer.get(n.id)] || []).push(n);
    const pos = new Map();
    const dense = layers.filter(Boolean);
    dense.forEach((row, li) => {
      if (li > 0) {
        const bc = (x) => {
          const ps = drawn.filter((l) => l.t === x.id).map((l) => pos.get(l.s)).filter((v) => v !== undefined);
          return ps.length ? ps.reduce((a, v) => a + v, 0) / ps.length : 999;
        };
        row.sort((a, b) => bc(a) - bc(b) || (a.topo_index ?? 0) - (b.topo_index ?? 0));
      }
      row.forEach((n, k) => pos.set(n.id, k / Math.max(1, row.length - 1)));
    });
    return { layers: dense, links: drawn, allLinks: [...links.values()], count: vis.length };
  }

  /** Search ranking over an index of {n, name, aliases, def} (all normalised). */
  function rankSearch(index, q, limit = 14) {
    const nq = norm(q);
    if (!nq) return [];
    const rq = rawKey(q);
    const out = [];
    for (const it of index) {
      let s = -1;
      if (it.raw === rq) s = 100;
      else if (it.rawAliases.includes(rq)) s = 97;
      else if (it.name === nq) s = 95;
      else if (it.aliases.includes(nq)) s = 90;
      else if (it.name.startsWith(nq)) s = 80 - Math.min(20, it.name.length - nq.length);
      else if (it.name.includes(nq)) s = 60 - Math.min(20, it.name.length - nq.length);
      else if (it.aliases.some((a) => a.includes(nq))) s = 45;
      else if (nq.length >= 2 && it.def.includes(nq)) s = 20;
      if (s >= 0) {
        if (it.n.visible_by_default) s += 3;
        if (it.n.priority === 'A') s += 2;
        out.push([s, it.n]);
      }
    }
    return out.sort((a, b) => b[0] - a[0] || (a[1].topo_index ?? 0) - (b[1].topo_index ?? 0)).slice(0, limit).map((x) => x[1]);
  }

  const searchIndex = (nodes, definitionOf) => nodes.map((n) => ({
    n, name: norm(n.name), aliases: (n.aliases || []).map(norm), def: norm(definitionOf(n.id)),
    raw: rawKey(n.name), rawAliases: (n.aliases || []).map(rawKey),
  }));

  /** Ancestor sub-DAG of a target (all branches kept), for the target learning-path view. */
  function prerequisiteSubgraph(pred, target) {
    const set = ancestors(pred, target);
    set.add(target);
    const edges = [];
    for (const t of set) for (const s of pred.get(t) || []) if (set.has(s)) edges.push({ source: s, target: t });
    const roots = [...set].filter((x) => !(pred.get(x) || []).some((p) => set.has(p)));
    return { nodes: set, edges, roots };
  }

  return {
    norm, adjacency, ancestors, descendants, unmetPrereqs, isVisible, nextClusterMode, passesFilter,
    layeredLayout, rankSearch, searchIndex, prerequisiteSubgraph,
  };
}));
