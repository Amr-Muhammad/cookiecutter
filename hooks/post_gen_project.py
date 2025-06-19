import osAdd commentMore actions
import json
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
PACKAGE_JSON = os.path.join(ROOT_DIR, "package.json")
@@ -32,21 +33,52 @@

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
            print("📦 Installing Playwright...")
        else:
            print("🎭 Playwright already declared in package.json. Skipping install.")
        if not playwright_test_declared:
            subprocess.run([yarn_path, "add", "-D", "@playwright/test"], cwd=ROOT_DIR, check=True)
            print("📦 Installing Playwright tests...")
        else:
            print("✅ @playwright/test already declared. Skipping install.")
    else:
        print("❌ Yarn not found in PATH.")
else:
    if npm_path and npx_path:
        if not playwright_declared:
            subprocess.run([npm_path, "install", "--save-dev", "playwright"], cwd=ROOT_DIR, check=True)
            subprocess.run([npx_path, "playwright", "install"], cwd=ROOT_DIR, check=True)
            print("📦 Installing Playwright...")
        else:
            print("🎭 Playwright already declared in package.json. Skipping install.")
        if not playwright_test_declared:
            subprocess.run([npm_path, "install", "--save-dev", "@playwright/test"], cwd=ROOT_DIR, check=True)
            print("📦 Installing Playwright tests...")
        else:
            print("✅ @playwright/test already declared. Skipping install.")
    else:
        print("❌ npm or npx not found in PATH. Please install Node.js and try again.")

if os.path.exists(PACKAGE_JSON):
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
@@ -89,46 +121,69 @@
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

if not os.path.exists(PLAYWRIGHT_CONFIG):
    with open(PLAYWRIGHT_CONFIG, "w", encoding="utf-8") as f:
        f.write(playwright_config_content + "\n")
    print("🎭 playwright.config.ts generated successfully.")
else:
    print("🎭 playwright.config.ts already exists. Skipping creation.")

print("✅ Playwright setup complete!")
