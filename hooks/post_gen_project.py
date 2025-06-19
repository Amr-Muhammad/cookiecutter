# hooks/post_gen_project.py

import os
import json
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.getcwd())
FOLDER = "{{ cookiecutter.folder_name }}".strip()
CONFIG_TS = os.path.join(ROOT_DIR, FOLDER, "config.ts")
PACKAGE_JSON = os.path.join(ROOT_DIR, "package.json")
TSCONFIG = os.path.join(ROOT_DIR, "tsconfig.json")
PLAYWRIGHT_CONFIG = os.path.join(ROOT_DIR, "playwright.config.ts")

# 1. Generate config.ts with roles
def gen_config():
    define = input("Define project roles? (yes/no) [yes]: ").strip().lower() or "yes"
    entries = {}
    if define == "yes":
        print("Enter each role (press Enter to finish):")
        while True:
            role = input("- Role: ").strip()
            if not role:
                break
            entries[role] = {}

    lines = "\n".join(f'        "{r}": {{ email: "", password: "" }}' for r in entries) or "      // no roles defined"
    content = f"""export const config = {{
  credentials: {{
    users: {{
{lines}
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
    print("✅ config.ts generated.")

# 2. Install Playwright + patch scripts, tsconfig, config file
def setup_playwright():
    pkg = shutil.which

    pm = "{{ cookiecutter.package_manager }}".strip().lower()
    npm_path = pkg("npm"); npx_path = pkg("npx"); yarn_path = pkg("yarn")

    declared = {}
    if os.path.exists(PACKAGE_JSON):
        with open(PACKAGE_JSON) as f:
            declared = json.load(f).get("devDependencies", {})

    def run(cmd): subprocess.run(cmd, cwd=ROOT_DIR, check=True)
    if pm == "yarn" and yarn_path:
        if "playwright" not in declared:
            run([yarn_path, "add", "-D", "playwright"])
            run([yarn_path, "playwright", "install"])
        if "@playwright/test" not in declared:
            run([yarn_path, "add", "-D", "@playwright/test"])
    elif npm_path and npx_path:
        if "playwright" not in declared:
            run([npm_path, "install", "--save-dev", "playwright"])
            run([npx_path, "playwright", "install"])
        if "@playwright/test" not in declared:
            run([npm_path, "install", "--save-dev", "@playwright/test"])

    # patch package.json scripts
    if os.path.exists(PACKAGE_JSON):
        with open(PACKAGE_JSON, "r+") as f:
            pkgdata = json.load(f)
            s = pkgdata.setdefault("scripts", {})
            for k, v in {
                "e2e": "playwright test",
                "e2e:ui": "playwright test --ui",
                "e2e:debug:chromium": "playwright test --project chromium --headed",
                "e2e:debug:firefox": "playwright test --project firefox --headed",
            }.items():
                s.setdefault(k, v)
            f.seek(0); json.dump(pkgdata, f, indent=2); f.truncate()
        print("✅ Scripts patched.")

    # patch tsconfig paths
    if os.path.exists(TSCONFIG):
        try:
            with open(TSCONFIG) as f:
                cfg = json.load(f)
            pc = cfg.setdefault("compilerOptions", {}).setdefault("paths", {})
            pc.setdefault("@tests/*", ["./tests/*"])
            pc.setdefault("@tests/config", ["./tests/config.ts"])
            with open(TSCONFIG, "w") as f:
                json.dump(cfg, f, indent=2)
            print("✅ tsconfig paths updated.")
        except Exception as e:
            print("⚠️ tsconfig patch skipped:", e)

    # generate playwright.config.ts
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
        print("✅ playwright.config.ts created.")

def main():
    gen_config()
    setup_playwright()
    print("✅ All done")

if __name__ == "__main__":
    main()
