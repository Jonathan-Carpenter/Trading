namespace Host.Protocol.Edgar;

internal sealed class CompanyFactUnit(DateOnly? start, DateOnly end, long val, int? fy, string? fp, string form, DateOnly filed)
{
    /// <remarks>
    /// Not all facts specify a start date.
    /// </remarks>
    public DateOnly? Start { get; } = start;

    public DateOnly End { get; } = end;

    public long Val { get; } = val;

    /// <remarks>
    /// Some API entries have null FY.
    /// </remarks>
    public int? Fy { get; } = fy;

    /// <remarks>
    /// Some API entries have null FP.
    /// </remarks>
    public string? Fp { get; } = fp;

    public string Form { get; } = form;

    public DateOnly Filed { get; } = filed;

    public bool IsAnnualFiling => this.Form.Equals("10-K", StringComparison.OrdinalIgnoreCase);

    public bool IsFullYearFiling
    {
        get
        {
            if (this.Start == null)
            {
                return false;
                // throw new InvalidOperationException("Cannot determine whether this unit is a full year filing because it doesn't have a start date.");
            }

            return (this.End.DayNumber - this.Start.Value.DayNumber) > 350;
        }
    }
}