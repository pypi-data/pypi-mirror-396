"""Brand name oracle - core forecasting logic."""

from dataclasses import dataclass, field, asdict
from typing import Optional
import os
import json
import whois
import httpx

# Cache for domain pricing to avoid repeated API calls
_pricing_cache: dict = {}


@dataclass
class SimilarCompany:
    """A similar-sounding existing company."""
    name: str
    similarity_score: float  # 0-1, higher = more similar
    industry: str
    reason: str  # Why it's similar (phonetic, spelling, etc.)


@dataclass
class SimilarCompaniesResult:
    """Result of similar companies search."""
    matches: list[SimilarCompany]
    confusion_risk: str  # "low", "medium", "high"


@dataclass
class SocialHandleResult:
    """Result for a single social platform."""
    platform: str
    exact_available: bool  # Is @name available?
    best_alternative: Optional[str] = None  # Best available alternative handle
    alternatives_checked: list[str] = field(default_factory=list)  # All alternatives checked


@dataclass
class PronunciationResult:
    """Result of pronunciation analysis."""
    score: float
    syllables: int
    spelling_difficulty: str  # "easy", "medium", "hard"


@dataclass
class PerceptionResult:
    """Result of AI perception analysis."""
    evokes: str
    industry_association: list[str]
    memorability: str
    mission_alignment: Optional[float] = None


@dataclass
class BrandScopeResult:
    """Result of brand scope analysis."""
    narrowness: float  # 1-10, higher = more expansive
    expansion_potential: float  # 1-10
    vision_alignment: float  # 1-10
    assessment: str  # Text explanation


@dataclass
class DomainStatus:
    """Detailed domain status."""
    available: bool  # Not registered
    parked: bool  # Registered but no active site
    active: bool  # Has live website
    status: str  # "available", "parked", "active"


@dataclass
class EvaluationResult:
    """Complete brand evaluation result."""
    name: str
    overall_score: float
    domain_score: float
    social_score: float
    pronunciation_score: float
    international_score: float
    similar_companies_score: float = 100.0
    brand_scope_score: float = 100.0
    tagline_score: float = 100.0

    domains: dict[str, bool] = field(default_factory=dict)
    domain_details: dict[str, DomainStatus] = field(default_factory=dict)
    domain_pricing: dict[str, dict] = field(default_factory=dict)
    social: dict[str, SocialHandleResult] = field(default_factory=dict)
    pronunciation: Optional[PronunciationResult] = None
    international: dict[str, dict] = field(default_factory=dict)
    perception: Optional[PerceptionResult] = None
    similar_companies: Optional[SimilarCompaniesResult] = None
    brand_scope: Optional[BrandScopeResult] = None
    taglines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_markdown(self) -> str:
        """Export as markdown report."""
        lines = [
            f"## Brand Evaluation: {self.name}",
            "",
            f"### Overall Score: {self.overall_score:.0f}/100",
            "",
            "### Domain Availability",
            "| TLD | Status |",
            "|-----|--------|",
        ]
        for tld, available in self.domains.items():
            status = "Available" if available else "Taken"
            lines.append(f"| {tld} | {status} |")

        lines.extend([
            "",
            "### Social Handles",
            "| Platform | @exact | Best Alternative |",
            "|----------|--------|------------------|",
        ])
        for platform, result in self.social.items():
            if isinstance(result, SocialHandleResult):
                exact = "✓" if result.exact_available else "✗"
                alt = result.best_alternative or "-"
                lines.append(f"| {platform} | {exact} | {alt} |")
            else:
                # Backwards compat with old bool format
                status = "✓" if result else "✗"
                lines.append(f"| {platform} | {status} | - |")

        if self.pronunciation:
            lines.extend([
                "",
                f"### Pronunciation Score: {self.pronunciation.score:.1f}/10",
                f"- Syllables: {self.pronunciation.syllables}",
                f"- Spelling: {self.pronunciation.spelling_difficulty}",
            ])

        if self.similar_companies and self.similar_companies.matches:
            lines.extend([
                "",
                f"### Similar Companies: {len(self.similar_companies.matches)} found",
                "",
            ])
            for company in self.similar_companies.matches:
                lines.append(f"- **{company.name}** ({company.industry}) - {company.reason}")

        return "\n".join(lines)


