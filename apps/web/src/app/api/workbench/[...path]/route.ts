import http from "node:http";

import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_HOST = "127.0.0.1";
const API_PORT = 8001;

async function proxyToVersefinaApi(
  request: NextRequest,
  params: { path: string[] },
) {
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.text();
  const search = new URL(request.url).search;
  const targetPath = `/api/v1/${params.path.join("/")}${search}`;

  return await new Promise<NextResponse>((resolve) => {
    const proxyRequest = http.request(
      {
        host: API_HOST,
        port: API_PORT,
        path: targetPath,
        method: request.method,
        headers: {
          "Content-Type": request.headers.get("content-type") ?? "application/json",
          Accept: request.headers.get("accept") ?? "application/json",
          "Content-Length": body ? Buffer.byteLength(body) : 0,
        },
      },
      (proxyResponse) => {
        const chunks: Buffer[] = [];
        proxyResponse.on("data", (chunk) => chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)));
        proxyResponse.on("end", () => {
          const payload = Buffer.concat(chunks);
          resolve(
            new NextResponse(payload, {
              status: proxyResponse.statusCode ?? 502,
              headers: {
                "Content-Type": proxyResponse.headers["content-type"] ?? "application/json",
              },
            }),
          );
        });
      },
    );

    proxyRequest.on("error", (error) => {
      resolve(
        NextResponse.json(
          {
            error_code: "WORKBENCH_PROXY_FAILED",
            error_message: error.message,
            target_path: targetPath,
          },
          { status: 502 },
        ),
      );
    });

    if (body) {
      proxyRequest.write(body);
    }
    proxyRequest.end();
  });
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  return proxyToVersefinaApi(request, await context.params);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  return proxyToVersefinaApi(request, await context.params);
}
