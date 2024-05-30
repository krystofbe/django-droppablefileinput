document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.querySelector(".droppablefileinput__card");
  const fileInfo = document.querySelector(".droppablefileinput__label");
  const loadingSpinners = dropArea.querySelectorAll(
    ".droppablefileinput__spinner"
  );

  function showFileDetails() {
    const input = dropArea.querySelector('input[type="file"]');
    const fileInputInstructions = dropArea.querySelector(
      ".droppablefileinput__instructions"
    );
    const fileInputIcon = dropArea.querySelector(".droppablefileinput__icon");
    fileInputIcon.style.display = "none";
    fileInputInstructions.style.display = "none";

    const fileName = input.files[0].name;
    const fileSize = input.files[0].size;
    const humanReadableFileSize =
      fileSize < 1024
        ? `${fileSize} bytes`
        : fileSize < 1024 * 1024
        ? `${(fileSize / 1024).toFixed(2)} KB`
        : `${(fileSize / (1024 * 1024)).toFixed(2)} MB`;

    fileInfo.innerHTML = `${fileName} (${humanReadableFileSize})`;
    const autoSubmit = input.dataset.autoSubmit === "True";
    if (autoSubmit) {
      for (const spinner of loadingSpinners) {
        spinner.style.display = "inline-block";
      }
    }
  }

  // Open file dialog when clicking on the drop area
  dropArea.addEventListener("click", () => {
    document.querySelector('input[type="file"]').click();
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight() {
    dropArea.classList.add("droppablefileinput__highlight");
  }

  function unhighlight() {
    dropArea.classList.remove("droppablefileinput__highlight");
  }

  function parseMaxSize(sizeStr) {
    const units = sizeStr.slice(-1);
    const value = parseInt(sizeStr.slice(0, -1), 10);

    switch (units.toUpperCase()) {
      case "K":
        return value * 1024;
      case "M":
        return value * 1024 * 1024;
      case "G":
        return value * 1024 * 1024 * 1024;
      default:
        return value;
    }
  }

  // Update file input and submit form
  function handleFiles(files) {
    const input = document.querySelector('input[type="file"]');
    const maxFileSizeAttribute = input.dataset.maxFileSize;
    const maxFileSize = parseMaxSize(maxFileSizeAttribute);
    const allowedTypesAttribute = input.dataset.allowedTypes;
    const allowedTypes = allowedTypesAttribute
      ? allowedTypesAttribute.split(",")
      : [];
    const autoSubmit = input.dataset.autoSubmit === "True";
    const maxSizeErrorMessage = input.dataset.maxSizeErrorMessage;
    const invalidFileTypeErrorMessage =
      input.dataset.invalidFileTypeErrorMessage;

    if (files[0].size > maxFileSize) {
      alert(maxSizeErrorMessage);
      return;
    }

    const fileType = files[0].type;
    if (allowedTypes.length > 0 && !allowedTypes.includes(fileType)) {
      alert(invalidFileTypeErrorMessage);
      return;
    }

    input.files = files;
    showFileDetails();
    if (autoSubmit) {
      input.form.submit();
    }
  }

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const { files } = dt;
    handleFiles(files);
  }

  // Prevent default behaviors for drag and drop
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight the drop area when a file is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.classList.add("highlight");
    dropArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.classList.remove("highlight");
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  // Handle file drop
  dropArea.addEventListener("drop", handleDrop, false);

  // Handle changes to the file input
  document
    .querySelector('input[type="file"]')
    .addEventListener("change", function () {
      if (this.files.length > 0) {
        handleFiles(this.files);
      }
    });
});
