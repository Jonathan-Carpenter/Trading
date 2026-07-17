using Common.Http;
using Host.Fetch.Edgar;
using Host.Model.Edgar;
using Microsoft.Extensions.Logging.Abstractions;

namespace Host.Behavior.Tests.Edgar;

public class EdgarCalculationTests
{
    private CompanyInformationFetcher companyInformationFetcher;
    private EdgarReturnOnAssetsCalculator edgarReturnOnAssetsCalculator;

    [SetUp]
    public async Task SetupAsync()
    {
        var appleFactsPath = Path.Combine(AppContext.BaseDirectory, "Edgar", "CIK0000320193.json");
        var appleFactsJson = await File.ReadAllTextAsync(appleFactsPath);
        var dummyHttpClient = new HttpClient(new StubHttpMessageHandler(appleFactsJson));

        this.companyInformationFetcher =
            new CompanyInformationFetcher(
                new WrappedHttpClient(dummyHttpClient),
                new WrappedHttpRequestFactory(),
                new NullLogger<CompanyInformationFetcher>());

        this.edgarReturnOnAssetsCalculator = new EdgarReturnOnAssetsCalculator();
    }
    
    [Test]
    public async Task FetchingAndCalculatingReturnOnAssetsCalculatesReturnOnAssets()
    {
        var appleFacts = await this.companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);
        var returnOnAssets = this.edgarReturnOnAssetsCalculator.Calculate(appleFacts.Facts.UsGaap);

        var latestThree = returnOnAssets.Values.Reverse().Take(3).ToList();

        Assert.That(latestThree[0].Value, Is.EqualTo(0.3117962593356548946250567168).Within(0.0001));
        Assert.That(latestThree[0].End, Is.EqualTo(new DateOnly(2025, 9, 27)));
        Assert.That(latestThree[0].Filed, Is.EqualTo(new DateOnly(2025, 10, 31)));

        Assert.That(latestThree[1].Value, Is.EqualTo(0.2568250315085758123732807277).Within(0.0001));
        Assert.That(latestThree[1].End, Is.EqualTo(new DateOnly(2024, 9, 28)));
        Assert.That(latestThree[1].Filed, Is.EqualTo(new DateOnly(2024, 11, 1)));

        Assert.That(latestThree[2].Value, Is.EqualTo(0.2750983456377647249016543622).Within(0.0001));
        Assert.That(latestThree[2].End, Is.EqualTo(new DateOnly(2023, 9, 30)));
        Assert.That(latestThree[2].Filed, Is.EqualTo(new DateOnly(2023, 11, 3)));
    }
}
