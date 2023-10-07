document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM Content Loaded");
  var conversation = document.getElementById("conversation");
  var userInput = document.getElementById("user-input");
  var submitButton = document.getElementById("submit-button");

  addIntroMessage();

  userInput.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitButton.click();
    }
  });

  submitButton.addEventListener("click", function () {
    console.log("Submit button clicked");
    var userMessage = userInput.value;
    conversation.innerHTML += `<div class="user-message">${userMessage}</div>`;
    userInput.value = "";

    // Scroll to the bottom
    conversation.scrollTop = conversation.scrollHeight;

    // Create and append typing indicator to conversation
    var typingIndicator = document.createElement("div");
    typingIndicator.id = "typing-indicator";
    typingIndicator.innerHTML =
      "<span><strong>SaatvaAI:</strong> is typing...</span>";
    conversation.appendChild(typingIndicator);

    // Scroll to show typing indicator
    conversation.scrollTop = conversation.scrollHeight;

    // Get the URL of the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      console.log("Inside chrome.tabs.query");
      var activeTab = tabs[0];
      var activeTabURL = activeTab.url;
      console.log("Active tab URL:", activeTabURL);

      chrome.scripting.executeScript(
        {
          target: { tabId: activeTab.id },
          function: stub,
        },
        (results) => {
          var payload = {
            conversation: userMessage,
            url: activeTabURL,
          };

          chat_with_chatbot(payload, function (chatbotResponse) {
            // Remove typing indicator
            conversation.removeChild(typingIndicator);

            // Append chatbot's reply to conversation
            conversation.innerHTML += `<div class="chatbot-message"><span class="chatbot-label"><strong>SaatvaAI:</strong></span> ${chatbotResponse}</div>`;

            // Scroll to the bottom again
            conversation.scrollTop = conversation.scrollHeight;
          });
        }
      );
    });
  });
});

function chat_with_chatbot(payload, callback) {
  console.log("Inside chat_with_chatbot");
  fetch("http://127.0.0.1:5000/hello", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => callback(data.response))
    .catch((error) => console.error("An error occurred:", error));
}

function scrollToBottom() {
  const conversationDiv = document.getElementById("conversation");
  conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

// Call this function every time a new message is added.
scrollToBottom();

function addIntroMessage() {
  const welcomeMessage =
    "Hi! I am SaatvaAI, an AI powered chatbot to answer your questions about Saatva. Feel free to ask me anything!";
  conversation.innerHTML += `<div class="chatbot-message">${welcomeMessage}</div>`;
}

function stub() {}
