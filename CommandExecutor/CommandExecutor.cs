using System;
using System.Diagnostics;
using System.Threading.Tasks;

public class CommandExecutor
{
    public static async Task ExecuteCommandAsync(string command)
    {
        ProcessStartInfo procStartInfo = new ProcessStartInfo("cmd", "/c " + command)
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using (Process proc = new Process { StartInfo = procStartInfo })
        {
            proc.Start();
            
            string result = await proc.StandardOutput.ReadToEndAsync();
            string error = await proc.StandardError.ReadToEndAsync();

            if (!string.IsNullOrEmpty(result))
                Console.WriteLine("Output: " + result);

            if (!string.IsNullOrEmpty(error))
                Console.WriteLine("Error: " + error);
        }
    }

    public static async Task Main(string[] args)
    {
        string command = "ipconfig";
        await ExecuteCommandAsync(command);
    }
}
