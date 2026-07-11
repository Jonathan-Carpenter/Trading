namespace Common.Http;

public interface IWrappedHttpRequestFactory
{
    IWrappedHttpRequestMessage Create(HttpMethod httpMethod, string url);
}