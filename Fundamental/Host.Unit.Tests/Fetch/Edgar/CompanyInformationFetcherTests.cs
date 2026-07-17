using Common.Http;
using Host.Fetch;
using Host.Fetch.Edgar;
using Host.Protocol.Edgar;
using Microsoft.Extensions.Logging;
using Moq;
using System.Text.Json;

namespace Host.Unit.Tests.Fetch.Edgar;

public class CompanyInformationFetcherTests
{
    private const string DummyCik = "2468";

    private static readonly IDictionary<string, CompanyTicker> DummyCompanyCiksResponse = new Dictionary<string, CompanyTicker> { {"0", new CompanyTicker(123, "dummy ticker", "dummy title") } };

    private static readonly CompanyFactsResponse DummyCompanyFactsResponse = new(
        5,
        "dummy entity",
        new CompanyFacts(
            new UsGaapFacts(
                new CompanyFact<CompanyFactEndUnit>(
                    "dummy label",
                    "dummy description", 
                    new CompanyFactUnits<CompanyFactEndUnit>(
                        new List<CompanyFactEndUnit> 
                        { 
                            new(new DateOnly(2026, 07, 15),
                                12345,
                                567,
                                "dummy fp",
                                "10-K",
                                new DateOnly(2026, 07, 11))
                        })),
                new CompanyFact<CompanyFactRangeUnit>(
                    "dummy label 2",
                    "dummy description 2",
                    new CompanyFactUnits<CompanyFactRangeUnit>([])))));

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

    private static IEnumerable<TestCaseData> ReadResponseExceptionTestCases
    {
        get
        {
            yield return new TestCaseData(new OperationCanceledException());
            yield return new TestCaseData(new JsonException());
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

        this.mockHttpResponse
            .Setup(hr => hr.ReadContentFromJsonAsync<IDictionary<string, CompanyTicker>>(It.IsAny<JsonSerializerOptions>()))
            .ReturnsAsync(DummyCompanyCiksResponse);

        this.companyInformationFetcher = new CompanyInformationFetcher(
            this.mockHttpClient.Object,
            this.mockHttpRequestFactory.Object,
            new Mock<ILogger<CompanyInformationFetcher>>().Object);
    }

    [Test]
    public async Task GettingCiksCreatesGetRequestForCorrectUrl()
    {
        await this.companyInformationFetcher.GetAllCiksAsync();

        this.mockHttpRequestFactory.Verify(
            hrf => hrf.Create(HttpMethod.Get, "https://www.sec.gov/files/company_tickers.json"),
            Times.Once);
    }

    [Test]
    public async Task GettingCiksSetsRequestHeaders()
    {
        await this.companyInformationFetcher.GetAllCiksAsync();

        this.mockHttpRequest.Verify(
            hr => hr.AddHeader("User-Agent", "Fundamental/CompanyInformationFetcher"),
            Times.Once);

        this.mockHttpRequest.Verify(
            hr => hr.AddHeader("Accept", "application/json"),
            Times.Once);
    }

    [Test]
    public async Task GettingCiksSendsRequestAndReturnsResult()
    {
        var response = await this.companyInformationFetcher.GetAllCiksAsync();

        this.mockHttpClient.Verify(hc => hc.SendAsync(this.mockHttpRequest.Object), Times.Once);

        Assert.That(response, Is.EqualTo(DummyCompanyCiksResponse.Values));
    }

    [Test]
    public async Task GettingCiksDeserializesResponseWithCaseInsensitivityAndRequiredConstructorAndRespectNullabilityParams()
    {
        await this.companyInformationFetcher.GetAllCiksAsync();

        this.mockHttpResponse.Verify(hr =>
            hr.ReadContentFromJsonAsync<IDictionary<string, CompanyTicker>>(It.Is<JsonSerializerOptions>(options =>
                options.RespectRequiredConstructorParameters && options.PropertyNameCaseInsensitive && options.RespectNullableAnnotations)));
    }

    [Test]
    [TestCaseSource(nameof(RequestExceptionTestCases))]
    public void GettingCiksWhenSendingRequestFailsThrowsDataFetchException(Exception requestException)
    {
        this.mockHttpClient.Setup(hc => hc.SendAsync(this.mockHttpRequest.Object)).ThrowsAsync(requestException);

        Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.GetAllCiksAsync());
    }

    [Test]
    public void GettingCiksWhenEnsuringSuccessStatusCodeFailsThrowsDataFetchException()
    {
        this.mockHttpResponse.Setup(hr => hr.EnsureSuccessStatusCode()).Throws(new HttpRequestException());

        Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.GetAllCiksAsync());
    }

    [Test]
    [TestCaseSource(nameof(ReadResponseExceptionTestCases))]
    public void GettingCiksWhenReadingResponseFailsThrowsDataFetchException(Exception exception)
    {
        this.mockHttpResponse
            .Setup(hr => hr.ReadContentFromJsonAsync<IDictionary<string, CompanyTicker>>(It.IsAny<JsonSerializerOptions>()))
            .ThrowsAsync(exception);

        var dataFetchException = Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.GetAllCiksAsync());

        Assert.That(dataFetchException, Is.Not.Null);
        Assert.That(dataFetchException.InnerException, Is.EqualTo(exception));
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
    public async Task FetchingFactsDeserializesResponseWithCaseInsensitivityAndRequiredConstructorAndRespectNullabilityParams()
    {
        await this.companyInformationFetcher.FetchFactsAsync(DummyCik);

        this.mockHttpResponse.Verify(hr =>
            hr.ReadContentFromJsonAsync<CompanyFactsResponse>(It.Is<JsonSerializerOptions>(options =>
                options.RespectRequiredConstructorParameters && options.PropertyNameCaseInsensitive && options.RespectNullableAnnotations)));
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
    [TestCaseSource(nameof(ReadResponseExceptionTestCases))]
    public void FetchingFactsWhenReadingResponseFailsThrowsDataFetchException(Exception exception)
    {
        this.mockHttpResponse
            .Setup(hr => hr.ReadContentFromJsonAsync<CompanyFactsResponse>(It.IsAny<JsonSerializerOptions>()))
            .ThrowsAsync(exception);

        var dataFetchException = Assert.ThrowsAsync<DataFetchException>(() => this.companyInformationFetcher.FetchFactsAsync(DummyCik));

        Assert.That(dataFetchException, Is.Not.Null);
        Assert.That(dataFetchException.InnerException, Is.EqualTo(exception));
    }
}
