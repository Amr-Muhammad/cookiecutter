import { test as setup } from '@playwright/test';
import { LoginModule } from '@tests/components/auth/login';
import { getFile } from '@tests/core';
import { config } from '@tests/config';

const applicantFile = getFile('../.auth/user_type.json');
setup('authenticate as user type', async ({ page }) => {
    const loginModule = new LoginModule(page);

    const email = config.applicantEmail!;
    const password = config.applicantPassword!;

    await loginModule.login(email, password);
    await page.context().storageState({ path: applicantFile });
});
