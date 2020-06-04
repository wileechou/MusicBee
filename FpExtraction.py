import hashlib
from _sha256 import sha256
from pydub import *
import numpy as np
from matplotlib import mlab
from scipy.ndimage import *

import FPconfig



filepath='music/test.flac'

def generateFilehash(filepath, blocksize = 2 ** 16):
    """

    :param filepath: path of music file
    :param blocksize:
    :return:hash value of music
    """
    sha = sha256()
    with open(filepath,'rb') as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            sha.update(buf)
    return sha.hexdigest().upper()

def getConstellationMap(spectrum,plot = False, min_peak_amp = FPconfig.minimum_peak_amplitude):
    """

    :param spectrum: the array of spectrum in log space
    :param plot: if show the plot
    :param min_peak_amp: the minimum value to regard as peak
    :return: 2-d array of peaks[(x1,y1),(x2,y2),.....]
    """



    struct = generate_binary_structure(2,1)
    neighborhood = iterate_structure(struct,FPconfig.peak_neighborhood_size)

    #find local maximum using our filter shape
    local_max = maximum_filter(spectrum, footprint=neighborhood) == spectrum
    background = (spectrum == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    #Boolean mask of arr2D with True at peaks
    detected_peaks = local_max ^ eroded_background

    #extract peaks
    amps = spectrum[detected_peaks]
    j, i = np.where(detected_peaks)

    #filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps) #time, freq, amp
    peaks_filtered = [x for x in peaks if x[2] > min_peak_amp]

    #calc hash of fp
    peaks = peaks_filtered
    peaks.sort(key=lambda x:x[0])
    fph=[]

    for i in range(len(peaks)-FPconfig.fanout_factor):
        for j in range(FPconfig.fanout_factor):
            t1 = peaks[i][0]
            t2 = peaks[i+j][0]
            freq1 = peaks[i][1]
            freq2 = peaks[i+j][1]
            t_delta = t2 - t1



            if t_delta >= FPconfig.time_constraint_condition[0] and t_delta <= FPconfig.time_constraint_condition[1]:
                print('0')
                '''
                h = hashlib.sha256(
                    ("%s_%s_%s" % (str(freq1), str(freq2), str(t_delta))).encode())
                yield (h.hexdigest()[0:64 - FPconfig.fingerprint_cutoff],t1)
                fph.append(h)
                '''






    #get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    #print(max(time_idx))
    #return list(zip(time_idx, frequency_idx)),hash
    return fph




if __name__== '__main__':
    audiofile = AudioSegment.from_file(filepath)
    data = np.fromstring(audiofile.raw_data,np.int16)
    fs = audiofile.frame_rate
    channels = []

    for channel in range(audiofile.channels):
        channels.append(data[channel::audiofile.channels])

    sample = channels[0]

    spectrum, freques, t = mlab.specgram(sample,NFFT=4096, Fs=fs, noverlap=2048)

    # transfer to log space
    # replace all 0 with 1 to avoid log(0) appear since the intensity is 0 when log(1)==0
    spectrum[spectrum == 0] = 1
    spectrum = 10 * np.log10(spectrum)

    # replace -inf with zeros since it does not effect the result
    spectrum[spectrum == -np.inf] = 0

    getConstellationMap(spectrum)
    print("breakpoint1")



