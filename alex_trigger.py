#!/usr/bin/env python3
"""
Скрипт для активации режима Alex в консольных ботах
Использование: python alex_trigger.py
"""

import sys
import os

def trigger_alex_mode():
    """Активирует режим Alex во всех ботах"""
    
    # Список файлов ботов
    bot_files = ['bybit_only.py', 'funding_01_watch.py']
    
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"🛑 Активация режима Alex в {bot_file}...")
            
            # Читаем файл
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем alex_mode = False на alex_mode = True
            if 'alex_mode = False' in content:
                content = content.replace('alex_mode = False', 'alex_mode = True')
                
                # Записываем обратно
                with open(bot_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Режим Alex активирован в {bot_file}")
            else:
                print(f"⚠️  Переменная alex_mode не найдена в {bot_file}")
        else:
            print(f"❌ Файл {bot_file} не найден")
    
    print("\n🛑 Режим Alex активирован во всех консольных ботах!")
    print("Перезапустите боты для применения изменений.")

def restore_alex_mode():
    """Восстанавливает нормальный режим во всех ботах"""
    
    bot_files = ['bybit_only.py', 'funding_01_watch.py']
    
    for bot_file in bot_files:
        if os.path.exists(bot_file):
            print(f"✅ Восстановление режима Alex в {bot_file}...")
            
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'alex_mode = True' in content:
                content = content.replace('alex_mode = True', 'alex_mode = False')
                
                with open(bot_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Режим Alex восстановлен в {bot_file}")
            else:
                print(f"⚠️  Переменная alex_mode = True не найдена в {bot_file}")
        else:
            print(f"❌ Файл {bot_file} не найден")
    
    print("\n✅ Режим Alex восстановлен во всех консольных ботах!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_alex_mode()
    else:
        trigger_alex_mode()
