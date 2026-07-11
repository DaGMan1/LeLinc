# LeLinc Cookie Grant extension

Captures the session cookies from a real, normal login on a supported
platform (Instagram, LinkedIn, Facebook, TikTok) and hands them to LeLinc's
backend. It never sees or transmits a password - only the resulting
session cookies, after the platform itself has already authenticated the
login.

## Why this exists

Cloak Browser (the headless browser LeLinc automates through) can't safely
perform the login itself - see `AGENTS.md` in the repo root for the full
reasoning. The short version: logging in is the one moment these platforms
scrutinize hardest for bot signals, so it has to happen in a real, local,
unrelayed browser. This extension is that bridge - login happens
completely normally, and only the already-authenticated session moves to
Cloak.

## How it works

1. The LeLinc dashboard calls `chrome.runtime.sendMessage` on this
   extension, asking it to watch for a login on a given platform for a
   given `client_id`.
2. The extension opens the platform's real login page in a new tab.
3. You log in exactly as you always would - 2FA, CAPTCHAs, everything
   works normally because it's genuinely the platform's own page.
4. The extension watches for that platform's session cookie to appear
   (e.g. Instagram's `sessionid`), then reads all cookies for that domain
   via the `cookies` API and POSTs them to LeLinc's Cookie Grant API
   (`POST /cookies`).
5. The login tab closes automatically. The LeLinc dashboard picks up the
   "Connected" status on its next poll.

One platform at a time - each login is a separate watch/capture cycle.

## Installing (dev / pre-Chrome-Web-Store)

1. Open `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this `extension/` folder

The extension ID is pinned via the `key` field in `manifest.json`, so it
stays the same across reloads and machines - that's what lets
`nginx/dashboard.html` message it by a fixed ID
(`jcidoldmjbfbbhnalodchgkcjbimkecf`).

## Not yet done

- Not published to the Chrome Web Store - customers currently have to
  sideload it via Developer mode, which is real friction for a sellable
  product. Worth prioritizing before launch.
- No icons (Chrome shows a default icon for unpacked extensions - fine for
  testing, not for a polished install experience).
- Firefox/Safari not supported - Chrome/Chromium only for now.
