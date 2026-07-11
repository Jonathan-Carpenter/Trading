namespace Host.Protocol.Edgar;

internal sealed class CompanyFactsResponse(int cik, string entityName, CompanyFacts facts)
{
    public int Cik { get; } = cik;

    public string EntityName { get; } = entityName;

    public CompanyFacts Facts { get; } = facts;
}