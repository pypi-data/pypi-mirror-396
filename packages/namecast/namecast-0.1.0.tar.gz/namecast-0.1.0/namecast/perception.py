"""AI-powered brand perception forecasting with dynamic personas."""

import json
from dataclasses import dataclass
from typing import Optional
from anthropic import Anthropic


@dataclass
class PersonaResponse:
    """Response from a single persona."""
    persona: str
    age: int
    occupation: str
    evokes: str
    industry_guess: str
    would_trust: bool
    memorable: bool
    memorability_score: int  # 1-10
    professionalism_score: int  # 1-10
    explanation: str


@dataclass
class ComportResponse:
    """Response from the 'does it comport?' follow-up question."""
    persona: str
    comports: str  # "yes", "partially", "no"
    comport_score: int  # 1-10, how well does the product match expectations?
    reaction: str  # "positive_surprise", "matches", "neutral", "jarring_mismatch"
    explanation: str


@dataclass
class TwoPassResponse:
    """Combined response from both passes of persona evaluation."""
    persona: str
    age: int
    occupation: str
    # Pass 1: Name alone
    expected_industry: str
    expected_product: str
    initial_trust: bool
    initial_memorability: int  # 1-10
    initial_professionalism: int  # 1-10
    # Pass 2: Does the actual product comport?
    comports: str  # "yes", "partially", "no"
    comport_score: int  # 1-10
    reaction: str  # "positive_surprise", "matches", "neutral", "jarring_mismatch"
    final_trust: bool  # Did trust change after learning what it does?
    contrast_works: bool  # If there's a mismatch, does it work intentionally?
    explanation: str


@dataclass
class PerceptionAnalysis:
    """Aggregated perception analysis from multiple personas."""
    evokes: str
    industry_association: list[str]
    memorability: str
    persona_responses: list[PersonaResponse]
    consensus_score: float  # 0-1, how much personas agree
    avg_memorability: float  # 1-10 average
    avg_professionalism: float  # 1-10 average
    mission_alignment: Optional[float] = None
    mission_explanation: Optional[str] = None


@dataclass
class TwoPassAnalysis:
    """Analysis from the two-pass 'what would you expect?' + 'does it comport?' evaluation."""
    name: str
    product_description: str
    responses: list[TwoPassResponse]

    # Aggregated metrics
    avg_comport_score: float  # 1-10 average: how well does product match name?
    comport_rate: float  # 0-1: what % said it comports?
    positive_surprise_rate: float  # 0-1: what % were pleasantly surprised?
    contrast_works_rate: float  # 0-1: if mismatch, what % say it works?
    trust_delta: float  # Change in trust from pass 1 to pass 2 (-1 to +1)

    # The key insight
    verdict: str  # "strong_fit", "positive_contrast", "neutral", "jarring_mismatch"
    verdict_explanation: str


# Default personas (used when no mission provided)
DEFAULT_PERSONAS = [
    {
        "name": "Sarah",
        "age": 28,
        "occupation": "Software Engineer",
        "background": "Tech-savvy millennial who works at a startup. Values innovation and authenticity.",
    },
    {
        "name": "Robert",
        "age": 55,
        "occupation": "Small Business Owner",
        "background": "Runs a local accounting firm. Conservative, values trust and reliability.",
    },
    {
        "name": "Maya",
        "age": 34,
        "occupation": "Marketing Director",
        "background": "Works at a Fortune 500 company. Expert in branding, very critical of names.",
    },
    {
        "name": "James",
        "age": 42,
        "occupation": "Investor",
        "background": "VC partner who evaluates hundreds of startups. Focuses on market positioning.",
    },
    {
        "name": "Lisa",
        "age": 22,
        "occupation": "College Student",
        "background": "Gen Z, heavy social media user. Cares about authenticity and social impact.",
    },
]


