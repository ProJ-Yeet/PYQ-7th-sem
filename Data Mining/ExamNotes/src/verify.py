# -*- coding: utf-8 -*-
"""PHASE 2 cross-check: recompute every published numerical answer from scratch
and compare with what the notes claim. Any FAIL is a real error in the PDFs."""
import math, itertools
from collections import Counter

fails, checks = [], 0

def chk(label, got, want, tol=5e-3):
    global checks
    checks += 1
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) else (got == want)
    if not ok:
        fails.append(f"FAIL {label}: got {got!r}, notes say {want!r}")

def chks(label, got, want):
    global checks
    checks += 1
    if set(got) != set(want):
        fails.append(f"FAIL {label}:\n     got  {sorted(got)}\n     want {sorted(want)}")

# ===================== CH2 =====================
v = [200, 300, 400, 600, 1000]
mn, mx = min(v), max(v)
chk("2 minmax 300", (300-mn)/(mx-mn), 0.125)
chk("2 minmax 600", (600-mn)/(mx-mn), 0.5)
mean = sum(v)/len(v); chk("2 mean", mean, 500)
sig = math.sqrt(sum((x-mean)**2 for x in v)/len(v)); chk("2 sigma_pop", sig, 282.84, 0.01)
chk("2 z(200)", (200-mean)/sig, -1.0607, 1e-3)
chk("2 z(1000)", (1000-mean)/sig, 1.7678, 1e-3)
sam = math.sqrt(sum((x-mean)**2 for x in v)/(len(v)-1)); chk("2 s_sample", sam, 316.23, 0.01)
chk("2 decimal j", 4, 4)          # 1000/10^3 = 1 not <1
chk("2 decscale 1000", 1000/10**4, 0.1)

# PCA: Sigma = [[1,-2,0],[-2,5,0],[0,0,2]]
l1 = 3 + 2*math.sqrt(2); l3 = 3 - 2*math.sqrt(2)
chk("2 PCA l1", l1, 5.8284, 1e-3); chk("2 PCA l3", l3, 0.1716, 1e-3)
chk("2 PCA trace", l1 + 2 + l3, 8.0, 1e-9)
chk("2 PCA pct1", l1/8*100, 72.86, 0.02)
chk("2 PCA pct3", l3/8*100, 2.14, 0.02)
# eigenvector for l1: v2 = -(l1-1)/2 * v1
r = -(l1-1)/2; n = math.hypot(1, r)
chk("2 PCA e1x", 1/n, 0.3827, 1e-3); chk("2 PCA e1y", r/n, -0.9239, 1e-3)

O = {1:(4,56,7,10), 2:(3,53,8,11), 3:(7,58,6,9), 4:(9,55,7,12)}
def euc(a,b): return math.dist(a,b)
def cos(a,b):
    return sum(x*y for x,y in zip(a,b))/(math.dist(a,(0,)*len(a))*math.dist(b,(0,)*len(b)))
chk("2 euc(O1,O3)", euc(O[1],O[3]), 3.873, 1e-3)
chk("2 euc(O1,O4)", euc(O[1],O[4]), 5.477, 1e-3)
chk("2 cos(O2,O4)", cos(O[2],O[4]), 0.9944, 1e-3)
chk("2 cos d1d2", cos((4,1,2,0,2,0,0),(2,1,3,0,1,1,1)), 0.8246, 1e-3)
chk("2 cos D1D2", cos((4,0,2,0,1),(2,0,0,2,2)), 0.6299, 5e-5)
P_,Q_ = (0,0,1,1,0,1),(1,1,1,1,0,1)
q = sum(1 for a,b in zip(P_,Q_) if a==1 and b==1)
rr= sum(1 for a,b in zip(P_,Q_) if a==1 and b==0)
s = sum(1 for a,b in zip(P_,Q_) if a==0 and b==1)
t = sum(1 for a,b in zip(P_,Q_) if a==0 and b==0)
chk("2 Jaccard PQ", q/(q+rr+s), 0.6); chk("2 SMC PQ", (q+t)/6, 0.6667, 1e-3)
# Manhattan / supremum P1(6,3) P2(2,2) P3(3,4)
pts={1:(6,3),2:(2,2),3:(3,4)}
man=lambda a,b: sum(abs(x-y) for x,y in zip(a,b))
sup=lambda a,b: max(abs(x-y) for x,y in zip(a,b))
chk("2 man12", man(pts[1],pts[2]), 5); chk("2 man13", man(pts[1],pts[3]), 4)
chk("2 man23", man(pts[2],pts[3]), 3)
chk("2 sup12", sup(pts[1],pts[2]), 4); chk("2 sup13", sup(pts[1],pts[3]), 3)
chk("2 sup23", sup(pts[2],pts[3]), 2)
# 80 Ba binary
ram,lax,shy = (1,0,1,0),(1,1,0,0),(0,1,0,1)
def qrst(a,b):
    return (sum(1 for x,y in zip(a,b) if x==1 and y==1), sum(1 for x,y in zip(a,b) if x==1 and y==0),
            sum(1 for x,y in zip(a,b) if x==0 and y==1), sum(1 for x,y in zip(a,b) if x==0 and y==0))
