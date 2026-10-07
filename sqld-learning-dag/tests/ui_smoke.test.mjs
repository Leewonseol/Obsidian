// Optional browser smoke test. Skips when Playwright is not installed (no dependency is added to the repo).
// Run:  PLAYWRIGHT_DIR=/path/with/node_modules node --test tests/ui_smoke.test.mjs
// If Chromium is preinstalled elsewhere, set CHROMIUM_PATH.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

let chromium = null;
try {
  const req = createRequire(process.env.PLAYWRIGHT_DIR ? `${process.env.PLAYWRIGHT_DIR}/` : import.meta.url);
  ({ chromium } = req('playwright'));
} catch { /* not installed */ }

const url = new URL('../web/index.html', import.meta.url).href;

test('UI smoke: both views, search, detail tabs, filters, legacy toggle, path', { skip: !chromium && 'playwright not installed' }, async () => {
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(url);
  const count = () => page.$$eval('#canvas .node', (els) => els.length);

  const learningCore = await count();
  assert.ok(learningCore > 50 && learningCore < 250, `initial learning view shows core concepts only (${learningCore})`);
  await page.click('[data-view="structure"]');
  const structureCore = await count();
  assert.ok(structureCore > 50 && structureCore < 250, `initial structure view shows core concepts only (${structureCore})`);

  await page.fill('#search', 'RANK');
  await page.keyboard.press('Enter');
  for (const [tab, needle] of [['overview', '정렬값이 같은 행'], ['exam', 'RANK vs DENSE_RANK'], ['sql', '1,2,2,4'], ['learn', '윈도우 함수']]) {
    await page.click(`[data-dtab="${tab}"]`);
    assert.match(await page.$eval('.subtab-body', (e) => e.innerText), new RegExp(needle));
  }
  await page.click('[data-act="path-to"]');
  const layers = await page.$$eval('.minidag .layer', (els) => els.length);
  assert.ok(layers >= 4, 'target path rendered as a multi-layer DAG');

  const before = await count();
  await page.click('.cluster[data-cluster="AG3"] [data-act="cluster-all"]');
  assert.ok(await count() > before, 'expand cluster shows detail concepts');
  await page.click('.cluster[data-cluster="AG3"] [data-act="cluster-toggle"]');
  assert.equal(await page.$eval('.cluster[data-cluster="AG3"]', (e) => e.classList.contains('is-collapsed')), true);

  const noLegacy = await count();
  await page.click('[data-scope="legacy"]');
  assert.ok(await count() > noLegacy, 'Include Legacy shows more concepts');
  await page.click('[data-scope="current"]');

  await page.selectOption('#f-domain', 'D3');
  const sections = await page.$$eval('.stage', (els) => els.length);
  assert.ok(sections <= 2, 'domain filter narrows sections');
  assert.deepEqual(errors, []);
  await browser.close();
});
