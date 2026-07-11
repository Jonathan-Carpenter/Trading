using Host.Protocol.Edgar;
using System.Net.Http.Json;
using System.Text.Json;

namespace Host.Fetch.Edgar;

internal sealed class CompanyInformationFetcher(HttpClient httpClient)
{
    private const string CompanyFactsUrlTemplate = "https://data.sec.gov/api/xbrl/companyfacts/CIK{0}.json";

    public async Task<CompanyFactsResponse> FetchFactsAsync(string cik)
    {
        var url = string.Format(CompanyFactsUrlTemplate, cik);
        var requestMessage = new HttpRequestMessage(HttpMethod.Get, url);

        requestMessage.Headers.Add("User-Agent", "Fundamental/CompanyInformationFetcher");
        requestMessage.Headers.Add("Accept", "application/json");

        using var response = await httpClient.SendAsync(requestMessage);

        response.EnsureSuccessStatusCode();

        var jsonSerializerOptions = new JsonSerializerOptions(JsonSerializerOptions.Web)
        {
            RespectRequiredConstructorParameters = true
        };

        var companyFactsResponse = await response.Content.ReadFromJsonAsync<CompanyFactsResponse>(jsonSerializerOptions);

        return companyFactsResponse;
    }
}