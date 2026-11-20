import { NextRequest, NextResponse } from "next/server";

const backend = () => (process.env.BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

export async function GET() {
  try {
    const response = await fetch(`${backend()}/api/conversations`, { cache: "no-store" });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ conversations: [], error: "تعذر الاتصال بالخادم." }, { status: 503 });
  }
}
