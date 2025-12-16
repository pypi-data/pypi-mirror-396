"""Tests for the brand name oracle."""

from unittest.mock import patch
from namecast.evaluator import BrandEvaluator, EvaluationResult


class TestBrandEvaluator:
    """Tests for the main BrandEvaluator class."""

    @patch("namecast.evaluator.whois_lookup")
    def test_evaluate_returns_evaluation_result(self, mock_whois):
        """evaluate() should return an EvaluationResult dataclass."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        assert isinstance(result, EvaluationResult)

    @patch("namecast.evaluator.whois_lookup")
    def test_evaluate_includes_brand_name(self, mock_whois):
        """Result should include the evaluated brand name."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("Acme")
        assert result.name == "Acme"

    @patch("namecast.evaluator.whois_lookup")
    def test_evaluate_includes_overall_score(self, mock_whois):
        """Result should include an overall score 0-100."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        assert 0 <= result.overall_score <= 100

    @patch("namecast.evaluator.whois_lookup")
    def test_evaluate_includes_all_subscores(self, mock_whois):
        """Result should include all subscore categories."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        assert hasattr(result, "domain_score")
        assert hasattr(result, "social_score")
        assert hasattr(result, "pronunciation_score")
        assert hasattr(result, "international_score")


class TestDomainChecker:
    """Tests for domain availability checking."""

    @patch("namecast.evaluator.whois_lookup")
    def test_check_domains_returns_dict(self, mock_whois):
        """check_domains() should return a dict of TLD -> availability."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.check_domains("testbrand")
        assert isinstance(result, dict)

    @patch("namecast.evaluator.whois_lookup")
    def test_check_domains_includes_common_tlds(self, mock_whois):
        """Should check .com, .io, .co, .ai, .app by default."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.check_domains("testbrand")
        assert ".com" in result
        assert ".io" in result
        assert ".co" in result
        assert ".ai" in result
        assert ".app" in result

    @patch("namecast.evaluator.whois_lookup")
    def test_check_domains_returns_booleans(self, mock_whois):
        """Each TLD should map to a boolean (available or not)."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.check_domains("testbrand")
        for tld, available in result.items():
            assert isinstance(available, bool), f"{tld} should be bool, got {type(available)}"

    @patch("namecast.evaluator.whois_lookup")
    def test_domain_available_when_not_registered(self, mock_whois):
        """Domain should be available when WHOIS returns no registration."""
        mock_whois.return_value = None  # No registration found
        evaluator = BrandEvaluator()
        result = evaluator.check_domains("xyzuniquename12345")
        assert result[".com"] is True

    @patch("namecast.evaluator.whois_lookup")
    def test_domain_unavailable_when_registered(self, mock_whois):
        """Domain should be unavailable when WHOIS returns registration."""
        mock_whois.return_value = {"domain_name": "google.com", "creation_date": "1997-09-15"}
        evaluator = BrandEvaluator()
        result = evaluator.check_domains("google")
        assert result[".com"] is False


class TestSocialChecker:
    """Tests for social media handle checking."""

    def test_check_social_returns_dict(self):
        """check_social() should return a dict of platform -> availability."""
        evaluator = BrandEvaluator()
        result = evaluator.check_social("testbrand")
        assert isinstance(result, dict)

    def test_check_social_includes_major_platforms(self):
        """Should check Twitter, Instagram, LinkedIn, TikTok, GitHub."""
        evaluator = BrandEvaluator()
        result = evaluator.check_social("testbrand")
        assert "twitter" in result
        assert "instagram" in result
        assert "linkedin" in result
        assert "tiktok" in result
        assert "github" in result

    def test_check_social_returns_social_handle_results(self):
        """Each platform should map to a SocialHandleResult."""
        from namecast.evaluator import SocialHandleResult
        evaluator = BrandEvaluator()
        result = evaluator.check_social("testbrand")
        for platform, handle_result in result.items():
            assert isinstance(handle_result, SocialHandleResult)
            assert isinstance(handle_result.exact_available, bool)


class TestPronunciationScorer:
    """Tests for pronunciation analysis."""

    def test_score_pronunciation_returns_score(self):
        """score_pronunciation() should return a score 0-10."""
        evaluator = BrandEvaluator()
        score = evaluator.score_pronunciation("Stripe")
        assert 0 <= score <= 10

    def test_short_names_score_higher(self):
        """Shorter names (1-2 syllables) should score higher."""
        evaluator = BrandEvaluator()
        short_score = evaluator.score_pronunciation("Stripe")
        long_score = evaluator.score_pronunciation("Supercalifragilistic")
        assert short_score > long_score

    def test_simple_phonetics_score_higher(self):
        """Names with simple phonetics should score higher."""
        evaluator = BrandEvaluator()
        simple_score = evaluator.score_pronunciation("Luma")
        complex_score = evaluator.score_pronunciation("Xwyzptlk")
        assert simple_score > complex_score

    def test_returns_syllable_count(self):
        """Should also return syllable count."""
        evaluator = BrandEvaluator()
        result = evaluator.analyze_pronunciation("Spotify")
        assert result.syllables == 3

    def test_returns_spelling_difficulty(self):
        """Should return spelling difficulty assessment."""
        evaluator = BrandEvaluator()
        result = evaluator.analyze_pronunciation("Google")
        assert result.spelling_difficulty in ["easy", "medium", "hard"]


class TestInternationalChecker:
    """Tests for international meaning/pronunciation check."""

    def test_check_international_returns_dict(self):
        """check_international() should return dict of language -> issues."""
        evaluator = BrandEvaluator()
        result = evaluator.check_international("TestBrand")
        assert isinstance(result, dict)

    def test_check_international_includes_major_languages(self):
        """Should check Spanish, French, German, Mandarin, Japanese, Portuguese, Arabic."""
        evaluator = BrandEvaluator()
        result = evaluator.check_international("TestBrand")
        expected_languages = ["spanish", "french", "german", "mandarin", "japanese", "portuguese", "arabic"]
        for lang in expected_languages:
            assert lang in result

    def test_flags_problematic_meanings(self):
        """Should flag names with problematic meanings in other languages."""
        evaluator = BrandEvaluator()
        # "mist" means "manure" in German
        result = evaluator.check_international("Mist")
        assert result["german"]["has_issue"] is True

    def test_returns_no_issues_for_clean_names(self):
        """Should return no issues for culturally neutral names."""
        evaluator = BrandEvaluator()
        result = evaluator.check_international("Luma")
        issues = [v for v in result.values() if v.get("has_issue")]
        assert len(issues) == 0


class TestAIPerception:
    """Tests for AI-powered perception analysis."""

    def test_analyze_perception_returns_analysis(self):
        """analyze_perception() should return perception analysis."""
        evaluator = BrandEvaluator()
        result = evaluator.analyze_perception("Stripe")
        assert hasattr(result, "evokes")
        assert hasattr(result, "industry_association")
        assert hasattr(result, "memorability")

    def test_analyze_perception_with_mission(self):
        """Should score mission alignment when mission provided."""
        evaluator = BrandEvaluator()
        result = evaluator.analyze_perception(
            "Luminary",
            mission="An education technology platform for lifelong learners"
        )
        assert hasattr(result, "mission_alignment")
        assert 0 <= result.mission_alignment <= 10


class TestScorecard:
    """Tests for the unified scorecard output."""

    @patch("namecast.evaluator.whois_lookup")
    def test_scorecard_as_dict(self, mock_whois):
        """Should be able to export result as dict."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "name" in d
        assert "overall_score" in d

    @patch("namecast.evaluator.whois_lookup")
    def test_scorecard_as_json(self, mock_whois):
        """Should be able to export result as JSON string."""
        mock_whois.return_value = None
        import json
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert parsed["name"] == "TestBrand"

    @patch("namecast.evaluator.whois_lookup")
    def test_scorecard_as_markdown(self, mock_whois):
        """Should be able to export result as markdown table."""
        mock_whois.return_value = None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        md = result.to_markdown()
        assert "## Brand Evaluation: TestBrand" in md
        assert "Overall Score" in md


