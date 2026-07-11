const PLATFORMS = {
  instagram: {
    domain: "instagram.com",
    sessionCookie: "sessionid",
    loginUrl: "https://www.instagram.com/accounts/login/",
  },
  linkedin: {
    domain: "linkedin.com",
    sessionCookie: "li_at",
    loginUrl: "https://www.linkedin.com/login",
  },
  facebook: {
    domain: "facebook.com",
    sessionCookie: "c_user",
    loginUrl: "https://www.facebook.com/login/",
  },
  tiktok: {
    domain: "tiktok.com",
    sessionCookie: "sessionid",
    loginUrl: "https://www.tiktok.com/login",
  },
};

const PENDING_TTL_MS = 5 * 60 * 1000;

async function getPending() {
  const { pending } = await chrome.storage.session.get("pending");
  return pending || {};
}

async function setPending(pending) {
  await chrome.storage.session.set({ pending });
}

// Dashboard page asks us to watch for a login on `platform`. We open the
// real login page ourselves so we know exactly which tab to close later.
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  if (message?.type !== "lelinc:connect") return false;
  const { platform, clientId, apiBase } = message;
  const config = PLATFORMS[platform];
  if (!config || !clientId || !apiBase) {
    sendResponse({ ok: false, error: `Unknown platform or missing fields: ${platform}` });
    return false;
  }
  chrome.tabs.create({ url: config.loginUrl }, async (tab) => {
    const pending = await getPending();
    pending[platform] = { clientId, apiBase, tabId: tab.id, startedAt: Date.now() };
    await setPending(pending);
    sendResponse({ ok: true });
  });
  return true; // keeps sendResponse alive across the async chrome.tabs.create callback
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  const pending = await getPending();
  let changed = false;
  for (const [platform, entry] of Object.entries(pending)) {
    if (entry.tabId === tabId) {
      delete pending[platform];
      changed = true;
    }
  }
  if (changed) await setPending(pending);
});

async function checkPlatform(platform, entry) {
  const config = PLATFORMS[platform];
  if (Date.now() - entry.startedAt > PENDING_TTL_MS) {
    return "expired";
  }

  const sessionCookie = await chrome.cookies.get({
    url: `https://${config.domain}`,
    name: config.sessionCookie,
  });
  if (!sessionCookie) return null;

  const cookies = await chrome.cookies.getAll({ domain: config.domain });
  const payloadCookies = cookies.map((c) => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: c.path,
    secure: c.secure,
    httpOnly: c.httpOnly,
    expirationDate: c.expirationDate,
  }));
  const expiresAt =
    cookies.reduce((max, c) => (c.expirationDate ? Math.max(max, c.expirationDate) : max), 0) ||
    null;

  await fetch(`${entry.apiBase}/cookies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: entry.clientId,
      platform,
      cookies: JSON.stringify(payloadCookies),
      expires_at: expiresAt,
    }),
  });

  if (entry.tabId != null) {
    chrome.tabs.remove(entry.tabId).catch(() => {});
  }
  return "captured";
}

async function sweep(domainHint) {
  const pending = await getPending();
  let changed = false;
  for (const [platform, entry] of Object.entries(pending)) {
    const config = PLATFORMS[platform];
    if (domainHint && !domainHint.includes(config.domain)) continue;
    const result = await checkPlatform(platform, entry);
    if (result === "captured" || result === "expired") {
      delete pending[platform];
      changed = true;
    }
  }
  if (changed) await setPending(pending);
}

// The session cookie landing is the actual "you're logged in now" signal.
chrome.cookies.onChanged.addListener((changeInfo) => {
  if (changeInfo.removed) return;
  sweep(changeInfo.cookie.domain);
});

// Fallback sweep in case a cookie event is missed, and to clear stale entries.
chrome.alarms.create("lelinc-sweep", { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "lelinc-sweep") sweep(null);
});
