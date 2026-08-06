const SUPPORTED_HOSTS = [
  "drive.google.com",
  "docs.google.com",
  "photos.google.com",
  "dropbox.com",
  "www.dropbox.com",
  "onedrive.live.com",
  "1drv.ms",
  "sharepoint.com",
  "icloud.com",
  "www.icloud.com",
  "box.com",
  "app.box.com"
];

function sourceName(url) {
  const host = new URL(url).hostname.toLowerCase();
  if (host.includes("google")) return host.includes("photos") ? "Google Photos" : "Google Drive";
  if (host.includes("dropbox")) return "Dropbox";
  if (host.includes("onedrive") || host === "1drv.ms" || host.includes("sharepoint")) return "OneDrive";
  if (host.includes("icloud")) return "iCloud";
  if (host.includes("box.com")) return "Box";
  return host;
}

function preferenceKey(url) {
  return `preference:${new URL(url).hostname.toLowerCase()}`;
}

function isSupported(url) {
  try {
    const host = new URL(url).hostname.toLowerCase();
    return SUPPORTED_HOSTS.some((supported) => host === supported || host.endsWith(`.${supported}`));
  } catch {
    return false;
  }
}

function removeExistingPrompt() {
  document.getElementById("dad-image-tool-choice")?.remove();
}

function showChoice(url) {
  removeExistingPrompt();

  const shade = document.createElement("div");
  shade.id = "dad-image-tool-choice";
  Object.assign(shade.style, {
    position: "fixed",
    inset: "0",
    zIndex: "2147483647",
    background: "rgba(0,0,0,.38)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "Segoe UI, Arial, sans-serif"
  });

  const box = document.createElement("div");
  Object.assign(box.style, {
    background: "white",
    color: "#111",
    width: "min(420px, calc(100vw - 32px))",
    borderRadius: "10px",
    padding: "22px",
    boxShadow: "0 12px 36px rgba(0,0,0,.35)"
  });

  const title = document.createElement("div");
  title.textContent = `Open this ${sourceName(url)} link with:`;
  Object.assign(title.style, { fontSize: "19px", fontWeight: "600", marginBottom: "16px" });
  box.appendChild(title);

  function addButton(label, action, primary = false) {
    const button = document.createElement("button");
    button.textContent = label;
    Object.assign(button.style, {
      display: "block",
      width: "100%",
      margin: "8px 0",
      padding: "12px",
      borderRadius: "7px",
      border: primary ? "1px solid #1b5fc6" : "1px solid #aaa",
      background: primary ? "#1b5fc6" : "#fff",
      color: primary ? "#fff" : "#111",
      fontSize: "16px",
      cursor: "pointer"
    });
    button.addEventListener("click", action);
    box.appendChild(button);
  }

  addButton("Use Dad Image Tool this time", () => {
    removeExistingPrompt();
    chrome.runtime.sendMessage({ type: "OPEN_DAD_IMAGE_TOOL", url });
  }, true);

  addButton(`Always use Dad Image Tool for ${sourceName(url)}`, async () => {
    await chrome.storage.local.set({ [preferenceKey(url)]: "app" });
    removeExistingPrompt();
    chrome.runtime.sendMessage({ type: "OPEN_DAD_IMAGE_TOOL", url });
  });

  addButton("Open in the original browser", () => {
    removeExistingPrompt();
    window.location.assign(url);
  });

  const reset = document.createElement("div");
  reset.textContent = "You can reset saved choices from the extension settings later.";
  Object.assign(reset.style, { marginTop: "12px", color: "#555", fontSize: "12px" });
  box.appendChild(reset);

  shade.appendChild(box);
  shade.addEventListener("click", (event) => {
    if (event.target === shade) removeExistingPrompt();
  });
  document.documentElement.appendChild(shade);
}

document.addEventListener("click", async (event) => {
  if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest?.("a[href]");
  if (!link || !isSupported(link.href)) return;

  const stored = await chrome.storage.local.get(preferenceKey(link.href));
  const preference = stored[preferenceKey(link.href)];

  if (preference === "app") {
    event.preventDefault();
    event.stopImmediatePropagation();
    chrome.runtime.sendMessage({ type: "OPEN_DAD_IMAGE_TOOL", url: link.href });
    return;
  }

  event.preventDefault();
  event.stopImmediatePropagation();
  showChoice(link.href);
}, true);
