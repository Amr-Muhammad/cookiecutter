import { test as setup } from "@playwright/test";
import { LoginModule } from "@tests/components/auth/login";
import { getFile } from "@tests/core/config";

const applicantFile = getFile("../.auth/user_type.json");
setup("authenticate as user type", async ({ page }) => {
    const loginModule = new LoginModule(page);

    const email = process.env.USER_EMAIL_APPLICANT!;
    const password = process.env.USER_PASSWORD_APPLICANT!;

    await loginModule.login(email, password);
    await page.context().storageState({ path: applicantFile });
});
