import json
import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

def cnn_model_fn(features, labels, mode):
    '''Функция описывающая модель'''

    input_layer = tf.reshape(features, [-1, 20, 20, 1])
    #1.	Свёрточный слой#1: Применяет 32 фильтра 5х5, с функцией активации ReLU
    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        filters=32,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu)
    #2.	Слой подвыборки#1: Объединяет фрагменты 2х2 в одно значение выбирая максимальный
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)

    #3.	Свёрточный слой#2: Применяет 64 фильтра 5х5, с функцией активации ReLU
    conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=64,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu)
    #4.	Слой подвыборки#2: Опять объединяет фрагменты 2х2 в одно значение выбирая максимальный
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)
    pool2_flat = tf.reshape(pool2, [-1, 5 * 5 * 64])

    # Плотный слой
    dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)

    dropout = tf.layers.dropout(
        inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

    # Уровень логирования
    logits = tf.layers.dense(inputs=dropout, units=2)

    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    #Расчет функции потерь по Softmax
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}
    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)




def InitModel(path_to_model):
    '''Функция загрузки модели'''
    planes_classifier = tf.estimator.Estimator(
        model_fn=cnn_model_fn, model_dir=path_to_model)
    return planes_classifier





def TrainModel(TrainData, EvalData):
    # Загружаем тренировочные и проверочные данные
    train_data = np.array(TrainData["data"], dtype=np.float32)
    train_labels = np.array(TrainData["labels"], dtype=np.int32)
    eval_data = np.array(EvalData["data"], dtype=np.float32)
    eval_labels = np.array(EvalData["labels"], dtype=np.int32)

    # Создаем модель и видимые результаты
    path_to_model = '../Resources/CNN_model'

    planes_classifier = InitModel(path_to_model)
    tensors_to_log = {"probabilities": "softmax_tensor"}
    logging_hook = tf.train.LoggingTensorHook(
        tensors=tensors_to_log, every_n_iter=50)

    # Тренируе модель
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=train_data,
        y=train_labels,
        batch_size=100,
        num_epochs=None,
        shuffle=True)
    planes_classifier.train(
        input_fn=train_input_fn,
        steps=10000,
        hooks=[logging_hook])

    print("Training end")
    # Проверяем модель
    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=eval_data,
        y=eval_labels,
        num_epochs=1,
        shuffle=False)
    eval_results = planes_classifier.evaluate(input_fn=eval_input_fn)

    # Сохраняем результат проверки
    with open("../Resources/EvalResults.txt", "w", encoding="utf-8") as file:
        file.write(str(eval_results))


def Predict(predict_data, model):
    ''' Функция получегния предсказания от модели'''
    predict_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=predict_data, shuffle=False)
    predictions = model.predict(input_fn=predict_input_fn)
    return list(predictions)[0]['classes']

