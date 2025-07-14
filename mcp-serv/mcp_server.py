#!/usr/bin/env python3
"""
MCP Server для работы с проектами GameMaker Studio 2
Предоставляет инструменты для парсинга и анализа GMS2 проектов
"""

import asyncio
import argparse
import json
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

from gms2_parser import GMS2ProjectParser


class GMS2MCPServer:
    """MCP Сервер для работы с GameMaker Studio 2"""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path
        self.parser = None
        if project_path:
            self.parser = GMS2ProjectParser(project_path)
    
    def get_tools(self) -> List[Tool]:
        """Возвращает список доступных инструментов"""
        return [
            Tool(
                name="scan_gms2_project",
                description="Сканирует проект GameMaker Studio 2 и возвращает структуру файлов",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2 (содержащей .yyp файл)"
                        }
                    },
                    "required": ["project_path"]
                }
            ),
            Tool(
                name="get_gml_file_content",
                description="Получает содержимое конкретного GML файла",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Путь к GML файлу (относительный или абсолютный)"
                        }
                    },
                    "required": ["project_path", "file_path"]
                }
            ),
            Tool(
                name="get_room_info",
                description="Получает детальную информацию о комнате из .yy файла",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "room_name": {
                            "type": "string",
                            "description": "Имя комнаты"
                        }
                    },
                    "required": ["project_path", "room_name"]
                }
            ),
            Tool(
                name="get_object_info",
                description="Получает детальную информацию об объекте из .yy файла",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "object_name": {
                            "type": "string",
                            "description": "Имя объекта"
                        }
                    },
                    "required": ["project_path", "object_name"]
                }
            ),
            Tool(
                name="get_sprite_info",
                description="Получает информацию о спрайте",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "sprite_name": {
                            "type": "string",
                            "description": "Имя спрайта"
                        }
                    },
                    "required": ["project_path", "sprite_name"]
                }
            ),
            Tool(
                name="export_project_data",
                description="Экспортирует все данные проекта в текстовый формат (аналог функции из vibe2gml)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "save_to_file": {
                            "type": "boolean",
                            "description": "Сохранить результат в файл (по умолчанию false)",
                            "default": False
                        },
                        "output_file": {
                            "type": "string",
                            "description": "Путь для сохранения файла (если save_to_file=true)"
                        }
                    },
                    "required": ["project_path"]
                }
            ),
            Tool(
                name="list_project_assets",
                description="Получает список всех ассетов проекта по категориям",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к папке проекта GMS2"
                        },
                        "category": {
                            "type": "string",
                            "description": "Фильтр по категории (Objects, Scripts, Rooms, Sprites, etc.)",
                            "enum": ["Objects", "Scripts", "Rooms", "Sprites", "Notes", "Tile Sets", "Timelines", "Fonts", "Sounds", "Extensions"]
                        }
                    },
                    "required": ["project_path"]
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Обрабатывает вызовы инструментов"""
        try:
            if name == "scan_gms2_project":
                return await self._scan_project(arguments)
            elif name == "get_gml_file_content":
                return await self._get_gml_content(arguments)
            elif name == "get_room_info":
                return await self._get_room_info(arguments)
            elif name == "get_object_info":
                return await self._get_object_info(arguments)
            elif name == "get_sprite_info":
                return await self._get_sprite_info(arguments)
            elif name == "export_project_data":
                return await self._export_project_data(arguments)
            elif name == "list_project_assets":
                return await self._list_project_assets(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
    
    async def _scan_project(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Сканирует проект GMS2"""
        project_path = arguments.get("project_path")
        if not project_path:
            return [TextContent(type="text", text="Error: project_path is required")]
        
        parser = GMS2ProjectParser(project_path)
        result = parser.scan_project()
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        # Форматируем результат для удобного чтения
        output = []
        output.append(f"GameMaker Studio 2 Project: {result['project_name']}")
        output.append(f"Path: {result['project_path']}")
        output.append(f"Total GML Files: {result['total_gml_files']}")
        output.append("")
        
        # Показываем структуру по категориям
        for category, info in result['categories'].items():
            if info['assets']:
                output.append(f"{category}: {len(info['assets'])} assets")
                for asset in info['assets']:
                    gml_count = len(asset['gml_files'])
                    yy_status = "✓" if asset['yy_file'] else "✗"
                    output.append(f"  - {asset['name']} (GML: {gml_count}, YY: {yy_status})")
        
        output.append("")
        output.append("Recent GML Files:")
        for i, (display_name, _, relative_path, _) in enumerate(result['gml_files'][:10]):
            output.append(f"  {i+1}. {display_name} ({relative_path})")
        
        if len(result['gml_files']) > 10:
            output.append(f"  ... and {len(result['gml_files']) - 10} more files")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _get_gml_content(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Получает содержимое GML файла"""
        project_path = arguments.get("project_path")
        file_path = arguments.get("file_path")
        
        if not project_path or not file_path:
            return [TextContent(type="text", text="Error: project_path and file_path are required")]
        
        parser = GMS2ProjectParser(project_path)
        
        # Если путь относительный, делаем его абсолютным
        if not os.path.isabs(file_path):
            file_path = os.path.join(project_path, file_path)
        
        result = parser.get_gml_content(file_path)
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        output = []
        output.append(f"GML File: {result['relative_path']}")
        output.append(f"Lines: {result['line_count']}")
        output.append("-" * 50)
        output.append(result['content'])
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _get_room_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Получает информацию о комнате"""
        project_path = arguments.get("project_path")
        room_name = arguments.get("room_name")
        
        if not project_path or not room_name:
            return [TextContent(type="text", text="Error: project_path and room_name are required")]
        
        parser = GMS2ProjectParser(project_path)
        result = parser.get_room_info(room_name)
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        output = []
        output.append(f"Room Information: {result['room_name']}")
        output.append("=" * 50)
        output.append("")
        output.append("Formatted View:")
        output.append(result['formatted_info'])
        output.append("")
        output.append("Raw Data Available:")
        output.append(f"- YY File: {result['yy_path']}")
        output.append(f"- Layers: {len(result['data'].get('layers', []))}")
        output.append(f"- Room Settings: {'Yes' if result['data'].get('roomSettings') else 'No'}")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _get_object_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Получает информацию об объекте"""
        project_path = arguments.get("project_path")
        object_name = arguments.get("object_name")
        
        if not project_path or not object_name:
            return [TextContent(type="text", text="Error: project_path and object_name are required")]
        
        parser = GMS2ProjectParser(project_path)
        result = parser.get_object_info(object_name)
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        output = []
        output.append(f"Object Information: {result['object_name']}")
        output.append("=" * 50)
        output.append("")
        output.append("Formatted View:")
        output.append(result['formatted_info'])
        output.append("")
        output.append("Raw Data Available:")
        output.append(f"- YY File: {result['yy_path']}")
        output.append(f"- Events: {len(result['data'].get('eventList', []))}")
        output.append(f"- Physics: {'Enabled' if result['data'].get('physicsObject') else 'Disabled'}")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _get_sprite_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Получает информацию о спрайте"""
        project_path = arguments.get("project_path")
        sprite_name = arguments.get("sprite_name")
        
        if not project_path or not sprite_name:
            return [TextContent(type="text", text="Error: project_path and sprite_name are required")]
        
        parser = GMS2ProjectParser(project_path)
        result = parser.get_sprite_info(sprite_name)
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        output = []
        output.append(f"Sprite Information: {result['sprite_name']}")
        output.append("=" * 50)
        output.append("")
        output.append(f"Sprite Path: {result['sprite_path']}")
        output.append(f"YY File: {'Yes' if result['yy_path'] else 'No'}")
        output.append(f"Frame Count: {len(result['frames'])}")
        
        if result['frames']:
            output.append("")
            output.append("Frames:")
            for i, frame in enumerate(result['frames']):
                output.append(f"  {i+1}. {frame['filename']}")
        
        return [TextContent(type="text", text="\n".join(output))]
    
    async def _export_project_data(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Экспортирует все данные проекта"""
        project_path = arguments.get("project_path")
        save_to_file = arguments.get("save_to_file", False)
        output_file = arguments.get("output_file")
        
        if not project_path:
            return [TextContent(type="text", text="Error: project_path is required")]
        
        parser = GMS2ProjectParser(project_path)
        export_data = parser.export_all_data()
        
        if save_to_file:
            if not output_file:
                # Генерируем имя файла по умолчанию
                project_name = os.path.basename(project_path)
                output_file = f"{project_name}_export.txt"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                
                return [TextContent(type="text", text=f"Project data exported to: {output_file}\n\nFile size: {len(export_data)} characters")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error saving file: {str(e)}\n\nExport data:\n{export_data}")]
        else:
            # Возвращаем данные напрямую
            return [TextContent(type="text", text=export_data)]
    
    async def _list_project_assets(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Список ассетов проекта"""
        project_path = arguments.get("project_path")
        category_filter = arguments.get("category")
        
        if not project_path:
            return [TextContent(type="text", text="Error: project_path is required")]
        
        parser = GMS2ProjectParser(project_path)
        result = parser.scan_project()
        
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]
        
        output = []
        output.append(f"Assets in {result['project_name']}:")
        output.append("=" * 50)
        
        categories_to_show = [category_filter] if category_filter else result['categories'].keys()
        
        for category in categories_to_show:
            if category in result['categories']:
                info = result['categories'][category]
                if info['assets']:
                    output.append(f"\n{category} ({len(info['assets'])} items):")
                    for asset in info['assets']:
                        gml_files = len(asset['gml_files'])
                        yy_file = "✓" if asset['yy_file'] else "✗"
                        output.append(f"  - {asset['name']} (GML: {gml_files}, YY: {yy_file})")
                        
                        # Показываем GML файлы если их немного
                        if gml_files > 0 and gml_files <= 5:
                            for gml in asset['gml_files']:
                                output.append(f"    • {gml['name']}")
        
        return [TextContent(type="text", text="\n".join(output))]


async def main():
    """Главная функция запуска сервера"""
    # Загружаем переменные окружения из config.env
    load_dotenv('config.env')
    
    parser = argparse.ArgumentParser(description="GameMaker Studio 2 MCP Server")
    parser.add_argument("--project-path", type=str, help="Path to GMS2 project (overrides config.env)")
    args = parser.parse_args()
    
    # Определяем путь к проекту: командная строка > config.env > None
    project_path = args.project_path or os.getenv('GMS2_PROJECT_PATH')
    
    if project_path and not os.path.exists(project_path):
        print(f"Warning: Project path does not exist: {project_path}")
    
    # Создаем экземпляр сервера
    mcp_server = GMS2MCPServer(project_path)
    
    # Создаем MCP Server
    server = Server("gms2-mcp-server")
    
    # Регистрируем список инструментов
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return mcp_server.get_tools()
    
    # Регистрируем обработчик вызовов инструментов
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        return await mcp_server.handle_tool_call(name, arguments)
    
    # Запускаем сервер через stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
