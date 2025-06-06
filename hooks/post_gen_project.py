import os
import json
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
PACKAGE_JSON = os.path.join(ROOT_DIR, "package.json")
TSCONFIG = os.path.join(ROOT_DIR, "tsconfig.json")
PLAYWRIGHT_CONFIG = os.path.join(ROOT_DIR, "playwright.config.ts")

playwright_config_content = """
import { defineConfig, devices } from "@playwright/test";
import { config } from "@tests/config";

export default defineConfig({
    testDir: "./tests",
    use: config,
    projects: [
        { name: "core", testMatch: /.*\\/core\\/auth\\.setup\\.ts$/ },
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
""".strip()

package_manager = "{{ cookiecutter.package_manager }}".strip().lower()

print(f"📦 Selected package manager: {package_manager}")
print("📦 Installing Playwright...")

def run_safe(cmd, **kwargs):
    try:
        subprocess.run(cmd, check=True, **kwargs)
    except FileNotFoundError:
        print(f"❌ Command not found: {' '.join(cmd)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}\nError: {e}")

if package_manager == "yarn":
    run_safe(["yarn", "add", "-D", "playwright"], cwd=ROOT_DIR)
    run_safe(["yarn", "playwright", "install"], cwd=ROOT_DIR)
    run_safe(["yarn", "add", "-D", "@playwright/test"], cwd=ROOT_DIR)
else:
    run_safe(["npm", "install", "--save-dev", "playwright"], cwd=ROOT_DIR)
    run_safe(["npx", "playwright", "install"], cwd=ROOT_DIR)
    run_safe(["npm", "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR)

if os.path.exists(PACKAGE_JSON):
    try:
        with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
            package_data = json.load(f)

        if "scripts" not in package_data:
            package_data["scripts"] = {}

        playwright_scripts = {
            "e2e": "playwright test",
            "e2e:ui": "playwright test --ui",
            "e2e:debug:chromium": "playwright test --project chromium --headed",
            "e2e:debug:firefox": "playwright test --project firefox --headed",
        }

        package_data["scripts"].update(
            {k: v for k, v in playwright_scripts.items() if k not in package_data["scripts"]}
        )

        with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)

        print("✅ Playwright scripts added to package.json")
    except Exception as e:
        print(f"❌ Failed to update package.json: {e}")
else:
    print("⚠️ No package.json found! Add the Playwright scripts manually.")

if os.path.exists(TSCONFIG):
    print("📝 Found tsconfig.json, updating paths...")
    try:
        with open(TSCONFIG, "r", encoding="utf-8") as f:
            tsconfig = json.load(f)

        if "compilerOptions" not in tsconfig:
            tsconfig["compilerOptions"] = {}

        if "paths" not in tsconfig["compilerOptions"]:
            tsconfig["compilerOptions"]["paths"] = {}

        tsconfig["compilerOptions"]["paths"]["@tests/*"] = ["./tests/*"]
        tsconfig["compilerOptions"]["paths"]["@tests/config"] = ["./tests/config.ts"]

        with open(TSCONFIG, "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)

        print("✅ Successfully updated tsconfig.json with paths.")
    except Exception as e:
        print(f"❌ Failed to update tsconfig.json: {e}")
else:
    print("⚠️ No tsconfig.json found. Add path updates manually.")

try:
    with open(PLAYWRIGHT_CONFIG, "w", encoding="utf-8") as f:
        f.write(playwright_config_content + "\n")
    print("🎭 playwright.config.ts generated successfully.")
except Exception as e:
    print(f"❌ Failed to create playwright.config.ts: {e}")

print("✅ Playwright setup complete!")
