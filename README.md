# 🥷🏻 Port Scanner
### Warning
I made this project in order to improve my programming logic and better understand some cybersecurity and c# issues, the code was not tested in production that is, it may contain flaws, always have explicit permission before scanning ports on systems that are not yours. Door scanners can be misinterpreted as intrusion attempts
### Introduction 
this project is a port scanning tool developed in C#. Port scanning is a crucial technique used in network security to identify open ports and services available on a target system. This tool helps in identifying potential vulnerabilities by scanning for open ports and understanding the services running on them.

Port scanning works by sending packets to specified ports on a target system and analyzing the responses. It is widely used by network administrators for security assessments and by attackers for reconnaissance. The key features of this PortScanner include:

- Multi-threaded Scanning: Enhances performance by scanning multiple ports simultaneously.
- Customizable Scanning Options: Allows users to specify the range of ports and the IP addresses to scan.
- Detailed Reporting: Provides comprehensive reports on the open ports and services detected.
This repository is designed to be a valuable resource for cybersecurity professionals, network administrators, and developers interested in network security.

## Usage
- Run the executable or start debugging from your development environment.
- Specify the target IP address and the range of ports you want to scan.
- Start the scan and view the results in the output window.

## Code Overview
### CommandExecutor.cs
The CommandExecutor class is responsible for executing system commands to gather network information.

```csharp
public class CommandExecutor
{
    public static string ExecuteCommand(string command)
    {
        // Initializes a new process to execute the command
        ProcessStartInfo procStartInfo = new ProcessStartInfo("cmd", "/c " + command)
        {
            RedirectStandardOutput = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        // Starts the process
        Process proc = new Process
        {
            StartInfo = procStartInfo
        };
        proc.Start();

        // Reads the output of the command
        return proc.StandardOutput.ReadToEnd();
    }
}
This function uses ProcessStartInfo to set up the command execution environment and Process to run the command and capture its output.
````
<br>

### PortScanner.cs
The PortScanner class handles the scanning logic.

```csharp
public class PortScanner
{
    private string targetIP;
    private int startPort;
    private int endPort;

    public PortScanner(string ip, int start, int end)
    {
        targetIP = ip;
        startPort = start;
        endPort = end;
    }

    public void Scan()
    {
        Parallel.For(startPort, endPort + 1, port =>
        {
            // Attempts to connect to the port
            using (TcpClient tcpClient = new TcpClient())
            {
                try
                {
                    tcpClient.Connect(targetIP, port);
                    Console.WriteLine($"Port {port} is open.");
                }
                catch (Exception)
                {
                    Console.WriteLine($"Port {port} is closed.");
                }
            }
        });
    }
}
```
This class sets up the scanning parameters and uses `Parallel.For` to scan ports concurrently, enhancing the scan speed significantly.
