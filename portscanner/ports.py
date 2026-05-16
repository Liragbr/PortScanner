TOP_COMMON = [

    20,21,22,23,25,53,67,68,69,80,110,111,123,135,137,138,139,143,161,162,

    179,389,443,445,465,514,515,587,631,636,873,993,995,1080,1194,1433,1521,

    1723,1883,2049,2375,2376,3000,3128,3306,3389,3690,4369,5000,5060,5432,

    5672,5900,5984,6379,6443,7001,8000,8008,8080,8081,8088,8443,8888,9000,

    9092,9200,9418,10000,11211,15672,27017,50000

]

def parse_ports(expr: str) -> list[int]:

    ports: set[int] = set()

    for chunk in expr.split(","):

        chunk = chunk.strip()

        if not chunk:

            continue

        if "-" in chunk:

            start_s, end_s = chunk.split("-", 1)

            start, end = int(start_s), int(end_s)

            if start > end:

                raise ValueError(f"Invalid range: {chunk}")

            for p in range(start, end + 1):

                if 1 <= p <= 65535:

                    ports.add(p)

        else:

            p = int(chunk)

            if not 1 <= p <= 65535:

                raise ValueError(f"Port out of range: {p}")

            ports.add(p)

    return sorted(ports)
