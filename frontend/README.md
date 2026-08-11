# Frontend — local dev without Docker (VS Code)

```bash
cd frontend
npm install
```

Create `frontend/.env` (Vite reads this automatically) or just rely on
the root `.env` if you run via Docker. For pure local dev:

```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

Open http://localhost:5173. Make sure the backend (see
`../backend/README.md`) is running on port 8000 first.

### VS Code tips
- Install the "ES7+ React/Redux/React-Native snippets" and "Prettier"
  extensions for a smoother TSX editing experience.
- The dev server hot-reloads on save — no restart needed.
