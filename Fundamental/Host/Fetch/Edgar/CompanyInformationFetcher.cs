using Common.Http;
using Host.Protocol.Edgar;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace Host.Fetch.Edgar;

internal sealed class CompanyInformationFetcher
{
    private static readonly JsonSerializerOptions jsonSerializerOptions = new(JsonSerializerOptions.Web)
    {
        RespectRequiredConstructorParameters = true,
        RespectNullableAnnotations = true
    };

    private readonly IWrappedHttpClient httpClient;
    private readonly IWrappedHttpRequestFactory httpRequestFactory;
    private readonly ILogger<CompanyInformationFetcher> logger;

    public CompanyInformationFetcher(
        IWrappedHttpClient httpClient,
        IWrappedHttpRequestFactory httpRequestFactory,
        ILogger<CompanyInformationFetcher> logger)
    {
        this.httpClient = httpClient;
        this.httpRequestFactory = httpRequestFactory;
        this.logger = logger;
    }

    private const string CompanyTickersUrl = "https://www.sec.gov/files/company_tickers.json";
    private const string CompanyFactsUrlTemplate = "https://data.sec.gov/api/xbrl/companyfacts/CIK{0}.json";

    public async Task<IEnumerable<CompanyTicker>> GetAllCiksAsync()
    {
        var requestMessage = this.httpRequestFactory.Create(HttpMethod.Get, CompanyTickersUrl);

        var response = await this.FetchAndWrapExceptions<IDictionary<string, CompanyTicker>>(requestMessage, "get all CIKs");

        return response.Values.ToList();
    }

    public Task<CompanyFactsResponse> FetchFactsAsync(string cik)
    {
        var url = string.Format(CompanyFactsUrlTemplate, cik);

        var requestMessage = this.httpRequestFactory.Create(HttpMethod.Get, url);

        return this.FetchAndWrapExceptions<CompanyFactsResponse>(requestMessage, $"fetch company facts for CIK {cik}");
    }

    private async Task<TResponse> FetchAndWrapExceptions<TResponse>(IWrappedHttpRequestMessage httpRequestMessage, string requestDescription)
    {
        httpRequestMessage.AddHeader("User-Agent", "Fundamental/CompanyInformationFetcher");
        httpRequestMessage.AddHeader("Accept", "application/json");

        try
        {
            this.logger.LogDebug("Sending HTTP request message to {RequestDescription}.", requestDescription);

            using var response = await this.httpClient.SendAsync(httpRequestMessage);

            response.EnsureSuccessStatusCode();

            this.logger.LogDebug(
                "Reading response content after a successful response was received from request to {RequestDescription}.",
                requestDescription);

            var convertedResponse = await response.ReadContentFromJsonAsync<TResponse>(jsonSerializerOptions);

            return convertedResponse;
        }
        catch (HttpRequestException httpRequestException)
        {
            throw new DataFetchException(
                $"Failed to {requestDescription} as an error occurred during the request. See the inner exception for details.",
                httpRequestException);
        }
        catch (OperationCanceledException operationCanceledException)
        {
            throw new DataFetchException(
                $"Failed to {requestDescription} as the operation was cancelled. See the inner exception for details.",
                operationCanceledException);
        }
        catch (JsonException jsonException)
        {
            throw new DataFetchException(
                $"Failed to {requestDescription} as the returned JSON was invalid. See the inner exception for details.",
                jsonException);
        }
    }
}