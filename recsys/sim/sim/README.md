# Модуль Sim

Симулятор поведения пользователей рекомендательного сервиса.
Реализован как среда OpenAI gym.

Запуск симулятора поделен на условные "дни".
В конце каждого дня симулятор останавливается, чтобы была возможность обработать данные, собранные за предыдущий день и обновить сервис рекомендаций.


## Инструкция

1. Создаем чистый env с python 3.7
   - Устанавливаем Python 3.7 (если нет)
    ```
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt install python3.7
   sudo apt-get install python3.7-dev python3.7-venv
   ```
   - Создаем venv
   ```
   python3.7 -m venv venv_recsys
   source venv_recsys/bin/activate
   ```
2. Устанавливаем зависимости
   ```
   pip install --upgrade pip
   pip install --upgrade setuptools
   pip install -r requirements.txt
   ``` 
3. Добавляем текущую директорию в $PYTHONPATH
   ```
   export PYTHONPATH=${PYTHONPATH}:.
   ```
4. Пометить папки sim и s7rec в PyCharm as Source root 

5. Симулятор можно запустить в "ручном" режиме, чтобы самостоятельно подбирать рекомендации для пользователя. 
   Это режим для ознакомления с симулятором.
   ```
   python sim/run.py --episodes 1 --recommender console --config config/env.yml --seed 31337
   ```
6. Запуск симулятора в режиме "трафика".
   Параметр `--episodes` определяет число сгенерированных пользовательских сессий.
   ```
   python sim/run.py --episodes 1000 --recommender remote --config config/env.yml --seed 31337
   ```