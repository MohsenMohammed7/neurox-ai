import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "NeuroX AI — مساحة الذكاء الاصطناعي", description: "مساحة عمل موحدة للذكاء الاصطناعي والأدوات المتصلة عبر MCP." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="ar" dir="rtl"><body>{children}</body></html>; }