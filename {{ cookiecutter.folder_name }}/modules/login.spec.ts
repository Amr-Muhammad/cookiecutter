import { test, expect } from '@playwright/test';
import { login } from '@tests/fixtures/login';

const userLogin = 'http://localhost:4200/auth/login';

test('Passed - Login As Entity', async ({ page }) => {
  await login(
    page,
    userLogin,
    '#mat-tab-label-0-1',
    'comprequiredother2jan25@mail.com',
    'Newpassword1&'
  );
  const element = await page.textContent('#staticitcs');
  expect(element).toContain('Statistics');
});

test('Failed - Login As Entity', async ({ page }) => {
    await login(
      page,
      userLogin,
      '#mat-tab-label-0-1',
      'comprequiredother2jan25@mail.com',
      'Newpassword11&'
    );
    const element = await page.textContent('#alert');
    expect(element).toContain('username or password is wrong');
  });