def generate_dynamic_personas(mission: str, client: Anthropic) -> list[dict]:
    """Generate personas dynamically based on the company mission/description."""

    prompt = f"""Based on this company description, identify 5 specific personas who would interact with this brand:

Company: {mission}

Consider:
- Primary customers/users
- Decision makers who would purchase
- Potential investors
- Industry experts/analysts
- End consumers if B2C

For each persona, provide:
- A realistic first name
- Age (be specific)
- Occupation/role
- Brief background relevant to why they'd encounter this brand

Respond in JSON format:
[
    {{"name": "...", "age": 35, "occupation": "...", "background": "..."}},
    ...
]

Make personas diverse in age, role, and perspective. Be specific and realistic.
Respond ONLY with valid JSON array."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        personas = json.loads(text)
        return personas
    except Exception as e:
        print(f"Error generating dynamic personas: {e}")
        return DEFAULT_PERSONAS


def analyze_with_personas(
    name: str,
    mission: Optional[str] = None,
    num_personas: int = 5,
) -> PerceptionAnalysis:
    """
    Forecast brand perception using multiple AI personas.

    If a mission is provided, generates dynamic personas tailored to the
    company's target audience. Otherwise uses default diverse personas.
    """
    client = Anthropic()

    # Generate dynamic personas if mission provided, otherwise use defaults
    if mission:
        personas = generate_dynamic_personas(mission, client)[:num_personas]
    else:
        personas = DEFAULT_PERSONAS[:num_personas]

    responses = []
    for persona in personas:
        response = _query_persona(client, name, persona, mission)
        if response:
            responses.append(response)

    return _aggregate_responses(responses, name, mission, client)


def _query_persona(
    client: Anthropic,
    name: str,
    persona: dict,
    mission: Optional[str],
) -> Optional[PersonaResponse]:
    """Query a single persona about the brand name."""

    mission_context = ""
    if mission:
        mission_context = f"\n\nThe company's mission is: {mission}"

    prompt = f"""You are {persona['name']}, a {persona['age']}-year-old {persona['occupation']}.
Background: {persona['background']}

You're being asked about a brand name for a company. Answer AS THIS PERSONA, based on their background and perspective.

Brand name: "{name}"{mission_context}

Answer these questions from {persona['name']}'s perspective in JSON format:
{{
    "evokes": "What does this name make you think of? (1-2 sentences)",
    "industry_guess": "What industry/type of company would you guess this is?",
    "would_trust": true/false - Would you trust a company with this name?,
    "memorable": true/false - Is this name memorable to you?,
    "memorability_score": 1-10 rating of how memorable this name is,
    "professionalism_score": 1-10 rating of how professional/credible this sounds,
    "explanation": "Brief explanation of your overall impression (2-3 sentences)"
}}

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        return PersonaResponse(
            persona=persona["name"],
            age=persona["age"],
            occupation=persona["occupation"],
            evokes=result.get("evokes", ""),
            industry_guess=result.get("industry_guess", ""),
            would_trust=result.get("would_trust", True),
            memorable=result.get("memorable", True),
            memorability_score=result.get("memorability_score", 5),
            professionalism_score=result.get("professionalism_score", 5),
            explanation=result.get("explanation", ""),
        )
    except Exception as e:
        print(f"Error querying persona {persona['name']}: {e}")
        return None


def _aggregate_responses(
    responses: list[PersonaResponse],
    name: str,
    mission: Optional[str],
    client: Anthropic,
) -> PerceptionAnalysis:
    """Aggregate persona responses into overall analysis."""

    if not responses:
        # Fallback if no API responses
        return PerceptionAnalysis(
            evokes="professional, modern",
            industry_association=["technology", "business"],
            memorability="high",
            persona_responses=[],
            consensus_score=0.0,
            avg_memorability=5.0,
            avg_professionalism=5.0,
        )

    # Collect all evocations and industries
    all_evokes = [r.evokes for r in responses]
    all_industries = [r.industry_guess for r in responses]

    # Calculate averages
    avg_memorability = sum(r.memorability_score for r in responses) / len(responses)
    avg_professionalism = sum(r.professionalism_score for r in responses) / len(responses)

    # Calculate consensus
    trust_rate = sum(1 for r in responses if r.would_trust) / len(responses)
    memorable_rate = sum(1 for r in responses if r.memorable) / len(responses)
    consensus_score = (trust_rate + memorable_rate) / 2

    # Determine memorability category
    if avg_memorability >= 7:
        memorability = "high"
    elif avg_memorability >= 5:
        memorability = "medium"
    else:
        memorability = "low"

    # Use Claude to synthesize the evocations
    synthesis_prompt = f"""Given these diverse reactions to the brand name "{name}":

{chr(10).join(f'- {r.persona} ({r.age}, {r.occupation}): "{r.evokes}"' for r in responses)}

Synthesize into a single 1-2 sentence summary of what this name evokes. Be specific and concrete."""

    try:
        synthesis = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=150,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        evokes_summary = synthesis.content[0].text.strip()
    except Exception:
        evokes_summary = all_evokes[0] if all_evokes else "professional, modern"

    # Get unique industries
    unique_industries = list(set(all_industries))[:4]

    result = PerceptionAnalysis(
        evokes=evokes_summary,
        industry_association=unique_industries,
        memorability=memorability,
        persona_responses=responses,
        consensus_score=consensus_score,
        avg_memorability=avg_memorability,
        avg_professionalism=avg_professionalism,
    )

    # Mission alignment if provided
    if mission:
        alignment = _evaluate_mission_alignment(client, name, mission, evokes_summary)
        result.mission_alignment = alignment["score"]
        result.mission_explanation = alignment["explanation"]

    return result


