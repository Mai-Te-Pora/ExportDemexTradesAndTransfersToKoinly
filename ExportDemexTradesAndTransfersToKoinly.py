#!/usr/bin/env python
# coding: utf-8

# ExportDemexTradesAndTransfersToKoinly
# Copyright © 2021 Eporediese for Switcheo / MaiTePora <3
# Licenced under GPL

# Creates CSV files in a format the the tax software Koinly understands, from Demex account trades and transfers for any Demex addresses
# The CSV files are written in the location that this script is executed
# This is not tax advice. The user accepts that the output of this tool should be reviewed for accuracy and completeness 

# LIBRARYS
# ------------------------------------------------------------------------------
# Tradehub Python API: https://mai-te-pora.github.io/tradehub-python/index.html
import tradehub
from tradehub.wallet import Wallet
from tradehub.transactions import Transactions
from tradehub.authenticated_client import AuthenticatedClient
from tradehub.types import CreateOrderMessage

# Date manipulation
import datetime;
import time;
from datetime import date

# Regular expressions
import re

# PARAMETERS
# ------------------------------------------------------------------------------
# Provide the mneumonic of any wallet (can be an empty wallet)
myMnemonic = 'these are twelve words that used together allow access to your wallet' #Tradehub mnemonic (example here: 12 word TradeHub mnemonic)

# Provide the Demex addresses that you want to pull trades and transfers for
demexAddresses = [
    'swth1primary', # Primary
    'swth1secondary' # Secondary
]

# CONSTANTS
# ------------------------------------------------------------------------------
demPK = Wallet(myMnemonic, network='mainnet')
clientDem = AuthenticatedClient(demPK, network='mainnet',trusted_ips=None, trusted_uris=['http://54.255.5.46:5001', 'http://175.41.151.35:5001'])

# MAIN
# ------------------------------------------------------------------------------
print(f'Connected To Tradehub --- {demPK.address}')

transDem = Transactions(demPK,
             trusted_ips=None,
             trusted_uris=['http://54.255.5.46:5001', 'http://175.41.151.35:5001'],
             network="mainnet")


# Iterate over Demex adresses

for address in demexAddresses:
    
    #print (address)
    
    # Get external transfers for Demex address
    transfers = transDem.get_external_transfers(address)
    #print (transfers)
    
    # Get trades (note: can set date range if needed)
    trades = transDem.get_address_trades('','',address) # Limited to 200 trades?
    #print (trades)

    # ct stores current time
    ct = datetime.datetime.now()
    #print("current time:-", ct)

    # Convert to a format that can be used in a filename
    fileDate = str(ct.month) + str(ct.day) + str(ct.year) + str(ct.hour) + str(ct.minute) + str(ct.second)
    #print (fileDate)

    # Open the output Koinly transfer history CSV file
    transferFilename = "koinly_transfer_history_for_" + address + "_at_" + str(fileDate) + ".csv"
    #print (transferFilename)
    transferFile = open(transferFilename, "w")
    
    # Open the output Koinly trade history CSV file
    tradeFilename = "koinly_trade_history_for_" + address + "_at_" + str(fileDate) + ".csv"
    #print (transferFilename)
    tradeFile = open(tradeFilename, "w")
    
    # Write out CSV files in Koinly file format
    # Trasfer tmplate is here: https://docs.google.com/spreadsheets/d/13H9kREcrNJmCNxkpYK-AaRlkWh8PSshbpPBmewmDX4o/edit#gid=0
    # Trade template is here: https://docs.google.com/spreadsheets/d/1MEVrdiS941S-s0igBZKh-pbW5TqJb4mpfkmnDzDkCcg/edit#gid=0
    # All date fields must be formatted like this: YYYY-MM-DD HH:mm:ss. 
    # For ex. if you want to enter 5th Jan 2019 the date will be 2019-01-05. 
    # All dates should be in UTC.
    
    transferHeader = "Koinly Date,Amount,Currency,Label,TxHash\n"
    #print (header)
    transferFile.write(transferHeader)
    
    tradeHeader = "Koinly Date,Pair,Side,Amount,Total,Fee Amount,Fee Currency,Order ID,Trade ID\n"
    tradeFile.write(tradeHeader)

