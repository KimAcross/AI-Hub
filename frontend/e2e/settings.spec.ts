import { test, expect } from '@playwright/test'

test.describe('Settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/settings')
  })

  test('should display settings page', async ({ page }) => {
    await expect(page.locator('text=Settings')).toBeVisible()
  })

  test('should display API key section', async ({ page }) => {
    await expect(page.locator('text=OpenRouter API Key')).toBeVisible()
    await expect(page.locator('input[type="password"]').or(page.locator('input[placeholder*="sk-or"]'))).toBeVisible()
  })

  test('should display theme selector', async ({ page }) => {
    await expect(page.locator('text=Appearance')).toBeVisible()
    await expect(page.locator('text=Theme')).toBeVisible()
  })

  test('should display default model selector', async ({ page }) => {
    await expect(page.locator('text=Default Model')).toBeVisible()
  })

  test('should display language selector', async ({ page }) => {
    await expect(page.locator('text=Language')).toBeVisible()
  })

  test('should display chat settings', async ({ page }) => {
    await expect(page.locator('text=Chat Settings')).toBeVisible()
    await expect(page.locator('text=Streaming Responses')).toBeVisible()
    await expect(page.locator('text=Auto-save Interval')).toBeVisible()
  })

  test('should toggle theme', async ({ page }) => {
    const themeSelect = page.locator('#theme').or(page.locator('select').filter({ hasText: /Light|Dark|System/ }))

    // Change theme
    await themeSelect.selectOption('dark')

    // Verify change was applied
    const html = page.locator('html')
    await expect(html).toHaveClass(/dark/)
  })

  test('should toggle streaming setting', async ({ page }) => {
    const streamingButton = page.locator('button').filter({ hasText: /Enabled|Disabled/ })
    const initialState = await streamingButton.textContent()

    await streamingButton.click()

    // Wait for state change
    await page.waitForTimeout(500)

    const newState = await streamingButton.textContent()
    expect(newState).not.toBe(initialState)
  })

  test('should display system information', async ({ page }) => {
    await expect(page.locator('text=System Information')).toBeVisible()
    await expect(page.locator('text=Embedding Model')).toBeVisible()
    await expect(page.locator('text=Max File Size')).toBeVisible()
  })

  test('should display about section', async ({ page }) => {
    await expect(page.locator('text=About AI-Across')).toBeVisible()
    await expect(page.locator('text=Version')).toBeVisible()
  })
})
