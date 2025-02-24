import { Page } from '@playwright/test';

export async function login(
  page: Page,
  url: string,
  tabId: string,
  username: string,
  password: string
) {
  await page.goto(url);
  if (tabId) {
    await page.click(tabId);
    await page.waitForTimeout(2000);
  }
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.waitForSelector('#captchaImage');
  await page.fill('#captcha', '123456');
  await page.click('#login-button');
}
