using System.Net.Http.Json;
using System.Text.Json;

namespace Common.Http;

public sealed class WrappedHttpResponseMessage : IWrappedHttpResponseMessage
{
    private readonly HttpResponseMessage httpResponseMessage;

    public WrappedHttpResponseMessage(HttpResponseMessage httpResponseMessage)
    {
        this.httpResponseMessage = httpResponseMessage;
    }

    public IWrappedHttpResponseMessage EnsureSuccessStatusCode()
    {
        this.httpResponseMessage.EnsureSuccessStatusCode();

        return this;
    }

    public async Task<T> ReadContentFromJsonAsync<T>(JsonSerializerOptions options)
    {
        var response = await this.httpResponseMessage.Content.ReadFromJsonAsync<T>();

        if (response is null)
        {
            throw new ArgumentException($"Failed to read HTTP response message content as type {typeof(T)}.");
        }

        return response;
    }

    public void Dispose()
    {
        this.httpResponseMessage.Dispose();
    }
}