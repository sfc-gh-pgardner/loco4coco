// Throwaway probe: WHICH child of the bubble grows when "you said" appears?
// measure_fixed_bubble.js reports the symptom (bubble 214 -> 220); this reports
// the cause, per child, so the fix lands on the right rule instead of the rule
// that looks guilty.
const { chromium } = require('playwright-core');

const KIDS = ['d-who', 'd-msg', 'd-more', 'yousaid', 'histback'];

function snap() {
  const out = {};
  const b = document.getElementById('bubble');
  out.bubble = b.offsetHeight;
  for (const id of ['d-who', 'd-msg', 'd-more', 'yousaid', 'histback']) {
    const e = document.getElementById(id);
    if (!e) { out[id] = 'absent'; continue; }
    const cs = getComputedStyle(e);
    out[id] = `h=${e.offsetHeight} mt=${cs.marginTop} pt=${cs.paddingTop}` +
              ` mh=${cs.minHeight} lh=${cs.lineHeight} fs=${cs.fontSize}`;
  }
  return out;
}

(async () => {
  const br = await chromium.launch();
  const p = await br.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('http://localhost:4747/', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(1800);
  // Same two clocks as the main harness: the render loop and the poll both push
  // the server's message back in and would revert anything injected here.
  await p.evaluate(() => {
    window.requestAnimationFrame = () => 0;
    for (let i = 1; i < 5000; i++) clearInterval(i);
  });

  const before = await p.evaluate(`(${snap})()`);
  await p.evaluate(() => {
    const y = document.getElementById('yousaid');
    y.classList.add('on');
    y.textContent = 'You said: we hold customer records and delivery telemetry';
  });
  const after = await p.evaluate(`(${snap})()`);

  for (const k of ['bubble', ...KIDS]) {
    const a = String(before[k]), b = String(after[k]);
    console.log(`${k.padEnd(9)} ${a === b ? 'same' : 'GREW'}`);
    console.log(`  before ${a}`);
    if (a !== b) console.log(`  after  ${b}`);
  }
  await br.close();
})();
