using FluentAssertions;
using Host.Model;
using Host.Model.Edgar;
using Host.Protocol.Edgar;

namespace Host.Unit.Tests.Model.Edgar;

[TestFixture]
internal sealed class EdgarReturnOnAssetsCalculatorTests
{
    private static readonly UsGaapFacts DummyUsGaapFacts = new(
        new CompanyFact(
            "dummy assets",
            "dummy desc", 
            new CompanyFactUnits(
                new List<CompanyFactUnit>
                {
                    // ROA 1: 2026-06-01 end; earliest filed (preferred)
                    new(
                        null,
                        new DateOnly(2020, 6, 1),
                        500,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2020, 6, 1)),
                    // ROA 1: 2026-06-01 end; filed later with different value (not preferred)
                    new(
                        null,
                        new DateOnly(2020, 6, 1),
                        600,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2021, 6, 1)),

                    // ROA 2.
                    new(
                        null,
                        new DateOnly(2021, 6, 1),
                        1000,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2021, 7, 6))
                })),
        new CompanyFact(
            "dummy net income",
            "dummy desc",
            new CompanyFactUnits(
                new List<CompanyFactUnit>
                {
                    // ROA 1: 2026-06-01 end; earliest filed (preferred)
                    new(
                        new DateOnly(2019, 6, 1),
                        new DateOnly(2020, 6, 1),
                        250,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2020, 6, 1)),
                    // ROA 1: 2026-06-01 end; filed later with different value (not preferred)
                    new(
                        new DateOnly(2019, 6, 1),
                        new DateOnly(2020, 6, 1),
                        200,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2021, 6, 1)),

                    // ROA 2.
                    new(
                        new DateOnly(2020, 6, 8),
                        new DateOnly(2021, 6, 1),
                        330,
                        null,
                        null,
                        "10-K",
                        new DateOnly(2021, 7, 6))
                })));

    private static readonly ReturnOnAssets ExpectedReturnOnAssets = new(
        new List<DatedValue<decimal>>
        {
            // ROA 1.
            new(
                new DateOnly(2020, 6, 1),
                new DateOnly(2020, 6, 1),
                (decimal) 250 / 500),

            // ROA 2.
            new(
                new DateOnly(2021, 6, 1),
                new DateOnly(2021, 7, 6),
                (decimal) 330 / 1000)
        });

    [Test]
    public void CalculatingReturnOnAssetsCalculatesCorrectly()
    {
        var returnOnAssets = new EdgarReturnOnAssetsCalculator().Calculate(DummyUsGaapFacts);

        returnOnAssets.Should().BeEquivalentTo(ExpectedReturnOnAssets);
    }
}