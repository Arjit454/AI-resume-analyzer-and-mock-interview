const answerTextarea = document.querySelector('textarea[name="answer"]');
const wordCountEl = document.getElementById("wordCount");
const answerForm = document.getElementById("answerForm");
const submitBtn = document.getElementById("submitAnswer");

if (answerTextarea) {
  answerTextarea.addEventListener("input", () => {
    const words = answerTextarea.value.trim().split(/\s+/).filter(Boolean);
    wordCountEl.textContent = words.length + (words.length === 1 ? " word" : " words");
  });
}

if (answerForm) {
  answerForm.addEventListener("submit", () => {
    submitBtn.disabled = true;
    submitBtn.textContent = "Scoring your answer...";
  });
}
