"""
    限界状態関数法サポートモジュール
　　Copyright 2021, S.Sakai All rights reserved
    private version 2024.2.5
    --メモ--
    v1.1 RelBase.GetPOFの修正:Pf=0近傍の条件のとき、RF()計算過程で異常値がでる可能性があり、打ち切られてしまう。そのとき、β=0,Pf=1が入力されていて、正しくない。正しくは、Pf=0となるべき。これの対応として、GetPOF時の対応で行うこととした。つまり、β=0でなおかつ、平均値でg値が正であれば、Pf=0であることが明らかなので、この条件でPf=0を戻すこととした(2024.2.8)
"""
import numpy as np
from scipy.stats import norm
class Dbase:
    """
    目的:任意分布管理のための基底クラス
    """
    def __init__(self,mu,sigmma):
        self.muX=mu
        self.sigmmaX=sigmma
    def GetMeanSig(self):
        return [self.muX,self.sigmmaX]
    def DushCalc(self,X):
        self.sigmmaDush=norm.pdf(norm.ppf(self.CDF(X))/self.PDF(X))
        self.muDush=X-(norm.ppf(self.CDF(X)))*self.sigmmaDush
    def CDF(self,X):
        return norm.cdf(X)
    def PDF(self,X):
        return norm.pdf(X)
    def Eq(self,X):
        print('Specify Eq()!')
import math
from scipy.stats import lognorm
from scipy.stats import gumbel_r
from scipy.stats import weibull_min
from scipy.stats import uniform
class GUniform(Dbase):
    """
    """
    def __init__(self,mu,sigmmaX):
        super().__init__(mu,sigmmaX)
    def Eq(self,X):
        a,b=self.Param()
        if uniform(loc=a,scale=b-a).cdf(X)==0.0:
            phi=0.0
        else:
            phi=norm.pdf(norm.ppf(uniform(loc=a,scale=b-a).cdf(X)))
        fxi=uniform(loc=a,scale=b-a).pdf(X)
        if fxi==0.0:
            fxi=1e-20
        sigm=phi/fxi
        if sigm==0:
            sigm=1e-20
        mu=X-norm.ppf(uniform(loc=a,scale=b-a).cdf(X))*sigm
        return [mu,sigm]        
    def Param(self):
        tt=super().GetMeanSig()
        mu=tt[0]; sig=tt[1]
        a=mu-np.sqrt(3)*sig
        b=mu+np.sqrt(3)*sig
        return a,b
    def MuSigm(self,a,b):
        mu=(a+b)/2.0
        sigm=(b-a)/(2*np.sqrt(3))
        return mu,sigm
    def CDF(self,X):
        a,b=self.Param()
        return uniform(loc=a,scale=b-a).cdf(X)
    def PDF(self,X):
        a,b=self.Param()
        return uniform(loc=a,scale=b-a).pdf(X)
class GNormal(Dbase):
    def __init__(self,mu,sigmmaX):
        super().__init__(mu,sigmmaX)
    def Eq(self,X):
        return [self.muX,self.sigmmaX]
class GLognormal(Dbase):
    """
       zeta:σ
       lambd:scale
    """
    def __init__(self,mu,sigmmaX):
        super().__init__(mu,sigmmaX)
    def Eq(self,X):
        zeta=math.sqrt(math.log(1+(self.sigmmaX/self.muX)**2))
        lambd=math.log(self.muX)-0.5*zeta*zeta
        scale=math.exp(lambd)
        phi=norm.pdf(norm.ppf(lognorm(s=zeta,scale=scale).cdf(X)))
        fxi=lognorm(s=zeta,scale=scale).pdf(X)
        sigm=phi/fxi
        mu=X-norm.ppf(lognorm(s=zeta,scale=scale).cdf(X))*sigm
        return [mu,sigm]
    def Param(self):
        self.zeta=math.sqrt(math.log(1+(self.sigmmaX/self.muX)**2))
        self.lambd=math.log(self.muX)-0.5*self.zeta*self.zeta
        return [self.zeta,self.lambd]
    def SetParam(self,lambd,zeta):
        self.muX=math.exp(lambd+zeta*zeta/2.0)
        self.sigmmaX=math.sqrt(self.muX*self.muX*(math.exp(eta*zeta)-1.0))
        return [self.muX,self.sigmmaX]
