

import asyncio
from bizkaibusAPI import BizkaibusAPI
from Model.BizkaibusLanguages import BizkaibusLanguages

async def main():
    stop_id = '0296'
    api = BizkaibusAPI(BizkaibusLanguages.EU, stop_id)
    lines = await api.GetLinesOnStop()
    print(f"Líneas en la parada {stop_id}:")
    for line in lines:
        print(f"- {line}")

if __name__ == "__main__":
    asyncio.run(main())