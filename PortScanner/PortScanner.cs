using System;
using System.Net.Sockets;
using System.Threading.Tasks;

public class PortScanner
{
    public static void ScanPorts(string host, int startPort, int endPort)
    {
        Parallel.For(startPort, endPort + 1, async port =>
        {
            using (TcpClient client = new TcpClient())
            {
                try
                {
                    await client.ConnectAsync(host, port);
                    Console.WriteLine($"Port {port} is open");
                    string service = IdentifyService(port);
                    Console.WriteLine($"Service: {service}");
                }
                catch (SocketException)
                {
                    Console.WriteLine($"Port {port} is closed");
                }
            }
        });
    }

    private static string IdentifyService(int port)
    {
        return port switch
        {
            21 => "FTP",
            22 => "SSH",
            23 => "Telnet",
            25 => "SMTP",
            53 => "DNS",
            80 => "HTTP",
            110 => "POP3",
            143 => "IMAP",
            443 => "HTTPS",
            3306 => "MySQL",
            3389 => "RDP",
            _ => "Unknown"
        };
    }

    public static void Main(string[] args)
    {
        string host = "127.0.0.1";
        int startPort = 1;
        int endPort = 1024;

        ScanPorts(host, startPort, endPort);
    }
}
