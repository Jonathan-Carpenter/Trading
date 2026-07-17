using System;
using System.Collections.Generic;
using System.Net;
using System.Text;

namespace Host.Behavior.Tests;

internal sealed class StubHttpMessageHandler(string json) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken) =>
        Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json"),
            RequestMessage = request
        });
}