def _evaluate_mission_alignment(
    client: Anthropic,
    name: str,
    mission: str,
    evokes: str,
) -> dict:
    """Evaluate how well the name aligns with the mission."""

    prompt = f"""Evaluate how well the brand name "{name}" aligns with this company mission:

Mission: {mission}

The name evokes: {evokes}

Rate the alignment from 1-10 and explain briefly.

Respond in JSON format:
{{
    "score": <1-10>,
    "explanation": "<2-3 sentences>"
}}

Respond ONLY with valid JSON."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)
    except Exception:
        return {"score": 5.0, "explanation": "Unable to evaluate alignment."}


def analyze_two_pass(
    name: str,
    product_description: str,
    personas: Optional[list[dict]] = None,
    num_personas: int = 5,
) -> TwoPassAnalysis:
    """
    Two-pass brand perception analysis:

    Pass 1: "What do you think a company named {name} would do?"
    Pass 2: "{name} does {product_description}. Does that comport?"

    The delta between expectation and reality is the key signal.
    """
    client = Anthropic()

    # Use provided personas or defaults
    if personas is None:
        personas = DEFAULT_PERSONAS[:num_personas]

    responses: list[TwoPassResponse] = []
    for persona in personas:
        response = _query_two_pass(client, name, product_description, persona)
        if response:
            responses.append(response)

    return _aggregate_two_pass(responses, name, product_description, client)


def _query_two_pass(
    client: Anthropic,
    name: str,
    product_description: str,
    persona: dict,
) -> Optional[TwoPassResponse]:
    """Run the two-pass evaluation for a single persona."""

    prompt = f"""You are {persona['name']}, a {persona['age']}-year-old {persona['occupation']}.
Background: {persona['background']}

This is a TWO-PART evaluation. Answer as this persona.

**PART 1: First Impression (name only)**
You see a company called "{name}" but don't know what they do yet.

- What industry would you guess they're in?
- What kind of product/service would you expect?
- Would you trust a company with this name? (yes/no)
- How memorable is this name? (1-10)
- How professional does it sound? (1-10)

**PART 2: Does it Comport?**
Now you learn: {name} {product_description}

- Does the actual product match what you expected from the name? (yes/partially/no)
- How well does the product fit the name? (1-10, where 10 = perfect fit)
- What's your reaction?
  - "positive_surprise" = better/more serious than expected
  - "matches" = exactly what I expected
  - "neutral" = no strong feeling either way
  - "jarring_mismatch" = confusing, doesn't fit
- Now that you know what they do, would you trust them? (yes/no)
- If there's a mismatch between name and product, does it work intentionally (like Mailchimp being serious despite playful name)? (yes/no)

Respond in JSON:
{{
    "expected_industry": "...",
    "expected_product": "...",
    "initial_trust": true/false,
    "initial_memorability": 1-10,
    "initial_professionalism": 1-10,
    "comports": "yes|partially|no",
    "comport_score": 1-10,
    "reaction": "positive_surprise|matches|neutral|jarring_mismatch",
    "final_trust": true/false,
    "contrast_works": true/false,
    "explanation": "2-3 sentences on your overall take"
}}

