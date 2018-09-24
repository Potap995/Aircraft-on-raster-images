import json
import Code.CNN as CNN
import Code.SupFunc as sp

''' Скрипт обрабатывающий сыпые данные и запускающий тренировку подели'''

def main():
    print("Start")
    path_to_data = '../Resources'
    try:
        sp.GetGreyData(path_to_data, 'planesnet.json')
        print("Making grey data has been ended")
    except:
        print("Ошибка при открытии или чтении 'planesnet.json'")
        return
    sp.MakeTrainEvalData(path_to_data, 'planesnetgrey.json')
    print("Making train and eval data has been ended")

    #Загрузка данных в нужном формате
    planesTrain = json.load(open(path_to_data + '/planestrain.json'))
    planesEval = json.load(open(path_to_data + '/planeseval.json'))
    print("End loading")
    print("Start traning")
    #Тренировка
    CNN.TrainModel(planesTrain, planesEval)
    print("Done")

if __name__ == "__main__":
  main()