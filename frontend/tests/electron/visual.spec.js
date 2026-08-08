const path = require('path')
const { test, expect } = require('@playwright/test')
const { _electron: electron } = require('playwright')

test('desktop shell visual baseline', async () => {
  const electronApp = await electron.launch({
    args: [path.join(__dirname, '../../electron/main.js')],
    cwd: path.join(__dirname, '../..'),
    env: {
      ...process.env,
      PLAYWRIGHT: '1',
      PLAYWRIGHT_ELECTRON_MOCK: '1',
    },
  })

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await expect(window.getByText('Your birth chart will appear here')).toBeVisible()
    await expect(window.locator('#app')).toHaveScreenshot('desktop-shell.png')
  } finally {
    await electronApp.close()
  }
})
