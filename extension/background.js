function openInApp(url) {
  const target = `dadimage://process?url=${encodeURIComponent(url)}`;
  chrome.tabs.create({ url: target, active: false });
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === "OPEN_DAD_IMAGE_TOOL" && message.url) {
    openInApp(message.url);
  }
});
