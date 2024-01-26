// TODO: Get this from some central personal database
const checklists = {
  "hiring.review.mlre": [
    "Product Development Depth",
    "ML Depth",
    "Engineering Depth",
    "Ownership, Agency, and ability to lead projects",
    "Learnability",
    "Ambitiousness"
  ],
  "hiring.interview": [
    "Difficult piece to learn",
    "Projects that impress you",
    "Thoughts on general intelligence"
  ],
  "hiring.refcheck": [
    "Explain the role",
    "Ask about conflicts",
    "Ask about speed",
    "Ask about growth in some aspect",
    "Figure out reasons why this person could leave",
    "What would be a complementary hire for this person"
  ],
  "1:1": [
    "What are they learning? What am I learning?",
    "Clarify current responsibilities",
    "Feedback from striving for excellence angle",
    "Anything I can do for them?"
  ],
  "communication": [
    "Is it true",
    "Is it necessary",
    "Is it polite"
  ]
}

const urlPatterns = {
  "skit.hire.trakstar.com": [
    "hiring.review.mlre",
    "hiring.interview",
    "hiring.refcheck",
  ],
  "meet.google.com": [
    "1:1"
  ],
  "app.slack.com": [
    "communication"
  ],
  "app.shortwave.com": [
    "communication"
  ],
  "mail.google.com": [
    "communication"
  ]
}

function updateURL() {
  browser.tabs.query({active: true, currentWindow: true}, function(tabs) {
    let activeTab = tabs[0];
    if (activeTab.url) {
      let activeURL = new URL(activeTab.url);
      let matchedLists = urlPatterns[activeURL.hostname];
      let listsContainer = document.getElementById('lists');

      if (matchedLists) {
        listsContainer.innerHTML = '';
        matchedLists.forEach(listKey => {
          let items = checklists[listKey];
          if (items) {
            let listHTML = `<h2>${listKey}</h2><ul>`;
            items.forEach((item, index) => {
              const checkboxId = `checkbox-${listKey.replace('.', '-')}-${index}`;
              listHTML += `<li><input type="checkbox" id="${checkboxId}"><label for="${checkboxId}">${item}</label></li>`;
            });
            listHTML += '</ul>';
            listsContainer.innerHTML += listHTML;
          }
        });
      } else {
        listsContainer.innerHTML = '<h3>No checklist items for this site</h3>';
      }
    }
  });
}

browser.tabs.onActivated.addListener(updateURL);
browser.tabs.onUpdated.addListener(updateURL);
updateURL();
