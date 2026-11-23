# RPTS — Research Project Tracking System

Agile Software Development project, MIT School of Computing, Pune (Dept. of CSE).
Faculty guide: Dr. Sonali Deshpande.

RPTS takes a research project from **proposal → approval → milestone-linked funding → progress reports → publications → agency report**, with role-based access for Faculty PIs, the HOD, Research Scholars and the Research Office.

## Run it

Needs **Node.js 22.13 or newer** (uses Node's built-in SQLite, so there is no database to install).

```bash
npm install
npm run setup      # installs server + client packages
npm run demo       # builds the UI and starts everything on http://localhost:4000
```

During development, `npm run dev` runs the API on :4000 and the Vite UI on :5173 with hot reload.

> **Windows PowerShell:** if `npm` says "running scripts is disabled", use `npm.cmd` instead (e.g. `npm.cmd run demo`).

| Command | What it does |
|---|---|
| `npm test` | Runs the 23 automated test cases (positive, negative and boundary) |
| `npm run seed` | Resets the database to the demo data |

### Demo accounts (sample data)

Password for all: **`Demo@1234`**. The login page has one-click buttons for these.

| Role | Email |
|---|---|
| Faculty PI | `pi@rpts.edu` (also `pi2@rpts.edu`) |
| Head of Department | `hod@rpts.edu` |
| Research Scholar | `scholar@rpts.edu` (also `scholar2@rpts.edu`) |
| Research Office (admin) | `admin@rpts.edu` |

## What is simulated

- **Email notifications:** no real email is sent. Every message the system would email appears in the **in-app inbox** (bell icon), labelled *Simulated email*.
- **Agency report template (US-7):** the quarterly report layout stands in for the agency's real template. It can be exported to CSV or printed to PDF.
- **All data is sample/dummy data** created by `server/src/seed.js`.

## Architecture

```
React (Vite, Tailwind, Motion, Sonner)  ──fetch /api──▶  Node.js + Express REST API  ──▶  SQLite (node:sqlite)
        client/                                         server/src/routes/*            server/data/rpts.db
                                                        JWT auth, role checks,          PDF uploads → server/data/uploads
                                                        validation, audit log
```

- **Three-tier:** presentation (React SPA), application (Express REST API), data (SQLite).
- **Security:** passwords hashed with bcrypt; JWT bearer tokens; every role rule is enforced **on the server** (the UI hiding a button is not enough: see DEF-01).
- **Validation:** done twice. The client checks for instant feedback, and the server checks again and returns per-field errors that the UI highlights.
- **Uploads:** PDF only, 10 MB maximum, with a clear error message (DEF-03).

## Features by user story

| Story | Feature | Where |
|---|---|---|
| Jury 1 | Login, registration, roles | `routes/auth.js`, `pages/Login.jsx`, `Register.jsx` |
| Jury 1 | Project profile: create, edit, delete, search, members | `routes/projects.js`, `pages/Projects.jsx`, `ProjectDetail.jsx` |
| Jury 1 | Milestones with assignment and tracking | `routes/projects.js` (milestones), Milestones tab |
| US-1 | Proposal submission with PDF | `routes/proposals.js`, `pages/ProposalForm.jsx` |
| US-2 | HOD approve / reject / return with comment | `routes/proposals.js` (`/decision`), `pages/ProposalDetail.jsx` |
| US-3 | Milestone-linked funding tranches | Funding tab, Research Office dashboard |
| US-4 | Monthly progress report upload | Progress reports tab, `pages/Reports.jsx` |
| US-5 | Publication records (DOI-validated) | Publications tab |
| US-6d | Fund audit trail | `pages/Activity.jsx` (HOD / Research Office) |
| US-7 | Quarterly agency report (simulated template) | Agency report tab |
| US-8 | "Returned" filter on proposal list | Proposals page tabs |
| US-9 | Save proposal as draft | Proposal form |

## Test cases

`server/test/rpts.test.js`. Run `npm test`. IDs TC-01 to TC-08 match the test-case slide in the Jury 2 deck.

| ID | Type | Scenario | Expected |
|---|---|---|---|
| TC-01 | Positive | HOD approves a submitted proposal | Approved, project created, PI notified |
| TC-02 | Negative | Scholar tries to approve | 403 |
| TC-03 | Negative | PI approves own proposal via direct URL | 403 (DEF-01 fixed) |
| TC-04 | Negative | HOD rejects with empty comment | "Comment required" |
| TC-05 | Positive | Assigned scholar marks milestone done | Time logged, PI notified |
| TC-06 | Negative | Another scholar completes or edits the milestone | 403 |
| TC-07 | Positive | Milestone done → tranche Eligible → released | Works even on the due date (DEF-02 fixed) |
| TC-08 | Boundary | Milestone date before project start | Validation error; the start date itself is allowed |
| TC-09 | Positive | Complete proposal with PDF | Submitted, HOD notified |
| TC-10 | Negative | Required fields empty | Every field flagged, nothing saved |
| TC-11 | Boundary | PDF of exactly 10 MB vs 10 MB + 1 byte | Accepted / 413 with clear message (DEF-03 fixed) |
| TC-12 | Negative | Non-PDF document | Refused |
| TC-13 | Boundary | Budget 0 or negative | Refused |
| TC-14 | Positive | Save as draft | Saved, hidden from HOD |
| TC-15 | Negative | Wrong password | 401 |
| TC-16 | Negative | Weak password, bad email, duplicate, HOD self-signup | Refused |
| TC-17 | Exceptional | Decide an already-decided proposal | 409 |
| TC-18 | Positive | Resubmit a returned proposal | Submitted again |
| TC-19 | Negative | Release funds before milestone done | 409 |
| TC-20 | Boundary | Tranches exceeding the budget | Refused |
| TC-21 | Negative | API call without login | 401 |
| TC-22 | Mixed | Monthly report; duplicate month; future month | 201 / 409 / 400 |
| TC-23 | Negative | Invalid or duplicate DOI | 400 / 409 |

## Team

| Member | Role | Owns |
|---|---|---|
| Kshitij Ratankumar Gedam (22) | Team lead / Scrum | Data model, code review, auth, integration |
| Lavanya Kiran Rane (23) | UI/UX | Screen design, HOD review screen, layout |
| Mohit Mahesh Gavhane (25) | Backend | Proposal + approval API, role checks, notifications |
| Om Arun Bele (26) | Frontend | Proposal form, report upload, project pages |
| Omkar Sandeep Dumbre (27) | Tester | Test cases TC-01 to TC-23, defect verification |