Q,R,S,T = qrst(ram,lax); chk("2 Jaccard(Ram,Laxmi)", Q/(Q+R+S), 1/3, 1e-3)
Q,R,S,T = qrst(ram,shy); chk("2 SMC(Ram,Shyam)", (Q+T)/4, 0.0)
lb,sb = (0,0,0),(1,0,1)   # Laxmi/Shyam symmetric binary
Q,R,S,T = qrst(lb,sb); chk("2 d(Laxmi,Shyam)", (R+S)/(Q+R+S+T), 2/3, 1e-3)
# binning practice
d=[4,8,9,15,21,21,24,25,26,28,29,34]
b=[d[0:4],d[4:8],d[8:12]]
chk("2 bin1 mean", sum(b[0])/4, 9); chk("2 bin2 mean", sum(b[1])/4, 22.75)
chk("2 bin3 mean", sum(b[2])/4, 29.25)
chk("2 eqwidth W", (max(d)-min(d))/3, 10)
chk("2 minmax income", (73600-12000)/(98000-12000), 0.716, 1e-3)
chk("2 minmax income [-1,1]", (73600-12000)/(98000-12000)*2-1, 0.432, 1e-3)

# ===================== CH3 =====================
DS = [("youth","high","no","fair","no"),("youth","high","no","excellent","no"),
      ("middle","high","no","fair","yes"),("senior","medium","no","fair","yes"),
      ("senior","low","yes","fair","yes"),("senior","low","yes","excellent","no"),
      ("middle","low","yes","excellent","yes"),("youth","medium","no","fair","no"),
      ("youth","low","yes","fair","yes"),("senior","medium","yes","fair","yes"),
      ("youth","medium","yes","excellent","yes"),("middle","medium","no","excellent","yes"),
      ("middle","high","yes","fair","yes"),("senior","medium","no","excellent","no")]
def info(rows):
    c = Counter(r[-1] for r in rows); n = len(rows)
    return -sum((v/n)*math.log2(v/n) for v in c.values() if v)
def gain(rows, i):
    n = len(rows); tot = 0
    for val in set(r[i] for r in rows):
        sub = [r for r in rows if r[i]==val]; tot += len(sub)/n*info(sub)
    return info(rows) - tot
chk("3 Info(D)", info(DS), 0.940, 1e-3)
chk("3 Gain(age)", gain(DS,0), 0.246, 1e-3)
chk("3 Gain(income)", gain(DS,1), 0.029, 1e-3)
chk("3 Gain(student)", gain(DS,2), 0.151, 1e-3)
chk("3 Gain(credit)", gain(DS,3), 0.048, 1e-3)
# gini
def gini(rows):
    c=Counter(r[-1] for r in rows); n=len(rows); return 1-sum((v/n)**2 for v in c.values())
chk("3 Gini(D)", gini(DS), 0.459, 1e-3)
g1=[r for r in DS if r[1] in ("low","medium")]; g2=[r for r in DS if r[1]=="high"]
chk("3 GiniA income", gini(DS)-(len(g1)/14*gini(g1)+len(g2)/14*gini(g2)), 0.016, 1e-3)
a1=[r for r in DS if r[0] in ("youth","senior")]; a2=[r for r in DS if r[0]=="middle"]
chk("3 GiniA age", gini(DS)-(len(a1)/14*gini(a1)+len(a2)/14*gini(a2)), 0.102, 1e-3)
# naive bayes 72 Ch
yes=[r for r in DS if r[-1]=="yes"]; no=[r for r in DS if r[-1]=="no"]
X=("youth","medium","yes","fair")
def pxc(sub):
    p=1.0
    for i,val in enumerate(X): p *= sum(1 for r in sub if r[i]==val)/len(sub)
    return p
py=pxc(yes)*len(yes)/14; pn=pxc(no)*len(no)/14
chk("3 NB P(X|yes)", pxc(yes), 0.0439, 1e-3); chk("3 NB P(X|no)", pxc(no), 0.0192, 1e-3)
chk("3 NB yes*prior", py, 0.028, 1e-3); chk("3 NB no*prior", pn, 0.007, 1e-3)
# KNN 80 Bh
tr=[(5.1,3.5,1.4,0.2,'setosa'),(4.9,3,1.4,0.2,'setosa'),(4.7,3.2,1.3,0.2,'setosa'),
    (6,2.2,4,1,'versicolor'),(6.1,2.9,4.7,1.4,'versicolor'),(5.6,2.9,3.6,1.3,'versicolor'),
    (6.7,3.1,4.4,1.4,'versicolor')]
qy=(7,3.2,4.7,1.4)
ds=sorted((math.dist(qy,t[:4]), i+1, t[4]) for i,t in enumerate(tr))
chk("3 KNN d7", ds[0][0], 0.436, 1e-3); chk("3 KNN d5", ds[1][0], 0.949, 1e-3)
chk("3 KNN d4", ds[2][0], 1.628, 1e-3)
chks("3 KNN top3 ids", [x[1] for x in ds[:3]], [7,5,4])
# confusion matrices
def met(TP,FN,FP,TN):
    P,N=TP+FN,FP+TN
    return dict(acc=(TP+TN)/(P+N), sens=TP/P, spec=TN/N, prec=TP/(TP+FP), fpr=FP/N)
