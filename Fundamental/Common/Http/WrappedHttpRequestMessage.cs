namespace Common.Http;

public sealed class WrappedHttpRequestMessage : IWrappedHttpRequestMessage
{
    private readonly HttpRequestMessage httpRequestMessage;

    public WrappedHttpRequestMessage(HttpRequestMessage httpRequestMessage)
    {
        this.httpRequestMessage = httpRequestMessage;
    }

    public void AddHeader(string name, string value)
    {
        this.httpRequestMessage.Headers.Add(name, value);
    }

    public HttpRequestMessage Message => this.httpRequestMessage;
}