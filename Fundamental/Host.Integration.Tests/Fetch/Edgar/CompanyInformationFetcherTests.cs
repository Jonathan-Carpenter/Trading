using Common.Http;
using Host.Fetch.Edgar;
using Microsoft.Extensions.Logging;
using Moq;

namespace Host.Integration.Tests.Fetch.Edgar;

internal sealed class CompanyInformationFetcherTests
{
    private CompanyInformationFetcher companyInformationFetcher;

    [SetUp]
    public void Setup()
    {
        this.companyInformationFetcher = new CompanyInformationFetcher(
            new ThrottledHttpClient(new WrappedHttpClient(new HttpClient()), TimeSpan.FromMilliseconds(100)),
            new WrappedHttpRequestFactory(),
            new Mock<ILogger<CompanyInformationFetcher>>().Object);
    }

    [Test]
    public async Task FetchingCompanyFactsFetchesAssetFacts()
    {
        var companyFactsResponse = await this.companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        Assert.That(companyFactsResponse.Cik, Is.EqualTo(320193));
        Assert.That(companyFactsResponse.EntityName, Is.EqualTo("Apple Inc."));

        var assetUnits = companyFactsResponse.Facts.UsGaap.Assets.Units.Usd.ToList();
        
        var september2008AssetUnits = assetUnits.Where(u => u.End == new DateOnly(2008, 9, 27)).ToList();

        Assert.That(september2008AssetUnits, Has.Count.EqualTo(4));

        Assert.That(september2008AssetUnits[0].Val, Is.EqualTo(39572000000));
        Assert.That(september2008AssetUnits[0].Fy, Is.EqualTo(2009));
        Assert.That(september2008AssetUnits[0].Fp, Is.EqualTo("Q3"));
        Assert.That(september2008AssetUnits[0].Form, Is.EqualTo("10-Q"));
        Assert.That(september2008AssetUnits[0].Filed, Is.EqualTo(new DateOnly(2009, 7, 22)));

        Assert.That(september2008AssetUnits[1].Val, Is.EqualTo(39572000000));
        Assert.That(september2008AssetUnits[1].Fy, Is.EqualTo(2009));
        Assert.That(september2008AssetUnits[1].Fp, Is.EqualTo("FY"));
        Assert.That(september2008AssetUnits[1].Form, Is.EqualTo("10-K"));
        Assert.That(september2008AssetUnits[1].Filed, Is.EqualTo(new DateOnly(2009, 10, 27)));

        Assert.That(september2008AssetUnits[2].Val, Is.EqualTo(36171000000));
        Assert.That(september2008AssetUnits[2].Fy, Is.EqualTo(2009));
        Assert.That(september2008AssetUnits[2].Fp, Is.EqualTo("FY"));
        Assert.That(september2008AssetUnits[2].Form, Is.EqualTo("10-K/A"));
        Assert.That(september2008AssetUnits[2].Filed, Is.EqualTo(new DateOnly(2010, 1, 25)));

        Assert.That(september2008AssetUnits[3].Val, Is.EqualTo(36171000000));
        Assert.That(september2008AssetUnits[3].Fy, Is.EqualTo(2010));
        Assert.That(september2008AssetUnits[3].Fp, Is.EqualTo("FY"));
        Assert.That(september2008AssetUnits[3].Form, Is.EqualTo("10-K"));
        Assert.That(september2008AssetUnits[3].Filed, Is.EqualTo(new DateOnly(2010, 10, 27)));
    }

    [Test]
    public async Task FetchingCompanyFactsFetchesNetIncomeLossFacts()
    {
        var companyFactsResponse = await this.companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        Assert.That(companyFactsResponse.Cik, Is.EqualTo(320193));
        Assert.That(companyFactsResponse.EntityName, Is.EqualTo("Apple Inc."));

        var assetUnits = companyFactsResponse.Facts.UsGaap.NetIncomeLoss.Units.Usd.ToList();

        var september2008NetIncomeLossUnits = assetUnits.Where(u => u.End == new DateOnly(2008, 9, 27)).ToList();

        Assert.That(september2008NetIncomeLossUnits, Has.Count.EqualTo(3));

        Assert.That(september2008NetIncomeLossUnits[0].Start, Is.EqualTo(new DateOnly(2007, 9, 30)));
        Assert.That(september2008NetIncomeLossUnits[0].Val, Is.EqualTo(4834000000));
        Assert.That(september2008NetIncomeLossUnits[0].Fy, Is.EqualTo(2009));
        Assert.That(september2008NetIncomeLossUnits[0].Fp, Is.EqualTo("FY"));
        Assert.That(september2008NetIncomeLossUnits[0].Form, Is.EqualTo("10-K"));
        Assert.That(september2008NetIncomeLossUnits[0].Filed, Is.EqualTo(new DateOnly(2009, 10, 27)));

        Assert.That(september2008NetIncomeLossUnits[1].Start, Is.EqualTo(new DateOnly(2007, 9, 30)));
        Assert.That(september2008NetIncomeLossUnits[1].Val, Is.EqualTo(6119000000));
        Assert.That(september2008NetIncomeLossUnits[1].Fy, Is.EqualTo(2009));
        Assert.That(september2008NetIncomeLossUnits[1].Fp, Is.EqualTo("FY"));
        Assert.That(september2008NetIncomeLossUnits[1].Form, Is.EqualTo("10-K/A"));
        Assert.That(september2008NetIncomeLossUnits[1].Filed, Is.EqualTo(new DateOnly(2010, 1, 25)));
        
        Assert.That(september2008NetIncomeLossUnits[2].Start, Is.EqualTo(new DateOnly(2007, 9, 30)));
        Assert.That(september2008NetIncomeLossUnits[2].Val, Is.EqualTo(6119000000));
        Assert.That(september2008NetIncomeLossUnits[2].Fy, Is.EqualTo(2010));
        Assert.That(september2008NetIncomeLossUnits[2].Fp, Is.EqualTo("FY"));
        Assert.That(september2008NetIncomeLossUnits[2].Form, Is.EqualTo("10-K"));
        Assert.That(september2008NetIncomeLossUnits[2].Filed, Is.EqualTo(new DateOnly(2010, 10, 27)));
    }

    [Test]
    public async Task FetchingAllCiksFetchesCiks()
    {
        var tickers = (await this.companyInformationFetcher.GetAllCiksAsync()).ToList();

        var appleTicker = tickers.SingleOrDefault(t => t.CikStr == 320193);

        Assert.That(appleTicker, Is.Not.Null);
        Assert.That(appleTicker.Ticker, Is.EqualTo("AAPL"));
        Assert.That(appleTicker.Title, Is.EqualTo("Apple Inc."));

        var netflixTicker = tickers.SingleOrDefault(t => t.CikStr == 1065280);

        Assert.That(netflixTicker, Is.Not.Null);
        Assert.That(netflixTicker.Ticker, Is.EqualTo("NFLX"));
        Assert.That(netflixTicker.Title, Is.EqualTo("NETFLIX INC"));
    }
}
