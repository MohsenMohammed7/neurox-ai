# NeuroX AI — Architecture (Initial Foundation)

- Frontend: Next.js App Router, React, TypeScript, Arabic RTL.
- Backend: FastAPI service with health, chat stub, and MCP registry placeholder endpoints.
- MCP: Integration point is reserved; no external MCP server is connected yet.
- AI provider: Not configured. The current chat endpoint returns an explicit demo response.

## Planned milestones
1. Configure environment variables and a real LLM provider.
2. Add MCP client lifecycle, server configuration, and tool discovery.
3. Add Firebase authentication and persistence.
4. Add image generation provider integration.
5. Add Capacitor Android packaging and release checks.

Never commit API keys or credentials. Use environment variables and local environment files (ignored by Git).