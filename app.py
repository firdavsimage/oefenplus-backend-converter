<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Faylni siqish – Oefen</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #FF973F, #B33F21);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center py-10 px-4 text-gray-900">
  <header class="w-full max-w-4xl flex justify-between items-center mb-10 px-6 py-4 rounded-xl shadow-md" style="background-color: #87BD6A;">
    <a href="https://oefen.uz">
      <img src="https://oefen.uz/assets/img/logo.png" alt="Oefen.uz Logo" class="h-16">
    </a>
    <a href="https://oefen.uz" class="text-white text-lg underline">Bosh sahifa</a>
  </header>

  <section class="w-full max-w-4xl bg-white bg-opacity-95 rounded-2xl shadow-lg p-6">
    <h2 class="text-xl font-semibold mb-4">1. JPG, PNG, PDF, Word yoki PowerPoint faylini yuklang</h2>
    <input id="fileInput" type="file" accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,.ppt,.pptx" class="mb-4 w-full border p-2 rounded" />
    <button id="compressBtn" class="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">🔧 Siqishni boshlash</button>
    <div id="loading" class="mt-4 hidden text-gray-700">⏳ Fayl siqilmoqda...</div>
    <div id="result" class="mt-6 hidden">
      <h3 class="text-lg font-semibold mb-2">2. Siqilgan fayl tayyor:</h3>
      <a id="downloadLink" class="inline-block bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700" download>⬇️ Yuklab olish</a>
    </div>
  </section>

<script>
  const fileInput = document.getElementById("fileInput");
  const compressBtn = document.getElementById("compressBtn");
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const downloadLink = document.getElementById("downloadLink");

  compressBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) {
      alert("Iltimos, fayl tanlang.");
      return;
    }

    loading.classList.remove("hidden");
    result.classList.add("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://oefenplus-backend-converter.onrender.com/api/compress", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Server xatosi yoki faylni qaytara olmadi.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      // Fayl nomi
      let filename = "compressed_" + file.name;
      const contentDisposition = response.headers.get("Content-Disposition");
      if (contentDisposition && contentDisposition.includes("filename=")) {
        filename = contentDisposition.split("filename=")[1].replace(/"/g, '');
      }

      downloadLink.href = url;
      downloadLink.download = filename;
      result.classList.remove("hidden");

    } catch (error) {
      alert("Xatolik: " + error.message);
    } finally {
      loading.classList.add("hidden");
    }
  });
</script>

</body>
</html>
