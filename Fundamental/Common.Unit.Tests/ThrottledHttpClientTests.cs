using Common.Http;
using Moq;

namespace Common.Unit.Tests;

public class ThrottledHttpClientTests
{
    private static readonly TimeSpan DummyMinTimeBetweenRequests = TimeSpan.FromMilliseconds(500);

    private Mock<IWrappedHttpClient> mockHttpClient;

    private ThrottledHttpClient throttledHttpClient;

    [SetUp]
    public void SetUp()
    {
        this.mockHttpClient = new Mock<IWrappedHttpClient>();

        this.throttledHttpClient = new ThrottledHttpClient(this.mockHttpClient.Object, DummyMinTimeBetweenRequests);
    }

    [Test]
    public async Task SendingRequestSendsRequest()
    {
        var mockRequest = new Mock<IWrappedHttpRequestMessage>();

        await this.throttledHttpClient.SendAsync(mockRequest.Object);

        this.mockHttpClient.Verify(hc => hc.SendAsync(mockRequest.Object), Times.Once);
    }

    [Test]
    public async Task SendingMultipleRequestsThrottlesEachRequest()
    {
        var testStart = DateTimeOffset.Now;

        var mockRequest = new Mock<IWrappedHttpRequestMessage>();

        await this.throttledHttpClient.SendAsync(mockRequest.Object);

        var elapsed = DateTimeOffset.Now - testStart;

        Assert.That(elapsed, Is.GreaterThan(DummyMinTimeBetweenRequests));

        await this.throttledHttpClient.SendAsync(mockRequest.Object);

        elapsed = DateTimeOffset.Now - testStart;

        Assert.That(elapsed, Is.GreaterThan(2 * DummyMinTimeBetweenRequests));
    }
}
