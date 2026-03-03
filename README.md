# Lead Generation Scraper

A full-stack tool for scraping Google Places and exporting structured business leads to Excel. Run it from the browser with live progress streaming, or use the CLI directly from your terminal.

---

## Use Cases

- **Sales teams** — build targeted prospect lists by category and city (e.g. "dentists in Cape Town")
- **Marketers** — find local businesses missing a web presence or with low ratings for outreach campaigns
- **Recruiters** — identify companies in a niche to approach for partnerships or placements
- **Freelancers** — find potential clients in a specific trade and location
- **Researchers** — gather business data including hours, ratings, reviews, phone numbers, and websites

---

## Features

- Search any business category + city via the Google Places API
- Filter by minimum star rating and cap on number of results
- Live progress streaming in the browser (SSE — no page refresh needed)
- Exports a formatted `.xlsx` file with two sheets:
  - **Businesses** — name, category, rating, reviews, phone, address, website, Google Maps URL, opening hours
  - **Reviews** — up to 5 reviews per business with author, stars, date, and text
- Traffic-light colour coding on star ratings (green ≥ 4.5 / yellow ≥ 3.5 / red < 3.5)
- Download the Excel file directly from the browser
- Also usable as a CLI tool (no browser required)

---

## Screenshots

### Search Form + Live Results
![UI Screenshot](UI%20screenshots/Screenshot%202026-03-03%20at%2016.54.32.png)
> Fill in category, city, minimum star rating, and max results then click **Start Scrape**. The live results table populates row-by-row with colour-coded ratings as each business is fetched.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python · FastAPI · sse-starlette |
| Data source | Google Places API (`googlemaps` SDK) |
| Excel export | openpyxl |
| Frontend | Next.js 14 · TypeScript · Tailwind CSS |
| Streaming | Server-Sent Events (SSE) |

---

## Project Structure

```
Lead-Generation-Scraper/
├── api.py                  ← FastAPI server (SSE scrape + file download)
├── scraper.py              ← CLI entry point
├── google_places.py        ← Google Places API wrapper
├── excel_exporter.py       ← openpyxl workbook builder
├── requirements.txt
├── .env.example
├── output/                 ← generated .xlsx files (git-ignored)
└── frontend/               ← Next.js app
    └── app/
        ├── layout.tsx
        ├── page.tsx
        └── globals.css
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Google Maps API key](https://developers.google.com/maps/documentation/places/web-service/get-api-key) with the **Places API** enabled

### 1. Clone the repo

```bash
git clone https://github.com/Tsehla-Motjolopoane-official/Lead-Generation-Scraper.git
cd Lead-Generation-Scraper
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env and add your Google Maps API key
```

### 3. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend && npm install && cd ..
```

---

## Running the Web UI

**Terminal 1 — backend:**
```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Running the CLI

```bash
python3 scraper.py
```

Follow the prompts for category, city, minimum rating, and max results. The output `.xlsx` is saved to `output/`.

---

## SSE Event Protocol

The `/api/scrape` endpoint streams the following events:

| Event type | Fields | Description |
|---|---|---|
| `searching` | — | Request received, Places API call started |
| `found` | `total` | Search returned, detail fetching begins |
| `progress` | `current`, `total`, `name`, `rating` | Each business detail fetched |
| `complete` | `filename`, `count` | Excel written, ready to download |
| `error` | `message` | Something went wrong |

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_MAPS_API_KEY` | Your Google Maps / Places API key |

---

## License

MIT
