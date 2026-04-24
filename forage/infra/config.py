"""Configuration loader for Nerfed agent."""

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SeedConfig:
    amount: float
    currency: str = "USD"


@dataclass
class ProviderConfig:
    name: str
    api_key: str
    models: list[str]
    tier: str  # routine | important | complex | critical
    base_url: str | None = None


@dataclass
class HardwareConfig:
    mode: str = "auto"
    cpu_cores: int | None = None
    ram_gb: float | None = None
    gpu_enabled: bool = False
    gpu_vram_gb: float | None = None
    gpu_count: int = 0


@dataclass
class SplitConfig:
    owner: float
    reinvest: float
    reserve: float


@dataclass
class MilestoneTrigger:
    balance_above: float | None = None
    consecutive_profitable_days: int | None = None
    monthly_revenue_above: float | None = None
    total_earned_above: float | None = None
    skills_count_above: int | None = None
    generation_above: int | None = None


@dataclass
class MilestoneConfig:
    name: str
    trigger: MilestoneTrigger
    split: SplitConfig


@dataclass
class RevenueConfig:
    default: SplitConfig
    milestones: list[MilestoneConfig] = field(default_factory=list)


@dataclass
class SpendingConfig:
    daily_limit: float = 5.0
    per_action_limit: float = 1.0
    emergency_reserve: float = 10.0


@dataclass
class PayoutConfig:
    method: str = "manual"
    min_payout: float = 5.0
    frequency: str = "weekly"
    wallet_address: str | None = None
    chain: str | None = None
    stripe_account_id: str | None = None


@dataclass
class CapabilitiesConfig:
    api_services: bool = True
    digital_products: bool = True
    content_creation: bool = True
    inference_service: bool = False
    crypto_yield: bool = False
    trading: bool = False
    freelancing: bool = False
    allowed_services: list[str] = field(default_factory=list)
    deploy_targets: list[str] = field(default_factory=list)


@dataclass
class EvolutionConfig:
    enabled: bool = True
    cycle: str = "daily"
    strategy: str = "conservative"


@dataclass
class ScheduleConfig:
    wake_interval_minutes: int = 30
    active_hours: dict | None = None


@dataclass
class DashboardConfig:
    enabled: bool = True
    port: int = 3000
    host: str = "127.0.0.1"


@dataclass
class LoggingConfig:
    level: str = "info"
    file: str = "logs/nerfed.log"
    max_size_mb: int = 50


@dataclass
class NotificationsConfig:
    enabled: bool = False
    events: list[str] = field(default_factory=list)
    discord_webhook: str | None = None
    slack_webhook: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None


@dataclass
class NerfedConfig:
    name: str
    seed: SeedConfig
    providers: list[ProviderConfig]
    hardware: HardwareConfig
    revenue: RevenueConfig
    spending: SpendingConfig
    payout: PayoutConfig
    capabilities: CapabilitiesConfig
    evolution: EvolutionConfig
    schedule: ScheduleConfig
    dashboard: DashboardConfig
    logging: LoggingConfig
    notifications: NotificationsConfig
    config_path: Path = field(default_factory=lambda: Path("config.yaml"))
    data_dir: Path = field(default_factory=lambda: Path("data"))


def _substitute_env_vars(raw: str) -> str:
    """Replace ${VAR_NAME} with environment variable values."""
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")
    return re.sub(r'\$\{(\w+)\}', replacer, raw)


