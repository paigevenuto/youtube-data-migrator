function checkIfComplete() {
  if (authURL.location.href.includes("yt-data-migrator/auth/google/callback")) {
    postMessage("closeNow", targetOrigin);
  }
  return;
}
let authURL = window.open(
  "/auth/google/signin",
  "authURL",
  "width=400,height=600"
);
setInterval(checkIfComplete, 100);
