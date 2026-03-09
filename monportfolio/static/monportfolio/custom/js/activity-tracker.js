(function () {
  var startedAt = Date.now();

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i += 1) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function sendDuration() {
    var elapsedSeconds = Math.max(0, Math.round((Date.now() - startedAt) / 1000));
    var payload = JSON.stringify({
      path: window.location.pathname,
      time_spent_seconds: elapsedSeconds
    });

    var url = "/activity/time-spent/";
    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken") || ""
      },
      body: payload,
      keepalive: true
    }).catch(function () {
      return null;
    });
  }

  window.addEventListener("beforeunload", sendDuration);
})();
