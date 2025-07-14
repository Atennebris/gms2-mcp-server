#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    # Очищаем sys.argv для чистого запуска
    sys.argv = ["mcp_server.py"]
    
    # Переходим в корень проекта (на уровень выше от tools/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Добавляем папки mcp-serv и tools в sys.path
    sys.path.insert(0, os.path.join(project_root, 'mcp-serv'))
    sys.path.insert(0, os.path.join(project_root, 'tools'))
    
    # Импортируем и запускаем mcp_server из mcp-serv/
    import mcp_server
    import asyncio
    
    # Запускаем main функцию (путь будет загружен из config.env)
    asyncio.run(mcp_server.main()) 