 
'''
Testing
Function: Figuring out how to process Howie data
'''

'''
Things to do:
TODO: add dbm support for large dictionaries 
'''

""" LIBRARY IMPORTATION """
# standard libraries
import os
import sys
import gzip 
import csv
import cPickle as pickle
import dbm
from collections import Counter

# nonstandard libraries
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# homegrown libraries
from methods import * # libraries: madhype,alphabetr,pairseq


""" FACTORY METHODS """

def compare_lists(l1,l2):
    """ compares two lists of numerals looking for a match """
    l1.sort()
    l2.sort()
    matches = []
    i1,i2 = 0,0
    while not (i1 == len(l1) or i2 == len(l2)):
        if l1[i1] == l2[i2]:
            matches.append(l1[i1])
            i1 += 1
            i2 += 1
        elif l1[i1] > l2[i2]:
            i2 += 1
        else:
            i1 += 1
    #print 'I1/I2',i1,i2
    #print len(l1),len(l2)
    return matches

def listcommon(testlist,biglist):
    return list(set(testlist) & set(biglist))

def flatten(l):
    """ Flatten a list into a 1D list """
    return [item for sublist in l for item in sublist]

def dbm_save(my_dict,fname):
    db = dbm.open('./pickles/'+fname,'c')
    for k,v in my_dict.items():
        db[str(k)] = str(v) 
    db.close()

def dbm_load(fname):
    return dbm.open('./pickles/'+fname,'r')

def dbm_local(fname):
    db,my_dict = dbm.open('./pickles/'+fname,'r'),{}
    print 'Pulling dictionary {}...'.format(fname)
    for i,k in enumerate(db.keys()):
        my_dict[k] = db[k]
    print 'Finished!'
    return my_dict


def dbm_check(*fnames):
    """ Checks for presence of pag and dir files, returns boolean """
    pag_files = [os.path.isfile('./pickles/'+f+'.pag') for f in fnames]
    dir_files = [os.path.isfile('./pickles/'+f+'.dir') for f in fnames]
    val = all(pag_files + dir_files)
    # print out missing files
    if not val:
        print 'Following files not found:'
        for a,f in zip(pag_files+dir_files,[f+'.pag' for f in fnames]+[f+'.dir' for f in fnames]):
            if not a: print f
    return val


""" NOTES """
# According to Howie data notes:
# > cDNA refers to sample of origin assignments
# > gDNA refers to repertoire frequency measurements

