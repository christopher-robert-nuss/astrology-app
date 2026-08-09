# Simple Astrology App Agent Guide

## Project overview

This repo contains:

- a Python/FastAPI backend for astrology calculations
- a Vue 3 + Vite frontend
- an Electron desktop wrapper

## Working conventions

- Prefer small, focused changes over large rewrites.
- Keep backend and frontend concerns separated.
- Preserve offline-friendly behavior, especially around ephemeris data.
- Do not hardcode paths or environment-specific values when a config pattern already exists.
- When changing APIs, update the frontend usage and relevant docs.

## Development workflow

- Create a new branch before starting a significant feature or bug fix, using a clear prefix such as `feat/` or `fix/`.
- Keep work in small, meaningful phases and commit after each milestone.
- Use comments sparingly and only when they explain why something exists, not how it works.

## Backend / Frontend sync

- When a backend change changes an API contract, request shape, or response format, update the matching frontend usage so the two stay aligned.
- Keep API and UI changes coordinated when adding or removing fields, endpoints, or preferences.

## Regression and validation

- When fixing a bug, verify the behavior before and after the change and add or update targeted checks where practical.
- For larger workflows or user-facing changes, validate the end-to-end path rather than relying only on a quick code review.

## Testing expectations

- Prefer targeted checks for small bug fixes and local behavior changes.
- For new features or user-facing flows, validate the full path through the backend and frontend when practical.
- When a change affects chart generation, API contracts, or offline data handling, verify the relevant end-to-end behavior rather than assuming it is correct.

## Backend guidance

- Main backend logic is in [backend/main.py](backend/main.py).
- Prefer existing patterns for path helpers, environment variables, and validation.
- Keep Pydantic models and FastAPI route changes explicit and predictable.
- Preserve the app’s ability to run without requiring bundled ephemeris files.

## Frontend guidance

- Main frontend setup is defined in [frontend/package.json](frontend/package.json).
- Follow existing Vue component and state patterns.
- Prefer small reusable UI components over ad hoc one-offs.
- Keep API calls consistent with the backend contract.
- Use passthrough styling over css for primevue components

## Planning / Spec-ing

Use tracer bullets when exploring a new feature or change. Build a small, end-to-end slice first so you can validate the approach quickly across the stack, rather than investing heavily in a large implementation up front. This is especially useful for backend API changes, frontend integrations, and Electron-related work where the full path spans multiple layers.

## Verification

Before claiming success:

- backend changes: run the relevant Python validation or start the backend locally
- frontend changes: run the frontend build
- if an API contract changes, verify the UI still works with it

## Style

- Be explicit and practical.
- Prefer clarity over cleverness.
- Write changes that are easy for another contributor to review.

## Pull Requests

- Use the canonical repository as the source of truth and ignore fork remotes unless explicitly instructed otherwise.
- Create feature branches from the canonical default branch, currently `main`, unless a dedicated `develop` branch is introduced for a longer-lived release workflow.
- Open pull requests against the canonical repository and the default branch.
- Before opening a PR, sanity-check that the diff is scoped to your change:
  - `git diff --stat main..<branch>`
- Keep pull request descriptions simple and focused.
- Good PR formats:
  1. `## Problem` and `## Solution`
  2. `## Why?`, `## What?`, and `## How?`
