from src.models import CompanyAnalysis, CompanyInfo, ResearchState


def test_research_state_list_defaults_are_isolated():
    first = ResearchState(query="vector databases")
    second = ResearchState(query="auth platforms")

    first.extracted_tools.append("Supabase")
    first.companies.append(
        CompanyInfo(
            name="Supabase",
            description="Open source Firebase alternative",
            website="https://supabase.com",
        )
    )

    assert second.extracted_tools == []
    assert second.companies == []


def test_company_analysis_defaults_are_isolated():
    first = CompanyAnalysis(pricing_model="Freemium")
    second = CompanyAnalysis(pricing_model="Paid")

    first.tech_stack.append("Postgres")
    first.language_support.append("JavaScript")

    assert second.tech_stack == []
    assert second.language_support == []


def test_company_info_developer_fields_default_cleanly():
    company = CompanyInfo(
        name="ExampleTool",
        description="Example developer tool",
        website="https://example.com",
    )

    assert company.tech_stack == []
    assert company.competitors == []
    assert company.integration_capabilities == []
