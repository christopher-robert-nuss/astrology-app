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

const fillRequiredBirthData = async (window) => {
  await window.getByPlaceholder('Day').fill('10')
  await window.getByPlaceholder('Month').fill('12')
  await window.getByPlaceholder('Year').fill('1815')
  await window.getByPlaceholder('Hour').fill('0')
  await window.getByPlaceholder('Minute').fill('0')
  await window.getByPlaceholder('Latitude').fill('51.5')
  await window.getByPlaceholder('Longitude').fill('0.1')
}

test('print styles keep the dark chart plate', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.emulateMedia({ media: 'print' })
    const printStyle = await window.evaluate(() => {
      const body = getComputedStyle(document.body)
      return {
        background: body.backgroundColor,
        colorAdjust: body.printColorAdjust || body.webkitPrintColorAdjust,
      }
    })
    expect(printStyle.background).toBe('rgb(255, 255, 255)')
  } finally {
    await electronApp.close()
  }
})

test('desktop shell visual baseline', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await expect(window.getByText('Natal chart workspace')).toBeVisible()
    await expect(window.locator('#app')).toHaveScreenshot('desktop-shell.png')
  } finally {
    await electronApp.close()
  }
})

test('desktop menus open vertically without moving the workspace', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await expect(window.getByText('Natal chart workspace')).toBeVisible()

    const before = await window.evaluate(() => {
      const app = document.querySelector('#app').getBoundingClientRect()
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      return { appTop: app.top, stageTop: stage.top, stageHeight: stage.height }
    })

    await window.getByText('File', { exact: true }).click()

    const menuState = await window.evaluate(() => {
      const rootItem = Array.from(document.querySelectorAll('.astro-menu-list > .astro-menu-item')).find(
        (item) => item.textContent.trim().startsWith('File'),
      )
      const submenu = rootItem?.querySelector(':scope > .astro-submenu')
      const submenuItems = submenu
        ? Array.from(submenu.querySelectorAll(':scope > .astro-menu-item')).map((item) => {
            const rect = item.getBoundingClientRect()
            return { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
          })
        : []
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      const menubar = document.querySelector('.astro-menubar').getBoundingClientRect()
      const rootList = document.querySelector('.astro-menu-list').getBoundingClientRect()
      const rootItemRect = rootItem?.getBoundingClientRect()
      const submenuStyle = submenu ? getComputedStyle(submenu) : null
      const submenuRect = submenu?.getBoundingClientRect()
      const separators = submenu
        ? Array.from(submenu.querySelectorAll('.astro-menu-separator')).map((separator) => {
            const rect = separator.getBoundingClientRect()
            return {
              left: rect.left,
              right: rect.right,
              top: rect.top,
              bottom: rect.bottom,
            }
          })
        : []
      return {
        active: rootItem?.getAttribute('data-p-active'),
        display: submenu ? getComputedStyle(submenu).display : 'missing',
        flexDirection: submenu ? getComputedStyle(submenu).flexDirection : 'missing',
        submenuItems,
        stageTop: stage.top,
        stageHeight: stage.height,
        menubarHeight: menubar.height,
        rootListHeight: rootList.height,
        rootItemHeight: rootItemRect?.height,
        submenuPosition: submenuStyle?.position,
        submenuTop: submenuStyle?.top,
        submenuRect,
        separators,
      }
    })
    expect(menuState.active).toBe('true')
    expect(menuState.display).toBe('flex')
    expect(menuState.flexDirection).toBe('column')
    expect(menuState.submenuItems.length).toBeGreaterThan(3)
    expect(new Set(menuState.submenuItems.map((item) => item.top)).size).toBeGreaterThan(1)
    expect(new Set(menuState.submenuItems.map((item) => item.left)).size).toBe(1)
    expect(menuState.separators.length).toBeGreaterThan(0)
    for (const separator of menuState.separators) {
      expect(separator.left).toBeGreaterThanOrEqual(menuState.submenuRect.left)
      expect(separator.right).toBeLessThanOrEqual(menuState.submenuRect.right)
    }
    expect(menuState.stageTop).toBe(before.stageTop)
    expect(menuState.stageHeight).toBe(before.stageHeight)
  } finally {
    await electronApp.close()
  }
})