def main(mode='coast2coast'):

    params = Parameters(default_parameters())

    if mode == 'coast2coast':
        custom_params = {
                        'max_threshold':None,
                        'pair_threshold':1,
                        'verbose':0,
                        'real_data':True,
                        'all_pairs':False,
                        'repertoire_adjustment':False,
                        'cores':8,
                        'skip_run':'exp1',
                        'record_hits':True,
                        'plot_auroc':False
                        }

        params.update(custom_params)


        ### directory assignments
        dirnameX = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectX'
        dirnameY = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectY'
        dirname_exp = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/experiment1'
        origin_dict = []

        ### analysis on presented data
        filesX,filesY = subjectXYdata(dirnameX,dirnameY) # returns dictionaries
        catalog_repertoire(filesX,filesY,overwrite=False) 
        data = data_assignment(dirname_exp,threshold=(4,91),overwrite=False,silent=False) # no save due to memory

        ### run analyis (mad-hype)
        startTime = datetime.now()
        
        #results_madhype = madhype.solve(data,pair_threshold=0.9,verbose=0,real_data=True,all_pairs=False,repertoire_adjustment=False,cores=8,skip_run='exp1')
        results_madhype = madhype.solve(data,custom_params=params.dict())
        pickle.dump(results_madhype,open('./pickles/results_{}.p'.format(dirname_exp[-1]),'wb'))
        print 'MAD-HYPE took {} seconds.\n'.format(datetime.now()-startTime)
        
        ### process results
        results = pickle.load(open('./pickles/results_{}.p'.format(dirname_exp[-1]),'r'))
        recordH,recordM,scoresH,scoresM = interpret_results(data,results_madhype,dirname_exp,params)

    elif mode == 'histograms':
        """ 
        This mode is for making a histogram of scores 
        """
        custom_params = {
                        'max_threshold':None,
                        'pair_threshold':1,
                        'verbose':0,
                        'real_data':True,
                        'all_pairs':False,
                        'repertoire_adjustment':False,
                        'cores':8,
                        'skip_run':'exp1',
                        'record_hits':True,
                        'plot_auroc':False
                        }

        params.update(custom_params)

        ### directory assignments
        dirnameX = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectX'
        dirnameY = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectY'
        dirname_exp = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/experiment1'

        ### analysis on presented data
        filesX,filesY = subjectXYdata(dirnameX,dirnameY) # returns dictionaries
        data = data_assignment(dirname_exp,threshold=(4,91),overwrite=False,silent=False) # no save due to memory

        ### run analyis (mad-hype)
        results_madhype = madhype.solve(data,custom_params=params.dict())
        
        ### process results
        recordH,recordM,scoresH,scoresM = interpret_results(data,results_madhype,dirname_exp,params)
        make_histogram(recordM,scoresM)
         
    
    elif mode == 'analysis':
        ### directory assignments

        ### EDIT BELOW ###
        dirnameX = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectX'
        dirnameY = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/subjectY'
        dirname_exp = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/experiment2'
        ### EDIT ABOVE ###

        data = data_assignment(dirname_exp,threshold=(5,91),overwrite=False,silent=False) # no save due to memory
        results = pickle.load(open('./pickles/results_{}.p'.format(dirname_exp[-1]),'r'))
        interpret_results(data,results,dirname_exp)
        

        ### process results
            
    elif mode == 'testing':
        fname_exp1 = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/experiment1'
        fname_exp2 = '/home/pholec/Dropbox (MIT)/MAD-HYPE/data/howie/experiment2'
        check_well_limits(fname_exp1)
        check_well_limits(fname_exp2)

def make_histogram(records,scores):
    ax = plt.figure()
    N,bins,patches = plt.hist(scores,bins=np.arange(1.,10.,0.2))

    for i,n in enumerate(N):
        valid_scores = [r for r,s in zip(records,scores) if s < bins[i+1] and s > bins[i]]
        acc = float(sum(valid_scores))/len(valid_scores)
        patches[i].set_facecolor(color_scale(acc,(0.5,1.0)))

    plt.yscale('log')
    plt.show(block=False)
    raw_input('Press enter to close...')
    plt.close()

def color_scale(val,vr):
    mid = 0.5*(vr[0] + vr[1])
    if val > mid:
        a = 2*(val-mid)/(vr[1]-vr[0])
        return [1.0,1.0,(1.-a)]
    else:
        a = min(-2*(val-mid)/(vr[1]-vr[0]),1)
        return [1.0,(1.-a),1.0]

        

def check_well_limits(dirname):
    
    with open(dirname + '/tcr_pairseq_fdr1pct.pairs','r') as f: 
        howie_results = [(a[1]).split(',') for i,a in enumerate(csv.reader(f, dialect="excel-tab")) if i != 0]
    #print howie_results[:10] 
    r = [len(h) for h in howie_results]
    print 'Dirname:'

