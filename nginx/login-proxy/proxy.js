const PLATFORM_LOGIN_URLS = {
  instagram: "https://www.instagram.com/accounts/login/",
  linkedin: "https://www.linkedin.com/login",
  facebook: "https://www.facebook.com/login/",
  tiktok: "https://www.tiktok.com/login",
};

// Opens the real platform login in a new tab - the LeLinc browser extension
// (not this page) watches that tab and POSTs captured cookies to /cookies.
function openPlatformLogin(platform) {
  const url = PLATFORM_LOGIN_URLS[platform];
  if (!url) return;
  window.open(url, "_blank", "noopener,noreferrer");
}
