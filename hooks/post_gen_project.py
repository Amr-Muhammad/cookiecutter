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

npm_path = shutil.which("npm")
npx_path = shutil.which("npx")
yarn_path = shutil.which("yarn")

print(f"📦 Selected package manager: {package_manager}")
print("📦 Installing Playwright...")
if package_manager == "yarn":
    subprocess.run([yarn_path, "add", "-D", "playwright"], cwd=ROOT_DIR, check=True)
    subprocess.run([yarn_path, "playwright", "install"], cwd=ROOT_DIR, check=True)
    subprocess.run([yarn_path, "add", "-D", "@playwright/test"], cwd=ROOT_DIR, check=True)
else:
    if npm_path and npx_path:
        subprocess.run([npm_path, "install", "--save-dev", "playwright"], cwd=ROOT_DIR, check=True)
        subprocess.run([npx_path, "playwright", "install"], cwd=ROOT_DIR, check=True)
        subprocess.run([npm_path, "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR, check=True)
        print("npm or npx are found in PATH successfully.")
    else:
        print("❌ npm or npx not found in PATH. Please install Node.js and try again.")

if os.path.exists(PACKAGE_JSON):
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
        {
            k: v
            for k, v in playwright_scripts.items()
            if k not in package_data["scripts"]
        }
    )

    with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(package_data, f, indent=2)

    print("✅ Playwright scripts added to package.json")
else:
    print("""
          ⚠️  No package.json found in the root directory! Please add the scripts manually. ⚠️
          
            "e2e": "playwright test",
            "e2e:ui": "playwright test --ui",
            "e2e:debug:chromium": "playwright test --project chromium --headed",
            "e2e:debug:firefox": "playwright test --project firefox --headed"
          """)


if os.path.exists(TSCONFIG):
    print("📝 Found tsconfig.json, updating paths...")
    try:
        with open(TSCONFIG, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Skip leading comments or blank lines
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
            print("❌ tsconfig.json is empty or only contains comments. Skipping update.")
        else:
            tsconfig = json.loads(json_content)

            if "compilerOptions" not in tsconfig:
                tsconfig["compilerOptions"] = {}

            if "paths" not in tsconfig["compilerOptions"]:
                tsconfig["compilerOptions"]["paths"] = {}

            paths = tsconfig["compilerOptions"]["paths"]

            # Only add missing keys
            if "@tests/*" not in paths:
                paths["@tests/*"] = ["./tests/*"]
            if "@tests/config" not in paths:
                paths["@tests/config"] = ["./tests/config.ts"]

            with open(TSCONFIG, "w", encoding="utf-8") as f:
                json.dump(tsconfig, f, indent=2)

            print("✅ Successfully updated tsconfig.json with paths.")

    except Exception as e:
        print("❌ Failed to update tsconfig.json. Add manually if needed.")
        print(f"Error: {e}")
        print("""
                "paths": {
                    ...current_paths...
                    "@tests/*": ["./tests/*"],
                    "@tests/config": ["./tests/config.ts"]
                },
        """)
else:
    print("""
           ⚠️  No tsconfig.json found, Add path updates manually. ⚠️
          
            "paths": {
                ...current_paths...
                "@tests/*": ["./tests/*"],
                "@tests/config": ["./tests/config.ts"]
            },
    """)

with open(PLAYWRIGHT_CONFIG, "w", encoding="utf-8") as f:
    f.write(playwright_config_content + "\n")

print("🎭 Playwright setup complete!")
