import os
import json
import subprocess

TESTS_DIR = "tests"
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")
MODULES_DIR = os.path.join(TESTS_DIR, "modules")
STORIES_DIR = os.path.join(TESTS_DIR, "stories")
PACKAGE_JSON = "package.json"

os.makedirs(FIXTURES_DIR, exist_ok=True)
os.makedirs(MODULES_DIR, exist_ok=True)
os.makedirs(STORIES_DIR, exist_ok=True)

package_manager = "{{cookiecutter.package_manager}}".strip().lower()

print(f"📦 Selected package manager: {package_manager}")

print("📦 Installing Playwright...")

if package_manager == "yarn":
    subprocess.run(["yarn", "add", "-D", "playwright"], check=True)
    subprocess.run(["yarn", "playwright", "install"], check=True)
else:
    subprocess.run(["npm", "install", "--save-dev", "playwright"], check=True)
    subprocess.run(["npx", "playwright", "install"], check=True)

if os.path.exists(PACKAGE_JSON):
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        package_data = json.load(f)

    if "scripts" not in package_data:
        package_data["scripts"] = {}

    playwright_scripts = {
        "e2e": "playwright test",
        "e2e:debug:chromium": "playwright test --project chromium --headed",
        "e2e:debug:firefox": "playwright test --project firefox --headed"
    }

    package_data["scripts"].update({k: v for k, v in playwright_scripts.items() if k not in package_data["scripts"]})

    with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(package_data, f, indent=2)

    print("✅ Playwright scripts added to package.json")
else:
    print("⚠️ No package.json found! Please add the scripts manually.")

print("🎭 Playwright setup complete!")
