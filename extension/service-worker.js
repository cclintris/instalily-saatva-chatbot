const SAATVA_ORIGIN = "https://www.saatva.com";

// Allows users to open the side panel by clicking on the action toolbar icon
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!tab.url) return;
  const url = new URL(tab.url);
  // Enables the side panel on saatva.com
  if (url.origin === SAATVA_ORIGIN) {
    console.log("automatically open extension");
    await chrome.sidePanel.setOptions({
      tabId,
      path: "sidePanel.html",
      enabled: true,
    });
  } else {
    // Disables the side panel on all other sites
    console.log("automatically closes extension");
    await chrome.sidePanel.setOptions({
      tabId,
      enabled: false,
    });
  }
});
