import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app_config import AppConfig
from dds_loader.dds_message_processor_job import DdsMessageProcessor
from dds_loader.repository.dds_repository import DdsRepository

app = Flask(__name__)



@app.get('/health')
def hello_world():
    return 'healthy'


if __name__ == '__main__':
   # Устанавливаем уровень логгирования в Debug, чтобы иметь возможность просматривать отладочные логи.
    app.logger.setLevel(logging.ERROR)

    # Инициализируем конфиг. Для удобства, вынесли логику получения значений переменных окружения в отдельный класс.
    config = AppConfig()

    consumer = config.kafka_consumer()
    producer = config.kafka_producer()
    stg_repository = DdsRepository
    # db = config.pg_warehouse_db()
    _batch_size = 100
    logger = logging.Logger(name='App1')
    # Инициализируем процессор сообщений.
    # Пока он пустой. Нужен для того, чтобы потом в нем писать логику обработки сообщений из Kafka.
    # proc = SampleMessageProcessor(app.logger)

    proc = DdsMessageProcessor(
        consumer,producer,stg_repository,_batch_size,app.logger
    )

    # Запускаем процессор в бэкграунде.
    # BackgroundScheduler будет по расписанию вызывать функцию run нашего обработчика(SampleMessageProcessor).
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=proc.run, trigger="interval", seconds=config.DEFAULT_JOB_INTERVAL)
    scheduler.start()

    # стартуем Flask-приложение.
    app.run(debug=False, host='0.0.0.0',port=5005, use_reloader=False)