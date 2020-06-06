import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from scipy.stats import normaltest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import probscale
import base64
import io
import seaborn as sns
sns.set()

def logprob(data):
    y = np.sort(data)
    x = np.arange(1, len(y)+1)/len(y)

    return x, y


def testar_norm(data):
    k, p = normaltest(data)
    alpha = 0.05
    print("p = " + str(p))
    if p < alpha:
        # null hypothesis of the test is the data is normally distributed.
        # If the p value returned is less than . 05 , then the null hypothesis
        # is rejected and there is evidence that the data is not from a normally distributed population
        print("The null hypothesis can be rejected. Data probably not normally distributed.")
        return 'doane'
    else:
        print("The null hypothesis cannot be rejected. Data probably is normally distributed.")
        return 'sturges'
    # plt.hist(data)

def classes_frequencias(dados):
    dist_type = testar_norm(dados)

    classes = np.histogram_bin_edges(dados, bins=dist_type)
    print('número de classes: ' + str(len(classes) - 1))
    print('intervalos: ' + str(classes))

    n_classes = len(classes) - 1

    lista_classes = []
    for i in range(0, n_classes):
        lista_classes.append([])

    classe = 0

    for sample in sorted(dados):
        if sample >= classes[classe] and sample < classes[classe + 1]:
            lista_classes[classe].append(sample)
            # print(str(sample)+' adicionado na classe '+str(classe))
        else:
            for intervalo in range(0, n_classes):
                if sample >= classes[intervalo] and sample <= classes[intervalo + 1]:
                    # print('avançou da classe '+str(classe)+' para a classe '+str(intervalo))
                    classe = intervalo
                    # print(classe)
                    lista_classes[classe].append(sample)
                    # print(str(sample)+' adicionado na classe '+str(classe))

    counts = []

    for classe in range(0, len(lista_classes)):
        counts.append(len(lista_classes[classe]))

    relative_freq = []

    for i in counts:
        freq = (i / len(dados)) * 100
        relative_freq.append(freq)

    intervals_min = []
    intervals_max = []

    minimum = min(dados)
    maximum = max(dados)

    Ai = (max(dados) - min(dados)) / n_classes

    for i in range(0, n_classes):
        intervals_min.append(minimum + i * Ai)

    for i in range(1, n_classes):
        intervals_max.append(i * Ai)

    intervals_max.append(maximum)

    return counts, relative_freq, intervals_min, intervals_max


def tabela_frequencias(dados):
    freq = pd.DataFrame()

    contagem, freq_relativa, intervalos_min, intervalos_max = classes_frequencias(dados)

    contagem = np.asarray(contagem)
    freq_relativa = np.asarray(freq_relativa)
    freq_acumulada = contagem.cumsum()

    freq_acum_dir = []
    for i in freq_acumulada:
        freq_acum_dir.append((i / len(dados)) * 100)
    freq_acum_dir = np.asarray(freq_acum_dir)

    intervalos_min = np.asarray(intervalos_min)
    intervalos_max = np.asarray(intervalos_max)
    # print(freq_relativa[::-1])

    inverse_freq = []
    for i in freq_relativa[::-1]:
        inverse_freq.append(i)

    freq.insert(loc=0, column='Lower limit', value=intervalos_min)
    freq.insert(loc=1, column='Upper limit', value=intervalos_max)
    freq.insert(loc=2, column='Lower limit (log)', value=np.log10(intervalos_min))
    freq.insert(loc=3, column='Absolut Frequency', value=contagem)
    freq.insert(loc=4, column='Relative Frequency (%)', value=freq_relativa)
    freq.insert(loc=5, column='Count', value=freq_acumulada)
    freq.insert(loc=6, column='Direct Cumulative Frequency (%)', value=freq_acum_dir)

    return freq

def clustered_df(X, n_clusters):
    model = KMeans(n_clusters=n_clusters, random_state=3425)
    model.fit(X)
    labels = model.predict(X)
    df_clustered = pd.DataFrame()
    df_clustered.insert(0, 'Relative Frequency (%)', X[:,0][::-1]*100)
    df_clustered.insert(1, 'Value', X[:,1])
    df_clustered.insert(2, 'Class', labels)

    means = []

    for classe in df_clustered.Class.unique():
        mean = np.mean(df_clustered.Value[df_clustered.Class == classe])
        means.append(mean)

    classes_zip = zip(df_clustered.Class.unique(), means)
    classes_zip = list(classes_zip)
    classes_zip = sorted(classes_zip, key=lambda x: x[1], reverse=True)

    anomalous = classes_zip[0][0]

    ordem = 1

    for n in classes_zip:
        if n[0] == anomalous:
            df_clustered.Class = df_clustered.Class.apply(lambda row: 'Anomalous Sample'
            if row == anomalous
            else row)
        else:
            df_clustered.Class = df_clustered.Class.apply(
                lambda row: str(ordem)+'º Order Background Sample'
                if row == n[0]
                else row)
            ordem = ordem + 1
    df_clustered.to_csv('df_clustered.csv')
    return df_clustered


def probscale_plot(df, var):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    plt.grid(True, which='both')

    for n in df.Class.unique():
        plt.plot(df['Relative Frequency (%)'][df.Class == n],
                 df[var][df.Class == n], 'o',
                 label=n, markersize=2.5)

    plt.xlabel('Cumulative Frequency (%)')
    plt.ylabel(str(var))
    plt.legend()

    ax.set_yscale('log')
    ax.set_xlim(0.5, 99.5)
    ax.set_xscale('prob')

    buf = io.BytesIO() # in-memory files
    plt.savefig(buf, format = "png") # save to the above file object
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()

    return data

