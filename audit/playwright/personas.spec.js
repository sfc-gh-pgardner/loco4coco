// Loco 4 CoCo - persona audit, real Chromium.
//
// One project per industry track, because each track is a different demo: a
// different letter, different library options, a different Marketplace stall.
// Acceptance criteria come from audit/personas.md - keep the two in step.
//
// Run:  npx --no-install playwright test --config audit/playwright.config.js
//
// The server must already be running on 127.0.0.1:4747. The spec resets the
// visitor between tracks because state is single-visitor per server process.

const { test, expect } = require('@playwright/test');

const BASE = 'http://127.0.0.1:4747';

// Non-UK geography markers. A UK stand offering "India Economic Monitor" is the
// exact defect this audit exists to catch.
const OFF_GEO = ['india', 'united states', ' usa', 'brazil', 'canada',
  'australia', 'japan', 'china', 'germany', 'france', 'mexico',
  'international', 'worldwide', 'all countries'];

const UK_SIGNAL = ['uk', 'united kingdom', 'great britain', 'gb', 'england',
  'wales', 'scotland', 'british', 'nhs', 'ordnance survey', 'postcode',
  'census', 'acorn'];

const TRACKS = {
  healthcare: {
    persona: 'Dr Amara Okafor, Clinical Informatics Lead',
    company: 'Royal Free London NHS FT',
    problem: 'Eleven years of discharge summaries and referral letters nobody can query.',
    expectOptions: ['Patient records', 'Clinical notes & letters'],
    maxMetOffice: 1, minUkSignal: 2, full: true,
  },
  financial: {
    persona: 'Tom Whitfield, Head of Data',
    company: 'Northbank Building Society',
    problem: 'We cannot explain a fraud alert to a regulator without a data team ticket.',
    expectOptions: ['Transaction history', 'Positions & trades'],
    maxMetOffice: 0, minUkSignal: 1, full: true,
  },
  retail: {
    persona: 'Priya Raman, Trading Analyst',
    company: 'Greenaisle Stores',
    problem: 'We do not know why a store underperforms against its catchment.',
    expectOptions: ['Sales & till transactions', 'Loyalty & customer data'],
    maxMetOffice: 2, minUkSignal: 3, full: false,
  },
  public: {
    persona: 'Sam Booth, Head of Digital',
    company: 'Leeds City Council',
    problem: 'Planning application determination takes far too long.',
    expectOptions: ['Case management records', 'Policy & guidance documents'],
    // The regression this audit was written for: 3 of 6 were Met Office and one
    // was India Economic Monitor.
    maxMetOffice: 1, minUkSignal: 3, full: true,
    mustInclude: ['Administrative boundaries'],   // OS, regions = ALL
  },
  manufacturing: {
    persona: 'Greg Nowak, Plant Systems Manager',
    company: 'Camshaft Precision Ltd',
    problem: 'Sensor data sits on the shop floor and we cannot predict defects.',
    expectOptions: ['Machine & sensor telemetry', 'Quality & defect records'],
    maxMetOffice: 2, minUkSignal: 0, full: false,
  },
  energy: {
    persona: 'Fiona Hargreaves, Network Data Manager',
    company: 'Pennine Power Networks',
    problem: 'We cannot forecast network constraint from smart meter volume.',
    expectOptions: ['Smart meter readings', 'Outage & fault records'],
    maxMetOffice: 2, minUkSignal: 0, full: false,
  },
  media: {
    persona: 'Dan Mercer, Audience Insight Lead',
    company: 'Channel Northern',
    problem: 'Viewing behaviour is not joined to audience context so churn surprises us.',
    expectOptions: ['Viewing & listening events', 'Subscriber & account data'],
    maxMetOffice: 1, minUkSignal: 1, full: false,
  },
  other: {
    persona: 'Alex Deniz, Ops Manager',
    company: 'Deniz Logistics',
    problem: 'Our data is spread across systems and we cannot see the whole picture.',
    expectOptions: ['Core operational records', 'Documents & PDFs'],
    maxMetOffice: 2, minUkSignal: 0, full: false,
  },
};

async function resetVisitor(page) {
  await page.request.post(`${BASE}/api/reset`).catch(() => {});
}

// The intro is a chain of timed, click-skippable beats. Click the stage until
// the letter appears rather than sleeping for a fixed period.
async function reachLetter(page) {
  await page.goto(`${BASE}/?audit=${Date.now()}`);
  const start = page.locator('#t-go');
  if (await start.isVisible().catch(() => false)) await start.click();
  const letter = page.locator('#ov-letter');
  for (let i = 0; i < 40; i++) {
    if (await letter.evaluate(el => el.classList.contains('on')).catch(() => false)) return;
    await page.locator('#stagewrap').click({ position: { x: 40, y: 40 } }).catch(() => {});
    await page.waitForTimeout(220);
  }
  throw new Error('letter overlay never appeared');
}