class TestDomainPricing:
    """Tests for domain pricing functionality."""

    MOCK_PRICING = {
        "ai": {"registration": "72.40", "renewal": "72.40"},
        "com": {"registration": "11.08", "renewal": "11.08"},
        "io": {"registration": "28.12", "renewal": "46.65"},
        "co": {"registration": "9.58", "renewal": "25.97"},
        "app": {"registration": "15.00", "renewal": "15.00"},
    }

    @patch("namecast.evaluator.httpx.get")
    def test_get_domain_pricing_returns_dict(self, mock_get):
        """get_domain_pricing() should return dict of TLD -> price info."""
        from namecast.evaluator import get_domain_pricing, _pricing_cache
        _pricing_cache.clear()
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        result = get_domain_pricing()
        assert isinstance(result, dict)

    @patch("namecast.evaluator.httpx.get")
    def test_get_domain_pricing_includes_common_tlds(self, mock_get):
        """Should include pricing for common TLDs."""
        from namecast.evaluator import get_domain_pricing, _pricing_cache
        _pricing_cache.clear()
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        result = get_domain_pricing()
        assert "ai" in result
        assert "com" in result
        assert "io" in result
        assert "co" in result

    @patch("namecast.evaluator.httpx.get")
    def test_get_domain_pricing_has_registration_price(self, mock_get):
        """Each TLD should have registration price."""
        from namecast.evaluator import get_domain_pricing, _pricing_cache
        _pricing_cache.clear()
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        result = get_domain_pricing()
        for tld, pricing in result.items():
            assert "registration" in pricing
            assert isinstance(float(pricing["registration"]), float)

    @patch("namecast.evaluator.httpx.get")
    def test_get_domain_pricing_has_renewal_price(self, mock_get):
        """Each TLD should have renewal price."""
        from namecast.evaluator import get_domain_pricing, _pricing_cache
        _pricing_cache.clear()
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        result = get_domain_pricing()
        for tld, pricing in result.items():
            assert "renewal" in pricing
            assert isinstance(float(pricing["renewal"]), float)

    @patch("namecast.evaluator.httpx.get")
    def test_get_domain_pricing_caches_results(self, mock_get):
        """Should cache pricing to avoid repeated API calls."""
        from namecast.evaluator import get_domain_pricing, _pricing_cache
        _pricing_cache.clear()
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        # First call
        result1 = get_domain_pricing()
        # Second call should use cache (mock not called again)
        result2 = get_domain_pricing()
        assert result1 == result2
        assert mock_get.call_count == 1  # Only called once due to caching

    @patch("namecast.evaluator.httpx.get")
    @patch("namecast.evaluator.whois_lookup")
    def test_evaluation_includes_domain_pricing(self, mock_whois, mock_get):
        """EvaluationResult should include domain pricing."""
        from namecast.evaluator import _pricing_cache
        _pricing_cache.clear()
        mock_whois.return_value = None
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        assert hasattr(result, "domain_pricing")
        assert isinstance(result.domain_pricing, dict)

    @patch("namecast.evaluator.httpx.get")
    @patch("namecast.evaluator.whois_lookup")
    def test_evaluation_pricing_matches_checked_tlds(self, mock_whois, mock_get):
        """Pricing should be included for all TLDs we check."""
        from namecast.evaluator import _pricing_cache
        _pricing_cache.clear()
        mock_whois.return_value = None
        mock_get.return_value.json.return_value = {"status": "SUCCESS", "pricing": self.MOCK_PRICING}
        mock_get.return_value.raise_for_status = lambda: None
        evaluator = BrandEvaluator()
        result = evaluator.evaluate("TestBrand")
        for tld in result.domains.keys():
            tld_key = tld.lstrip(".")
            assert tld_key in result.domain_pricing


class TestCLI:
    """Tests for the command-line interface."""

    @patch("namecast.evaluator.whois_lookup")
    def test_cli_with_single_name(self, mock_whois):
        """CLI should accept a single brand name."""
        mock_whois.return_value = None
        from namecast.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "Acme"])
        assert result.exit_code == 0
        assert "Acme" in result.output

    @patch("namecast.evaluator.whois_lookup")
    def test_cli_with_mission_flag(self, mock_whois):
        """CLI should accept --mission flag."""
        mock_whois.return_value = None
        from namecast.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "Luminary", "--mission", "Education platform"])
        assert result.exit_code == 0
        assert "Mission Alignment" in result.output

    @patch("namecast.evaluator.whois_lookup")
    def test_cli_json_output(self, mock_whois):
        """CLI should support --json flag for JSON output."""
        mock_whois.return_value = None
        import json
        from namecast.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "Acme", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert parsed["name"] == "Acme"

    @patch("namecast.evaluator.whois_lookup")
    def test_cli_compare_multiple_names(self, mock_whois):
        """CLI should support comparing multiple names."""
        mock_whois.return_value = None
        from namecast.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ["eval", "--compare", "Acme", "Globex", "Initech"])
        assert result.exit_code == 0
        assert "Comparison" in result.output
