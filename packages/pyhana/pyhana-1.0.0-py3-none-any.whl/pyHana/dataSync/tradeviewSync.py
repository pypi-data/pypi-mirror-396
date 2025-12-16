from ..outerIO  import tradeview
from ..common   import conf, dataProc, code

def SyncStockInfoUSA():

    filePathNm = conf.companyInfoPath + "/주식종목정보(미국).pkl"

    dfData = tradeview.GetStockInfoUSA()
    
    data = {}
    data['columns'] = dfData.columns.values.tolist()
    data['data'] = dfData.values.tolist()

    dataProc.WritePickleFile(filePathNm, data) 