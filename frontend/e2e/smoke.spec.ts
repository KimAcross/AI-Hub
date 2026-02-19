import { expect, test } from '@playwright/test'

test.describe('CI smoke', () => {
  test('login page renders required fields', async ({ page }) => {
    await page.goto('/login')

    await expect(page).toHaveTitle(/AI-Across/)
    await expect(page.getByRole('heading', { name: 'Welcome to AI-Across' })).toBeVisible()
    await expect(page.getByLabel('Email')).toBeVisible()
    await expect(page.getByLabel('Password')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible()
  })
})
