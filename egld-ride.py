import requests
import json
import os
from time import sleep
from dotenv import load_dotenv
from utils.log import Log
from twilio.rest import Client
load_dotenv(os.path.join(os.getcwd(), 'config.ini'))
log = Log.setup_custom_logger()

RECHECK_EVERY = int(os.environ['RECHECK_EVERY'])
RIDE_PER_EGLD = int(os.environ['RIDE_PER_EGLD'])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://maiar.exchange/",
    # "Authorization": f"Bearer {AUTHORIZATION}",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Te": "trailers"
}
BODY = {"variables": {"mexID": "MEX-455c57", "wegldID": "WEGLD-bd4d79", "days": 7, "offset": 0, "pairsLimit": 3,
                      "egldMexPairAddress": "erd1qqqqqqqqqqqqqpgqa0fsfshnff4n76jhcye6k7uvd7qacsq42jpsp6shh2"},
        "query": "query ($days: Int!, $mexID: String!, $wegldID: String!, $offset: Int, $pairsLimit: Int, $egldMexPairAddress: String!) {\n  totalAggregatedRewards(days: $days)\n  wegldPriceUSD: getTokenPriceUSD(tokenID: $wegldID)\n  mexPriceUSD: getTokenPriceUSD(tokenID: $mexID)\n  mexSupply: totalTokenSupply(tokenID: $mexID)\n  mexBurned: burnedTokenAmount(pairAddress: $egldMexPairAddress, tokenID: $mexID)\n  totalLockedValueUSDFarms\n  totalValueLockedUSD\n  farms {\n    address\n    farmingToken {\n      name\n      identifier\n      decimals\n      __typename\n    }\n    farmedToken {\n      name\n      identifier\n      decimals\n      __typename\n    }\n    farmTokenSupply\n    farmTokenPriceUSD\n    farmedTokenPriceUSD\n    farmingTokenReserve\n    farmingTokenPriceUSD\n    perBlockRewards\n    penaltyPercent\n    totalValueLockedUSD\n    apr\n    requireWhitelist\n    aprMultiplier\n    unlockedRewardsAPR\n    lockedRewardsAPR\n    version\n    rewardType\n    __typename\n  }\n  pairs(offset: $offset, limit: $pairsLimit) {\n    address\n    firstToken {\n      name\n      identifier\n      decimals\n      __typename\n    }\n    secondToken {\n      name\n      identifier\n      decimals\n      __typename\n    }\n    firstTokenPrice\n    firstTokenPriceUSD\n    secondTokenPrice\n    secondTokenPriceUSD\n    liquidityPoolTokenPriceUSD\n    info {\n      reserves0\n      reserves1\n      totalSupply\n      __typename\n    }\n    state\n    lockedValueUSD\n    feesAPR\n    __typename\n  }\n  factory {\n    totalVolumeUSD24h\n    maintenance\n    __typename\n  }\n}\n"}


def run(check):
    r = requests.post('https://graph.maiar.exchange/graphql', headers=HEADERS, json=BODY)
    js = json.loads(r.text)
    ride_pair = None
    for pair in js['data']['pairs']:
        try:
            if pair['firstToken']['name'] == 'WrappedEGLD' and pair['secondToken']['name'] == 'holoride':
                ride_pair = int(pair['firstTokenPrice'].split('.')[0])
                break
        except:
            pass

    if not ride_pair:
        raise Exception('could not find EGLD-RIDE pair')

    log.info(f'[+] RIDE per EGLD: {ride_pair}')
    if ride_pair >= RIDE_PER_EGLD:
        log.info('Ratio is good, sending SMS')
        send_sms(f'[elrond] RIDE per EGLD is {ride_pair}')
        return True


# Send SMS message
def send_sms(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    phone_number = os.environ['TWILIO_PHONE_NUMBER']
    to = os.environ['SMS_RECEIVER']

    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=message,
        from_=phone_number,
        to=to
    )

    log.info(f'Message sent: {message.sid}')


# main method
def main():
    try:
        check = 1
        while True:
            if run(check):
                break
            sleep(RECHECK_EVERY)
            check += 1
    except Exception as ex:
        log.error(ex)
    # recursive
    main()


if __name__ == "__main__":
    main()
