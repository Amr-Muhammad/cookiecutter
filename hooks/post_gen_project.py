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
    {
      name: "core",
      testMatch: /.*\\/core\\/auth\\.setup\\.ts$/
    },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["core"]
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      dependencies: ["core"]
    }
  ]
});
""".strip()

package_manager = "{{ cookiecutter.package_manager }}".strip().lower()

npm_path = shutil.which("npm")
npx_path = shutil.which("npx")
yarn_path = shutil.which("yarn")

playwright_declared = False
playwright_test_declared = False

print(f"📦 Selected package manager: {package_manager}")

if os.path.exists(PACKAGE_JSON):
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        package_data = json.load(f)
        dev_deps = package_data.get("devDependencies", {})
        playwright_declared = "playwright" in dev_deps
        playwright_test_declared = "@playwright/test" in dev_deps

if package_manager == "yarn":
    if yarn_path:
        if not playwright_declared:
            subprocess.run([yarn_path, "add", "-D", "playwright"], cwd=ROOT_DIR, check=True)
            subprocess.run([yarn_path, "playwright", "install"], cwd=ROOT_DIR, check=True)
        if not playwright_test_declared:
            subprocess.run([yarn_path, "add", "-D", "@playwright/test"], cwd=ROOT_DIR, check=True)
    else:
        print("❌ Yarn not found.")
else:
    if npm_path and npx_path:
        if not playwright_declared:
            subprocess.run([npm_path, "install", "--save-dev", "playwright"], cwd=ROOT_DIR, check=True)
            subprocess.run([npx_path, "playwright", "install"], cwd=ROOT_DIR, check=True)
        if not playwright_test_declared:
            subprocess.run([npm_path, "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR, check=True)
    else:
        print("❌ npm or npx not found. Please install Node.js.")

# ✅ patch package.json scripts
if os.path.exists(PACKAGE_JSON):
    with open(PACKAGE_JSON, "r+", encoding="utf-8") as f:
        package_data = json.load(f)
        s = package_data.setdefault("scripts", {})
        for k, v in {
            "e2e": "playwright test",
            "e2e:ui": "playwright test --ui",
            "e2e:debug:chromium": "playwright test --project chromium --headed",
            "e2e:debug:firefox": "playwright test --project firefox --headed"
        }.items():
            s.setdefault(k, v)
        f.seek(0); json.dump(package_data, f, indent=2); f.truncate()
    print("✅ Scripts added to package.json.")

# ✅ patch tsconfig.json paths
if os.path.exists(TSCONFIG):
    try:
        with open(TSCONFIG, "r", encoding="utf-8") as f:
            lines = f.readlines()

        clean_lines = []
        start_collecting = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("{"):
                start_collecting = True
            if start_collecting:
                clean_lines.append(line)

        json_content = "".join(clean_lines).strip()
        if not json_content:
            print("❌ tsconfig.json is empty.")
        else:
            tsconfig = json.loads(json_content)
            if "compilerOptions" not in tsconfig:
                tsconfig["compilerOptions"] = {}
            if "paths" not in tsconfig["compilerOptions"]:
                tsconfig["compilerOptions"]["paths"] = {}

            paths = tsconfig["compilerOptions"]["paths"]
            paths.setdefault("@tests/*", ["./tests/*"])
            paths.setdefault("@tests/config", ["./tests/config.ts"])

            with open(TSCONFIG, "w", encoding="utf-8") as f:
                json.dump(tsconfig, f, indent=2)

            print("✅ tsconfig paths updated.")

    except Exception as e:
        print(f"❌ Failed to patch tsconfig.json: {e}")

# ✅ create playwright.config.ts if missing
if not os.path.exists(PLAYWRIGHT_CONFIG):
    with open(PLAYWRIGHT_CONFIG, "w", encoding="utf-8") as f:
        f.write(playwright_config_content + "\n")
    print("🎭 playwright.config.ts created.")
else:
    print("🎭 playwright.config.ts already exists.")

print("✅ Playwright setup complete!")
