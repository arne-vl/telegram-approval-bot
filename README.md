# telegram-approval-bot
Telegram approval bot that uses RabbitMQ. Used for approving repository creation.

<a href="https://hub.docker.com/r/arnevl/telegram-approval-bot" target="_blank">
    <img alt="Static Badge" src="https://img.shields.io/badge/docker-arnevl/telegram--approval--bot-blue">
</a>

Queue message payload should be the following json format:
```json
{
    "repo_name": "{your_repo_name}"
}
```

## Environment variables
| Variable                     | Description                                                          |
|------------------------------|----------------------------------------------------------------------|
| `TELEGRAM_API_TOKEN`         | The API token used to authenticate with the Telegram Bot API.        |
| `CHAT_ID`                    | The unique identifier for the chat where messages will be sent.      |
| `RABBITMQ_URL`               | The URL for connecting to the RabbitMQ broker.                       |
| `RABBITMQ_APPROVAL_QUEUE`    | The name of the queue where approval request messages are sent.      |
| `RABBITMQ_APPROVED_QUEUE`    | The name of the queue where approval confirmation messages are sent. |
