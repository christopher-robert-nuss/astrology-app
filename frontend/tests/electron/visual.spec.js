const path = require('path')
const { test, expect } = require('@playwright/test')
const { _electron: electron } = require('playwright')

const launchApp = () =>
  electron.launch({
    args: [path.join(__dirname, '../../electron/main.js')],
    cwd: path.join(__dirname, '../..'),
    env: {
      ...process.env,
      PLAYWRIGHT: '1',
      PLAYWRIGHT_ELECTRON_MOCK: '1',
    },
  })

test('desktop shell visual baseline', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await expect(window.getByText('Your birth chart will appear here')).toBeVisible()
    await expect(window.locator('#app')).toHaveScreenshot('desktop-shell.png')
  } finally {
    await electronApp.close()
  }
})

test('chart layout keeps aspects pinned to bottom', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()

    const drawerClose = window.locator('.p-drawer button.p-drawer-close-button')
    if (await drawerClose.count()) {
      await drawerClose.first().click()
      await expect(window.locator('.p-drawer')).toBeHidden()
    }

    await expect(window.locator('.chart-aspects-panel')).toBeVisible()
    const metrics = await window.evaluate(() => {
      const panels = Array.from(document.querySelectorAll('.chart-aspects-panel'))
      const panel = panels[0]
      if (!panel) return null
      const rect = panel.getBoundingClientRect()
      return {
        bottom: rect.bottom,
        viewportHeight: window.innerHeight,
      }
    })
    expect(metrics).not.toBeNull()
    expect(metrics.bottom).toBeLessThanOrEqual(metrics.viewportHeight)
    await expect(window.locator('#app')).toHaveScreenshot('desktop-chart-pinned-aspects.png')
  } finally {
    await electronApp.close()
  }
})
