const LELINC_EXTENSION_ID = "jcidoldmjbfbbhnalodchgkcjbimkecf";
const SUPPORTED_PLATFORMS = ["instagram", "linkedin", "facebook", "tiktok"];

// Asks the LeLinc Cookie Grant extension to open the real platform login
// page and watch for a successful login. The extension owns the tab and
// the cookie capture - this page just triggers it and reports back whether
// the extension is even installed.
function openPlatformLogin(platform, clientId, onResult) {
  if (!SUPPORTED_PLATFORMS.includes(platform)) return;

  if (!window.chrome || !chrome.runtime || !chrome.runtime.sendMessage) {
    onResult && onResult({ ok: false, reason: "not-installed" });
    return;
  }

  chrome.runtime.sendMessage(
    LELINC_EXTENSION_ID,
    { type: "lelinc:connect", platform, clientId, apiBase: window.location.origin },
    (response) => {
      if (chrome.runtime.lastError || !response || !response.ok) {
        onResult && onResult({ ok: false, reason: "not-installed" });
        return;
      }
      onResult && onResult({ ok: true });
    }
  );
}