Respond ONLY with valid JSON."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        result = json.loads(text)

        return TwoPassResponse(
            persona=persona["name"],
            age=persona["age"],
            occupation=persona["occupation"],
            expected_industry=result.get("expected_industry", ""),
            expected_product=result.get("expected_product", ""),
            initial_trust=result.get("initial_trust", True),
            initial_memorability=result.get("initial_memorability", 5),
            initial_professionalism=result.get("initial_professionalism", 5),
            comports=result.get("comports", "partially"),
            comport_score=result.get("comport_score", 5),
            reaction=result.get("reaction", "neutral"),
            final_trust=result.get("final_trust", True),
            contrast_works=result.get("contrast_works", False),
            explanation=result.get("explanation", ""),
        )
    except Exception as e:
        print(f"Error in two-pass query for {persona['name']}: {e}")
        return None


def _aggregate_two_pass(
    responses: list[TwoPassResponse],
    name: str,
    product_description: str,
    client: Anthropic,
) -> TwoPassAnalysis:
    """Aggregate two-pass responses into overall analysis."""

    if not responses:
        return TwoPassAnalysis(
            name=name,
            product_description=product_description,
            responses=[],
            avg_comport_score=5.0,
            comport_rate=0.5,
            positive_surprise_rate=0.0,
            contrast_works_rate=0.0,
            trust_delta=0.0,
            verdict="neutral",
            verdict_explanation="No persona responses available.",
        )

    n = len(responses)

    # Calculate metrics
    avg_comport_score = sum(r.comport_score for r in responses) / n
    comport_rate = sum(1 for r in responses if r.comports == "yes") / n
    positive_surprise_rate = sum(1 for r in responses if r.reaction == "positive_surprise") / n
    jarring_rate = sum(1 for r in responses if r.reaction == "jarring_mismatch") / n

    # For those who saw a mismatch, how many said it works?
    mismatch_responses = [r for r in responses if r.comports != "yes"]
    if mismatch_responses:
        contrast_works_rate = sum(1 for r in mismatch_responses if r.contrast_works) / len(mismatch_responses)
    else:
        contrast_works_rate = 1.0  # No mismatch = contrast "works" trivially

    # Trust delta: did trust increase or decrease after learning what the product does?
    initial_trust_rate = sum(1 for r in responses if r.initial_trust) / n
    final_trust_rate = sum(1 for r in responses if r.final_trust) / n
    trust_delta = final_trust_rate - initial_trust_rate

    # Determine verdict
    if avg_comport_score >= 7 and comport_rate >= 0.6:
        verdict = "strong_fit"
        verdict_explanation = f"The name '{name}' clearly signals what the product does. {int(comport_rate*100)}% of personas found it a natural fit."
    elif positive_surprise_rate >= 0.4 and contrast_works_rate >= 0.5:
        verdict = "positive_contrast"
        verdict_explanation = f"The name '{name}' initially suggests something different, but {int(positive_surprise_rate*100)}% were pleasantly surprised by the product's sophistication. The contrast works."
    elif jarring_rate >= 0.4 or (avg_comport_score < 5 and contrast_works_rate < 0.5):
        verdict = "jarring_mismatch"
        verdict_explanation = f"The name '{name}' creates confusion - {int(jarring_rate*100)}% found the name-product mismatch jarring rather than intentional."
    else:
        verdict = "neutral"
        verdict_explanation = f"Mixed signals - the name '{name}' neither clearly fits nor clearly clashes with the product."

    # Add trust delta to explanation if significant
    if abs(trust_delta) >= 0.2:
        if trust_delta > 0:
            verdict_explanation += f" Trust increased by {int(trust_delta*100)}% after learning what the product does."
        else:
            verdict_explanation += f" Trust decreased by {int(abs(trust_delta)*100)}% after learning what the product does."

    return TwoPassAnalysis(
        name=name,
        product_description=product_description,
        responses=responses,
        avg_comport_score=avg_comport_score,
        comport_rate=comport_rate,
        positive_surprise_rate=positive_surprise_rate,
        contrast_works_rate=contrast_works_rate,
        trust_delta=trust_delta,
        verdict=verdict,
        verdict_explanation=verdict_explanation,
    )
