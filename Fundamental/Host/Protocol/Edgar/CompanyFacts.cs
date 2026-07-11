using System.Text.Json.Serialization;

namespace Host.Protocol.Edgar;

internal sealed class CompanyFacts(UsGaapFacts usGaap)
{
    [JsonPropertyName("us-gaap")]
    public UsGaapFacts UsGaap { get; } = usGaap;
}