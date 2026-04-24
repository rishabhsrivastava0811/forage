"""CLI entry point for nerfed."""

import click
from pathlib import Path


@click.group()
@click.option("--config", default="config.yaml", help="Path to config file")
@click.pass_context
def main(ctx, config):
    """Nerfed — An AI agent that survives, earns, and evolves on its own."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = Path(config)


@main.command()
@click.option("--seed", type=float, help="Override seed amount from config")
@click.pass_context
def start(ctx, seed):
    """Start the agent."""
    from forage.agent.core import Agent

    config_path = ctx.obj["config_path"]
    agent = Agent.from_config(config_path)
    if seed:
        agent.config.seed.amount = seed
    click.echo(f"Starting agent '{agent.config.name}' with ${agent.config.seed.amount:.2f} seed...")
    agent.run()


@main.command()
@click.pass_context
def status(ctx):
    """Show agent status."""
    from forage.agent.core import Agent

    agent = Agent.from_config(ctx.obj["config_path"])
    status = agent.get_status()
    click.echo(f"Agent: {status['name']}")
    click.echo(f"State: {status['state']}")
    click.echo(f"Balance: ${status['balance']:.2f}")
    click.echo(f"Runway: {status['runway_days']} days")
    click.echo(f"Milestone: {status['current_milestone']}")
    click.echo(f"Total earned: ${status['total_earned']:.2f}")
    click.echo(f"Total paid to owner: ${status['total_paid_owner']:.2f}")
    click.echo(f"Generation: {status['generation']}")
    click.echo(f"Uptime: {status['uptime_days']} days")


@main.command()
@click.pass_context
def balance(ctx):
    """Show detailed balance and financial history."""
    from forage.economy.ledger import Ledger

    ledger = Ledger.load(ctx.obj["config_path"])
    summary = ledger.summary()
    click.echo(f"Current balance: ${summary['balance']:.2f}")
    click.echo(f"Emergency reserve: ${summary['emergency_reserve']:.2f}")
    click.echo(f"Available: ${summary['available']:.2f}")
    click.echo(f"Total revenue: ${summary['total_revenue']:.2f}")
    click.echo(f"Total expenses: ${summary['total_expenses']:.2f}")
    click.echo(f"Total owner payouts: ${summary['total_owner_payouts']:.2f}")
    click.echo(f"Owner pending: ${summary['owner_pending']:.2f}")
    click.echo("\nLast 10 transactions:")
    for tx in summary["recent_transactions"]:
        direction = "+" if tx["amount"] > 0 else "-"
        click.echo(f"  {tx['timestamp']}  {direction}${abs(tx['amount']):.2f}  {tx['description']}")


@main.command()
@click.argument("amount", type=float)
@click.pass_context
def withdraw(ctx, amount):
    """Withdraw your accumulated share."""
    from forage.economy.payout import PayoutManager

    payout = PayoutManager.load(ctx.obj["config_path"])
    result = payout.withdraw(amount)
    if result["success"]:
        click.echo(f"Withdrawn ${amount:.2f} via {result['method']}")
        if result.get("tx_hash"):
            click.echo(f"Transaction: {result['tx_hash']}")
    else:
        click.echo(f"Withdrawal failed: {result['error']}")


@main.command()
@click.pass_context
def pause(ctx):
    """Pause the agent (keeps state, stops spending)."""
    from forage.agent.core import Agent

    agent = Agent.from_config(ctx.obj["config_path"])
    agent.pause()
    click.echo("Agent paused. State preserved. No spending will occur.")
    click.echo("Resume with: nerfed resume")


@main.command()
@click.pass_context
def resume(ctx):
    """Resume a paused agent."""
    from forage.agent.core import Agent

    agent = Agent.from_config(ctx.obj["config_path"])
    agent.resume()
    click.echo("Agent resumed.")


@main.command()
@click.confirmation_option(prompt="Are you sure? This archives the agent permanently.")
@click.pass_context
def kill(ctx):
    """Kill the agent permanently. Archives state."""
    from forage.agent.core import Agent

    agent = Agent.from_config(ctx.obj["config_path"])
    archive_path = agent.kill()
    click.echo(f"Agent killed. State archived to: {archive_path}")
    click.echo(f"Remaining balance: ${agent.get_status()['balance']:.2f}")


@main.command()
@click.pass_context
def dashboard(ctx):
    """Open the local dashboard in your browser."""
    import webbrowser
    from forage.infra.dashboard import get_dashboard_url

    url = get_dashboard_url(ctx.obj["config_path"])
    click.echo(f"Dashboard: {url}")
    webbrowser.open(url)


@main.command()
@click.pass_context
def logs(ctx):
    """Tail the agent's activity log."""
    from forage.safety.audit import AuditLog

    audit = AuditLog.load(ctx.obj["config_path"])
    for entry in audit.tail(50):
        click.echo(f"[{entry['timestamp']}] {entry['level']} | {entry['message']}")


@main.command()
@click.pass_context
def evolve(ctx):
    """Manually trigger an evolution cycle."""
    from forage.evolution.engine import EvolutionEngine

    engine = EvolutionEngine.load(ctx.obj["config_path"])
    result = engine.run_cycle()
    if result["improved"]:
        click.echo(f"Evolution: KEPT — {result['description']}")
        click.echo(f"Fitness: {result['old_fitness']:.3f} → {result['new_fitness']:.3f}")
    else:
        click.echo(f"Evolution: DISCARDED — {result['description']}")
        click.echo(f"No improvement (score: {result['new_fitness']:.3f} vs {result['old_fitness']:.3f})")


@main.command()
@click.argument("amount", type=float)
@click.pass_context
def fund(ctx, amount):
    """Add more funds to the agent."""
    from forage.economy.wallet import Wallet

    wallet = Wallet.load(ctx.obj["config_path"])
    wallet.deposit(amount, source="owner_deposit")
    click.echo(f"Deposited ${amount:.2f}. New balance: ${wallet.balance:.2f}")


@main.command("export-genome")
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
@click.pass_context
def export_genome(ctx, output):
    """Export the agent's evolved genome as JSON."""
    from forage.evolution.genome_store import GenomeStore
    from forage.infra.config import load_config
    from forage.infra.database import init_db

    config = load_config(ctx.obj["config_path"])
    init_db(config)
    store = GenomeStore(config)
    genome = store.load_current()
    if not genome:
        click.echo("No genome found. Start the agent first.", err=True)
        raise SystemExit(1)

    json_str = genome.to_json()
    if output:
        Path(output).write_text(json_str)
        click.echo(f"Genome exported to {output} (generation {genome.generation}, hash {genome.hash()})")
    else:
        click.echo(json_str)


@main.command("import-genome")
@click.argument("genome_file", type=click.Path(exists=True))
@click.pass_context
def import_genome(ctx, genome_file):
    """Import a genome from a JSON file."""
    from forage.agent.genome import AgentGenome
    from forage.evolution.genome_store import GenomeStore
    from forage.infra.config import load_config
    from forage.infra.database import init_db

    config = load_config(ctx.obj["config_path"])
    init_db(config)

    json_str = Path(genome_file).read_text()
    genome = AgentGenome.from_json(json_str)
    store = GenomeStore(config)
    genome_hash = store.save_genome(genome)
    click.echo(f"Genome imported: generation {genome.generation}, hash {genome_hash}")
    click.echo(f"Segments: {len(genome.segments)}, mutable: {len(genome.get_mutable_segments())}")


if __name__ == "__main__":
    main()
