using System;
using System.Net;

public class NetworkInfo
{
    public static void GetLocalNetworkInfo()
    {
        string hostName = Dns.GetHostName();
        Console.WriteLine($"Host Name: {hostName}");

        IPAddress[] addresses = Dns.GetHostAddresses(hostName);
        foreach (var address in addresses)
        {
            Console.WriteLine($"IP Address: {address}");
        }
    }

    public static void Main(string[] args)
    {
        GetLocalNetworkInfo();
    }
}
