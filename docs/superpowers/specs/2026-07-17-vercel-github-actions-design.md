# Vercel deployment through GitHub Actions

## Goal

Deploy the frontend in `frontend/` to the existing Vercel project
`vnfood_vision` whenever a commit is pushed to `feat/full-stack-app`, without
using Vercel's GitHub App integration.

## Workflow

The repository will contain one GitHub Actions workflow at
`.github/workflows/deploy-vercel.yml`.

It runs on:

- every push to `feat/full-stack-app`;
- `workflow_dispatch`, for an on-demand production deployment.

The job checks out the triggering commit, installs Node.js 22, runs
`npm ci` in `frontend/`, then uses the Vercel CLI to pull production settings,
build, and deploy the prebuilt output to production.

## Configuration and security

The workflow reads `VERCEL_TOKEN` exclusively from the repository's GitHub
Actions secrets. The token is never committed or printed. The Vercel team and
project IDs are workflow configuration values identifying the already-existing
`vnfood_vision` project.

## Failure behavior

If dependency installation, build, Vercel authentication, or deployment fails,
the GitHub Actions run fails and the currently live Vercel deployment remains
unchanged. The run log provides the failure point for troubleshooting.

## Verification

Before committing, validate workflow YAML and run the frontend production build
locally. After the token is configured, verify a workflow run deploys the
current branch commit to Vercel production.
