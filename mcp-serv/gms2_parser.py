"""
GameMaker Studio 2 Project Parser Module
Извлеченная логика парсинга из оригинального скрипта vibe2gml
"""

import os
import json
import re
from collections import Counter
from typing import List, Dict, Tuple, Optional, Any


class GMS2ProjectParser:
    """Парсер для проектов GameMaker Studio 2"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_gml_files_details = []  # (display_name, gml_path, relative_path, asset_yy_path)
        
    def scan_project(self) -> Dict[str, Any]:
        """Сканирует проект и возвращает структуру файлов"""
        if not os.path.exists(self.project_path):
            return {"error": f"Project path not found: {self.project_path}"}
            
        # Проверяем наличие .yyp файла
        yyp_files = [f for f in os.listdir(self.project_path) if f.endswith('.yyp')]
        if not yyp_files:
            return {"error": f"No .yyp file found in {self.project_path}"}
            
        self.project_gml_files_details.clear()
        
        # Категории ассетов
        asset_categories = {
            "Objects": "objects",
            "Scripts": "scripts", 
            "Rooms": "rooms",
            "Sprites": "sprites",
            "Notes": "notes",
            "Tile Sets": "tilesets",
            "Timelines": "timelines",
            "Fonts": "fonts",
            "Sounds": "sounds",
            "Extensions": "extensions"
        }
        
        structure = {
            "project_name": os.path.basename(self.project_path),
            "project_path": self.project_path,
            "categories": {},
            "gml_files": [],
            "total_gml_files": 0
        }
        
        # Сканируем каждую категорию
        for display_name, folder_name in asset_categories.items():
            category_path = os.path.join(self.project_path, folder_name)
            if os.path.isdir(category_path):
                structure["categories"][display_name] = self._scan_category(category_path, display_name)
                
        # Сканируем GML файлы
        self._scan_gml_files()
        structure["gml_files"] = self.project_gml_files_details
        structure["total_gml_files"] = len(self.project_gml_files_details)
        
        return structure
    
    def _scan_category(self, category_path: str, category_name: str) -> Dict[str, Any]:
        """Сканирует категорию ассетов"""
        category_info = {
            "path": category_path,
            "assets": []
        }
        
        try:
            for asset_name in sorted(os.listdir(category_path)):
                asset_path = os.path.join(category_path, asset_name)
                if os.path.isdir(asset_path):
                    asset_info = {
                        "name": asset_name,
                        "path": asset_path,
                        "type": category_name.lower().rstrip('s'),  # objects -> object
                        "yy_file": None,
                        "gml_files": []
                    }
                    
                    # Ищем .yy файл
                    yy_path = os.path.join(asset_path, f"{asset_name}.yy")
                    if os.path.isfile(yy_path):
                        asset_info["yy_file"] = yy_path
                        
                    # Ищем .gml файлы
                    for file in os.listdir(asset_path):
                        if file.endswith('.gml'):
                            gml_path = os.path.join(asset_path, file)
                            asset_info["gml_files"].append({
                                "name": file,
                                "path": gml_path
                            })
                            
                    category_info["assets"].append(asset_info)
                    
        except OSError as e:
            category_info["error"] = f"Could not read directory: {e}"
            
        return category_info
    
    def _scan_gml_files(self):
        """Сканирует все GML файлы в проекте"""
        for root, dirs, files in os.walk(self.project_path):
            # Пропускаем системные папки
            relative_root = os.path.relpath(root, self.project_path)
            if relative_root != '.':
                top_dir = relative_root.split(os.sep)[0].lower()
                if top_dir in ['options', 'datafiles', 'configs', '.git', '.vscode', 'temp']:
                    dirs[:] = []
                    continue
                    
            for file in sorted(files):
                if file.endswith('.gml'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.project_path)
                    parent_dir = os.path.dirname(file_path)
                    
                    # Определяем связанный .yy файл
                    asset_yy_path = None
                    asset_name = os.path.basename(parent_dir)
                    potential_yy_path = os.path.join(parent_dir, f"{asset_name}.yy")
                    if os.path.isfile(potential_yy_path):
                        asset_yy_path = potential_yy_path
                        
                    # Определяем display name
                    parent_asset_name = os.path.basename(parent_dir)
                    gml_name = os.path.splitext(file)[0]
                    display_name = f"{parent_asset_name} / {gml_name}"
                    
                    self.project_gml_files_details.append((
                        display_name, file_path, relative_path, asset_yy_path
                    ))
    
    def get_gml_content(self, file_path: str) -> Dict[str, Any]:
        """Получает содержимое GML файла"""
        try:
            if not os.path.isfile(file_path):
                return {"error": f"File not found: {file_path}"}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                "file_path": file_path,
                "relative_path": os.path.relpath(file_path, self.project_path),
                "content": content,
                "line_count": len(content.splitlines())
            }
        except Exception as e:
            return {"error": f"Error reading file {file_path}: {e}"}
    
    def get_room_info(self, room_name: str) -> Dict[str, Any]:
        """Получает информацию о комнате из .yy файла"""
        room_path = os.path.join(self.project_path, "rooms", room_name)
        room_yy_path = os.path.join(room_path, f"{room_name}.yy")
        
        if not os.path.isfile(room_yy_path):
            return {"error": f"Room .yy file not found: {room_yy_path}"}
            
        try:
            with open(room_yy_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Очищаем JSON от лишних запятых
            content_cleaned = re.sub(r",\s*([]}])", r"\1", content)
            room_data = json.loads(content_cleaned)
            
            return {
                "room_name": room_name,
                "room_path": room_path,
                "yy_path": room_yy_path,
                "data": room_data,
                "formatted_info": self._format_room_data(room_data)
            }
        except json.JSONDecodeError as e:
            return {"error": f"Error parsing room JSON: {e}"}
        except Exception as e:
            return {"error": f"Error reading room file: {e}"}
    
    def get_object_info(self, object_name: str) -> Dict[str, Any]:
        """Получает информацию об объекте из .yy файла"""
        object_path = os.path.join(self.project_path, "objects", object_name)
        object_yy_path = os.path.join(object_path, f"{object_name}.yy")
        
        if not os.path.isfile(object_yy_path):
            return {"error": f"Object .yy file not found: {object_yy_path}"}
            
        try:
            with open(object_yy_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Очищаем JSON от лишних запятых
            content_cleaned = re.sub(r",\s*([]}])", r"\1", content)
            object_data = json.loads(content_cleaned)
            
            return {
                "object_name": object_name,
                "object_path": object_path,
                "yy_path": object_yy_path,
                "data": object_data,
                "formatted_info": self._format_object_data(object_data)
            }
        except json.JSONDecodeError as e:
            return {"error": f"Error parsing object JSON: {e}"}
        except Exception as e:
            return {"error": f"Error reading object file: {e}"}
    
    def get_sprite_info(self, sprite_name: str) -> Dict[str, Any]:
        """Получает информацию о спрайте"""
        sprite_path = os.path.join(self.project_path, "sprites", sprite_name)
        sprite_yy_path = os.path.join(sprite_path, f"{sprite_name}.yy")
        
        if not os.path.isdir(sprite_path):
            return {"error": f"Sprite folder not found: {sprite_path}"}
            
        sprite_info = {
            "sprite_name": sprite_name,
            "sprite_path": sprite_path,
            "yy_path": sprite_yy_path if os.path.isfile(sprite_yy_path) else None,
            "frames": []
        }
        
        # Ищем PNG файлы (кадры спрайта)
        try:
            for filename in sorted(os.listdir(sprite_path)):
                if filename.lower().endswith('.png'):
                    sprite_info["frames"].append({
                        "filename": filename,
                        "path": os.path.join(sprite_path, filename)
                    })
        except OSError as e:
            sprite_info["error"] = f"Error reading sprite folder: {e}"
            
        return sprite_info
    
    def export_all_data(self) -> str:
        """Экспортирует все данные проекта в текстовый формат"""
        if not self.project_gml_files_details:
            self.scan_project()
            
        output_lines = []
        output_lines.append(f"// GML and YY Data Export from Project: {self.project_path}")
        output_lines.append(f"// Total GML Files Found: {len(self.project_gml_files_details)}")
        output_lines.append("=" * 70)
        output_lines.append("")
        
        exported_yy_files = set()
        
        for display_name, file_path, relative_path, asset_yy_path in self.project_gml_files_details:
            # Экспортируем GML файл
            output_lines.append(f"// ----- Start GML: {display_name} -----")
            output_lines.append(f"// ----- GML Path: {relative_path} -----")
            output_lines.append("")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    output_lines.append(f.read())
            except Exception as e:
                output_lines.append(f"// ***** ERROR READING GML FILE: {relative_path} *****")
                output_lines.append(f"// ***** Error: {e} *****")
                
            output_lines.append("")
            output_lines.append("-" * 50 + "[End GML]" + "-" * 19)
            output_lines.append("")
            
            # Экспортируем связанный YY файл
            if asset_yy_path and os.path.isfile(asset_yy_path) and asset_yy_path not in exported_yy_files:
                relative_yy_path = os.path.relpath(asset_yy_path, self.project_path)
                asset_name = os.path.basename(os.path.dirname(asset_yy_path))
                
                output_lines.append(f"// ----- Associated YY File: {asset_name} -----")
                output_lines.append(f"// ----- YY Path: {relative_yy_path} -----")
                output_lines.append("")
                
                try:
                    with open(asset_yy_path, 'r', encoding='utf-8') as f:
                        output_lines.append(f.read())
                except Exception as e:
                    output_lines.append(f"// ***** ERROR READING YY FILE: {relative_yy_path} *****")
                    output_lines.append(f"// ***** Error: {e} *****")
                    
                output_lines.append("")
                output_lines.append("=" * 30 + "[End YY]" + "=" * 32)
                output_lines.append("")
                
                exported_yy_files.add(asset_yy_path)
                
        return "\n".join(output_lines)
    
    def _format_room_data(self, data: Dict[str, Any]) -> str:
        """Форматирует данные комнаты для отображения"""
        output_lines = []
        room_name = data.get('name', 'Unknown Room')
        output_lines.append(f"{room_name}")
        
        layers = data.get('layers', [])
        layers_prefix = "├──" if data.get('roomSettings') or data.get('isPersistent') is not None else "└──"
        output_lines.append(f"{layers_prefix} Layers ({len(layers)})")
        
        for i, layer in enumerate(layers):
            is_last_layer = (i == len(layers) - 1)
            layer_prefix_connector = "│   " if not is_last_layer else "    "
            layer_prefix = f"{layer_prefix_connector}{'└──' if is_last_layer else '├──'}"
            
            layer_name = layer.get('name', f'Unnamed Layer {i}')
            layer_type = layer.get('__type', layer.get('modelName', 'Unknown'))
            output_lines.append(f"{layer_prefix} {layer_name} [{layer_type.replace('GM', '')}]")
            
            if layer_type == "GMInstanceLayer":
                instances = layer.get('instances', [])
                inst_prefix_connector = f"{layer_prefix_connector}    "
                inst_prefix = f"{inst_prefix_connector}└──"
                
                if instances:
                    output_lines.append(f"{inst_prefix} Instances ({len(instances)})")
                    instance_counts = Counter()
                    for inst in instances:
                        instance_counts[inst.get('objId', {}).get('name', 'UnknownObject')] += 1
                    
                    sorted_objects = sorted(instance_counts.items())
                    obj_prefix_connector = f"{inst_prefix_connector}    "
                    
                    for j, (obj_name, count) in enumerate(sorted_objects):
                        is_last_obj = (j == len(sorted_objects) - 1)
                        obj_prefix = f"{obj_prefix_connector}{'└──' if is_last_obj else '├──'}"
                        count_str = f" (x{count})" if count > 1 else ""
                        output_lines.append(f"{obj_prefix} {obj_name}{count_str}")
        
        # Свойства комнаты
        room_settings = data.get('roomSettings', {})
        if room_settings:
            prop_prefix = "└──"
            output_lines.append(f"{prop_prefix} Properties")
            prop_connector = "    "
            
            prop_items = [
                f"Width: {room_settings.get('Width', '?')}",
                f"Height: {room_settings.get('Height', '?')}",
                f"Speed: {room_settings.get('Speed', 30)}",
                f"Persistent: {data.get('isPersistent', False)}"
            ]
            
            creation_code_file = data.get('creationCodeFile', '')
            if creation_code_file:
                prop_items.append(f"Creation Code: {os.path.basename(creation_code_file)}")
            
            for k, prop_text in enumerate(prop_items):
                is_last_prop = (k == len(prop_items) - 1)
                prop_item_prefix = f"{prop_connector}{'└──' if is_last_prop else '├──'}"
                output_lines.append(f"{prop_item_prefix} {prop_text}")
        
        return "\n".join(output_lines)
    
    def _format_object_data(self, data: Dict[str, Any]) -> str:
        """Форматирует данные объекта для отображения"""
        output_lines = []
        obj_name = data.get('name', 'Unknown Object')
        output_lines.append(f"Object: {obj_name}")
        output_lines.append("=" * (len(obj_name) + 8))
        
        # Основные свойства
        output_lines.append("")
        output_lines.append("[Properties]")
        sprite_id = data.get('spriteId')
        output_lines.append(f"  Sprite: {sprite_id.get('name', 'None') if sprite_id else 'None'}")
        
        mask_id = data.get('spriteMaskId')
        output_lines.append(f"  Mask: {mask_id.get('name', 'Same as Sprite') if mask_id else 'Same as Sprite'}")
        
        parent_id = data.get('parentObjectId')
        output_lines.append(f"  Parent: {parent_id.get('name', 'None') if parent_id else 'None'}")
        
        output_lines.append(f"  Visible: {data.get('visible', True)}")
        output_lines.append(f"  Solid: {data.get('solid', False)}")
        output_lines.append(f"  Persistent: {data.get('persistent', False)}")
        
        # События
        event_list = data.get('eventList', [])
        output_lines.append(f"")
        output_lines.append(f"[Events ({len(event_list)})]")
        
        # Физика
        if data.get('physicsObject', False):
            output_lines.append("")
            output_lines.append("[Physics Properties]")
            output_lines.append(f"  Enabled: True")
            output_lines.append(f"  Sensor: {data.get('physicsSensor', False)}")
            output_lines.append(f"  Shape: {data.get('physicsShape', 1)}")
            output_lines.append(f"  Density: {data.get('physicsDensity', 0.5)}")
            output_lines.append(f"  Restitution: {data.get('physicsRestitution', 0.1)}")
            output_lines.append(f"  Group: {data.get('physicsGroup', 1)}")
            output_lines.append(f"  Linear Damping: {data.get('physicsLinearDamping', 0.1)}")
            output_lines.append(f"  Angular Damping: {data.get('physicsAngularDamping', 0.1)}")
            output_lines.append(f"  Friction: {data.get('physicsFriction', 0.2)}")
            output_lines.append(f"  Awake: {data.get('physicsStartAwake', True)}")
            output_lines.append(f"  Kinematic: {data.get('physicsKinematic', False)}")
        else:
            output_lines.append("")
            output_lines.append("[Physics Properties]")
            output_lines.append(f"  Enabled: False")
        
        # Переменные объекта
        obj_props = data.get('properties', [])
        output_lines.append(f"")
        output_lines.append(f"[Object Variables ({len(obj_props)})]")
        if obj_props:
            for prop in obj_props:
                prop_name = prop.get('name', prop.get('varName', 'UnknownVar'))
                prop_val = prop.get('value', prop.get('varValue', 'UnknownVal'))
                prop_type = prop.get('type', prop.get('varType', '?'))
                output_lines.append(f"  - {prop_name} = {prop_val} (Type: {prop_type})")
        else:
            output_lines.append("  (None)")
        
        return "\n".join(output_lines) 