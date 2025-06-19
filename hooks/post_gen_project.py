# hooks/post_gen_project.py
import os
import json
import subprocess
import shutil

# — Part 1: Dynamic config.ts generation —

ROOT_DIR = os.path.abspath(os.getcwd())
FOLDER = os.environ.get("COOKIECUTTER_folder_name", "tests")
CONFIG_TS = os.path.join(ROOT_DIR, FOLDER, "config.ts")

def gen_config():
    define = input("Define project roles? (yes/no) [yes]: ").strip().lower() or "yes"
    entries = {}
    if define == "yes":
        print("Enter roles, one per line (blank to finish):")
        while True:
            role = input("- Role: ").strip()
            if not role: break
            entries[role] = {"email": "", "password": ""}

    block = ",\n".join(
        f"    \"{r}\": {{ email: '', password: '' }}" for r in entries
    )
    content = f"""export const config = {{
  credentials: {{
    users: {{
{block or '    // no roles defined'}
  }}  
  }},
  paths: {{
    baseUrl: '',
    adminLoginPath: '',
    normalUserLoginPath: ''
  }}
}};
"""
    os.makedirs(os.path.dirname(CONFIG_TS), exist_ok=True)
    with open(CONFIG_TS, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ config.ts generated")

# — Part 2: Playwright installation & setup —

def setup_playwright():
    PACKAGE_JSON = os.path.join(ROOT_DIR, "package.json")
    TSCONFIG = os.path.join(ROOT_DIR, "tsconfig.json")
    PLAYWRIGHT_CONFIG = os.path.join(ROOT_DIR, "playwright.config.ts")

    npm = shutil.which("npm")
    npx = shutil.which("npx")
    yarn = shutil.which("yarn")
    pm = "{{ cookiecutter.package_manager }}".strip().lower()

    dev = {}
    if os.path.exists(PACKAGE_JSON):
        with open(PACKAGE_JSON) as f:
            dev = json.load(f).get("devDependencies", {})

    if pm == "yarn" and yarn:
        if "playwright" not in dev:
            subprocess.run([yarn, "add", "-D", "playwright"], cwd=ROOT_DIR, check=True)
            subprocess.run([yarn, "playwright", "install"], cwd=ROOT_DIR, check=True)
        if "@playwright/test" not in dev:
            subprocess.run([yarn, "add", "-D", "@playwright/test"], cwd=ROOT_DIR, check=True)
    elif npm and npx:
        if "playwright" not in dev:
            subprocess.run([npm, "install", "--save-dev", "playwright"], cwd=ROOT_DIR, check=True)
            subprocess.run([npx, "playwright", "install"], cwd=ROOT_DIR, check=True)
        if "@playwright/test" not in dev:
            subprocess.run([npm, "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR, check=True)

    # Add scripts
    if os.path.exists(PACKAGE_JSON):
        with open(PACKAGE_JSON, "r+") as f:
            data = json.load(f)
            scripts = data.setdefault("scripts", {})
            for k, v in {
                "e2e": "playwright test",
                "e2e:ui": "playwright test --ui",
                "e2e:debug:chromium": "playwright test --project chromium --headed",
                "e2e:debug:firefox": "playwright test --project firefox --headed",
            }.items():
                scripts.setdefault(k, v)
            f.seek(0); json.dump(data, f, indent=2); f.truncate()
        print("✅ Added scripts to package.json")

    # Patch tsconfig
    if os.path.exists(TSCONFIG):
        try:
            with open(TSCONFIG) as f:
                cfg = json.load(f)
            paths = cfg.setdefault("compilerOptions", {}).setdefault("paths", {})
            paths.setdefault("@tests/*", ["./tests/*"])
            paths.setdefault("@tests/config", ["./tests/config.ts"])
            with open(TSCONFIG, "w") as f:
                json.dump(cfg, f, indent=2)
            print("✅ Patched tsconfig paths")
        except Exception as e:
            print("⚠️ Skip tsconfig patch:", e)

    # Write playwright.config.ts if missing
    if not os.path.exists(PLAYWRIGHT_CONFIG):
        content = f"""import {{ defineConfig, devices }} from "@playwright/test";
import {{ config }} from "@tests/config";

export default defineConfig({{
  testDir: "./tests",
  use: config,
  projects: [
    {{ name: "core", testMatch: /.*\\/core\\/auth\\.setup\\.ts$/ }},
    {{ name: "chromium", use: {{ ...devices["Desktop Chrome"] }}, dependencies: ["core"] }},
    {{ name: "firefox", use: {{ ...devices["Desktop Firefox"] }}, dependencies: ["core"] }},
  ],
}});
"""
        with open(PLAYWRIGHT_CONFIG, "w") as f:
            f.write(content)
        print("✅ Created playwright.config.ts")

def main():
    gen_config()
    setup_playwright()

if __name__ == "__main__":
    main()
