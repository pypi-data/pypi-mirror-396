import pandas as pd
from collections import Counter
import numpy as np
from typing import Tuple
class MLCA:
    # selfの内容
    # self.loadValue 環境負荷の積算リスト
    # self.load_list 環境負荷項目の文字列リスト
    # self.Aload 環境負荷係数マトリックス
    # self.IFk 環境負荷項目ごとの統合化積算量からなるリスト
    # self.IFtotal 統合化積算による単一指標SIのこと
    # self.S_beta_IFtotal 式(8)の感度のリスト
    # self.sensitivity_L 環境負荷係数の環境負荷総和に対する感度値のリスト
    # self.solution プロセス値の解
    # self.process プロセス名のリスト
    # self.Smat_beta_bi 環境負荷総和に対する各プロセスの環境負荷係数の感度値マトリックス
    # self.Smat_IFtotal_bi SIに対する各プロセスの環境負荷係数の感度マトリックス
    #def __init__(self):
        #self.impact=Impact()
    def input_data(self,data:dict,read=False):
        '''
        入力データの取り込み
        read: Trueのときには，LIME2データをファイルから読む
        そうでないときには，そのままself.dfに読み込む
        '''
        if read:
            #LIME2データを読み取り，dfに追加する
            IFlist=self.impact.get_IFlist(data)
            load=list(IFlist.keys())
            for ldata in load:
                data['LIME2'][ldata].append(IFlist[ldata])
        self.df=data
        self.n_process=len(data['PROCESS'])

    def extract_base(self):
        '''
        self.dfに設定されているデータに基づいて各種マトリックスを構成する
        '''
        process=list(self.df['PROCESS'].keys())
        self.process=process
        mat=[]
        load=[]
        for proc in process:
            pr_data=self.df['PROCESS'][proc]
            for data in pr_data:
                if data[0]=='I' or data[0]=='O' or data[0]=='F':
                    mat.append(data[1])
                if data[0]=='L':
                    load.append(data[1])
            boundary=self.df['BOUNDARY']
            for bd in boundary:
                mat.append(bd[1])
        count=Counter(mat)
        surplus=[item for item in mat if count[item] == 1]
        filtered_list = [item for item in mat if item not in surplus]
        material=list(set(filtered_list))
        material=[]
        for proc in process:
            pr_data=self.df['PROCESS'][proc]
            for data in pr_data:
                if data[0]=='F':
                    material.append(data[1])            
        self.material=material
        load_list=list(set(load))
        self.load_list=load_list
        return material,surplus,load_list
    def MakeMatrix(self):
        material,surplus,load_list=self.extract_base()
        process=list(self.df['PROCESS'].keys())
        self.coefficientMat=self.matrix(process,material)
        self.surplusMat=self.matrix(process,surplus)
        self.loadMat=self.matrix(process,load_list)
        self.sdMat,self.sdL=self.SDmatrix(process,material)
    def matrix(self,proc:list,mat:list)->pd.DataFrame:
        data={'mat':mat}
        for process in proc:
            dd=[0]*len(mat)
            ll=self.df['PROCESS'][process]
            for basic_data in ll:
                if basic_data[1] in mat:
                    position=mat.index(basic_data[1])
                    dd[position]=basic_data[3]
            data[process]=dd
        return pd.DataFrame(data)
    def SDmatrix(self,proc:list,mat:list)->Tuple[pd.DataFrame, pd.DataFrame]:
        data={'mat':mat}
        sdL={'Load':self.load_list}
        for process in proc:
            dd=[0]*len(mat)
            ld=[0]*len(self.load_list)
            ll=self.df['PROCESS'][process]#llは一つのインベントリ
            for basic_data in ll:#basic_dataはインベントリ内の一行
                if basic_data[1] in mat:
                    if len(basic_data)==5: #sの記述在り
                        position=mat.index(basic_data[1])
                        dd[position]=basic_data[4]#標準偏差
                if basic_data[0]=='L':
                    position=self.load_list.index(basic_data[1])
                    if len(basic_data)==5:#sの記述在り
                        ld[position]=basic_data[4]#標準偏差                 
            data[process]=dd
            #print(process,ld)
            sdL[process]=ld
        return pd.DataFrame(data),pd.DataFrame(sdL)
    def Solve(self)->tuple[np.ndarray, np.ndarray, np.ndarray]:
        boundary=self.df['BOUNDARY']
        bb=[0]*len(self.material)
        for bound in boundary:
            ii=self.material.index(bound[1])
            bb[ii]=bound[3]
        b=np.array(bb)
        process=list(self.df['PROCESS'].keys())
        A=self.coefficientMat[process].values
        self.A=A
        self.A_inv = np.linalg.inv(A)
        # 解を求める
        solution = np.linalg.solve(A, b)
        self.solution=solution
        Asurplus=self.surplusMat[process].values
        surplusFlow=np.dot(Asurplus,solution)
        Aload=self.loadMat[process].values
        self.Aload=Aload
        loadValue=np.dot(Aload,solution)
        self.loadValue=list(loadValue)#環境負荷
        self.sensitivity_L=self.SentisivityLoad()
        return solution,surplusFlow,loadValue
    def S_bi_beta(self):
        # k番目の感度負荷総和に対する第i番目プロセスのb_k_iの感度値マトリックスの評価
        # 上の段の式(4)の評価
        nP=len(self.process)
        nL=len(self.load_list)
        smat = np.zeros((nL, nP))
        for iL in range(nL):
            for iP in range(nP):
                P=self.solution[iP]
                b=self.Aload[iL,iP]
                beta=self.loadValue[iL]
                smat[iL,iP]=P*b/beta
        self.Smat_beta_bi=smat
    def SentisivityLoad(self)->list:
        #環境負荷係数に対する感度値の計算
        sensitivity_L=[]
        for al,load in zip(self.Aload,self.loadValue):
            # 各要素の積を計算
            product_list = [a * b for a, b in zip(self.solution, al)]
            sensitivity_L.append(product_list/load)
        self.sensitivity_L=sensitivity_L
        return sensitivity_L           
    def Aij(self,i,j):
        n=len(self.process)
        zero_matrix = np.zeros((n, n))
        zero_matrix[i,j]=1
        return zero_matrix
    def sij(self,i,j,i_beta):
        beta=self.loadValue[i_beta]
        B=self.Aload[i_beta]
        aa=np.dot(self.Aij(i,j),self.solution)
        aa=np.dot(self.A_inv,aa)
        aa=np.dot(B.T,aa)
        res=-self.A[i,j]/beta*aa
        return res
    def SmatIF(self):
        #この関数を呼ぶ前にIFk,IFtotalが計算されているという前提
        IF=self.IF
        IFtotal=self.IFtotal
        beta=self.loadValue
        n=len(self.process)
        smatIF = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                smat_ij_beta=[]
                for i_beta in range(len(beta)):
                    aa=self.sij(i,j,i_beta)
                    smat_ij_beta.append(aa)
                smatIF[i,j]=self.impact.S_ij_IFtotal(beta,smat_ij_beta,IF,IFtotal)
        self.smatIF=smatIF
        return smatIF
    def setIF(self,IFlist):
        # IFは表から引いてくる統合化係数
        # 統合化係数値と環境負荷積算地の積，つまり統合化係数積算値のリストを作る。
        # その結果から統合化量の積算値，つまり単一指標の計算を行う
        # IFtotalはSI値のことである
        # この関数を呼ぶ前に，感度分析評価が終わっていることを前提とする
        # self.S_beta_IFtotal 式(8)の感度のリスト
        # self.sensitivity_L 環境負荷係数の環境負荷総和に対する感度値のリスト
        # self.process プロセス名のリスト
        # self.Smat_bi_beta 環境負荷総和に対する各プロセスの環境負荷係数の感度値マトリックス
        IF=[]
        sdIF=[]
        load_list=self.load_list
        for load in load_list:
            IF.append(IFlist[load][0])
            sdIF.append(IFlist[load][1])
        self.IF=IF
        self.IFk=[a*b for a,b in zip(self.loadValue,IF)]
        self.sdIF=sdIF
        self.IFtotal=sum(self.IFk)
        self.S_beta_IFtotal=self.S_ifk_IFtotal=self.IFk/self.IFtotal        
        self.S_bi_beta()
        nP=len(self.process)
        nL=len(self.loadValue)
        smat = np.zeros((nL, nP))
        for iP in range(nP):
            for iL in range(nL):
                smat[iL,iP]=self.IF[iL]*self.solution[iP]*self.Aload[iL,iP]/self.IFtotal
        self.Smat_IFtotal_bi=smat #式(15)の評価
    def Smat(self,i_beta):
        """
        感度マトリックスの計算
            i_beta: 環境負荷のindex
        """
        n=len(self.process)
        smat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                smat[i,j]=self.sij(i,j,i_beta)
        return smat
    def find_nth_largest(self,matrix, n):
        """
        マトリックスの n 番目に大きい値の行と列を返す
        Args:
            matrix (numpy.ndarray): 対象のマトリックス
            n (int): 取得したい順位 (1が最大)
               n<0のとき，最小値から|n|番目の行と列
        Returns:
            tuple: (行, 列)
        """
        if n<0:
            n=matrix.size+n+1
        if not (1 <= n <= matrix.size):
            raise ValueError("nは1以上、要素数以下である必要があります")
        
        # マトリックスをフラット化
        flattened = matrix.flatten()
        
        # 値を降順でソートしてインデックスを取得
        sorted_indices = np.argsort(flattened)[::-1]
        # n番目に大きい要素の元のフラット化インデックス
        nth_largest_index = sorted_indices[n - 1]
        
        # 元のマトリックスでの行と列のインデックス
        row, col = divmod(nth_largest_index, matrix.shape[1])
        
        return row, col
    def find_nth(self,matrix,n,i_beta):
        """
        感度値の大きな要素を抽出するにあたり，係数部分の感度と，環境負荷係数の感度の両者を考慮に入れたうえでの評価を行う
        対象を環境負荷に特化した取り扱い。より汎用的にしてものはfind_nth2
        """
        #フロー名に環境負荷名を追加する
        mat=self.material.copy()
        mat.append(self.load_list[i_beta])
        # マトリックスに行を追加
        new_row=np.array(self.sensitivity_L[i_beta])
        matrix = np.vstack([matrix, new_row])
        row,col=self.find_nth_largest(matrix,n)
        return [self.process[col],mat[row],matrix[row,col]]
    def find_nthSI(self,matrix,load:list,ifv:list,n):
        """
        感度値の大きな要素を抽出するにあたり，係数部分の感度と，環境負荷係数の感度の両者を考慮に入れたうえでの評価を行う
        matrixにはSIに対する感度マトリックス，
        loadには，SIの出力量に対する環境負荷感度マトリックス
        """
        #統合化係数をプロセス扱いし一列追加，プロセス名はIF
        proc=self.process.copy()
        proc.append('IF')
        # ゼロ要素の列を作成
        zero_column = np.zeros((matrix.shape[0], 1))  # 配列の行数に一致させる
        new_matrix=np.hstack((matrix,zero_column))
        #フロー名に環境負荷名を追加する
        mat=self.material.copy()
        for llist in self.load_list:
            mat.append(llist)
            iflist='IF_'+llist
            mat.append(iflist)
        # マトリックスに行を追加
        for i_beta in range(len(self.load_list)):
            #環境負荷係数分の追加
            ld=load[i_beta]
            ld=np.append(ld,0.0)
            new_row=np.array(ld)
            new_matrix = np.vstack([new_matrix, new_row])
            #統合化係数分の追加
            ld=[0]*len(self.process)
            ld.append(ifv[i_beta])
            new_row=np.array(ld)
            new_matrix = np.vstack([new_matrix, new_row])
        row,col=self.find_nth_largest(new_matrix,n)
        return [proc[col],mat[row],new_matrix[row,col]]
    def PickMax(self,matrix,n:int,i_beta:int)->list:
        """
        目的:i_beta番目の環境負荷についてmatrixの中の上位n個の[プロセス名，フロー名，感度値]データをリスト形式で返す
        対象を環境負荷に特化した取り扱い。より汎用化したものはPickMax2
        """
        max_list=[]
        for i in range(n):
            ii=i+1
            max_list.append(self.find_nth(matrix,ii,i_beta))
        return max_list
    def PickMaxSI(self,matrix,load:list,ifv:list,n:int)->list:
        """
        目的:SIについてmatrix,loadの中の上位n個の[プロセス名，フロー名，感度値]データをリスト形式で返す
        """
        max_list=[]
        for i in range(n):
            ii=i+1
            max_list.append(self.find_nthSI(matrix,load,ifv,ii))
        return max_list
    def PickMin(self,matrix,n:int,i_beta:int)->list:
        """
        目的:matrixの中の下位n個の[プロセス名，フロー名，感度値]データをリスト形式で返す
        対象を環境負荷に特化した取り扱い。より汎用化したものはPickMin2
        """
        nmat=matrix.size
        min_list=[]
        for i in range(n):
            ii=-i-1
            min_list.append(self.find_nth(matrix,ii,i_beta))
        return min_list
    def PickMinSI(self,matrix,load:list,ifv:list,n:int)->list:
        """
        目的:SIについてmatrixの中の下位n個の[プロセス名，フロー名，感度値]データをリスト形式で返す
        """
        nmat=matrix.size
        min_list=[]
        for i in range(n):
            ii=-i-1
            min_list.append(self.find_nthSI(matrix,load,ifv,ii))
        return min_list
    def Uncertainty(self)->list:
        n=len(self.material)
        n_beta=len(self.load_list)
        sd=self.sdMat
        sd=sd[self.process].values
        res_beta=[]
        resA=[]
        resB=[]
        for i_beta in range(n_beta):
            sL=self.sensitivity_L[i_beta]
            b=self.Aload[i_beta]
            sigm=self.sdL[self.process].values[i_beta]
            s=self.Smat(i_beta)
            A=self.A
            beta=self.loadValue[i_beta]
            sum=0
            for i in range(n):
                for j in range(n):
                    if A[i,j]!=0:
                        aa=beta/A[i,j]*s[i,j]*sd[i,j]
                        sum += aa*aa
            #環境負荷係数部分の寄与分加算
            sumL=0
            for i in range(n):
                if b[i]!=0:
                    aa=beta/b[i]*sL[i]*sigm[i]
                    sumL += aa*aa
            sumTotal = sum+sumL
            res_beta.append(np.sqrt(sumTotal))
            resA.append(np.sqrt(sum))
            resB.append(np.sqrt(sumL))
            df={
                'SdA':resA,#係数マトリックス分の不確定性
                'SdB':resB,#環境負荷係数分の不確定性
                'Sd':res_beta
            }   
        self.sdBeta=df['Sd']
        return df
    def SigmSI(self):
        """
        統合化係数の標準偏差の評価
        """
        var=0
        len_k=len(self.load_list)

        var=0
        for k in range(len_k):
            IF=self.IF[k]
            sBeta=self.sdBeta[k]
            beta=self.loadValue[k]
            sIF=self.sdIF[k]
            var += IF*IF*sBeta*sBeta+beta*beta*sIF*sIF
        self.sdSI=np.sqrt(var)
        return np.sqrt(var)

    def SIcalc(self,IFlist):
        """
        プロセスごとの統合化係数と
        統合化単一指標SIの計算
        IFlistから評価する方法
        self.setIFによっても計算できる
        当面，setIFの方が正しそう
        """
        proc=self.df['PROCESS'].keys()
        SIk={}
        SI=0.0
        for process in proc:
            dd=self.df['PROCESS'][process]#プロセスデータ
            val=0.0
            ii=self.process.index(process)
            for data in dd:
                if data[0]=='L':
                    load=data[1]
                    val += IFlist[load][0]*data[3]*self.solution[ii]
            SIk[process]=val
            SI += val
        SIk['SI']=SI
        return SIk
    def S_IF_bi(self):
        '''
        biのIFtotalに対する感度マトリックスの評価
        '''
        nload=len(self.load_list)
        nprocess=len(self.process)
        smat=np.zeros((nload,nprocess))
        IFtotal=self.IFtotal
        for k in range(nload):
            for p in range(nprocess):
                smat[k][p]=self.IF[k]*self.solution[p]*self.Aload[k,p]/IFtotal
        return smat
    def EvalRank(self,Rank:int):
        '''
        環境項目ごとに感度値の上位，下位Rank番目までを評価してpd.DataFrameを作る
        そのリストの形でbest,worstをもどす
        '''
        nload=len(self.load_list)
        best=[]
        worst=[]
        for i_beta in range(nload):
            s=self.Smat(i_beta)
            b5=self.PickMax(s,Rank,i_beta)
            w5=self.PickMin(s,Rank,i_beta)
            process=[x[0] for x in b5]
            flow=[x[1] for x in b5]
            value=[x[2] for x in b5]
            best5=pd.DataFrame()
            best5['process']=process
            best5['flow']=flow
            best5['value']=value
            #print('best 5\n',best5)
            ##
            process=[x[0] for x in w5]
            flow=[x[1] for x in w5]
            value=[x[2] for x in w5]
            worst5=pd.DataFrame()
            worst5['process']=process
            worst5['flow']=flow
            worst5['value']=value
            #print('worst 5\n',worst5)
            best.append(best5)
            worst.append(worst5)
        return best,worst
    def EvalRankSI(self,Rank:int):
        '''
        SIに対する感度値の上位，下位Rank番目までを評価してpd.DataFrameを作る
        そのリストの形でbest,worstをもどす。
        '''
        nload=len(self.load_list)
        best=[]
        worst=[]
        load=self.Smat_IFtotal_bi
        ifv=self.S_ifk_IFtotal
        # 環境負荷に対する評価
        for i_beta in range(nload):
            s=self.SmatIF()
            b5=self.PickMaxSI(s,load,ifv,Rank)
            w5=self.PickMinSI(s,load,ifv,Rank)
            process=[x[0] for x in b5]
            flow=[x[1] for x in b5]
            value=[x[2] for x in b5]
            best5=pd.DataFrame()
            best5['process']=process
            best5['flow']=flow
            best5['value']=value
            #print('best 5\n',best5)
            ##
            process=[x[0] for x in w5]
            flow=[x[1] for x in w5]
            value=[x[2] for x in w5]
            worst5=pd.DataFrame()
            worst5['process']=process
            worst5['flow']=flow
            worst5['value']=value
            #print('worst 5\n',worst5)
            best.append(best5)
            worst.append(worst5)
        
        return best,worst
    def SingleIndex(self):
        '''
        Evaluation of Single index
        '''
        IFlist=self.impact.get_IFlist(self.df)
        self.setIF(IFlist)
        return self.IFtotal
    def PrintResult(self):
        print('+++ TITLE=',self.df['TITLE'],' +++\n\n')
        print('[[Sensitivity for coefficients]]\n')
        best,worst=self.EvalRank(10)
        for i_beta in range(len(self.load_list)):
            print('   **** Environmental load=',self.load_list[i_beta],' ****')
            print('    --- best--- \n',best[i_beta])
            print('    --- worst ---\n',worst[i_beta])
        print('\n[[Evaluation of Single Index]]\n') 
        print('SI=',self.SingleIndex())
    def __del__(self):
        if 'self.obj' in locals():
            del self.impact      
    
    
