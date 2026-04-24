"""Tests for genome and evolution components."""

from forage.agent.genome import AgentGenome, PromptSegment


class TestGenome:
    def test_default_genome_has_segments(self, config):
        genome = AgentGenome.default_genome(config)
        assert len(genome.segments) >= 5

    def test_genome_serialization_roundtrip(self, config):
        genome = AgentGenome.default_genome(config)
        json_str = genome.to_json()
        restored = AgentGenome.from_json(json_str)
        assert len(restored.segments) == len(genome.segments)
        assert restored.generation == genome.generation
        assert restored.hash() == genome.hash()

    def test_genome_hash_is_deterministic(self, config):
        genome = AgentGenome.default_genome(config)
        assert genome.hash() == genome.hash()

    def test_genome_hash_changes_on_modification(self, config):
        genome = AgentGenome.default_genome(config)
        h1 = genome.hash()
        copy = genome.copy()
        copy.segments[0].content = "Modified content"
        h2 = copy.hash()
        assert h1 != h2

    def test_mutable_segments_filter(self, config):
        genome = AgentGenome.default_genome(config)
        mutable = genome.get_mutable_segments()
        immutable = [s for s in genome.segments if not s.mutable]
        assert len(mutable) + len(immutable) == len(genome.segments)
        assert len(mutable) > 0
        assert len(immutable) > 0

    def test_system_prompt_assembles_in_priority_order(self, config):
        genome = AgentGenome(segments=[
            PromptSegment(id="low", role="goal", content="Low priority", priority=10),
            PromptSegment(id="high", role="system", content="High priority", priority=90),
            PromptSegment(id="mid", role="constraint", content="Mid priority", priority=50),
        ])
        prompt = genome.to_system_prompt()
        # High should come before mid, mid before low
        assert prompt.index("High priority") < prompt.index("Mid priority")
        assert prompt.index("Mid priority") < prompt.index("Low priority")

    def test_get_segment_by_id(self, config):
        genome = AgentGenome.default_genome(config)
        seg = genome.get_segment("core_identity")
        assert seg is not None
        assert seg.id == "core_identity"

    def test_get_nonexistent_segment_returns_none(self, config):
        genome = AgentGenome.default_genome(config)
        assert genome.get_segment("nonexistent") is None

    def test_copy_is_independent(self, config):
        genome = AgentGenome.default_genome(config)
        copy = genome.copy()
        copy.segments[0].content = "Changed"
        assert genome.segments[0].content != "Changed"


class TestGenomeStore:
    def test_save_and_load(self, initialized_db):
        from forage.evolution.genome_store import GenomeStore
        store = GenomeStore(initialized_db)
        genome = AgentGenome.default_genome(initialized_db)

        # Need to create the agent_state row first
        from forage.infra.database import get_connection
        conn = get_connection(initialized_db)
        conn.execute(
            "INSERT INTO agent_state (id, name, state, genome_json, generation) VALUES (1, 'test', 'idle', ?, 0)",
            (genome.to_json(),))
        conn.commit()
        conn.close()

        loaded = store.load_current()
        assert loaded is not None
        assert loaded.hash() == genome.hash()

    def test_increment_generation(self, initialized_db):
        from forage.evolution.genome_store import GenomeStore
        from forage.infra.database import get_connection
        store = GenomeStore(initialized_db)
        conn = get_connection(initialized_db)
        conn.execute(
            "INSERT INTO agent_state (id, name, state, generation) VALUES (1, 'test', 'idle', 0)")
        conn.commit()
        conn.close()

        assert store.get_generation() == 0
        new_gen = store.increment_generation()
        assert new_gen == 1
        assert store.get_generation() == 1


class TestSurvival:
    def test_stress_high_when_balance_low(self, initialized_db):
        from forage.economy.ledger import Ledger
        from forage.economy.wallet import Wallet
        from forage.safety.limits import SpendingLimiter
        from forage.agent.survival import SurvivalEngine

        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(11.0, "seed")  # just above reserve

        survival = SurvivalEngine(initialized_db, wallet, ledger)
        stress = survival.compute_stress()
        assert stress >= 0.5  # should be stressed

    def test_stress_low_when_balance_high(self, initialized_db):
        from forage.economy.ledger import Ledger
        from forage.economy.wallet import Wallet
        from forage.safety.limits import SpendingLimiter
        from forage.agent.survival import SurvivalEngine

        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(500.0, "seed")

        survival = SurvivalEngine(initialized_db, wallet, ledger)
        stress = survival.compute_stress()
        assert stress <= 0.3

    def test_check_vitals_returns_expected_keys(self, initialized_db):
        from forage.economy.ledger import Ledger
        from forage.economy.wallet import Wallet
        from forage.safety.limits import SpendingLimiter
        from forage.agent.survival import SurvivalEngine

        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(50.0, "seed")

        survival = SurvivalEngine(initialized_db, wallet, ledger)
        vitals = survival.check_vitals()
        assert "balance" in vitals
        assert "runway_days" in vitals
        assert "stress" in vitals
        assert "threat_level" in vitals
        assert "goal_priority" in vitals
        assert "is_alive" in vitals