test('desktop menus do not open or switch from hover', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    const fileMenu = window.getByText('File', { exact: true })
    const editMenu = window.getByText('Edit', { exact: true })

    await editMenu.hover()
    await expect(window.locator('.astro-menu-item[data-p-active="true"]')).toHaveCount(0)
    await expect(window.locator('.astro-menu-item > .astro-submenu')).toHaveCount(4)
    await expect(window.locator('.astro-menu-item > .astro-submenu').first()).toBeHidden()

    await fileMenu.click()
    await expect(window.locator('.astro-menu-item[data-p-active="true"]').first()).toContainText('File')
    const separatorBounds = await window.locator('.astro-menu-item[data-p-active="true"] > .astro-submenu').evaluate((submenu) => {
      const submenuRect = submenu.getBoundingClientRect()
      return Array.from(submenu.querySelectorAll('.astro-menu-separator')).map((separator) => {
        const rect = separator.getBoundingClientRect()
        return { left: rect.left, right: rect.right, submenuLeft: submenuRect.left, submenuRight: submenuRect.right }
      })
    })
    expect(separatorBounds.length).toBeGreaterThan(0)
    for (const separator of separatorBounds) {
      expect(separator.left).toBeGreaterThanOrEqual(separator.submenuLeft)
      expect(separator.right).toBeLessThanOrEqual(separator.submenuRight)
    }

    await editMenu.hover()
    await expect(window.locator('.astro-menu-item[data-p-active="true"]').first()).toContainText('File')
  } finally {
    await electronApp.close()
  }
})

test('File New Chart opens the Birth Data dialog', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByText('File', { exact: true }).click()
    await window.getByText('New Chart', { exact: true }).click()
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()
    await expect(window.getByText('Enter Birth Data', { exact: true })).toBeVisible()
  } finally {
    await electronApp.close()
  }
})

test('File Save without a chart uses a quiet menubar status, not a toast', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    const before = await window.evaluate(() => {
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      return { stageTop: stage.top }
    })

    await window.getByText('File', { exact: true }).click()
    await window.getByText('Save', { exact: true }).click()

    const status = window.locator('.astro-status')
    await expect(status).toBeVisible()
    await expect(status).toContainText('Generate a chart before saving')
    await expect(status.locator('.astro-status-dismiss')).toHaveCount(0)
    await expect(window.locator('.p-toast')).toHaveCount(0)

    const after = await window.evaluate(() => {
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      const status = document.querySelector('.astro-status')
      const menubar = document.querySelector('.astro-menubar').getBoundingClientRect()
      const statusRect = status.getBoundingClientRect()
      return {
        stageTop: stage.top,
        statusTop: statusRect.top,
        menubarBottom: menubar.bottom,
        inline: status.classList.contains('astro-status--inline'),
      }
    })
    expect(after.stageTop).toBe(before.stageTop)
    expect(after.inline).toBe(true)
    expect(after.statusTop).toBeGreaterThanOrEqual(0)
    expect(after.statusTop).toBeLessThan(after.menubarBottom)
  } finally {
    await electronApp.close()
  }
})

test('problem status sits under the menubar without moving the workspace', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    const before = await window.evaluate(() => {
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      return { stageTop: stage.top }
    })

    await window.evaluate(() => {
      window.__astroStatus.show({
        tone: 'problem',
        text: 'Could not save the chart. Disk is full.',
      })
    })

    const status = window.locator('.astro-status')
    await expect(status).toBeVisible()
    await expect(status).toHaveClass(/astro-status--strip/)
    await expect(status).toHaveClass(/astro-status--problem/)
    await expect(status.getByRole('button', { name: 'Dismiss' })).toBeVisible()
    await expect(window.locator('.p-toast')).toHaveCount(0)

    const geometry = await window.evaluate(() => {
      const stage = document.querySelector('.chart-stage').getBoundingClientRect()
      const menubar = document.querySelector('.astro-menubar').getBoundingClientRect()
      const status = document.querySelector('.astro-status').getBoundingClientRect()
      return {
        stageTop: stage.top,
        menubarBottom: menubar.bottom,
        statusTop: status.top,
        statusHeight: status.height,
      }
    })
    expect(geometry.stageTop).toBe(before.stageTop)
    expect(Math.abs(geometry.statusTop - geometry.menubarBottom)).toBeLessThanOrEqual(1)

    await status.getByRole('button', { name: 'Dismiss' }).click()
    await expect(status).toHaveCount(0)
  } finally {
    await electronApp.close()
  }
})

