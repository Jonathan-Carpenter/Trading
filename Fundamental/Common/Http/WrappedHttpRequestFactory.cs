namespace Common.Http;

public sealed class WrappedHttpRequestFactory : IWrappedHttpRequestFactory
{
    public IWrappedHttpRequestMessage Create(HttpMethod httpMethod, string url)
    {
        return new WrappedHttpRequestMessage(new HttpRequestMessage(httpMethod, url));
    }
}