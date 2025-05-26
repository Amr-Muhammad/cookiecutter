import { defineConfig, devices } from "@playwright/test";
import { config } from "@tests/config";

export default defineConfig({
    testDir: "./tests",
    use: config,
    projects: [
        { name: "core", testMatch: /.*\/core\/auth\.setup\.ts$/ },
        {
            name: "chromium",
            use: { ...devices["Desktop Chrome"] },
            dependencies: ["core"],
        },
        {
            name: "firefox",
            use: { ...devices["Desktop Firefox"] },
            dependencies: ["core"],
        },
    ],
});
