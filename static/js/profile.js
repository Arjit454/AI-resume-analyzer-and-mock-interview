const photoInput = document.getElementById("photoInput");
if (photoInput) {
  photoInput.addEventListener("change", () => {
    const label = document.querySelector('label[for="photoInput"]');
    if (photoInput.files.length && label) {
      label.textContent = photoInput.files[0].name;
    }
  });
}

const deleteForm = document.getElementById("deleteForm");
if (deleteForm) {
  deleteForm.addEventListener("submit", (e) => {
    const confirmed = confirm(
      "This permanently deletes your account and all data. This can't be undone. Continue?"
    );
    if (!confirmed) {
      e.preventDefault();
    }
  });
}