m=met(142,40,98,720)  # 74 Ch rows=actual
chk("3 74Ch acc",m['acc'],0.862,1e-3); chk("3 74Ch sens",m['sens'],0.780,1e-3)
chk("3 74Ch prec",m['prec'],0.592,1e-3); chk("3 74Ch spec",m['spec'],0.880,1e-3)
m=met(142,98,40,720)  # 78 Bh rows=predicted -> FN/FP swap
chk("3 78Bh acc",m['acc'],0.862,1e-3); chk("3 78Bh tpr",m['sens'],0.592,1e-3)
chk("3 78Bh prec",m['prec'],0.780,1e-3); chk("3 78Bh fpr",m['fpr'],0.053,1e-3)
m=met(21,6,7,41);  chk("3 75Ash acc",m['acc'],0.827,1e-3); chk("3 75Ash sens",m['sens'],0.778,1e-3)
chk("3 75Ash spec",m['spec'],0.854,1e-3); chk("3 75Ash prec",m['prec'],0.750,1e-3)
m=met(21,7,6,41);  chk("3 72Ch sens",m['sens'],0.750,1e-3); chk("3 72Ch prec",m['prec'],0.778,1e-3)
chk("3 72Ch spec",m['spec'],0.872,1e-3)
m=met(25,9,4,31);  chk("3 74Ash acc",m['acc'],0.812,1e-3); chk("3 74Ash sens",m['sens'],0.735,1e-3)
chk("3 74Ash spec",m['spec'],0.886,1e-3); chk("3 74Ash prec",m['prec'],0.862,1e-3)
m=met(1050,150,250,950)
chk("3 80Ba err",1-m['acc'],0.167,1e-3); chk("3 80Ba sens",m['sens'],0.875,1e-3)
chk("3 80Ba far",m['fpr'],0.208,1e-3); chk("3 80Ba spec",m['spec'],0.792,1e-3)
m=met(20,5,10,40); chk("3 73Shr tpr",m['sens'],0.80,1e-3); chk("3 73Shr fpr",m['fpr'],0.20,1e-3)
chk("3 73Shr prec",m['prec'],0.667,1e-3)
act="AABBBAAABB"; Y="AAAABBAAAB"
TP=sum(1 for a,b in zip(act,Y) if a=='A' and b=='A'); FN=sum(1 for a,b in zip(act,Y) if a=='A' and b=='B')
FP=sum(1 for a,b in zip(act,Y) if a=='B' and b=='A'); TN=sum(1 for a,b in zip(act,Y) if a=='B' and b=='B')
chks("3 70Ch Y counts",[TP,FN,FP,TN],[4,1,3,2])
m=met(TP,FN,FP,TN)
chk("3 70Ch Y acc",m['acc'],0.60,1e-3); chk("3 70Ch Y prec",m['prec'],0.571,1e-3)
chk("3 70Ch Y tpr",m['sens'],0.80,1e-3); chk("3 70Ch Y fpr",m['fpr'],0.60,1e-3)

# ===================== CH4 =====================
def apriori(txns, minsup):
    items = sorted({i for t in txns for i in t}); L, k = {}, 1
    cur = [frozenset([i]) for i in items]
    while cur:
        cnt = {c: sum(1 for t in txns if c <= t) for c in cur}
        Lk = {c: v for c, v in cnt.items() if v >= minsup}
        if not Lk: break
        L.update(Lk); prev = list(Lk)
        cur = set()
        for a, b in itertools.combinations(prev, 2):
            u = a | b
            if len(u) == k + 1 and all(frozenset(s) in Lk for s in itertools.combinations(u, k)):
                cur.add(u)
        cur = list(cur); k += 1
    return L
T80bh=[set("FACDGIMPN"),set("ABCDFLMOP"),set("BFHVJOP"),set("BCKSAV"),
       set("LAFCEPMNV"),set("IBAPSM"),set("FACIBAP")]
L=apriori(T80bh,4)
chks("4 80Bh L1",[ "".join(sorted(s)) for s in L if len(s)==1],["A","B","C","F","M","P"])
chks("4 80Bh L4",[ "".join(sorted(s)) for s in L if len(s)==4],["ACFP"])
chk("4 80Bh ACFP sup", L[frozenset("ACFP")], 4)
chks("4 80Bh L3",[ "".join(sorted(s)) for s in L if len(s)==3],
     ["ACF","ACP","AFP","AMP","CFP"])
T80ba=[set("ACD"),set("BCE"),set("ABCE"),set("BE")]
L=apriori(T80ba,2)
chks("4 80Ba L2",["".join(sorted(s)) for s in L if len(s)==2],["AC","BC","BE","CE"])
chks("4 80Ba L3",["".join(sorted(s)) for s in L if len(s)==3],["BCE"])
T70ch=[set("ACD"),set("BD"),set("ABCE"),set("BDF")]
L=apriori(T70ch,2)
chks("4 70Ch L2",["".join(sorted(s)) for s in L if len(s)==2],["AC","BD"])
T79bh=[set("AB"),set("AD"),set("AC"),set("BE"),set("BDE"),set("AEC")]
L=apriori(T79bh,3)
chks("4 79Bh L1",["".join(sorted(s)) for s in L if len(s)==1],["A","B","E"])
chks("4 79Bh L2 empty",["".join(sorted(s)) for s in L if len(s)==2],[])
L=apriori(T79bh,2)
chks("4 79Bh L2 @33%",["".join(sorted(s)) for s in L if len(s)==2],["AC","BE"])
Tff=[{"M1","M2","M5"},{"M2","M4"},{"M2","M3"},{"M1","M2","M4"},{"M1","M3"},
     {"M2","M3"},{"M1","M3"},{"M1","M2","M3","M5"},{"M1","M2","M3"}]
