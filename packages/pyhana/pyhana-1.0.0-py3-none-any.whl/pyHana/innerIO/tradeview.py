import pandas as pd
from   ..common import conf, dataProc

def StockInfoUSA(shCode='', shName=''):   
    filePathNm = conf.companyInfoPath + "/주식종목정보(미국).pkl"
    currData = dataProc.ReadPickleFile(filePathNm)
    df = pd.DataFrame(currData.get('data', []), columns=currData['columns'])
    
    if len(shCode) > 0:       
        if type(shCode) == type(pd.DataFrame([])):
            dfX = shCode[['종목코드']] 
        else:
            if type(shCode) == str:
                dfX = [shCode]
            elif type(shCode) == list:
                dfX = shCode 
            dfX = pd.DataFrame(dfX, columns=['종목코드'])  
        df = pd.merge(dfX, df)         
    if len(shName) > 0:
        df = df.query("종목명.str.contains(@shName)")
    return  df