from abc import ABC, abstractmethod
import multiprocessing
import structlog
import asyncio
import traceback
from dattos_data_engine_common.webhook.models import BaseAsyncRequest
from dattos_data_engine_common.webhook.utils import send_webhook_notification

logger = structlog.stdlib.get_logger()


def execute_process_wrapper(cls_type, request, kwargs, result_queue):
    try:
        # Cria instância real (no processo filho!)
        service = cls_type()
        # Roda o método execute de forma síncrona
        result_data = service.execute(request, **kwargs)
        result_queue.put({"success": True, "data": result_data})
    except Exception as exc:
        logger.error("Erro no processo filho", exc_info=True)
        result_queue.put(
            {
                "success": False,
                "error_message": str(exc),
                "trace": traceback.format_exc(),
            }
        )


class BaseWebhookService(ABC):
    async def process_async(self, request: BaseAsyncRequest, **kwargs):
        heartbeat_task = None
        result_queue = multiprocessing.Queue()
        proc = None        
        try:
            # Inicia o processo filho
            proc = multiprocessing.Process(
                target=execute_process_wrapper,
                args=(self.__class__, request, kwargs, result_queue),
            )
            proc.start()

            async def heartbeat_loop():
                while proc.is_alive():
                    await asyncio.sleep(request.heartbeat_check_seconds_interval)
                    try:
                        if not await self.send_check_notification(
                            request.webhook_uri,
                            request.webhook_token,
                            request.request_id,
                        ):
                            logger.error(
                                "Heartbeat check failed, terminating process..."
                            )
                            if proc.is_alive():
                                proc.terminate()                                
                            return  # Sai do loop
                    except Exception as exc:
                        logger.error(
                            "Heartbeat notification failed, terminating process...",
                            exc_info=True,
                        )
                        if proc.is_alive():
                            proc.terminate()                            
                        return  # Sai do loop

            if request.heartbeat_check_seconds_interval:
                heartbeat_task = asyncio.create_task(heartbeat_loop())

            # Espera término do processo
            while proc.is_alive():
                await asyncio.sleep(0.5)
            proc.join(timeout=0.1)

            # Cancela o heartbeat (caso ele ainda rode, evita await pendente)
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            # Coleta resultado
            try:
                result_info = result_queue.get_nowait()
            except Exception:
                result_info = None

            if result_info:
                if result_info.get("success"):
                    await self.send_success_notification(
                        request.webhook_uri,
                        request.webhook_token,
                        request.request_id,
                        data=result_info.get("data"),
                    )
                else:
                    error_message = result_info.get("error_message", "Unknown error")
                    logger.error(error_message)
                    await self.send_failure_notification(
                        request.webhook_uri,
                        request.webhook_token,
                        request.request_id,
                        error_message=error_message,
                    )                    

        except Exception as e:
            logger.error("Erro durante o processamento principal.", exc_info=True)
            await self.send_failure_notification(
                request.webhook_uri,
                request.webhook_token,
                request.request_id,
                error_message=str(e),
            )
            raise
        finally:
            # Garante que processo morra!
            if proc and proc.is_alive():
                proc.terminate()
                proc.join(timeout=1)
            if heartbeat_task and not heartbeat_task.done():
                heartbeat_task.cancel()  # Não precisa de await aqui

    async def send_success_notification(
        self, webhook_uri, webhook_token, request_id, data
    ):
        await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=True,
            heartbeat_check=False,
            data=data,
        )

    async def send_failure_notification(
        self, webhook_uri, webhook_token, request_id, error_message
    ):
        await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=False,
            heartbeat_check=False,
            data={"message": error_message},
        )

    async def send_check_notification(self, webhook_uri, webhook_token, request_id):
        return await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=True,
            heartbeat_check=True,
            data=None,
        )

    @abstractmethod
    def execute(self, request: BaseAsyncRequest, **kwargs):
        pass
