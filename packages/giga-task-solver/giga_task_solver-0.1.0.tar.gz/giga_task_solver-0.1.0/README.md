# giga-task-solver

Минимальная библиотека для отправки текста задач в GigaChat API.

## Установка
```bash
pip install giga-task-solver
```

## Настройка ключа

```bash
export GIGACHAT_API_KEY="ваш_api_ключ"
```

## Использование

```python
from deep_task_solver import solve

text = input("Введите условие задачи: ")
answer = solve(text)
print(answer)
```
