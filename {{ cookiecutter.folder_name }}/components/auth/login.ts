import { Locator, Page, expect } from '@playwright/test';

export class LoginModule {

    readonly page: Page;

    // Fields
    readonly email: Locator;
    readonly password: Locator;
    readonly otpCode: Locator;

    // Interactive
    readonly loginButton: Locator;
    readonly verifyOTOButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.email = page.getByTestId('userName');
        this.password = page.getByTestId('userPassword');
        this.loginButton = page.getByTestId('login');
        this.verifyOTOButton = this.page.getByTestId('verifyOtp');
        this.otpCode = this.page.getByTestId('otpCode')
    }

    async goToLoginPage(loginPath: string) {
        await this.page.goto(loginPath);
    }

    async loginWithCredentials(email: string, password: string) {
        await this.email.fill(email);
        await this.password.fill(password);
        await this.loginButton.click();
    }

    async enterOTPAndVerify(navigationPathAfterLogin: string) {
        const otpText = await this.otpCode.textContent();
        const otp = otpText?.trim() ?? '';
        expect(otp.length).toBe(5);

        for (let i = 0; i < otp.length; i++) {
            await this.page.fill(`[data-testid="otp${i + 1}"]`, otp[i]);
        }
        await this.verifyOTOButton.click()
        await this.page.waitForURL(navigationPathAfterLogin);
    }
}
