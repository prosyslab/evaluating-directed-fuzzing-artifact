from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from scipy.stats import mannwhitneyu
import numpy as np
import matplotlib.pyplot as plt


def replace_none(tte_list, timeout):
    list_to_return = []
    for tte in tte_list:
        if tte is not None:
            list_to_return.append(tte)
        elif timeout != -1:
            list_to_return.append(timeout)
        else:
            print("[ERROR] Should provide valid T/O sec for this result.")
            exit(1)
    return list_to_return


def average_tte(tte_list, timeout):
    has_timeout = None in tte_list
    tte_list = replace_none(tte_list, timeout)
    avg_val = sum(tte_list) / len(tte_list)
    prefix = "> " if has_timeout else ""
    return "%s%d" % (prefix, avg_val)


def median_tte(tte_list, timeout):
    tte_list = replace_none(tte_list, timeout)
    tte_list.sort()
    n = len(tte_list)
    if n % 2 == 0:  # When n = 2k, use k-th and (k+1)-th elements.
        i = int(n / 2) - 1
        j = int(n / 2)
        med_val = (tte_list[i] + tte_list[j]) / 2
        half_timeout = (tte_list[j] == timeout)
    else:  # When n = 2k + 1, use (k+1)-th element.
        i = int((n - 1) / 2)
        med_val = tte_list[i]
        half_timeout = (tte_list[i] == timeout)
    prefix = "> " if half_timeout else ""
    return "%s%d" % (prefix, med_val)


def min_max_tte(tte_list, timeout):
    has_timeout = None in tte_list
    tte_list = replace_none(tte_list, timeout)
    max_val = max(tte_list)
    min_val = min(tte_list)
    prefix = "> " if has_timeout else ""
    return ("%d" % min_val, "%s%d" % (prefix, max_val))


def example():
    # Exmaple of a case where the result of log-rank test and U-test diverges

    TIMEOUT = 86400

    kmf = KaplanMeierFitter()
    kmf2 = KaplanMeierFitter()

    # T = [TTE data from cxxfilt-2016-4487-AFL]
    T = np.array([
        122, 11, 249, 36, 555, 44, 87, 180, 91, 227, 269, 64, 153, 142, 62,
        244, 149, 49, 32, 191, 142, 97, 32, 194, 166, 213, 190, 55, 99, 217,
        79, 183, 100, 80, 60, 125, 201, 89, 91, 60, 189, 161, 119, 43, 82, 81,
        76, 159, 584, 67, 128, 29, 148, 47, 95, 326, 285, 94, 108, 314, 100,
        232, 34, 156, 112, 93, 106, 315, 53, 186, 99, 99, 201, 64, 149, 38,
        113, 97, 75, 102, 120, 38, 370, 179, 135, 136, 71, 18, 226, 196, 162,
        114, 117, 22, 78, 196, 41, 212, 73, 286, 37, 23, 154, 323, 118, 60, 53,
        75, 79, 167, 140, 38, 220, 270, 24, 79, 184, 128, 93, 92, 75, 195, 68,
        72, 42, 220, 147, 53, 123, 83, 52, 77, 338, 146, 160, 180, 85, 551,
        140, 145, 141, 92, 24, 98, 76, 137, 255, 141, 222, 32, 242, 167, 108,
        203, 88, 343, 216, 72, 224, 92
    ])
    # T2 = [TTE data from cxxfilt-2016-4487-WindRanger]
    T2 = np.array([
        924, 30, 324, 31, 583, 869, 200, 120, 163, 67, 100, 52, 190, 73, 34,
        410, 57, 44, 222, 195, 282, 112, 87, 240, 26, 18, 63, 82, 140, 141, 18,
        148, 24, 287, 94, 567, 76, 54, 65, 225, 55, 61, 238, 88, 26, 107, 246,
        87, 68, 55, 195, 868, 69, 16, 706, 68, 30, 38, 675, 353, 95, 49, 152,
        58, 142, 12, 26, 353, 114, 117, 216, 256, 1284, 19, 46, 184, 313, 95,
        143, 517, 48, 45, 215, 146, 23, 284, 188, 145, 29, 279, 52, 29, 31, 88,
        87, 894, 803, 26, 198, 78, 336, 25, 77, 73, 94, 53, 119, 44, 379, 146,
        61, 102, 295, 31, 75, 183, 460, 409, 444, 133, 623, 196, 88, 146, 130,
        25, 284, 97, 733, 27, 830, 106, 214, 52, 62, 85, 24, 258, 362, 200, 99,
        38, 39, 132, 145, 32, 96, 84, 222, 69, 63, 100, 31, 575, 214, 1108,
        140, 38, 148, 102
    ])

    C = T < TIMEOUT
    C2 = T2 < TIMEOUT

    kmf.fit(T, event_observed=C, label='AFL')
    kmf2.fit(T2, event_observed=C2, label='WR')

    # Plots Kaplan-Meier estimator of two data
    kmf.plot()
    kmf2.plot()
    plt.savefig('output/kmf.png')

    # Log-rank test (Null hypothesis: two populations have equal survival function)
    summary = logrank_test(T, T2, C, C2, alpha=99)
    print(summary)

    # Mann-Whitney U test
    print(mannwhitneyu(T, T2, method="auto"))


if __name__ == "__main__":
    example()
