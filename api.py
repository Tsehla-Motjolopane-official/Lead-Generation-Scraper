"""
FastAPI server for Lead Generation Scraper.

Run with:
    uvicorn api:app --reload --port 8000
"""
import asyncio
import json
import os
import re
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

import excel_exporter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _safe_filename(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(":", "")
        .replace("'", "")
        .replace('"', "")
    )


@app.get("/api/scrape")
async def scrape(
    category: str = Query(...),
    city: str = Query(...),
    min_stars: float = Query(4.0, ge=0, le=5),
    max_results: int = Query(20, ge=1, le=60),
):
    async def event_generator():
        try:
            import google_places  # lazy import — defers API key check until scrape time
            yield {"data": json.dumps({"type": "searching"})}

            matches = await asyncio.to_thread(
                google_places.search_businesses,
                category=category,
                city=city,
                min_stars=min_stars,
                max_results=max_results,
            )

            if not matches:
                yield {"data": json.dumps({"type": "complete", "filename": "", "count": 0})}
                return

            total = len(matches)
            yield {"data": json.dumps({"type": "found", "total": total})}

            enriched = []
            for idx, business in enumerate(matches, start=1):
                place_id = business.get("place_id")
                if not place_id:
                    continue
                details = await asyncio.to_thread(google_places.get_place_details, place_id)
                enriched.append(details)
                yield {
                    "data": json.dumps({
                        "type": "progress",
                        "current": idx,
                        "total": total,
                        "name": details.get("name", ""),
                        "rating": details.get("rating", 0),
                    })
                }

            if not enriched:
                yield {"data": json.dumps({"type": "error", "message": "Could not retrieve details for any businesses."})}
                return

            os.makedirs("output", exist_ok=True)
            today = date.today().isoformat()
            cat_slug = _safe_filename(category)
            city_slug = _safe_filename(city)
            filename = f"{today}_{cat_slug}_{city_slug}_{min_stars}stars.xlsx"
            output_path = f"output/{filename}"

            await asyncio.to_thread(
                excel_exporter.export,
                businesses=enriched,
                category=category,
                city=city,
                output_path=output_path,
            )

            yield {"data": json.dumps({"type": "complete", "filename": filename, "count": len(enriched)})}

        except Exception as exc:
            yield {"data": json.dumps({"type": "error", "message": str(exc)})}

    return EventSourceResponse(event_generator())


@app.get("/api/download")
async def download(filename: str = Query(...)):
    if not re.fullmatch(r"[\w\-\.]+", filename):
        raise HTTPException(status_code=400, detail="Invalid filename.")
    path = os.path.join("output", filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
