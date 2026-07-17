namespace Host.Protocol.Edgar;

internal sealed class CompanyFactUnits<T>(IEnumerable<T> usd)
    where T : BaseCompanyFactUnit
{
    // TODO: This doesn't allow other currencies?
    public IEnumerable<T> Usd { get; } = usd;
}