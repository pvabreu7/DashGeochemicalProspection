import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

sns.set()

def vis_logprob(dados):
    x = np.sort(dados)
    y = np.arange(1, len(x)+1)/len(x)
    
    fig = plt.figure(figsize=(14,10))
    
    plt.grid(True, which="both")
    plt.semilogy(y[::-1], x, 'o', markersize=2.5)
    plt.title(str(dados.name) +' Log x Probabilidade Acumulada')
    plt.xlabel('Probabilidade (%)')
    plt.ylabel(str(dados.name))
    
    plt.show()
    
    vis_dist(dados)

    return x, y


def vis_dist(dados):

    fig = plt.figure(figsize=(14,4))

    plt.subplot(121)
    sns.distplot(dados, color='orange')
    plt.title('Distribuição '+str(dados.name))

    plt.subplot(122)
    sns.boxplot(dados, color='orange')
    plt.title('Boxplot '+str(dados.name))

    plt.show()


def determinar_param(dados):
    n = dados.count()
    k = 1 + 3.3*(np.log10(n))
    T = np.max(dados)
    t = np.min(dados)
    Ai = (T-t)/k
    std = np.std(dados)
    print(dados.describe())
    return T, t, k, Ai, std

classe1 = []
classe2 = []
classe3 = []
classe4 = []
classe5 = []
classe6 = []
classe7 = []
classe8 = []
classe9 = []
contagem = []


def classes_frequencias(dados):
    maximo, minimo, k, Ai, std = determinar_param(dados)

    for i in dados:    
        if i >= i and i < Ai:
            classe1.append(i)
        
        if i >= Ai and i < 2*Ai:
            classe2.append(i)
    
        if i >= 2*Ai and i < 3*Ai:
            classe3.append(i)
    
        if i >= 3*Ai and i < 4*Ai:
            classe4.append(i)
    
        if i >= 4*Ai and i < 5*Ai:
            classe5.append(i)
    
        if i >= 5*Ai and i < 6*Ai:
            classe6.append(i)
    
        if i >= 6*Ai and i < 7*Ai:
            classe7.append(i)
    
        if i >= 7*Ai and i < 8*Ai:
            classe8.append(i)
    
        if i >= 8*Ai:
            classe9.append(i)
    
    
    contagem.append(float(len(classe1))); contagem.append(float(len(classe2))); contagem.append(float(len(classe3)));
    contagem.append(float(len(classe4))); contagem.append(float(len(classe5))); contagem.append(float(len(classe6)));
    contagem.append(float(len(classe7))); contagem.append(float(len(classe8))); contagem.append(float(len(classe9)))

    freq_relativa = []

    for i in contagem:
        freq = (i/315)*100
        freq_relativa.append(freq)
    
    intervalos_min = []
    intervalos_max = []
    
    for i in range(0,9):
        intervalos_min.append(minimo +i*Ai)
        
    for i in range(1,9):
        intervalos_max.append(i*Ai)
    intervalos_max.append(maximo)

    return contagem, freq_relativa, intervalos_min, intervalos_max


def tabela_frequencias(dados):

    freq = pd.DataFrame()

    contagem, freq_relativa, intervalos_min, intervalos_max = classes_frequencias(dados)

    contagem = np.asarray(contagem)
    freq_relativa = np.asarray(freq_relativa)
    freq_acumulada = contagem.cumsum()
    freq_acum_dir = []
    for i in freq_acumulada:
        freq_acum_dir.append(i/315)
    freq_acum_dir = np.asarray(freq_acum_dir)
    intervalos_min = np.asarray(intervalos_min)
    intervalos_max = np.asarray(intervalos_max)

    freq.insert(loc=0, column='Mínimo', value=intervalos_min)
    freq.insert(loc=1, column='Máximo', value=intervalos_max)
    freq.insert(loc=2, column='Mínimo (log)', value=np.log10(intervalos_min))
    freq.insert(loc=3, column='Frequência Absoluta', value=contagem)
    freq.insert(loc=4, column='Frequência Relativa (%)', value=freq_relativa)
    freq.insert(loc=5, column='Frequência Acumulada', value=freq_acumulada)
    freq.insert(loc=6, column='Frequência Acumulada Direta (%)', value=freq_acum_dir)
    freq.insert(loc=7, column='Frequência Acumulada Invertida (%)', value=freq_acum_dir[::-1])

    freq.drop(axis=0, index=freq[freq['Frequência Absoluta'] == 0].index, inplace=True)

    return freq