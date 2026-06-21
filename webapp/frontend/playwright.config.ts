import { defineConfig } from '@playwright/test';
export default defineConfig({
    testDir: './e2e', timeout: 60000, retries: 1,
    use: { baseURL: 'http://localhost:10772', headless: true, screenshot: 'only-on-failure' },
    webServer: {
        command: 'uv run python -m gimp_mcp.server --port 10773',
        port: 10773, timeout: 30000, reuseExistingServer: false
    }
});
