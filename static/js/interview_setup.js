document.querySelectorAll(".option-card input").forEach((input) => {
  const syncGroup = () => {
    const groupName = input.name;
    document.querySelectorAll(`input[name="${groupName}"]`).forEach((sibling) => {
      sibling.closest(".option-card").classList.toggle("option-card-active", sibling.checked);
    });
  };
  input.addEventListener("change", syncGroup);
  syncGroup();
});
