// Background: Tạo context menu và xử lý click
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "reviewWithFigma",
      title: "Review this change with Figma",
      contexts: ["selection"] // chỉ hiện khi có bôi chọn
    });
  });
  
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "reviewWithFigma") {
      chrome.tabs.sendMessage(tab.id, {
        action: "getSelectedCode",
        selectionText: info.selectionText
      });
    }
  });
  
  // Nhận kết quả so sánh từ content.js và gọi API comment
  chrome.runtime.onMessage.addListener(async (msg, sender) => {
    if (msg.action === "postComment") {
      const token = await chrome.storage.sync.get("githubToken").then(d => d.githubToken);
      if (!token) {
        console.error("GitHub token not set!");
        return;
      }
  
      const { repoOwner, repoName, prNumber, filePath, lineNumber, commentBody } = msg.data;
  
      try {
        const url = `https://api.github.com/repos/${repoOwner}/${repoName}/pulls/${prNumber}/comments`;
        const res = await fetch(url, {
          method: "POST",
          headers: {
            "Authorization": `token ${token}`,
            "Accept": "application/vnd.github.v3+json"
          },
          body: JSON.stringify({
            body: commentBody,
            path: filePath,
            line: lineNumber,
            side: "RIGHT"
          })
        });
        const result = await res.json();
        console.log("Comment posted:", result);
      } catch (err) {
        console.error("Error posting comment", err);
      }
    }
  });
  