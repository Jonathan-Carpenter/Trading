namespace Host.Model;

internal abstract class DatedSeries<T>
{
    public IEnumerable<DatedValue<T>> Values { get; }

    protected DatedSeries(IEnumerable<DatedValue<T>> values)
    {
        this.Values = values;
    }
}