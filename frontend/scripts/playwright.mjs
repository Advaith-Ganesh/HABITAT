// Use one absolute cache path for installation and execution, regardless of npm's cwd.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const browsers = fileURLToPath(new URL('../../.test-runtime/ms-playwright', import.meta.url));
const cli = fileURLToPath(new URL('../node_modules/playwright/cli.js', import.meta.url));
const result = spawnSync(process.execPath, [cli, ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: {...process.env, PLAYWRIGHT_BROWSERS_PATH: process.env.PLAYWRIGHT_BROWSERS_PATH || browsers},
});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