def interpret_results(data,results,dirname,params={}):
    
    # prepare howie results
    with open(dirname + '/tcr_pairseq_fdr1pct.pairs','r') as f: 
        howie_results = [((a[0],a[2]),0.0,-float(a[5])) for i,a in enumerate(csv.reader(f, dialect="excel-tab")) if i != 0]

    # prepare madhype results
    results_ab = [(a,b,c,'AB') for a,b,c in zip(
        results['AB']['edges'],results['AB']['freqs'],results['AB']['scores'])]
    results_aa = [(a,b,c,'AA') for a,b,c in zip(
        results['AA']['edges'],results['AA']['freqs'],results['AA']['scores'])]
    results_bb = [(a,b,c,'BB') for a,b,c in zip(
        results['BB']['edges'],results['BB']['freqs'],results['BB']['scores'])]

    all_results = results_ab  + results_aa + results_bb

    # map results using data dictionaries
    print 'Here',params.dict
    xH,yH,r1,s1 = map_results(howie_results,data,params)
    xM,yM,r2,s2 = map_results(all_results,data,params)

    if params.plot_auroc:

        # generate figure
        axes = plt.gca()
        
        # plot results
        plt.plot(xH['X'],yH['X'],label='Howie (X)')
        plt.plot(xH['Y'],yH['Y'],label='Howie (Y)')
        plt.plot(xM['X'],yM['X'],label='MAD-HYPE (X)')
        plt.plot(xM['Y'],yM['Y'],label='MAD-HYPE (Y)')

        print 'here'
        # add error limit
        xB,yB = np.arange(0,1+int(axes.get_ylim()[1])/200),200*np.arange(0,1+int(axes.get_ylim()[1])/200)
        plt.plot(xB,yB,label='1% Error',linestyle='--',color='k')
        axes.set_xlim(left = 0)
        axes.set_ylim(bottom = 0)

        # stylize graph
        plt.xlabel('Number of false positives')
        plt.ylabel('Number of true positives')

        # print out improvement metrics
        for xm,ym,label in [(xM['X'],yM['X'],'X'),(xM['Y'],yM['Y'],'Y'),(xH['X'],yH['X'],'X (howie)'),(xH['Y'],yH['Y'],'Y (howie)')]:
            for i,x,y in zip(xrange(len(xm)),xm,ym):
                if y < 200*x:
                    print 'Subject {}: {} [X = {}]'.format(label,ym[i-1],xm[i-1])
                    break

        plt.legend()
        plt.show(block=False)
        raw_input('Press enter to continue...')
    
    return r1,r2,s1,s2

def map_results(results,data,params={}):
    results.sort(key=lambda x:-float(x[2]))
    print 'Total matches:',len(results)
    x,y = {'X':[0],'Y':[0]},{'X':[0],'Y':[0]}
    
    # create reverse dictionary in case of need
    seq_chain_A = dict([(v,k) for k,v in (data.chain_seq['A']).items()])
    seq_chain_B = dict([(v,k) for k,v in (data.chain_seq['B']).items()])
    pairs = []
    records = []
    scores = []

    for edge in results:
        if type(edge[0][0]) == int:
            if len(edge) == 4:
                pairs.append(str(edge[0][0])+edge[3][0]+' | '+str(edge[0][1])+edge[3][1]) 
                x_origin = data.chain_origin[edge[3][0]][str(edge[0][0])]
                y_origin = data.chain_origin[edge[3][1]][str(edge[0][1])]
            else:
                x_origin = data.chain_origin['A'][edge[0][0]]
                y_origin = data.chain_origin['B'][edge[0][1]]
        elif type(edge[0][0]) == str:
            try:
                x_ind,y_ind = seq_chain_A[edge[0][0]],seq_chain_B[edge[0][1]]
                x_origin,y_origin = data.chain_origin['A'][x_ind],data.chain_origin['B'][y_ind]
            except KeyError:
                continue
        # check if same origin patient (exclusive)
        if ('X' == x_origin and 'X' == y_origin):
            x['X'].append(x['X'][-1])
            y['X'].append(y['X'][-1]+1)
            records.append(1)
            scores.append(edge[2])
        elif ('Y' == x_origin and 'Y' == y_origin):
            x['Y'].append(x['Y'][-1])
            y['Y'].append(y['Y'][-1]+1)
            records.append(1)
            scores.append(edge[2])
        elif ('X' == x_origin and 'Y' == y_origin) or ('Y' == x_origin and 'X' == y_origin): 
            x['X'].append(x['X'][-1]+1) # think about this (should it be 0.5?)
            x['Y'].append(x['Y'][-1]+1)
            y['X'].append(y['X'][-1])
            y['Y'].append(y['Y'][-1])
            records.append(0)
            scores.append(edge[2])
        else:
            pass
        if params.max_threshold:
            if x['X'][-1] == params.max_threshold: break

    return x,y,records,scores