class GGumbel(Dbase):
    def __init__(self,mu,sigmmaX):
        super().__init__(mu,sigmmaX)
    def Eq(self,X):
        eta=math.sqrt(6.)*self.sigmmaX/math.pi #shape
        mu=self.muX-0.57722*eta #loc
        phi=norm.pdf(norm.ppf(gumbel_r.cdf(X,mu,eta)))
        fXi=gumbel_r.pdf(X,mu,eta)
        sigm=phi/fXi
        mu=X-norm.ppf(gumbel_r.cdf(X,mu,eta)) * sigm
        return [mu,sigm]
    def Param(self):
        eta=math.sqrt(6.)*self.sigmmaX/math.pi #shape
        mu=self.muX-0.57722*eta #loc
        return [mu,eta]
    def SetParam(self,mu,eta):
        self.sigmmaX=math.pi/math.sqrt(6.)*eta
        self.muX=mu+0.57722*eta
        return [self.muX,self.sigmmaX]
    def MuSigm(self,mu,eta):
        return [mu+0.57722*eta, math.pi*eta/math.sqrt(6.)]
class GWeibull(Dbase):
    def __init__(self,mu,sigmmaX):
        super().__init__(mu,sigmmaX)
    def Eq(self,X):
        self.FactorCalc()
        super().DushCalc(X)
        return [self.muDush,self.sigmmaDush]
    def FactorCalc(self):
        cov=self.muX/self.sigmmaX
        self.ar=cov**(-1.08) #Prof.Ichikawa's theory
        self.beta=self.muX/math.gamma(1.0+1/self.ar)
    def PDF(self,X):
        return weibull_min.pdf(X, self.ar, scale=self.beta)
    def CDF(self,X):
        return weibull_min.cdf(X, self.ar, scale=self.beta)
class Lbase:
    """
    目的:限界状態関数定義のための基底クラス
    """
    def __init__(self,n):
        self.n=n
        self.X=np.zeros(n)
        self.dGdX=np.zeros(n)
        self.g=0
    def GetN(self):
        return self.n
    def GetX(self):
        return self.X
    def SetX(self,X):
        self.X=X
    def GetG(self):
        return self.g
    def SetG(self,g):
        self.g=g
    def GetdGdX(self):
        return self.dGdX
    def SetdGdX(self,x):
        self.dGdX=x
def dict2data(data):
    """
    辞書型データのLSFM入力データへの変換
    """
    keys=data.keys()
    muX=[]
    sigmmaX=[]
    dist=[]
    for key in keys:
        muX.append(data[key]['mean'])
        sigmmaX.append(data[key]['mean']*data[key]['cov'])
        dist.append(data[key]['dist'])
    return len(keys),muX,sigmmaX,dist
