import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
plt.rcParams.update({'legend.fontsize': 'xx-large',
    'axes.labelsize': '24',
    'axes.titlesize':'xx-large',
    'xtick.labelsize':'xx-large',
    'ytick.labelsize':'xx-large',
    'figure.autolayout': True,
    'text.usetex'      : False})



def get_plot_subroutine(params):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    xs = params['loggs']['additional'][params['xsname']]
    for algo in params['loggs']['additional']['algonames']:
        if params['flag_bars']==True:
            ys_lb  = np.asarray([np.percentile(params['loggs'][algo]['time'][i,:],25) for i in range(len(xs))])
            ys_ub  = np.asarray([np.percentile(params['loggs'][algo]['time'][i,:],75) for i in range(len(xs))])
            ax.fill_between(xs, ys_lb, ys_ub, alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848')
        ys     = np.asarray([np.percentile(params['loggs'][algo][params['logname']][i,:],50) for i in range(len(xs))])
        ax.plot(xs, ys,label=algo)

    ax.legend(loc='best', bbox_to_anchor=(0.5, 1.05), ncol=3)
    plt.ylabel(params['ylab'])
    plt.xlabel(params['xlab'])
    plt.legend(loc='best')
    plt.xlim(params['xlims'])

    if params['flag_savefig'] == True:
        plt.savefig(params['fname'])  
    plt.show()


def get_plots(fname=None,flag_savefig=False,xlim=5001,loggs=None,xsname='prodList',xlab='Number of Products'):

    #Load data
    if fname is None and loggs is None:
        print 'No data or pickle filename supplied.'
        return 0
    elif fname is not None:
        loggs = pickle.load(open(fname,'rb'))
    else:
        fname = 'undefined0000'#generic
    # print loggs['additional']['N']

    ####plot1
    params = {'fname':fname[:-4]+'_time.png','flag_savefig':flag_savefig,'xlims':[0,xlim],
        'loggs':loggs,'flag_bars':False,'xlab':xlab,'ylab':'Time (s)','logname':'time','xsname':xsname}
    get_plot_subroutine(params)


    ###plot2
    params = {'fname':fname[:-4]+'_revPctErr.png','flag_savefig':flag_savefig,'xlims':[0,xlim],
        'loggs':loggs,'flag_bars':False,'xlab':xlab,'ylab':'Pct. Err. in Revenue','logname':'revPctErr','xsname':xsname}
    get_plot_subroutine(params)


    ###plot3
    params = {'fname':fname[:-4]+'_setOlp.png','flag_savefig':flag_savefig,'xlims':[0,xlim],
        'loggs':loggs,'flag_bars':False,'xlab':xlab,'ylab':'Pct. Set Overlap','logname':'setOlp','xsname':xsname}
    get_plot_subroutine(params)


    ###plot4
    # params = {'fname':fname[:-4]+'_corrSet.png','flag_savefig':flag_savefig,'xlims':[0,xlim],
    #     'loggs':loggs,'flag_bars':False,'xlab':xlab,'ylab':'Pct. Correct Set Output','logname':'corrSet','xsname':xsname}
    # get_plot_subroutine(params)



if __name__ == '__main__':


    fname = './output/gen_loggs_synthetic_lenF_400_20170525_1155PM.pkl'
    xlim = 401
    xsname = 'lenFeasibles'
    xlab = 'Number of Assortments'

    get_plots(fname,flag_savefig=True,xlim=xlim,xsname=xsname,xlab=xlab)