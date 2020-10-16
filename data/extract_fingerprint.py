import numpy as np
import math
import matplotlib.pyplot as plt

"""
Reads the CSV file (delimiter ,) and returns it 
@param path Path of the file to be read
"""
def read_from_file(path):
    return np.loadtxt(path, delimiter=',')

"""
Calculates the gradiends of the phases between the subcarriers 

@param SCs Phases of all subcarriers (without DC) a & ac
"""
def get_gradients(SCs):
    gradients = []
    for i in range(len(SCs)):
        # First gradient set to 0
        if (i > 0):
            gradients.append(SCs[i] - SCs[i - 1])
        else:
            gradients.append(0)
    return gradients


"""
Sanitizes the phases of the subcarriers so that no jumps of 2*pi occur

@param SCs Phases of all subcarriers (without DC) a & ac
"""
def sanitize_array(SCs):
    fubr = 0
    # Get gradients first
    gradients = get_gradients(SCs)
    pi = 4
    for i in range(len(SCs)):
        if (i > 0):
            if (gradients[i] > pi):
                fubr += 1
            elif (gradients[i] < -pi):
                fubr -= 1
            if (fubr != 0):
                SCs[i] = SCs[i] - fubr * math.pi * 2
    return SCs


"""
Sanitizes an array of arrays of phases of all SCs

@param meas Array of arrays of phases of all SCs
"""
def sanitize_measurements(meas):
    # import ipdb; ipdb.set_trace()
    #Check if measurement has only one dimension
    if (len(meas.shape) == 1):
        return sanitize_array(meas)
    #Iterate through all measurements
    for i in range(len(meas)):
        meas[i] = sanitize_array(meas[i])
    return meas


"""
There are different devices in some measurements, In order to figure them out, we take the sum of the gradients and 
apply a sime threshold mechanism

@param meas Array of arrays of phases of all SCs
"""
def categorize_measurements(meas):
    threshold = -4
    cat1 = []
    cat2 = []
    for i in range(len(meas)):
        print(np.sum(get_gradients(meas[i])))
        if (np.sum(get_gradients(meas[i])) < threshold):
            cat1.append(meas[i])
        else:
            cat2.append(meas[i])
    return np.array(cat1), np.array(cat2)

def calc_Z(phases_per_subcarrier):
    return ((phases_per_subcarrier[26] + phases_per_subcarrier[25]) / 2)

