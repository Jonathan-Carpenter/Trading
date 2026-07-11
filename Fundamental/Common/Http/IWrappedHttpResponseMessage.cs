using System.Text.Json;

namespace Common.Http;

public interface IWrappedHttpResponseMessage : IDisposable
{
    /// <exception cref="HttpRequestException"></exception>
    IWrappedHttpResponseMessage EnsureSuccessStatusCode();

    /// <exception cref="OperationCanceledException"></exception>
    Task<T> ReadContentFromJsonAsync<T>(JsonSerializerOptions options);
}