L=apriori(Tff,2)
chks("4 76Ch L3",[",".join(sorted(s)) for s in L if len(s)==3],
     ["M1,M2,M3","M1,M2,M5"])
chk("4 76Ch conf M1M5->M2", L[frozenset({"M1","M2","M5"})]/L[frozenset({"M1","M5"})], 1.0)
chk("4 76Ch conf M1M2->M5", L[frozenset({"M1","M2","M5"})]/L[frozenset({"M1","M2"})], 0.5)
Tmk=[set("MONKEY"),set("DONKEY"),set("MAKE"),set("MUCKY"),set("COOKIE")]
L=apriori(Tmk,3)
chks("4 81Ba frequent",["".join(sorted(s)) for s in L],
     ["K","E","M","O","Y","EK","KM","KO","EO","KY","EKO"])
chk("4 81Ba KEO sup", L[frozenset("KEO")], 3)
chk("4 81Ba conf K->E", L[frozenset("KE")]/L[frozenset("K")], 0.8)
chk("4 81Ba conf E->O", L[frozenset("EO")]/L[frozenset("E")], 0.75)
# lift / chi-square
sup_ab, sup_a, sup_b = 0.40, 0.60, 0.75
chk("4 lift game/video", sup_ab/(sup_a*sup_b), 0.89, 5e-3)
obs=[4000,3500,2000,500]; exp=[4500,3000,1500,1000]
chk("4 chi2", sum((o-e)**2/e for o,e in zip(obs,exp)), 555.6, 0.1)

# ===================== CH5 =====================
def kmeans(pts, seeds, iters=30):
    C = list(seeds)
    for _ in range(iters):
        asg = [min(range(len(C)), key=lambda j: math.dist(p, C[j])) for p in pts]
        newC = []
        for j in range(len(C)):
            mem = [p for p, a in zip(pts, asg) if a == j]
            newC.append(tuple(sum(x)/len(mem) for x in zip(*mem)) if mem else C[j])
        if newC == C: return asg, C
        C = newC
    return asg, C
P6=[(1,2),(2.5,1),(3.5,1.5),(4,1),(3.5,2.5),(5,3)]
asg,C=kmeans(P6,[(1,2),(5,3)])
chks("5 78Bh cluster1",[i for i,a in enumerate(asg) if a==0],[0,1])
chk("5 78Bh c1x",C[0][0],1.75); chk("5 78Bh c1y",C[0][1],1.5)
chk("5 78Bh c2x",C[1][0],4.0);  chk("5 78Bh c2y",C[1][1],2.0)
asg2,C2=kmeans(P6,[(1,2),(2.5,1)])
chks("5 78Bh degenerate",[i for i,a in enumerate(asg2) if a==0],[0])
P75=[(1,2),(2.5,4.5),(4,6),(3.5,4),(4,5.5),(3,6)]
asg,C=kmeans(P75,[(1,2),(4,6)])
chks("5 75Ash c1",[i for i,a in enumerate(asg) if a==0],[0])
chk("5 75Ash c2x",C[1][0],3.4,1e-6); chk("5 75Ash c2y",C[1][1],5.2,1e-6)
P71=[(1,1),(1.5,2),(3,4),(5,7),(3.5,5),(4.5,5),(3.5,4.5)]
asg,C=kmeans(P71,[(1,1),(5,7)])
chk("5 71Shr c1x",C[0][0],1.25); chk("5 71Shr c1y",C[0][1],1.5)
chk("5 71Shr c2x",C[1][0],3.9,1e-6); chk("5 71Shr c2y",C[1][1],5.1,1e-6)
X76=[(5.9,3.2),(4.6,2.9),(6.2,2.8),(4.7,3.2),(5.5,4.2),(5.0,3.0),(4.9,3.1),(6.7,3.1),(5.1,3.8),(6.0,3.0)]
asg,C=kmeans(X76,[(6.2,3.2),(6.6,3.7),(6.5,3.0)])
Cs=sorted(C)
chk("5 76Ch red x",Cs[0][0],4.80,1e-6); chk("5 76Ch red y",Cs[0][1],3.05,1e-6)
chk("5 76Ch grn x",Cs[1][0],5.30,1e-6); chk("5 76Ch grn y",Cs[1][1],4.00,1e-6)
chk("5 76Ch blu x",Cs[2][0],6.20,1e-6); chk("5 76Ch blu y",Cs[2][1],3.025,1e-6)
# hierarchical
def hier(D0, labels, link):
    D={frozenset([a]):{} for a in labels}
    cl=[frozenset([a]) for a in labels]; dist={}
    for a,b in itertools.combinations(labels,2):
        dist[frozenset([frozenset([a]),frozenset([b])])]=D0[(a,b)] if (a,b) in D0 else D0[(b,a)]
    heights=[]
    while len(cl)>1:
        best=min(((v,k) for k,v in dist.items() if len(k)==2), key=lambda x:(x[0],))
        h,key=best; x,y=tuple(key); new=x|y; heights.append(round(h,4))
        cl=[c for c in cl if c not in (x,y)]
        for c in cl:
            d1=dist[frozenset([x,c])]; d2=dist[frozenset([y,c])]
            dist[frozenset([new,c])]=min(d1,d2) if link=='single' else max(d1,d2)
        for k in list(dist):
            if x in k or y in k: del dist[k]
        cl.append(new)
    return heights
