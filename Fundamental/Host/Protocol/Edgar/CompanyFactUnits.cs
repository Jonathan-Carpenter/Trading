namespace Host.Protocol.Edgar;

internal sealed class CompanyFactUnits(IEnumerable<CompanyFactUnit> usd)
{
    public IEnumerable<CompanyFactUnit> Usd { get; } = usd;
}