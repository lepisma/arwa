function updateURL() {
  browser.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let activeTab = tabs[0];
    document.getElementById('url-display').textContent = activeTab.url;
  });
}

browser.tabs.onActivated.addListener(updateURL);
browser.tabs.onUpdated.addListener(updateURL);
updateURL();