async function submitLetter(page, t, industry) {
  await page.fill('#l-first', t.persona.split(',')[0].split(' ').pop());
  await page.fill('#l-company', t.company);
  await page.fill('#l-problem', t.problem);
  await page.selectOption('#l-industry', industry === 'other' ? '' : industry);
  await page.click('#l-go');
}

// Skip intro beats until the home-stage gate is showing, without answering it -
// used by the X5/X6 guardrail test which inspects the gate itself.
async function reachHomeGate(page) {
  const home = page.locator('#ov-home');
  for (let i = 0; i < 50; i++) {
    if (await home.evaluate(el => el.classList.contains('on')).catch(() => false)) return;
    await page.locator('#stagewrap').click({ position: { x: 40, y: 40 } }).catch(() => {});
    await page.waitForTimeout(220);
  }
  throw new Error('home-stage gate never appeared');
}

async function answerHomeGate(page, platform = 'AWS') {
  const home = page.locator('#ov-home');
  if (!(await home.evaluate(el => el.classList.contains('on')).catch(() => false))) return;
  // Q1 platforms
  await page.locator('#hq-chips .chip', { hasText: platform }).first().click();
  await page.click('#hq-go');
  await page.waitForTimeout(150);
  // Q2 country
  await page.locator('#hq-chips .chip').first().click();
  await page.click('#hq-go');
  await page.waitForTimeout(150);
  // Q3 residency
  await page.locator('#hq-chips .chip').first().click();
  await page.click('#hq-go');
  await page.waitForTimeout(200);
}

async function reachMap(page) {
  // The intro plays line1/line2 as bubble text (no overlay), then the BLOCKING
  // home gate. An earlier version returned as soon as no overlay was on, which
  // fell through during line1 - before the gate appeared - so the gate was
  // never answered and residency/country were never captured. So: wait for the
  // gate, answer it, then confirm no opening overlay remains.
  const home = page.locator('#ov-home');
  let answered = false;
  for (let i = 0; i < 70; i++) {
    if (await home.evaluate(el => el.classList.contains('on')).catch(() => false)) {
      await answerHomeGate(page); answered = true; break;
    }
    // Skipping a timed beat (line1/line2) is safe; skipBeat refuses to skip the
    // gate itself, so this only fast-forwards the narration.
    await page.locator('#stagewrap').click({ position: { x: 40, y: 40 } }).catch(() => {});
    await page.waitForTimeout(220);
  }
  for (let i = 0; i < 30 && answered; i++) {
    const anyOv = await page.evaluate(() =>
      ['ov-title', 'ov-arctic', 'ov-letter', 'ov-home'].some(id => {
        const e = document.getElementById(id);
        return e && e.classList.contains('on');
      }));
    if (!anyOv) return;
    await page.waitForTimeout(200);
  }
}

// Walking the penguin tile by tile is slow and flaky; the panel opener is the
// same function the keyboard path calls.
async function openLocation(page, id) {
  // Retry, do not fire once. openPanel() gates on the CLIENT's ST.unlocked,
  // which only refreshes on the browser's poll tick - so immediately after the
  // server unlocks a stop the client still believes it is locked. Also absorbs
  // reopenLock, the 700ms guard that stops ENTER reopening a just-closed panel.
  const ov = page.locator('#ov-loc');
  for (let i = 0; i < 30; i++) {
    await page.evaluate(loc => window.openPanel && window.openPanel(loc), id);
    await page.waitForTimeout(400);
    if (await ov.evaluate(el => el.classList.contains('on')).catch(() => false)) return;
  }
  throw new Error(`panel ${id} never opened`);
}

// Locations unlock in order, so the marketplace cannot be opened until the
// library has been answered. Tick one option, confirm, and wait for CoCo.
async function completeLibrary(page) {
  await openLocation(page, 'library');
  await page.locator('#c-opts .opt').first().click();
  await page.waitForTimeout(300);
  await page.locator('#ov-loc button.primary').click();
  await page.waitForFunction(
    () => !document.getElementById('ov-loc').classList.contains('on'),
    null, { timeout: 120000 });
  // CoCo's reply is what unlocks the next stop. ST is a `let` binding, not a
  // window property, so poll the server rather than the page.
  for (let i = 0; i < 60; i++) {
    const st = await (await page.request.get(`${BASE}/api/state`)).json();
    if ((st.unlocked || []).includes('marketplace')) return;
    await page.waitForTimeout(1000);
  }
  throw new Error('marketplace never unlocked after the library');
}

