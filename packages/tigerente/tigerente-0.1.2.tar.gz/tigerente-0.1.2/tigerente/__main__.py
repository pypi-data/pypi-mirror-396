import asyncio
import sys

from tigerente import client, daemon

if sys.argv[-1] == "--d--":
    asyncio.run(daemon.main())
else:
    client.main()
