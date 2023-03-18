# 
import asyncio
from AdvancedTrade import AdvancedTrade


PUBLIC = 'XXX'
SECRET = 'XXX'
adv = AdvancedTrade(PUBLIC, SECRET)

# adv.products()
# print(adv.get_market_trades("BTC-USDT", limit=0)['trades'][-1])
# adv.list_accounts()
# adv.list_orders(2)
# adv.order()
# adv.buy("BTC-USDT","423123", 1)
# adv.get_order_id('d7504c34-b844-42bb-a8f0-c05261275199')

asyncio.run(adv.main())