def get_domain_pricing(tlds: Optional[list[str]] = None) -> dict[str, dict]:
    """Get domain pricing from Porkbun API.

    Args:
        tlds: Optional list of TLDs to filter (e.g., ["ai", "com", "io"]).
              If None, returns all available pricing.

    Returns:
        Dict mapping TLD (without dot) to pricing info:
        {"ai": {"registration": "72.40", "renewal": "72.40", ...}, ...}
    """
    global _pricing_cache

    # Return cached results if available
    if _pricing_cache:
        if tlds:
            return {k: v for k, v in _pricing_cache.items() if k in tlds}
        return _pricing_cache

    try:
        response = httpx.get(
            "https://api.porkbun.com/api/json/v3/pricing/get",
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "SUCCESS" and "pricing" in data:
            _pricing_cache.update(data["pricing"])
            if tlds:
                return {k: v for k, v in _pricing_cache.items() if k in tlds}
            return _pricing_cache
    except Exception as e:
        print(f"Failed to fetch domain pricing: {e}")

    return {}


def whois_lookup(domain: str) -> Optional[dict]:
    """Look up WHOIS info for a domain. Returns None if not registered."""
    try:
        w = whois.whois(domain)
        if w.domain_name:
            return {"domain_name": w.domain_name, "creation_date": w.creation_date}
        return None
    except whois.exceptions.WhoisDomainNotFoundError:
        return None  # Domain is available
    except Exception:
        return None  # Treat errors as "unknown" (assume available)


class BrandEvaluator:
    """Main brand name evaluator."""

    DEFAULT_TLDS = [".com", ".io", ".co", ".ai", ".app"]
    DEFAULT_PLATFORMS = ["twitter", "instagram", "linkedin", "tiktok", "github"]

    def __init__(self):
        pass

    def evaluate(
        self,
        name: str,
        mission: Optional[str] = None,
        planned_domain: Optional[str] = None,
    ) -> EvaluationResult:
        """Run full evaluation on a brand name.

        Args:
            name: The brand name to evaluate
            mission: Optional company mission for alignment scoring
            planned_domain: The domain you plan to use (e.g., "farness.ai") -
                           used to suggest matching social handle alternatives
        """
        domains, domain_details = self.check_domains_detailed(name)
        social = self.check_social(name, planned_domain)
        pronunciation = self.analyze_pronunciation(name)
        international = self.check_international(name)
        perception = self.analyze_perception(name, mission)
        similar_companies = self.find_similar_companies(name)
        brand_scope = self.analyze_brand_scope(name, mission)
        taglines = self.generate_taglines(name, mission) if mission else []

        # Get domain pricing for checked TLDs
        tlds_to_price = [tld.lstrip(".") for tld in self.DEFAULT_TLDS]
        domain_pricing = get_domain_pricing(tlds_to_price)

        # Calculate scores
        domain_score = self._calc_domain_score_detailed(domain_details)
        social_score = self._calc_social_score(social)
        pronunciation_score = pronunciation.score * 10  # 0-10 -> 0-100
        international_score = self._calc_international_score(international)
        similar_companies_score = self._calc_similar_companies_score(similar_companies)
        brand_scope_score = self._calc_brand_scope_score(brand_scope)
        tagline_score = 70.0 if taglines else 50.0  # Placeholder

        # Weighted overall score
        overall_score = (
            domain_score * 0.20
            + social_score * 0.05
            + pronunciation_score * 0.10
            + international_score * 0.10
            + similar_companies_score * 0.20
            + brand_scope_score * 0.20
            + tagline_score * 0.10
            + (perception.mission_alignment or 7) * 0.5  # 0-10 -> 0-5 pts
        )

        return EvaluationResult(
            name=name,
            overall_score=overall_score,
            domain_score=domain_score,
            social_score=social_score,
            pronunciation_score=pronunciation_score,
            international_score=international_score,
            similar_companies_score=similar_companies_score,
            brand_scope_score=brand_scope_score,
            tagline_score=tagline_score,
            domains=domains,
            domain_details=domain_details,
            domain_pricing=domain_pricing,
            social=social,
            pronunciation=pronunciation,
            international=international,
            perception=perception,
            similar_companies=similar_companies,
            brand_scope=brand_scope,
            taglines=taglines,
        )

    def check_domains(self, name: str) -> dict[str, bool]:
        """Check domain availability across TLDs (simple version)."""
        result = {}
        name_lower = name.lower()
        for tld in self.DEFAULT_TLDS:
            domain = f"{name_lower}{tld}"
            info = whois_lookup(domain)
            result[tld] = info is None  # Available if no WHOIS record
        return result

    def check_domains_detailed(self, name: str) -> tuple[dict[str, bool], dict[str, DomainStatus]]:
        """Check domain availability with live site detection.

        Returns:
            Tuple of (simple bool dict for backwards compat, detailed status dict)
        """
        import subprocess

        simple_result = {}
        detailed_result = {}
        name_lower = name.lower()

        for tld in self.DEFAULT_TLDS:
            domain = f"{name_lower}{tld}"

            # Step 1: Check if site is live (curl)
            is_live = False
            try:
                result = subprocess.run(
                    ["curl", "-sI", "--connect-timeout", "3", f"https://{domain}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # If we get HTTP headers, site is live
                is_live = "HTTP/" in result.stdout
            except (subprocess.TimeoutExpired, Exception):
                is_live = False

            # Step 2: Check whois registration
            whois_info = whois_lookup(domain)
            is_registered = whois_info is not None

            # Classify: available / parked / active
            if not is_registered:
                status = DomainStatus(available=True, parked=False, active=False, status="available")
                simple_result[tld] = True
            elif is_registered and not is_live:
                status = DomainStatus(available=False, parked=True, active=False, status="parked")
                simple_result[tld] = False  # Not available but acquirable
            else:
                status = DomainStatus(available=False, parked=False, active=True, status="active")
                simple_result[tld] = False

            detailed_result[tld] = status

        return simple_result, detailed_result

    def check_social(self, name: str, planned_domain: Optional[str] = None) -> dict[str, SocialHandleResult]:
        """Check social media handle availability with alternatives.

        Args:
            name: The brand name to check
            planned_domain: The domain you plan to use (e.g., "farness.ai") -
                           used to suggest matching alternatives like @farnessai
        """
        results = {}
        name_lower = name.lower()

        # Generate alternative handles based on name and planned domain
        alternatives = self._generate_handle_alternatives(name_lower, planned_domain)

        for platform in self.DEFAULT_PLATFORMS:
            # TODO: Implement actual availability checks via API/scraping
            # For now, return the alternatives we would check
            results[platform] = SocialHandleResult(
                platform=platform,
                exact_available=True,  # Placeholder - would check @{name}
                best_alternative=alternatives[0] if alternatives else None,
                alternatives_checked=[name_lower] + alternatives,
            )

        return results

    def _generate_handle_alternatives(self, name: str, planned_domain: Optional[str] = None) -> list[str]:
        """Generate alternative handles to check if exact name is taken."""
        alternatives = []

        # If planned domain provided, derive alternatives from it
        # e.g., farness.ai -> farnessai, farness_ai
        if planned_domain:
            # Remove protocol if present
            domain = planned_domain.replace("https://", "").replace("http://", "")
            # Get TLD
            if "." in domain:
                base, tld = domain.rsplit(".", 1)
                alternatives.append(f"{base}{tld}")  # farnessai
                alternatives.append(f"{base}_{tld}")  # farness_ai
                alternatives.append(f"{base}.{tld}")  # farness.ai (some platforms allow dots)
                alternatives.append(f"get{base}")  # getfarness
                alternatives.append(f"{base}hq")  # farnesshq
                alternatives.append(f"{base}app")  # farnessapp

        # Common suffix alternatives
        alternatives.extend([
            f"{name}hq",      # namehq
            f"{name}app",    # nameapp
            f"get{name}",    # getname
            f"try{name}",    # tryname
            f"use{name}",    # usename
            f"{name}_",      # name_
            f"_{name}",      # _name
            f"{name}io",     # nameio (if planning .io)
            f"{name}ai",     # nameai (if planning .ai)
            f"the{name}",    # thename
            f"{name}official",  # nameofficial
        ])

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for alt in alternatives:
            if alt not in seen and alt != name:
                seen.add(alt)
                unique.append(alt)

        return unique[:10]  # Top 10 alternatives

    def find_similar_companies(self, name: str) -> SimilarCompaniesResult:
        """Find similar-sounding or confusingly similar existing companies."""
        # Use LLM to research similar companies
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                return self._find_similar_with_llm(name)
            except Exception as e:
                print(f"LLM similar companies search failed: {e}")

        # Fallback: no matches if no API key
        return SimilarCompaniesResult(matches=[], confusion_risk="low")

    def _find_similar_with_llm(self, name: str) -> SimilarCompaniesResult:
        """Use LLM to find similar companies."""
        from anthropic import Anthropic
        client = Anthropic()

        prompt = f"""Find existing companies with names that could be confused with "{name}".

Consider ALL types of similarity:

1. **Phonetic similarity** - names that sound alike when spoken
   - Example: "Lyft" ~ "Lift", "Figma" ~ "Sigma"

2. **Visual similarity** - names that look alike when written
   - Example: "Stripe" ~ "Stripey", "Notion" ~ "Motion"

3. **Semantic similarity** - names with similar meanings or concepts
   - Example: "PayFlow" ~ "Stripe" (both evoke payment/flow)
   - Example: "CloudBase" ~ "Firebase" (both evoke cloud/base)

4. **Morphological similarity** - shared prefixes, suffixes, or word parts
   - Example: "Datadog" ~ "Databricks" (shared "Data-")
   - Example: "Mailchimp" ~ "Mailgun" (shared "Mail-")

5. **Industry confusion** - names that suggest the same product category
   - Example: "ChatBot AI" ~ "ChatGPT" (both chat + AI)

Focus on REAL, existing companies that someone might confuse with "{name}".
Include well-known tech companies, startups, and established brands.

For each similar company, provide:
- name: The company's actual name
- industry: Their primary industry/product
- similarity_score: 0.0-1.0 (how likely to cause confusion)
- reason: Specific type of similarity

Respond in JSON format:
{{
    "matches": [
        {{"name": "CompanyName", "industry": "their industry", "similarity_score": 0.7, "reason": "phonetically similar - both end in '-ify'"}}
    ],
    "confusion_risk": "low|medium|high"
}}

Guidelines for confusion_risk:
- "high": Very similar to a well-known company, or multiple close matches
- "medium": Moderately similar to known companies, some confusion possible
- "low": Only loose similarity, minimal confusion risk

Only include companies with similarity_score > 0.4. Respond ONLY with valid JSON, no markdown."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        matches = [
            SimilarCompany(
                name=m["name"],
                similarity_score=m["similarity_score"],
                industry=m["industry"],
                reason=m["reason"],
            )
            for m in result.get("matches", [])
        ]

        return SimilarCompaniesResult(
            matches=matches,
            confusion_risk=result.get("confusion_risk", "low"),
        )

    def score_pronunciation(self, name: str) -> float:
        """Score pronunciation difficulty (0-10, higher = easier)."""
        result = self.analyze_pronunciation(name)
        return result.score

    def analyze_pronunciation(self, name: str) -> PronunciationResult:
        """Analyze pronunciation characteristics."""
        syllables = self._count_syllables(name)
        name_lower = name.lower()

        # Score based on syllables (1-2 ideal)
        if syllables <= 2:
            base_score = 9.0
        elif syllables <= 3:
            base_score = 7.0
        elif syllables <= 4:
            base_score = 5.0
        else:
            base_score = 3.0

        # Penalize difficult consonant clusters
        difficult_patterns = ["xw", "zx", "ptl", "tch", "sch"]
        for pattern in difficult_patterns:
            if pattern in name_lower:
                base_score -= 1.5

        # Penalize AMBIGUOUS pronunciations - where syllable boundaries are unclear
        # These are letter combos that could be split/pronounced multiple ways
        ambiguous_patterns = [
            ("eax", 2.0),   # Pipeax: is it "ee-ax" or "ex" or "eeks"?
            ("eox", 2.0),   # Same issue
            ("iax", 2.0),   # Could be "ee-ax" or "yax"
            ("oax", 1.5),   # Coax is clear but others aren't
            ("uax", 2.0),   # Unclear
            ("aeo", 1.5),   # Vowel clusters - where's the break?
            ("eai", 1.5),
            ("oeu", 1.5),
            ("iou", 1.5),
            ("aea", 2.0),
            ("eae", 2.0),
            ("iai", 2.0),
            ("oao", 2.0),
            ("uau", 2.0),
        ]
        for pattern, penalty in ambiguous_patterns:
            if pattern in name_lower:
                base_score -= penalty

        # Penalize made-up suffixes that look like words but aren't
        # These create "how do I say this?" moments
        weird_suffixes = [
            ("ax", 0.5),    # Pipeax - is the 'a' long or short?
            ("ix", 0.5),    # Unless it's a real word ending
            ("ux", 0.5),
            ("eum", 1.0),   # Lineum - sounds like a fake element
            ("ium", 0.5),   # Real element suffix, less penalty
            ("ify", 0.0),   # Spotify-like, well understood
            ("ly", 0.0),    # Adverb suffix, clear
        ]
        for suffix, penalty in weird_suffixes:
            if name_lower.endswith(suffix) and len(name_lower) > len(suffix) + 2:
                base_score -= penalty

        # Bonus for clearly pronounceable patterns (well-known morphemes)
        clear_patterns = ["flow", "hub", "stack", "base", "cloud", "sync", "link", "wise", "ly"]
        for pattern in clear_patterns:
            if pattern in name_lower:
                base_score += 0.5
                break  # Only one bonus

        # Determine spelling difficulty
        if self._is_phonetic(name):
            spelling = "easy"
        elif any(c in name_lower for c in ["ph", "gh", "ough"]):
            spelling = "hard"
        else:
            spelling = "medium"

        return PronunciationResult(
            score=max(0, min(10, base_score)),
            syllables=syllables,
            spelling_difficulty=spelling,
        )

    def check_international(self, name: str) -> dict[str, dict]:
        """Check for problematic meanings in other languages."""
        languages = ["spanish", "french", "german", "mandarin", "japanese", "portuguese", "arabic"]
        result = {}

        # Known problematic words
        problematic = {
            "mist": {"german": "manure/dung"},
            "fart": {"scandinavian": "speed"},
            "nova": {"spanish": "doesn't go (no va)"},
        }

        name_lower = name.lower()
        for lang in languages:
            issue = None
            if name_lower in problematic and lang in problematic[name_lower]:
                issue = problematic[name_lower][lang]
            result[lang] = {"has_issue": issue is not None, "meaning": issue}

        return result

    def analyze_perception(self, name: str, mission: Optional[str] = None) -> PerceptionResult:
        """Analyze brand perception using AI personas."""
        # Check if we have an API key for real analysis
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                from namecast.perception import analyze_with_personas
                analysis = analyze_with_personas(name, mission, num_personas=5)
                return PerceptionResult(
                    evokes=analysis.evokes,
                    industry_association=analysis.industry_association,
                    memorability=analysis.memorability,
                    mission_alignment=analysis.mission_alignment,
                )
            except Exception as e:
                print(f"AI perception analysis failed: {e}")

        # Fallback to placeholder if no API key or error
        result = PerceptionResult(
            evokes="professional, modern",
            industry_association=["technology", "business"],
            memorability="high",
        )
        if mission:
            result.mission_alignment = 7.0  # Placeholder
        return result

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        # Handle silent e
        if word.endswith("e") and count > 1:
            count -= 1
        return max(1, count)

    def _is_phonetic(self, name: str) -> bool:
        """Check if name is phonetically simple."""
        # Simple heuristic: no unusual letter combos
        unusual = ["ph", "gh", "ough", "tion", "sion", "xc", "cq"]
        return not any(u in name.lower() for u in unusual)

    def _calc_domain_score(self, domains: dict[str, bool]) -> float:
        """Calculate domain availability score (0-100)."""
        if not domains:
            return 0
        # .com is worth 50%, others split the rest
        score = 0
        if domains.get(".com"):
            score += 50
        other_tlds = [tld for tld in domains if tld != ".com"]
        available_others = sum(1 for tld in other_tlds if domains.get(tld))
        if other_tlds:
            score += (available_others / len(other_tlds)) * 50
        return score

    def _calc_social_score(self, social: dict[str, SocialHandleResult]) -> float:
        """Calculate social handle availability score (0-100).

        Scoring:
        - Exact handle available: 100% for that platform
        - Alternative available: 70% for that platform
        - Nothing available: 0% for that platform
        """
        if not social:
            return 0

        total_score = 0
        for result in social.values():
            if isinstance(result, SocialHandleResult):
                if result.exact_available:
                    total_score += 100
                elif result.best_alternative:
                    total_score += 70  # Alternative is decent but not perfect
                # else: 0 points
            else:
                # Backwards compat with old bool format
                total_score += 100 if result else 0

        return total_score / len(social)

    def _calc_international_score(self, international: dict[str, dict]) -> float:
        """Calculate international safety score (0-100)."""
        if not international:
            return 100
        issues = sum(1 for v in international.values() if v.get("has_issue"))
        return max(0, 100 - (issues * 20))

    def _calc_similar_companies_score(self, similar: SimilarCompaniesResult) -> float:
        """Calculate similar companies score (0-100). Lower = more conflicts."""
        if not similar.matches:
            return 100
        # High risk = big penalty
        if similar.confusion_risk == "high":
            return 20
        elif similar.confusion_risk == "medium":
            return 60
        else:
            return 85

    def _calc_domain_score_detailed(self, domain_details: dict[str, DomainStatus]) -> float:
        """Calculate domain score with available/parked/active distinction."""
        if not domain_details:
            return 0

        score = 0
        # Score per domain: available=100, parked=60, active=0
        weights = {".com": 0.4, ".ai": 0.3, ".io": 0.15, ".co": 0.1, ".app": 0.05}

        for tld, status in domain_details.items():
            weight = weights.get(tld, 0.1)
            if status.available:
                score += 100 * weight
            elif status.parked:
                score += 60 * weight  # Parked = acquirable
            # Active = 0 points

        return score

    def _calc_brand_scope_score(self, brand_scope: Optional[BrandScopeResult]) -> float:
        """Calculate brand scope score (0-100)."""
        if not brand_scope:
            return 70  # Default if not analyzed
        # Average of the three metrics, scaled to 100
        avg = (brand_scope.narrowness + brand_scope.expansion_potential + brand_scope.vision_alignment) / 3
        return avg * 10  # 0-10 -> 0-100

    def analyze_brand_scope(self, name: str, mission: Optional[str] = None) -> BrandScopeResult:
        """Analyze if the name boxes in the company or allows for growth."""
        if os.environ.get("ANTHROPIC_API_KEY") and mission:
            try:
                return self._analyze_brand_scope_with_llm(name, mission)
            except Exception as e:
                print(f"Brand scope analysis failed: {e}")

        # Fallback heuristic
        return self._analyze_brand_scope_heuristic(name)

    def _analyze_brand_scope_heuristic(self, name: str) -> BrandScopeResult:
        """Simple heuristic brand scope analysis."""
        name_lower = name.lower()

        # Narrow indicators (product-specific words)
        narrow_words = ["bot", "ai", "app", "tool", "api", "hub", "sync", "track", "log", "scan"]
        industry_words = ["tax", "pay", "mail", "chat", "code", "doc", "form", "data", "cloud"]

        narrowness = 7  # Default: moderately expansive
        if any(word in name_lower for word in narrow_words):
            narrowness -= 2
        if any(word in name_lower for word in industry_words):
            narrowness -= 2

        # Abstract names get bonus
        if len(name) <= 6 and not any(word in name_lower for word in narrow_words + industry_words):
            narrowness += 1

        narrowness = max(1, min(10, narrowness))

        return BrandScopeResult(
            narrowness=narrowness,
            expansion_potential=narrowness,  # Correlated
            vision_alignment=7,  # Can't assess without mission
            assessment=f"Heuristic analysis: {'expansive' if narrowness >= 7 else 'moderate' if narrowness >= 4 else 'narrow'} brand scope"
        )

    def _analyze_brand_scope_with_llm(self, name: str, mission: str) -> BrandScopeResult:
        """Use LLM to analyze brand scope."""
        from anthropic import Anthropic
        client = Anthropic()

        prompt = f"""Analyze the brand name "{name}" for a company with this mission:
"{mission}"

Evaluate brand scope - does the name box in the company or allow for growth?

Consider:
1. **Narrowness**: Does the name imply only ONE product/feature?
   - "TaxGraph" = narrow (only tax)
   - "Amazon" = expansive (completely abstract)

2. **Expansion potential**: Could the company expand into adjacent areas?

3. **Vision alignment**: Does the name capture the FULL mission?

Rate each 1-10 (10 = most expansive/aligned).

Respond in JSON:
{{
    "narrowness": 7,
    "expansion_potential": 8,
    "vision_alignment": 6,
    "assessment": "Brief explanation of the brand scope"
}}

Respond ONLY with valid JSON."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        result = json.loads(response.content[0].text)

        return BrandScopeResult(
            narrowness=result["narrowness"],
            expansion_potential=result["expansion_potential"],
            vision_alignment=result["vision_alignment"],
            assessment=result["assessment"],
        )

    def generate_taglines(self, name: str, mission: str) -> list[str]:
        """Generate taglines that complement the name."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return []

        try:
            from anthropic import Anthropic
            client = Anthropic()

            prompt = f"""Generate 3 taglines for the brand "{name}" with this mission:
"{mission}"

Good taglines:
- Explain/complement the name if it's abstract
- Capture the full mission
- Are memorable and quotable (under 8 words)

Examples:
- Apple: "Think Different"
- Nike: "Just Do It"
- Stripe: "Payments infrastructure for the internet"

Respond with ONLY a JSON array:
["tagline 1", "tagline 2", "tagline 3"]"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            return json.loads(text)

        except Exception as e:
            print(f"Tagline generation failed: {e}")
            return []

    def quick_domain_check(self, name: str) -> dict[str, bool]:
        """Fast domain check - .com, .ai, and .io for filtering."""
        result = {}
        name_lower = name.lower()
        for tld in [".com", ".ai", ".io"]:
            domain = f"{name_lower}{tld}"
            info = whois_lookup(domain)
            result[tld] = info is None
        return result


@dataclass
class NameCandidate:
    """A name candidate with its filtering status."""
    name: str
    source: str  # "user" or "generated"
    domains_available: dict[str, bool] = field(default_factory=dict)
    passed_domain_filter: bool = False
    evaluation: Optional[EvaluationResult] = None
    rejection_reason: Optional[str] = None


@dataclass
class WorkflowResult:
    """Result of the full naming workflow."""
    project_description: str
    all_candidates: list[NameCandidate]
    viable_candidates: list[NameCandidate]  # Passed domain filter
    evaluated_candidates: list[NameCandidate]  # Full evaluation complete
    recommended: Optional[NameCandidate] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class NamecastWorkflow:
    """Smart workflow: generate + filter + evaluate names."""

    def __init__(self):
        self.evaluator = BrandEvaluator()

    def run(
        self,
        project_description: str,
        user_name_ideas: Optional[list[str]] = None,
        generate_count: int = 10,
        max_to_evaluate: int = 5,
    ) -> WorkflowResult:
        """Run the full naming workflow.

        Args:
            project_description: Description of the project/company/product
            user_name_ideas: Optional list of name ideas from the user
            generate_count: How many AI names to generate
            max_to_evaluate: Max candidates to run full evaluation on

        Returns:
            WorkflowResult with all candidates and evaluations
        """
        all_candidates: list[NameCandidate] = []

        # Step 1: Add user's ideas
        if user_name_ideas:
            for name in user_name_ideas:
                all_candidates.append(NameCandidate(
                    name=name.strip(),
                    source="user"
                ))

        # Step 2: Generate additional names via AI
        generated_names = self._generate_names(project_description, generate_count)
        for name in generated_names:
            # Don't duplicate user's ideas
            if not any(c.name.lower() == name.lower() for c in all_candidates):
                all_candidates.append(NameCandidate(
                    name=name,
                    source="generated"
                ))

        # Step 3: Quick domain filter - check .com and .io
        viable_candidates: list[NameCandidate] = []
        for candidate in all_candidates:
            domains = self.evaluator.quick_domain_check(candidate.name)
            candidate.domains_available = domains

            # Must have at least one key domain available
            if domains.get(".com") or domains.get(".ai") or domains.get(".io"):
                candidate.passed_domain_filter = True
                viable_candidates.append(candidate)
            else:
                candidate.rejection_reason = "No .com, .ai, or .io domain available"

        # Step 4: Full evaluation on top viable candidates
        # Sort by user ideas first, then by domain availability
        viable_candidates.sort(key=lambda c: (
            0 if c.source == "user" else 1,
            0 if c.domains_available.get(".com") else 1
        ))

        evaluated_candidates: list[NameCandidate] = []
        for candidate in viable_candidates[:max_to_evaluate]:
            try:
                candidate.evaluation = self.evaluator.evaluate(
                    candidate.name,
                    mission=project_description
                )
                evaluated_candidates.append(candidate)
            except Exception as e:
                candidate.rejection_reason = f"Evaluation failed: {e}"

        # Step 5: Find recommendation (highest overall score)
        recommended = None
        if evaluated_candidates:
            recommended = max(
                evaluated_candidates,
                key=lambda c: c.evaluation.overall_score if c.evaluation else 0
            )

        return WorkflowResult(
            project_description=project_description,
            all_candidates=all_candidates,
            viable_candidates=viable_candidates,
            evaluated_candidates=evaluated_candidates,
            recommended=recommended,
        )

    def _generate_names(self, project_description: str, count: int) -> list[str]:
        """Generate name ideas using AI."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return []

        try:
            from anthropic import Anthropic
            client = Anthropic()

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"""Generate {count} brand name ideas for this project:

{project_description}

Requirements for good brand names:
- Short (1-2 words, ideally 6-10 characters)
- Easy to spell and pronounce - AVOID made-up suffixes like "-eum", "-ax", "-ix"
- Clear pronunciation - someone should know how to say it on first read
- Memorable and distinctive
- Available as a domain (.com or .io preferred)
- No negative connotations in major languages
- Evokes the right associations for the product/industry

IMPORTANT: Do NOT generate names that are similar to existing well-known products mentioned in the description. For example:
- If description mentions "Linear", don't generate "Lineum", "Linearify", "Linea", etc.
- If description mentions "Notion", don't generate "Notionify", "Notionly", etc.
- Create ORIGINAL names that complement, not copy, the referenced products.

Respond with ONLY a JSON array of names, no explanation:
["Name1", "Name2", ...]"""
                }]
            )

            # Parse JSON from response
            text = response.content[0].text.strip()
            # Handle markdown code blocks
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            names = json.loads(text)
            raw_names = [n.strip() for n in names if isinstance(n, str)]

            # Post-filter: remove names too similar to mission keywords
            filtered_names = self._filter_similar_to_mission(raw_names, project_description)
            return filtered_names

        except Exception as e:
            print(f"Name generation failed: {e}")
            return []

    def _filter_similar_to_mission(self, names: list[str], mission: str) -> list[str]:
        """Filter out names that are too similar to PRODUCT/COMPANY names in the mission.

        This is CRITICAL - if user says "crm + linear", we must NEVER return
        "Lineum", "Linearify", "Linea", etc. These are lazy derivatives.

        But we SHOULD allow derivatives of industry terms like "CRM", "API", "SaaS".
        """
        import re

        # Common words to ignore
        common_words = {"the", "and", "for", "that", "this", "with", "from", "have",
                        "been", "will", "would", "could", "should", "their", "there",
                        "about", "which", "when", "what", "your", "more", "some",
                        "into", "like", "just", "than", "them", "then", "also", "very",
                        "most", "only", "over", "such", "make", "made", "can", "but",
                        "app", "apps", "tool", "tools", "like", "better"}

        # Industry terms - these are NOT company names, ok to derive from
        industry_terms = {"crm", "erp", "api", "saas", "paas", "iaas", "cms", "cdn",
                         "seo", "ppc", "roi", "kpi", "b2b", "b2c", "ai", "ml", "llm",
                         "devops", "fintech", "edtech", "healthtech", "martech",
                         "ecommerce", "analytics", "automation", "dashboard",
                         "workflow", "integration", "sync", "data", "cloud"}

        # Extract words that look like product/company names
        # Heuristic: Capitalized words or words 4+ chars that aren't industry terms
        mission_words = set()

        # First pass: get capitalized words (likely product names)
        for word in re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', mission):
            word_lower = word.lower()
            if word_lower not in common_words and word_lower not in industry_terms:
                mission_words.add(word_lower)

        # Second pass: get lowercase words 4+ chars that aren't industry terms
        for word in re.findall(r'\b[a-z]{4,}\b', mission.lower()):
            if word not in common_words and word not in industry_terms:
                mission_words.add(word)

        filtered = []
        for name in names:
            name_lower = name.lower()
            is_too_similar = False

            for mission_word in mission_words:
                # AGGRESSIVE checks - we'd rather reject good names than accept derivatives

                # 1. Name contains the mission word as a substring
                if mission_word in name_lower and len(mission_word) >= 3:
                    is_too_similar = True
                    break

                # 2. Mission word contains the name as a substring
                if name_lower in mission_word and len(name_lower) >= 3:
                    is_too_similar = True
                    break

                # 3. Name starts with first 3+ chars of mission word
                if len(mission_word) >= 3 and name_lower.startswith(mission_word[:3]):
                    is_too_similar = True
                    break

                # 4. Name ends with last 3+ chars of mission word
                if len(mission_word) >= 4 and name_lower.endswith(mission_word[-4:]):
                    is_too_similar = True
                    break

                # 5. Edit distance check (catches "Lineum" vs "Linear")
                if self._is_similar_string(name_lower, mission_word, threshold=0.6):
                    is_too_similar = True
                    break

            if not is_too_similar:
                filtered.append(name)

        return filtered

    def _is_similar_string(self, s1: str, s2: str, threshold: float = 0.6) -> bool:
        """Check if two strings are too similar using Levenshtein-like ratio."""
        # Quick length check
        len_diff = abs(len(s1) - len(s2))
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return True
        if len_diff > max_len * 0.4:  # More than 40% length difference
            return False

        # Count matching characters (simple but effective)
        matches = 0
        s2_chars = list(s2)
        for c in s1:
            if c in s2_chars:
                matches += 1
                s2_chars.remove(c)  # Each char can only match once

        # Similarity is matched chars / average length
        similarity = (2.0 * matches) / (len(s1) + len(s2))
        return similarity >= threshold