# Iterate over transfers
# Koinly Date	Amount	Currency	Label	TxHash

for transfer in transfers:

    #print (transfer)

    # Extract timestamp
    transferEpoch = transfer['timestamp']
    #print (transferEpoch)

    # Convert Epoch timestamp format to YYYY-MM-DD HH:mm:ss format
    # In UTC
    koinlyTimestamp = datetime.datetime.utcfromtimestamp(transferEpoch).strftime('%Y-%m-%d %H:%M:%S')

    # Extract amount
    transferAmount = transfer['amount']

    # Extract currency
    transferSymbol = transfer['symbol']

    # Convert Demex to Koinly symbols
    if (transferSymbol == "SWTHN"):
        koinlySymbol = "SWTH"
    else:
        koinlySymbol = transferSymbol

    # Extract Transaction type
    transferType = transfer['transfer_type']

    # Extract Transaction hash to use as label
    transferHash = transfer['transaction_hash']      

    # Extract Transaction status
    transferStatus = transfer['status']  

    if (transferStatus == 'success'):
        transferFile.write(koinlyTimestamp + "," + transferAmount + "," + koinlySymbol.upper() + "," + transferType + "," + transferHash + "\n")

# Iterate over trades
# Koinly Date	Pair	Side	Amount	Total	Fee Amount	Fee Currency	Order ID	Trade ID

for trade in trades:

    #print (trade)

    # Extract timestamp
    tradeEpoch = trade['block_created_at']
    #print (tradeEpoch)

    # Convert block timestamp format to YYYY-MM-DD HH:mm:ss format

    s = re.findall('(.+)T(.+)\.', tradeEpoch)
    #print (s)
    #print (s[0][0])
    #print (s[0][1])
    koinlyTimestamp = s[0][0] + " " + s[0][1]
    #print (koinlyTimestamp)

    # Extract amount
    tradeAmount = trade['quantity']    
    
    # Construct Buy|Sell side
    if (trade['side'] == 'sell'):
        tradeSide = 'Sell'
    else:
        tradeSide = 'Buy'
        
    # Extract trade pair
    tradePairExtracted = trade['market']
    #print (tradePairExtracted)
    # Convert to Koinly format and known coins
    s = re.findall('(.+[^\d])[\d]*_(.+[^\d])[\d]*', tradePairExtracted)
    fromCurrencyExtracted = s[0][0].upper()
    toCurrencyExtracted = s[0][1].upper()
    tradePair = s[0][0].upper() + "-" + s[0][1].upper()
    #print (tradePair)
    
    # Extract trade price and use to calculate the total
    tradePrice = trade['price']
    #print (tradePrice)
    #print (tradeAmount)
    tradeTotal = float(tradePrice) * float(tradeAmount)
    #print (str(tradeTotal))
    
    # Extract fee amount
    tradeFeeAmount = str(trade['fee_amount'])
    
    # Extract fee total
    tradeFeeCurrencyExtracted = trade['fee_denom']
    #print (tradeFeeCurrencyExtracted)
    # Convert to Koinly format and known coins
    s = re.findall('(.+[^\d])[\d]*', tradeFeeCurrencyExtracted)
    tradeFeeCurrency = s[0].upper()
    #print (tradeFeeCurrency)
    
    # Extract order ID
    tradeOrderID = str(trade['order_id'])
    
    # Extract trade ID
    tradeTradeID = str(trade['id'])

    tradeFile.write(koinlyTimestamp + "," + tradePair + "," + tradeSide + "," + str(tradeAmount) + "," + str(tradeTotal) + "," + tradeFeeAmount + "," + tradeFeeCurrency + "," + tradeOrderID + "," + tradeTradeID + "\n")


transferFile.close()
tradeFile.close()





