namespace Host.Model;

public class DatedValue<T>
{
    public DateOnly End { get; }

    public DateOnly Filed { get; }

    public T Value { get; }

    public DatedValue(DateOnly end, DateOnly filed, T value)
    {
        this.End = end;
        this.Filed = filed;
        this.Value = value;
    }
}