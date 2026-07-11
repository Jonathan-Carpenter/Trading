using Common.Http;
using Host.Fetch;
using Host.Fetch.Edgar;
using Host.Protocol.Edgar;
using Microsoft.Extensions.Logging;
using Moq;
using System.Text.Json;

namespace Host.Unit.Tests.Fetch.Edgar;

public class Tests
{
    private const string DummyCik = "2468";

    private static readonly CompanyFactsResponse DummyCompanyFactsResponse = new(
        5,
        "dummy entity",
        new CompanyFacts(
            new UsGaapFacts(
                new CompanyFact(
                    "dummy label",
                    "dummy description", 
                    new CompanyFactUnits(
                        new List<CompanyFactUnit> 
                        { 
                            new(
                                null,
                                new DateOnly(2026, 07, 10),
                                12345,
                                567,
                                "dummy fp",
                                "10-K",
                                new DateOnly(2026, 07, 11))
                        })),
                new CompanyFact(
                    "dummy label 2",
                    "dummy description 2",
                    new CompanyFactUnits([])))));

    private Mock<IWrappedHttpClient> mockHttpClient;
    private Mock<IWrappedHttpRequestFactory> mockHttpRequestFactory;

    private Mock<IWrappedHttpRequestMessage> mockHttpRequest;
    private Mock<IWrappedHttpResponseMessage> mockHttpResponse;

    private CompanyInformationFetcher companyInformationFetcher;

    private static IEnumerable<TestCaseData> RequestExceptionTestCases
    {
        get
        {
            yield return new TestCaseData(new HttpRequestException());
            yield return new TestCaseData(new OperationCanceledException());
        }
    }

    [SetUp]
    public void Setup()
    {
        this.mockHttpClient = new Mock<IWrappedHttpClient>();
        this.mockHttpRequestFactory = new Mock<IWrappedHttpRequestFactory>();

        this.mockHttpRequest = new Mock<IWrappedHttpRequestMessage>();
        this.mockHttpResponse = new Mock<IWrappedHttpResponseMessage>();

        this.mockHttpRequestFactory
            .Setup(hrf => hrf.Create(It.IsAny<HttpMethod>(), It.IsAny<string>()))
            .Returns(this.mockHttpRequest.Object);

        this.mockHttpClient
            .Setup(hc => hc.SendAsync(this.mockHttpRequest.Object))
            .ReturnsAsync(this.mockHttpResponse.Object);

        this.mockHttpResponse
            .Setup(hr => hr.ReadContentFromJsonAsync<CompanyFactsResponse>(It.IsAny<JsonSerializerOptions>()))
            .ReturnsAsync(DummyCompanyFactsResponse);

        this.companyInformationFetcher = new CompanyInformationFetcher(
            this.mockHttpClient.Object,
            this.mockHttpRequestFactory.Object,
            new Mock<ILogger<CompanyInformationFetcher>>().Object);
    }

    [Test]
    public async Task FetchingFactsCreatesGetRequestForFormattedUrl()
    {
        await this.companyInformationFetcher.FetchFactsAsync(DummyCik);

        this.mockHttpRequestFactory.Verify(
            hrf => hrf.Create(HttpMethod.Get, "https://data.sec.gov/api/xbrl/companyfacts/CIK2468.json"),
            Times.Once);
    }

    [Test]
    public async Task FetchingFactsSetsRequestHeaders()
    {
        await this.companyInformationFetcher.FetchFactsAsync(DummyCik);

        this.mockHttpRequest.Verify(
            hr => hr.AddHeader("User-Agent", "Fundamental/CompanyInformationFetcher"),
            Times.Once);

        this.mockHttpRequest.Verify(
            hr => hr.AddHeader("Accept", "application/json"),
            Times.Once);
    }

    [Test]
    public async Task FetchingFactsSendsRequestAndReturnsResult()
    {
        var response = await this.companyInformationFetcher.FetchFactsAsync(DummyCik);

        this.mockHttpClient.Verify(hc => hc.SendAsync(this.mockHttpRequest.Object), Times.Once);

        Assert.That(response, Is.EqualTo(DummyCompanyFactsResponse));
    }

    [Test]
    public async Task FetchingFactsDeserializesResponseWithCaseInsensitivityAndRequiredConstructorParams()
    {
        await this.companyInformationFetcher.FetchFactsAsync(DummyCik);

        this.mockHttpResponse.Verify(hr =>
            hr.ReadContentFromJsonAsync<CompanyFactsResponse>(It.Is<JsonSerializerOptions>(options =>
                options.RespectRequiredConstructorParameters && options.PropertyNameCaseInsensitive)));
    }

    [Test]
    [TestCaseSource(nameof(RequestExceptionTestCases))]
    public void FetchingFactsWhenSendingRequestFailsThrowsDataFetchException(Exception requestException)
    {
        this.mockHttpClient.Setup(hc => hc.SendAsync(this.mockHttpRequest.Object)).ThrowsAsync(requestException);

        Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.FetchFactsAsync(DummyCik));
    }

    [Test]
    public void FetchingFactsWhenEnsuringSuccessStatusCodeFailsThrowsDataFetchException()
    {
        this.mockHttpResponse.Setup(hr => hr.EnsureSuccessStatusCode()).Throws(new HttpRequestException());
        
        Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.FetchFactsAsync(DummyCik));
    }

    [Test]
    public void FetchingFactsWhenReadingResponseFailsThrowsDataFetchException()
    {
        this.mockHttpResponse
            .Setup(hr => hr.ReadContentFromJsonAsync<CompanyFactsResponse>(It.IsAny<JsonSerializerOptions>()))
            .ThrowsAsync(new OperationCanceledException());

        Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.FetchFactsAsync(DummyCik));
    }
}
