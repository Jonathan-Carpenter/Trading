namespace Host.Protocol.Edgar;

internal sealed class CompanyFact(string label, string description, CompanyFactUnits units)
{
    public string Label { get; } = label;

    public string Description { get; } = description;

    public CompanyFactUnits Units { get; } = units;
}