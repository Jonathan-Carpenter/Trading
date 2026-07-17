using Common.Http;
using Host.Fetch;
using Host.Fetch.Edgar;
using Host.Model;
using Host.Model.Edgar;
using Host.Protocol.Edgar;
using Microsoft.Extensions.Logging;
using Serilog;
using Serilog.Extensions.Logging;

namespace Host;

internal class Program
{
    static async Task Main()
    {
        Console.WriteLine("Fundamental is running...");

        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Verbose()
            .WriteTo.File("./logs/Host.log", rollOnFileSizeLimit: true)
            .CreateLogger();

        var loggerFactory = new SerilogLoggerFactory(Log.Logger);
        var programLogger = loggerFactory.CreateLogger<Program>();

        var companyInformationFetcher = new CompanyInformationFetcher(
            new ThrottledHttpClient(new WrappedHttpClient(new HttpClient()), TimeSpan.FromMilliseconds(100)),
            new WrappedHttpRequestFactory(),
            loggerFactory.CreateLogger<CompanyInformationFetcher>());

        var ciks = (await companyInformationFetcher.GetAllCiksAsync()).ToList();
        var allReturnOnAssets = new List<(CompanyTicker, DatedValue<decimal>)>();

        var i = 0;
        var j = Math.Min(1000, ciks.Count);

        foreach (var cik in ciks)
        {
            if (++i > j)
            {
                break;
            }

            programLogger.LogDebug(
                "Calculating return on assets. Progress: {CurrentIncrement}/{TotalIncrements}.",
                i,
                j);

            try
            {
                var facts = await companyInformationFetcher.FetchFactsAsync(cik.CikStr.ToString("D10"));
                var returnOnAssets = new EdgarReturnOnAssetsCalculator().Calculate(facts.Facts.UsGaap);
                var lastReturnOnAssets = returnOnAssets.Values.LastOrDefault();

                if (lastReturnOnAssets is not null)
                {
                    allReturnOnAssets.Add((cik, lastReturnOnAssets));

                    programLogger.LogDebug(
                        "Computed return on assets for {CompanyTicker}.",
                        cik.Ticker);
                }
                else
                {
                    programLogger.LogDebug(
                        "Could not compute any return on assets for {CompanyTicker}.",
                        cik.Ticker);
                }
            }
            catch (DataFetchException dataFetchException)
            {
                programLogger.LogWarning(
                    dataFetchException,
                    "Failed to compute return on assets for {CompanyTicker} as data could not be fetched. See the exception for details.",
                    cik.Ticker);
            }
        }

        programLogger.LogInformation("Return on assets calculation complete. The following messages show the ranked results of the calculations.");

        allReturnOnAssets = allReturnOnAssets.OrderByDescending(tuple => tuple.Item2.Value).ToList();

        foreach (var tuple in allReturnOnAssets)
        {
            programLogger.LogInformation("{CompanyTitle} ({CompanyTicker}) return on assets: {ReturnOnAssets} ({ReturnOnAssetsEndDate}).", tuple.Item1.Title, tuple.Item1.Ticker, tuple.Item2.Value, tuple.Item2.End);
        }

        Console.WriteLine("Fundamental has finished.");

        Console.ReadLine();
    }
}