test('Generate Chart without birth data asks for the missing fields', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()
    await window.getByRole('button', { name: 'Generate Chart' }).click()

    const status = window.locator('.astro-status')
    await expect(status).toBeVisible()
    await expect(status).toContainText('Enter birth date, time, and location before generating a chart.')
    await expect(status).not.toContainText('object Object')
    await expect(status).not.toContainText('api-request')
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()
    await expect(window.getByAltText('Birth Chart')).toHaveCount(0)
  } finally {
    await electronApp.close()
  }
})

test('problem status can be dismissed while the Birth Data dialog is open', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()

    await window.evaluate(() => {
      window.__astroStatus.show({
        tone: 'problem',
        text: 'Could not generate the chart. Ephemeris data is needed.',
      })
    })

    const status = window.locator('.astro-status')
    await expect(status).toBeVisible()
    await status.getByRole('button', { name: 'Dismiss' }).click()
    await expect(status).toHaveCount(0)
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()
  } finally {
    await electronApp.close()
  }
})

test('menu focus uses the subtle focus treatment', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    const menuList = window.locator('.astro-menubar .astro-menu-list')
    await menuList.focus()

    const focusStyle = await menuList.evaluate((element) => {
      const style = getComputedStyle(element)
      return { outline: style.outline, shadow: style.boxShadow }
    })

    expect(focusStyle.outline).toContain('none')
    expect(focusStyle.shadow).toBe('none')
  } finally {
    await electronApp.close()
  }
})

test('buttons keep a visible gap between icons and labels', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    const button = window.getByRole('button', { name: 'Open Birth Data' })
    const spacing = await button.evaluate((element) => {
      const icon = element.querySelector('.astro-button-icon')
      const label = element.querySelector('.astro-button-label')
      if (!icon || !label) return null
      const iconRect = icon.getBoundingClientRect()
      const labelRect = label.getBoundingClientRect()
      return {
        gap: getComputedStyle(element).gap,
        distance: labelRect.left - iconRect.right,
      }
    })

    expect(spacing).not.toBeNull()
    expect(spacing.gap).toBe('8px')
    expect(spacing.distance).toBeGreaterThanOrEqual(8)
    expect(
      await button.evaluate((element) => ({
        background: getComputedStyle(element).backgroundColor,
        border: getComputedStyle(element).borderTopColor,
      })),
    ).toEqual({
      background: 'rgb(201, 164, 103)',
      border: 'rgb(201, 164, 103)',
    })

    const beforeClick = await button.boundingBox()
    await button.click()
    const afterClick = await button.boundingBox()
    expect(afterClick.width).toBe(beforeClick.width)
  } finally {
    await electronApp.close()
  }
})

test('edit birth data uses the primary button treatment', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await fillRequiredBirthData(window)
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()

    const button = window.getByRole('button', { name: 'Edit Birth Data' })
    await expect(button).toBeVisible()
    await expect
      .poll(() => button.evaluate((element) => getComputedStyle(element).backgroundColor))
      .toBe('rgb(201, 164, 103)')
  } finally {
    await electronApp.close()
  }
})

test('chart toolbar actions use outlined primary treatment', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await fillRequiredBirthData(window)
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()

    const primaryButton = window.getByRole('button', { name: 'Edit Birth Data' })
    const primaryMetrics = await primaryButton.evaluate((element) => {
      const styles = getComputedStyle(element)
      return { padding: styles.padding, height: styles.height, minHeight: styles.minHeight }
    })

    for (const name of ['View Full Screen', 'Show Magnifier']) {
      const button = window.getByRole('button', { name })
      await expect(button).toBeVisible()
      await expect
        .poll(() =>
          button.evaluate((element) => ({
            background: getComputedStyle(element).backgroundColor,
            border: getComputedStyle(element).borderTopColor,
            color: getComputedStyle(element).color,
          })),
        )
        .toEqual({
          background: 'rgba(0, 0, 0, 0)',
          border: 'rgb(201, 164, 103)',
          color: 'rgb(201, 164, 103)',
        })
      expect(
        await button.evaluate((element) => {
          const styles = getComputedStyle(element)
          return { padding: styles.padding, height: styles.height, minHeight: styles.minHeight }
        }),
      ).toEqual(primaryMetrics)
    }
  } finally {
    await electronApp.close()
  }
})

