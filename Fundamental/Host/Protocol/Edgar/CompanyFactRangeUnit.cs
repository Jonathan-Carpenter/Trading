namespace Host.Protocol.Edgar;

internal sealed class CompanyFactRangeUnit(
    DateOnly start,
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
    public DateOnly Start { get; } = start;

    public bool IsFullYearFiling => (this.End.DayNumber - this.Start.DayNumber) > 350;
}