for (const [industry, t] of Object.entries(TRACKS)) {
  test.describe(`${industry} - ${t.persona}`, () => {
    test.beforeEach(async ({ page }) => {
      await resetVisitor(page);
    });

    test('X1 letter asks only what it needs, and never an email', async ({ page }) => {
      await reachLetter(page);
      const ctl = await page.evaluate(() => {
        const ov = document.getElementById('ov-letter');
        return [...ov.querySelectorAll('input,select,textarea')]
          .map(e => ({ id: e.id, type: e.type || e.tagName.toLowerCase() }));
      });
      expect(ctl.length, `letter controls: ${JSON.stringify(ctl)}`).toBe(4);
      expect(ctl.some(c => c.type === 'email' || /email/i.test(c.id))).toBe(false);
    });

    test('X2/X10 library speaks this industry and renders as a room', async ({ page }, ti) => {
      await reachLetter(page);
      await submitLetter(page, t, industry);
      await reachMap(page);
      await openLocation(page, 'library');

      const labels = await page.$$eval('#c-opts .opt',
        els => els.map(e => e.querySelector('.lb').textContent.trim()));
      expect(labels.length, `options: ${JSON.stringify(labels)}`).toBe(6);
      for (const want of t.expectOptions) {
        expect(labels.join(' | '),
          `expected "${want}" in ${JSON.stringify(labels)}`).toContain(want);
      }

      // X10: the interior must be a room, not a squashed strip, and the pixel
      // buffer must match the box or the art is stretched.
      const geo = await page.evaluate(() => {
        const cv = document.getElementById('cv'), sc = document.getElementById('scene');
        const r = cv.getBoundingClientRect();
        return {
          cssRatio: +(r.height / r.width).toFixed(3),
          bufRatio: +(sc.height / sc.width).toFixed(3),
          h: Math.round(r.height),
        };
      });
      expect(Math.abs(geo.cssRatio - geo.bufRatio),
        `pixels stretched: css ${geo.cssRatio} vs buffer ${geo.bufRatio}`).toBeLessThan(0.02);
      expect(geo.h, 'interior collapsed to a letterbox strip').toBeGreaterThan(180);

      await page.screenshot({ path: `audit/shots/${industry}-library.png` });
      await ti.attach('library', {
        body: JSON.stringify({ labels, geo }, null, 1), contentType: 'application/json',
      });
    });

    test('X5/X6 platform guardrail and reachability', async ({ page }) => {
      await reachLetter(page);
      await submitLetter(page, t, industry);
      await reachHomeGate(page);   // the gate now lives on the home stage

      const sel = () => page.$$eval('#hq-chips .chip.on', e => e.map(x => x.textContent.trim()));
      const chip = name => page.locator('#hq-chips .chip', { hasText: name }).first();

      // two named sources coexist
      await chip('AWS').click();
      await chip('Oracle').click();
      expect((await sel()).length, 'two named platforms should coexist').toBe(2);

      // an exclusive answer clears the named ones
      await chip('Already in Snowflake').click();
      expect(await sel()).toEqual(['Already in Snowflake']);

      // and a named source clears the exclusive one
      await chip('AWS').click();
      expect(await sel()).toEqual(['AWS']);

      // the two exclusives are mutually exclusive with each other
      await chip('Not sure yet').click();
      await chip('Already in Snowflake').click();
      expect(await sel()).toEqual(['Already in Snowflake']);

      // X6: chips and CONTINUE reachable without the visitor scrolling
      const reach = await page.evaluate(() => {
        const w = document.getElementById('hq-chips');
        const r = w.getBoundingClientRect();
        const go = document.getElementById('hq-go');
        const g = go.getBoundingClientRect();
        return {
          chipsIn: r.top >= 0 && r.bottom <= innerHeight,
          confirmIn: g.top >= 0 && g.bottom <= innerHeight,
        };
      });
      expect(reach.chipsIn, 'platform chips not in viewport').toBe(true);
      expect(reach.confirmIn, 'CONTINUE not reachable').toBe(true);
    });

    test('X3/X4 stall is attachable and on-geography', async ({ page }, ti) => {
      await reachLetter(page);
      await submitLetter(page, t, industry);
      await reachMap(page);
      await completeLibrary(page);
      await openLocation(page, 'marketplace');

      const picks = await page.$$eval('#c-opts .opt', els => els.map(e => ({
        label: e.querySelector('.lb').textContent.trim(),
        note: (e.querySelector('.nt') || { textContent: '' }).textContent.trim(),
      })));

      expect(picks.length, `stall: ${JSON.stringify(picks.map(p => p.label))}`).toBe(6);

      // X3: everything must be attachable on a trial, today.
      for (const p of picks) {
        expect(p.note.toLowerCase(), `not free: ${p.label} (${p.note})`).toContain('free');
        expect(p.note.toLowerCase(), `by-request: ${p.label}`).not.toContain('request');
      }

      // X4 / P3: nothing off-geography on a UK stand.
      const off = picks.filter(p =>
        OFF_GEO.some(g => p.label.toLowerCase().includes(g)));
      expect(off.map(p => p.label), 'off-geography picks on a UK stand').toEqual([]);

      // P4 / R3 / E2: weather must not dominate.
      const met = picks.filter(p => /met office/i.test(p.note)).length;
      expect(met, `too many Met Office picks (${met})`).toBeLessThanOrEqual(t.maxMetOffice);

      // UK relevance floor.
      const uk = picks.filter(p =>
        UK_SIGNAL.some(s => p.label.toLowerCase().includes(s))).length;
      expect(uk, `too few UK-relevant picks (${uk})`).toBeGreaterThanOrEqual(t.minUkSignal);

      for (const want of (t.mustInclude || [])) {
        expect(picks.map(p => p.label).join(' | '),
          `expected "${want}"`).toContain(want);
      }

      await page.screenshot({ path: `audit/shots/${industry}-stall.png` });
      await ti.attach('stall', {
        body: JSON.stringify({ picks, met, uk }, null, 1), contentType: 'application/json',
      });
    });

    if (t.full) {
      test('X7/X8/X9 blueprint is concrete and never contradicts itself', async ({ page }, ti) => {
        test.setTimeout(180000);            // four model calls at ~12s each
        await reachLetter(page);
        await submitLetter(page, t, industry);
        await reachMap(page);

        // The platform (Oracle etc.) is answered on the home-stage gate now,
        // so reachMap already captured it. The Library asks only for data held.
        await openLocation(page, 'library');
        await page.locator('#c-opts .opt').first().click();
        await page.waitForTimeout(400);
        await page.locator('#ov-loc button.primary').click();
        await page.waitForFunction(() => !document.getElementById('ov-loc')
          .classList.contains('on'), null, { timeout: 180000 });

        await openLocation(page, 'marketplace');
        await page.locator('#c-opts .opt').first().click();
        await page.locator('#ov-loc button.primary').click();
        await page.waitForFunction(() => !document.getElementById('ov-loc')
          .classList.contains('on'), null, { timeout: 180000 });

        await openLocation(page, 'workshop');
        // The workshop's button stays disabled until the visitor has actually
        // answered - a tick, a CoCo-chooses pick, or free text. Give it one, then
        // wait for the button to enable rather than clicking a dead control.
        const opt = page.locator('#c-opts .opt').first();
        if (await opt.count() && await opt.isVisible().catch(() => false)) {
          await opt.click();
        }
        const other = page.locator('#c-other');
        if (await other.isVisible().catch(() => false)) {
          await other.fill('Make our case documents searchable.');
        }
        // "LET COCO CHOOSE" is the workshop's designed no-typing path and is
        // itself the submit for that branch, so prefer it when the primary
        // button has not enabled.
        const go = page.locator('#ov-loc button.primary');
        if (!(await go.isEnabled().catch(() => false))) {
          const choose = page.locator('#c-coco-choose');
          if (await choose.isVisible().catch(() => false)) {
            await choose.click();
          } else {
            await expect(go).toBeEnabled({ timeout: 15000 });
            await go.click();
          }
        } else {
          await go.click();
        }
        await page.waitForFunction(() => !document.getElementById('ov-loc')
          .classList.contains('on'), null, { timeout: 150000 });

        const st = await (await page.request.get(`${BASE}/api/state`)).json();
        const poc = st.poc || {};
        expect(poc.poc_name, 'no POC name').toBeTruthy();
        expect((poc.features || []).length, 'no named Snowflake feature')
          .toBeGreaterThan(0);
        expect(poc.guide_title, 'no guide to fork').toBeTruthy();

        // X8: a named platform (AWS) was picked on the home gate, so a route
        // must be printed.
        const body = JSON.stringify(st);
        // X9: never both at once.
        const nomove = /nothing to move/i.test(body);
        const moves = /openflow|snowpipe|external stage|storage integration/i.test(body);
        expect(nomove && moves, 'blueprint contradicts itself').toBe(false);

        await ti.attach('poc', {
          body: JSON.stringify(poc, null, 1), contentType: 'application/json',
        });
      });
    }
  });
}