test('full screen chart uses the dark editorial plate', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await fillRequiredBirthData(window)
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()
    await expect(window.locator('.astro-birth-data-dialog')).toBeHidden()

    await window.getByRole('button', { name: 'View Full Screen' }).click()
    const overlay = window.locator('.astro-chart-fullscreen')
    await expect(overlay).toBeVisible()
    await expect(
      overlay.locator('.astro-chart-fullscreen-wheel, img[alt="Birth Chart Full Screen"]'),
    ).toBeVisible()
    await expect
      .poll(() => overlay.evaluate((element) => getComputedStyle(element).backgroundColor))
      .toBe('rgb(23, 25, 26)')

    const closeButton = window.getByRole('button', { name: 'Close full screen chart' })
    await expect(closeButton).toBeVisible()
    await expect
      .poll(() =>
        closeButton.evaluate((element) => ({
          background: getComputedStyle(element).backgroundColor,
          border: getComputedStyle(element).borderTopColor,
          color: getComputedStyle(element).color,
        })),
      )
      .toEqual({
        background: 'rgba(0, 0, 0, 0)',
        border: 'rgb(201, 164, 103)',
        color: 'rgb(201, 164, 103)',
      })

    await closeButton.click()
    await expect(overlay).toHaveCount(0)
    await expect(window.getByAltText('Birth Chart')).toBeVisible()
  } finally {
    await electronApp.close()
  }
})

test('Escape closes Birth Data, Preferences, and full screen', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')

    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()
    await window.keyboard.press('Escape')
    await expect(window.locator('.astro-birth-data-dialog')).toBeHidden()

    await window.getByText('Edit', { exact: true }).click()
    await window.getByText('Preferences...', { exact: true }).click()
    await expect(window.getByText('Edit Preferences', { exact: true })).toBeVisible()
    await window.keyboard.press('Escape')
    await expect(window.getByText('Edit Preferences', { exact: true })).toBeHidden()

    await window.getByRole('button', { name: 'Open Birth Data' }).click()
    await fillRequiredBirthData(window)
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()
    await window.getByRole('button', { name: 'View Full Screen' }).click()
    await expect(window.locator('.astro-chart-fullscreen')).toBeVisible()
    await window.keyboard.press('Escape')
    await expect(window.locator('.astro-chart-fullscreen')).toHaveCount(0)
  } finally {
    await electronApp.close()
  }
})

test('Visible Aspects presets reflect the active selection', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByText('Edit', { exact: true }).click()
    await window.getByText('Preferences...', { exact: true }).click()

    const allPreset = window.locator('.astro-dialog .astro-aspect-preset', { hasText: 'All' })
    await allPreset.click()
    await expect(allPreset).toHaveAttribute('aria-pressed', 'true')
    await expect(allPreset).toHaveCSS('border-top-color', 'rgb(201, 164, 103)')
    await expect(allPreset).toHaveCSS('background-color', 'rgba(0, 0, 0, 0)')
    await expect(allPreset).toHaveCSS('outline-style', 'none')

    const selectedAspect = window.locator('.astro-dialog .astro-aspect-option').first()
    await expect(selectedAspect).toHaveAttribute('aria-pressed', 'true')
    await expect(selectedAspect).toHaveCSS('border-top-color', 'rgb(201, 164, 103)')
    await expect(selectedAspect).toHaveCSS('outline-style', 'none')

    await window
      .locator('.astro-dialog .astro-aspect-preset', { hasText: 'None' })
      .click()
    await expect(allPreset).toHaveAttribute('aria-pressed', 'false')
    await expect(
      window.locator('.astro-dialog .astro-aspect-preset', { hasText: 'None' }),
    ).toHaveAttribute('aria-pressed', 'true')
    await expect(selectedAspect).toHaveAttribute('aria-pressed', 'false')
    await expect(selectedAspect).toHaveCSS('border-top-color', 'rgb(92, 98, 94)')
    await expect(selectedAspect).toHaveCSS('outline-style', 'none')
  } finally {
    await electronApp.close()
  }
})

