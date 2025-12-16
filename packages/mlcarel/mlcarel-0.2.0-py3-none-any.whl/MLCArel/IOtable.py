import numpy as np
import csv
class IOtreat:
    '''
    産業連関表解析用管理ツール
    '''
    def to_number_if_numeric_string(self,ch):      
        """
        高機能版の変換:
        - keep_leading_zeros: '0012' のような先頭ゼロ付き整数を数値にしない（文字列のまま）
        - allow_commas: '1,234.56' のようなカンマ区切りを受け入れてカンマを除去
        - allow_nan_inf: 'NaN', 'inf', '-inf' を float として許容するかどうか
        """

        if not isinstance(ch, str):
            return ch
        s = ch.strip()
        if s == '':
            return ch
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        return ch

    def ReadFromPath(self,path='./',data='data.csv',IOdata='IOdata.csv'):
        with open(path+data, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f,delimiter=',', quotechar="'")
            d_imp={}
            for row in reader:
                converted_list = [self.to_number_if_numeric_string(ch) for ch in row[1:]]
                d_imp[row[0]]=converted_list
        with open(path+IOdata, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f,delimiter=',', quotechar="'")
            dd=[]
            i=0
            for row in reader:
                if i==0:
                    i+=1
                    continue
                d=[self.to_number_if_numeric_string(ch) for ch in row]
                dd.append(d)
        d_imp['産業連関表']=dd 
        return d_imp
    def ReadFromDf(self,df):    
        IOtable=np.array(df['産業連関表'])
        addedValue=np.array(df['付加価値'])
        productionV=np.sum(IOtable, axis=0)+addedValue
        A=self.MakeA(IOtable,productionV)
        adf=self.MakeADF(addedValue,productionV)
        finalD=np.array(df['最終需要'])
        exportV=np.array(df['輸出'])
        importV=np.array(df['輸入'])
        impf=self.MakeImpF(IOtable,finalD,exportV,importV)
        M=self.MakeM(impf)        
        self.finalM=self.MakeFinalM(M,A)#I-(I-M)Aのマトリックスの計算
        self.A=A #投入係数マトリックス
        self.M=M #輸入係数マリリックス
    def SimpleAnalysis(self,F):
        self.F=F
        unitM=np.eye(self.n)
        invMat=np.linalg.inv(self.finalM)
        self.solution=invMat@(unitM-self.M)@F
        self.loadValue=self.adf@self.solution
        return self.solution,self.loadValue
    def GetA(self):
        '''
        投入係数マトリックスの取得
        '''
        return self.A
    def GetM(self):
        '''
        輸入係数マトリックスの取得
        '''
        return self.M        
    def GetBoundary(self,path='./',boundary='boundary.csv'):
        with open(path+boundary, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f,delimiter=',',quotechar="'")
            dd=[]
            i=0
            for row in reader:
                if i==0:
                    i+=1
                    continue
                d=[self.to_number_if_numeric_string(ch) for ch in row]
                dd.append(d)
        return dd         
    def GetFinalM(self):
        return self.finalM
    def MakeA(self,IOtable,productionV):
        '''
        投入係数の計算
        '''
        A=IOtable/productionV
        return A
    def MakeADF(self,addedValue,productionV):
        '''
        付加価値係数の計算
        '''
        adf=addedValue/productionV
        self.adf=adf
        return adf
    def GetADF(self):
        return self.adf
    def MakeImpF(self,IOtable,finalD,exportV,importV):
        '''
        輸入係数の計算
        '''
        row_sums = np.sum(IOtable, axis=1)
        impf=-importV/(row_sums+finalD+exportV)
        return impf
    def MakeM(self,impf):
        return np.diag(impf)
    def MakeFinalM(self,M,A):
        '''
        I-(I-M)Aのマトリックスの計算
        '''
        unitM=np.eye(len(M[0]))
        finM=unitM-(unitM-M)@A
        return finM
    def MakeProcess(self,df,finalM,adf,unit='yen',ratio=0.1):
        industry=df['産業名']
        industryName=df['産業名称']
        envimp=df['付加価値係数名']
        data={}
        n=len(industry)
        self.n=n
        for i in range(n):
            dd=[]
            for j in range(n):
                if i==j:
                    ch='F'
                else:
                    ch='I'
                ll=[ch,industry[j],unit,float(finalM[j][i]),float(finalM[j][i])*ratio]
                dd.append(ll)
            # 付加価値係数名は一個しか存在しないのでenvimp[0]のみ
            ll=['L',envimp[0],unit,float(adf[i]),float(adf[i])*ratio]
            dd.append(ll)
            data[industryName[i]]=dd
        res={}
        res['PROCESS']=data
        return res
    def Set(self,solution,loadValue,Aload):
        self.solution=solution
        self.loadValue=loadValue
        self.Aload=Aload
    def Aij(self,i,j):
        n=self.n
        zero_matrix = np.zeros((n, n))
        zero_matrix[i,j]=1
        return zero_matrix
    def sijA(self,i,j,i_beta,invMat,A,M):
        '''
        産業連関法、投入係数Aの付加価値合計に対する感度
        '''
        unitM=np.eye(len(M[0]))
        X=invMat@(unitM-M)
        beta=self.loadValue[i_beta]
        B=self.Aload[i_beta]
        aa=np.dot(self.Aij(i,j),self.solution)
        aa=np.dot(X,aa)
        aa=np.dot(B.T,aa)
        res=A[i,j]/beta*aa
        return res
    def sijM(self,i,j,i_beta,invMat,A,M):
        '''
        産業連関法、輸入係数Mの付加価値合計に対する感度
        '''
        if i!=j:
            return 0.0
        beta=self.loadValue[i_beta]
        B=self.Aload[i_beta]
        aa=np.dot(A,self.solution)
        aa=self.Aij(i,j)@aa
        aa=-invMat@aa
        aa=np.dot(B.T,aa)
        res=M[i,j]/beta*aa
        return res
    def SmatAold(self,i_beta,invMat,A,M):
        """
        合理化前のバージョン
        投入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        n=self.n
        smat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                smat[i,j]=self.sijA(i,j,i_beta,invMat,A,M)
        return smat
    def SmatA(self,i_beta,invMat,A,M):
        """
        合理化後のバージョン
        投入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        unitM=np.eye(len(M[0]))
        XA=invMat@(unitM-M)
        n=self.n
        xmat = np.zeros((n,n))
        Adin=self.loadValue[i_beta]
        B=self.Aload[i_beta]
        for i in range(n):
            x=XA[:,i]
            xx=np.dot(B.T,x)
            for j in range(n):
                xmat[i,j]=self.solution[j]*xx/Adin
        smat=A*xmat
        return smat
    def SmatA_IO(self):
        """
        合理化後のバージョン
        投入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        unitM=np.eye(self.n)
        IM=unitM-self.M
        xx=unitM-IM@self.A
        invMat=np.linalg.inv(xx)
        P1=invMat@IM
        n=self.n
        xmat = np.zeros((n,n))
        Adin=self.loadValue
        B=self.adf
        for i in range(n):
            for j in range(n):
                PI=P1@self.Aij(i,j)@self.solution
                xmat[i,j]=1.0/Adin*np.dot(B.T,PI)
        smat=self.A*xmat
        return smat
    def SmatM_IO(self):
        """
        合理化後のバージョン
        輸入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        unitM=np.eye(self.n)
        IM=unitM-self.M
        xx=unitM-IM@self.A
        invMat=np.linalg.inv(xx)
        P1=self.A@self.solution+self.F
        n=self.n
        xmat = np.zeros((n,n))
        Adin=self.loadValue
        B=self.adf
        for i in range(n):
            for j in range(n):
                PI=-self.Aij(i,j)@P1
                xmat[i,j]=B.T@invMat@PI/Adin
        smat=self.M*xmat
        return smat  
    def SmatM(self,i_beta,invMat,A,M):
        """
        合理化後のバージョン
        輸入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        beta=self.loadValue[i_beta]
        B=self.Aload[i_beta]
        xx=np.dot(A,self.solution)
        n=self.n
        xmat = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i!=j:
                    xmat[i,j]=0.0
                    continue
                aa=self.Aij(i,j)@xx
                aa=-invMat@aa
                aa=np.dot(B.T,aa)
                xmat[i,j]=1./beta*aa
        smat=M*xmat
        return smat                
    def SmatMold(self,i_beta,invMat,A,M):
        """
        合理化前のバージョン
        輸入係数Mの付加価値合計に対する感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        n=self.n
        smatM=np.zeros((n, n))
        for i in range(n):
            smatM[i,i]=self.sijM(i,i,i_beta,invMat,A,M)
        return smatM
    def Add(self,df,process,boundary,unit='yen'):
        industry=df['産業名']
        proc=process.copy()
        dd=[]
        n=len(industry)
        for i in range(n):
            d=['B',industry[i],unit,boundary[i]]
            dd.append(d)
        proc['BOUNDARY']=dd
        return proc