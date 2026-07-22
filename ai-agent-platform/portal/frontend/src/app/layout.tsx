import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Agent Platform",
  description: "Enterprise AI Agent Collaboration Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-TW">
      <body>{children}</body>
    </html>
  );
}
