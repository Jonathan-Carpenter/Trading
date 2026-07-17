namespace Host.Protocol.Edgar;

internal abstract class BaseCompanyFactUnit(DateOnly end, long val, int? fy, string? fp, string form, DateOnly filed)
{
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
}