import  io
from socket import *
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
#import Code.SupFunc as sp
import SupFunc as sp
#import Code.CNN as CNN
import CNN as CNN



def GetAns(data, model):
    ''' Функция получения предсказания объекта на фотографии'''

    stream = io.BytesIO(data)
    img = Image.open(stream)
    img = np.array(img, dtype=np.float32)[:, :, 0:3]
    img = sp.Kontrast(sp.RGBtogrey(img))[:, :, 0]
    img = np.array(img, dtype=np.float32)
    # plt.imshow(img)
    # plt.show()
    ans = CNN.Predict(img, model)
    print(ans)
    return ans


def InitServer():
    '''Функция задания сервера'''
    try:
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(('127.0.0.1', 10001))
        server.listen(1)
    except:
        server = None
        print("Сервер на этом порту уже запущенн")
    return server

def InitTrainedModel(path):
    '''Функция загрузки модели и проверки на что что она натренирована'''
    model = CNN.InitModel(path)
    try:
        img = Image.open("../Resources/TestImg.png")
        img = np.array(img, dtype=np.float32)[:, :, 0:3]
        img = sp.Kontrast(sp.RGBtogrey(img))[:, :, 0]
        img = np.array(img, dtype=np.float32)
        # plt.imshow(img)
        # plt.show()
        ans = CNN.Predict(img, model)
        return model
    except:
        print("Модель не обучена")
        return None


def Main():
    '''Логика работы сервера'''

    server = InitServer() #Задаем параметры сервера
    model = InitTrainedModel('../Resources/CNN_model')#Подгружаем модель
    if (server == None or model == None):
        return
    while(True):
        print("Смотрим подключения")
        try:
            # Принимаем подключение
            conn, addr = server.accept()
        except:
            print("Ошибка во время приема")
        else:
            try:
                # Получаем данные
                data = conn.recv(2048)
                print(data)
                try:
                    # Предсказываем класс и отправляем ответ
                    ans = GetAns(data, model)
                    conn.sendall(bytes([ans]))
                except:
                    print("Ошибка возникшая во вребя обработки")
                    conn.sendall(bytes([3]))
            except:
                print("Ошибка при получении данных")
            finally:
                # Закрываем подключение
                conn.shutdown(SHUT_WR)
                conn.close()

if __name__ == "__main__":
  Main()