def subjectXYdata(dirnameX,dirnameY):
    """ Pulls out file names corresponding the directories submitted, subjects X/Y """
    # initialize dictionaries
    subject_x_files,subject_y_files = {'gdna':{},'cdna':{}},{'gdna':{},'cdna':{}}
    
    # iterate across dirnames and file dictionaries
    for dirname,files in zip([dirnameX,dirnameY],[subject_x_files,subject_y_files]):
        for data_type in ['gdna','cdna']:
            # story directory contents
            dirfiles = os.listdir(dirname+'/{}_data'.format(data_type))
            # check across files for file in dirfiles:
            for file in dirfiles:
                # check if starting file is gzipped
                if file.endswith('.gz') and not any([file[:-3] in d for d in dirfiles if not d.endswith('.gz')]):
                    with gzip.open(dirname+'/{}_data/'.format(data_type)+file,'rb') as f:
                        with open(dirname+'/{}_data/'.format(data_type)+file[:-3],'wb') as f_new:
                            f_new.write(f.read(file[:-3]))
                    print 'Unzipped {}.'.format(dirname+'/{}_data/'.format(data_type)+file)
                    files[data_type][file[file.index('TCR')+3] + file[file.index('.well')+5:file.index('.results')]] = \
                            dirname+'/{}_data/'.format(data_type)+file[:-3]

                # otherwise store file location
                elif file.endswith('.tsv'):
                    files[data_type][file[file.index('TCR')+3] + file[file.index('.well')+5:file.index('.results')]] = \
                            dirname+'/{}_data/'.format(data_type)+file
            
    return subject_x_files,subject_y_files

def catalog_repertoire(filesX,filesY,overwrite=False):
    """ Creates a dictionary that takes each unique sequence and assigns ownership between subject X/Y """
    """ This analysis is very slow, so I'm pulling as many tricks out as I can """
    if overwrite == True or not dbm_check('origin_dict_B','origin_dict_A'):
        origin_dict = {} 
        # iterate across repertoires to make independent dictionaries
        for patient_id,files in zip(['X','Y'],[filesX,filesY]):
            origin_dict[patient_id] = {}
            for chain_id in ['A','B']: 
                found,keep = set(),[] # create some storage variables
                add,app = found.add,keep.append
                # return 
                for file_id,file in files['cdna'].items(): 
                    if not chain_id in file_id: continue # catch to weed out nonmatching chains
                    print 'Processing sample {} for patient {}'.format(file_id,patient_id) 
                    # go through file and pull sequences
                    with open(file,'rb') as f:
                        for line in csv.reader(f, dialect="excel-tab"):
                            if line[0] not in found:
                                add(line[0]) # circumvent attribute lookup
                                app(line[0]) # circumvent attribute lookup
                origin_dict[patient_id][chain_id] = keep 
                #pickle.dump(origin_dict,open('./pickles/origin_dict.p','wb'),protocol=pickle.HIGHEST_PROTOCOL) 
        # merge dictionaries
        final_dict = {'A':{},'B':{}}
        for patient_id,chain_dict in origin_dict.items():
            for chain_id,seqs in chain_dict.items():
                print '{} sequences found for chain {}, patient {}'.format(len(seqs),chain_id,patient_id)
                for seq in seqs:
                    try:
                        #final_dict[chain_id][seq].append(patient_id)
                        final_dict[chain_id][seq] += patient_id
                    except KeyError:
                        #final_dict[chain_id][seq] = [patient_id]
                        final_dict[chain_id][seq] = patient_id
        #pickle.dump(final_dict,open('./pickles/origin_dict.p','wb'),protocol=pickle.HIGHEST_PROTOCOL) 
        # DBM save
        dbm_save(final_dict['A'],'origin_dict_A') 
        dbm_save(final_dict['B'],'origin_dict_B') 
    
    # if there already exists a dictionary that isn't to be overwritten 
    else:
        # TODO: This really isn't necessary
        print 'Loading existing origin dictionary...'
        #final_dict = pickle.load(open('./pickles/origin_dict.p','r'))
        print 'Finished loading!'

    # final counts on chain sequence popularity 
    #for chain_id,seq_dict in final_dict.items():
        #print 'Total sequences for chain {}: {}'.format(chain_id,len(seq_dict.keys()))

    #return final_dict

