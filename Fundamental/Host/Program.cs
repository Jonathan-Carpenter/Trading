using Host.Fetch.Edgar;

namespace Host;

internal class Program
{
    static async Task Main()
    {
        var httpClient = new HttpClient();
        var companyInformationFetcher = new CompanyInformationFetcher(httpClient);

        await companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        Console.ReadLine();
    }
}