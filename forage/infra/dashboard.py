"""Local web dashboard — FastAPI server with inline HTML."""

import threading
from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import init_db, get_connection

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

_config: NerfedConfig | None = None

if HAS_FASTAPI:
    app = FastAPI(title="Nerfed Dashboard", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return DASHBOARD_HTML

    @app.get("/api/status")
    async def api_status():
        conn = get_connection(_config)
        try:
            row = conn.execute("SELECT * FROM agent_state WHERE id = 1").fetchone()
            if not row:
                return {"error": "No agent state"}
            ledger_row = conn.execute(
                "SELECT balance_after FROM ledger ORDER BY id DESC LIMIT 1").fetchone()
            balance = ledger_row[0] if ledger_row else 0
            return {
                "name": row["name"], "state": row["state"],
                "balance": balance, "generation": row["generation"],
                "created_at": row["created_at"], "updated_at": row["updated_at"],
            }
        finally:
            conn.close()

    @app.get("/api/balance")
    async def api_balance():
        from forage.economy.ledger import Ledger
        ledger = Ledger(_config)
        return ledger.summary()

    @app.get("/api/activity")
    async def api_activity(limit: int = 50):
        from forage.safety.audit import AuditLog
        audit = AuditLog(_config)
        return audit.tail(limit)

    @app.get("/api/evolution")
    async def api_evolution(limit: int = 20):
        conn = get_connection(_config)
        try:
            rows = conn.execute(
                "SELECT id, timestamp, generation, mutation_type, description, "
                "old_fitness, new_fitness, kept FROM evolution_history "
                "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def get_dashboard_url(config_path: Path) -> str:
    config = load_config(config_path)
    return f"http://{config.dashboard.host}:{config.dashboard.port}"


def start_dashboard(config: NerfedConfig) -> None:
    """Start dashboard in a daemon thread."""
    if not HAS_FASTAPI:
        return
    if not config.dashboard.enabled:
        return
    global _config
    _config = config
    init_db(config)
    thread = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": config.dashboard.host, "port": config.dashboard.port,
                "log_level": "error"},
        daemon=True,
    )
    thread.start()


DASHBOARD_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Nerfed Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}
h1{color:#58a6ff;margin-bottom:20px;font-size:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px}
.card h3{color:#8b949e;font-size:12px;text-transform:uppercase;margin-bottom:8px}
.card .value{font-size:28px;font-weight:700;color:#f0f6fc}
.card .value.green{color:#3fb950}
.card .value.yellow{color:#d29922}
.card .value.red{color:#f85149}
table{width:100%;border-collapse:collapse;margin-top:16px}
th,td{text-align:left;padding:8px 12px;border-bottom:1px solid #21262d}
th{color:#8b949e;font-size:12px;text-transform:uppercase}
td{font-size:13px}
.badge{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge.kept{background:#238636;color:#fff}
.badge.discarded{background:#da3633;color:#fff}
.badge.running{background:#1f6feb;color:#fff}
.badge.paused{background:#d29922;color:#000}
#status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px}
.alive{background:#3fb950}.dead{background:#f85149}
section{margin-bottom:32px}
section h2{color:#c9d1d9;font-size:16px;margin-bottom:12px;border-bottom:1px solid #21262d;padding-bottom:8px}
</style></head><body>
<h1><span id="status-dot" class="alive"></span>Nerfed Dashboard</h1>
<div class="grid">
<div class="card"><h3>Balance</h3><div class="value green" id="balance">$--</div></div>
<div class="card"><h3>State</h3><div class="value" id="state">--</div></div>
<div class="card"><h3>Generation</h3><div class="value" id="generation">--</div></div>
<div class="card"><h3>Revenue</h3><div class="value green" id="revenue">$--</div></div>
<div class="card"><h3>Expenses</h3><div class="value red" id="expenses">$--</div></div>
<div class="card"><h3>Owner Pending</h3><div class="value yellow" id="pending">$--</div></div>
</div>
<section><h2>Activity Feed</h2><table><thead><tr><th>Time</th><th>Type</th><th>Message</th><th>Cost</th><th>Revenue</th></tr></thead><tbody id="activity"></tbody></table></section>
<section><h2>Evolution History</h2><table><thead><tr><th>Gen</th><th>Type</th><th>Description</th><th>Fitness</th><th>Result</th></tr></thead><tbody id="evolution"></tbody></table></section>
<script>
async function refresh(){
try{
let s=await(await fetch('/api/status')).json();
document.getElementById('balance').textContent='$'+s.balance?.toFixed(2);
document.getElementById('state').innerHTML='<span class="badge '+(s.state||'')+'">'+s.state+'</span>';
document.getElementById('generation').textContent=s.generation||0;
document.getElementById('status-dot').className=s.state==='dead'?'dead':'alive';
}catch(e){}
try{
let b=await(await fetch('/api/balance')).json();
document.getElementById('revenue').textContent='$'+(b.total_revenue||0).toFixed(2);
document.getElementById('expenses').textContent='$'+(b.total_expenses||0).toFixed(2);
document.getElementById('pending').textContent='$'+(b.owner_pending||0).toFixed(2);
}catch(e){}
try{
let a=await(await fetch('/api/activity?limit=20')).json();
let html='';
a.forEach(e=>{
let t=e.timestamp?.split('T')[1]?.slice(0,8)||e.timestamp?.slice(11,19)||'';
html+='<tr><td>'+t+'</td><td>'+e.action_type+'</td><td>'+e.message?.slice(0,80)+'</td><td>'+(e.cost_usd>0?'$'+e.cost_usd.toFixed(4):'')+'</td><td>'+(e.revenue_usd>0?'$'+e.revenue_usd.toFixed(2):'')+'</td></tr>';
});
document.getElementById('activity').innerHTML=html;
}catch(e){}
try{
let ev=await(await fetch('/api/evolution')).json();
let html='';
ev.forEach(e=>{
let badge=e.kept?'<span class="badge kept">KEPT</span>':'<span class="badge discarded">DISCARDED</span>';
html+='<tr><td>'+e.generation+'</td><td>'+e.mutation_type+'</td><td>'+(e.description||'').slice(0,60)+'</td><td>'+(e.old_fitness?.toFixed(3)||'-')+' → '+(e.new_fitness?.toFixed(3)||'-')+'</td><td>'+badge+'</td></tr>';
});
document.getElementById('evolution').innerHTML=html;
}catch(e){}
}
refresh();setInterval(refresh,10000);
</script></body></html>"""
