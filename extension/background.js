const MENU_ID = "send-to-dad-image-tool";

function openInApp(url) {
  const target = `dadimage://process?url=${encodeURIComponent(url)}`;
  chrome.tabs.create({ url: target, active: false });
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: MENU_ID,
      title: "Send to Dad Image Tool",
      contexts: ["link"]
    });
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === MENU_ID && info.linkUrl) {
    openInApp(info.linkUrl);
  }
});

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "OPEN_DAD_IMAGE_TOOL" && message.url) {
    openInApp(message.url);
  }
});
