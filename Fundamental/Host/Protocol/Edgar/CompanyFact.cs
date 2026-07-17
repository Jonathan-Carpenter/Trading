namespace Host.Protocol.Edgar;

internal sealed class CompanyFact<T>(string label, string description, CompanyFactUnits<T> units)
    where T : BaseCompanyFactUnit
{
    public string Label { get; } = label;

    public string Description { get; } = description;

    public CompanyFactUnits<T> Units { get; } = units;
}