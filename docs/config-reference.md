# Configuration Reference

All configuration lives in `config.yaml`. See `config.example.yaml` for a fully commented template.

## Sections

### `name`
Your agent's name. Used in logs and the dashboard.

### `seed`
| Field | Type | Default | Description |
|---|---|---|---|
| `amount` | float | 50.00 | Starting balance in USD. Minimum $10 |
| `currency` | string | "USD" | Currency (only USD supported currently) |

### `providers`
List of LLM providers. Agent picks the cheapest that can handle each task.

| Field | Type | Description |
|---|---|---|
| `name` | string | Provider name: groq, openai, anthropic, deepseek, together, ollama |
| `api_key` | string | API key. Supports `${ENV_VAR}` syntax |
| `models` | list | Model IDs to use |
| `tier` | string | `routine` \| `important` \| `complex` \| `critical` |
| `base_url` | string | (optional) Custom API endpoint (for Ollama, etc.) |

**Tier fallback:** If a tier has no provider, the agent falls back to the next higher tier.

### `hardware`
| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | "auto" | `auto` (detect at startup) or `manual` |
| `cpu_cores` | int | auto | Override CPU core count |
| `ram_gb` | float | auto | Override RAM in GB |
| `gpu.enabled` | bool | auto | GPU available? |
| `gpu.vram_gb` | float | auto | GPU VRAM in GB |
| `gpu.count` | int | auto | Number of GPUs |

### `revenue`
#### `revenue.default`
The split applied before any milestones are reached.

| Field | Type | Description |
|---|---|---|
| `owner` | float | Fraction to owner (0.0-1.0) |
| `reinvest` | float | Fraction back to agent |
| `reserve` | float | Fraction to emergency fund |

Must sum to 1.0.

#### `revenue.milestones`
List of milestone stages. Each has `name`, `trigger`, and `split`.

**Trigger fields (all optional, AND logic — all specified must be met):**

| Trigger | Type | Description |
|---|---|---|
| `balance_above` | float | Agent balance exceeds this |
| `consecutive_profitable_days` | int | N consecutive days with net positive |
| `monthly_revenue_above` | float | Rolling 30-day revenue exceeds this |
| `total_earned_above` | float | Lifetime revenue exceeds this |

Milestones are evaluated in order. The **last** milestone whose trigger is fully satisfied wins.

**Emergency override:** If balance drops below 2x `spending.emergency_reserve`, all revenue goes to survival (0% owner payout) regardless of milestone.

### `spending`
| Field | Type | Default | Description |
|---|---|---|---|
| `daily_limit` | float | 5.00 | Max total spend per 24 hours |
| `per_action_limit` | float | 1.00 | Max per single action |
| `emergency_reserve` | float | 10.00 | Never spend below this balance |

**Frugal mode:** When balance < 2x emergency_reserve, daily_limit is automatically halved.

### `payout`
| Field | Type | Default | Description |
|---|---|---|---|
| `method` | string | "manual" | `manual` \| `crypto` \| `stripe` |
| `min_payout` | float | 5.00 | Minimum amount before sending |
| `frequency` | string | "weekly" | `daily` \| `weekly` \| `monthly` |
| `wallet_address` | string | — | For crypto payouts |
| `chain` | string | — | `solana` \| `base` \| `ethereum` |

### `capabilities`
Enable/disable revenue strategies:

| Field | Type | Default | Description |
|---|---|---|---|
| `api_services` | bool | true | Build & deploy API micro-services |
| `digital_products` | bool | true | Create & sell digital products |
| `content_creation` | bool | true | Write blogs, SEO content |
| `inference_service` | bool | false | Sell local model inference (needs GPU) |
| `crypto_yield` | bool | false | DeFi yield farming (risky) |
| `trading` | bool | false | Crypto trading (very risky) |

`allowed_services`: List of domains the agent can access. It **cannot** make requests to unlisted domains.

### `evolution`
| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | true | Enable self-improvement |
| `cycle` | string | "daily" | `hourly` \| `daily` \| `weekly` |
| `strategy` | string | "conservative" | `conservative` \| `balanced` \| `aggressive` |

**Strategies:**
- **conservative:** 5% mutation rate, max 1 change/cycle, requires >5% improvement
- **balanced:** 15% mutation rate, max 3 changes/cycle, stress-responsive
- **aggressive:** 30% mutation rate, unlimited changes, full SOS response under stress

### `schedule`
| Field | Type | Default | Description |
|---|---|---|---|
| `wake_interval_minutes` | int | 30 | How often the agent wakes |
| `active_hours.start` | string | "06:00" | Start of active period |
| `active_hours.end` | string | "23:00" | End of active period |
| `active_hours.timezone` | string | "UTC" | Timezone |

Set `active_hours: null` for 24/7 operation.

### `dashboard`
| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | true | Run local web dashboard |
| `port` | int | 3000 | Port number |
| `host` | string | "127.0.0.1" | Bind address |

### `notifications`
| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | false | Enable notifications |
| `discord_webhook` | string | — | Discord webhook URL |
| `slack_webhook` | string | — | Slack webhook URL |
| `events` | list | — | Events to notify about |

Events: `milestone_reached`, `payout_sent`, `balance_low`, `agent_dying`, `evolution_improvement`, `new_skill_learned`, `first_dollar_earned`
