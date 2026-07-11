namespace Common.Http;

public interface IWrappedHttpClient
{
    /// <exception cref="ArgumentNullException"></exception>
    /// <exception cref="InvalidOperationException"></exception>
    /// <exception cref="HttpRequestException"></exception>
    /// <exception cref="OperationCanceledException"></exception>
    Task<IWrappedHttpResponseMessage> SendAsync(IWrappedHttpRequestMessage request);
}