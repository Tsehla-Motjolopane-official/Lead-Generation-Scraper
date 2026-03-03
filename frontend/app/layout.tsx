import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lead Generation Scraper",
  description: "Scrape Google Places and export to Excel",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="bg-[#1F3864] text-white py-4 px-6 shadow-md">
          <h1 className="text-xl font-bold tracking-wide">Lead Generation Scraper</h1>
        </header>
        <main className="max-w-4xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
