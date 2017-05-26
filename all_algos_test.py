import numpy as np
import time, pprint, pickle, datetime, random, os, copy
from plots_paper import get_plots

# Importing Algorithms
from capAst_paat import capAst_paat
from capAst_LP import capAst_LP
from capAst_adxopt import capAst_adxopt
from capAst_scikitLSH import capAst_AssortExact, capAst_AssortLSH, preprocess

def get_real_prices(price_range, prod, iterNum = 0):
  fname = os.getcwd() + '/billion_price_data/processed_data/usa_2/numProducts_stats.npz'
  dateList = np.load(fname)['good_dates']
  fileName = os.getcwd() + '/billion_price_data/processed_data/usa_2/prices_'
  fileNameList = []
  for chosenDay in dateList:
    fileNameList.append(fileName+ chosenDay+'.npz')

  allPrices = np.load(fileNameList[iterNum])['arr_0']
  allValidPrices = allPrices[allPrices < price_range]
  p = random.sample(allValidPrices, prod)
  return p 

def generate_instance(price_range,prod,genMethod,iterNum):
  if genMethod=='bppData':
    p = get_real_prices(price_range, prod, iterNum)
  else:
    p = price_range * np.random.beta(2,5,prod) 
  p = np.around(p, decimals =2)
  p = np.insert(p,0,0) #inserting 0 as the first element to denote the price of the no purchase option
  
  #generating the customer preference vector
  v = np.random.rand(prod+1) #v is a prod+1 length vector as the first element signifies the customer preference for the no purchase option
  v = np.around(v, decimals =7)                
  #Ensure that there are no duplicate entires in v - required for Paat's algorithm
  u, indices = np.unique(v, return_inverse=True)   
  ct = 1
  while(not(len(u)== prod+1) or v[0]==0):
      if v[0]==0:
        v[0] = np.random.rand(1)
        u, indices = np.unique(v, return_inverse=True) 
      #print len(u)
      extraSize = prod+1 - len(u)
      newEnt = np.random.rand(extraSize)
      newEnt = np.around(newEnt, decimals =2) 
      v= np.concatenate((u,newEnt))
      u, indices = np.unique(v, return_inverse=True)
      ct =ct+1
  # print 'Number of times v had to be generated', ct

  return p,v

def get_log_dict(prodList,N,algos,price_range,eps,genMethod,C=None):

  def matrices(prodList,N):
    names1 = ['revPctErr','setOlp','corrSet','rev','time']
    names2 = ['corrSet_mean', 'setOlp_mean',  'revPctErr_max', 'revPctErr_mean','revPctErr_std', 'time_mean', 'time_std'] 
    output = {}
    for name in names1:
     output[name] = np.zeros((np.shape(prodList)[0], N))
    for name in names2: 
      output[name] = np.zeros( np.shape(prodList)[0]) 
    return output

  loggs = {}
  loggs['additional'] = {'prodList':prodList,'algonames':algos.keys(),'N':N,'eps':eps,'price_range':price_range,'genMethod':genMethod}
  if C is not None:
    loggs['additional']['C'] = C
  else:
    loggs['additional']['C'] = np.zeros((np.shape(prodList)[0], N))

  for algoname in algos:
    loggs[algoname] = matrices(prodList,N)

    loggs[algoname]['maxSet'] = {}

  return loggs

def compute_summary_stats(algos,loggs,benchmark,i):
  for algoname in algos:
    # print algoname
    if benchmark in algos:
      loggs[algoname]['revPctErr'][i] = (loggs[benchmark]['rev'][i,:] - loggs[algoname]['rev'][i,:])/(loggs[benchmark]['rev'][i,:]+1e-6)
      loggs[algoname]['revPctErr_mean'][i] = np.mean(loggs[algoname]['revPctErr'][i,:])
      loggs[algoname]['revPctErr_std'][i] = np.std(loggs[algoname]['revPctErr'][i,:])
      loggs[algoname]['revPctErr_max'][i] = np.max(loggs[algoname]['revPctErr'][i,:])
    loggs[algoname]['corrSet_mean'][i] = np.mean(loggs[algoname]['corrSet'][i,:])
    loggs[algoname]['setOlp_mean'][i] = np.mean(loggs[algoname]['setOlp'][i,:])
    loggs[algoname]['time_mean'][i] = np.mean(loggs[algoname]['time'][i,:])
    loggs[algoname]['time_std'][i] = np.std(loggs[algoname]['time'][i,:])

  return loggs