import pandas as pd
class LSFM:
    """
    目的:信頼性解析管理のための基底クラス
    method一覧
    RF()      Rackvitz Fiessler法による設計点探索
    GetBeta() 信頼性指標βの取得
    GetAlpha()感度ベクトルの取得
    GetPOF()  破損確率の取得
    GetDP()   設計点の取得
    GetConv() RF法の収束回数の取得
    GetPSF()  部分安全係数の取得
    """
    def __init__(self,n,Mu,sigmmaX,dist):
        #これを呼ぶ以前にDefineGでself.limを定義しておくこと
        self.n=n
        self.muX=Mu
        self.sigmmaX=sigmmaX
        self.dist=dist
        self.alphai=np.zeros(n)
        self.beta=0.0
        self.POF=1.0
        self.Distr=[]
        self.flag=1#平均値が破損領域の時-1,非破損領域の解き1
        if self.gcalc(Mu)<0:
            self.flag=-1
        #self.lim=Lbase
        for i in range(n):
            if self.dist[i]=='weibull':
                self.Distr.append(GWeibull(self.muX[i],self.sigmmaX[i]))
            if self.dist[i]=='normal':
                self.Distr.append(GNormal(self.muX[i],self.sigmmaX[i]))
            if self.dist[i]=='lognormal':
                self.Distr.append(GLognormal(self.muX[i],self.sigmmaX[i]))
            if self.dist[i]=='gumbel':
                self.Distr.append(GGumbel(self.muX[i],self.sigmmaX[i]))
            if self.dist[i]=='uniform':
                self.Distr.append(GUniform(self.muX[i],self.sigmmaX[i]))           
    def GetN(self):
        return self.n
    def GetMu(self):
        return self.muX
    def SetMu(self,aa):
        self.muX=aa
    def gcalc(self):
        #virtual function
        return 0
    def dGdXcalc(self):
        #virtual function
        return 0
    def RFn(self,start='Origin',Xstart=[100,100]):
        """
        Racwitz-Fiessler algoritm
        start:  'Origin'      start point is origin(Default)
                'Coordinate'  start point is an arbitrary coordinate
        Xstart: list of starting point
        gcalc,dGdXcalcを仮想関数で与えるバージョン
        """
        betaold=40
        delta=1e-6
        munormX=np.zeros(self.n)
        sigmmanormX=np.zeros(self.n)
        X=self.muX.copy()
        if start!='Origin':
            X=Xstart
        for i in range(100):
            for j in range(self.n):
                Valu=self.Distr[j].Eq(X[j])
                munormX[j]=Valu[0]#非正規分布の正規化後の平均値
                sigmmanormX[j]=Valu[1]#非正規分布の正規化後の標準偏差
            Xdush=(X-munormX)/sigmmanormX
            Xdush_old=Xdush
            #self.lim.SetX(X)
            g=self.gcalc(X)
            dgdX=self.dGdXcalc(X)
            #g=self.lim.GetG()
            #dgdX=self.lim.GetdGdX()
            dgdXdush=dgdX*sigmmanormX
            A = 1 / sum(dgdXdush * dgdXdush) * (sum(dgdXdush * Xdush) - g)
            Xdush = A * dgdXdush
            self.alphai = dgdXdush / math.sqrt(sum(dgdXdush * dgdXdush))
            Xdush_new = Xdush
            betanew = math.sqrt(sum(Xdush * Xdush))
            hantei = math.isnan(betanew)
            if hantei:
                betaold = betaold
            else:
                X = munormX + sigmmanormX * Xdush
                if abs(betaold - betanew) < delta:
                    break
                betaold=betanew
            X_t = munormX + sigmmanormX * Xdush_old
            g_hantei = self.gcalc(X_t)
            deltan = 50
            dXdush = (Xdush_new - Xdush_old) / deltan
            for i1 in range(deltan):
                Xdush_t = Xdush_old + i1 * dXdush
                X_t = munormX + sigmmanormX * Xdush_t
                g_hantein = self.gcalc(X_t)
                if math.isnan(g_hantei): #<----------------
                    return
                if g_hantei**2 > g_hantein**2:
                    Xdush = Xdush_t
                    g_hantei = g_hantein
                else:
                    g_hantei =g_hantei
            X = munormX + sigmmanormX * Xdush
        if self.flag>0:
            self.beta=betanew
        else:#平均値が破損領域に存在していたときには、信頼性指標の符合を反転する
            self.beta=-betanew
        self.POF=norm.sf(self.beta)
        self.DP=X
        self.ncon=i
    def RF(self,start='Origin',Xstart=[100,100]):
        """
        Racwitz-Fiessler algoritm
        start:  'Origin'      start point is origin(Default)
                'Coordinate'  start point is an arbitrary coordinate
        Xstart: list of starting point
        """
        betaold=40
        delta=1e-6
        munormX=np.zeros(self.n)
        sigmmanormX=np.zeros(self.n)
        X=self.muX.copy()
        if start!='Origin':
            X=Xstart
        for i in range(100):
            for j in range(self.n):
                Valu=self.Distr[j].Eq(X[j])
                munormX[j]=Valu[0]#非正規分布の正規化後の平均値
                sigmmanormX[j]=Valu[1]#非正規分布の正規化後の標準偏差
            Xdush=(X-munormX)/sigmmanormX
            Xdush_old=Xdush
            self.lim.SetX(X)
            self.lim.gcalc()
            self.lim.dGdXcalc()
            g=self.lim.GetG()
            dgdX=self.lim.GetdGdX()
            dgdXdush=dgdX*sigmmanormX
            A = 1 / sum(dgdXdush * dgdXdush) * (sum(dgdXdush * Xdush) - g)
            Xdush = A * dgdXdush
            self.alphai = dgdXdush / math.sqrt(sum(dgdXdush * dgdXdush))
            Xdush_new = Xdush
            betanew = math.sqrt(sum(Xdush * Xdush))
            hantei = math.isnan(betanew)
            if hantei:
                betaold = betaold
            else:
                X = munormX + sigmmanormX * Xdush
                if abs(betaold - betanew) < delta:
                    break
                betaold=betanew
            X_t = munormX + sigmmanormX * Xdush_old
            self.lim.SetX(X_t)
            self.lim.gcalc()
            g_hantei = self.lim.GetG()
            deltan = 50
            dXdush = (Xdush_new - Xdush_old) / deltan
            for i1 in range(deltan):
                Xdush_t = Xdush_old + i1 * dXdush
                X_t = munormX + sigmmanormX * Xdush_t
                self.lim.SetX(X_t)
                self.lim.gcalc()
                g_hantein = self.lim.GetG()
                if math.isnan(g_hantei): #<----------------
                    return
                if g_hantei**2 > g_hantein**2:
                    Xdush = Xdush_t
                    g_hantei = g_hantein
                else:
                    g_hantei =g_hantei
            X = munormX + sigmmanormX * Xdush
        if self.flag>0:
            self.beta=betanew
        else:#平均値が破損領域に存在していたときには、信頼性指標の符合を反転する
            self.beta=-betanew
        self.POF=norm.sf(self.beta)
        self.DP=X
        self.ncon=i
    def GetSigm(self):
        return self.sigmmaX
    def GetBeta(self):
        return self.beta
    def GetAlpha(self):
        return self.alphai
    def GetPOF(self):
        return self.POF
    def GetDP(self):
        return self.DP
    def GetConv(self):
        return self.ncon
    def GetPSF(self):
        return self.DP/self.muX
    def GetLim(self):
        return self.lim
    def GetG(self):
        X=self.muX
        self.lim.SetX(X)
        self.lim.gcalc()#ここでエラーがでるときには、self.limに対する特定処理が終わっていない
        return self.lim.GetG()
    def Gcalc(self,X):
        self.lim.SetX(X)
        self.lim.gcalc()
        return self.lim.GetG()
    def GetdGdX(self):
        return self.lim.GetdGdX()
