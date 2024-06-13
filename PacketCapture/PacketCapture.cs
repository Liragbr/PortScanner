using System;
using PacketDotNet;
using SharpPcap;
using SharpPcap.LibPcap;

public class PacketCapture
{
    public static void StartCapture(string deviceName)
    {
        var devices = CaptureDeviceList.Instance;

        foreach (var dev in devices)
        {
            if (dev.Name == deviceName)
            {
                dev.OnPacketArrival += new PacketArrivalEventHandler(OnPacketArrival);
                dev.Open(DeviceMode.Promiscuous, 1000);
                dev.StartCapture();
                break;
            }
        }
    }

    private static void OnPacketArrival(object sender, CaptureEventArgs e)
    {
        var packet = Packet.ParsePacket(e.Packet.LinkLayerType, e.Packet.Data);
        var ipPacket = (IpPacket)packet.Extract(typeof(IpPacket));

        if (ipPacket != null)
        {
            Console.WriteLine($"Packet: {ipPacket.SourceAddress} -> {ipPacket.DestinationAddress}");
        }
    }

    public static void Main(string[] args)
    {
        string deviceName = "\\Device\\NPF_{YOUR_DEVICE_ID}";
        StartCapture(deviceName);
    }
}
