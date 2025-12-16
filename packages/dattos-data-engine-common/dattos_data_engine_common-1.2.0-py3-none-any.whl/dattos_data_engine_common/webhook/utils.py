import structlog
import httpx
import json

logger = structlog.stdlib.get_logger()


async def send_webhook_notification(
    webhook_uri, webhook_token, request_id, success, heartbeat_check, data
):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            webhook_uri,
            json={
                "requestId": request_id,
                "success": success,
                "heartbeatCheck": heartbeat_check,
                "data": json.dumps(data),
            },
            headers={"Authorization": f"Bearer {webhook_token}"},
        )
        logger.info(f"Webhook response: {response}")
        return response.is_success
