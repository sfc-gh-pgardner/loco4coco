// Does the board below the bubble hold still while the bubble itself breathes?
//
// The complaint this answers: "both the interior location and map still move
// around based on the text box changing size". So we do not measure the bubble's
// height in isolation, we measure the TOP OF THE CANVAS in every state the
// bubble can be in. If that number moves, the visitor sees the board jump.
//
// Updated 2026-09-22 for #bubbleslot. The bubble no longer has a fixed height -
// pinning it left almost every reply in a box with visible dead space inside the
// border. The slot reserves the worst case instead, so the contract is now:
//   slot height CONSTANT, hud height CONSTANT, canvas top CONSTANT,
//   bubble height VARIES, and bubble <= slot always.
//
// Run: node audit/measure_fixed_bubble.js [width] [height]
const { chromium } = require('playwright');

const W = parseInt(process.argv[2] || '1440', 10);
const H = parseInt(process.argv[3] || '900', 10);

const SHORT = 'Right then.';
const FOUR  = 'Snowflake Marketplace gives you live, governed data that never needs a pipeline, '
            + 'which means the dataset you query today is the same one the provider updates '
            + 'tomorrow, with no copy to reconcile and no schedule to babysit at all.';
const LONG  = FOUR + ' ' + FOUR + ' ' + FOUR;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  // NOT networkidle: the client polls the server continuously, so the network
  // never goes idle and the navigation would time out.
  await p.goto('http://localhost:4747/', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(1800);

  // FREEZE THE RENDER LOOP. render() calls setMessage() with the server's current
  // message on every animation frame, so an injected test message is reverted
  // within one frame and every state below would measure the same thing.
  // Replacing requestAnimationFrame breaks the loop's self-rescheduling chain.
  await p.evaluate(() => {
    window.requestAnimationFrame = () => 0;
    // The poll interval also pushes the server's message back in, which reverts an
    // injected one and cancels its pending advance. Both clocks have to stop.
    for (let i = 1; i < 5000; i++) clearInterval(i);
  });
  await p.waitForTimeout(200);

  const probe = async (label, setup) => {
    // Invoke the setup explicitly. A bare "() => {...}" string is evaluated as an
    // expression that merely YIELDS a function, so the setup never ran and every
    // state silently measured the same untouched page.
    await p.evaluate(`(${setup})()`);
    await p.waitForTimeout(250);
    const m = await p.evaluate(`(() => {
      const bub = document.getElementById('bubble');
      const slot = document.getElementById('bubbleslot');
      const hud = document.getElementById('hud');
      const cv = document.getElementById('cv');
      const r = cv ? cv.getBoundingClientRect() : null;
      return {
        bubble: bub ? bub.offsetHeight : null,
        slot: slot ? slot.offsetHeight : null,
        hud: hud ? hud.offsetHeight : null,
        cvTop: r ? Math.round(r.top) : null,
        cvBottom: r ? Math.round(r.bottom) : null,
        viewport: window.innerHeight,
        pages: pages.length,
        pageI: pageI,
        chars: msgSource.length,
      };
    })()`);
    console.log(
      String(label).padEnd(34),
      'bubble=' + String(m.bubble).padStart(4),
      'slot=' + String(m.slot).padStart(4),
      'cvTop=' + String(m.cvTop).padStart(5),
      'cvBottom=' + String(m.cvBottom).padStart(5),
      'vh=' + m.viewport,
      'page=' + m.pageI + '/' + m.pages
    );
    return m;
  };

  const rows = [];
  rows.push(await probe('short reply', `() => {
    document.getElementById('yousaid').classList.remove('on');
    document.getElementById('histback').classList.remove('on');
    setMessage(${JSON.stringify(SHORT)}, true);
  }`));

  rows.push(await probe('four-line reply', `() => setMessage(${JSON.stringify(FOUR)}, true)`));

  // The REAL arrival path: a reply that types itself out. With the loop frozen we
  // pump stepType() ourselves, so the advance is scheduled by the same code that
  // schedules it at the booth rather than by the instant/recall shortcut.
  rows.push(await probe('multi-page, page 1 (typed)', `() => {
    setMessage(${JSON.stringify(LONG)}, false);
    for (let i = 0; i < 4000 && typeI < typeTarget.length; i++) stepType();
  }`));

  // Let the auto-advance carry it forward on its own - no click.
  const before = await p.evaluate("pageI");
  await p.waitForTimeout(9500);
  const after = await p.evaluate("pageI");
  rows.push(await probe('multi-page, after auto-advance', `() => {}`));
  console.log('\nauto-advance: page ' + before + ' -> ' + after +
              (after > before ? '  ADVANCED WITHOUT A CLICK' : '  DID NOT ADVANCE'));

  rows.push(await probe('with "you said" shown', `() => {
    const y = document.getElementById('yousaid');
    y.textContent = 'You said: Banking Analytics Bundle, Snowflake Public Data: Foreign Exchange Rates, and more';
    y.classList.add('on');
  }`));

  rows.push(await probe('with history line shown', `() => {
    const h = document.getElementById('histback');
    h.textContent = 'Viewing an earlier answer';
    h.classList.add('on');
  }`));

  rows.push(await probe('back to short reply', `() => setMessage(${JSON.stringify(SHORT)}, true)`));

  const tops = [...new Set(rows.map(r => r.cvTop))];
  const hs = [...new Set(rows.map(r => r.bubble))];
  const slots = [...new Set(rows.map(r => r.slot))];
  const huds = [...new Set(rows.map(r => r.hud))];
  console.log('\ndistinct bubble heights: ' + JSON.stringify(hs));
  console.log('distinct slot heights  : ' + JSON.stringify(slots));
  console.log('distinct hud heights   : ' + JSON.stringify(huds));
  console.log('distinct canvas tops   : ' + JSON.stringify(tops));

  // The bubble must never be taller than the slot that reserves it: if it were,
  // the overflow would push the board down and the reservation would be a lie.
  const overflow = rows.filter(r => r.bubble > r.slot);
  const clipped = rows.filter(r => r.cvBottom > r.viewport);
  console.log('\n' + (tops.length === 1 ? 'PASS' : 'FAIL') + ' board position constant');
  console.log((slots.length === 1 ? 'PASS' : 'FAIL') + ' slot height constant');
  console.log((huds.length === 1 ? 'PASS' : 'FAIL') + ' hud row height constant');
  // Inverted deliberately on 2026-09-22. A constant bubble height used to be the
  // requirement; it is now the bug. The bubble is supposed to hug its text, so a
  // single distinct height across a one-line reply and a four-line one would
  // mean the box is padded with dead space again - the thing the slot exists to
  // move outside the border.
  console.log((hs.length > 1 ? 'PASS' : 'FAIL')
              + ' bubble height tracks its content');
  console.log((overflow.length === 0 ? 'PASS' : 'FAIL') + ' bubble fits its slot'
              + (overflow.length ? ' (worst ' +
                  Math.max(...overflow.map(r => r.bubble - r.slot)) + 'px over)' : ''));
  console.log((clipped.length === 0 ? 'PASS' : 'FAIL') + ' board bottom edge on screen'
              + (clipped.length ? ' (worst overrun ' +
                  Math.max(...clipped.map(r => r.cvBottom - r.viewport)) + 'px)' : ''));
  console.log((after > before ? 'PASS' : 'FAIL') + ' pages advance with no click');
  if (errs.length) console.log('\nJS ERRORS:\n' + errs.join('\n'));

  await b.close();
  process.exit(tops.length === 1 && slots.length === 1 && huds.length === 1
               && hs.length > 1 && !overflow.length && !clipped.length
               && after > before && !errs.length ? 0 : 1);
})();
