using Common.Http;
using Host.Fetch.Edgar;
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
            new WrappedHttpClient(new HttpClient()),
            new WrappedHttpRequestFactory(),
            loggerFactory.CreateLogger<CompanyInformationFetcher>());

        await companyInformationFetcher.FetchFactsAsync(CompanyCiks.AppleInc);

        Console.ReadLine();
    }
}