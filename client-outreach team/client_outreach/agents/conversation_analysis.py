from typing import Optional
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.llm.base import LLMProvider


INTEREST_KEYWORDS = {
    "high": [
        "interested", "yes", "let's do it", "sounds good", "tell me more",
        "pricing", "how much", "get started", "book a call", "sign me up",
    ],
    "medium": [
        "maybe", "not sure", "send me info", "let me think", "considering",
        "tell me more", "what do you offer", "how does it work",
    ],
    "low": [
        "not interested", "no", "stop", "unsubscribe", "leave me alone",
        "not now", "busy", "don't contact", "remove",
    ],
}

OBJECTION_KEYWORDS = {
    "budget": ["too expensive", "no budget", "can't afford", "cost", "pricing"],
    "timing": ["not now", "busy", "later", "next quarter", "too soon"],
    "authority": ["not my decision", "boss", "owner", "need to ask"],
    "need": ["don't need", "already have", "happy with current", "not a priority"],
}

BUYING_SIGNAL_KEYWORDS = [
    "how much", "pricing", "demo", "book", "schedule", "call",
    "proposal", "contract", "get started", "yes", "interested",
]


class ConversationAnalysisAgent(BaseAgent):
    def __init__(self, llm: Optional[LLMProvider] = None, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm

    def analyze_response(self, lead_id: str, message: str, comm_id: Optional[int] = None) -> dict:
        if self.llm:
            return self._llm_analyze(lead_id, message, comm_id)
        return self._rule_analyze(lead_id, message, comm_id)

    def classify_lead(self, lead_id: str) -> str:
        analyses = self.db.get_analyses(lead_id)
        if not analyses:
            return "Unknown"

        latest = analyses[0]
        interest = latest.get("interest_level", "unknown")
        urgency = latest.get("urgency", "low")

        if interest == "high" and urgency == "high":
            return "Hot Lead"
        elif interest == "high" or (interest == "medium" and urgency == "high"):
            return "Warm Lead"
        else:
            return "Cold Lead"

    def _llm_analyze(self, lead_id: str, message: str, comm_id: Optional[int] = None) -> dict:
        prompt = (
            f"Analyze this sales conversation response and return a JSON object:\n\n"
            f"Response: \"{message}\"\n\n"
            f"Return JSON:\n"
            f"- interest_level: 'high', 'medium', or 'low'\n"
            f"- objections: comma-separated list of objections (or empty string)\n"
            f"- urgency: 'high', 'medium', or 'low'\n"
            f"- buying_signals: comma-separated list of buying signals (or empty string)\n"
            f"- classification: 'Hot Lead', 'Warm Lead', or 'Cold Lead'\n"
            f"- summary: one-sentence summary"
        )
        result = self.llm.generate_json(prompt)
        import json
        try:
            analysis = json.loads(result)
        except (json.JSONDecodeError, TypeError):
            analysis = self._rule_analyze(lead_id, message, comm_id)

        analysis["lead_id"] = lead_id
        analysis["comm_id"] = comm_id
        analysis_id = self.db.add_analysis(analysis)

        classification = analysis.get("classification", "Unknown")
        pipeline_map = {
            "Hot Lead": "Interested",
            "Warm Lead": "Interested",
            "Cold Lead": "Contacted",
        }
        self.db.update_pipeline_stage(lead_id, pipeline_map.get(classification, "Contacted"))

        self.log(f"Analyzed response for {lead_id}: {classification}")
        return analysis

    def _rule_analyze(self, lead_id: str, message: str, comm_id: Optional[int] = None) -> dict:
        msg_lower = message.lower()

        interest = "low"
        if any(kw in msg_lower for kw in INTEREST_KEYWORDS["low"]):
            interest = "low"
        elif any(kw in msg_lower for kw in INTEREST_KEYWORDS["high"]):
            interest = "high"
        elif any(kw in msg_lower for kw in INTEREST_KEYWORDS["medium"]):
            interest = "medium"

        objections = []
        for category, keywords in OBJECTION_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                objections.append(category)

        urgency = "low"
        urgency_keywords = {
            "high": ["asap", "urgent", "quickly", "today", "now", "soon"],
            "medium": ["this week", "next week", "few days", "shortly"],
        }
        for level, keywords in urgency_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                urgency = level
                break

        signals = [s for s in BUYING_SIGNAL_KEYWORDS if s in msg_lower]

        if interest == "high" and not objections:
            classification = "Hot Lead"
        elif interest == "medium" or (interest == "high" and objections):
            classification = "Warm Lead"
        else:
            classification = "Cold Lead"

        pipeline_map = {
            "Hot Lead": "Interested",
            "Warm Lead": "Interested",
            "Cold Lead": "Contacted",
        }
        self.db.update_pipeline_stage(lead_id, pipeline_map.get(classification, "Contacted"))

        analysis = {
            "lead_id": lead_id,
            "comm_id": comm_id,
            "interest_level": interest,
            "objections": ", ".join(objections) if objections else "",
            "urgency": urgency,
            "buying_signals": ", ".join(signals) if signals else "",
            "classification": classification,
            "summary": f"Interest: {interest}, Objections: {objections}, Urgency: {urgency}",
        }
        self.db.add_analysis(analysis)
        self.log(f"Rule-analyzed {lead_id}: {classification}")
        return analysis