lab=['p1','p2','p3','p4','p5','p6']
M={('p1','p2'):.24,('p1','p3'):.22,('p1','p4'):.37,('p1','p5'):.34,('p1','p6'):.23,
   ('p2','p3'):.15,('p2','p4'):.20,('p2','p5'):.14,('p2','p6'):.25,
   ('p3','p4'):.15,('p3','p5'):.28,('p3','p6'):.11,
   ('p4','p5'):.29,('p4','p6'):.22,('p5','p6'):.39}
chks("5 80Bh single heights", hier(M,lab,'single'), [0.11,0.14,0.15,0.15,0.22])
co={'p1':(0.40,0.53),'p2':(0.22,0.38),'p3':(0.35,0.32),'p4':(0.26,0.19),'p5':(0.08,0.41),'p6':(0.45,0.30)}
M2={(a,b): math.dist(co[a],co[b]) for a,b in itertools.combinations(lab,2)}
hh=hier(M2,lab,'complete')
for got,want in zip(hh,[0.102,0.143,0.219,0.342,0.386]):
    chk(f"5 80Ba complete {want}", got, want, 2e-3)
labA=['A','B','C','D','E','F']
M3={('A','B'):.12,('A','C'):.51,('A','D'):.84,('A','E'):.28,('A','F'):.34,
    ('B','C'):.25,('B','D'):.16,('B','E'):.77,('B','F'):.61,
    ('C','D'):.14,('C','E'):.70,('C','F'):.93,
    ('D','E'):.45,('D','F'):.20,('E','F'):.67}
chks("5 76Ch single", hier(M3,labA,'single'), [0.12,0.14,0.16,0.20,0.28])
chks("5 76Ch complete", hier(M3,labA,'complete'), [0.12,0.14,0.61,0.70,0.93])
# DBSCAN practice
DB=[(1,1),(1,2),(2,1),(8,8),(8,9),(25,25)]
eps,mp=2,3
cnt=[sum(1 for q in DB if math.dist(p,q)<=eps) for p in DB]
chks("5 dbscan counts", cnt, [3,3,3,2,2,1])
core=[i for i,c in enumerate(cnt) if c>=mp]
chks("5 dbscan core", core, [0,1,2])
noise=[i for i in range(len(DB)) if i not in core and
       not any(math.dist(DB[i],DB[j])<=eps for j in core)]
chks("5 dbscan noise", noise, [3,4,5])

# ===================== CH6 =====================
pA_I, pA_nI, pI = 0.99, 0.01, 0.01
chk("6 detection rate", pA_I, 0.99); chk("6 false alarm", pA_nI, 0.01)
bayes = pA_I*pI/(pA_I*pI + pA_nI*(1-pI))
chk("6 Bayesian detection", bayes, 0.50, 1e-9)
pI2=0.001; b2=pA_I*pI2/(pA_I*pI2+pA_nI*(1-pI2))
chk("6 rarer P(I|A)", b2, 0.090, 2e-3)
chk("6 TP on 10000", 0.99*100, 99); chk("6 FP on 10000", 0.01*9900, 99)
# DB(r,pi)
pts5=[(1,1),(1,2),(2,1),(2,2),(8,8)]
r_,pi_=2,0.4
frac=[sum(1 for q in pts5 if math.dist(p,q)<=r_)/len(pts5) for p in pts5]
chks("6 DB outliers", [i for i,f in enumerate(frac) if f<=pi_], [4])

# ---- M7 (NEW): central tendency, grouped median, quartiles, IQR, outliers ----
def grouped_median(L1, N, cum_below, freq_med, width):
    return L1 + (N / 2 - cum_below) / freq_med * width

# 7.1  PC salary table, 100 employees
f71 = [8, 15, 20, 32, 18, 7]
cum71, run = [], 0
for x in f71:
    run += x
    cum71.append(run)
chk("2 M7.1 N", sum(f71), 100)
chk("2 M7.1 cum below median interval", cum71[2], 43)
chk("2 M7.1 freq median", cum71[3] - cum71[2], 32)
# median interval = first interval whose cumulative freq reaches N/2
i71 = next(i for i, c in enumerate(cum71) if c >= sum(f71) / 2)
chk("2 M7.1 median interval index", i71, 3)
chk("2 M7.1 grouped median",
    grouped_median(40000, sum(f71), cum71[2], f71[3], 10000), 42187.50, 1e-6)

# 7.2  smaller table, N = 60
f72 = [5, 8, 12, 20, 10, 5]
chk("2 M7.2 N", sum(f72), 60)
chk("2 M7.2 grouped median",
    grouped_median(40, sum(f72), 5 + 8 + 12, f72[3], 10), 42.5, 1e-9)

# 7.3  mode from mean and median
chk("2 M7.3 mode approx", 3 * 55 - 2 * 60, 45)