test('number inputs use the shared field treatment and subtle focus ring', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()

    const numberInput = window.locator('input[role="spinbutton"]').first()
    await expect(numberInput).toBeVisible()
    const beforeFocus = await numberInput.evaluate((element) => {
      const styles = getComputedStyle(element)
      return {
        className: element.className,
        parentClass: element.parentElement?.className,
        height: styles.height,
        background: styles.backgroundColor,
        border: styles.borderColor,
      }
    })
    await numberInput.focus()
    const focused = await numberInput.evaluate((element) => {
      const styles = getComputedStyle(element)
      return {
        height: styles.height,
        background: styles.backgroundColor,
        border: styles.borderColor,
        shadow: styles.boxShadow,
      }
    })
    expect(beforeFocus.height).toBe('34px')
    expect(beforeFocus.background).toBe('rgb(23, 25, 26)')
    expect(beforeFocus.border).toBe('rgb(92, 98, 94)')
    expect(focused.background).toBe(beforeFocus.background)
    expect(focused.shadow).toContain('rgba(189, 180, 167, 0.2)')
    expect(focused.shadow).not.toContain('195, 106, 70')
  } finally {
    await electronApp.close()
  }
})

test('all form fields share the same focus ring', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()

    const textInput = window.locator('input[type="text"]').first()
    const numberInput = window.locator('input[role="spinbutton"]').first()
    for (const field of [textInput, numberInput]) {
      await field.focus()
      await expect
        .poll(() => field.evaluate((element) => getComputedStyle(element).boxShadow))
        .toContain('rgba(189, 180, 167, 0.2)')
      expect(await field.evaluate((element) => getComputedStyle(element).outlineStyle)).toBe('none')
    }

    await window.getByRole('button', { name: 'Close' }).click()
    await window.getByText('Edit', { exact: true }).click()
    await window.getByText('Preferences...', { exact: true }).click()
    const select = window.locator('.astro-select').first()
    await expect(select).toBeVisible()
    await select.click()
    const dropdownIcon = select.locator('svg').first()
    const selectBox = await select.boundingBox()
    const iconBox = await dropdownIcon.boundingBox()
    expect(iconBox.x + iconBox.width).toBeLessThanOrEqual(selectBox.x + selectBox.width)
    expect(
      await dropdownIcon.evaluate((element) => getComputedStyle(element).color),
    ).toBe('rgb(201, 164, 103)')
    const selectShadow = await select.evaluate((element) => getComputedStyle(element).boxShadow)
    expect(selectShadow).toContain('rgba(189, 180, 167, 0.2)')
  } finally {
    await electronApp.close()
  }
})

test('preferences dialog close button has no automatic focus ring', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByText('Edit', { exact: true }).click()
    await window.getByText('Preferences...', { exact: true }).click()

    const closeButton = window.locator('.astro-dialog button').first()
    await expect(closeButton).toBeVisible()
    expect(await closeButton.evaluate((element) => getComputedStyle(element).outlineStyle)).toBe(
      'none',
    )
    expect(await closeButton.evaluate((element) => getComputedStyle(element).boxShadow)).toBe(
      'none',
    )
  } finally {
    await electronApp.close()
  }
})

test('birth data drawer keeps its close button beside the heading', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()

    const header = window.locator('.astro-birth-data-dialog .astro-overlay-header')
    const title = header.getByText('Enter Birth Data')
    const close = header.locator('button')
    const headerBox = await header.boundingBox()
    const titleBox = await title.boundingBox()
    const closeBox = await close.boundingBox()

    expect(headerBox).not.toBeNull()
    expect(titleBox).not.toBeNull()
    expect(closeBox).not.toBeNull()
    expect(Math.abs(titleBox.y + titleBox.height / 2 - (closeBox.y + closeBox.height / 2))).toBeLessThanOrEqual(1)
    expect(closeBox.x + closeBox.width).toBeCloseTo(headerBox.x + headerBox.width - 16, 0)
  } finally {
    await electronApp.close()
  }
})

test('Birth Data modal screens the rest of the window', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.getByRole('button', { name: 'Open Birth Data' }).click()

    const mask = window.locator('.astro-dialog-mask')
    await expect(mask).toBeVisible()
    await expect(window.locator('.astro-birth-data-dialog')).toBeVisible()

    const paint = await mask.evaluate((element) => {
      const styles = getComputedStyle(element)
      const rect = element.getBoundingClientRect()
      return {
        background: styles.backgroundColor,
        width: rect.width,
        height: rect.height,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
      }
    })
    expect(paint.background).not.toBe('rgba(0, 0, 0, 0)')
    expect(paint.background).not.toBe('rgb(0, 0, 0)')
    expect(paint.width).toBe(paint.viewportWidth)
    expect(paint.height).toBe(paint.viewportHeight)
  } finally {
    await electronApp.close()
  }
})