"""
Calculates the fingerprint of one measurement

@:param phases_per_subcarrier 
"""
def get_fingerprint(phases_per_subcarrier):
    r = phases_per_subcarrier
    Z = (r[26] + r[25]) / 2
    #plt.plot(r-Z)
    K = [-26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4,
         -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    K = np.array(K)
    l = (-r[0] + r[51]) / (2 * math.pi * 52)
    E = r - (2 * math.pi * l * K + Z)
    return E, (r-Z)


"""
Calculates the fingerprint for 80211ac measurements
"""
def get_fingerprint_ac(phases_per_subcarrier):
    r = phases_per_subcarrier
    Z = (phases_per_subcarrier[28] + phases_per_subcarrier[27]) / 2
    #plt.plot(r-Z)
    K = [-28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
    K = np.array(K)
    l = (-r[0] + r[55]) / (2 * math.pi * 56)
    E = r - (2 * math.pi * l * K + Z)
    return E, (r-Z)

"""
Obtain the subcarriers that carry STF signals
"""
def get_stf_subcarriers(phases_per_subcarrier):
    subc = []
    stf_subcarriers = [4, 8, 12, 16, 20, 24, 31, 35, 39, 43, 47, 51]
    for i in range(len(phases_per_subcarrier)):
        if i in stf_subcarriers:
            subc.append(phases_per_subcarrier[i])
    return subc

"""
Caluclate the STF-based fingerprint
"""
def get_fingerprint_stf(phases_per_subcarrier):
    r = get_stf_subcarriers(phases_per_subcarrier)
    Z = (r[5] + r[6]) / 2
    K = [-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24]
    K = np.array(K)
    l = (-r[0] + r[11]) / (2 * math.pi * 56)
    E = r - (2 * math.pi * l * K + Z)
    return E, (r-Z)

"""
Extract the fingerprints from a set of measurements
"""
def get_fingerprints(measurements):
    fingerprints = []
    rZ = [] 
    # import ipdb; ipdb.set_trace()
    # Check if we have one or more measurements
    if (len(measurements.shape) == 1):
        if (measurements.shape[0] == 56):
            return get_fingerprint_ac(measurements)
        else:
            return get_fingerprint(measurements)
    #Iterate through all measurements
    for i in range(measurements.shape[0]):
        if (measurements.shape[1] == 56):
            fp, r = get_fingerprint_ac(measurements[i])
        else:
            fp, r = get_fingerprint(measurements[i])
        fingerprints.append(fp)
        rZ.append(r)
    fingerprints = np.array(fingerprints)
    rZ = np.array(rZ)
    return fingerprints, rZ

"""
Extract the fingerprints from a set of STF measurements
"""
def get_fingerprints_stf(measurements):
    print(measurements.shape)
    fingerprints = []
    rZ = [] 
    # import ipdb; ipdb.set_trace()
    # Check if we have one or more measurements
    if (len(measurements.shape) == 1):
        return get_fingerprint_stf(measurements)
    #Iterate through all measurements
    for i in range(measurements.shape[0]):
        fp, r = get_fingerprint_stf(measurements[i])
        fingerprints.append(fp)
        rZ.append(r)
    fingerprints = np.array(fingerprints)
    rZ = np.array(rZ)
    return fingerprints, rZ

"""
Calculates the mean of all measurements for one SC

@:param measurements Array of arrays of phases of all SCs
@:param number_of_measurements Ammount of measurements
"""
def get_mean(measurements, number_of_measurements):
    m = []
    for i in range(len(measurements)):
        m.append(measurements[i].sum() / number_of_measurements)
    return np.array(m)

def get_mean_std(measurements, number_of_measurements):
    means = []
    for i in range(len(measurements)):
        means.append(measurements[i].sum() / number_of_measurements)
    std = []
    for i in range(measurements.shape[0]):
        std.append(np.std(measurements[i]))
    return np.array(means), np.array(std)


"""
Caluclate MAE of a fingerprint when compared to a reference fingerprint

@return: MAE
"""
def get_mean_average_error(reference_fingerprint, fingerprint):
    reference_abs = np.absolute(reference_fingerprint)
    fingerprint_abs = np.absolute(fingerprint)
    error = np.sum(np.absolute(reference_abs - fingerprint_abs))
    return (error/len(reference_fingerprint))


"""
Calculates all the fingerprints and take mean afterwards

@:param path Path to the file

@:param description Description for the legend
"""
def extract_measurements(path, description, path_to_store="none", color="none", number=100):
    r = read_from_file(path)
    r = sanitize_measurements(r)
    print(r.shape)
    fingerprints = []
    fingerprints, rZ = get_fingerprints(r)
    fingerprints = np.array(fingerprints)

    #get standard deviation
    print(fingerprints.T.shape)
    var = []
    for i in range(fingerprints.T.shape[0]):
        var.append(np.std(fingerprints.T[i]))
    means = get_mean(fingerprints.T, len(fingerprints))

    x = np.linspace(0, fingerprints.T.shape[0]-1, fingerprints.T.shape[0])
    if (color != "none"):
        plt.errorbar(y=means, x=x, yerr=var, fmt="none", capsize=3, color=color)
        plt.plot(means, label=description, marker='o', color=color)
    else:
        plt.errorbar(y=means, x=x, yerr=var, fmt="none", capsize=3)
        plt.plot(means, label=description, marker='o')

    #prepare output to file

    means_string = []
    for m in means:
        means_string.append("{:.4f}".format(m))

    if path_to_store != "none":
        with open(path_to_store, "w") as output:
            means_string = str(means_string).replace("[", "")
            means_string = means_string.replace("]", "")
            means_string = means_string.replace("'", "")
            output.write(str(means_string))
    return means

"""

"""
def extract_measurements_iteration(path, number=100, iterations = 1):
    r = read_from_file(path)
    r = sanitize_measurements(r)
    fingerprints = []
    for i in range(len(r)):
        fingerprints.append(get_fingerprint(r[i]))
    fingerprints = np.array(fingerprints)
    fingerprints_it = []
    index = 0
    for i in range(iterations):
        fp = fingerprints[index:index+number]
        index += number
        #get standard deviation
        var = []
        for i in range(52):
            var.append(np.std(fp.T[i]))
        means = get_mean(fp.T, len(fp))
        fingerprints_it.append(means)

    return fingerprints_it

"""
Obtain phases from the file in @path
"""
def get_phases(path, description):
    r = read_from_file(path)
    r = r - r[0]
    means_string = []
    for m in r:
        means_string.append("{:.4f}".format(m))
    print(means_string)
    with open("Data/Fingerprints/mean_phase_mean_ursp_rere_at_lili.csv", "w") as output:
        means_string = str(means_string).replace("[", "")
        means_string = means_string.replace("]", "")
        means_string = means_string.replace("'", "")

        output.write(str(means_string))


"""
Misleading name; Used to get he fingerprints of the measurements where multiple devices sent packets

@params Path to the file
"""
def debug_one_measurements(path):
    r = read_from_file(path)
    r = sanitize_measurements(r)
    r1, r2 = categorize_measurements(r)
    fingerprint = 0
    fingerprints = []
    for i in range(len(r1)):
        fingerprints.append(get_fingerprint(r1[i]))
    fingerprints = np.array(fingerprints)
    plt.plot(get_mean(fingerprints.T, len(fingerprints)), marker='o', label="00 Macbook/AC1750 10 cm")

    fingerprints = []
    for i in range(len(r2)):
        fingerprints.append(get_fingerprint(r2[i]))
    fingerprints = np.array(fingerprints)
    plt.plot(get_mean(fingerprints.T, len(fingerprints)), marker='o', label="00 Macbook/AC1750 10 cm")
    axes = plt.gca()
    #axes.set_ylim([-0.8, 0.8])

    #debug_one_measurements("C:/Users/SEEMOO/Desktop/AnBa Masterthesis/Data/06 Phases TPAC1750 lili antenna 10cm 100.csv")
    #plt.legend()
    plt.xlabel("Subcarrierindex")
    plt.ylabel("Phase error")