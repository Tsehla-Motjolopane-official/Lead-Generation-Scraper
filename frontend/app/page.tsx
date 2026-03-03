"use client";

import { useRef, useState } from "react";

type Status = "idle" | "searching" | "fetching" | "complete" | "error";

interface Row {
  name: string;
  rating: number;
}

function RatingBadge({ rating }: { rating: number }) {
  let cls = "px-2 py-0.5 rounded text-xs font-semibold ";
  if (rating >= 4.5) cls += "bg-green-100 text-green-800";
  else if (rating >= 3.5) cls += "bg-yellow-100 text-yellow-800";
  else cls += "bg-red-100 text-red-800";
  return <span className={cls}>{rating.toFixed(1)}</span>;
}

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [current, setCurrent] = useState(0);
  const [total, setTotal] = useState(0);
  const [rows, setRows] = useState<Row[]>([]);
  const [filename, setFilename] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const esRef = useRef<EventSource | null>(null);

  const isBusy = status === "searching" || status === "fetching";
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    esRef.current?.close();

    const fd = new FormData(e.currentTarget);
    const params = new URLSearchParams({
      category: fd.get("category") as string,
      city: fd.get("city") as string,
      min_stars: fd.get("min_stars") as string,
      max_results: fd.get("max_results") as string,
    });

    setStatus("searching");
    setCurrent(0);
    setTotal(0);
    setRows([]);
    setFilename("");
    setErrorMsg("");

    const es = new EventSource(`/api/scrape?${params}`);
    esRef.current = es;

    es.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      switch (msg.type) {
        case "searching":
          setStatus("searching");
          break;
        case "found":
          setTotal(msg.total);
          setStatus("fetching");
          break;
        case "progress":
          setCurrent(msg.current);
          setTotal(msg.total);
          setRows((prev) => [...prev, { name: msg.name, rating: msg.rating }]);
          break;
        case "complete":
          setFilename(msg.filename);
          setStatus("complete");
          es.close();
          break;
        case "error":
          setErrorMsg(msg.message);
          setStatus("error");
          es.close();
          break;
      }
    };

    es.onerror = () => {
      setErrorMsg("Connection lost. Please try again.");
      setStatus("error");
      es.close();
    };
  }

  return (
    <div className="space-y-6">
      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl shadow p-6 space-y-4"
      >
        <h2 className="text-lg font-semibold text-gray-800">Search Parameters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Business Category
            </label>
            <input
              name="category"
              type="text"
              required
              placeholder="e.g. dentists, plumbers"
              disabled={isBusy}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              City / Area
            </label>
            <input
              name="city"
              type="text"
              required
              placeholder="e.g. Cape Town"
              disabled={isBusy}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Minimum Star Rating
            </label>
            <input
              name="min_stars"
              type="number"
              min="0"
              max="5"
              step="0.5"
              defaultValue="4.0"
              disabled={isBusy}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Results (1–60)
            </label>
            <input
              name="max_results"
              type="number"
              min="1"
              max="60"
              defaultValue="20"
              disabled={isBusy}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={isBusy}
          className="mt-2 bg-[#1F3864] hover:bg-[#162b4d] text-white font-medium px-6 py-2 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isBusy ? "Scraping…" : "Start Scrape"}
        </button>
      </form>

      {/* Progress bar */}
      {(status === "searching" || status === "fetching") && (
        <div className="bg-white rounded-xl shadow p-6 space-y-2">
          <p className="text-sm text-gray-600">
            {status === "searching" ? "Searching Google Places…" : `Fetching details — ${current} / ${total}`}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-500 h-3 rounded-full transition-all duration-300"
              style={{ width: status === "searching" ? "5%" : `${pct}%` }}
            />
          </div>
          {status === "fetching" && (
            <p className="text-xs text-gray-500 text-right">{pct}%</p>
          )}
        </div>
      )}

      {/* Live results table */}
      {rows.length > 0 && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="px-6 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700">
              Live Results ({rows.length})
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 uppercase text-xs">
                <tr>
                  <th className="px-4 py-2 text-left w-10">#</th>
                  <th className="px-4 py-2 text-left">Name</th>
                  <th className="px-4 py-2 text-left w-24">Rating</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="px-4 py-2 text-gray-400">{i + 1}</td>
                    <td className="px-4 py-2 font-medium text-gray-800">{row.name}</td>
                    <td className="px-4 py-2">
                      <RatingBadge rating={row.rating} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Complete banner */}
      {status === "complete" && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 flex items-center justify-between">
          <div>
            <p className="text-green-800 font-semibold">
              Done! Exported {rows.length} business{rows.length !== 1 ? "es" : ""}.
            </p>
            <p className="text-green-600 text-sm mt-0.5">{filename}</p>
          </div>
          {filename && (
            <a
              href={`/api/download?filename=${encodeURIComponent(filename)}`}
              className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              Download Excel
            </a>
          )}
        </div>
      )}

      {/* Error banner */}
      {status === "error" && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-5">
          <p className="text-red-800 font-semibold">Error</p>
          <p className="text-red-600 text-sm mt-0.5">{errorMsg}</p>
        </div>
      )}
    </div>
  );
}
