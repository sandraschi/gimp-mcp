import { expect, test } from "@playwright/test";

const BE = "http://127.0.0.1:10773";
const _FE = "http://127.0.0.1:10772";

test.describe("Fleet Audit", () => {
  test("Backend health", async ({ request }) => {
    const resp = await request.get(`${BE}/health`);
    expect(resp.status()).toBe(200);
  });
});
