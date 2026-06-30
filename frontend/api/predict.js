export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).send({ error: "Method Not Allowed" });
    return;
  }

  const targetUrl = "https://baboumaha-breast-cancer-detector.hf.space/api/predict";
  const headers = {};

  if (req.headers["content-type"]) {
    headers["content-type"] = req.headers["content-type"];
  }

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers,
      body: req,
      duplex: "half",
    });

    const body = await response.text();

    res.status(response.status);
    response.headers.forEach((value, key) => {
      if (key === "content-length" || key === "transfer-encoding") return;
      res.setHeader(key, value);
    });
    res.send(body);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