from sympy import sympify,Symbol,factor,diff,pprint,expand
class GeneralG(LSFM):
    def __init__(self,gg,var,n,muX,sigmmaX,dist):
        self.n=len(var)
        self.gg=gg
        self.var=var
        super().__init__(n,muX,sigmmaX,dist)
    def gcalc(self,X):
        expr=self.gg
        for i in range(self.n):
            str1=self.var[i]+'=X['
            str1=str1+str(i)+']'
            #eval(str1)
            exec(str1)
        return eval(expr)
    def dGdXcalc(self,X):
        dGdX=[0]*len(X)
        for i in range(self.n):
            str1=self.var[i]+'=X['
            str1=str1+str(i)+']'
            exec(str1)
        expr=sympify(self.gg,locals={'S': Symbol('S')})
        for i in range(self.n):
            dstr1=diff(expr,self.var[i])
            dGdX[i]=eval(str(dstr1))
        return dGdX 
class Gmanage(LSFM):
    """ユーザ定義のGをLSFMによる解析に接続する
    　　使い方
      　brl=Gmanage(n,muX,sigmmaX,dist,G)
        brl.RF()
        print('beta=',brl.GetBeta())
        print('alpha=',brl.GetAlpha())
        Gの部分にユーザ定義のクラス名を記述
    """
    def __init__(self,n,Mu,sigmmaX,dist,g,dict={}):#dictにデータが記載されているときは、親クラスのDefineG関数関数内で限界状態関数管理オブジェクトself.limのsetDict関数を読んで、パラメータの設定や必要処置の実行を行う
        self.n=n
        gg=g(self.n)
        super().DefineG(gg,dict=dict)#この時点でLSFM.limにGが定義される
        super().__init__(n,Mu,sigmmaX,dist)
