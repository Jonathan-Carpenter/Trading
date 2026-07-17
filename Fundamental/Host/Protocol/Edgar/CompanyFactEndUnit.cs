namespace Host.Protocol.Edgar;

internal sealed class CompanyFactEndUnit(
    DateOnly end,
    long val,
    int? fy,
    string? fp,
    string form,
    DateOnly filed) : BaseCompanyFactUnit(end,
    val,
    fy,
    fp,
    form,
    filed)
{
}