# ExportDemexTradesAndTransfersToKoinly
Simple Python Script, using tradehub-python that creates CSV files in a format the the tax software Koinly understands, from Demex account trades and transfers for any Demex addresses

Python 3.8+ required.<br>

Instructions<br>
1)Install Tradehub-python library "pip install tradehub" (https://github.com/Mai-Te-Pora/tradehub-python)<br>
2)Open ExportDemexTradesAndTransfersToKoinly.py<br>
3)Change # PARAMETERS settings<br>
4)Run the script in a location where you have write permission<br>
5)Verify that the content of the trade and transaction files is correct with Notepad<br>


# PARAMETERS<br>
myMnemonic = 'these are twelve words that used together allow access to your wallet' #Tradehub mnemonic of any wallet (can be empty)<br>

demexAddresses = [
    'swth1primary', # Primary
    'swth1secondary' # Secondary
]

