const SPACE_ID = "baboumaha/breast-cancer-detector";
const API_NAME = "/predict";

let selectedFile = null;
let gradioClient = null;
let handleFile = null;

// Connect once and reuse — avoids re-handshaking with the Space on every click
async function getClient() {
  if (!gradioClient) {
    const module = await import("https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js");
    handleFile = module.handle_file;
    gradioClient = await module.Client.connect(SPACE_ID);
  }
  return gradioClient;
}

async function predictWithFallbackParams(client, file) {
  const payloadCandidates = [
    { file: handleFile(file) },
    { files: [handleFile(file)] },
    { input: handleFile(file) },
  ];

  let lastError = null;

  for (const payload of payloadCandidates) {
    try {
      return await client.predict(API_NAME, payload);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError;
}

document.getElementById("fileInput").addEventListener("change", function (e) {
  const file = e.target.files[0];
  if (!file) return;
  if (!file.name.endsWith(".csv")) {
    showError("Please upload a valid CSV file.");
    return;
  }
  selectedFile = file;
  document.getElementById("fileName").textContent = file.name;
  document.getElementById("fileBadge").style.display = "flex";
  document.getElementById("uploadZone").classList.add("active");
  document.getElementById("analyzeBtn").disabled = false;
  hideError();
});

const zone = document.getElementById("uploadZone");
zone.addEventListener("dragover", (e) => {
  e.preventDefault();
  zone.classList.add("active");
});
zone.addEventListener("dragleave", () => zone.classList.remove("active"));
zone.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) {
    const dt = new DataTransfer();
    dt.items.add(file);
    document.getElementById("fileInput").files = dt.files;
    document.getElementById("fileInput").dispatchEvent(new Event("change"));
  }
});

window.resetFile = function () {
  selectedFile = null;
  document.getElementById("fileBadge").style.display = "none";
  document.getElementById("uploadZone").classList.remove("active");
  document.getElementById("analyzeBtn").disabled = true;
  document.getElementById("fileInput").value = "";
  hideError();
};

window.resetAll = function () {
  resetFile();
  document.getElementById("resultsCard").style.display = "none";
  document.getElementById("resultsList").innerHTML = "";
};

window.analyze = async function () {
  if (!selectedFile) return;
  const btn = document.getElementById("analyzeBtn");
  btn.disabled = true;
  btn.classList.add("loading");
  btn.innerHTML = '<div class="spinner"></div> Analyzing…';
  hideError();

  try {
    const client = await getClient();
    const result = await predictWithFallbackParams(client, selectedFile);

    console.log("Raw prediction result:", result.data);

    // Gradio wraps each output component's value in an array. If your function
    // has a single output, the data you want is usually result.data[0].
    const predictions = Array.isArray(result.data[0]) ? result.data[0] : result.data;

    showResults(predictions);
  } catch (e) {
    console.error(e);
    showError("Connection failed. Please try again.");
  } finally {
    btn.disabled = false;
    btn.classList.remove("loading");
    btn.innerHTML = '<i class="ti ti-microscope" style="font-size:18px;"></i> Analyze patient data';
  }
};

// Parses a confidence value that might come as "99.98%" or 0.9998 or 99.98
function parseConfidence(raw) {
  if (typeof raw === "string") {
    const num = parseFloat(raw.replace("%", ""));
    return num;
  }
  if (typeof raw === "number") {
    return raw <= 1 ? raw * 100 : raw;
  }
  return 0;
}

// Builds a plain-language explanation based on prediction + confidence
function buildPlainLanguageMessage(prediction, confidencePct) {
  const isMalignant = prediction.toLowerCase() === "malignant";
  const isLowConfidence = confidencePct < 75;

  if (isLowConfidence) {
    return {
      headline: "Result unclear — please see a doctor",
      detail: `The model could not confidently tell whether this sample is benign or malignant (confidence: ${confidencePct.toFixed(1)}%). This kind of borderline result should always be followed up with an in-person medical evaluation, not relied on alone.`,
    };
  }

  if (isMalignant) {
    return {
      headline: "Pattern consistent with a cancerous (malignant) tumor",
      detail: `Based on the cell measurements provided, this sample shows characteristics commonly seen in malignant (cancerous) tumors, with ${confidencePct.toFixed(1)}% confidence. This is not a diagnosis. Please consult a doctor or oncologist promptly for further testing.`,
    };
  }

  return {
    headline: "Pattern consistent with a non-cancerous (benign) tumor",
    detail: `Based on the cell measurements provided, this sample shows characteristics commonly seen in benign (non-cancerous) tumors, with ${confidencePct.toFixed(1)}% confidence. This is not a diagnosis. Routine follow-up with a doctor is still recommended.`,
  };
}

function showResults(data) {
  const list = document.getElementById("resultsList");
  list.innerHTML = "";
  data.forEach((item) => {
    const cls = item.Prediction.toLowerCase();
    const icon = cls === "benign" ? "ti-circle-check" : "ti-alert-circle";
    const confidencePct = parseConfidence(item.Confidence);
    const plain = buildPlainLanguageMessage(item.Prediction, confidencePct);

    list.innerHTML += `
      <div class="result-item ${cls}">
        <div style="flex:1;">
          <div class="result-sample">Sample ${item.Sample}</div>
          <div class="result-label ${cls}">
            <i class="ti ${icon}" style="font-size:14px; vertical-align:-2px; margin-right:4px;"></i>
            ${item.Prediction}
          </div>
          <div style="font-size:13px; font-weight:600; margin-top:6px; color:#1a1a2e;">
            ${plain.headline}
          </div>
          <div style="font-size:12px; color:#555; margin-top:4px; line-height:1.4;">
            ${plain.detail}
          </div>
        </div>
        <div class="result-conf">${item.Confidence}</div>
      </div>`;
  });
  document.getElementById("resultsCard").style.display = "block";
}

function showError(msg) {
  const box = document.getElementById("errorBox");
  box.textContent = msg;
  box.style.display = "block";
}

function hideError() {
  document.getElementById("errorBox").style.display = "none";
}