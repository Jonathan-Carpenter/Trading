using Host.Fetch.Edgar;

namespace Host.Integration.Tests.Fetch.Edgar;

internal sealed class CompanyInformationFetcherTests
{
    private CompanyInformationFetcher companyInformationFetcher;

    [SetUp]
    public void Setup()
    {
        this.companyInformationFetcher = new CompanyInformationFetcher(new HttpClient());
    }

    [Test]
    public async Task FetchingCompanyFactsFetchesFacts()
    {
        var companyFactsResponse = await this.companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        Assert.That(companyFactsResponse.Cik, Is.EqualTo(320193));
        Assert.That(companyFactsResponse.EntityName, Is.EqualTo("Apple Inc."));

        var assetUnits = companyFactsResponse.Facts.UsGaap.Assets.Units.Usd.ToList();
        
        var september2008Units = assetUnits.Where(u => u.End == new DateOnly(2008, 9, 27)).ToList();

        Assert.That(september2008Units, Has.Count.EqualTo(4));

        Assert.That(september2008Units[0].Val, Is.EqualTo(39572000000));
        Assert.That(september2008Units[0].Fy, Is.EqualTo(2009));
        Assert.That(september2008Units[0].Fp, Is.EqualTo("Q3"));
        Assert.That(september2008Units[0].Filed, Is.EqualTo(new DateOnly(2009, 7, 22)));

        Assert.That(september2008Units[1].Val, Is.EqualTo(39572000000));
        Assert.That(september2008Units[1].Fy, Is.EqualTo(2009));
        Assert.That(september2008Units[1].Fp, Is.EqualTo("FY"));
        Assert.That(september2008Units[1].Filed, Is.EqualTo(new DateOnly(2009, 10, 27)));

        Assert.That(september2008Units[2].Val, Is.EqualTo(36171000000));
        Assert.That(september2008Units[2].Fy, Is.EqualTo(2009));
        Assert.That(september2008Units[2].Fp, Is.EqualTo("FY"));
        Assert.That(september2008Units[2].Filed, Is.EqualTo(new DateOnly(2010, 1, 25)));

        Assert.That(september2008Units[3].Val, Is.EqualTo(36171000000));
        Assert.That(september2008Units[3].Fy, Is.EqualTo(2010));
        Assert.That(september2008Units[3].Fp, Is.EqualTo("FY"));
        Assert.That(september2008Units[3].Filed, Is.EqualTo(new DateOnly(2010, 10, 27)));
    }
}
