"""Setup for an IBC experiment.

Contains all configs from the application scheme.
Experiments should differ by this setup only.
Can create HDF5-based or fast online experiments.
"""
__author__ = "Anton Akusok"
__license__ = "PSFL"
__version__ = "0.0.1"


class IBCConfig(object):
    """Global parameters for WIC system.

    Import this with some simpler name, like "conf".
    """
    _dir = "/data/r0/spiiras_train/"
    _ibc = "/home/akusoka1/WIBC/src/"
    _maxc = 12  # maximum amount of different classes
    _raw_dir = _dir + "raw_img/"
    _ws_descr = _dir + "wsdescr.txt"
    
    # m02: choose either option, the other gets ""
    _mode = "hdf5"  # its either "hdf5" or something else
    _hdf5 = _dir + "spiiras_train.h5"
    _img_data = _dir + "imgdata.pkl"
    
    # m03: img_preprocessor
    _img_dir = _dir + "images/"
    _min_size = 2400
    _max_dim = 500
    _jpeg_quality = 95
    
    # m04: get_descriptors
    _temp_dir = "/run/shm/"
    _descr_extractor = "csift"
    _max_reg = 10000  # maximum number of regions
    _cD_bin = _ibc + "sift/colorDescriptor"
     
    # m05: get_centroids
    _C_file = _dir + "C.pkl"
        # must correspond to the given _maxc !!!
        # contains: C["C"] = centroids
        #           C["L_majority"] = majority labels
        #           C["L_soft"] = soft labels
    
    # m06: run_nn
    _nn_count = 10
    _nn_batch = 100
    
    # m08: elm_classifier
    _train_size = 10000
    _val_size = 10000
    _test_size = 20000
    _neurons = 50
    _elm_rep = 100  # ELM re-train repetitions for validation
    _elm_param = _dir + "ELM.pkl"

    # saving results
    _f_out = _dir + "out_test_border.txt"

    # multiprocessing config
    _nr_wrk = 10  # a good guess is the number of cores - 1
    _qsize = 300  # maximum size of a queue, to limit memory consumption
    _host = _dir + "hostname.txt"
    _port = 50763
    _key = "IBC"
    _show_progress = True
    

    ##########################################################################
    
    # neighborhood matrix config
    _nm_hdf5 = _dir + "descr_clust.h5"  # HDF5 file storing neighbours info
    _nm_descr = _dir + "descr.pkl"  # cPickle'd array of descriptors
    _nm_N = 1100000  # amount of descriptors for neighbourhood matrix calc
    _nm_K = 1000  # amount of nearest neighbours kept
    _nm_batch = 100000  # batch size












    classes = {}  # table of classes in number notations
    classes["Adult"]         = 0 
    classes["Alcohol"]       = 1
    classes["Cults"]         = 2
    classes["Dating"]        = 3
    classes["Drugs"]         = 4
    classes["Gambling"]      = 5
    classes["Hate"]          = 6
    classes["Tobacco"]       = 7
    classes["Violence"]      = 8
    classes["Weapons"]       = 9
    classes["Innocent"]      = 10
    classes["Advertisement"] = 11

    @staticmethod
    def get_SIFT_command(img_file, temp_file):
        max_reg = 10000  # limiting number of local features per one image
        command = ('./colorDescriptor %s --detector harrislaplace '
                   '--descriptor csift --output %s --outputFormat binary '
                   '--keepLimited %d > /dev/null'
                   % (img_file, temp_file, max_reg))
        return command
    
    @staticmethod
    def file_name(classN, nr_in_class, ext):
        """Build standard image or region file name.

        Allows to change the name pattern as desired (keep same arguments).
        """
        fname = "i%02d_%08d.%s" % (classN, nr_in_class, ext)
        return fname



