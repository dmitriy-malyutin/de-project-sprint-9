import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app_config import AppConfig
from cdm_loader.cdm_message_processor_job import CdmMessageProcessor
from cdm_loader.repository.cdm_repository import CdmRepository

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
    cdm_repository = CdmRepository
    # db = config.pg_warehouse_db()
    _batch_size = 100
    logger = logging.Logger(name='App1')
    # Инициализируем процессор сообщений.
    # Пока он пустой. Нужен для того, чтобы потом в нем писать логику обработки сообщений из Kafka.
    # proc = SampleMessageProcessor(app.logger)

    proc = CdmMessageProcessor(
        consumer,producer,cdm_repository,_batch_size,app.logger
    )

    # Запускаем процессор в бэкграунде.
    # BackgroundScheduler будет по расписанию вызывать функцию run нашего обработчика(SampleMessageProcessor).
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=proc.run, trigger="interval", seconds=config.DEFAULT_JOB_INTERVAL)
    scheduler.start()

    # стартуем Flask-приложение.
    app.run(debug=False, host='0.0.0.0',port=5005, use_reloader=False)