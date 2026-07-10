const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const filePreview = document.getElementById("filePreview");
const fileNameEl = document.getElementById("fileName");
const fileSizeEl = document.getElementById("fileSize");
const fileIconEl = document.getElementById("fileIcon");
const fileRemove = document.getElementById("fileRemove");
const progressTrack = document.getElementById("progressTrack");
const progressFill = document.getElementById("progressFill");
const uploadStatus = document.getElementById("uploadStatus");
const uploadSubmit = document.getElementById("uploadSubmit");
const uploadError = document.getElementById("uploadError");

let selectedFile = null;

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

function showFile(file) {
  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatSize(file.size);
  fileIconEl.textContent = file.name.toLowerCase().endsWith(".pdf") ? "PDF" : "DOC";

  dropzone.hidden = true;
  filePreview.hidden = false;
  uploadError.hidden = true;
  progressTrack.hidden = true;
  progressFill.style.width = "0%";
  uploadStatus.textContent = "";
  uploadSubmit.disabled = false;
  uploadSubmit.textContent = "Analyze resume";
}

function resetUpload() {
  selectedFile = null;
  fileInput.value = "";
  dropzone.hidden = false;
  filePreview.hidden = true;
  uploadError.hidden = true;
}

// click to browse
dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) showFile(fileInput.files[0]);
});

// drag and drop
["dragenter", "dragover"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone-active");
  });
});
["dragleave", "drop"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone-active");
  });
});
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) showFile(file);
});

fileRemove.addEventListener("click", (e) => {
  e.stopPropagation();
  resetUpload();
});

// upload with real progress via XHR (fetch doesn't expose upload progress)
uploadSubmit.addEventListener("click", () => {
  if (!selectedFile) return;

  const validExt = /\.(pdf|docx)$/i.test(selectedFile.name);
  if (!validExt) {
    uploadError.textContent = "Only PDF and DOCX files are supported.";
    uploadError.hidden = false;
    return;
  }
  if (selectedFile.size > 5 * 1024 * 1024) {
    uploadError.textContent = "File is too large. Max size is 5MB.";
    uploadError.hidden = false;
    return;
  }

  uploadError.hidden = true;
  progressTrack.hidden = false;
  uploadSubmit.disabled = true;
  uploadSubmit.textContent = "Analyzing...";
  uploadStatus.textContent = "Uploading...";

  const formData = new FormData();
  formData.append("resume", selectedFile);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/upload", true);

  xhr.upload.addEventListener("progress", (e) => {
    if (e.lengthComputable) {
      const percent = Math.round((e.loaded / e.total) * 100);
      progressFill.style.width = percent + "%";
      uploadStatus.textContent = percent < 100 ? `Uploading... ${percent}%` : "Parsing resume...";
    }
  });

  xhr.onload = () => {
    let data;
    try {
      data = JSON.parse(xhr.responseText);
    } catch {
      data = { success: false, error: "Unexpected server response." };
    }

    if (xhr.status === 200 && data.success) {
      progressFill.style.width = "100%";
      uploadStatus.textContent = "Done — redirecting...";
      window.location.href = "/resume/" + data.resume_id;
    } else {
      uploadError.textContent = data.error || "Something went wrong. Please try again.";
      uploadError.hidden = false;
      uploadSubmit.disabled = false;
      uploadSubmit.textContent = "Analyze resume";
      progressTrack.hidden = true;
      uploadStatus.textContent = "";
    }
  };

  xhr.onerror = () => {
    uploadError.textContent = "Upload failed. Check your connection and try again.";
    uploadError.hidden = false;
    uploadSubmit.disabled = false;
    uploadSubmit.textContent = "Analyze resume";
    progressTrack.hidden = true;
  };

  xhr.send(formData);
});
