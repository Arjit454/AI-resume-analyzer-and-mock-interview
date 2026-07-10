document.querySelectorAll(".roadmap-week").forEach((weekEl) => {
  const checkbox = weekEl.querySelector(".week-checkbox");
  const weekNumber = weekEl.dataset.week;

  checkbox.addEventListener("change", async () => {
    weekEl.classList.toggle("roadmap-week-done", checkbox.checked);

    try {
      const res = await fetch(`/learning/toggle/${weekNumber}`, { method: "POST" });
      const data = await res.json();

      if (data.success) {
        document.getElementById("roadmapProgressFill").style.width = data.progress + "%";
        document.getElementById("roadmapProgressLabel").textContent = data.progress + "% complete";
      } else {
        // revert on failure
        checkbox.checked = !checkbox.checked;
        weekEl.classList.toggle("roadmap-week-done", checkbox.checked);
      }
    } catch {
      checkbox.checked = !checkbox.checked;
      weekEl.classList.toggle("roadmap-week-done", checkbox.checked);
    }
  });
});
