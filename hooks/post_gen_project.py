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

npm_path = shutil.which("npm")
npx_path = shutil.which("npx")
yarn_path = shutil.which("yarn")

def run_safe(cmd, cwd):
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except FileNotFoundError:
        print(f"❌ Command not found: {' '.join(cmd)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}\nError: {e}")

# Install dependencies
if package_manager == "yarn":
    if yarn_path:
        run_safe([yarn_path, "add", "-D", "playwright"], cwd=ROOT_DIR)
        run_safe([yarn_path, "playwright", "install"], cwd=ROOT_DIR)
        run_safe([yarn_path, "add", "-D", "@playwright/test"], cwd=ROOT_DIR)
    else:
        print("❌ Yarn not found in PATH.")
else:
    if npm_path and npx_path:
        run_safe([npm_path, "install", "--save-dev", "playwright"], cwd=ROOT_DIR)
        run_safe([npx_path, "playwright", "install"], cwd=ROOT_DIR)
        run_safe([npm_path, "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR)
    else:
        print("❌ npm or npx not found in PATH. Please install Node.js and try again.")

# Add Playwright scripts to package.json
def ensure_package_scripts():
    if not os.path.exists(PACKAGE_JSON):
        print("⚠️ No package.json found! Add the Playwright scripts manually.")
        return

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

        updated = False
        for k, v in playwright_scripts.items():
            if k not in package_data["scripts"]:
                package_data["scripts"][k] = v
                updated = True

        if updated:
            with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
                json.dump(package_data, f, indent=2)
            print("✅ Playwright scripts added to package.json")
        else:
            print("✅ package.json already contains Playwright scripts.")
    except Exception as e:
        print(f"❌ Failed to update package.json: {e}")

# Ensure tsconfig.json is valid and updated
def ensure_tsconfig(tsconfig_path):
    default_paths = {
        "@tests/*": ["./tests/*"],
        "@tests/config": ["./tests/config.ts"]
    }

    default_compiler_options = {
        "target": "esnext",
        "module": "commonjs",
        "baseUrl": "./",
        "paths": default_paths
    }

    default_tsconfig = {
        "compilerOptions": default_compiler_options
    }

    if not os.path.exists(tsconfig_path):
        print("⚠️ No tsconfig.json found. Creating a new one...")
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(default_tsconfig, f, indent=2)
        print("✅ tsconfig.json created with default settings.")
        return

    try:
        with open(tsconfig_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            tsconfig = json.loads(content) if content else {}
    except Exception as e:
        print(f"❌ tsconfig.json exists but is invalid. Resetting file. Error: {e}")
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(default_tsconfig, f, indent=2)
        print("✅ tsconfig.json reset with default settings.")
        return

    if "compilerOptions" not in tsconfig:
        tsconfig["compilerOptions"] = {}

    compiler_options = tsconfig["compilerOptions"]
    updated = False

    for key, value in default_compiler_options.items():
        if key == "paths":
            if "paths" not in compiler_options:
                compiler_options["paths"] = {}
                updated = True

            for path_key, path_value in default_paths.items():
                if path_key not in compiler_options["paths"]:
                    compiler_options["paths"][path_key] = path_value
                    updated = True
        elif key not in compiler_options:
            compiler_options[key] = value
            updated = True

    if updated:
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)
        print("✅ tsconfig.json updated with missing fields.")
    else:
        print("✅ tsconfig.json already has all required fields.")

# Write Playwright config
def write_playwright_config():
    try:
        with open(PLAYWRIGHT_CONFIG, "w", encoding="utf-8") as f:
            f.write(playwright_config_content + "\n")
        print("🎭 playwright.config.ts generated successfully.")
    except Exception as e:
        print(f"❌ Failed to create playwright.config.ts: {e}")

# Run setup
ensure_package_scripts()
ensure_tsconfig(TSCONFIG)
write_playwright_config()
print("✅ Playwright setup complete!")
