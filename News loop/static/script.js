let isHindi = false;

const translations = {
  en: {
    title: "News loop",
    placeholder: "Paste your WhatsApp forward here...",
    checkBtn: "🔍 Check Fact",
    langBtn: "🌐 हिन्दी / English",
  },
  hi: {
    title: " समाचार लूप",
    placeholder: "यहाँ अपना व्हाट्सएप फॉरवर्ड पेस्ट करें...",
    checkBtn: "🔍 तथ्य जांचें",
    langBtn: "🌐 English / हिन्दी",
  }
};

function toggleLanguage() {
  isHindi = !isHindi;
  const lang = isHindi ? "hi" : "en";
  document.getElementById("title").innerText = translations[lang].title;
  document.getElementById("inputText").placeholder = translations[lang].placeholder;
  document.querySelector(".check-btn").innerText = translations[lang].checkBtn;
  document.querySelector(".lang-btn").innerText = translations[lang].langBtn;
}

async function checkFact() {
  const text = document.getElementById("inputText").value.trim();
  const link = document.getElementById("inputLink").value.trim();
  const image = document.getElementById("imageInput").files[0];
  const resultEl = document.getElementById("result");

  if (!text && !image && !link) {
    resultEl.innerText = isHindi ? "कृपया कुछ पाठ, एक छवि, या लिंक दर्ज करें।" : "Please enter some text, upload an image, or provide a link.";
    return;
  }

  resultEl.innerText = isHindi ? "जांच हो रही है..." : "Checking...";

  const formData = new FormData();
  formData.append("user_input", text);
  formData.append("user_link", link);
  if (image) formData.append("image_input", image);

  fetch("/process", {
    method: "POST",
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      resultEl.innerText = data.reply || (isHindi ? "कोई प्रतिक्रिया नहीं मिली।" : "No response received.");
    })
    .catch(() => {
      resultEl.innerText = isHindi ? "त्रुटि हुई।" : "An error occurred.";
    });
}

// Image upload and drag & drop logic
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');

uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
});
uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    handleImage(e.dataTransfer.files[0]);
  }
});
imageInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files[0]) {
    handleImage(e.target.files[0]);
  }
});

function handleImage(file) {
  if (!file.type.startsWith('image/')) return;
  const reader = new FileReader();
  reader.onload = function (e) {
    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image" />`;
  };
  reader.readAsDataURL(file);
}