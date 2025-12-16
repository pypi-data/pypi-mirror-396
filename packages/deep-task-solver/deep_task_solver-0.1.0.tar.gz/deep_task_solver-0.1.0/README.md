# deep-task-solver

Минимальная библиотека для отправки текста задач в DeepSeek API.

## Установка

pip install deep-task-solver

## Настройка ключа

Linux / macOS:
export DEEPSEEK_API_KEY="ваш_api_ключ"

Windows (PowerShell):
setx DEEPSEEK_API_KEY "ваш_api_ключ"

## Использование

from deep_task_solver import solve

text = input("Введите условие задачи: ")
answer = solve(text)
print(answer)
