const MENU_ID = "send-to-dad-image-tool";

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
  if (info.menuItemId !== MENU_ID || !info.linkUrl) return;
  const target = `dadimage://process?url=${encodeURIComponent(info.linkUrl)}`;
  chrome.tabs.create({ url: target, active: false });
});
