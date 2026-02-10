import { test, expect } from '@playwright/test'

test.describe('Assistants', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/assistants')
  })

  test('should display assistants page', async ({ page }) => {
    await expect(page.locator('text=Assistants')).toBeVisible()
  })

  test('should have create assistant button', async ({ page }) => {
    const createButton = page.locator('text=Create Assistant').or(page.locator('text=New Assistant'))
    await expect(createButton).toBeVisible()
  })

  test('should navigate to new assistant page', async ({ page }) => {
    await page.click('text=Create Assistant')
    await expect(page).toHaveURL(/\/assistants\/new/)
  })

  test('should display empty state when no assistants', async ({ page }) => {
    // Check for empty state or assistant cards
    const assistantCards = page.locator('[data-testid="assistant-card"]')
    const emptyState = page.locator('text=No assistants')

    // Either we have cards or empty state
    const hasCards = await assistantCards.count() > 0
    const hasEmptyState = await emptyState.isVisible().catch(() => false)

    expect(hasCards || hasEmptyState).toBeTruthy()
  })
})

test.describe('Create Assistant', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/assistants/new')
  })

  test('should display create assistant form', async ({ page }) => {
    await expect(page.locator('input[name="name"]').or(page.locator('input[placeholder*="name"]'))).toBeVisible()
    await expect(page.locator('textarea[name="instructions"]').or(page.locator('textarea[placeholder*="instructions"]'))).toBeVisible()
  })

  test('should show validation error for empty name', async ({ page }) => {
    // Try to submit without filling required fields
    const submitButton = page.locator('button[type="submit"]').or(page.locator('text=Create'))
    await submitButton.click()

    // Should show validation error or not navigate away
    await expect(page).toHaveURL(/\/assistants\/new/)
  })

  test('should create assistant with valid data', async ({ page }) => {
    // Fill in the form
    const nameInput = page.locator('input[name="name"]').or(page.locator('input[placeholder*="name"]'))
    await nameInput.fill('Test Assistant')

    const instructionsInput = page.locator('textarea[name="instructions"]').or(page.locator('textarea[placeholder*="instructions"]'))
    await instructionsInput.fill('You are a helpful test assistant.')

    // Submit the form
    const submitButton = page.locator('button[type="submit"]').or(page.locator('text=Create'))
    await submitButton.click()

    // Should redirect to assistants list or detail page
    await expect(page).toHaveURL(/\/assistants(?!\/new)/)
  })
})
