import asyncio
import urllib.parse
import aiohttp
from aiohttp_socks import ProxyConnector

opensea_api_key = ''

USE_PROXY = False
proxy = ''

NEW_LIST_AMOUNT = 35  # number of listings to check for validity. the cheapest listings are checked.

LIST_ON_PAGE = 100  # amount of listings on page
PAGES_AMOUNT = 2  # amount of pages to check, 1 page = LIST_ON_PAGE

DELAY_BETWEEN_BASEDEVO_REQUEST = 0.2
DELAY_BETWEEN_OPENSEA_REQUEST = 1


async def first_pages(session):
    while True:
        try:
            next = None
            cnt = 1
            while True:
                if cnt == PAGES_AMOUNT:
                    next = None
                    cnt = 1
                if next is not None:
                    cnt += 1
                    resp = await session.get(
                        f'https://api.opensea.io/api/v2/listings/collection/base-introduced/best?limit={str(LIST_ON_PAGE)}&next={urllib.parse.quote(next)}')
                    print(F'CURRENT PAGE: {cnt}')
                else:
                    resp = await session.get(
                        f'https://api.opensea.io/api/v2/listings/collection/base-introduced/best?limit={str(LIST_ON_PAGE)}')
                    print(f'CURRENT PAGE: {cnt}')
                r = await resp.json()
                next = r['next']
                for listing in r['listings']:
                    offer = listing['protocol_data']['parameters']['offer']
                    for item in offer:
                        identifier = item.get('identifierOrCriteria')
                        json = {
                            'tokenId': str(identifier)
                        }
                        resp = await session.post('https://basedevo.fun/api/checkToken', json=json)
                        r = await resp.json()
                        result = r['body']['tokenUsed']
                        if result is False:
                            print(
                                f"{identifier} can be used. Buy link: https://opensea.io/assets/ethereum/0xd4307e0acd12cf46fd6cf93bc264f5d5d1598792/{identifier}")
                        else:
                            print(f'{identifier} CANNOT be used')
                        await asyncio.sleep(DELAY_BETWEEN_BASEDEVO_REQUEST)
                await asyncio.sleep(DELAY_BETWEEN_OPENSEA_REQUEST)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)


async def new_listings(session):
    while True:
        try:
            while True:
                resp = await session.get(
                    f'https://api.opensea.io/api/v2/listings/collection/base-introduced/best?limit={str(NEW_LIST_AMOUNT)}')
                r = await resp.json()
                for listing in r['listings']:
                    offer = listing['protocol_data']['parameters']['offer']
                    for item in offer:
                        identifier = item.get('identifierOrCriteria')
                        json = {
                            'tokenId': str(identifier)
                        }
                        resp = await session.post('https://basedevo.fun/api/checkToken', json=json)
                        r = await resp.json()
                        result = r['body']['tokenUsed']
                        if result is False:
                            print(
                                f"{identifier} can be used. Buy link: https://opensea.io/assets/ethereum/0xd4307e0acd12cf46fd6cf93bc264f5d5d1598792/{identifier}")
                        else:
                            print(f'{identifier} CANNOT be used')
                        await asyncio.sleep(DELAY_BETWEEN_BASEDEVO_REQUEST)
                await asyncio.sleep(DELAY_BETWEEN_OPENSEA_REQUEST)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)


async def main():
    headers = {
        'Accept': 'application/json',
        'X-API-KEY': opensea_api_key
    }
    if USE_PROXY is True:
        connector = ProxyConnector.from_url(proxy)
        session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)
    else:
        session = aiohttp.ClientSession(headers=headers, trust_env=True)

    print("Base Introduced NFT tracker for basedevo.fun by artvine.\n")

    action = int(input("Select action:\n1. Start new listings check\n2. Start first pages check\n\n> "))

    if action == 1:
            await new_listings(session)
    if action == 2:
            await first_pages(session)


if __name__ == '__main__':
    asyncio.run(main())
