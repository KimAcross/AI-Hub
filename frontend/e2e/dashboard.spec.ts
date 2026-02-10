import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display the dashboard page', async ({ page }) => {
    await expect(page).toHaveTitle(/AI-Across/)
    await expect(page.locator('text=Dashboard')).toBeVisible()
  })

  test('should have navigation sidebar', async ({ page }) => {
    await expect(page.locator('nav')).toBeVisible()
    await expect(page.locator('text=Dashboard')).toBeVisible()
    await expect(page.locator('text=Assistants')).toBeVisible()
    await expect(page.locator('text=Chat')).toBeVisible()
    await expect(page.locator('text=Settings')).toBeVisible()
  })

  test('should navigate to assistants page', async ({ page }) => {
    await page.click('text=Assistants')
    await expect(page).toHaveURL(/\/assistants/)
  })

  test('should navigate to chat page', async ({ page }) => {
    await page.click('text=Chat')
    await expect(page).toHaveURL(/\/chat/)
  })

  test('should navigate to settings page', async ({ page }) => {
    await page.click('text=Settings')
    await expect(page).toHaveURL(/\/settings/)
  })
})
