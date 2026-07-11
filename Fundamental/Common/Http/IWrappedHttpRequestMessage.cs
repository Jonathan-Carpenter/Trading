namespace Common.Http;

public interface IWrappedHttpRequestMessage
{
    /// <exception cref="ArgumentException"></exception>
    /// <exception cref="InvalidOperationException"></exception>
    /// <exception cref="FormatException"></exception>
    void AddHeader(string name, string value);

    HttpRequestMessage Message { get; }
}