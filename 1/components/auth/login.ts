import { Page, Locator, expect } from "@playwright/test";

export class LoginModule {
    readonly page: Page;

    // Fields
    readonly email: Locator;
    readonly password: Locator;
    readonly pinCode: Locator[];

    // Interactive
    readonly loginButton: Locator;
    readonly pinCodeButton: Locator;

    constructor(page: Page) {
        this.page = page;
        // Change below fields to fit the required project login form
        this.email = page.getByTestId("email-input");
        this.password = page.getByTestId("password-input");
        this.loginButton = page.getByTestId("login-button");
    }

    async login(email: string, password: string) {
        await this.page.goto("/");
        await this.email.fill(email);
        await this.password.fill(password);
        await this.loginButton.click();
        // Extra code for otp

        // Assert to ensure login is successful to capture the cookies
        // await expect(
        //     this.page.getByRole("heading", { name: "الخدمات" })
        // ).toBeVisible();
    }
}
