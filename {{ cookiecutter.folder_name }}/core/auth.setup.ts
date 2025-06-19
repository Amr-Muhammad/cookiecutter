import { test as setup } from '@playwright/test';
import { config } from '@tests/config';
import { chromium } from '@playwright/test';
import { LoginModule } from '@tests/components/auth/login';
import fs from 'fs';

let roles = Object.keys(config.credentials.users);
// Chnage that for ur project
let navigationPathAfterLogin = '**/dashboard/home';
setup('Setup User Session', async () => {
    for (const role of roles) {
        let storagePath = `tests/.auth/${role}-session.json`;
        if (fs.existsSync(storagePath)) return;

        let loginPath: any = role.toLowerCase().includes('admin') ? config.paths.adminLoginPath : config.paths.normalUserLoginPath;
        let email: any = config.credentials.users[role].email;
        let password: any = config.credentials.users[role].password;

        const browser = await chromium.launch();
        const page = await browser.newPage();
        const loginModule = new LoginModule(page);

        await loginModule.goToLoginPage(loginPath);
        await loginModule.loginWithCredentials(email, password);
        await loginModule.enterOTPAndVerify(navigationPathAfterLogin);

        await page.context().storageState({ path: storagePath });
        await browser.close();
    }
});