namespace Host.Protocol.Edgar;

internal sealed class CompanyFactUnit(DateOnly end, long val, int? fy, string? fp, DateOnly filed)
{
    public DateOnly End { get; } = end;

    public long Val { get; } = val;

    public int? Fy { get; } = fy;

    public string? Fp { get; } = fp;

    public DateOnly Filed { get; } = filed;
}