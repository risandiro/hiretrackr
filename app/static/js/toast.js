function showToast(message, type = "info", ms = 3500) {
  const el = document.createElement("div");
  el.className = "toast";

  if (type === "error") el.classList.add("toast--error");
  else if (type === "success") el.classList.add("toast--success");
  else el.classList.add("toast--info");

  el.textContent = message;
  document.body.appendChild(el);

  requestAnimationFrame(() => el.classList.add("show"));

  window.setTimeout(() => {
    el.classList.remove("show");
    el.classList.add("leave");

    const done = () => {
      el.removeEventListener("transitionend", done);
      el.remove();
    };

    el.addEventListener("transitionend", done);
    window.setTimeout(done, 500); /* fallback ak transitionend nenastane */
  }, ms);
}