# 7.4  Han & Kamber Example 2.6 dataset
d74 = [30, 36, 47, 50, 52, 52, 56, 60, 63, 70, 70, 110]
n74 = len(d74)
chk("2 M7.4 n", n74, 12)
chk("2 M7.4 sum", sum(d74), 696)
chk("2 M7.4 mean", sum(d74) / n74, 58.0, 1e-9)
chk("2 M7.4 median", (d74[5] + d74[6]) / 2, 54.0, 1e-9)
chk("2 M7.4 midrange", (min(d74) + max(d74)) / 2, 70.0, 1e-9)
cnt74 = Counter(d74)
top = max(cnt74.values())
chks("2 M7.4 modes", [v for v, c in cnt74.items() if c == top], [52, 70])
chk("2 M7.4 modality", top, 2)

# positional convention (Han & Kamber): 3rd, 6th, 9th sorted values
q1p, q2p, q3p = d74[2], d74[5], d74[8]
chk("2 M7.4 Q1 positional", q1p, 47)
chk("2 M7.4 Q3 positional", q3p, 63)
chk("2 M7.4 IQR positional", q3p - q1p, 16)

# interpolated convention: position of Qk = k(n+1)/4
def quartile_interp(data, k):
    pos = k * (len(data) + 1) / 4
    lo = int(pos)
    frac = pos - lo
    return data[lo - 1] + frac * (data[lo] - data[lo - 1])

q1i = quartile_interp(d74, 1)
q2i = quartile_interp(d74, 2)
q3i = quartile_interp(d74, 3)
chk("2 M7.4 Q1 interp", q1i, 47.75, 1e-9)
chk("2 M7.4 Q2 interp", q2i, 54.0, 1e-9)
chk("2 M7.4 Q3 interp", q3i, 68.25, 1e-9)
iqr_i = q3i - q1i
chk("2 M7.4 IQR interp", iqr_i, 20.5, 1e-9)
chk("2 M7.4 lower fence interp", q1i - 1.5 * iqr_i, 17.0, 1e-9)
chk("2 M7.4 upper fence interp", q3i + 1.5 * iqr_i, 99.0, 1e-9)
chks("2 M7.4 outliers interp",
     [x for x in d74 if x < q1i - 1.5 * iqr_i or x > q3i + 1.5 * iqr_i], [110])
# same verdict under the positional convention
chks("2 M7.4 outliers positional",
     [x for x in d74 if x < q1p - 1.5 * (q3p - q1p) or x > q3p + 1.5 * (q3p - q1p)], [110])
chk("2 M7.4 upper fence positional", q3p + 1.5 * (q3p - q1p), 87.0, 1e-9)
# five-number summary (interpolated)
chks("2 M7.4 five-number", [min(d74), q1i, q2i, q3i, max(d74)], [30, 47.75, 54.0, 68.25, 110])
# largest non-outlier, where the upper whisker stops
chk("2 M7.4 upper whisker", max(x for x in d74 if x <= q3i + 1.5 * iqr_i), 70)

# ---- chi-square test of independence, section 2.2(b) ----
obs = [[20, 30], [30, 20]]
rows = [sum(r) for r in obs]
cols = [sum(c) for c in zip(*obs)]
tot = sum(rows)
exp = [[rows[i] * cols[j] / tot for j in range(2)] for i in range(2)]
chk("2 chi2 grand total", tot, 100)
chk("2 chi2 E11", exp[0][0], 25.0, 1e-9)
chi2 = sum((obs[i][j] - exp[i][j]) ** 2 / exp[i][j] for i in range(2) for j in range(2))
chk("2 chi2 statistic", chi2, 4.0, 1e-9)
chk("2 chi2 df", (2 - 1) * (2 - 1), 1)
chk("2 chi2 reject H0", chi2 > 3.841, True)

# ===================== CH7 =====================
inl={'A':['C'],'B':['A'],'C':['A','B','D'],'D':[]}
C_={'A':2,'B':1,'C':1,'D':1}
pr={k:0.25 for k in 'ABCD'}; d=0.85
snap=[]
for _ in range(5):
    pr={p: (1-d)+d*sum(pr[t]/C_[t] for t in inl[p]) for p in 'ABCD'}
    snap.append(dict(pr))
chk("7 PR A it1", snap[0]['A'], 0.3625, 1e-4)
chk("7 PR C it1", snap[0]['C'], 0.6813, 1e-4)
chk("7 PR A it5", snap[4]['A'], 0.9718, 1e-3)
chk("7 PR B it5", snap[4]['B'], 0.5193, 1e-3)
chk("7 PR C it5", snap[4]['C'], 1.0280, 1e-3)
chk("7 PR D it5", snap[4]['D'], 0.15, 1e-9)
chks("7 PR ranking", sorted('ABCD', key=lambda k:-snap[4][k]), ['C','A','B','D'])
# exact fixed point
for _ in range(400):
    pr={p:(1-d)+d*sum(pr[t]/C_[t] for t in inl[p]) for p in 'ABCD'}
chk("7 PR fixed A", pr['A'], 1.490, 2e-3); chk("7 PR fixed C", pr['C'], 1.577, 2e-3)
chk("7 PR fixed B", pr['B'], 0.783, 2e-3)
chk("7 PR sum = N", sum(pr.values()), 4.0, 1e-3)
# normalised form
pr2={k:0.25 for k in 'ABCD'}; N=4
pr2={p:(1-d)/N + d*sum(pr2[t]/C_[t] for t in inl[p]) for p in 'ABCD'}
chk("7 PRnorm A it1", pr2['A'], 0.2500, 1e-3)
chk("7 PRnorm C it1", pr2['C'], 0.5688, 1e-3)
chk("7 PRnorm sum", sum(pr2.values()), 1.0, 2e-3)