test('birth data fields share a consistent width and place country beside city', async () => {
  const electronApp = await launchApp()

  try {
    const window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.setViewportSize({ width: 1280, height: 800 })
    await window.getByRole('button', { name: 'Open Birth Data' }).click()

    const field = (placeholder) =>
      window.locator(`.astro-birth-data-dialog input[placeholder="${placeholder}"]`)

    const nameBox = await field('Name').boundingBox()
    const timezoneBox = await window.locator('.astro-birth-data-dialog .astro-timezone').boundingBox()
    const cityBox = await field('City').boundingBox()
    const countryBox = await field('Country').boundingBox()
    const houseBox = await window.locator('.astro-birth-data-dialog .astro-house-system').boundingBox()
    const latitudeBox = await field('Latitude').boundingBox()
    const longitudeBox = await field('Longitude').boundingBox()

    expect(nameBox).not.toBeNull()
    expect(timezoneBox).not.toBeNull()
    expect(cityBox).not.toBeNull()
    expect(countryBox).not.toBeNull()
    expect(houseBox).not.toBeNull()
    expect(latitudeBox).not.toBeNull()
    expect(longitudeBox).not.toBeNull()

    expect(Math.abs(timezoneBox.width - nameBox.width)).toBeLessThanOrEqual(1)
    expect(Math.abs(houseBox.width - nameBox.width)).toBeLessThanOrEqual(1)
    expect(Math.abs(cityBox.width - countryBox.width)).toBeLessThanOrEqual(1)
    expect(Math.abs(cityBox.width - latitudeBox.width)).toBeLessThanOrEqual(1)
    expect(Math.abs(countryBox.width - longitudeBox.width)).toBeLessThanOrEqual(1)
    expect(Math.abs(cityBox.y - countryBox.y)).toBeLessThanOrEqual(1)
    expect(countryBox.x).toBeGreaterThan(cityBox.x + cityBox.width)

    await window.setViewportSize({ width: 420, height: 760 })
    await expect
      .poll(async () => {
        const city = await field('City').boundingBox()
        const country = await field('Country').boundingBox()
        return {
          stacked: country.y >= city.y + city.height - 1,
          aligned: Math.abs(country.x - city.x) <= 1,
          fullWidth: Math.abs(city.width - (await field('Name').boundingBox()).width) <= 1,
        }
      })
      .toEqual({ stacked: true, aligned: true, fullWidth: true })
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
    await fillRequiredBirthData(window)
    await window.getByRole('button', { name: 'Generate Chart' }).click()
    await expect(window.getByAltText('Birth Chart')).toBeVisible()
    await expect(window.locator('.astro-birth-data-dialog')).toBeHidden()

    await expect(window.locator('.chart-aspects-panel')).toBeVisible()
    const metrics = await window.evaluate(() => {
      const panels = Array.from(document.querySelectorAll('.chart-aspects-panel'))
      const panel = panels[0]
      if (!panel) return null
      const rect = panel.getBoundingClientRect()
      return {
        bottom: rect.bottom,
        viewportHeight: window.innerHeight,
        buttonCount: panel.querySelectorAll('button').length,
        overflowingButtons: Array.from(panel.querySelectorAll('button')).filter((button) => {
          const buttonRect = button.getBoundingClientRect()
          return buttonRect.right > window.innerWidth || buttonRect.bottom > rect.bottom
        }).length,
      }
    })
    expect(metrics).not.toBeNull()
    expect(metrics.bottom).toBeLessThanOrEqual(metrics.viewportHeight)
    expect(metrics.buttonCount).toBeGreaterThan(0)
    expect(metrics.overflowingButtons).toBe(0)

    const majorPreset = window.locator('.chart-aspects-panel .astro-aspect-preset', {
      hasText: 'Major',
    })
    await expect(majorPreset).toHaveAttribute('aria-pressed', 'true')
    await expect(majorPreset).toHaveCSS('border-top-color', 'rgb(201, 164, 103)')
    await expect(majorPreset).toHaveCSS('outline-style', 'none')

    const selectedAspect = window.locator('.chart-aspects-panel .astro-aspect-option').first()
    await expect(selectedAspect).toHaveAttribute('aria-pressed', 'true')
    await expect(selectedAspect).toHaveCSS('border-top-color', 'rgb(201, 164, 103)')
    await expect(selectedAspect).toHaveCSS('outline-style', 'none')
    await expect(window.locator('#app')).toHaveScreenshot('desktop-chart-pinned-aspects.png')
  } finally {
    await electronApp.close()
  }
})
