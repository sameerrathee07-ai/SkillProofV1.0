# SkillProof - Verified Problem-Solving Marketplace

A marketplace where organizations post real operational problems and solvers must pass an automated pitch-quality gate before their proposal is delivered.

## Tech Stack

- **Frontend**: React 18 + Vite + TypeScript
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Auth**: JWT (HS256) with HttpOnly cookies
- **PDF**: ReportLab
- **Deployment**: Vercel (frontend) + Render (backend)

## Project Structure

```
SkillProofV1.0/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers
│   │   ├── core/          # Config, database
│   │   ├── engine/        # Core validation/scoring engine (pure Python)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Unit tests
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── components/    # Reusable components
    │   ├── pages/         # Page components
    │   ├── context/       # React context (Auth)
    │   ├── hooks/         # Custom hooks
    │   ├── utils/         # API client
    │   └── types/         # TypeScript types
    ├── package.json
    └── vite.config.js
```

## Core Engine (Pure Python, No Framework Imports)

The engine in `backend/app/engine/` contains:

- **Validation**: 5-step guided pitch with rule-based checks
- **Scoring**: 6 dimensions with keyword-based scoring
- **Gate**: Threshold-based pass/fail (6/10 average)
- **Suggestions**: Targeted feedback for failed dimensions
- **Outline**: 7-section proposal generator
- **PDF**: ReportLab-based PDF generation
- **Credibility**: Solver reputation from gate history

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Auth
- `POST /auth/signup` - Register (email, password, name, role)
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user

### Problems
- `POST /problems/validate` - Validate problem before posting
- `POST /problems` - Create problem (posters only)
- `GET /problems` - List open problems
- `GET /problems/{id}` - Get problem details
- `PATCH /problems/{id}/close` - Close problem

### Pitch (Solvers)
- `POST /problems/{id}/pitch/start` - Start pitch session
- `GET /pitch/{session_id}` - Get session
- `GET /pitch/{session_id}/messages` - Get messages
- `POST /pitch/{session_id}/chat` - Submit answer
- `POST /pitch/{session_id}/score` - Score completed pitch
- `POST /pitch/proposals/{id}/revise` - Revise failed proposal
- `GET /pitch/proposals/mine` - My proposals
- `GET /pitch/problems/{id}/proposals` - Proposals for problem (posters)

### Tokens (Solvers)
- `GET /tokens/balance` - Current balance
- `GET /tokens/packages` - Available packages
- `POST /tokens/purchase` - Purchase package (mocked)

### PDF
- `GET /pdf/proposals/{id}` - Download proposal PDF

### Solvers
- `GET /solvers/{id}/credibility` - Solver credibility score

## Validation Rules

### Problem Posting
- Description: ≥15 words + action verb
- Category: Hospitality, Financial Services, Education, Other
- Budget: Currency reference + number (Rs, INR, ₹, $)
- Timeline: Duration or date reference

### Pitch Steps
1. **Idea**: ≥10 words + action verb
2. **Customer**: Role/team reference + pain keyword
3. **Cost & Value**: Price pattern + justification word
4. **Alternatives**: ≥2 alternatives + differentiation word
5. **Solver**: Experience claim + advantage claim

## Scoring Dimensions

| Dimension | Base | Max Boost | Max Penalty |
|-----------|------|-----------|-------------|
| Problem Clarity | 5 | 3 | 2 |
| Customer Specificity | 5 | 3 | 2 |
| Cost and Value Case | 4 | 3 | 3 |
| Alternatives Awareness | 4 | 3 | 3 |
| Solver Capability | 4 | 3 | 3 |
| Delivery Readiness | 4 | 2 | 2 |

Gate threshold: **6.0** (average of 6 dimensions)

## Token Economy

| Event | Tokens |
|-------|--------|
| Signup | +20 |
| Accepted answer | -2 |
| Rejected answer | 0 |
| Starter Pack (Rs 29) | +10 |
| Pro Pack (Rs 59) | +20 |
| Expert Pack (Rs 99) | +50 |
| Enterprise Pack (Rs 179) | +100 |

## Testing

```bash
cd backend
pytest tests/ -v
```

## Deployment

### Backend (Render)
1. Connect GitHub repo
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

### Frontend (Vercel)
1. Connect GitHub repo
2. Framework: Vite
3. Build: `npm run build`
4. Output: `dist`
5. Add `VITE_API_URL` environment variable

## License

MIT