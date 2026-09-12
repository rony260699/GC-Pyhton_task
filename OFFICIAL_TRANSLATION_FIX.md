# Fix Render 502 Translation Error

The deployed service now uses the official Gemini API instead of an unofficial Google Translate scraper.

## 1. Create an API key

Open https://aistudio.google.com/app/apikey and create a Gemini API key.

## 2. Configure locally

In `.env`:

```env
TRANSLATION_PROVIDER=gemini
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Never commit `.env` or paste the key into source code.

## 3. Push this update

```powershell
git add .
git commit -m "Use official Gemini translation API"
git push origin main
```

## 4. Configure Render

Open the Render service, then **Environment > Add Environment Variable**:

```text
Key: GEMINI_API_KEY
Value: your_real_key_here
```

Save changes and wait for the automatic redeploy. If it does not redeploy, use **Manual Deploy > Deploy latest commit**.

## 5. Verify

Use `/docs` and run `POST /api/translate-pdf`. A valid translation returns status `200` and a downloadable PDF. Missing configuration returns `503`; rejected credentials or provider errors return `502` with a clear message.
