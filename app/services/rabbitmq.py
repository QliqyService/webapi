import logging

from faststream.rabbit import RabbitBroker, RabbitMessage
from loguru import logger as LOGGER

from app.services.base import BaseService


class RabbitMQClient(BaseService):
    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.client = RabbitBroker(url=url, timeout=timeout, log_level=logging.ERROR)
        self.timeout = timeout

    async def start(self):
        await self.client.connect()
        LOGGER.debug("[Broker Client] Connection initialized.")

    async def stop(self):
        await self.client.stop()

    async def request(self, queue: str, message: dict) -> RabbitMessage | None:
        """Метод для синхронного вызова удаленной функции

        Args:
            queue (str): имя очереди, которую слушает удаленный сервис и выполнит задачу
            message (dict): тело сообщения для передачи в удаленный сервис

        """
        try:
            response = await self.client.request(message=message, queue=queue, timeout=self.timeout)
            return response
        except Exception as e:
            LOGGER.error(f"Ошбика при вызове удаленной функции по адресу {queue}: {e}")
            return None

    async def publish(self, queue: str, message: dict) -> bool:
        """Метод для отправки сообщений в очередь RabbitMQ (fire-and-forget).

        Args:
            queue (str): имя очереди
            message (dict): тело сообщения (json-serializable)

        Returns:
            bool: True если отправка прошла без исключения, иначе False
        """
        try:
            await self.client.publish(message=message, queue=queue)
            LOGGER.debug(f"[Broker Client] Published message to {queue}")
            return True
        except Exception as e:
            LOGGER.error(f"Ошибка при публикации сообщения в очередь {queue}: {e}")
            return False
