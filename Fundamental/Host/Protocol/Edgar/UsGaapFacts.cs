namespace Host.Protocol.Edgar;

internal sealed class UsGaapFacts(CompanyFact<CompanyFactEndUnit> assets, CompanyFact<CompanyFactRangeUnit> netIncomeLoss)
{
    public CompanyFact<CompanyFactEndUnit> Assets { get; } = assets;

    public CompanyFact<CompanyFactRangeUnit> NetIncomeLoss { get; } = netIncomeLoss;
}