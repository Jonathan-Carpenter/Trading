namespace Host.Model;

internal sealed class ReturnOnAssets : DatedSeries<decimal>
{
    public ReturnOnAssets(IEnumerable<DatedValue<decimal>> values)
        : base(values)
    {
    }
}