"""Digital product creation — generates products and lists them on Gumroad."""

import json
import os

import httpx

from forage.capabilities.base import Capability


class DigitalProductCapability(Capability):
    name = "digital_products"

    def can_execute(self, context: dict) -> bool:
        return (self.config.capabilities.digital_products
                and context.get("balance", 0) > self.config.spending.emergency_reserve + 0.10)

    def estimate_cost(self, task: dict) -> float:
        return 0.02

    def estimate_revenue(self, task: dict) -> float:
        return 1.0

    def execute(self, task: dict, wallet, llm) -> dict:
        """Create a digital product and list it on Gumroad for real."""
        niche = task.get("description", "AI productivity tools")

        total_cost = 0.0

        # Step 1: Identify product opportunity
        idea_resp = llm.complete(
            "You create digital products to sell online. "
            f"Suggest one specific product in the niche: {niche}. "
            "It should be something people would pay $1-5 for. "
            "Types: prompt template, cheat sheet, checklist, mini-guide, code snippet pack. "
            "Return JSON with keys: name, description, price (integer, cents — e.g. 200 for $2), "
            "target_audience.",
            tier="routine", max_tokens=300, json_mode=True,
        )
        total_cost += idea_resp.cost_usd
        wallet.spend(idea_resp.cost_usd, "Product: ideation")

        try:
            idea = json.loads(idea_resp.content)
        except json.JSONDecodeError:
            idea = {"name": "AI Prompt Pack", "description": niche,
                    "price": 200, "target_audience": "developers"}

        # Step 2: Create the product content
        create_resp = llm.complete(
            f"Create the full content for this digital product:\n"
            f"Name: {idea.get('name', 'Product')}\n"
            f"Description: {idea.get('description', niche)}\n\n"
            "If it's a prompt template, provide the complete template with instructions. "
            "If it's a guide, provide the full text. If it's a checklist, provide all items. "
            "Make it genuinely valuable — someone should feel it was worth paying for. "
            "Output ONLY the product content, nothing else.",
            tier="routine", max_tokens=1000, temperature=0.7,
        )
        total_cost += create_resp.cost_usd
        wallet.spend(create_resp.cost_usd, "Product: content creation")

        # Step 3: Generate listing description
        listing_resp = llm.complete(
            f"Write a compelling one-paragraph Gumroad product description for:\n"
            f"Name: {idea.get('name', 'Product')}\n"
            f"Content preview: {create_resp.content[:200]}...\n\n"
            "Make it sell. 2-3 sentences max. Output ONLY the description text.",
            tier="routine", max_tokens=150,
        )
        total_cost += listing_resp.cost_usd
        wallet.spend(listing_resp.cost_usd, "Product: listing copy")

        # Step 4: List on Gumroad for real
        gumroad_result = self._list_on_gumroad(
            name=idea.get("name", "AI Product"),
            description=listing_resp.content.strip(),
            price=idea.get("price", 200),
            content=create_resp.content.strip(),
        )

        if gumroad_result["success"]:
            return {
                "success": True,
                "revenue": 0.0,  # Revenue comes later when someone buys
                "cost": total_cost,
                "description": f"Listed on Gumroad: {idea.get('name', 'Product')} "
                               f"(${idea.get('price', 200) / 100:.0f}) — "
                               f"{gumroad_result.get('url', 'live')}",
                "artifacts": {
                    "idea": idea,
                    "content": create_resp.content,
                    "gumroad_url": gumroad_result.get("url"),
                    "gumroad_id": gumroad_result.get("product_id"),
                },
            }
        else:
            return {
                "success": False,
                "revenue": 0.0,
                "cost": total_cost,
                "description": f"Product created but Gumroad listing failed: "
                               f"{gumroad_result.get('error', 'unknown')}",
                "artifacts": {
                    "idea": idea,
                    "content": create_resp.content,
                    "error": gumroad_result.get("error"),
                },
            }

    def _list_on_gumroad(self, name: str, description: str,
                         price: int, content: str) -> dict:
        """Post a product to Gumroad via their API."""
        access_token = os.environ.get("GUMROAD_ACCESS_TOKEN", "")
        if not access_token:
            return {"success": False, "error": "GUMROAD_ACCESS_TOKEN not set in environment"}

        try:
            response = httpx.post(
                "https://api.gumroad.com/v2/products",
                data={
                    "access_token": access_token,
                    "name": name[:200],
                    "description": f"{description[:4000]}\n\n---\n\nPreview:\n{content[:800]}",
                    "price": max(100, int(price)),  # minimum $1 (100 cents)
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    product = data.get("product", {})
                    return {
                        "success": True,
                        "product_id": product.get("id"),
                        "url": product.get("short_url") or product.get("url"),
                    }
                else:
                    return {"success": False,
                            "error": data.get("message", "Gumroad API returned success=false")}
            else:
                return {"success": False,
                        "error": f"Gumroad API HTTP {response.status_code}: {response.text[:200]}"}

        except httpx.TimeoutException:
            return {"success": False, "error": "Gumroad API timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