class RelBase:
    """汎用信頼性評価のための基底クラス
    """
    def SetData(self,data):
        key=self.variable
        self.muX=[]
        self.cov=[]
        self.dist=[]
        """
        for aa in key:
            self.muX.append(data[aa]['mean'])
            self.cov.append(data[aa]['cov'])
            self.dist.append(data[aa]['dist'])
        self.sigmmaX = list(np.array(self.cov)*np.array(self.muX))
        """
        self.sigmmaX=[]
        for aa in key:
            self.dist.append(data[aa]['dist'])
            muX=data[aa]['mean']
            self.muX.append(muX)
            if 'cov' in data[aa]:
                sX=muX*data[aa]['cov']
            else:
                sX=data[aa]['sd']
            self.sigmmaX.append(sX)       
    def Reliability(self,data,start='Origin',Xstart=[100,100],dict={}):
        """
        Reliability analysis by RF algorithm
                start:  'Origin'      start point is origin(Default)
                        'Coordinate'  start point is an arbitrary coordinate
                Xstart: list of starting point(Default [100,100])
        """
        n=len(self.variable)
        self.SetData(data)
        self.lsfm=Gmanage(n,self.muX,self.sigmmaX,self.dist,self.G,dict=dict)
        #if self.lsfm.GetG()>0:#平均値でのg値が破損領域にあるときには、自動的にβ=0,Pf=1として終了する。
        self.lsfm.RF(start=start,Xstart=Xstart)
    def RelSet(self,data,start='Origin',Xstart=[100,100]):
        n=len(self.variable)
        self.SetData(data)
        self.lsfm=Gmanage(n,self.muX,self.sigmmaX,self.dist,self.G)
        return self.lsfm       
    def Geval(self,xx,dict={}):
        """
        Reliabilityを実施せずに、g値を計算する
        """
        n=len(xx)
        # muuX,sigmmaX,distにはダミーの値を入れておく
        muX=[0.0001 for x in range(n)]
        sigmmaX=[0.0001 for x in range(n)]
        dist=['normal' for x in range(n)]
        self.lsfm=Gmanage(n,muX,sigmmaX,dist,self.G,dict=dict)
        return self.lsfm.Gcalc(xx)
    def GetDP(self):
        return self.lsfm.GetDP()
    def Gcalc(self,X):
        """
        Reliability実施後にg値を計算するとき、もっともGevalがあれば、これは不要かも
        """
        return self.lsfm.Gcalc(X)
    def GetG(self):
        return self.lsfm.GetG()
    def Gmean(self):
        return self.lsfm.Gcalc(self.muX)
    def GetBeta(self):
        return self.lsfm.GetBeta()
    def GetAlpha(self):
        return self.lsfm.GetAlpha()
    def GetPOF(self):
        Pf=self.lsfm.GetPOF()
        if self.lsfm.GetBeta()==0.0 and self.Gcalc(self.muX)>0.0:
            Pf=0.0
        return Pf
    def GetVar(self):
        return self.variable
    def GetTitle(self):
        return self.title
    ### 2023.1.5 Penetrationより移動
    def Gcheck(self,data,dict={}):
        """
        目的:dataについてg値の計算を行う
        """
        xx=[data[w]['mean'] for w in self.GetVariable()]
        return self.Geval(xx,dict=dict) #super() removed
    def SaveVariable(self,aa):
        """
        目的:確率変数の保存
        """
        self.variable=aa#<-------------------------------
    def GetVariable(self):
        return self.variable#<-------------------------------
    ###