import os
import csv
class IO:
    #GitHubバージョンでは，LIME関係の機能は削除する
        def __init__(self):
            self.limeFlag=False
            if self.limeFlag: self.impact=Impact()
        def ReadFromFolder(self,path):
            p_folder=path+'/p'
            self.p_files = [f for f in os.listdir(p_folder) if os.path.isfile(os.path.join(p_folder, f))]
            b_folder=path+'/b'
            self.b_files = [f for f in os.listdir(b_folder) if os.path.isfile(os.path.join(b_folder, f))]
            lime_folder=path+'/lime'
            if os.path.isdir(lime_folder):
                self.lime_files = [f for f in os.listdir(lime_folder) if os.path.isfile(os.path.join(lime_folder, f))]
            df={
                'PROCESS':{},
                'BOUNDARY':[],
                'LIME2':{}
            }
            for file in self.p_files:
                path_p=p_folder+'/' +file
                with open(path_p, mode='r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    data=[]
                    for row in reader:
                        if row[0][0]=='%':continue
                        data.append(row)
                    name=data[0][0]
                    data2=data[1:]
                    dd=[]
                    for fdata in data2:
                        fdata[3]=float(fdata[3])
                        if len(fdata)==5:
                            fdata[4]=float(fdata[4])
                        dd.append(fdata)
                    df['PROCESS'][name]=dd
            path_b=b_folder+'/' +self.b_files[0]
            with open(path_b, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                data=[]
                for row in reader:
                    if row[0][0]=='%':continue
                    row[3]=float(row[3])
                    data.append(row)
                df['BOUNDARY']=data
            if os.path.isdir(lime_folder):
                for file in self.lime_files:
                    path_lime=lime_folder+'/' +file
                    with open(path_lime, mode='r', encoding='utf-8-sig') as f:
                        reader = csv.reader(f)
                        data=[]
                        for row in reader:
                            if row[0][0]=='%':continue
                            data.append(row)
                        name=data[0][0]
                        data2=data[1][0]
                        dd=[data2]
                        dcond=[]
                        data3=data[2:]
                        for cond in data3:
                            a=(cond[0],cond[1])
                            dcond.append(a)
                        dd.append(dcond)
                        df['LIME2'][name]=dd
            if self.limeFlag:
                IFlist=self.impact.get_IFlist(df)
                load=list(IFlist.keys())
                for ldata in load:
                    df['LIME2'][ldata].append(IFlist[ldata])                   
            self.df=df
            return
        def ReadFromDict(self,df,read=True):
            if read:
                #LIME2データを読み取り，dfに追加する
                IFlist=self.impact.get_IFlist(df,read=read)
                load=list(IFlist.keys())
                for ldata in load:
                    df['LIME2'][ldata].append(IFlist[ldata])
            self.df=df
        def GetDf(self):
            return self.df
        def Calc(self,read=True):
            self.mlca=MLCA()
            self.mlca.input_data(self.df,read)
            self.mlca.MakeMatrix()
            solution,surplusFlow,loadValue=self.mlca.Solve()
            self.solution=solution
            self.surplusFlow=surplusFlow
            self.loadValue=loadValue
            self.uncertainty=self.mlca.Uncertainty()
        def __del__(self):
            if 'self.obj' in locals():
                del self.impact          

            
class Impact:
    def __init__(self):
        IFPath=['acidification','air_pollution','consumption','ecotoxicity','Eutrophication','global_warming','hazardous','noise','oxidantsv','Ozone','waste']
        IFvalue=[]
        for path in IFPath:
            df=pd.read_csv(path+'.csv')
            IFvalue.append((path,df))
        self.IFvalue=IFvalue
        self.IFPath=IFPath
    def getIFvalue(self,IFname):
        for name,df in self.IFvalue:
            if name==IFname:
                data=df
                break
        return data
    def get_data(self,chemical,df):
        mean=df.loc[df['化学式']==chemical,'平均値']
        sigm=df.loc[df['化学式']==chemical,'標準偏差']
        median=df.loc[df['化学式']==chemical,'代表値\r\n(中央値)']
        unit=df.loc[df['化学式']==chemical,'基準単位']
        val2=df.loc[df['化学式']==chemical,'代表値2']
        val3=df.loc[df['化学式']==chemical,'代表値2']
        data={
            'mean':mean.values,
            'sigm':sigm.values,
            'median':median.values,
            'unit':unit.values,
            'val2':val2.values,
            'val3':val3.values
            }
        return data
    def AndCondition(self,conditions,df):
# 条件を動的に作成
        condition = pd.Series(True, index=df.index)
        for col, value in conditions:
            condition &= (df[col] == value)

        # 条件に一致する行の 'target_col' を取得
        mean = df.loc[condition, '平均値'].values[0]
        sigm = df.loc[condition, '標準偏差'].values[0]
        median = df.loc[condition, '代表値\r\n(中央値)'].values[0]
        unit = df.loc[condition, '基準単位'].values[0]
        val2 = df.loc[condition, '代表値2'].values[0]
        val3 = df.loc[condition, '代表値2'].values[0]
        data={
            'mean':mean,
            'sigm':sigm,
            'median':median,
            'unit':unit,
            'val2':val2,
            'val3':val3
            }
        return data
    def S_ij_IFtotal(self,beta,smat_ij_beta,IFk,IFtotal):
        """
        aijのIFtotalに対する感度
        式(14)
        """
        # 積和の計算
        product_sum = sum(a * b * c for a, b, c in zip(beta,smat_ij_beta,IFk))
        return product_sum/IFtotal
    def get_IFlist(self,df,read=True):
        '''
        dfよりIF情報を読み取り，IFlistとして返す
        もし，read=Falseのとき，dfに書かれている
        データそのものを返す
        '''
        IFlist={}
        if read:
            load_list=list(df['LIME2'].keys())
            for load in load_list:
                dd=df['LIME2'][load]
                dt=self.getIFvalue(dd[0])
                conditions=dd[1]
                picked_data=self.AndCondition(conditions,dt)
                IFlist[load]=[picked_data['mean'],picked_data['sigm']] 
        else:#dfから直接IFを読みだす
            loads=df['LIME2'].keys()
            for load in loads:
                IFlist[load]=df['LIME2'][load][2]
        return IFlist

import copy
from pyDOE import *
from scipy.stats.distributions import norm
from . import Kriging as kr
import pickle
class RBLD():
    '''
    Class for Reliability Based LCA Design
    '''
    def __init__(self):
        self.limeFlag=False
        self.io=IO()
        if self.limeFlag: self.impact=Impact()        
        self.mlca=MLCA()
        self.krig=kr.Kriging()
    def SetDf(self,df,read=True):
        self.io.ReadFromDict(df,read)
    def SetDfFromPath(self,path):
        self.io.ReadFromFolder(path)
    def Calc(self):
        '''
        Single Indexのチェック
        '''
        #mlca=pm.MLCA()
        self.mlca.input_data(self.io.GetDf(),read=False)
        self.mlca.MakeMatrix()
        solution,surplusFlow,loadValue=self.mlca.Solve()
        IFlist=self.impact.get_IFlist(self.io.GetDf(),read=False)
        self.mlca.setIF(IFlist)
        print('SI=',self.mlca.SingleIndex())
    def PickLargeFlowSI(self,RankLimit:float):
        '''
        SIについて
        IOに読み込んでいるdfに対してインベントリ分析を実施し，
        感度値がRankLimit以上のフローを抽出してpd.DataFrame
        形式で戻す
        '''
        self.mlca.input_data(self.io.GetDf(),read=False)
        self.mlca.MakeMatrix()
        solution,surplusFlow,loadValue=self.mlca.Solve()
        IFlist=self.impact.get_IFlist(self.io.GetDf(),read=False)
        self.mlca.setIF(IFlist)
        self.mlca.SmatIF()
        Rank=10
        best,worst=self.mlca.EvalRankSI(Rank)
        i_beta=0
        # 条件に基づく抽出
        filtered_best = best[i_beta][best[i_beta]['value'] >= RankLimit]
        filtered_worst = worst[i_beta][worst[i_beta]['value'] <= -RankLimit]
        # 新しいDataFrameの作成
        variables = pd.concat([filtered_best, filtered_worst], ignore_index=True)
        return variables
    def PickLargeFlow(self,load:str,RankLimit:float):
        '''
        環境負荷項目loadについて
        IOに読み込んでいるdfに対してインベントリ分析を実施し，
        感度値がRankLimit以上のフローを抽出してpd.DataFrame
        形式で戻す
        '''
        self.mlca.input_data(self.io.GetDf(),read=False)
        self.mlca.MakeMatrix()
        solution,surplusFlow,loadValue=self.mlca.Solve()
        Rank=10
        best,worst=self.mlca.EvalRank(Rank)
        i_beta=self.mlca.load_list.index(load)
        # 条件に基づく抽出
        filtered_best = best[i_beta][best[i_beta]['value'] >= RankLimit]
        filtered_worst = worst[i_beta][worst[i_beta]['value'] <= -RankLimit]
        # 新しいDataFrameの作成
        variables = pd.concat([filtered_best, filtered_worst], ignore_index=True)
        return variables
    def LHScalc(self,load:str,variables,samples=1000):
        '''
        variables情報をもとに，上位のflowのmean,stdを抽出し，
        lhsに基づく正規乱数のサンプル点を生成。応答曲面を作成して
        戻す。samplesは各変数のサンプル点数。
        self.mean 平均値リスト
        self.std 標準偏差リスト
        '''
        i_beta=self.mlca.load_list.index(load)
        mean=[]
        std=[]
        n=len(variables)
        for i in range(n):
            process=variables.loc[i, 'process']
            flow=variables.loc[i,'flow']
            dd=self.mlca.df['PROCESS'][process]
            #print(dd)
            m=[sublist[3] for sublist in dd if sublist[1]==flow]
            mean.append(m[0])
            s=[sublist[4] for sublist in dd if sublist[1]==flow]
            std.append(s[0])
        self.mean=mean
        self.std=std
        X= lhs(n, samples=samples)
        for i in range(n):
            X[:, i] = norm(loc=mean[i], scale=std[i]).ppf(X[:, i])
            #X[:,i]=np.random.randint(mean[i]-std[i],mean[i]+std[i],samples)
        #Kriging用の入力データ作成
        W=np.zeros(len(X))
        for i in range(len(X)):
            xx=X[i]
            df=self.ArrangeData(xx,variables)
            self.mlca.input_data(df,read=False)
            self.mlca.MakeMatrix()
            solution,surplusFlow,loadValue=self.mlca.Solve()
            W[i]=loadValue[i_beta]
        #何故かWに負の値が入ることがある。該当するX,Wの要素は削除する
        X_filtered = [x for x, w in zip(X, W) if w >= 0]
        W_filtered = [w for w in W if w >= 0]
        X=np.array(X_filtered)
        W=np.array(W_filtered)
        return X,W
    def LHScalcSI(self,variables,samples=1000):
        '''
        variables情報をもとに，上位のflowのmean,stdを抽出し，
        lhsに基づく正規乱数のサンプル点を生成。応答曲面を作成して
        戻す。samplesは各変数のサンプル点数。
        self.mean 平均値リスト
        self.std 標準偏差リスト
        '''
        mean=[]
        std=[]
        n=len(variables)
        IFlist=self.impact.get_IFlist(self.io.GetDf(),read=False)
        for i in range(n):
            process=variables.loc[i, 'process']
            flow=variables.loc[i,'flow']
            if process=='IF':
                load_str=flow.removeprefix('IF_')
                iindex=self.mlca.load_list.index(load_str)
                m=self.mlca.IF[iindex]
                s=self.mlca.sdIF[iindex]
                mean.append(m)
                std.append(s)
            else:
                dd=self.mlca.df['PROCESS'][process]
                #print(dd)
                m=[sublist[3] for sublist in dd if sublist[1]==flow]
                mean.append(m[0])
                s=[sublist[4] for sublist in dd if sublist[1]==flow]
                std.append(s[0])
        self.mean=mean
        self.std=std
        X= lhs(n, samples=samples)
        for i in range(n):
            X[:, i] = norm(loc=mean[i], scale=std[i]).ppf(X[:, i])
            #X[:,i]=np.random.randint(mean[i]-std[i],mean[i]+std[i],samples)
        #Kriging用の入力データ作成
        W=np.zeros(len(X))
        for i in range(len(X)):
            xx=X[i]
            #va位情報に基づき，lhsで発生されたサンプルの組xxの数値をdfの該当部分に代入してdfとし戻すriablesの感度上
            df=self.ArrangeData(xx,variables)
            self.mlca.input_data(df,read=False)
            self.mlca.MakeMatrix()
            solution,surplusFlow,loadValue=self.mlca.Solve()
            W[i]=self.mlca.SingleIndex()
        #何故かWに負の値が入ることがある。該当するX,Wの要素は削除する
        X_filtered = [x for x, w in zip(X, W) if w >= 0]
        W_filtered = [w for w in W if w >= 0]
        X=np.array(X_filtered)
        W=np.array(W_filtered)
        return X,W
    def CalcLoad(self,i_beta,RankLimit=0.9,ratio=0.1,n_grid = 5):
        '''
        環境負荷i_betaに対する応答曲面計算
        RankLimit:  この数値以上の感度データを対象変数とする
        ratio: 応答曲面の範囲とする平均値周りの平均値に対する割合
        n_grid: 一変数に対する格子点数
        '''
        #mlca=pm.MLCA()
        self.mlca.input_data(self.io.GetDf(),read=False)
        self.mlca.MakeMatrix()
        solution,surplusFlow,loadValue=self.mlca.Solve()
        Rank=10
        best,worst=self.mlca.EvalRank(Rank)
        # 条件に基づく抽出
        filtered_best = best[i_beta][best[i_beta]['value'] >= RankLimit]
        #filtered_worst = worst[i_beta][worst[i_beta]['value'] <= -RankLimit]
        # 新しいDataFrameの作成
        #variables = pd.concat([filtered_best, filtered_worst], ignore_index=True)
        variables=filtered_best
        n=len(variables)#対象とする変数の数
        # n個のリストを生成
        lists=[]        
        for i in range(n):
            process=variables.loc[i, 'process']
            flow=variables.loc[i,'flow']
            dd=self.mlca.df['PROCESS'][process]
            #print(dd)
            val=[sublist[3] for sublist in dd if sublist[1]==flow]
            vmin=val[0]-abs(val[0])*ratio
            vmax=val[0]+abs(val[0])*ratio
            lists.append(np.linspace(vmin,vmax,n_grid))#対象とする変数のグリッドデータ
        #Kriging用の入力データ作成
        X2=np.meshgrid(*lists)
        X=np.stack(X2, axis=-1).reshape(-1, n)
        W=np.zeros(len(X))
        self.variables=variables

        for i in range(len(X)):
            xx=X[i]
            df=self.ArrangeData(xx,variables)
            self.mlca.input_data(df,read=False)
            self.mlca.MakeMatrix()
            solution,surplusFlow,loadValue=self.mlca.Solve()
            W[i]=loadValue[i_beta]
        return X,W
    def ArrangeData(self,xx,variables):
        '''
        dfに対して，変更する変数の組xxの値をvariable(pd.DataFrame)のテーブルに従って，dfを書き換えて戻す
        '''
        dff=self.io.GetDf()
        df=copy.deepcopy(dff)#辞書型データのコピーは深いコピーをしないと，元のデータに影響を与えてしまうことに注意
        for i in range(len(variables)):
            line=variables.iloc[i]
            if line['process']!='IF':
                dd=df['PROCESS'][line['process']]
                for j in range(len(dd)):
                    flow=dd[j]
                    if flow[1]==line['flow']:
                        flow[3]=xx[i]
                        dd[j]=flow
                        break
                df['PROCESS'][line['process']]=dd
            else:#LIME2データに対する処置
                load=line['flow'][3:]#頭にIF_が付いているので除去
                dd=df['LIME2'][load][2]#平均値，標準偏差のリスト取り出し
                dd[0]=xx[i]#平均値部分の書き換え
                df['LIME2'][load][2]=dd
        return df
    def Sampling(self,RankLimit:float,samples:int,target='SI')-> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        '''
        応答曲面作成のための，サンプル点の発生
        RankLimit: 感度値の打ち切り値
        samples: サンプル数
        target: 応答計算の対象，default 'SI'，それ以外は環境負荷項目
        '''
        if target=='SI':
            variables=self.PickLargeFlowSI(RankLimit)
            X,W=self.LHScalcSI(variables,samples=samples)
        else: #環境負荷項目
            variables=self.PickLargeFlow(target,RankLimit)
            X,W=self.LHScalc(target,variables,samples=samples)
        return X,W,variables
    def MakeSurface(self,RankLimit:float,samples:int,alpha=1e-5,target='SI')-> Tuple[float, np.ndarray, np.ndarray,pd.DataFrame]:
        '''
        応答曲面を作成する
        RankLimit: 感度値の打ち切り値
        samples: サンプル数
        '''
        X,W,variables=self.Sampling(RankLimit,samples,target=target)
        self.krig.setData(X,W)
        r2_score=self.krig.Fit(alpha=alpha)
        return r2_score,X,W,variables
    def Reliability(self,allow:float) :
        '''
        計算済みの応答曲面を使って信頼性評価
        '''
        muX=self.mean
        sigmmaX=self.std
        n=len(muX)
        dist=[]
        for i in range(n):
            dist.append('normal')
        self.rs=ResponseSurface(muX,sigmmaX,dist,self.krig,allow)
        self.rs.RFn()
        return self.rs
    def f_save(self,fname:str): 
        '''
        信頼性インスタンスのpklファイルへの保存
        ''' 
        with open(fname, "wb") as file:
            pickle.dump(self.rs, file)
    def f_load(self,fname:str) :
        with open(fname, "rb") as file:
            self.rs = pickle.load(file)                          
    def __del__(self):
        del self.mlca
        del self.io
        if 'self.impact' in locals():
            del self.impact
        del self.krig
        if 'self.rs' in locals():
            del self.rs
from MLCArel import LimitState as ls
import numpy as np
class ResponseSurface(ls.LSFM):
    """
    応答曲面管理クラス
    """
    def __init__(self,muX,sigmmaX,dist,krig,allow):
        self.krig=krig
        self.n=len(muX)
        self.allow=allow#許容値
        super().__init__(self.n,muX,sigmmaX,dist)
    def gcalc(self,X): #g値を計算する仮想関数
        lists=[]
        for i in range(self.n):
            lists.append(X[i])
        target_point = np.array([lists])
        val,sigma=self.krig.Predict(target_point)
        g=self.allow-val[0]
        #print(X,g)
        return g  #必ずg値を戻す
    def dGdXcalc(self,X): #gの微分ベクトルを計算する仮想関数
        lists=[]
        for i in range(self.n):
            lists.append(X[i])
        target_point = np.array([lists])
        dGdX=-self.krig.Diff(target_point) 
        #print(dGdX)
        return list(dGdX) #必ず微分ベクトルを戻す
import matplotlib.pyplot as plt
class DesignProcess():
    '''
    信頼性設計を一元管理するクラス
    '''
    def __init__(self):
        self.rbld=RBLD()
    def CheckRankLimit(self,RankLimit=1.5,target='SI')->Tuple[np.ndarray]:
        if target=='SI':
            self.variables=self.rbld.PickLargeFlowSI(RankLimit)
        else:
            self.variables=self.rbld.PickLargeFlow(target,RankLimit)
        return self.variables
    def SetDf(self,df,read=True):
        '''
        LIME2に関する値のセットをするときread=True,何の処置もしないときはFalse
        '''
        self.df=df
        self.rbld.SetDf(df,read)
    def SimpleAnalysis(self):
        '''
        読み込まれているデータに対して一度のMatrix-based LCAを実施する
        戻り値:solution,surplusFlow,loadValue
        '''
        df=self.GetDf()
        self.rbld.mlca.input_data(df)
        self.rbld.mlca.MakeMatrix()
        solution,surplusFlow,loadValue=self.rbld.mlca.Solve()
        return solution,surplusFlow,loadValue
    def GetMultiplier(self,n_disp=5) ->dict:
        '''
        SimpleAnalysisで解析後にMultiplierを環境負荷ごとに取得する。
        データは辞書形式で戻す。n_dispは表示するmultiplierの数。
        '''
        n_beta=len(self.rbld.mlca.load_list)
        n_disp=5
        res={}
        for i_beta in range(n_beta):
            s=self.rbld.mlca.Smat(i_beta)
            res[self.rbld.mlca.load_list[i_beta]]={}
            dmax=self.rbld.mlca.PickMax(s,n_disp,i_beta)
            dmin=self.rbld.mlca.PickMin(s,n_disp,i_beta)
            res[self.rbld.mlca.load_list[i_beta]]={'Max':dmax}
            res[self.rbld.mlca.load_list[i_beta]]['Min']=dmin
        return res       
    def SetDfFromPath(self,path:str):
        self.rbld.SetDfFromPath(path)
    def GetDf(self):
        return self.rbld.io.df
    def SetVal(self,RankLimit=1.5,samples=2000):
        self.RankLimit=RankLimit
        self.samples=samples
    def SetAllow(self,allow):
        self.allow=allow        
    def CalcSurface(self,target='SI',alpha=1e-5):
        r2_score,X,W,variables=self.rbld.MakeSurface(self.RankLimit,self.samples,target=target,alpha=alpha)
        #self.rs=self.rbld.Reliability(self.allow)
        return r2_score,X,W,variables
    def ReliabilityAnal(self):
        self.rs=self.rbld.Reliability(self.allow)
    def SeriesCalc(self,target,rmin,rmax,n):
        '''
        multiplierの中から決定した特定のentityについて，連続的に変化させて対応する信頼性指標を計算する。計算結果はDataFrameで返す。targetは
        target=multiplier['CO2']['Max'][1]
        のような形で指定する。
        rmin: 選んだ項目に乗じた値を下限とする
        rmax: 選んだ項目に乗じた値を上限とする
        n   : 上下限の間の計算点数
        '''
        df=self.GetDf()
        process=target[0]; entity=target[1]
        data=df['PROCESS'][process]
        picked_data = [(index, item) for index, item in enumerate(data) if len(item) > 1 and item[1] == entity]
        c_no=picked_data[0][0]
        c_data=picked_data[0][1]
        val=c_data[3]
        vval=np.linspace(rmin*val,rmax*val,n).tolist()
        vv=[]
        beta=[]
        for v in vval:
            c_data[3]=v
            df['PROCESS'][process][c_no] =c_data
            self.SetDf(df,read=False)
            r2_score,X,W,variables=self.CalcSurface(target='CO2')
            self.ReliabilityAnal()
            vv.append(v)
            beta.append(self.rs.GetBeta())
        res=pd.DataFrame()
        res['Val']=vv
        res['Beta']=beta
        return process,entity,res
    def Hist(self,W,target='SI'):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.hist(W, bins=50)
        ax.set_title('first histogram of '+target)
        ax.set_xlabel(target)
        ax.set_ylabel('freq')
        fig.show()
    def GetName(self):
        '''
        材料，余剰フロー，環境名の文字列リストを返す
        '''
        material,surplus,load_list=self.rbld.mlca.extract_base()
        return material,surplus,load_list
    def GetSmat(self,i):
        return self.rbld.mlca.Smat(i)
    def GetloadValue(self):
        return self.rbld.mlca.loadValue
    def GetAload(self):
        return self.rbld.mlca.Aload
    def __del__(self):
        del self.rbld
###################################
#Comaparative LCA実践のための追加
###################################
class ComparativeLCA:
    def __init__(self):
        self.dpA=DesignProcess()
        self.dpB=DesignProcess()
        self.krig=kr.Kriging()
    def SetDfFromPath(self,pathA:str,pathB:str)->None:
        self.dpA.SetDfFromPath(pathA)
        self.dpB.SetDfFromPath(pathB)
    def SimpleAnalysis(self):
        solutionA,surplusFlowA,loadValueA=self.dpA.SimpleAnalysis()
        solutionB,surplusFlowB,loadValueB=self.dpB.SimpleAnalysis()
        resA=[solutionA,surplusFlowA,loadValueA]
        resB=[solutionB,surplusFlowB,loadValueB]
        return resA,resB
    def SetVal(self,RankLimitA=1.5,RankLimitB=0.9,samples=2000)->None:
        self.dpA.SetVal(RankLimit=RankLimitA,samples=samples)
        self.dpB.SetVal(RankLimit=RankLimitB,samples=samples)
    def SetAllow(self,allowA,allowB):
        self.dpA.SetAllow(allowA)
        self.dpB.SetAllow(allowB)
    def MakeSurface(self,target='CO2',alpha=1e-5):
        r2A,XA,WA,varA=self.dpA.CalcSurface(target=target)
        r2B,XB,WB,varB=self.dpB.CalcSurface(target=target)
        X=np.hstack((XA,XB))#Xについて両者をマージ
        W=WA-WB#二つのシナリオの差を計算
        self.krig.setData(X,W)
        r2_score=self.krig.Fit(alpha=alpha)
        variables=[varA,varB]
        return r2_score,X,W,variables
    def CheckRankLimit(self,RankLimitA=1.5,RankLimitB=0.9,target='CO2')->Tuple[np.ndarray]:
        varA=self.dpA.rbld.PickLargeFlow(target,RankLimitA)
        varB=self.dpB.rbld.PickLargeFlow(target,RankLimitB)
        return varA,varB
    def Reliability(self) :
        '''
        計算済みの応答曲面を使って信頼性評価
        '''
        muX=self.dpA.rbld.mean+self.dpB.rbld.mean
        sigmmaX=self.dpA.rbld.std+self.dpB.rbld.std
        n=len(muX)
        dist=[]
        for i in range(n):
            dist.append('normal')
        self.rs=ResponseComparative(muX,sigmmaX,dist,self.krig)
        self.rs.RFn()
        return self.rs
    def __del__(self):
        del self.rbldA
        del self.rbldB
        del self.krig
class ResponseComparative(ls.LSFM):
    """
    ComparativeLCA用応答曲面管理クラス
    """
    def __init__(self,muX,sigmmaX,dist,krig):
        self.krig=krig
        self.n=len(muX)
        super().__init__(self.n,muX,sigmmaX,dist)
    def gcalc(self,X): #g値を計算する仮想関数
        lists=[]
        for i in range(self.n):
            lists.append(X[i])
        target_point = np.array([lists])
        val,sigma=self.krig.Predict(target_point)
        g=val[0]#A-Bの結果が入っている
        #print(X,g)
        return g  #必ずg値を戻す
    def dGdXcalc(self,X): #gの微分ベクトルを計算する仮想関数
        lists=[]
        for i in range(self.n):
            lists.append(X[i])
        target_point = np.array([lists])
        dGdX=self.krig.Diff(target_point) 
        #print(dGdX)
        return list(dGdX) #必ず微分ベクトルを戻す