def _resolve_data_dir(config_path: Path) -> Path:
    env_dir = os.environ.get("FORAGE_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return config_path.parent / "data"


def _parse_split(raw: dict) -> SplitConfig:
    return SplitConfig(
        owner=raw.get("owner", 0.0),
        reinvest=raw.get("reinvest", 1.0),
        reserve=raw.get("reserve", 0.0),
    )


def _parse_trigger(raw: dict) -> MilestoneTrigger:
    return MilestoneTrigger(
        balance_above=raw.get("balance_above"),
        consecutive_profitable_days=raw.get("consecutive_profitable_days"),
        monthly_revenue_above=raw.get("monthly_revenue_above"),
        total_earned_above=raw.get("total_earned_above"),
        skills_count_above=raw.get("skills_count_above"),
        generation_above=raw.get("generation_above"),
    )


def detect_hardware() -> HardwareConfig:
    """Auto-detect available hardware."""
    cpu_cores = os.cpu_count() or 1
    ram_gb = None
    try:
        import sys
        if sys.platform == "linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        ram_gb = round(kb / 1024 / 1024, 1)
                        break
        elif sys.platform == "darwin":
            result = subprocess.run(["sysctl", "-n", "hw.memsize"],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ram_gb = round(int(result.stdout.strip()) / 1024**3, 1)
    except Exception:
        pass

    gpu_enabled = False
    gpu_vram_gb = None
    gpu_count = 0
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,count", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            gpu_count = len(lines)
            gpu_enabled = True
            gpu_vram_gb = round(int(lines[0].split(",")[0].strip()) / 1024, 1)
    except Exception:
        pass

    return HardwareConfig(
        mode="auto",
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        gpu_enabled=gpu_enabled,
        gpu_vram_gb=gpu_vram_gb,
        gpu_count=gpu_count,
    )


def load_config(config_path: Path) -> NerfedConfig:
    """Load YAML config, substitute env vars, validate, return NerfedConfig."""
    config_path = Path(config_path).resolve()
    raw_text = config_path.read_text()
    raw_text = _substitute_env_vars(raw_text)
    raw = yaml.safe_load(raw_text)

    data_dir = _resolve_data_dir(config_path)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Parse providers
    providers = []
    for p in raw.get("providers", []):
        providers.append(ProviderConfig(
            name=p["name"],
            api_key=p.get("api_key", ""),
            models=p.get("models", []),
            tier=p.get("tier", "routine"),
            base_url=p.get("base_url"),
        ))

    # Parse hardware
    hw_raw = raw.get("hardware", {})
    if hw_raw.get("mode") == "manual":
        gpu_raw = hw_raw.get("gpu", {})
        hardware = HardwareConfig(
            mode="manual",
            cpu_cores=hw_raw.get("cpu_cores"),
            ram_gb=hw_raw.get("ram_gb"),
            gpu_enabled=gpu_raw.get("enabled", False) if gpu_raw else False,
            gpu_vram_gb=gpu_raw.get("vram_gb") if gpu_raw else None,
            gpu_count=gpu_raw.get("count", 0) if gpu_raw else 0,
        )
    else:
        hardware = detect_hardware()

    # Parse revenue
    rev_raw = raw.get("revenue", {})
    milestones = []
    for m in rev_raw.get("milestones", []):
        milestones.append(MilestoneConfig(
            name=m["name"],
            trigger=_parse_trigger(m.get("trigger", {})),
            split=_parse_split(m.get("split", {})),
        ))
    revenue = RevenueConfig(
        default=_parse_split(rev_raw.get("default", {"owner": 0, "reinvest": 1, "reserve": 0})),
        milestones=milestones,
    )

    # Parse spending
    sp_raw = raw.get("spending", {})
    spending = SpendingConfig(
        daily_limit=sp_raw.get("daily_limit", 5.0),
        per_action_limit=sp_raw.get("per_action_limit", 1.0),
        emergency_reserve=sp_raw.get("emergency_reserve", 10.0),
    )

    # Parse payout
    po_raw = raw.get("payout", {})
    payout = PayoutConfig(
        method=po_raw.get("method", "manual"),
        min_payout=po_raw.get("min_payout", 5.0),
        frequency=po_raw.get("frequency", "weekly"),
        wallet_address=po_raw.get("wallet_address"),
        chain=po_raw.get("chain"),
        stripe_account_id=po_raw.get("stripe_account_id"),
    )

    # Parse capabilities
    cap_raw = raw.get("capabilities", {})
    capabilities = CapabilitiesConfig(
        api_services=cap_raw.get("api_services", True),
        digital_products=cap_raw.get("digital_products", True),
        content_creation=cap_raw.get("content_creation", True),
        inference_service=cap_raw.get("inference_service", False),
        crypto_yield=cap_raw.get("crypto_yield", False),
        trading=cap_raw.get("trading", False),
        freelancing=cap_raw.get("freelancing", False),
        allowed_services=cap_raw.get("allowed_services", []),
        deploy_targets=cap_raw.get("deploy_targets", []),
    )

    # Parse evolution
    ev_raw = raw.get("evolution", {})
    evolution = EvolutionConfig(
        enabled=ev_raw.get("enabled", True),
        cycle=ev_raw.get("cycle", "daily"),
        strategy=ev_raw.get("strategy", "conservative"),
    )

    # Parse schedule
    sc_raw = raw.get("schedule", {})
    schedule = ScheduleConfig(
        wake_interval_minutes=sc_raw.get("wake_interval_minutes", 30),
        active_hours=sc_raw.get("active_hours"),
    )

    # Parse dashboard
    db_raw = raw.get("dashboard", {})
    dashboard = DashboardConfig(
        enabled=db_raw.get("enabled", True),
        port=db_raw.get("port", 3000),
        host=db_raw.get("host", "127.0.0.1"),
    )

    # Parse logging
    lg_raw = raw.get("logging", {})
    logging_cfg = LoggingConfig(
        level=lg_raw.get("level", "info"),
        file=lg_raw.get("file", "logs/nerfed.log"),
        max_size_mb=lg_raw.get("max_size_mb", 50),
    )

    # Parse notifications
    nt_raw = raw.get("notifications", {})
    notifications = NotificationsConfig(
        enabled=nt_raw.get("enabled", False),
        events=nt_raw.get("events", []),
        discord_webhook=nt_raw.get("discord_webhook"),
        slack_webhook=nt_raw.get("slack_webhook"),
        telegram_bot_token=nt_raw.get("telegram_bot_token"),
        telegram_chat_id=nt_raw.get("telegram_chat_id"),
    )

    seed_raw = raw.get("seed", {})
    config = NerfedConfig(
        name=raw.get("name", "forage-agent"),
        seed=SeedConfig(amount=seed_raw.get("amount", 50.0), currency=seed_raw.get("currency", "USD")),
        providers=providers,
        hardware=hardware,
        revenue=revenue,
        spending=spending,
        payout=payout,
        capabilities=capabilities,
        evolution=evolution,
        schedule=schedule,
        dashboard=dashboard,
        logging=logging_cfg,
        notifications=notifications,
        config_path=config_path,
        data_dir=data_dir,
    )

    _validate(config)
    return config


def _validate(config: NerfedConfig) -> None:
    """Validate configuration values."""
    if config.seed.amount < 10.0:
        raise ValueError(f"Seed amount must be >= $10.00, got ${config.seed.amount}")
    if not config.providers:
        raise ValueError("At least one LLM provider must be configured")
    for ms in config.revenue.milestones:
        total = ms.split.owner + ms.split.reinvest + ms.split.reserve
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Milestone '{ms.name}' split must sum to 1.0, got {total}")
    default_total = config.revenue.default.owner + config.revenue.default.reinvest + config.revenue.default.reserve
    if abs(default_total - 1.0) > 0.01:
        raise ValueError(f"Default revenue split must sum to 1.0, got {default_total}")
