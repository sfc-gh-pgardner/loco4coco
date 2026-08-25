// Real Chromium, one project per industry track.
//
// Deliberately serial with a single worker: the server holds ONE visitor in
// state.json per process, so parallel tracks would overwrite each other's
// visitor and every assertion would be against the wrong industry. This is the
// single most important line in this file.

const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './playwright',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 120000,
  expect: { timeout: 10000 },
  reporter: [['list'], ['json', { outputFile: 'results.json' }]],
  use: {
    baseURL: 'http://127.0.0.1:4747',
    browserName: 'chromium',
    headless: true,
    // A realistic booth laptop. The interior aspect ratio and the
    // "is CONFIRM reachable" checks are viewport-sensitive, so this is part of
    // the assertion, not a convenience.
    viewport: { width: 1512, height: 800 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'off',
  },
});
