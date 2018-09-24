import json
import numpy as np



def Kontrast(bands, lower_percent=2, higher_percent=98):
    ''' Функция контрасного фильтра'''
    out = np.zeros_like(bands)
    for i in range(3):
        a = 0 #np.min(band)
        b = 255  #np.max(band)
        c = np.percentile(bands[:,:,i], lower_percent)
        d = np.percentile(bands[:,:,i], higher_percent)
        t = a + (bands[:,:,i] - c) * (b - a) / (d - c)
        t[t<a] = a
        t[t>b] = b
        out[:,:,i] =t
    return out.astype(np.uint8)



def RGBtogrey(img):
    ''' Функция черно-белого фильтра'''
    imgn = np.zeros_like(img)
    for i in range(20):
        for j in range(20):
            a = img[i][j][0]
            b = img[i][j][1]
            c = img[i][j][2]
            S = (a + b + c) // 3
            imgn[i][j][0] = S
            imgn[i][j][1] = S
            imgn[i][j][2] = S
    return imgn



def UnisonShuffle(a, b):
    ''' Функция совместного перемешивания'''
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]



def GetGreyData(path_to_data, file):
    ''' Функция переводящая сырые данные в удобные для работы'''
    # Загружаем данные
    planes = json.load(open(path_to_data + '/' + file))
    Data = np.array(planes['data'], dtype=np.float32)
    Labels = planes['labels']
    # Приводим к виду (n, m, 3)
    n = Data.shape[0]
    Data.shape = (n, 3, 20, 20)
    Data = np.transpose(Data, (0, 2, 3, 1))
    NewData = np.zeros((n, 20, 20, 3))
    # Делаем картинки черно-белыми и более контрастными
    for i in range(n):
        NewData[i] = Kontrast(RGBtogrey(Data[i]))
    NewData = NewData[:,:,:,0]
    # Сохраняем
    planesNew = {"data": NewData.tolist(), "labels": Labels}
    with open(path_to_data + "/planesnetgrey.json", "w", encoding="utf-8") as file:
        json.dump(planesNew, file)



def MakeTrainEvalData(path_to_data, file):
    ''' Функция разделяющая на данные для тренировки и проверки'''
    # Загружаем данные
    planes = json.load(open(path_to_data + '/' + file))
    Data = np.array(planes['data'])
    Labels = np.array(planes['labels'])
    # Перемешиваем(внутри одного типа)
    np.random.shuffle(Data[0:8000])
    np.random.shuffle(Data[8000:32000])
    # Разделяем данные
    TrainData = np.concatenate((Data[0:7000], Data[8000:29000]), axis=0)
    TrainLabels = np.concatenate((Labels[0:7000], Labels[8000:29000]), axis=0)
    EvalData = np.concatenate((Data[7000:8000], Data[29000:32000]), axis=0)
    EvalLabels = np.concatenate((Labels[7000:8000], Labels[29000:32000]), axis=0)
    # Перемешиваем
    TrainData, TrainLabels = UnisonShuffle(TrainData, TrainLabels)
    EvalData, EvalLabels = UnisonShuffle(EvalData, EvalLabels)

    # Сохраняем в json файлы
    planesTrain = {"data": TrainData.tolist(),
                   "labels": TrainLabels.tolist()}
    with open(path_to_data + "/planestrain.json", "w", encoding="utf-8") as file:
        json.dump(planesTrain, file)

    planesEval = {"data": EvalData.tolist(),
                  "labels": EvalLabels.tolist()}
    with open(path_to_data + "/planeseval.json", "w", encoding="utf-8") as file:
        json.dump(planesEval, file)

