using System.Text.Json.Serialization;

namespace Host.Protocol.Edgar;

internal sealed class CompanyTicker(int cikStr, string ticker, string title)
{
    [JsonPropertyName("cik_str")]
    public int CikStr { get; } = cikStr;

    public string Ticker { get; } = ticker;

    public string Title { get; } = title;
}