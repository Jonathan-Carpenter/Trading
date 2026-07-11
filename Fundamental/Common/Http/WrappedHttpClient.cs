namespace Common.Http;

public sealed class WrappedHttpClient : IWrappedHttpClient
{
    private readonly HttpClient httpClient;

    public WrappedHttpClient(HttpClient httpClient)
    {
        this.httpClient = httpClient;
    }

    public async Task<IWrappedHttpResponseMessage> SendAsync(IWrappedHttpRequestMessage request)
    {
        var response = await this.httpClient.SendAsync(request.Message);

        return new WrappedHttpResponseMessage(response);
    }
}