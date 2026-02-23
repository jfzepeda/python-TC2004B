import numpy as np

def create_train_test(data, test_ratio, seed):
    '''Realiza el split de los datos en
       training y test set.

       Parámetros
       ----------
       data: pd.DataFrame
           Matriz de datos.
       test_ratio: float64
           Proporción de datos en el test set.
       seed: int64
           Semilla para generar los números aleatorios.

       Output
       ------
       pd.DataFrame, pd.DataFrame
           Un data frame con el training set
           y otro data frame con el test set.
    '''

    ## Inicializamos la semilla
    np.random.seed(seed)

    ## Creamos un arreglo con las posiciones de
    ## los datos seleccionadas de forma aleatoria
    idx = np.random.choice(len(data), size=len(data), replace=False)
    

    ## Determinamos cuántas observaciones
    ## se incluirán en el test set
    test_size = int(len(data) * test_ratio)

    ## Creamos el training y test set seleccionando
    ## los índices correspondientes que generamos
    test_idx = idx[:test_size]
    train_idx = idx[test_size:]

    train_set = data.iloc[train_idx, :]
    test_set = data.iloc[test_idx, :]

    ## Regresamos estos data frames
    ## como resultado de la función
    return train_set, test_set
