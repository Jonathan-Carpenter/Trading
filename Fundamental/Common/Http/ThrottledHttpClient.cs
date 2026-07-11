namespace Common.Http;

public sealed class ThrottledHttpClient : IWrappedHttpClient
{
    private readonly IWrappedHttpClient httpClient;
    private readonly TimeSpan minTimeBetweenRequests;

    public ThrottledHttpClient(IWrappedHttpClient httpClient, TimeSpan minTimeBetweenRequests)
    {
        this.httpClient = httpClient;
        this.minTimeBetweenRequests = minTimeBetweenRequests;
    }

    public async Task<IWrappedHttpResponseMessage> SendAsync(IWrappedHttpRequestMessage request)
    {
        await Task.Delay(this.minTimeBetweenRequests);

        return await this.httpClient.SendAsync(request);
    }
}