# ===================== 2026-09 MERGE: the six new papers =====================
# 82 Bh Q5 -- DBSCAN, eps 2, MinPts 2 (the point counts itself)
pts = {'A':(2,10),'B':(2,5),'C':(8,4),'D':(5,8),'E':(7,5),'F':(6,4),'G':(1,2),'H':(4,9)}
nb = {k: [j for j,w in pts.items() if math.dist(v,w) <= 2] for k,v in pts.items()}
core = sorted(k for k in pts if len(nb[k]) >= 2)
chks("82Bh DBSCAN core", core, ['C','D','E','F','H'])
chks("82Bh DBSCAN noise", sorted(k for k in pts if len(nb[k]) < 2), ['A','B','G'])
chk("82Bh DBSCAN C-F is exactly eps", math.dist(pts['C'],pts['F']), 2.0, 1e-9)

# 82 Bh Q6 -- K-means k=2 seeded (1,2),(6,4)
def kmeans(P, C, dist=math.dist, iters=25):
    for _ in range(iters):
        a = [min(range(len(C)), key=lambda i: dist(p,C[i])) for p in P]
        n = [tuple(sum(p[d] for p,x in zip(P,a) if x==i)/max(1,a.count(i))
                   for d in range(len(P[0]))) for i in range(len(C))]
        if n == C: return C, a
        C = n
    return C, a
C,a = kmeans([(1,2),(1.5,1),(3.5,1.5),(4,3),(3.5,2.5),(6,4)], [(1,2),(6,4)])
chk("82Bh kmeans c1x", C[0][0], 2.375); chk("82Bh kmeans c1y", C[0][1], 1.75)
chk("82Bh kmeans c2x", C[1][0], 5.0);   chk("82Bh kmeans c2y", C[1][1], 3.5)

# 81 Bh Q8 -- K-means from one given centroid; second seed = farthest point
P = [(2,3),(3,3),(6,8),(8,8),(7,5)]
chks("81Bh farthest seed", [max(P, key=lambda p: math.dist((2,3),p))], [(8,8)])
C,a = kmeans(P, [(2,3),(8,8)])
chk("81Bh kmeans c1x", C[0][0], 2.5); chk("81Bh kmeans c1y", C[0][1], 3.0)
chk("81Bh kmeans c2x", C[1][0], 7.0); chk("81Bh kmeans c2y", C[1][1], 7.0)

# 73 Ch Q7 -- 1-D K-means from {5,12,18} then SSE
x = [5,12,18,24,30,42,48]; c = [5,12,18]
for _ in range(25):
    a = [min(range(3), key=lambda i: abs(p-c[i])) for p in x]
    n = [sum(p for p,g in zip(x,a) if g==i)/max(1,a.count(i)) for i in range(3)]
    if n == c: break
    c = n
chks("73Ch 1d centroids", c, [5.0,18.0,40.0])
chk("73Ch SSE", sum((p-c[g])**2 for p,g in zip(x,a)), 240.0)

# 79 Ba Q8 -- K-means with MANHATTAN, 3 centres, stop after 3 iterations
xs = [5.9,4.6,6.2,4.7,5.5,5.0,4.9,6.7,5.1,6.0]
ys = [3.2,2.9,2.8,3.2,4.2,3.0,3.1,3.1,3.8,3.0]
P3 = list(zip(xs,ys)); C3 = [(6.2,3.2),(6.6,3.7),(6.5,3.0)]
man = lambda p,q: abs(p[0]-q[0])+abs(p[1]-q[1])
for _ in range(3):
    a = [min(range(3), key=lambda i: man(p,C3[i])) for p in P3]
    C3 = [(sum(p[0] for p,g in zip(P3,a) if g==i)/max(1,a.count(i)),
           sum(p[1] for p,g in zip(P3,a) if g==i)/max(1,a.count(i))) for i in range(3)]
chk("79Ba manhattan Ax", C3[0][0], 4.8, 1e-3); chk("79Ba manhattan Ay", C3[0][1], 3.05, 1e-3)
chk("79Ba manhattan Bx", C3[1][0], 5.3, 1e-3); chk("79Ba manhattan By", C3[1][1], 4.0, 1e-3)
chk("79Ba manhattan Cx", C3[2][0], 6.2, 1e-3); chk("79Ba manhattan Cy", C3[2][1], 3.025, 1e-3)

# ---- Apriori helper shared by the four new association numericals
def apri(trans, minc):
    L = {}; k = 1; cur = [frozenset([i]) for i in {i for t in trans for i in t}]
    while cur:
        keep = {c: sum(1 for t in trans if c <= t) for c in cur}
        keep = {c: n for c, n in keep.items() if n >= minc}
        if not keep: break
        L.update(keep); k += 1
        cur = [a | b for a, b in itertools.combinations(keep, 2)
               if len(a | b) == k and all(frozenset(s) in keep
                                          for s in itertools.combinations(a | b, k - 1))]
        cur = list(dict.fromkeys(cur))
    return L
def strong(L, mc):
    out = []
    for l, n in L.items():
        if len(l) < 2: continue
        for r in range(1, len(l)):
            for s in itertools.combinations(sorted(l), r):
                if n / L[frozenset(s)] >= mc:
                    out.append((tuple(sorted(s)), tuple(sorted(l - frozenset(s)))))
    return out

