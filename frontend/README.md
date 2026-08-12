# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Build desktop installers

Freeze the backend with PyInstaller, then package with Electron. Build on the
**same OS** as the target installer (PyInstaller does not cross-compile).

```sh
cd ..
pip install -r backend/requirements-dev.txt
cd frontend
npm install

# Linux .deb
npm run electron:build

# Windows NSIS installer (run on Windows)
npm run electron:build:win
```

Both scripts call `npm run build:backend` (`../backend/build_backend.py`) and
expect the frozen binary in `../backend/dist/` (`astrology-backend` or
`astrology-backend.exe`).

### Electron visual regression with Playwright

```sh
npm install
npx playwright install chromium
npm run pw:electron:update
npm run pw:electron
```
