document.getElementById("reset").addEventListener("click", async () => {
  await chrome.storage.local.clear();
  document.getElementById("status").textContent = "Saved choices were reset.";
});