# 82 Bh Q4 -- min sup 60% of 5 = 3, min conf 80%
T = [set('ABCDEF'), set('BCDEFG'), set('ADEH'), set('ADFIJ'), set('BDEK')]
L = apri(T, 3)
chks("82Bh L1", [''.join(sorted(s)) for s in L if len(s)==1], ['A','B','D','E','F'])
chks("82Bh L2", [''.join(sorted(s)) for s in L if len(s)==2],
     ['AD','BD','BE','DE','DF'])
chks("82Bh L3", [''.join(sorted(s)) for s in L if len(s)==3], ['BDE'])
chk("82Bh strong rule count", len(strong(L, 0.80)), 9)

# 81 Bh Q7 -- min sup 50% of 4 = 2, min conf 65%
T = [{'MILK','BREAD','CAKE'}, {'BUTTER','BREAD','EGG'},
     {'MILK','BUTTER','BREAD','EGG'}, {'BUTTER','EGG'}]
L = apri(T, 2)
chk("81Bh L3 size", len([s for s in L if len(s)==3]), 1)
chk("81Bh all 14 rules strong", len(strong(L, 0.65)), 14)

# 73 Ch Q5 -- both thresholds 50%
T = [{'A','B','C'}, {'A','C'}, {'A','D'}, {'B','E','F'}]
L = apri(T, 2)
chks("73Ch L2", [''.join(sorted(s)) for s in L if len(s)==2], ['AC'])
chk("73Ch strong rules", len(strong(L, 0.50)), 2)

# 79 Ba Q5 -- 7 transactions, 20% -> count 2; rules DO exist
T = [{'A2','A4','A8'}, {'A4','A5','A7'}, {'A3'}, {'A5','A6','A7'},
     {'A2','A3','A4'}, {'A2','A6','A7','A9'}, {'A5'}]
L = apri(T, 2)
chks("79Ba L2", sorted(''.join(sorted(s)) for s in L if len(s)==2),
     ['A2A4','A5A7','A6A7'])
chk("79Ba rule count at conf 0", len(strong(L, 0.0)), 6)

# 79 Ba Q6 / 73 Ch Q4 -- confusion matrices
chk("79Ba accuracy",   (100+50)/165, 0.909, 1e-3)
chk("79Ba error rate", (10+5)/165,   0.091, 1e-3)
chk("79Ba sensitivity", 100/105,     0.952, 1e-3)
chk("79Ba specificity", 50/60,       0.833, 1e-3)
chk("79Ba precision",   100/110,     0.909, 1e-3)
chk("73Ch TPR rows-actual", 100/140, 0.714, 1e-3)
chk("73Ch FPR rows-actual", 60/360,  0.167, 1e-3)
chk("73Ch accuracy either way", 400/500, 0.800, 1e-9)

# 79 Ba Q2 -- binning depth 3, then the three normalisations of 35
v = [13,15,16,16,19,20,20,21,22,22,25,25,25,25,30,33,33,35,35,35,35,36,40,45,46,52,70]
chk("79Ba n", len(v), 27)
means = [sum(v[i:i+3])/3 for i in range(0, 27, 3)]
chk("79Ba bin1 mean", means[0], 14.67, 5e-3)
chk("79Ba bin9 mean", means[8], 56.0)
chk("79Ba minmax 35", (35-13)/(70-13), 0.386, 1e-3)
chk("79Ba mean", sum(v)/len(v), 29.963, 1e-3)
chk("79Ba zscore 35", (35-sum(v)/len(v))/12.94, 0.389, 1e-3)
chk("79Ba decimal 35", 35/100, 0.35)

# 82 Bh Q3 / 81 Bh Q5 -- ID3 gains
def H(*c):
    n = sum(c)
    return -sum((x/n)*math.log2(x/n) for x in c if x)
chk("82Bh Info(D)", H(6,3,5), 1.531, 1e-3)
chk("82Bh gain Income", H(6,3,5) - (4/14*H(4)+4/14*H(2,2)+6/14*H(1,5)), 0.966, 1e-3)
chk("82Bh gain CreditHistory",
    H(6,3,5) - (4/14*H(3,1)+5/14*H(2,1,2)+5/14*H(1,1,3)), 0.266, 1e-3)
chk("81Bh Info(D)", H(4,3,3), 1.571, 1e-3)
chk("81Bh gain TravelCost", H(4,3,3) - (5/10*H(4,1)+2/10*H(2)+3/10*H(3)), 1.210, 1e-3)
chk("81Bh Car and Income tie",
    H(4,3,3) - (3/10*H(2,1)+5/10*H(2,2,1)+2/10*H(2)),
    H(4,3,3) - (2/10*H(2)+5/10*H(2,2,1)+3/10*H(1,2)), 1e-9)

# ch3-num Problem 1.2 -- the Income-level gain that was printed as 0.971
chk("78Bh Info(D) 3-class", H(4,3,3), 1.571, 1e-3)
chk("78Bh gain Income (was wrong)",
    H(4,3,3) - (2/10*H(2)+6/10*H(2,1,3)+2/10*H(2)), 0.695, 1e-3)

print(f"checks run: {checks}")
print(f"failures  : {len(fails)}")
for f in fails: print(" ", f)
