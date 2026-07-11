using Host.Protocol.Edgar;

namespace Host.Model.Edgar;

internal sealed class EdgarReturnOnAssetsCalculator : IEdgarReturnOnAssetsCalculator
{
    public ReturnOnAssets Calculate(UsGaapFacts facts)
    {
        var assets = GetYearEndAssets(facts);
        var incomes = GetYearEndNetIncome(facts);

        var returnOnAssets = new Dictionary<DateOnly, DatedValue<decimal>>();

        foreach (var assetUnit in assets.Values)
        {
            var end = assetUnit.End;

            if (!incomes.TryGetValue(end, out var incomeUnit))
            {
                continue;
            }

            // Use later filing date of two units - this is the earliest this calculation could have been made.
            var filed = assetUnit.Filed.DayNumber >= incomeUnit.Filed.DayNumber
                ? assetUnit.Filed
                : incomeUnit.Filed;

            var returnOnAssetsValue = (decimal) incomeUnit.Val / assetUnit.Val;

            returnOnAssets[end] = new DatedValue<decimal>(end, filed, returnOnAssetsValue);
        }

        var returnOnAssetsSeries = returnOnAssets.Values
            .AsEnumerable()
            .OrderBy(v => v.End)
            .ToList();

        return new ReturnOnAssets(returnOnAssetsSeries);
    }

    private static Dictionary<DateOnly, CompanyFactUnit> GetYearEndAssets(UsGaapFacts facts) =>
        facts.Assets.Units.Usd
            .Where(u => u.IsAnnualFiling)
            .GroupBy(u => u.End)
            .Select(g => g.OrderBy(u => u.Filed))
            .Select(g => g.First())
            .ToDictionary(u => u.End, u => u);

    private static Dictionary<DateOnly, CompanyFactUnit> GetYearEndNetIncome(UsGaapFacts facts) =>
        facts.NetIncomeLoss.Units.Usd
            .Where(u => u.IsAnnualFiling && u.IsFullYearFiling)
            .GroupBy(u => u.End)
            .Select(g => g.OrderBy(u => u.Filed))
            .Select(g => g.First())
            .ToDictionary(u => u.End, u => u);
}