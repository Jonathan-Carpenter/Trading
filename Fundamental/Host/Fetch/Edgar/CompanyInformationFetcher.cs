using Common.Http;
using Host.Protocol.Edgar;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace Host.Fetch.Edgar;

internal sealed class CompanyInformationFetcher
{
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

    private const string CompanyFactsUrlTemplate = "https://data.sec.gov/api/xbrl/companyfacts/CIK{0}.json";

    public async Task<CompanyFactsResponse> FetchFactsAsync(string cik)
    {
        var url = string.Format(CompanyFactsUrlTemplate, cik);

        var requestMessage = this.httpRequestFactory.Create(HttpMethod.Get, url);
        requestMessage.AddHeader("User-Agent", "Fundamental/CompanyInformationFetcher");
        requestMessage.AddHeader("Accept", "application/json");

        try
        {
            using var response = await this.httpClient.SendAsync(requestMessage);

            response.EnsureSuccessStatusCode();

            var jsonSerializerOptions = new JsonSerializerOptions(JsonSerializerOptions.Web)
            {
                RespectRequiredConstructorParameters = true
            };

            var companyFactsResponse =
                await response.ReadContentFromJsonAsync<CompanyFactsResponse>(jsonSerializerOptions);

            return companyFactsResponse;
        }
        catch (HttpRequestException httpRequestException)
        {
            throw new DataFetchException(
                $"Failed to fetch company facts for CIK {cik} as an error occurred during the request. See the inner exception for details.",
                httpRequestException);
        }
        catch (OperationCanceledException operationCanceledException)
        {
            throw new DataFetchException(
                $"Failed to fetch company facts for CIK {cik} as the operation was cancelled. See the inner exception for details.",
                operationCanceledException);
        }
    }
}