from pyDOE import *
class LHSbase:
    """
    目的:LHS+USの乱数発生を管理するための基底クラス
    RSモデルの例
        from Utility import LimitState as ls
        class rnd_RS(ls.LHSbase):
            def __init__(self,nv):
                super().__init__(nv)
            def g(self,rnd):  #限界状態関数gを定義する。rnd:発生された乱数列。変数の順番に格納されている。
                    rr=rnd[:,0]  #変数の順番に乱数列を取り出していく
                    ss=rnd[:,1]
                    gval=rr-ss  #限界状態関数の計算結果リスト
                    return gval
        #### プログラム例 ####
        data={"r":{"mean":170,"cov":20/170,"dist":"normal"},
             "s":{"mean":100,"cov":20/100,"dist":"normal"},
             }
        nv=2 #変数の数
        n=300 #サンプル点数
        k=3 #サンプリングの領域の広さ
        lhb=rnd_RS(nv) #インスタンスの生成
        lhb.SetData(data) #データセット
        rnd,t=lhb.Calc(n,k) #乱数発生
        X_std=(rnd-lhb.Means())/lhb.Stdvs() #データの基準化
        print(lhb.gMean()) #平均値でのg値の値

    """
    def __init__(self,nv):
        self.nv=nv
    def SetData(self,data):
        self.data=data
        means=[]
        stdvs=[]
        flags=[]
        for key in data:
            mean=data[key]['mean']
            std=data[key]['cov']*mean
            flag=data[key]['flag']
            means.append(mean)
            stdvs.append(std)
            flags.append(flag)
        self.means=means
        self.stdvs=stdvs
        self.flags=flags
    def Means(self):
        return self.means
    def Stdvs(self):
        return self.stdvs
    def gMean(self):
        num=self.nv
        val=np.zeros((1,num))
        for i in range(num):
            val[0,i]=self.means[i]
        return self.g(val)[0]
    def Calc(self,n,k):
        design = lhs(self.nv, samples=n,criterion='maximin')
        u=design
        for i in range(self.nv):            
            #u[0,1]-->[mu-k*s,mu+k*s]への写像
            u[:, i] = k*self.stdvs[i]*(2*design[:,i]-1)+self.means[i]
        rnd=u
        t=(np.sign(self.g(rnd))+1)/2
        return rnd,t
    def Calc_foothills(self,n,k1=1,k2=4):
        """
        分布の裾野の乱数発生
        """
        design = lhs(self.nv, samples=n,criterion='center')
        u=design
        for i in range(self.nv):
            if self.flags[i]=='R':
                #u[0,1]-->[mu-kmin*s,mu-kl*s]への写像
                u[:,i]=(k2-k1)*self.stdvs[i]*design[:,i]+self.means[i]-k2*self.stdvs[i]
            if self.flags[i]=='S':
                #u[0,1]-->[mu-kmin*s,mu-kl*s]への写像
                u[:,i]=(k2-k1)*self.stdvs[i]*design[:,i]+self.means[i]+k1*self.stdvs[i]
            rnd=u
        t=(np.sign(self.g(rnd))+1)/2
        return rnd,t       
        
                     
