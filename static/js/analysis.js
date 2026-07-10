const analyzeBtn = document.getElementById("analyzeBtn");
const analyzeStatus = document.getElementById("analyzeStatus");

if (analyzeBtn) {
  analyzeBtn.addEventListener("click", async () => {
    const resumeId = analyzeBtn.dataset.resumeId;

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";
    analyzeStatus.textContent = "Scoring your resume and consulting the AI — this can take a few seconds.";

    try {
      const res = await fetch(`/resume/${resumeId}/analyze`, { method: "POST" });
      const data = await res.json();

      if (res.ok && data.success) {
        analyzeStatus.textContent = "Done — loading your results...";
        window.location.reload();
      } else {
        analyzeStatus.textContent = data.error || "Something went wrong. Please try again.";
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze resume";
      }
    } catch (err) {
      analyzeStatus.textContent = "Couldn't reach the server. Check your connection and try again.";
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze resume";
    }
  });
}
