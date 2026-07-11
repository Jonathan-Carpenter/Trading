namespace Host.Fetch;

internal sealed class DataFetchException : Exception
{
    public DataFetchException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}