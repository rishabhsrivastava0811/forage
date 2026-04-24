# Good First Issues

Starter tasks for new contributors. Pick one, open an issue to claim it, and submit a PR.

## Capabilities (New Revenue Strategies)

### 1. Medium Article Publisher
**Difficulty:** Easy
**What:** Add a capability that publishes generated articles to Medium via their API.
**Files:** `forage/capabilities/medium.py`
**Skills:** HTTP API calls, Medium API

### 2. RapidAPI Service Deployer
**Difficulty:** Medium
**What:** Let the agent create and deploy simple API services on RapidAPI marketplace.
**Files:** `forage/capabilities/api_service.py`
**Skills:** RapidAPI provider API, Fly.io deployment

### 3. Substack Newsletter
**Difficulty:** Easy
**What:** Generate and publish a newsletter via Substack API or email.
**Files:** `forage/capabilities/newsletter.py`
**Skills:** HTTP API calls

### 4. Local Inference Service
**Difficulty:** Medium
**What:** Implement the `inference_service` capability — serve the agent's local model as a paid API endpoint.
**Files:** `forage/capabilities/inference_service.py`
**Skills:** FastAPI, Ollama API

## Payouts

### 5. Solana Payout Implementation
**Difficulty:** Medium
**What:** Implement `_crypto_withdraw()` in payout.py for Solana using the `solders` library.
**Files:** `forage/economy/payout.py`
**Skills:** Solana, solders library

### 6. Stripe Payout Implementation
**Difficulty:** Easy
**What:** Implement `_stripe_withdraw()` in payout.py using Stripe Connect.
**Files:** `forage/economy/payout.py`
**Skills:** Stripe API

## Evolution

### 7. Crossover (Sexual Recombination)
**Difficulty:** Medium
**What:** Implement genome crossover — combine the best segments from two different genome versions.
**Files:** `forage/evolution/crossover.py`
**Skills:** Evolutionary algorithms

### 8. Population-Based Evolution
**Difficulty:** Hard
**What:** Run N agent genome variants in parallel, evaluate fitness, keep the best. Island model with migration.
**Files:** `forage/evolution/population.py`
**Skills:** Evolutionary algorithms, parallel processing

## Dashboard

### 9. Fitness Chart Over Time
**Difficulty:** Easy
**What:** Add a line chart to the dashboard showing fitness score progression across generations.
**Files:** `forage/infra/dashboard.py` (update `DASHBOARD_HTML`)
**Skills:** Chart.js or inline SVG

### 10. Balance Runway Chart
**Difficulty:** Easy
**What:** Add a chart showing projected balance over time (extrapolating current spend/earn rate).
**Files:** `forage/infra/dashboard.py`
**Skills:** JavaScript, basic math

## Notifications

### 11. Telegram Notification Support
**Difficulty:** Easy
**What:** Implement Telegram bot notifications for agent events using the Bot API.
**Files:** New file `forage/infra/notifications.py`
**Skills:** Telegram Bot API, httpx

### 12. Discord Webhook Notifications
**Difficulty:** Easy
**What:** Send agent events to a Discord channel via webhook.
**Files:** `forage/infra/notifications.py`
**Skills:** Discord webhooks, httpx

## Infrastructure

### 13. Weekly Email Summary
**Difficulty:** Easy
**What:** Generate and send a weekly summary email with balance, revenue, evolution progress.
**Files:** `forage/infra/notifications.py`
**Skills:** Email sending (resend.com or SMTP)

### 14. Agent Health Monitoring Endpoint
**Difficulty:** Easy
**What:** Add a `/api/health` endpoint to the dashboard that external monitoring tools (UptimeRobot) can ping.
**Files:** `forage/infra/dashboard.py`
**Skills:** FastAPI

### 15. Genome Export/Import Sharing Hub
**Difficulty:** Medium
**What:** Build a simple web page or CLI flow where users can share evolved genomes with each other.
**Files:** New flow in CLI + optional web component
**Skills:** JSON, CLI, optionally GitHub Gists API