def data_assignment(dirname,threshold=(4,90),overwrite=True,silent=False):
    """ Pulls out data from experiment directory and assigns TCR wells """
    """ Only valid for two subject testing """
    """ Note: threshold mimicked from Howie """

    secret_switch = False 
    ind = dirname[-1]

    # initialize dictionaries
    well_dict = {'A':[],'B':[]} # will hold lists of lists containing chain indices
    #chain_2_origin = {'A':{},'B':{}} # will hold lists of lists containing chain indices
    #chain_2_sequence = {'A':{},'B':{}} # will hold lists of lists containing chain indices
    #sequence_2_chain = {'A':{},'B':{}} # will hold lists of lists containing chain indices

    # create DBM dictionaries
    '''
    chain_2_origin = {'A':dbm_load('chain_2_origin_{}_A'.format(ind)),
                      'B':dbm_load('chain_2_origin_{}_B'.format(ind))}
    chain_2_sequence = {'A':dbm_load('chain_2_sequence_{}_A'.format(ind)),
                        'B':dbm_load('chain_2_sequence_{}_B'.format(ind))}
    sequence_2_chain = {'A':dbm_load('chain_2_origin_{}_A'.format(ind)),
                        'B':dbm_load('chain_2_origin_{}_B'.format(ind))}
    '''

    files = {'A':{},'B':{}}

    # save files
    

    """ Start unpackaging data, create the four dictionaries """ 
    if overwrite == True or not os.path.isfile('./pickles/well_dict_{}.p'.format(dirname[-1])) or secret_switch:
        
        #print 'why am i here'
        #print overwrite == True
        #print not os.path.isfile('./pickles/well_dict_{}.p'.format(dirname[-1]))
        #print secret_switch

        dirfiles = os.listdir(dirname+'/cdna_data/')
        """ Find the file names of all the data, unzip where needed """
        # check across all files, unzip as needed
        for file in dirfiles:
            # check if starting file is gzipped
            if file.endswith('.gz') and not any([file[:-3] in d for d in dirfiles if not d.endswith('.gz')]):
                with gzip.open(dirname+'/cdna_data/'+file,'rb') as f:
                    with open(dirname+'/cdna_data/'+file[:-3],'wb') as f_new:
                        f_new.write(f.read(file[:-3]))
                print 'Unzipped {}.'.format(dirname+'/cdna_data/'+file)
                files[file[file.index('TCR')+3]][int(file[file.index('.well')+5: \
                        file.index('.results')])] = dirname+'/cdna_data/'+file[:-3]

            # otherwise store file location
            elif file.endswith('.tsv'):
                files[file[file.index('TCR')+3]][int(file[file.index('.well')+5: \
                        file.index('.results')])] = dirname+'/cdna_data/'+file

        ###
        if not dbm_check('origin_dict_A','origin_dict_B'):
            print 'No origin dictionary provided, exiting...'
            return None


        for chain_id,chain_files in files.items(): # iterate across file locations 
            if secret_switch: continue
            # create a list of all sequences in origin dictionary (now .dbm)
            origin_dict = dbm_local('origin_dict_{}'.format(chain_id))
            origin_seqs = origin_dict.keys()
            chain_2_origin = {} # will hold lists of lists containing chain indices
            chain_2_sequence = {} # will hold lists of lists containing chain indices
            sequence_2_chain = {} # will hold lists of lists containing chain indices
            clone_ind = 0 
            passed_seqs = []

            # iterate across repertoires to make independent dictionaries
            for well_id in sorted(chain_files.keys(),key=int):
                # go through file and pull sequences
                with open(files[chain_id][well_id],'rb') as f:
                    if not silent: print 'Analyzing well {} for chain {}...'.format(well_id,chain_id)
                    well_dict[chain_id].append([])
                    for i,line in enumerate(csv.reader(f, dialect="excel-tab")):
                        if i == 0: continue # skip header line 
                        #if line[0] in origin_seqs:    
                        try: # try to assign the chain to a sequence index
                            well_dict[chain_id][-1].append(sequence_2_chain[line[0]])
                        except KeyError: # if there isn't an existing index
                            # TODO: change to use origin dict
                            try:
                                chain_2_origin[clone_ind] = \
                                        origin_dict[line[0]] 
                                well_dict[chain_id][-1].append(clone_ind)
                                chain_2_sequence[clone_ind] = line[0]
                                sequence_2_chain[line[0]] = clone_ind
                                passed_seqs.append(line[0])
                                clone_ind += 1
                            except KeyError:
                                pass
                        
                        #if not silent: 
                            #if i%100 == 0: print 'Completed {} lines.'.format(i+1)
            
            
            # save the dictionaries between chains 
            if not secret_switch:
                dbm_save(chain_2_origin,'chain_2_origin_{}_{}'.format(ind,chain_id))
                dbm_save(chain_2_sequence,'chain_2_sequence_{}_{}'.format(ind,chain_id))
                dbm_save(sequence_2_chain,'sequence_2_chain_{}_{}'.format(ind,chain_id))

            # in case deep failure
            if secret_switch: well_dict = pickle.load(open('./pickles/before_well_dict_{}.p'.format(ind),'rb'))

            # remove chains that occur less than threshold 
            print 'Adjusting well data for occurance threshold...'
            chain_keys = {'A':[k for k,v in Counter(flatten(well_dict['A'])).items() if v >= threshold[0] and v <= threshold[1]],
                          'B':[k for k,v in Counter(flatten(well_dict['B'])).items() if v >= threshold[0] and v <= threshold[1]]}


            # A little safety dump
            pickle.dump(well_dict,open('./pickles/before_well_dict_{}.p'.format(ind),'wb'),protocol=pickle.HIGHEST_PROTOCOL) 

            well_dict['A'] = [compare_lists(j,chain_keys['A']) for i,j in enumerate(well_dict['A'])]
            print 'Finished well A adjustment!'
            well_dict['B'] = [compare_lists(j,chain_keys['B']) for i,j in enumerate(well_dict['B'])]
            print 'Finished well B adjustment!'

            print 'Key size:'
            print ' > A:',len(chain_keys['A'])
            print ' > B:',len(chain_keys['B'])
            print 'Uniques:' 
            print ' > A:',len(set([i for w in well_dict['A'] for i in w]))
            print ' > B:',len(set([i for w in well_dict['B'] for i in w]))

            pickle.dump(well_dict,open('./pickles/well_dict_{}.p'.format(ind),'wb'),protocol=pickle.HIGHEST_PROTOCOL) 
            print 'Finished saving!'
        
        # if there already exists a dictionary that isn't to be overwritten 
    else:
        well_dict = pickle.load(open('./pickles/well_dict_{}.p'.format(ind),'rb'))

    chain_2_origin = {'A':dbm_local('chain_2_origin_{}_A'.format(ind)),
                      'B':dbm_local('chain_2_origin_{}_B'.format(ind))}
    chain_2_sequence = {'A':dbm_local('chain_2_sequence_{}_A'.format(ind)),
                        'B':dbm_local('chain_2_sequence_{}_B'.format(ind))}

    return Results(well_dict,chain_2_origin,chain_2_sequence)
    


class Results:
    """ Quick class to package output data """
    def __init__(self,well_dict,chain_origin,chain_seq):
        # save data to object
        self.well_data = [[a,b] for a,b in zip(well_dict['A'],well_dict['B'])]
        self.chain_origin = chain_origin
        self.chain_seq = chain_seq

### Parameters Class & Defaults ###

def default_parameters():
    return {
            'mode':'coast2coast',
           }

class Parameters:
    """ Creates a default set of analytical parameters, replaces with any input dictionary """ 
    # use a dictionary to update class attributes
    def update(self,params={}):
        # makes params dictionary onto class attributes
        print params
        for key, value in params.items():
            setattr(self, key, value)
            print key, self.__dict__[key]
        # can apply checks afterward

    # initialize class with default dictionary
    def __init__(self,default_params,custom_params={}):
        self.update(default_params)
        self.model_parameters = default_params.keys()
        self.update(custom_params)

    def dict(self):
        return self.__dict__

# script call catch
if __name__ == '__main__':
    if len(sys.argv) > 1:
        print 'Starting script under command: {}'.format(sys.argv[1])
        main(sys.argv[1])
    else:
        main()

