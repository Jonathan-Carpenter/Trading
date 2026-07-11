namespace Host.Protocol.Edgar;

internal sealed class UsGaapFacts(CompanyFact assets, CompanyFact netIncomeLoss)
{
    public CompanyFact Assets { get; } = assets;

    public CompanyFact NetIncomeLoss { get; } = netIncomeLoss;
}