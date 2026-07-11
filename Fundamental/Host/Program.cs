using Common.Http;
using Host.Fetch.Edgar;
using Host.Model.Edgar;
using Microsoft.Extensions.Logging;
using Serilog;
using Serilog.Extensions.Logging;

namespace Host;

internal class Program
{
    static async Task Main()
    {
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Verbose()
            .WriteTo.Console()
            .WriteTo.File("./Host.log")
            .CreateLogger();

        var loggerFactory = new SerilogLoggerFactory(Log.Logger);

        var companyInformationFetcher = new CompanyInformationFetcher(
            new ThrottledHttpClient(new WrappedHttpClient(new HttpClient()), TimeSpan.FromSeconds(1)),
            new WrappedHttpRequestFactory(),
            loggerFactory.CreateLogger<CompanyInformationFetcher>());

        var facts = await companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        var returnOnAssets = new EdgarReturnOnAssetsCalculator().Calculate(facts.Facts.UsGaap);

        Console.ReadLine();
    }
}