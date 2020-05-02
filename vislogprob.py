import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def logprob(data):
    y = np.sort(data)
    x = np.arange(1, len(y)+1)/len(y)

    return x, y



def determinar_param(dados):
    n = dados.count()
    k = 1 + 3.3*(np.log10(n))
    T = np.max(dados)
    t = np.min(dados)
    Ai = (T-t)/k
    std = np.std(dados)
    #print(dados.describe())
    return T, t, k, Ai, std




def classes_frequencias(dados):
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

def clustered_df(X, n_clusters):
    model = KMeans(n_clusters=n_clusters, random_state=3425)
    model.fit(X)
    labels = model.predict(X)
    df_clustered = pd.DataFrame()
    df_clustered.insert(0, 'Prob', X[:,0]*100)
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

    return df_clustered