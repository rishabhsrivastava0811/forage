"""Content creation capability — generates articles and blog posts."""

from forage.capabilities.base import Capability


class ContentCapability(Capability):
    name = "content_creation"

    def can_execute(self, context: dict) -> bool:
        return (self.config.capabilities.content_creation
                and context.get("balance", 0) > self.config.spending.emergency_reserve + 0.05)

    def estimate_cost(self, task: dict) -> float:
        return 0.005  # ~5 LLM calls at routine tier

    def estimate_revenue(self, task: dict) -> float:
        return 0.0  # conservative — content earns over time, not immediately

    def execute(self, task: dict, wallet, llm) -> dict:
        """Generate a piece of content. For MVP, content is stored but not published."""
        niche = task.get("description", "technology and AI tools")

        total_cost = 0.0

        # Step 1: Generate topic
        topic_resp = llm.complete(
            f"Generate one specific, SEO-friendly blog post topic about: {niche}. "
            f"The topic should target a problem people search for. "
            f"Return only the topic title, nothing else.",
            tier="routine", max_tokens=100,
        )
        total_cost += topic_resp.cost_usd
        topic = topic_resp.content.strip()

        # Spend check before the expensive step
        spend_result = wallet.spend(topic_resp.cost_usd, "Content: topic generation",
                                     details={"topic": topic})
        if not spend_result.success:
            return {"success": False, "revenue": 0, "cost": 0,
                    "description": f"Cannot afford: {spend_result.reason}"}

        # Step 2: Write article
        article_resp = llm.complete(
            f"Write a concise, valuable blog post about: {topic}\n\n"
            f"Requirements:\n"
            f"- 300-500 words\n"
            f"- Actionable advice\n"
            f"- Clear structure with headers\n"
            f"- No filler or fluff\n"
            f"Write the full article.",
            tier="important", max_tokens=800, temperature=0.8,
        )
        total_cost += article_resp.cost_usd
        article = article_resp.content.strip()

        wallet.spend(article_resp.cost_usd, "Content: article writing",
                     details={"topic": topic, "length": len(article)})

        # Step 3: Generate metadata
        meta_resp = llm.complete(
            f"For this article titled '{topic}', generate:\n"
            f"1. SEO meta description (under 160 chars)\n"
            f"2. 5 relevant tags\n"
            f"3. One-sentence summary\n"
            f"Format as JSON.",
            tier="routine", max_tokens=200, json_mode=True,
        )
        total_cost += meta_resp.cost_usd
        wallet.spend(meta_resp.cost_usd, "Content: metadata generation")

        # TODO: Publish to Cloudflare Pages / Medium / blog platform
        # For MVP, the content is just stored as an artifact

        return {
            "success": True,
            "revenue": 0.0,  # No immediate revenue from content
            "cost": total_cost,
            "description": f"Created article: {topic}",
            "artifacts": {
                "topic": topic,
                "article": article,
                "metadata": meta_resp.content,
                "word_count": len(article.split()),
            },
        }
