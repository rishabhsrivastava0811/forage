# Quick Start

Get an agent running in under 2 minutes.

## 1. Install

```bash
git clone https://github.com/rishabhsrivastava0811/forage.git
cd forage
pip install -e .
```

## 2. Get an API Key

You need at least one LLM API key. The cheapest option:

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create an API key
4. Export it: `export GROQ_API_KEY="your-key-here"`

## 3. Configure

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` — the only required change is your API key (if not using env vars).

Or use a preset:

```bash
cp examples/minimal.yaml config.yaml    # $10 seed, Groq only, conservative
```

## 4. Start

```bash
forage start --seed 50
```

You'll see:

```
Agent 'my-agent' is alive. Balance: $50.00
Wake interval: 30min | Ctrl+C to stop
Cycle | Balance: $50.00 | Runway: 142d | Stress: 0% | Priority: experiment_and_build
  Action: content_creation | Cost: $0.0030 | Revenue: $0.00 | OK
Sleeping 30min...
```

## 5. Monitor

Open the dashboard:

```bash
forage dashboard
```

Or check status from the CLI:

```bash
forage status
forage balance
```

## What Next?

- Read [Configuration Reference](config-reference.md) to tune revenue splits, spending limits, and evolution strategy
- Try `forage evolve` to manually trigger an evolution cycle
- Check the [examples/](../examples/) directory for more config presets