def compute_overlap_stats(benchmark,algos,loggs,i,t,badError,maxSetBenchmark,eps):

  def overlap(maxSet,maxSetBenchmark):
    setOlp  = len(maxSetBenchmark.intersection(maxSet))
    corrSet = int(setOlp==  len(maxSetBenchmark))
    setOlp  = setOlp*1.0/len(maxSetBenchmark) #to normalize
    return setOlp,corrSet

  if benchmark in algos:
    for algoname in algos:
      # print 'Collecting benchmarks for ',algoname
      loggs[algoname]['setOlp'][i,t],loggs[algoname]['corrSet'][i,t] = overlap(loggs[algoname]['maxSet'][(i,t)],maxSetBenchmark)
      if(loggs[benchmark]['rev'][i,t] - loggs[algoname]['rev'][i,t] > eps ):
          badError = badError +1
  return loggs,badError


def main():

  #parameters required
  flag_savedata = True
  np.random.seed(1000)
  C           = 50        #capacity of assortment
  price_range = 1000      #denotes highest possible price of a product
  eps         = 0.1       #tolerance
  N           = 14 #30 #   #number of times Monte Carlo simulation will run
  prodList    = [100,400,5000] #[100, 200, 400, 600, 800, 1000,5000,10000] #
  genMethod   = 'synthetic' #'bppData' #
  algos = {'Assort-Exact':capAst_AssortExact,'Assort-LSH':capAst_AssortLSH,'Adxopt':capAst_adxopt,'LP':capAst_LP}#,'Static-MNL':capAst_paat}
  benchmark = 'LP'#'Static-MNL'#


  loggs = get_log_dict(prodList,N,algos,price_range,eps,genMethod,C)
  badError = 0
  t1= time.time()
  for i,prod in enumerate(prodList):
      
    t0 = time.time()
    t = 0
    while(t<N):

      print 'Iteration number is ', str(t+1),' of ',N,', for prod size ',prod

      #generating the price 
      p,v = generate_instance(price_range,prod,genMethod,t)

      meta = {'eps':eps}
      if 'Assort-Exact' in algos:
        meta['db_exact'],_,meta['normConst'] = preprocess(prod, C, p, 'special_case_exact')
      if 'Assort-LSH' in algos:
        meta['db_LSH'],_,_ = preprocess(prod, C, p, 'special_case_LSH', nEst=20,nCand=80)#Hardcoded values

      #run algos
      maxSetBenchmark = None
      for algoname in algos:
        loggs[algoname]['rev'][i,t],loggs[algoname]['maxSet'][(i,t)],loggs[algoname]['time'][i,t] = algos[algoname](prod,C,p,v,meta)
        print '\tExecuted ',algoname,' in ',loggs[algoname]['time'][i,t],'sec.'

        if algoname==benchmark:
          maxSetBenchmark = copy.deepcopy(loggs[algoname]['maxSet'][(i,t)])

      loggs,badError = compute_overlap_stats(benchmark,algos,loggs,i,t,badError,maxSetBenchmark,eps)

      t = t+1    
      

    
    print 'Experiments (',N,' sims) for number of products ',prod, ' is done.'  
    print 'Cumulative time taken is', time.time() - t0,'\n'   
    loggs = compute_summary_stats(algos,loggs,benchmark,i)

    #dump it incrementally for each product size
    if flag_savedata == True:
      pickle.dump(loggs,open('./output/cap_loggs_'+genMethod+'_'+str(prod)+'_'+datetime.datetime.now().strftime("%Y%m%d_%I%M%p")+'.pkl','wb'))

  print '\nAll experiments done. Total time taken is', time.time()  - t1,'\n\n'
  print "Summary:"
  for algoname in algos:
    print '\t',algoname,'time_mean',loggs[algoname]['time_mean']
    print '\t',algoname,'revPctErr_mean',loggs[algoname]['revPctErr_mean']

  return loggs

if __name__=='__main__':
  loggs = main()
  # get_plots(fname=None,flag_savefig=False,xlim=5001,loggs=loggs)