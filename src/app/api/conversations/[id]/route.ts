import { NextRequest, NextResponse } from "next/server";

const backend = () => (process.env.BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

type Context = { params: Promise<{ id: string }> };

export async function GET(_request: NextRequest, context: Context) {
  try {
    const { id } = await context.params;
    const response = await fetch(`${backend()}/api/conversations/${encodeURIComponent(id)}`, { cache: "no-store" });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "تعذر الاتصال بالخادم." }, { status: 503 });
  }
}

export async function DELETE(_request: NextRequest, context: Context) {
  try {
    const { id } = await context.params;
    const response = await fetch(`${backend()}/api/conversations/${encodeURIComponent(id)}`, { method: "DELETE", cache: "no-store" });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "تعذر الاتصال بالخادم." }, { status: 503 });
  }
}
