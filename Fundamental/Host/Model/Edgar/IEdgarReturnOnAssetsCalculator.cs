using Host.Protocol.Edgar;

namespace Host.Model.Edgar;

internal interface IEdgarReturnOnAssetsCalculator
{
    ReturnOnAssets Calculate(UsGaapFacts facts);
}